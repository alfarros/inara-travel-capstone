# app/database.py - Production Version dengan PostgreSQL
from datetime import datetime
from typing import List, Dict, Optional
import logging
import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager

logger = logging.getLogger(__name__)

# Database URL dari environment
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://chatbot_user:chatbot_pass@postgres:5432/chatbot_db")

# SQLAlchemy setup
engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=3600)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

# ===== DATABASE MODELS =====
class AdminMessage(Base):
    """Model untuk menyimpan escalated messages"""
    __tablename__ = "admin_messages"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String(255), index=True, nullable=False)
    channel = Column(String(50), nullable=False)  # "web" atau "whatsapp"
    user_message = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=False)
    escalation_reason = Column(String(500), nullable=False)
    user_contact = Column(String(255), nullable=True)  # Email atau nomor WA
    status = Column(String(50), default="pending", index=True)  # "pending" atau "resolved"
    admin_reply = Column(Text, nullable=True)
    admin_name = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    resolved_at = Column(DateTime, nullable=True)

class WebUser(Base):
    """Model untuk menyimpan web users (untuk email notification)"""
    __tablename__ = "web_users"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    email_verified = Column(Boolean, default=False)
    notification_enabled = Column(Boolean, default=True)

class User(Base):
    """Model untuk akun pelanggan (login/register)"""
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    phone_number = Column(String(20), unique=True)
    created_at = Column(DateTime, default=datetime.now)
    
# Buat semua tabel
try:
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Database tables created/verified successfully")
except Exception as e:
    logger.error(f"❌ Error creating database tables: {e}")

