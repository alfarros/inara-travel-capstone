# backend/module_2_packages_reviews/app/database.py
import logging
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from contextlib import contextmanager

logger = logging.getLogger(__name__)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://admin:adminpass@postgres-db:5432/haji_umrah_db")

engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=3600)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

# Buat tabel jika belum ada
from . import models # Import model untuk memastikan tabel dibuat
Base.metadata.create_all(bind=engine)

@contextmanager
def get_db() -> Session:
    """Context manager untuk database session"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        db.close()
