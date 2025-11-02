# app/whatsapp_handler.py - FIXED VERSION WITH ENHANCED DEBUGGING
from fastapi import APIRouter, Request, BackgroundTasks
import logging
import requests
import os
import json
import re
from .rag_logic import get_ai_response

logger = logging.getLogger(__name__)
router = APIRouter()

# --- Konfigurasi ---
FONNTE_API_KEY = os.getenv("FONNTE_API_KEY", "")
ADMIN_WHATSAPP = os.getenv("ADMIN_WHATSAPP_NUMBER", "")
BUSINESS_WHATSAPP = os.getenv("BUSINESS_WHATSAPP_NUMBER", "")

def send_whatsapp_message(phone: str, message: str) -> bool:
    """Kirim pesan WhatsApp via Fonnte API"""
    if not FONNTE_API_KEY:
        logger.error("FONNTE_API_KEY tidak diatur")
        return False
    
    # Bersihkan nomor telepon
    phone = re.sub(r'[^\d]', '', phone)  # Hapus semua non-digit
    if not phone.startswith('62'):
        if phone.startswith('0'):
            phone = '62' + phone[1:]
        elif phone.startswith('8'):
            phone = '62' + phone
    
    url = "https://api.fonnte.com/send"
    headers = {"Authorization": FONNTE_API_KEY}
    payload = {"target": phone, "message": message}
    
    try:
        response = requests.post(url, headers=headers, data=payload, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        if result.get("status") == True or result.get("status") == "success":
            logger.info(f"✅ Pesan terkirim ke {phone}")
            return True
        else:
            logger.error(f"❌ Fonnte error: {response.text}")
            return False
    except Exception as e:
        logger.error(f"❌ Gagal kirim ke {phone}: {e}")
        return False

def notify_admin_whatsapp(phone: str, user_message: str, reason: str):
    """Notifikasi admin via WhatsApp"""
    if not ADMIN_WHATSAPP:
        return

    admin_msg = f"""🚨 *ESCALATED MESSAGE*

📱 *Dari:* {phone}
💬 *Pesan:* {user_message}
⚠️ *Alasan:* {reason}

Reply via Admin Dashboard.
"""
    send_whatsapp_message(ADMIN_WHATSAPP, admin_msg)

def is_system_message(message: str, sender: str) -> bool:
    """Check apakah pesan adalah system message yang harus di-skip"""
    if not message:
        return True
    
    message_lower = message.lower()
    
    # Skip pesan OTP/System dari Fonnte
    system_keywords = [
        "otp",
        "fonnte.com",
        "delete device",
        "this action will delete",
        "package",
        "token",
        "history",
        "consent:",
        "valid for",
        "verification code",
        "kode verifikasi"
    ]
    
    for keyword in system_keywords:
        if keyword in message_lower:
            logger.info(f"⏭️ Skipping system message with keyword: {keyword}")
            return True
    
    # Skip jika sender adalah nomor Fonnte official atau sistem
    if sender:
        sender_clean = re.sub(r'[^\d]', '', sender)
        system_numbers = ["6285959553452", "6289508496619"]  # Tambahkan nomor sistem lain jika ada
        
        for sys_num in system_numbers:
            if sys_num in sender_clean:
                logger.info(f"⏭️ Skipping message from system number: {sender}")
                return True
    
    return False

async def process_whatsapp_message(phone: str, message: str, pushname: str = "User"):
    """Proses pesan WhatsApp dengan AI"""
    try:
        logger.info(f"📩 Processing WA from {phone} ({pushname}): {message[:100]}")
        
        # Double check bukan system message
        if is_system_message(message, phone):
            logger.info(f"⏭️ Skipping system message in process stage")
            return
        
        # Get AI response
        result = get_ai_response(
            user_id=phone,
            message=message,
            channel="whatsapp",
            user_contact=phone
        )
        
        # Send response
        send_success = send_whatsapp_message(phone, result["response"])
        
        if not send_success:
            logger.error(f"Failed to send response to {phone}")
        
        # Notify admin if escalated
        if result["escalated"]:
            notify_admin_whatsapp(phone, message, result["escalation_reason"])
        
        logger.info(f"✅ Message from {phone} processed successfully")
        
    except Exception as e:
        logger.error(f"❌ Error processing {phone}: {e}", exc_info=True)
        error_msg = "Mohon maaf, terjadi kesalahan sistem. Silakan coba lagi atau hubungi admin kami."
        send_whatsapp_message(phone, error_msg)
        notify_admin_whatsapp(phone, message, f"SYSTEM_ERROR: {str(e)}")

def extract_data_from_webhook(data: dict) -> tuple:
    """
    Extract sender, message, dan pushname dari berbagai format webhook Fonnte
    Returns: (sender, message, pushname)
    """
    # === EXTRACT SENDER ===
    sender = None
    sender_fields = [
        "sender", "from", "phone", "number", "pengirim", 
        "wa", "whatsapp", "chatId", "remoteJid"
    ]
    
    for field in sender_fields:
        value = data.get(field)
        if value:
            # Bersihkan dari @s.whatsapp.net jika ada
            sender = str(value).replace("@s.whatsapp.net", "").replace("+", "")
            logger.info(f"✅ Sender found in field '{field}': {sender}")
            break
    
    # === EXTRACT MESSAGE ===
    message = None
    message_fields = [
        "message", "text", "body", "msg", "pesan", 
        "content", "caption", "messageText"
    ]
    
    for field in message_fields:
        value = data.get(field)
        if value and isinstance(value, str) and value.strip():
            message = value.strip()
            logger.info(f"✅ Message found in field '{field}': {message[:50]}...")
            break
    
    # Check nested message object (beberapa webhook format)
    if not message and "message" in data and isinstance(data["message"], dict):
        nested_msg = data["message"]
        for field in ["conversation", "text", "body", "extendedTextMessage"]:
            if field in nested_msg:
                if isinstance(nested_msg[field], str):
                    message = nested_msg[field].strip()
                elif isinstance(nested_msg[field], dict) and "text" in nested_msg[field]:
                    message = nested_msg[field]["text"].strip()
                if message:
                    logger.info(f"✅ Message found in nested object: {message[:50]}...")
                    break
    
    # === EXTRACT PUSHNAME ===
    pushname = "User"
    pushname_fields = [
        "name", "pushname", "sender_name", "userName", 
        "notifyName", "displayName", "pushName"
    ]
    
    for field in pushname_fields:
        value = data.get(field)
        if value:
            pushname = str(value)
            logger.info(f"✅ Pushname found in field '{field}': {pushname}")
            break
    
    return sender, message, pushname

@router.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    🔍 Webhook Fonnte dengan enhanced debugging dan multi-format support
    """
    try:
        # ===== LOGGING DETAIL =====
        logger.info("=" * 80)
        logger.info("📥 WEBHOOK RECEIVED")
        logger.info(f"🌐 Method: {request.method}")
        logger.info(f"🔗 URL: {request.url}")
        logger.info(f"📋 Headers: {dict(request.headers)}")
        
        # ===== PARSE BODY =====
        try:
            body = await request.body()
            body_str = body.decode('utf-8')
            logger.info(f"📦 Raw Body: {body_str}")
            
            if not body:
                logger.warning("⚠️ Empty body received")
                return {"status": "error", "message": "Empty request body"}
            
            json_data = json.loads(body_str)
            logger.info(f"📋 JSON Keys: {list(json_data.keys())}")
            logger.info(f"📄 Full JSON: {json.dumps(json_data, indent=2)}")
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Invalid JSON: {e}")
            return {"status": "error", "message": "Invalid JSON format"}
        except Exception as e:
            logger.error(f"❌ Error parsing body: {e}")
            return {"status": "error", "message": str(e)}
        
        # ===== FILTER STATUS UPDATES =====
        # Skip status updates (delivered, read, sent)
        if json_data.get("state") in ["read", "delivered", "sent"]:
            logger.info("⏭️ Skipping status update")
            return {"status": "ignored", "reason": "status_update"}
        
        # Skip disconnect/connect notifications
        webhook_status = json_data.get("status")
        if webhook_status in ["disconnect", "connect", "connecting"]:
            logger.info(f"⏭️ Skipping {webhook_status} notification")
            return {"status": "ignored", "reason": f"{webhook_status}_notification"}
        
        # ===== EXTRACT DATA =====
        sender, message, pushname = extract_data_from_webhook(json_data)
        
        logger.info(f"🔍 EXTRACTED DATA:")
        logger.info(f"   👤 Sender: {sender}")
        logger.info(f"   💬 Message: {message[:100] if message else None}")
        logger.info(f"   📛 Name: {pushname}")
        logger.info("=" * 80)
        
        # ===== VALIDASI =====
        # Skip jika tidak ada sender atau message
        if not sender or not message:
            logger.warning("⚠️ No valid sender or message found")
            return {
                "status": "ignored",
                "reason": "no_sender_or_message",
                "available_fields": list(json_data.keys()),
                "debug_info": {
                    "sender_found": sender is not None,
                    "message_found": message is not None,
                    "raw_data": json_data
                }
            }
        
        # Skip jika dari bot sendiri
        sender_clean = re.sub(r'[^\d]', '', sender)
        if sender_clean == BUSINESS_WHATSAPP:
            logger.info("⏭️ Skipping message from self (bot)")
            return {"status": "ignored", "reason": "message_from_self"}
        
        # Skip system messages
        if is_system_message(message, sender):
            logger.info("⏭️ Skipping system message")
            return {"status": "ignored", "reason": "system_message"}
        
        # ===== PROCESS MESSAGE =====
        logger.info(f"🚀 Queueing message for processing: {sender}")
        background_tasks.add_task(process_whatsapp_message, sender, message, pushname)
        
        return {
            "status": "processing",
            "sender": sender,
            "message_preview": message[:50] + "..." if len(message) > 50 else message,
            "pushname": pushname
        }
        
    except Exception as e:
        logger.error(f"❌ WEBHOOK ERROR: {e}", exc_info=True)
        return {
            "status": "error",
            "error": str(e),
            "type": type(e).__name__
        }

@router.get("/whatsapp/status")
async def check_whatsapp_status():
    """Cek status koneksi Fonnte"""
    if not FONNTE_API_KEY:
        return {
            "status": "error",
            "message": "FONNTE_API_KEY not configured",
            "configured": False
        }
    
    try:
        url = "https://api.fonnte.com/device"
        headers = {"Authorization": FONNTE_API_KEY}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        device_info = response.json()
        
        return {
            "status": "connected",
            "configured": True,
            "device_info": device_info,
            "business_number": BUSINESS_WHATSAPP
        }
    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "configured": True,
            "message": f"Failed to connect to Fonnte: {str(e)}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@router.post("/whatsapp/send-test")
async def send_test_message(phone: str, message: str = "Test dari chatbot"):
    """Test kirim pesan ke nomor tertentu"""
    if not phone:
        return {
            "success": False,
            "error": "Phone number required"
        }
    
    success = send_whatsapp_message(phone, message)
    
    return {
        "success": success,
        "phone": phone,
        "message": message,
        "api_key_configured": bool(FONNTE_API_KEY)
    }

@router.get("/whatsapp/debug-info")
async def get_debug_info():
    """Get current configuration for debugging"""
    return {
        "fonnte_api_key_configured": bool(FONNTE_API_KEY) and len(FONNTE_API_KEY) > 10,
        "admin_whatsapp": ADMIN_WHATSAPP if ADMIN_WHATSAPP else "Not configured",
        "business_whatsapp": BUSINESS_WHATSAPP if BUSINESS_WHATSAPP else "Not configured",
        "webhook_endpoint": "/webhook/whatsapp",
        "status_endpoint": "/whatsapp/status",
        "test_endpoint": "/whatsapp/send-test"
    }