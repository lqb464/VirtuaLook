"""Virtual try-on inference service entry point."""

from __future__ import annotations

import logging
import uuid
from io import BytesIO
from pathlib import Path

import httpx
from PIL import Image, ImageDraw, ImageFilter

from backend.core.config import (
    RESULTS_DIR,
    UPLOAD_DIR,
    DEVICE_SETTING,
    MOCK_MODE,
)

from src.pipeline.tryon_pipeline import TryOnPipeline

logger = logging.getLogger(__name__)

_device: str | None = None
_gpu_name: str | None = None
_use_mock = False
_pipeline: TryOnPipeline | None = None

def _detect_device() -> tuple[str, str | None]:
    try:
        import torch
        if DEVICE_SETTING == "cpu":
            return "cpu", None
        if DEVICE_SETTING in ["cuda", "auto"] and torch.cuda.is_available():
            return "cuda", torch.cuda.get_device_name(0)
        return "cpu", None
    except (ImportError, OSError) as exc:
        logger.warning("PyTorch unavailable (%s)", exc)
        return "cpu", None

def get_device_info() -> dict:
    global _device, _gpu_name, _use_mock
    if _device is None:
        _device, _gpu_name = _detect_device()
        _use_mock = MOCK_MODE

    return {
        "device": _device,
        "gpu_name": _gpu_name,
        "mock_mode": _use_mock,
        "backend": "mock" if _use_mock else "local_diffusion",
    }

def warmup_models() -> None:
    global _pipeline, _device
    info = get_device_info()
    if info["mock_mode"]:
        return
    
    logger.info("Loading Local Diffusion VTON Pipeline into memory...")
    try:
        _pipeline = TryOnPipeline(device=_device)
        logger.info("Local Diffusion VTON ready")
    except Exception as exc:
        logger.error("Warmup failed: %s", exc)

async def download_image(url: str) -> Image.Image:
    if url.startswith("http://") or url.startswith("https://"):
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return Image.open(BytesIO(resp.content)).convert("RGB")
    if url.startswith("/storage/"):
        path = UPLOAD_DIR / url.removeprefix("/storage/")
    else:
        path = Path(url)
    if path.exists():
        return Image.open(path).convert("RGB")
    raise FileNotFoundError(f"Cannot load image: {url}")

def _mock_compose(person: Image.Image, garment: Image.Image) -> Image.Image:
    person = person.resize((512, 768), Image.Resampling.LANCZOS)
    garment = garment.resize((280, 350), Image.Resampling.LANCZOS)

    result = person.copy()
    garment = garment.convert("RGBA")

    overlay = Image.new("RGBA", result.size, (0, 0, 0, 0))
    gx = (result.width - garment.width) // 2
    gy = int(result.height * 0.22)
    overlay.paste(garment, (gx, gy), garment if garment.mode == "RGBA" else None)
    overlay = overlay.filter(ImageFilter.GaussianBlur(radius=0.5))

    base = result.convert("RGBA")
    composed = Image.alpha_composite(base, overlay).convert("RGB")

    draw = ImageDraw.Draw(composed)
    draw.rectangle([8, 8, 220, 28], fill=(0, 149, 255))
    draw.text((14, 12), "Mock Try-On Preview", fill="white")

    return composed

async def run_inference(
    person_url: str,
    garment_url: str,
    job_id: str | None = None,
    garment_des: str = "clothing item",
    category_slug: str | None = None,
) -> str:
    global _pipeline
    info = get_device_info()
    filename = f"{job_id or uuid.uuid4().hex}.jpg"
    out_path = RESULTS_DIR / filename

    person = await download_image(person_url)
    garment = await download_image(garment_url)

    if info["mock_mode"]:
        person = person.resize((768, 1024), Image.Resampling.LANCZOS)
        garment = garment.resize((768, 1024), Image.Resampling.LANCZOS)
        result = _mock_compose(person, garment)
        result.save(out_path, "JPEG", quality=92)
        return f"/storage/try-on-results/{filename}"

    if _pipeline is None:
        warmup_models()
        
    if _pipeline is None:
        raise RuntimeError("Diffusion Pipeline failed to load.")
        
    result = _pipeline.process(person, garment)
    result.save(out_path, "JPEG", quality=92)
    return f"/storage/try-on-results/{filename}"
