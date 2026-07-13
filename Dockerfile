FROM python:3.12-slim

WORKDIR /app

# Runtime deps only — mock backend does not need torch/diffusers in the container.
COPY services/vton/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1
ENV HOST=0.0.0.0
ENV PORT=8000
ENV VTON_BACKEND=mock
ENV UPLOAD_DIR=/data/storage
ENV PYTHONPATH=/app/services/vton

EXPOSE 8000

CMD ["python", "app.py"]
