"""Virtual try-on inference: Replicate IDM-VTON, CatVTON local, or mock fallback."""

from __future__ import annotations

import logging
import uuid
from io import BytesIO
from pathlib import Path

import httpx
from PIL import Image, ImageDraw, ImageFilter

from .config import (
    CATVTON_DIR,
    CATVTON_ATTN_DIR,
    SD_INPAINT_DIR,
    MODEL_DIR,
    RESULTS_DIR,
    UPLOAD_DIR,
    DEVICE_SETTING,
    INFERENCE_STEPS,
    INFERENCE_WIDTH,
    INFERENCE_HEIGHT,
    MOCK_MODE,
    VTON_BACKEND,
)
from .replicate_runner import is_replicate_configured, run_replicate_idm_vton

logger = logging.getLogger(__name__)

_device: str | None = None
_gpu_name: str | None = None
_model_loaded = False
_use_mock = False
_active_backend: str | None = None


# ── Backend detection ─────────────────────────────────────────────────────────

def _has_catvton_weights() -> bool:
    """Check if CatVTON attention weights are present."""
    # Attention weights live in catvton/<checkpoint>/attention/model.safetensors
    return (CATVTON_ATTN_DIR / "model.safetensors").exists()


def _has_idmvton_weights() -> bool:
    if not MODEL_DIR.exists():
        return False
    return any(MODEL_DIR.rglob("*.pth")) or any(MODEL_DIR.rglob("*.safetensors"))


def _resolve_backend() -> str:
    if MOCK_MODE:
        return "mock"
    backend = VTON_BACKEND.lower()
    if backend == "replicate" or (backend == "auto" and is_replicate_configured()):
        return "replicate"
    if backend == "catvton" or (backend == "auto" and _has_catvton_weights()):
        return "catvton"
    if backend == "mock":
        return "mock"
    if _has_idmvton_weights():
        return "local"
    return "mock"


def _detect_device() -> tuple[str, str | None]:
    try:
        import torch
        if DEVICE_SETTING == "cpu":
            return "cpu", None
        if DEVICE_SETTING == "cuda" and torch.cuda.is_available():
            return "cuda", torch.cuda.get_device_name(0)
        if DEVICE_SETTING == "auto" and torch.cuda.is_available():
            return "cuda", torch.cuda.get_device_name(0)
        return "cpu", None
    except (ImportError, OSError) as exc:
        logger.warning("PyTorch unavailable (%s)", exc)
        return "cpu", None


def get_device_info() -> dict:
    global _device, _gpu_name, _model_loaded, _use_mock, _active_backend

    if _active_backend is None:
        _active_backend = _resolve_backend()
        _device, _gpu_name = _detect_device()
        _use_mock = _active_backend == "mock"

        if _active_backend == "replicate":
            _model_loaded = True
            logger.info("VTON backend: Replicate IDM-VTON (real AI)")
        elif _active_backend == "catvton":
            logger.info(
                "VTON backend: CatVTON local (CPU, ~%d steps, %dx%d)",
                INFERENCE_STEPS, INFERENCE_WIDTH, INFERENCE_HEIGHT,
            )
        elif _active_backend == "local":
            _model_loaded = _has_idmvton_weights()
            logger.info("VTON backend: local IDM-VTON weights (pipeline stub)")
        else:
            _model_loaded = False
            logger.warning(
                "VTON backend: mock overlay — "
                "download weights and run download-models.sh for real try-on"
            )

    if _active_backend == "catvton":
        from .catvton_runner import is_pipeline_loaded
        model_loaded = is_pipeline_loaded()
    elif _active_backend == "replicate":
        model_loaded = is_replicate_configured()
    else:
        model_loaded = _model_loaded

    return {
        "device": _device,
        "gpu_name": _gpu_name,
        "model_loaded": model_loaded,
        "mock_mode": _use_mock,
        "backend": _active_backend,
        "replicate_configured": is_replicate_configured(),
        "catvton_available": _has_catvton_weights(),
        "inference_steps": INFERENCE_STEPS,
    }


def get_torch_device() -> str:
    """Return the resolved torch device string ('cuda' or 'cpu')."""
    global _device
    if _device is None:
        get_device_info()
    return _device or "cpu"


def warmup_models() -> None:
    """Load inference models at startup so the first try-on is not delayed."""
    info = get_device_info()
    if info["backend"] != "catvton":
        return

    from .catvton_runner import warmup_pipeline

    logger.info("Loading CatVTON model into memory at startup (may take 30–60s)...")
    try:
        warmup_pipeline(SD_INPAINT_DIR, CATVTON_ATTN_DIR)
        logger.info("CatVTON model ready")
    except Exception as exc:
        logger.error("CatVTON warmup failed: %s — try-on will retry or fall back to mock", exc)


# ── Image loading ─────────────────────────────────────────────────────────────

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


# ── Mock fallback ─────────────────────────────────────────────────────────────

def _mock_compose(person: Image.Image, garment: Image.Image) -> Image.Image:
    """Simple overlay — only used when no weights available."""
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
    draw.rectangle([8, 8, 220, 28], fill=(99, 102, 241))
    draw.text((14, 12), "Mock Try-On Preview", fill="white")

    return composed


# ── Main inference entry point ────────────────────────────────────────────────

async def run_inference(
    person_url: str,
    garment_url: str,
    job_id: str | None = None,
    garment_des: str = "clothing item",
    category_slug: str | None = None,
) -> str:
    info = get_device_info()
    filename = f"{job_id or uuid.uuid4().hex}.jpg"
    out_path = RESULTS_DIR / filename

    # ── Replicate (cloud AI) ──────────────────────────────────────────────────
    if info["backend"] == "replicate":
        result_bytes = await run_replicate_idm_vton(
            person_url,
            garment_url,
            garment_des,
            category_slug,
        )
        out_path.write_bytes(result_bytes)
        return f"/storage/try-on-results/{filename}"

    # ── Load images (needed for CatVTON and mock) ─────────────────────────────
    person = await download_image(person_url)
    garment = await download_image(garment_url)

    # ── CatVTON local ─────────────────────────────────────────────────────────
    if info["backend"] == "catvton":
        from .catvton_runner import run_catvton

        result = await run_catvton(
            person_img=person,
            garment_img=garment,
            sd_dir=SD_INPAINT_DIR,
            catvton_attn_dir=CATVTON_ATTN_DIR,
            steps=INFERENCE_STEPS,
            width=INFERENCE_WIDTH,
            height=INFERENCE_HEIGHT,
            category=category_slug or "upper",
        )
        result.save(out_path, "JPEG", quality=92)
        return f"/storage/try-on-results/{filename}"

    # ── Local IDM-VTON stub ───────────────────────────────────────────────────
    if info["backend"] == "local":
        raise RuntimeError("Local IDM-VTON pipeline is not implemented")

    # ── Mock only when backend is explicitly mock ─────────────────────────────
    if info["backend"] != "mock":
        raise RuntimeError(f"Unsupported VTON backend: {info['backend']}")

    person = person.resize((768, 1024), Image.Resampling.LANCZOS)
    garment = garment.resize((768, 1024), Image.Resampling.LANCZOS)
    result = _mock_compose(person, garment)
    result.save(out_path, "JPEG", quality=92)
    return f"/storage/try-on-results/{filename}"
