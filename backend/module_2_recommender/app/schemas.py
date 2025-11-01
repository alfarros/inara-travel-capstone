# /module_2_recommender/app/schemas.py
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# --- Package Schemas ---
class PackageBase(BaseModel):
    name: str
    price: int
    duration_days: Optional[int] = None
    hotel_info: Optional[str] = None
    image_url: Optional[str] = None

class Package(PackageBase):
    package_id: int

    class Config:
        from_attributes = True # <<< INI PERBAIKANNYA

# --- Review Schemas ---
class ReviewCreate(BaseModel):
    user_id: int # Nanti ini akan diambil dari token otentikasi
    rating: int
    comment: Optional[str] = None

class Review(BaseModel):
    review_id: int
    user_id: int
    rating: int
    comment: Optional[str] = None
    created_at: datetime
    
    class Config:
       from_attributes = True