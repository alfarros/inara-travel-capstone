# /module_2_recommender/app/main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .database import get_db, engine
from . import models, schemas
from fastapi.middleware.cors import CORSMiddleware # PENTING UNTUK CORS

# Buat tabel di DB jika belum ada
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API Rekomendasi & Paket (Modul 2)",
    description="Menyediakan data paket dan menerima ulasan (review).",
    version="1.0.0"
)

# --- TAMBAHKAN INI UNTUK MENGIZINKAN REACT MENGAKSES API ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Izinkan semua (atau ganti "http://localhost:5173" di production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ... (kode /recommend Anda yang sudah ada bisa tetap di sini) ...

# ===== ENDPOINT BARU UNTUK PAKET =====

@app.get("/packages", response_model=List[schemas.Package])
def get_all_packages(db: Session = Depends(get_db)):
    """
    Mengambil semua daftar paket umrah yang tersedia.
    """
    packages = db.query(models.Package).filter(models.Package.is_available == True).all()
    return packages

@app.get("/packages/{package_id}", response_model=schemas.Package)
def get_package_by_id(package_id: int, db: Session = Depends(get_db)):
    """
    Mengambil detail satu paket berdasarkan ID-nya.
    """
    package = db.query(models.Package).filter(models.Package.package_id == package_id).first()
    if not package:
        raise HTTPException(status_code=404, detail="Paket tidak ditemukan")
    return package

# ===== ENDPOINT BARU UNTUK REVIEW =====

@app.post("/packages/{package_id}/reviews", response_model=schemas.Review)
def create_review_for_package(
    package_id: int, 
    review: schemas.ReviewCreate, 
    db: Session = Depends(get_db)
):
    """
    Membuat review baru untuk sebuah paket.
    (Nantinya, user_id harus diambil dari token JWT, bukan dari body)
    """
    # Cek apakah paket ada
    db_package = db.query(models.Package).filter(models.Package.package_id == package_id).first()
    if not db_package:
        raise HTTPException(status_code=404, detail="Paket tidak ditemukan")
        
    db_review = models.Review(
        package_id=package_id,
        user_id=review.user_id,
        rating=review.rating,
        comment=review.comment
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review

@app.get("/packages/{package_id}/reviews", response_model=List[schemas.Review])
def get_reviews_for_package(package_id: int, db: Session = Depends(get_db)):
    """
    Mengambil semua review untuk sebuah paket.
    """
    reviews = db.query(models.Review).filter(models.Review.package_id == package_id).all()
    return reviews