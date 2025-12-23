from fastapi import APIRouter, Depends, HTTPException, Query
from app.core.cache import TTLCache
from app.core.config import settings
from app.core.security import require_api_key
from app.services.ytdlp_service import extract_media_info, build_direct_links

router = APIRouter(prefix="/api/dl", tags=["Downloader"], dependencies=[Depends(require_api_key)])

_cache = TTLCache()


@router.get("/info")
def info(url: str = Query(..., description="URL TikTok/IG/YouTube/X/dll")):
    cache_key = f"info:{url}"
    cached = _cache.get(cache_key)
    if cached:
        return {"ok": True, "cached": True, "data": cached}

    try:
        data = extract_media_info(url)
    except Exception as e:
        raise HTTPException(status_code=400, detail={"ok": False, "error": str(e)})

    _cache.set(cache_key, data, ttl_seconds=settings.ytdlp_cache_ttl_seconds)
    return {"ok": True, "cached": False, "data": data}


@router.get("/direct")
def direct(url: str = Query(..., description="URL TikTok/IG/YouTube/X/dll")):
    cache_key = f"direct:{url}"
    cached = _cache.get(cache_key)
    if cached:
        return {"ok": True, "cached": True, "data": cached}

    try:
        info_obj = extract_media_info(url)
        data = build_direct_links(info_obj)
    except Exception as e:
        raise HTTPException(status_code=400, detail={"ok": False, "error": str(e)})

    _cache.set(cache_key, data, ttl_seconds=settings.ytdlp_cache_ttl_seconds)
    return {"ok": True, "cached": False, "data": data}