# ===== DATABASE SESSION HELPER =====
@contextmanager
def get_db() -> Session:
    """Context manager untuk database session"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        db.close()

# ===== ADMIN MESSAGE FUNCTIONS =====
def save_to_admin_queue(
    user_id: str, 
    channel: str, 
    message: str, 
    ai_response: str, 
    reason: str,
    user_contact: Optional[str] = None
) -> int:
    """Simpan message yang perlu ditangani admin ke PostgreSQL"""
    try:
        with get_db() as db:
            entry = AdminMessage(
                user_id=user_id,
                channel=channel,
                user_message=message,
                ai_response=ai_response,
                escalation_reason=reason,
                user_contact=user_contact,
                status="pending"
            )
            db.add(entry)
            db.flush()  # Untuk mendapatkan ID
            
            message_id = entry.id
            logger.info(f"📢 Message #{message_id} escalated: {user_id} via {channel} - Reason: {reason}")
            
            return message_id
            
    except Exception as e:
        logger.error(f"Error saving to admin queue: {e}", exc_info=True)
        raise

def get_pending_messages() -> List[Dict]:
    """Ambil semua pending messages dari database"""
    try:
        with get_db() as db:
            messages = db.query(AdminMessage).filter(
                AdminMessage.status == "pending"
            ).order_by(AdminMessage.created_at.desc()).all()
            
            return [
                {
                    "id": msg.id,
                    "user_id": msg.user_id,
                    "channel": msg.channel,
                    "user_message": msg.user_message,
                    "ai_response": msg.ai_response,
                    "escalation_reason": msg.escalation_reason,
                    "user_contact": msg.user_contact,
                    "status": msg.status,
                    "created_at": msg.created_at,
                    "admin_reply": msg.admin_reply,
                    "admin_name": msg.admin_name,
                    "resolved_at": msg.resolved_at
                }
                for msg in messages
            ]
    except Exception as e:
        logger.error(f"Error getting pending messages: {e}", exc_info=True)
        return []

def get_resolved_messages(limit: int = 50) -> List[Dict]:
    """Ambil resolved messages (terbaru dulu)"""
    try:
        with get_db() as db:
            messages = db.query(AdminMessage).filter(
                AdminMessage.status == "resolved"
            ).order_by(AdminMessage.resolved_at.desc()).limit(limit).all()
            
            return [
                {
                    "id": msg.id,
                    "user_id": msg.user_id,
                    "channel": msg.channel,
                    "user_message": msg.user_message,
                    "ai_response": msg.ai_response,
                    "escalation_reason": msg.escalation_reason,
                    "user_contact": msg.user_contact,
                    "status": msg.status,
                    "created_at": msg.created_at,
                    "admin_reply": msg.admin_reply,
                    "admin_name": msg.admin_name,
                    "resolved_at": msg.resolved_at
                }
                for msg in messages
            ]
    except Exception as e:
        logger.error(f"Error getting resolved messages: {e}", exc_info=True)
        return []

def get_message_by_id(message_id: int) -> Optional[Dict]:
    """Ambil message berdasarkan ID"""
    try:
        with get_db() as db:
            msg = db.query(AdminMessage).filter(AdminMessage.id == message_id).first()
            
            if not msg:
                return None
            
            return {
                "id": msg.id,
                "user_id": msg.user_id,
                "channel": msg.channel,
                "user_message": msg.user_message,
                "ai_response": msg.ai_response,
                "escalation_reason": msg.escalation_reason,
                "user_contact": msg.user_contact,
                "status": msg.status,
                "created_at": msg.created_at,
                "admin_reply": msg.admin_reply,
                "admin_name": msg.admin_name,
                "resolved_at": msg.resolved_at
            }
    except Exception as e:
        logger.error(f"Error getting message by ID: {e}", exc_info=True)
        return None

def update_message_status(
    message_id: int, 
    admin_reply: str, 
    admin_name: str = "Admin"
) -> bool:
    """Update status message setelah admin reply"""
    try:
        with get_db() as db:
            message = db.query(AdminMessage).filter(AdminMessage.id == message_id).first()
            
            if not message:
                logger.warning(f"Message #{message_id} not found")
                return False
            
            message.admin_reply = admin_reply
            message.admin_name = admin_name
            message.status = "resolved"
            message.resolved_at = datetime.now()
            
            logger.info(f"✅ Message #{message_id} resolved by {admin_name}")
            return True
            
    except Exception as e:
        logger.error(f"Error updating message status: {e}", exc_info=True)
        return False

def get_stats() -> Dict:
    """Get statistics untuk dashboard"""
    try:
        with get_db() as db:
            total = db.query(AdminMessage).count()
            pending = db.query(AdminMessage).filter(AdminMessage.status == "pending").count()
            resolved = db.query(AdminMessage).filter(AdminMessage.status == "resolved").count()
            
            # Hitung average response time
            resolved_msgs = db.query(AdminMessage).filter(
                AdminMessage.status == "resolved",
                AdminMessage.resolved_at.isnot(None)
            ).all()
            
            if resolved_msgs:
                response_times = [
                    (msg.resolved_at - msg.created_at).total_seconds() / 60
                    for msg in resolved_msgs
                ]
                avg_response_time = sum(response_times) / len(response_times)
            else:
                avg_response_time = 0
            
            return {
                "total_messages": total,
                "pending_count": pending,
                "resolved_count": resolved,
                "avg_response_time_minutes": round(avg_response_time, 1)
            }
    except Exception as e:
        logger.error(f"Error getting stats: {e}", exc_info=True)
        return {
            "total_messages": 0,
            "pending_count": 0,
            "resolved_count": 0,
            "avg_response_time_minutes": 0
        }

# ===== WEB USER FUNCTIONS (untuk email notification) =====
def save_web_user(email: str, name: Optional[str] = None) -> bool:
    """Simpan web user untuk email notification"""
    try:
        with get_db() as db:
            # Cek apakah user sudah ada
            existing = db.query(WebUser).filter(WebUser.email == email).first()
            if existing:
                logger.info(f"User {email} already exists")
                return True
            
            user = WebUser(email=email, name=name)
            db.add(user)
            logger.info(f"✅ Web user {email} saved")
            return True
            
    except Exception as e:
        logger.error(f"Error saving web user: {e}", exc_info=True)
        return False

def get_user_by_email(email: str) -> Optional[Dict]:
    """Ambil user berdasarkan email"""
    try:
        with get_db() as db:
            user = db.query(WebUser).filter(WebUser.email == email).first()
            
            if not user:
                return None
            
            return {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "created_at": user.created_at,
                "email_verified": user.email_verified,
                "notification_enabled": user.notification_enabled
            }
    except Exception as e:
        logger.error(f"Error getting user by email: {e}", exc_info=True)
        return None