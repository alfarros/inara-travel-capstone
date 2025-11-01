# /module_2_recommender/app/models.py
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, BIGINT, FLOAT, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    # ... (kolom user lain jika diperlukan oleh modul ini)
    
    reviews = relationship("Review", back_populates="user")
    bookings = relationship("Booking", back_populates="user")

class Package(Base):
    __tablename__ = "packages"
    package_id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    price = Column(BIGINT, nullable=False)
    duration_days = Column(Integer)
    hotel_info = Column(String(500))
    image_url = Column(String(500))
    
    reviews = relationship("Review", back_populates="package")
    bookings = relationship("Booking", back_populates="package")

class Review(Base):
    __tablename__ = "reviews"
    review_id = Column(Integer, primary_key=True)
    package_id = Column(Integer, ForeignKey("packages.package_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(Text)
    sentiment_status = Column(String(50), default="pending")
    sentiment_score = Column(FLOAT)
    created_at = Column(DateTime, default=datetime.now)
    
    package = relationship("Package", back_populates="reviews")
    user = relationship("User", back_populates="reviews")

class Booking(Base):
    __tablename__ = "bookings"
    booking_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    package_id = Column(Integer, ForeignKey("packages.package_id"), nullable=False)
    order_id = Column(String(255), unique=True, nullable=False)
    total_amount = Column(BIGINT, nullable=False)
    status = Column(String(50), default="pending")
    
    user = relationship("User", back_populates="bookings")
    package = relationship("Package", back_populates="bookings")