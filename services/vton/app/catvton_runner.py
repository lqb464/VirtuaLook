"""
CatVTON local inference.

CatVTON (Concatenation Is All You Need for Virtual Try-On) works by:
  1. Concatenating the person image and garment image side-by-side
  2. Running SD v1.5 inpainting on the concatenated image
  3. The custom attention weights learn to transfer the garment onto the person
  4. Cropping the left half (person side) of the output as the result

References:
  - Paper: https://arxiv.org/abs/2407.15886
  - Weights: https://huggingface.co/zhengchong/CatVTON
"""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path

from PIL import Image, ImageDraw

logger = logging.getLogger(__name__)

# Pipeline singleton — warmed up at server startup via warmup_pipeline()
_pipeline = None
_pipeline_loaded = False


def _make_upper_body_mask(img: Image.Image, category: str = "upper") -> Image.Image:
    """
    Generate a simple mask for the clothing region.

    Without DensePose we approximate:
    - upper body / tops: rows 15%–65% of height, full width
    - lower body / pants: rows 50%–95% of height, full width
    - dress: rows 15%–90% of height, full width

    The mask is white (255) where the garment should be applied.
    """
    w, h = img.size
    mask = Image.new("L", (w, h), 0)
    draw = ImageDraw.Draw(mask)

    cat = (category or "upper").lower()
    if "lower" in cat or "pant" in cat or "skirt" in cat:
        y0, y1 = int(h * 0.50), int(h * 0.95)
    elif "dress" in cat or "full" in cat:
        y0, y1 = int(h * 0.15), int(h * 0.90)
    else:
        y0, y1 = int(h * 0.15), int(h * 0.65)

    x_pad = int(w * 0.05)
    draw.rectangle([x_pad, y0, w - x_pad, y1], fill=255)
    return mask


def _sd_local_ready(sd_dir: Path) -> bool:
    """True only if local SD weights are fully downloaded (not just metadata)."""
    if not (sd_dir / "model_index.json").exists():
        return False
    unet_dir = sd_dir / "unet"
    if not unet_dir.is_dir():
        return False
    return bool(list(unet_dir.glob("*.safetensors")) or list(unet_dir.glob("*.bin")))


def _load_catvton_attn_weights(unet, attn_dir: Path) -> None:
    """
    Load CatVTON self-attention weights into UNet attn1 modules.

    Official weights (model.safetensors) are NOT LoRA / attn_procs format.
    Keys look like ``0.to_q.weight``, ``8.to_k.weight``, … (non-contiguous
    indices from CatVTON's ModuleList). We map them in sorted-index order onto
    UNet modules whose names end with ``attn1``.
    """
    from safetensors.torch import load_file

    attn_file = attn_dir / "model.safetensors"
    if not attn_file.is_file():
        raise FileNotFoundError(f"CatVTON attention weights not found: {attn_file}")

    state = load_file(str(attn_file))
    by_idx: dict[int, dict[str, object]] = {}
    for key, tensor in state.items():
        idx_str, rest = key.split(".", 1)
        by_idx.setdefault(int(idx_str), {})[rest] = tensor

    attn1_modules = [m for name, m in unet.named_modules() if name.endswith("attn1")]
    sorted_idxs = sorted(by_idx)
    if len(attn1_modules) != len(sorted_idxs):
        raise RuntimeError(
            f"CatVTON attn mismatch: UNet has {len(attn1_modules)} attn1 modules, "
            f"checkpoint has {len(sorted_idxs)} blocks"
        )

    for module, idx in zip(attn1_modules, sorted_idxs):
        module.load_state_dict(by_idx[idx], strict=True)

    logger.info(
        "Loaded CatVTON attention weights (%d self-attn blocks) from %s",
        len(attn1_modules),
        attn_file,
    )


