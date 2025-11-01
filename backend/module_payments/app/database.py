# /module_payments/app/database.py - VERSI PERBAIKAN
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
import logging
import time
from .models import Base  # <<< Import Base dari models.py

logger = logging.getLogger(__name__)

# Ambil konfigurasi DB dari environment variables
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://admin:adminpass@postgres-db:5432/haji_umrah_db")

engine = None
SessionLocal = None

def initialize_database():
    """Mencoba membuat koneksi engine dan session factory."""
    global engine, SessionLocal
    if engine is None:
        logger.info("Mencoba menginisialisasi koneksi database untuk Modul Pembayaran...")
        for i in range(5): # Coba beberapa kali
            try:
                engine = create_engine(DATABASE_URL, pool_pre_ping=True)
                # Tes koneksi
                with engine.connect() as connection:
                    connection.execute(text("SELECT 1"))
                SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
                
                # Membuat tabel (jika belum ada) menggunakan Base dari models.py
                Base.metadata.create_all(bind=engine) 
                
                logger.info("Koneksi database (SQLAlchemy Engine & SessionLocal) berhasil dibuat.")
                break # Keluar loop jika sukses
            except Exception as e:
                logger.warning(f"Koneksi DB gagal (percobaan {i+1}/5): {e}. Menunggu 3 detik...")
                engine = None
                SessionLocal = None
                time.sleep(3)
        if engine is None:
             logger.error("Gagal total terhubung ke database setelah beberapa percobaan.")

initialize_database()

def get_db():
    """Menyediakan session database per request."""
    if SessionLocal is None:
         raise RuntimeError("Koneksi database tidak tersedia.")

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()