from fastapi import APIRouter, Depends, HTTPException
import httpx

from app.core.cache import TTLCache
from app.core.config import settings
from app.core.deps import get_http_client
from app.core.security import require_api_key
from app.services.bmkg_service import fetch_bmkg_autogempa

router = APIRouter(prefix="/api/bmkg", tags=["BMKG"], dependencies=[Depends(require_api_key)])

_cache = TTLCache()


@router.get("/autogempa")
async def autogempa(client: httpx.AsyncClient = Depends(get_http_client)):
    cached = _cache.get("autogempa")
    if cached:
        return {"ok": True, "cached": True, "data": cached}

    try:
        data = await fetch_bmkg_autogempa(client)
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail={"ok": False, "error": str(e)})

    _cache.set("autogempa", data, ttl_seconds=settings.bmkg_cache_ttl_seconds)
    return {"ok": True, "cached": False, "data": data, "source": "BMKG"}