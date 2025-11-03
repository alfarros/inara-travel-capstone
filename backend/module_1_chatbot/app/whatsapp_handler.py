# app/whatsapp_handler.py (Versi Pangkas - Hanya Mengirim)
import logging
import requests
import os
import re
from typing import Optional

logger = logging.getLogger(__name__)

# --- Konfigurasi ---
FONNTE_API_KEY = os.getenv("FONNTE_API_KEY", "")
ADMIN_WHATSAPP = os.getenv("ADMIN_WHATSAPP_NUMBER", "") # Nomor WA Admin

def send_whatsapp_message(phone: str, message: str) -> bool:
    """Kirim pesan WhatsApp via Fonnte API"""
    if not FONNTE_API_KEY:
        logger.error("FONNTE_API_KEY tidak diatur. Notifikasi admin gagal.")
        return False
    
    # Bersihkan nomor telepon
    phone = re.sub(r'[^\d]', '', phone)
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
            logger.info(f"✅ Pesan (notifikasi) terkirim ke {phone}")
            return True
        else:
            logger.error(f"❌ Fonnte error: {response.text}")
            return False
    except Exception as e:
        logger.error(f"❌ Gagal kirim ke {phone}: {e}")
        return False

def notify_admin_whatsapp(
    user_id: str, 
    user_contact: Optional[str], 
    user_message: str, 
    reason: str
):
    """Notifikasi admin via WhatsApp (Logika Baru)"""
    if not ADMIN_WHATSAPP:
        logger.warning("ADMIN_WHATSAPP_NUMBER tidak diatur. Tidak bisa eskalasi.")
        return

    # Siapkan info kontak user agar admin bisa membalas
    kontak = user_contact if user_contact else user_id

    admin_msg = f"""🚨 *ESKALASI CHATBOT* 🚨

*Dari User:* {user_id}
*Kontak (Email/WA):* {kontak}
*Alasan Eskalasi:* {reason}
---
*Pesan User:*
{user_message}
---
Harap segera tindak lanjuti."""
    
    send_whatsapp_message(ADMIN_WHATSAPP, admin_msg)

# (Semua kode router dan webhook dihapus)