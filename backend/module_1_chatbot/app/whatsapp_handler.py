# app/whatsapp_handler.py - VERSI FONNTE
from fastapi import APIRouter, Request, BackgroundTasks, Form
from typing import Dict, Any
import logging
import requests
import os
from .rag_logic import get_ai_response # Menggunakan RAG logic yang sama

logger = logging.getLogger(__name__)
router = APIRouter()

# --- Mengambil Konfigurasi Fonnte dari .env ---
FONNTE_API_KEY = os.getenv("FONNTE_API_KEY", "")
ADMIN_WHATSAPP = os.getenv("ADMIN_WHATSAPP_NUMBER", "") #
BUSINESS_WHATSAPP = os.getenv("BUSINESS_WHATSAPP_NUMBER", "") #

def send_whatsapp_message(phone: str, message: str) -> bool:
    """Kirim pesan WhatsApp via Fonnte API"""
    if not FONNTE_API_KEY:
        logger.error("FONNTE_API_KEY tidak diatur. Pesan tidak terkirim.")
        return False
        
    # Pastikan format nomor benar (misal: 62812...)
    phone = phone.replace("+", "").replace("@s.whatsapp.net", "")
    
    url = "https://api.fonnte.com/send"
    headers = {
        "Authorization": FONNTE_API_KEY
    }
    # Fonnte menggunakan 'data' (form) bukan 'json'
    payload = {
        "target": phone,
        "message": message
    }
    
    try:
        response = requests.post(url, headers=headers, data=payload, timeout=10)
        response.raise_for_status()
        
        # Fonnte mengembalikan JSON, kita bisa cek statusnya
        if response.json().get("status") == True:
            logger.info(f"✅ Pesan Fonnte terkirim ke {phone}")
            return True
        else:
            logger.error(f"❌ Fonnte API error: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Gagal kirim pesan ke {phone} (Fonnte): {e}")
        return False

def notify_admin_whatsapp(phone: str, user_message: str, reason: str):
    """Notifikasi admin via WhatsApp ketika ada escalation"""
    if not ADMIN_WHATSAPP:
        logger.warning("ADMIN_WHATSAPP_NUMBER tidak diatur. Notifikasi gagal.")
        return

    admin_msg = f"""🚨 *PERHATIAN - Escalated Message*

📱 *Dari:* {phone}
💬 *Pesan:* {user_message}
⚠️ *Alasan Escalation:* {reason}

Silakan reply via Admin Dashboard.
"""
    
    send_whatsapp_message(ADMIN_WHATSAPP, admin_msg)
    logger.info(f"📢 Admin notified via WhatsApp untuk customer {phone}")

async def process_whatsapp_message(phone: str, message: str, pushname: str = "User"):
    """Proses pesan dari WhatsApp dengan AI (LOGIKA INI TETAP SAMA)"""
    try:
        logger.info(f"📩 Processing WA message from {phone}: {message}")
        
        # Memanggil RAG logic Anda yang sudah ada
        result = get_ai_response(
            user_id=phone,
            message=message,
            channel="whatsapp",
            user_contact=phone
        )
        
        # Kirim response ke user
        send_whatsapp_message(phone, result["response"])
        
        # Jika di-escalate, notif admin via WA juga
        if result["escalated"]:
            notify_admin_whatsapp(phone, message, result["escalation_reason"])
        
        logger.info(f"✅ Message from {phone} processed successfully")
        
    except Exception as e:
        logger.error(f"❌ Error processing message dari {phone}: {e}", exc_info=True)
        error_msg = "Mohon maaf, terjadi kesalahan sistem. Tim kami akan segera menghubungi Anda."
        send_whatsapp_message(phone, error_msg)
        
        # Notif admin tentang error
        notify_admin_whatsapp(phone, message, f"SYSTEM_ERROR: {str(e)}")


# --- PERUBAHAN BESAR ADA DI SINI ---
@router.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Webhook untuk menerima pesan dari WhatsApp (FONNTE)
    Fonnte mengirim data sebagai 'form-data', BUKAN JSON.
    """
    try:
        data = await request.form()
        
        sender = data.get("sender") # Nomor pengirim (misal: 62812...)
        message = data.get("message") # Isi pesan
        pushname = data.get("name", "User") # Nama pengirim
        
        logger.info(f"📩 Fonnte Webhook received from {sender}: {message}")

        # Skip jika pesan dari bot sendiri (nomor WA bisnis Anda)
        if sender == BUSINESS_WHATSAPP: 
            logger.info("Skipping message from self")
            return {"status": "ignored", "reason": "message_from_self"}
        
        if message and sender:
            # Proses di background
            background_tasks.add_task(process_whatsapp_message, sender, message, pushname)
            return {"status": "processing"}
        else:
            logger.warning("No message or sender in Fonnte webhook")
            return {"status": "ignored", "reason": "no_message_or_sender"}

    except Exception as e:
        logger.error(f"❌ Fonnte Webhook error: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}

# Endpoint ini tidak lagi relevan karena Fonnte mengurus status koneksi
@router.get("/whatsapp/status")
async def check_whatsapp_status():
    return {"status": "check_fonnte_dashboard", "message": "Koneksi diurus oleh Fonnte"}

# Endpoint tes ini masih bisa kita gunakan
@router.post("/whatsapp/send-test")
async def send_test_message(phone: str, message: str = "Test message dari chatbot"):
    """Testing endpoint untuk kirim pesan WA via Fonnte"""
    success = send_whatsapp_message(phone, message)
    return {
        "success": success,
        "phone": phone,
        "message": message
    }