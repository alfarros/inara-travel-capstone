# app/database.py (Versi Pangkas)
import logging
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from contextlib import contextmanager

logger = logging.getLogger(__name__)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://admin:adminpass@postgres-db:5432/haji_umrah_db")

# SQLAlchemy setup
engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=3600)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

# (Semua model seperti AdminMessage, User, WebUser dihapus)

# ===== DATABASE SESSION HELPER =====
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

# (Semua fungsi seperti save_to_admin_queue, get_pending_messages, dll. dihapus)