import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .database import create_tables
from .inference import get_device_info, warmup_models
from .routers import admin, garments, photos, tryon
from .seed import seed_garments
from .site_pages import register_frontend_routes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
STORAGE_DIR = BASE_DIR.parent.parent / "storage"


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    from .database import SessionLocal
    db = SessionLocal()
    try:
        seed_garments(db)
    finally:
        db.close()

    warmup_models()

    info = get_device_info()
    logger.info(
        "VirtuaLook started: backend=%s device=%s model_loaded=%s mock=%s",
        info.get("backend"),
        info.get("device"),
        info.get("model_loaded"),
        info["mock_mode"],
    )
    yield


app = FastAPI(
    title="VirtuaLook API",
    version="1.0.0",
    description="AI Virtual Try-On — CatVTON local, Replicate IDM-VTON, or mock fallback.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(garments.router)
app.include_router(photos.router)
app.include_router(tryon.router)
app.include_router(admin.router)


def _health_payload() -> dict:
    info = get_device_info()
    return {
        "status": "ok",
        "version": "1.0.0",
        "device": info["device"],
        "gpu_name": info.get("gpu_name"),
        "model_loaded": info["model_loaded"],
        "mock_mode": info["mock_mode"],
        "backend": info.get("backend"),
        "replicate_configured": info.get("replicate_configured"),
        "catvton_available": info.get("catvton_available"),
        "inference_steps": info.get("inference_steps"),
    }


@app.get("/health")
async def health():
    return _health_payload()


@app.get("/api/health")
async def api_health():
    """Alias for /health — matches RAnythinG-style API conventions."""
    return _health_payload()


if STORAGE_DIR.exists():
    app.mount("/storage", StaticFiles(directory=str(STORAGE_DIR)), name="storage")

register_frontend_routes(app)
