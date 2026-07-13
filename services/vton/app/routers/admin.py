from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Garment, TryOnJob

router = APIRouter(prefix="/api/admin", tags=["admin"])


class StatsOut(BaseModel):
    total_garments: int
    total_jobs: int
    done_jobs: int
    failed_jobs: int
    success_rate: float


class JobOut(BaseModel):
    id: str
    status: str
    garment_name: str | None
    result_url: str | None
    error: str | None
    created_at: str

    model_config = {"from_attributes": True}


@router.get("/stats", response_model=StatsOut)
def get_stats(db: Session = Depends(get_db)):
    total_garments = db.query(Garment).count()
    total_jobs = db.query(TryOnJob).count()
    done_jobs = db.query(TryOnJob).filter(TryOnJob.status == "done").count()
    failed_jobs = db.query(TryOnJob).filter(TryOnJob.status == "failed").count()
    success_rate = round(done_jobs / total_jobs * 100, 1) if total_jobs > 0 else 0.0

    return StatsOut(
        total_garments=total_garments,
        total_jobs=total_jobs,
        done_jobs=done_jobs,
        failed_jobs=failed_jobs,
        success_rate=success_rate,
    )


@router.get("/jobs", response_model=list[JobOut])
def list_jobs(db: Session = Depends(get_db)):
    jobs = db.query(TryOnJob).order_by(TryOnJob.created_at.desc()).limit(100).all()
    return [
        JobOut(
            id=j.id,
            status=j.status,
            garment_name=j.garment.name if j.garment else None,
            result_url=j.result_url,
            error=j.error,
            created_at=j.created_at.isoformat() if j.created_at else "",
        )
        for j in jobs
    ]
