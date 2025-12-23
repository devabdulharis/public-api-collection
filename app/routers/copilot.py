from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from app.services.copilot import copilot_service

router = APIRouter(
    prefix="/api/copilot",
    tags=["Copilot"],
    responses={404: {"description": "Not found"}},
)

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    model: str = "gpt-4o"
    messages: List[ChatMessage]

@router.get("/auth/start")
async def start_auth():
    """Calculates the device code and returns the verification URL."""
    try:
        data = await copilot_service.start_device_auth()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/auth/check")
async def check_auth(device_code: str = Body(..., embed=True)):
    """Checks if the user has completed the authentication process."""
    try:
        result = await copilot_service.check_device_auth(device_code)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat")
async def chat(request: ChatRequest):
    """
    Stream chat response from Github Copilot.
    """
    messages_dict = [msg.dict() for msg in request.messages]
    
    # We return a StreamingResponse
    return StreamingResponse(
        copilot_service.chat_completions(messages_dict, request.model),
        media_type="text/event-stream"
    )
