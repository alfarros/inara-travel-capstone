# /module_1_chatbot/app/main.py (Versi Pangkas)
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import logging
import os

# --- Import dari file lain di dalam 'app' ---
from .rag_logic import get_ai_response
from .schemas import ChatRequest, ChatResponse
# (Kita hapus router admin, auth, dan whatsapp)
# ----------------------------------------------------

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Chatbot Haji & Umrah (Modul 1)",
    description="AI-powered chatbot dengan RAG",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# (Semua app.include_router dihapus)

@app.get("/")
async def homepage():
    return {"message": "Chatbot Haji & Umrah API Aktif!", "version": "1.0.0"}

# ===== WEB CHAT ENDPOINT =====
@app.post("/chat", response_model=ChatResponse)
async def web_chat(request_data: ChatRequest):
    try:
        if not request_data.message or not request_data.message.strip():
            raise HTTPException(status_code=400, detail="Pesan tidak boleh kosong.")

        logger.info(f"📩 Web chat from {request_data.user_id}: '{request_data.message}'")

        result = get_ai_response(
            user_id=request_data.user_id,
            message=request_data.message,
            channel="web",
            user_contact=request_data.user_email
        )

        return ChatResponse(
            user_id=request_data.user_id,
            response_text=result["response"],
            source=result["source"],
            escalated=result["escalated"],
            escalation_reason=result.get("escalation_reason")
        )

    except HTTPException as http_exc:
         raise http_exc
    except Exception as e:
        logger.error(f"❌ Error tidak terduga di endpoint /chat: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Terjadi error internal server saat memproses permintaan Anda."
        )

# ===== HEALTH CHECK =====
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# ===== ERROR HANDLERS =====
@app.exception_handler(404)
async def not_found_exception_handler(request: Request, exc: HTTPException):
    logger.warning(f"404 Not Found: {request.url}")
    return JSONResponse(
        status_code=404,
        content={"detail": f"Resource not found at path: {request.url.path}"},
    )
    
# (Sisa file main.py biarkan seperti ini)