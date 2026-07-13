#!/usr/bin/env bash
# Start VirtuaLook in mock mode (no GPU / no model weights needed).
set -eu
cd "$(dirname "$0")/.."

VENV=".venv"
if [ ! -d "$VENV" ]; then
  echo "Creating virtualenv at $VENV ..."
  python3 -m venv "$VENV"
  "$VENV/bin/pip" install -q --upgrade pip
  "$VENV/bin/pip" install -q -r requirements.txt
fi

export VTON_BACKEND="${VTON_BACKEND:-mock}"
export MOCK_MODE="${MOCK_MODE:-true}"
export HOST="${HOST:-127.0.0.1}"
export PORT="${PORT:-8000}"

echo "VirtuaLook → http://${HOST}:${PORT}  (backend=${VTON_BACKEND})"
exec "$VENV/bin/python" app.py
