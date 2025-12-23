from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from typing import Optional

from app.services.gemini_web import gemini_web_service

router = APIRouter(
    prefix="/api/gemini-web",
    tags=["Gemini Web"],
    responses={404: {"description": "Not found"}},
)

class AuthRequest(BaseModel):
    secure_1psid: str
    secure_1psidts: str
    secure_1psidcc: str

class ChatRequest(BaseModel):
    message: str
    image_url: Optional[str] = None

@router.post("/auth")
async def authenticate(auth: AuthRequest):
    """
    Set cookies for Gemini authentication.
    """
    try:
        result = await gemini_web_service.set_cookies(
            auth.secure_1psid,
            auth.secure_1psidts,
            auth.secure_1psidcc
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat")
async def chat(request: ChatRequest):
    """
    Chat with Gemini using browser cookies.
    """
    try:
        response = await gemini_web_service.chat(request.message, request.image_url)
        # Assuming response is a simple string, wrap in dict
        return {"response": response}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
