import uuid
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..config import UPLOAD_DIR
from ..database import get_db
from ..models import PersonPhoto

router = APIRouter(prefix="/api/photos", tags=["photos"])

PHOTOS_DIR = UPLOAD_DIR / "person-photos"
PHOTOS_DIR.mkdir(parents=True, exist_ok=True)


class PhotoOut(BaseModel):
    id: str
    file_path: str
    label: str
    is_default: bool
    url: str

    model_config = {"from_attributes": True}


class PhotoUpdate(BaseModel):
    label: Optional[str] = None
    is_default: Optional[bool] = None


def resolve_photo_path(file_path: str) -> Path:
    """Resolve a stored photo path across OSes (DB may hold old absolute paths)."""
    raw = Path(file_path)
    if raw.is_file():
        return raw.resolve()
    candidate = PHOTOS_DIR / raw.name
    if candidate.is_file():
        return candidate.resolve()
    raise FileNotFoundError(f"Cannot load image: {file_path}")


def _photo_url(file_path: str) -> str:
    return f"/storage/person-photos/{Path(file_path).name}"


def _to_out(p: PersonPhoto) -> PhotoOut:
    return PhotoOut(
        id=p.id,
        file_path=p.file_path,
        label=p.label,
        is_default=bool(p.is_default),
        url=_photo_url(p.file_path),
    )


@router.get("", response_model=list[PhotoOut])
def list_photos(db: Session = Depends(get_db)):
    photos = db.query(PersonPhoto).order_by(PersonPhoto.created_at.desc()).all()
    return [_to_out(p) for p in photos]


@router.get("/{photo_id}", response_model=PhotoOut)
def get_photo(photo_id: str, db: Session = Depends(get_db)):
    photo = db.query(PersonPhoto).filter(PersonPhoto.id == photo_id).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    return _to_out(photo)


@router.post("", response_model=PhotoOut)
async def upload_photo(
    file: UploadFile = File(...),
    label: str = Form(""),
    db: Session = Depends(get_db),
):
    ext = Path(file.filename or "photo.jpg").suffix or ".jpg"
    filename = f"{uuid.uuid4().hex}{ext}"
    dest = PHOTOS_DIR / filename
    dest.write_bytes(await file.read())

    # Make the first uploaded photo the default automatically
    is_first = db.query(PersonPhoto).count() == 0
    # Store filename only so paths stay portable across machines/OS.
    photo = PersonPhoto(id=uuid.uuid4().hex, file_path=filename, label=label, is_default=is_first)
    db.add(photo)
    db.commit()
    db.refresh(photo)
    return _to_out(photo)


@router.patch("/{photo_id}", response_model=PhotoOut)
def update_photo(photo_id: str, update: PhotoUpdate, db: Session = Depends(get_db)):
    photo = db.query(PersonPhoto).filter(PersonPhoto.id == photo_id).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    if update.label is not None:
        photo.label = update.label
    if update.is_default is True:
        db.query(PersonPhoto).filter(PersonPhoto.is_default.is_(True)).update({"is_default": False})
        photo.is_default = True
    db.commit()
    db.refresh(photo)
    return _to_out(photo)


@router.delete("/{photo_id}")
def delete_photo(photo_id: str, db: Session = Depends(get_db)):
    photo = db.query(PersonPhoto).filter(PersonPhoto.id == photo_id).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    was_default = bool(photo.is_default)
    try:
        resolve_photo_path(photo.file_path).unlink(missing_ok=True)
    except Exception:
        pass
    db.delete(photo)
    db.commit()
    # Promote the newest remaining photo as default if we deleted the default
    if was_default:
        next_photo = db.query(PersonPhoto).order_by(PersonPhoto.created_at.desc()).first()
        if next_photo:
            next_photo.is_default = True
            db.commit()
    return {"ok": True}
