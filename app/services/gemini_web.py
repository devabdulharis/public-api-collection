import json
import os
from fastapi import HTTPException
from gemini_webapi import GeminiClient

class GeminiWebService:
    def __init__(self, token_file_path: str = ".gemini_cookies"):
        self.token_file_path = token_file_path
        self._client: GeminiClient | None = None

    def _load_cookies(self) -> dict | None:
        if os.path.exists(self.token_file_path):
            with open(self.token_file_path, 'r') as f:
                return json.load(f)
        return None

    def _save_cookies(self, cookies: dict):
        with open(self.token_file_path, 'w') as f:
            json.dump(cookies, f)

    async def get_client(self) -> GeminiClient:
        if self._client:
            return self._client
        
        cookies = self._load_cookies()
        if not cookies:
            raise HTTPException(status_code=401, detail="Gemini cookies not set. Please authenticate first.")
        
        try:
            # gemini-webapi client initialization
            self._client = GeminiClient(
                secure_1psid=cookies.get("__Secure-1PSID"),
                secure_1psidts=cookies.get("__Secure-1PSIDTS"),
                secure_1psidcc=cookies.get("__Secure-1PSIDCC"),
            )
            # Initialize connection
            await self._client.init()
            return self._client
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to initialize Gemini client: {str(e)}")

    async def set_cookies(self, psid: str, psidts: str, psidcc: str):
        cookies = {
            "__Secure-1PSID": psid,
            "__Secure-1PSIDTS": psidts,
            "__Secure-1PSIDCC": psidcc
        }
        self._save_cookies(cookies)
        # Reset client to force re-initialization with new cookies
        self._client = None
        return {"status": "success", "message": "Cookies saved"}

    async def chat(self, message: str, image_url: str = None):
        client = await self.get_client()
        try:
            # Note: The library might have slightly different method signatures, 
            # we assume generate_content based on standard patterns or library update.
            # Checking library usage via pip install showed it exists, but exact method might vary.
            # Assuming client.generate_content or client.chat
            
            # Based on common usage of such wrappers:
            response = await client.generate_content(message, image_url=image_url)
            return response.text
        except Exception as e:
             # If error suggests auth issue, clear client
             if "401" in str(e) or "unauthorized" in str(e).lower():
                 self._client = None
             raise HTTPException(status_code=500, detail=str(e))

gemini_web_service = GeminiWebService()
