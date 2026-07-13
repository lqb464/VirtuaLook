import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
STORAGE_DIR = Path(os.getenv("UPLOAD_DIR", str(BASE_DIR / "storage")))
STORAGE_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = STORAGE_DIR / "virtulook.db"
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DB_PATH}")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    from . import models  # noqa: F401 — ensure models are registered
    Base.metadata.create_all(bind=engine)
    # Add is_default column to existing person_photos tables that predate it
    with engine.connect() as conn:
        cols = [row[1] for row in conn.execute(
            __import__("sqlalchemy").text("PRAGMA table_info(person_photos)")
        )]
        if "is_default" not in cols:
            conn.execute(__import__("sqlalchemy").text(
                "ALTER TABLE person_photos ADD COLUMN is_default INTEGER NOT NULL DEFAULT 0"
            ))
            conn.commit()
