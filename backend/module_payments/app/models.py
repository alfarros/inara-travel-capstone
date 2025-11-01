# /module_payments/app/models.py
from sqlalchemy import Column, Integer, String, Text, DateTime, BIGINT, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

# ========================
# MODEL USER
# ========================
class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    phone_number = Column(String(20))
    hashed_password = Column(String(255))

    # Relasi
    bookings = relationship("Booking", back_populates="user")


# ========================
# MODEL PACKAGE
# ========================
class Package(Base):
    __tablename__ = "packages"

    package_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    price = Column(BIGINT, nullable=False)
    duration_days = Column(Integer)
    image_url = Column(String(500))

    # Relasi
    bookings = relationship("Booking", back_populates="package")


# ========================
# MODEL BOOKING
# ========================
class Booking(Base):
    __tablename__ = "bookings"

    booking_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    package_id = Column(Integer, ForeignKey("packages.package_id"), nullable=False)
    order_id = Column(String(255), unique=True, nullable=False)
    total_amount = Column(BIGINT, nullable=False)
    status = Column(String(50), default="pending")
    midtrans_redirect_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relasi
    user = relationship("User", back_populates="bookings")
    package = relationship("Package", back_populates="bookings")
