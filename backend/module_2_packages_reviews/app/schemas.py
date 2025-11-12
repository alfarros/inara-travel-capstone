# backend/module_2_packages_reviews/app/schemas.py
from pydantic import BaseModel
from typing import Optional, List # Tambahkan List
from datetime import datetime

# --- Schema untuk Packages dan Reviews - Diperbarui ---
class PackageBase(BaseModel):
    name: str
    duration: Optional[str] = None                    # Tambahkan
    price: int
    features: Optional[List[str]] = []               # Tambahkan, default ke list kosong
    image_url: Optional[str] = None
    featured: Optional[bool] = False                 # Tambahkan
    description: Optional[str] = None
    airline: Optional[str] = None                    # Tambahkan
    departure_city: Optional[str] = None             # Tambahkan

    # Kolom lama
    duration_days: Optional[int] = None
    hotel_info: Optional[str] = None
    destination: Optional[str] = None
    category: Optional[str] = None

class Package(PackageBase):
    package_id: int
    class Config:
        from_attributes = True # Ini penting agar Pydantic bisa membaca dari objek SQLAlchemy

class ReviewBase(BaseModel):
    # user_id: Optional[int] = None # Kita ganti ini
    reviewer_name: Optional[str] = "Anonim" # Tambahkan field nama reviewer
    review_text: str
    rating: int

class Review(ReviewBase):
    review_id: int
    package_id: int
    created_at: datetime
    class Config:
        from_attributes = True

class ReviewCreate(ReviewBase): # Schema untuk permintaan pembuatan review
    package_id: int # Diperlukan saat membuat review
    # Kita hapus user_id, gunakan reviewer_name

class PackageWithReviews(Package):
    reviews: List[Review] = []

class AllPackagesResponse(BaseModel):
    packages: List[Package]

class PackageDetailResponse(PackageWithReviews):
    pass

# Schema untuk endpoint /chat (sudah ada sebelumnya, biarkan jika tidak diubah)
# class ChatRequest(BaseModel):
#     # ...
# class ChatResponse(BaseModel):
#     # ...
