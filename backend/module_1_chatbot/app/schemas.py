# /module_1_chatbot/app/schemas.py (Versi Pangkas)
from pydantic import BaseModel
from typing import Optional

# Schema untuk endpoint /chat di main.py
class ChatRequest(BaseModel):
    user_id: str
    message: str
    user_email: Optional[str] = None # Untuk kontak eskalasi

class ChatResponse(BaseModel):
    user_id: str
    response_text: str
    source: str
    escalated: bool
    escalation_reason: Optional[str] = None

# (Semua schema UserCreate, User, dan Token dihapus)