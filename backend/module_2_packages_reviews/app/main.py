# backend/module_2_packages_reviews/app/main.py
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
from . import models, schemas, database # Impor dari modul ini sendiri
import sqlalchemy.exc

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Packages & Reviews API (Modul 2)",
    description="API untuk manajemen paket wisata dan ulasan",
    version="1.0.0"
)

# --- TAMBAHKAN/PERBAIKI Middleware CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"], # <-- Pastikan ini sesuai dengan origin frontend Anda
    allow_credentials=True,
    allow_methods=["*"], # Atau lebih spesifik seperti ["GET", "POST"]
    allow_headers=["*"], # Atau lebih spesifik jika perlu
)

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Health Check
@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Get All Packages
@app.get("/packages", response_model=schemas.AllPackagesResponse)
def get_all_packages(db: Session = Depends(get_db)):
    try:
        packages = db.query(models.Package).all()
        return schemas.AllPackagesResponse(packages=packages)
    except Exception as e:
        logger.error(f"❌ Error mengambil semua paket: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Gagal mengambil data paket.")

# Get Package Detail
@app.get("/packages/{package_id}", response_model=schemas.PackageDetailResponse)
def get_package_detail(package_id: int, db: Session = Depends(get_db)):
    try:
        package = db.query(models.Package).filter(models.Package.package_id == package_id).first()
        if not package:
            raise HTTPException(status_code=404, detail="Paket tidak ditemukan.")
        return package
    except Exception as e:
        logger.error(f"❌ Error mengambil detail paket {package_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Gagal mengambil detail paket.")

# Create Review
@app.post("/reviews", response_model=schemas.Review, status_code=201)
def create_review(review_data: schemas.ReviewCreate, db: Session = Depends(get_db)):
    try:
        # Cek apakah paket yang dituju ada
        package = db.query(models.Package).filter(models.Package.package_id == review_data.package_id).first()
        if not package:
            raise HTTPException(status_code=404, detail="Paket untuk review ini tidak ditemukan.")

        # Buat objek Review SQLAlchemy
        # Gunakan reviewer_name dari request body, atau default ke "Anonim"
        reviewer_name = review_data.reviewer_name if review_data.reviewer_name else "Anonim"
        db_review = models.Review(
            reviewer_name=reviewer_name, # Gunakan reviewer_name
            package_id=review_data.package_id,
            review_text=review_data.review_text,
            rating=review_data.rating
        )
        db.add(db_review)
        db.commit()
        db.refresh(db_review)

        return db_review
    except sqlalchemy.exc.IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Data review tidak valid (rating mungkin tidak sesuai).")
    except Exception as e:
        logger.error(f"❌ Error membuat review: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail="Gagal membuat review.")
