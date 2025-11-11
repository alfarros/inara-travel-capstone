# backend/module_2_packages_reviews/app/schemas.py
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# --- Schema untuk Packages dan Reviews ---
class PackageBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: int
    duration_days: Optional[int] = None
    hotel_info: Optional[str] = None
    image_url: Optional[str] = None
    destination: Optional[str] = None
    category: Optional[str] = None

class Package(PackageBase):
    package_id: int
    class Config:
        from_attributes = True

class ReviewBase(BaseModel):
    user_id: Optional[int] = None
    review_text: str
    rating: int

class Review(ReviewBase):
    review_id: int
    package_id: int
    created_at: datetime
    class Config:
        from_attributes = True

class ReviewCreate(ReviewBase):
    package_id: int

class PackageWithReviews(Package):
    reviews: List[Review] = []

class AllPackagesResponse(BaseModel):
    packages: List[Package]

class PackageDetailResponse(PackageWithReviews):
    pass