def _load_pipeline(sd_dir: Path, catvton_attn_dir: Path):
    """
    Load and cache the CatVTON pipeline.

    SD v1.5 base is loaded from local path if available, otherwise downloads
    from HuggingFace (booksforcharlie/stable-diffusion-inpainting) to cache.
    CatVTON attention weights are loaded from catvton_attn_dir/model.safetensors.
    """
    global _pipeline, _pipeline_loaded

    if _pipeline_loaded:
        return _pipeline

    try:
        import torch
        from diffusers import StableDiffusionInpaintPipeline

        from .inference import get_torch_device

        device = get_torch_device()
        dtype = torch.float16 if device == "cuda" else torch.float32

        sd_source = (
            str(sd_dir)
            if _sd_local_ready(sd_dir)
            else "booksforcharlie/stable-diffusion-inpainting"
        )
        logger.info("Loading SD inpaint base from: %s (device=%s)", sd_source, device)

        pipe = StableDiffusionInpaintPipeline.from_pretrained(
            sd_source,
            torch_dtype=dtype,
            safety_checker=None,
            requires_safety_checker=False,
        )

        attn_file = catvton_attn_dir / "model.safetensors"
        if attn_file.exists():
            _load_catvton_attn_weights(pipe.unet, catvton_attn_dir)
        else:
            logger.warning(
                "CatVTON attention weights not found at %s — using plain SD inpainting",
                attn_file,
            )

        pipe = pipe.to(device)
        if device == "cpu":
            pipe.enable_attention_slicing(slice_size="max")
            pipe.enable_vae_slicing()

        _pipeline = pipe
        _pipeline_loaded = True
        logger.info("CatVTON pipeline loaded successfully (device: %s)", device)
        return pipe

    except Exception as exc:
        logger.error("Failed to load CatVTON pipeline: %s", exc)
        # Do not cache a failed load — allow a later retry after fixing weights/deps.
        _pipeline_loaded = False
        _pipeline = None
        raise


def is_pipeline_loaded() -> bool:
    return _pipeline_loaded and _pipeline is not None


def warmup_pipeline(sd_dir: Path, catvton_attn_dir: Path) -> None:
    """Load CatVTON pipeline into memory. Call once at server startup."""
    _load_pipeline(sd_dir, catvton_attn_dir)


def _run_pipe_sync(
    pipe,
    concat_img: Image.Image,
    full_mask: Image.Image,
    steps: int,
    concat_w: int,
    height: int,
) -> Image.Image:
    """Blocking diffusion call — must run in a thread pool, not the event loop."""
    return pipe(
        prompt="a photo of a person wearing the garment, realistic, high quality",
        negative_prompt="deformed, distorted, blurry, unrealistic, cartoon",
        image=concat_img,
        mask_image=full_mask,
        num_inference_steps=steps,
        guidance_scale=2.5,
        width=concat_w,
        height=height,
    ).images[0]


async def run_catvton(
    person_img: Image.Image,
    garment_img: Image.Image,
    sd_dir: Path,
    catvton_attn_dir: Path,
    steps: int = 20,
    width: int = 512,
    height: int = 768,
    category: str = "upper",
) -> Image.Image:
    """
    Run CatVTON inference asynchronously (diffusion runs in a worker thread).
    """
    pipe = _load_pipeline(sd_dir, catvton_attn_dir)
    if pipe is None:
        raise RuntimeError("CatVTON pipeline is not loaded")

    person_resized = person_img.resize((width, height), Image.Resampling.LANCZOS)
    garment_resized = garment_img.resize((width, height), Image.Resampling.LANCZOS)

    concat_w = width * 2
    concat_img = Image.new("RGB", (concat_w, height))
    concat_img.paste(person_resized, (0, 0))
    concat_img.paste(garment_resized, (width, 0))

    full_mask = Image.new("L", (concat_w, height), 0)
    clothing_mask = _make_upper_body_mask(person_resized, category)
    full_mask.paste(clothing_mask, (0, 0))

    logger.info(
        "CatVTON inference: %dx%d concat, %d steps, category=%s",
        concat_w, height, steps, category,
    )

    result_concat = await asyncio.to_thread(
        _run_pipe_sync, pipe, concat_img, full_mask, steps, concat_w, height,
    )
    return result_concat.crop((0, 0, width, height))
