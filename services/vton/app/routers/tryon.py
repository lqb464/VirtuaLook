import asyncio
import uuid
import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Garment, PersonPhoto, TryOnJob
from ..inference import run_inference
from .photos import resolve_photo_path

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/tryon", tags=["tryon"])


class TryOnRequest(BaseModel):
    garment_id: str
    photo_id: str


class TryOnOut(BaseModel):
    id: str
    status: str
    result_url: str | None
    error: str | None
    garment_name: str | None = None

    model_config = {"from_attributes": True}


def _job_out(job: TryOnJob) -> TryOnOut:
    return TryOnOut(
        id=job.id,
        status=job.status,
        result_url=job.result_url,
        error=job.error,
        garment_name=job.garment.name if job.garment else None,
    )


async def _run_job(job_id: str, person_url: str, garment_url: str, garment_des: str, category: str):
    from ..database import SessionLocal
    db = SessionLocal()
    try:
        job = db.query(TryOnJob).filter(TryOnJob.id == job_id).first()
        if not job:
            return
        job.status = "processing"
        db.commit()

        result_url = await run_inference(
            person_url,
            garment_url,
            job_id,
            garment_des,
            category,
        )
        job.status = "done"
        job.result_url = result_url
    except Exception as exc:
        logger.exception("Try-on job %s failed", job_id)
        job = db.query(TryOnJob).filter(TryOnJob.id == job_id).first()
        if job:
            job.status = "failed"
            job.error = str(exc)
    finally:
        db.commit()
        db.close()


@router.post("", response_model=TryOnOut)
async def create_job(body: TryOnRequest, db: Session = Depends(get_db)):
    garment = db.query(Garment).filter(Garment.id == body.garment_id).first()
    if not garment:
        raise HTTPException(status_code=404, detail="Garment not found")

    photo = db.query(PersonPhoto).filter(PersonPhoto.id == body.photo_id).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    job_id = uuid.uuid4().hex
    job = TryOnJob(
        id=job_id,
        garment_id=garment.id,
        person_photo_id=photo.id,
        person_image_path=photo.file_path,
        status="queued",
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    person_url = str(resolve_photo_path(photo.file_path))
    garment_url = garment.image_url

    asyncio.create_task(_run_job(job_id, person_url, garment_url, garment.description or garment.name, garment.category))

    return _job_out(job)


@router.get("/history", response_model=list[TryOnOut])
def get_history(db: Session = Depends(get_db)):
    jobs = db.query(TryOnJob).order_by(TryOnJob.created_at.desc()).limit(50).all()
    return [_job_out(j) for j in jobs]


@router.get("/{job_id}", response_model=TryOnOut)
def get_job(job_id: str, db: Session = Depends(get_db)):
    job = db.query(TryOnJob).filter(TryOnJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return _job_out(job)
