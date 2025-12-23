from contextlib import asynccontextmanager
import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import cors_origins_list
from app.routers.meta import router as meta_router
from app.routers.bmkg import router as bmkg_router
from app.routers.downloaders import router as dl_router
from app.routers.images import router as img_router
from app.routers.utils import router as utils_router
from app.routers.copilot import router as copilot_router
from app.routers.gemini_web import router as gemini_web_router
from app.routers.islamic import router as islamic_router
from app.routers.converters import router as converters_router
from app.routers.ocr import router as ocr_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    timeout = httpx.Timeout(30.0, connect=10.0)
    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
        app.state.http = client
        yield


app = FastAPI(
    title="Personal Tools API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
origins = cors_origins_list()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(meta_router)
app.include_router(bmkg_router)
app.include_router(dl_router)
app.include_router(img_router)
app.include_router(utils_router)
app.include_router(copilot_router)
app.include_router(gemini_web_router)
app.include_router(islamic_router)
app.include_router(converters_router)
app.include_router(ocr_router)