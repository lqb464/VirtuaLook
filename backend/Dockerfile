# VirtuaLook API (build context = ./backend)
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . ./backend/

ENV HOST=0.0.0.0
ENV PORT=8000
ENV VTON_BACKEND=mock
ENV UPLOAD_DIR=/app/storage
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["python", "-m", "backend"]
