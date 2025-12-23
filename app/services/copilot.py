import base64
import json
import time
import os
import httpx
from fastapi import HTTPException

# Constants matching the original wrapper
CLIENT_ID = "Iv1.b507a08c87ecfe98"
SCOPE = "read:user"
TOKEN_URL = "https://api.github.com/copilot_internal/v2/token"
DEVICE_CODE_URL = "https://github.com/login/device/code"
ACCESS_TOKEN_URL = "https://github.com/login/oauth/access_token"
CHAT_URL = "https://api.individual.githubcopilot.com/chat/completions"

# Headers
USER_AGENT = "GithubCopilot/1.155.0"
EDITOR_VERSION = "Neovim/0.6.1"
EDITOR_PLUGIN_VERSION = "copilot.vim/1.16.0"

class CopilotService:
    def __init__(self, token_file_path: str = ".copilot_token"):
        self.token_file_path = token_file_path
        self._access_token = None
        self._copilot_token = None
        self._copilot_token_expiry = 0

    def _encrypt(self, text: str) -> str:
        """Simple XOR 'encryption' port from original wrapper"""
        if not text:
            return ""
        encrypted = []
        text_bytes = text.encode('utf8')
        for item in [str(text_bytes[i]) for i in range(len(text_bytes))]:
            if len(item) == 2:
                item = "0" + item
            encrypted.append(item)
        obj = "".join(encrypted)[::-1]
        return base64.b64encode(obj.encode('utf8')).decode('utf8').replace("=", "")

    def _decrypt(self, text: str) -> str | None:
        """Simple XOR 'decryption' port from original wrapper"""
        try:
            text = base64.b64decode(text + '==').decode('utf8')[::-1]
            decrypted = []
            for i in range(0, len(text), 3):
                chunk = text[i:i+3]
                if len(chunk) == 3:
                    if chunk.startswith('0'):
                        chunk = chunk[1:]
                    decrypted.append(chr(int(chunk)))
            return ''.join(decrypted)
        except Exception:
            return None

    def _load_access_token(self):
        if self._access_token:
            return self._access_token
        
        if os.path.exists(self.token_file_path):
            with open(self.token_file_path, 'r') as f:
                content = f.read().strip()
                self._access_token = self._decrypt(content)
        return self._access_token

    def _save_access_token(self, token: str):
        self._access_token = token
        with open(self.token_file_path, 'w') as f:
            f.write(self._encrypt(token))

    async def start_device_auth(self):
        """Step 1: Get device code"""
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                DEVICE_CODE_URL,
                headers={
                    'accept': 'application/json',
                    'editor-version': EDITOR_VERSION,
                    'editor-plugin-version': EDITOR_PLUGIN_VERSION,
                    'content-type': 'application/json',
                    'user-agent': USER_AGENT,
                },
                json={"client_id": CLIENT_ID, "scope": SCOPE}
            )
            resp.raise_for_status()
            return resp.json()

    async def check_device_auth(self, device_code: str):
        """Step 2: Poll/Check for access token"""
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                ACCESS_TOKEN_URL,
                headers={
                    'accept': 'application/json',
                    'editor-version': EDITOR_VERSION,
                    'editor-plugin-version': EDITOR_PLUGIN_VERSION,
                    'content-type': 'application/json',
                    'user-agent': USER_AGENT,
                },
                json={
                    "client_id": CLIENT_ID,
                    "device_code": device_code,
                    "grant_type": "urn:ietf:params:oauth:grant-type:device_code"
                }
            )
            resp.raise_for_status()
            data = resp.json()
            
            if "access_token" in data:
                self._save_access_token(data["access_token"])
                return {"status": "success", "access_token": "Saved internally"}
            elif "error" in data:
                 return {"status": "pending", "error": data.get("error_description", data["error"])}
            return data

    async def get_copilot_token(self):
        """Get the internal Copilot token (expires every 30m usually)"""
        current_time = time.time()
        if self._copilot_token and self._copilot_token_expiry > current_time:
             return self._copilot_token

        access_token = self._load_access_token()
        if not access_token:
            raise HTTPException(status_code=401, detail="Not authenticated. Please perform device login first.")

        async with httpx.AsyncClient() as client:
            resp = await client.get(
                TOKEN_URL,
                headers={
                    'authorization': f'token {access_token}',
                    'editor-version': EDITOR_VERSION,
                    'editor-plugin-version': EDITOR_PLUGIN_VERSION,
                    'user-agent': USER_AGENT
                }
            )
            if resp.status_code != 200:
                 raise HTTPException(status_code=401, detail=f"Failed to get copilot token: {resp.text}")
            
            data = resp.json()
            self._copilot_token = data.get('token')
            # Rudimentary expiry check (default to 25 mins to be safe)
            self._copilot_token_expiry = current_time + (25 * 60)
            return self._copilot_token

    async def chat_completions(self, messages: list, model: str = "gpt-4o"):
        token = await self.get_copilot_token()
        
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                CHAT_URL,
                headers={
                    'Authorization': f'Bearer {token}',
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'Editor-Version': 'vscode/1.95.3',
                    'Editor-Plugin-Version': 'copilot-chat/0.22.4',
                    'Openai-Intent': 'conversation-panel',
                    'X-Github-Api-Version': '2023-07-07'
                },
                json={
                    'messages': messages,
                    'model': model,
                    'temperature': 0,
                    'stream': True,
                    'n': 1
                },
                timeout=60.0
            ) as resp:
                if resp.status_code != 200:
                    error_text = await resp.read()
                    raise HTTPException(status_code=resp.status_code, detail=f"Copilot API error: {error_text.decode('utf-8')}")

                async for line in resp.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str.strip() == "[DONE]":
                            break
                        try:
                            data_json = json.loads(data_str)
                            if data_json.get('choices'):
                                content = data_json['choices'][0].get('delta', {}).get('content', '')
                                if content:
                                    yield content
                        except json.JSONDecodeError:
                            continue

copilot_service = CopilotService()
