# backend/module_2_packages_reviews/app/models.py
from sqlalchemy import Column, Integer, String, Text, BigInteger, ForeignKey, CheckConstraint, DateTime, Boolean, ARRAY
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class Package(Base):
    __tablename__ = "packages"

    package_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)             # Sesuai: name
    duration = Column(String(100))                        # Tambahkan: duration string
    price = Column(BigInteger, nullable=False)            # Sesuai: price (angka)
    features = Column(ARRAY(String))                      # Tambahkan: PostgreSQL Array of String
    image_url = Column(String(500))                       # Sesuai: image_url
    featured = Column(Boolean, default=False)             # Tambahkan: featured (default false)
    description = Column(Text)                            # Sesuai
    airline = Column(String(255))                         # Tambahkan: airline
    departure_city = Column(String(255))                  # Tambahkan: departure_city (snake_case)

    # Kolom lama
    duration_days = Column(Integer)                       # Bisa dipertahankan
    hotel_info = Column(String(500))                      # Bisa dipertahankan
    destination = Column(String(255))                     # Bisa dipertahankan
    category = Column(String(100))                        # Bisa dipertahankan

    # Relasi ke tabel reviews
    reviews = relationship("Review", back_populates="package", cascade="all, delete-orphan")

class Review(Base):
    __tablename__ = "reviews"

    review_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    package_id = Column(Integer, ForeignKey("packages.package_id"), nullable=True) # ON DELETE SET NULL
    review_text = Column(Text, nullable=False)
    rating = Column(Integer, CheckConstraint('rating >= 1 AND rating <= 5'))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relasi ke tabel packages
    package = relationship("Package", back_populates="reviews")
