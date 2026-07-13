import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
WEIGHTS_DIR = BASE_DIR / "weights"

MODEL_DIR = Path(os.getenv("MODEL_DIR", WEIGHTS_DIR / "idm-vton"))
CATVTON_DIR = Path(os.getenv("CATVTON_DIR", WEIGHTS_DIR / "catvton"))
# Attention weights subdir — vitonhd-16k-512 (512px, balanced) or mix-48k-1024 (1024px, higher quality)
CATVTON_CHECKPOINT = os.getenv("CATVTON_CHECKPOINT", "vitonhd-16k-512")
CATVTON_ATTN_DIR = CATVTON_DIR / CATVTON_CHECKPOINT / "attention"
SD_INPAINT_DIR = Path(os.getenv("SD_INPAINT_DIR", WEIGHTS_DIR / "sd-inpaint"))

_upload = os.getenv("UPLOAD_DIR")
if _upload:
    UPLOAD_DIR = Path(_upload)
    if not UPLOAD_DIR.is_absolute():
        UPLOAD_DIR = (BASE_DIR / UPLOAD_DIR).resolve()
else:
    UPLOAD_DIR = (BASE_DIR.parent.parent / "storage").resolve()
RESULTS_DIR = UPLOAD_DIR / "try-on-results"

DEVICE_SETTING = os.getenv("DEVICE", "auto")
# Force mock overlay when true/1/yes — useful for UI dev without any model weights.
MOCK_MODE = os.getenv("MOCK_MODE", "false").lower() in ("true", "1", "yes")
VTON_BACKEND = os.getenv("VTON_BACKEND", "auto")  # auto | replicate | catvton | mock

# Number of diffusion steps for CatVTON (20 = fast/balanced, 50 = higher quality)
INFERENCE_STEPS = int(os.getenv("INFERENCE_STEPS", "20"))
# Resolution for CatVTON — reduce to 384x512 if OOM
INFERENCE_WIDTH = int(os.getenv("INFERENCE_WIDTH", "512"))
INFERENCE_HEIGHT = int(os.getenv("INFERENCE_HEIGHT", "768"))

RESULTS_DIR.mkdir(parents=True, exist_ok=True)
