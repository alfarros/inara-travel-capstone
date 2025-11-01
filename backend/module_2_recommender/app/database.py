# /module_2_recommender/app/database.py
import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager

logger = logging.getLogger(__name__)

# Ambil URL database dari docker-compose environment
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://admin:adminpass@postgres-db:5432/haji_umrah_db")

try:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    logger.info("✅ Koneksi database (recommender-api) siap.")
except Exception as e:
    logger.error(f"❌ Gagal koneksi database (recommender-api): {e}")
    SessionLocal = None

@contextmanager
def get_db() -> Session:
    """Context manager untuk database session"""
    if SessionLocal is None:
        raise Exception("Database tidak terkonfigurasi")
    
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