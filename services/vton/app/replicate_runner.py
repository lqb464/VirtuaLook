"""Run real IDM-VTON via Replicate cloud (no local GPU required)."""

from __future__ import annotations

import asyncio
import logging
import os
import tempfile
from pathlib import Path

import httpx

logger = logging.getLogger(__name__)

REPLICATE_MODEL = os.getenv(
    "REPLICATE_MODEL",
    "cuuupid/idm-vton:d73e611d73581af0410fc0b5cc400e2cae959a92cb6c8b54d6ad102c52b4d5ab",
)


def is_replicate_configured() -> bool:
    return bool(os.getenv("REPLICATE_API_TOKEN", "").strip())


def map_category(category_slug: str | None) -> str:
    slug = (category_slug or "").lower()
    if slug in {"vay", "dress", "dresses"}:
        return "dresses"
    if slug in {"quan", "pants", "lower"}:
        return "lower_body"
    return "upper_body"


async def _download_bytes(url: str) -> bytes:
    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        return resp.content


def _run_replicate_sync(
    human_path: Path,
    garment_path: Path,
    garment_des: str,
    category: str,
) -> bytes:
    import replicate

    token = os.getenv("REPLICATE_API_TOKEN")
    if not token:
        raise RuntimeError("REPLICATE_API_TOKEN is not set")

    os.environ["REPLICATE_API_TOKEN"] = token

    with human_path.open("rb") as human_file, garment_path.open("rb") as garment_file:
        output = replicate.run(
            REPLICATE_MODEL,
            input={
                "human_img": human_file,
                "garm_img": garment_file,
                "garment_des": garment_des or "clothing item",
                "category": category,
                "crop": True,
                "steps": 30,
                "seed": 42,
            },
        )

    if hasattr(output, "read"):
        return output.read()

    if hasattr(output, "url"):
        url = output.url
    elif isinstance(output, str):
        url = output
    else:
        raise RuntimeError(f"Unexpected Replicate output type: {type(output)}")

    import httpx as sync_httpx

    resp = sync_httpx.get(url, timeout=120.0)
    resp.raise_for_status()
    return resp.content


async def run_replicate_idm_vton(
    person_image_url: str,
    garment_image_url: str,
    garment_des: str,
    category_slug: str | None,
) -> bytes:
    category = map_category(category_slug)
    logger.info(
        "Running Replicate IDM-VTON category=%s garment_des=%s",
        category,
        garment_des,
    )

    person_bytes, garment_bytes = await asyncio.gather(
        _download_bytes(person_image_url),
        _download_bytes(garment_image_url),
    )

    with tempfile.TemporaryDirectory() as tmp:
        human_path = Path(tmp) / "person.jpg"
        garment_path = Path(tmp) / "garment.jpg"
        human_path.write_bytes(person_bytes)
        garment_path.write_bytes(garment_bytes)

        return await asyncio.to_thread(
            _run_replicate_sync,
            human_path,
            garment_path,
            garment_des,
            category,
        )
