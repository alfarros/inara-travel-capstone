# /module_1_chatbot/app/models.py
from sqlalchemy import Column, Integer, String, Text, BigInteger, ForeignKey, CheckConstraint, DateTime
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class Package(Base):
    __tablename__ = "packages"

    package_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    price = Column(BigInteger, nullable=False)
    duration_days = Column(Integer)
    hotel_info = Column(String(500))
    image_url = Column(String(500))
    destination = Column(String(255))
    category = Column(String(100))

    # Relasi ke tabel reviews
    reviews = relationship("Review", back_populates="package", cascade="all, delete-orphan")

class Review(Base):
    __tablename__ = "reviews"

    review_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer) # Bisa jadi Foreign Key ke tabel user nanti
    package_id = Column(Integer, ForeignKey("packages.package_id"), nullable=True) # ON DELETE SET NULL
    review_text = Column(Text, nullable=False)
    rating = Column(Integer, CheckConstraint('rating >= 1 AND rating <= 5'))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relasi ke tabel packages
    package = relationship("Package", back_populates="reviews")

# Jangan lupa untuk mengimpor model ini di database.py agar tabel dibuat
# File: backend/module_1_chatbot/app/database.py
# Tambahkan baris ini di akhir file:
# from .models import Package, Review # <-- Tambahkan baris ini
# Base = declarative_base()
# ... (sisa kode database.py)