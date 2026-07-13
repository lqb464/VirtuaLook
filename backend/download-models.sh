#!/usr/bin/env bash
# Download CatVTON + SD v1.5 inpainting weights for local inference.
# Run from services/vton/ with the venv activated.
set -eu

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WEIGHTS_DIR="$SCRIPT_DIR/weights"
CHECKPOINT="${CATVTON_CHECKPOINT:-vitonhd-16k-512}"

echo "=== VirtuaLook — Download Model Weights ==="
echo ""

if ! command -v hf &>/dev/null; then
    echo "Installing huggingface_hub..."
    pip install -q "huggingface_hub[cli]" -U
fi

# ── CatVTON attention weights ─────────────────────────────────────────────────
CATVTON_DIR="$WEIGHTS_DIR/catvton"
ATTN_FILE="$CATVTON_DIR/$CHECKPOINT/attention/model.safetensors"
if [ -f "$ATTN_FILE" ]; then
    echo "[skip] CatVTON attention weights already exist at $ATTN_FILE"
else
    echo "Downloading CatVTON attention weights only (~190MB, checkpoint: $CHECKPOINT)..."
    mkdir -p "$CATVTON_DIR/$CHECKPOINT/attention"
    hf download zhengchong/CatVTON \
        "$CHECKPOINT/attention/model.safetensors" \
        --local-dir "$CATVTON_DIR"
    echo "[done] CatVTON weights saved to $CATVTON_DIR"
fi

# ── Stable Diffusion v1.5 Inpainting base ─────────────────────────────────────
SD_DIR="$WEIGHTS_DIR/sd-inpaint"
UNET_WEIGHT=$(find "$SD_DIR/unet" -maxdepth 1 \( -name '*.safetensors' -o -name '*.bin' \) 2>/dev/null | head -1 || true)
if [ -n "$UNET_WEIGHT" ]; then
    echo "[skip] SD v1.5 inpainting UNet already exists at $UNET_WEIGHT"
else
    echo "Downloading Stable Diffusion v1.5 Inpainting base (~7GB, one-time)..."
    mkdir -p "$SD_DIR"
    hf download runwayml/stable-diffusion-inpainting \
        --local-dir "$SD_DIR" \
        --max-workers 8
    echo "[done] SD v1.5 inpainting saved to $SD_DIR"
fi

echo ""
echo "=== Download complete! ==="
echo ""
echo "Verify:"
echo "  ls $ATTN_FILE"
echo "  ls $SD_DIR/unet/*.safetensors 2>/dev/null || ls $SD_DIR/unet/*.bin"
echo ""
echo "Next: uvicorn app.main:app --reload --port 8000"
