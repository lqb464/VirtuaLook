import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship

from .database import Base


def _new_id() -> str:
    return uuid.uuid4().hex


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Garment(Base):
    __tablename__ = "garments"

    id = Column(String, primary_key=True, default=_new_id)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False, default="tops")
    image_url = Column(String, nullable=False)
    description = Column(Text, default="")

    jobs = relationship("TryOnJob", back_populates="garment", cascade="all, delete-orphan")


class PersonPhoto(Base):
    __tablename__ = "person_photos"

    id = Column(String, primary_key=True, default=_new_id)
    file_path = Column(String, nullable=False)
    label = Column(String, default="")
    is_default = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=_now)

    jobs = relationship("TryOnJob", back_populates="person_photo")


class TryOnJob(Base):
    __tablename__ = "tryon_jobs"

    id = Column(String, primary_key=True, default=_new_id)
    garment_id = Column(String, ForeignKey("garments.id"), nullable=False)
    person_photo_id = Column(String, ForeignKey("person_photos.id"), nullable=True)
    person_image_path = Column(String, nullable=False)
    status = Column(String, default="queued")  # queued | processing | done | failed
    result_url = Column(String, nullable=True)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=_now)

    garment = relationship("Garment", back_populates="jobs")
    person_photo = relationship("PersonPhoto", back_populates="jobs")
