import httpx
from fastapi import HTTPException, UploadFile
from typing import Optional, Dict, Any

class OCRService:
    def __init__(self):
        # Base44 Config
        self.base44_host = "base44.app"
        self.app_id = "68eeab16253a1b0a823884ad" # From user request header x-app-id
        self.integration_app_id = "68eeb6171a0e2bf341b93443" # From URL
        self.endpoint_url = f"https://{self.base44_host}/api/apps/{self.integration_app_id}/integration-endpoints/Core/ExtractDataFromUploadedFile"
        
        # Schema from user request
        self.ktp_json_schema = {
            "type": "object",
            "properties": {
                "nik": {"type": "string", "description": "Nomor Induk Kependudukan (16 digit)"},
                "nama": {"type": "string", "description": "Nama lengkap sesuai KTP"},
                "tempat_tanggal_lahir": {"type": "string", "description": "Tempat dan tanggal lahir, misal: Bandung, 23 Januari 1999"},
                "jenis_kelamin": {"type": "string", "description": "Jenis kelamin, misal: Laki-laki atau Perempuan"},
                "golongan_darah": {"type": "string", "description": "Golongan darah, misal: A, B, AB, O"},
                "alamat": {"type": "string", "description": "Alamat lengkap"},
                "rt_rw": {"type": "string", "description": "RT dan RW, misal: 001/002"},
                "kel_desa": {"type": "string", "description": "Kelurahan atau desa"},
                "kecamatan": {"type": "string", "description": "Kecamatan"},
                "agama": {"type": "string", "description": "Agama"},
                "status_perkawinan": {"type": "string", "description": "Status perkawinan"},
                "pekerjaan": {"type": "string", "description": "Pekerjaan"},
                "kewarganegaraan": {"type": "string", "description": "Kewarganegaraan, misal: WNI atau WNA"},
                "berlaku_hingga": {"type": "string", "description": "Masa berlaku KTP, biasanya Seumur Hidup"}
            }
        }

    async def _upload_to_file_io(self, file_content: bytes, filename: str) -> str:
        """
        Uploads file to file.io to get a temporary public URL.
        file.io files are deleted after 1 download or 14 days by default.
        We can set expiry to 1 day.
        """
        url = "https://file.io"
        async with httpx.AsyncClient() as client:
            files = {'file': (filename, file_content)}
            resp = await client.post(url, files=files, data={"expires": "1d"})
            if resp.status_code != 200:
                try:
                    detail = resp.json()
                except:
                    detail = resp.text
                raise HTTPException(status_code=502, detail=f"Failed to upload to temp storage: {detail}")
            
            data = resp.json()
            if not data.get("success"):
                 raise HTTPException(status_code=502, detail="Temp storage service reported failure")
            
            return data.get("link")

    async def extract_ktp_data(self, file_url: Optional[str] = None, file: Optional[UploadFile] = None) -> Dict[str, Any]:
        if not file_url and not file:
            raise HTTPException(status_code=400, detail="Either file_url or file must be provided")

        final_url = file_url
        
        # If file is uploaded, upload to temp storage first
        if file:
            content = await file.read()
            final_url = await self._upload_to_file_io(content, file.filename)

        # Call Base44 API
        payload = {
            "file_url": final_url,
            "json_schema": self.ktp_json_schema
        }
        
        headers = {
            "Host": self.base44_host,
            "x-app-id": self.app_id,
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(self.endpoint_url, headers=headers, json=payload)
            
            if resp.status_code != 200:
                 raise HTTPException(status_code=resp.status_code, detail=f"OCR Provider Error: {resp.text}")
            
            return resp.json()

ocr_service = OCRService()
