from __future__ import annotations

import io
from PIL import Image

try:
    from rembg import remove  # type: ignore
    REMBG_AVAILABLE = True
except Exception:
    remove = None
    REMBG_AVAILABLE = False


def remove_bg_image_bytes(image_bytes: bytes) -> bytes:
    if not REMBG_AVAILABLE or remove is None:
        raise RuntimeError("rembg not installed/available")

    img = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
    out = remove(img)  # PIL.Image
    buf = io.BytesIO()
    out.save(buf, format="PNG")
    return buf.getvalue()