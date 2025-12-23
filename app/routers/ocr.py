from fastapi import APIRouter, File, UploadFile, Body, HTTPException
from typing import Optional
from app.services.ocr import ocr_service

router = APIRouter(
    prefix="/api/ocr",
    tags=["OCR"],
    responses={404: {"description": "Not found"}},
)

@router.post("/ktp")
async def extract_ktp(
    file_url: Optional[str] = Body(None, embed=True),
    file: Optional[UploadFile] = File(None)
):
    """
    Extract KTP Data (OCR).
    
    - **file_url**: Direct URL to the image (faster).
    - **file**: Upload image file (will be uploaded to temp storage first).
    """
    try:
        if not file_url and not file:
            raise HTTPException(status_code=400, detail="Provide either 'file_url' or 'file'")
        
        result = await ocr_service.extract_ktp_data(file_url=file_url, file=file)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
