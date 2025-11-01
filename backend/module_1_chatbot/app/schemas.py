# /module_1_chatbot/app/schemas.py
from pydantic import BaseModel
from typing import Optional

# Schema untuk endpoint /chat di main.py
class ChatRequest(BaseModel):
    user_id: str
    message: str
    user_email: Optional[str] = None # Jadikan opsional

class ChatResponse(BaseModel):
    user_id: str
    response_text: str
    source: str
    escalated: bool
    escalation_reason: Optional[str] = None

# --- TAMBAHKAN SCHEMA INI ---
class UserCreate(BaseModel):
    email: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None

class User(BaseModel):
    user_id: int
    email: str
    first_name: Optional[str] = None

    class Config:
        from_attributes = True # <<< INI PERBAIKANNYA

class Token(BaseModel):
    access_token: str
    token_type: str
# (Anda bisa tambahkan schema lain di sini jika diperlukan oleh handler lain,
# misalnya untuk admin_handler atau whatsapp_handler jika butuh validasi Pydantic)