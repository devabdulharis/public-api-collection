import base64
import hashlib
import io

import qrcode
from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response

from app.core.security import require_api_key

router = APIRouter(prefix="/api/utils", tags=["Utils"], dependencies=[Depends(require_api_key)])


@router.get("/hash")
def hash_text(text: str, algo: str = Query("sha256", enum=["md5", "sha1", "sha256"])):
    h = hashlib.new(algo)
    h.update(text.encode("utf-8"))
    return {"ok": True, "algo": algo, "digest": h.hexdigest()}


@router.get("/base64/encode")
def b64_encode(text: str):
    return {"ok": True, "base64": base64.b64encode(text.encode("utf-8")).decode("ascii")}


@router.get("/base64/decode")
def b64_decode(b64: str):
    raw = base64.b64decode(b64.encode("ascii"))
    return {"ok": True, "text": raw.decode("utf-8", errors="replace")}


@router.get("/qr")
def qr(text: str):
    img = qrcode.make(text)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return Response(content=buf.getvalue(), media_type="image/png")