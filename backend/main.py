import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import Response

from backend.database.database import create_tables, SessionLocal
from backend.database.seed import seed_garments
from backend.services.inference import get_device_info, warmup_models
from backend.api import admin, garments, photos, tryon

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
STORAGE_DIR = BASE_DIR / "storage"


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
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


@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    svg_content = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
        '<text y=".9em" font-size="90">👔</text></svg>'
    )
    return Response(content=svg_content, media_type="image/svg+xml")


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
    return _health_payload()


if STORAGE_DIR.exists():
    app.mount("/storage", StaticFiles(directory=str(STORAGE_DIR)), name="storage")
