#!/usr/bin/env python3
"""VirtuaLook entrypoint — starts the VTON FastAPI service."""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VTON_DIR = ROOT / "services" / "vton"
sys.path.insert(0, str(VTON_DIR))

# Load .env from services/vton if present
from dotenv import load_dotenv

load_dotenv(VTON_DIR / ".env")


def main() -> None:
    import uvicorn

    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8004"))
    reload = os.getenv("RELOAD", "").lower() in ("1", "true", "yes")
    uvicorn.run("app.main:app", host=host, port=port, reload=reload)


if __name__ == "__main__":
    main()
