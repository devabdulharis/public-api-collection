from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import Response
import httpx

from app.core.deps import get_http_client
from app.core.security import require_api_key
from app.services.image_service import remove_bg_image_bytes, REMBG_AVAILABLE

router = APIRouter(prefix="/api/img", tags=["Images"], dependencies=[Depends(require_api_key)])


@router.post("/remove-bg")
async def remove_bg(file: UploadFile = File(...)):
    if not REMBG_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail={"ok": False, "error": "rembg not available. Install rembg + onnxruntime."},
        )

    raw = await file.read()
    try:
        out = remove_bg_image_bytes(raw)
    except Exception as e:
        raise HTTPException(status_code=400, detail={"ok": False, "error": str(e)})

    return Response(content=out, media_type="image/png")


@router.get("/remove-bg-by-url")
async def remove_bg_by_url(
    image_url: str,
    client: httpx.AsyncClient = Depends(get_http_client),
):
    if not REMBG_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail={"ok": False, "error": "rembg not available. Install rembg + onnxruntime."},
        )

    try:
        r = await client.get(image_url)
        r.raise_for_status()
        out = remove_bg_image_bytes(r.content)
    except Exception as e:
        raise HTTPException(status_code=400, detail={"ok": False, "error": str(e)})

    return Response(content=out, media_type="image/png")