# VirtuaLook — AI Virtual Try-On Engine

**AI Virtual Try-On**: cho ảnh người + ảnh trang phục → sinh ảnh composite photorealistic người mặc đồ đó.

Trọng tâm kỹ thuật là **ML inference service** (`services/vton/app`); `frontend/` là **demo UI** (HTML/JS, không cần npm) — mở qua server, **không** mở file `.html` trực tiếp.

## UI — mở trình duyệt sau khi chạy server

| Trang | URL | Dùng để |
|-------|-----|---------|
| **Trang chủ** (catalogue) | http://127.0.0.1:8000/ | Chọn trang phục → Thử đồ |
| **Thử đồ** | http://127.0.0.1:8000/tryon | Upload ảnh + chạy try-on |
| **Quản trị** | http://127.0.0.1:8000/admin | Xem jobs, thống kê |
| Tính năng | http://127.0.0.1:8000/features | |
| Hướng dẫn | http://127.0.0.1:8000/guide | |

**Luồng test nhanh:** Trang chủ → chọn áo → **Thử đồ** → upload ảnh toàn thân → **Bắt đầu thử đồ** → chờ vài giây (mock mode) → xem kết quả.

## Chạy với Docker (khuyên dùng cho demo)

```bash
docker compose up --build
```

Mở **http://localhost:8000** — backend mock (không cần GPU/weights). Dữ liệu lưu volume `virtulook_data`.

## Chạy local (mock — nhanh nhất)

```bash
cd VirtuaLook

# Bước 1: tạo venv (bắt buộc — Ubuntu chặn pip global)
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Bước 2: chạy (dùng python3, không phải python)
VTON_BACKEND=mock python3 app.py
```

Hoặc một lệnh: `bash scripts/run.sh`

Mở **http://127.0.0.1:8000**

## Chạy local (CatVTON thật)

```bash
cd services/vton
python -m venv .venv && source .venv/bin/activate
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt
bash download-models.sh
uvicorn app.main:app --reload --port 8000
```

CPU: ~5–15 phút/ảnh. CUDA: nhanh hơn nhiều (`DEVICE=auto`).

## Trang web

| URL | Nội dung |
|-----|----------|
| `/` | Trang chủ + catalogue trang phục |
| `/features` | Tính năng |
| `/guide` | Hướng dẫn cài đặt |
| `/pricing` | Bảng giá (demo) |
| `/about` | Về dự án & roadmap |
| `/tryon` | Luồng thử đồ |
| `/admin` | Dashboard quản trị |

## Luồng sử dụng

1. Trang chủ → chọn trang phục → **Thử đồ**
2. Upload ảnh toàn thân
3. **Bắt đầu thử đồ** → poll trạng thái job
4. Xem kết quả + lịch sử tại `/admin`

## REST API

| Endpoint | Mô tả |
|----------|-------|
| `GET /health`, `GET /api/health` | Backend, device, model status |
| `GET /api/garments` | Danh sách trang phục |
| `POST /api/garments` | Thêm trang phục (URL ảnh) |
| `POST /api/photos` | Upload ảnh người (multipart) |
| `POST /api/tryon` | Tạo job try-on `{garment_id, photo_id}` |
| `GET /api/tryon/{id}` | Poll trạng thái job |
| `GET /api/admin/stats` | Thống kê dashboard |

## Backend inference

| Backend | Mô tả | Yêu cầu |
|---------|-------|---------|
| `replicate` | IDM-VTON cloud (~30–60s) | `REPLICATE_API_TOKEN` |
| `catvton` | CatVTON local (offline) | SD + CatVTON weights |
| `mock` | PIL overlay (dev) | — |

`VTON_BACKEND=auto` (mặc định): Replicate → CatVTON → mock.

## Kiến trúc

| File / thư mục | Mô tả |
|----------------|-------|
| `app.py` | Entrypoint gốc (`python app.py`) |
| `services/vton/app/main.py` | FastAPI app + lifespan |
| `services/vton/app/inference.py` | Backend resolution + orchestration |
| `services/vton/app/catvton_runner.py` | CatVTON diffusion (thread pool, GPU) |
| `services/vton/app/replicate_runner.py` | Replicate IDM-VTON client |
| `services/vton/app/site_pages.py` | Marketing + app page routes |
| `services/vton/app/routers/` | REST API (garments, photos, tryon, admin) |
| `services/vton/app/database.py` | SQLite + SQLAlchemy |
| `frontend/` | Demo UI (HTML/JS/Tailwind CDN) |
| `tests/` | Pytest (mock backend, không load ML) |

## Pipeline CatVTON

```
person + garment → concat side-by-side → SD v1.5 inpainting UNet
  (+ CatVTON attention weights) → crop person side → kết quả
```

## Cấu hình

| Biến | Mặc định | Mô tả |
|------|-----------|-------|
| `VTON_BACKEND` | `auto` | `auto` \| `replicate` \| `catvton` \| `mock` |
| `MOCK_MODE` | `false` | `true` → bắt buộc mock |
| `DEVICE` | `auto` | `auto` \| `cuda` \| `cpu` |
| `REPLICATE_API_TOKEN` | — | Token Replicate |
| `INFERENCE_STEPS` | `20` | Diffusion steps |
| `UPLOAD_DIR` | `../../storage` | Storage root |
| `CATVTON_CHECKPOINT` | `vitonhd-16k-512` | Checkpoint variant |

Xem đầy đủ: `services/vton/.env.example`

## Test

```bash
pip install -r requirements-dev.txt
python -m pytest
```

11 tests — API integration + mock inference, không cần GPU/API key.

## Ghi chú

- Không có auth/thanh toán — dự án demo/portfolio.
- Model weights **không** commit git — tải bằng `download-models.sh`.
- Frontend không cần npm/build step.

## License

Demo project for learning and local development.
