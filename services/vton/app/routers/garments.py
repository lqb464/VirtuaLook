import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Garment

router = APIRouter(prefix="/api/garments", tags=["garments"])


class GarmentCreate(BaseModel):
    name: str
    category: str = "tops"
    image_url: str
    description: Optional[str] = ""


class GarmentOut(BaseModel):
    id: str
    name: str
    category: str
    image_url: str
    description: str

    model_config = {"from_attributes": True}


@router.get("", response_model=list[GarmentOut])
def list_garments(db: Session = Depends(get_db)):
    return db.query(Garment).all()


@router.post("", response_model=GarmentOut)
def create_garment(body: GarmentCreate, db: Session = Depends(get_db)):
    garment = Garment(id=uuid.uuid4().hex, **body.model_dump())
    db.add(garment)
    db.commit()
    db.refresh(garment)
    return garment


@router.delete("/{garment_id}")
def delete_garment(garment_id: str, db: Session = Depends(get_db)):
    garment = db.query(Garment).filter(Garment.id == garment_id).first()
    if not garment:
        raise HTTPException(status_code=404, detail="Garment not found")
    db.delete(garment)
    db.commit()
    return {"ok": True}
