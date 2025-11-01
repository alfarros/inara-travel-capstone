# /module_1_chatbot/app/main.py
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
from .auth_handler import router as auth_router

# --- Import dari file lain di dalam 'app' ---
from .rag_logic import get_ai_response
from .whatsapp_handler import router as whatsapp_router
from .admin_handler import router as admin_router
# --- PERBAIKAN IMPORT: Ambil schema dari schemas.py ---
from .schemas import ChatRequest, ChatResponse
from .auth_handler import router as auth_router
# ----------------------------------------------------

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Chatbot Haji & Umrah (Modul 1)",
    description="AI-powered chatbot dengan multi-channel support (Web + WhatsApp) & RAG",
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

# Include routers
# Prefix ditambahkan agar endpoint lebih terstruktur (opsional)
app.include_router(whatsapp_router, tags=["WhatsApp"])
app.include_router(admin_router, prefix="/admin", tags=["Admin"])


@app.get("/")
async def homepage(): # Hapus parameter 'request' jika tidak dipakai
    """ Endpoint root sederhana sebagai penanda API aktif. """
    return {"message": "Chatbot Haji & Umrah API Aktif!", "version": "1.0.0"}

# ===== WEB CHAT ENDPOINT =====
@app.post("/chat", response_model=ChatResponse)
async def web_chat(request_data: ChatRequest): # Gunakan request_data (schema impor)
    """ Endpoint utama untuk menerima chat dari Web Interface. """
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

        # Kembalikan response sesuai schema ChatResponse yang diimpor
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
    """ Endpoint standar untuk monitoring. """
    return {"status": "healthy"}

# ===== ERROR HANDLERS =====
@app.exception_handler(404)
async def not_found_exception_handler(request: Request, exc: HTTPException):
    logger.warning(f"404 Not Found: {request.url}")
    return JSONResponse(
        status_code=404,
        content={"detail": f"Resource not found at path: {request.url.path}"},
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception for request {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error - An unexpected error occurred."},
    )

# ===== STARTUP & SHUTDOWN EVENTS =====
@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Memulai FastAPI application...")
    # Trigger loading model (sudah terjadi saat import rag_logic)
    logger.info("✅ Aplikasi siap menerima request.")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🛑 Menghentikan FastAPI application...")
    logger.info("✅ Aplikasi berhenti.")