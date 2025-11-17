# module_1_chatbot/app/rag_logic.py (FIXED - ESCALATION FLOW)
import os
import requests
import chromadb
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import logging
from typing import Tuple, Optional, Dict, List
import json
import redis 
import re 
from sqlalchemy import text 

# --- IMPORTS DATABASE & WA ---
from .whatsapp_handler import notify_admin_whatsapp
from .database import get_db 

logger = logging.getLogger(__name__)
load_dotenv()

# --- KONEKSI REDIS (CACHE & STATE) ---
redis_client = None
try:
    redis_client = redis.Redis(
        host=os.getenv("REDIS_HOST", "redis-cache"), 
        port=6379, 
        db=0, 
        decode_responses=True
    )
    redis_client.ping()
    logger.info("✅ Koneksi ke Redis berhasil.")
except Exception as e:
    logger.error(f"❌ Gagal koneksi ke Redis: {e}. Fitur history & state non-aktif.")
    redis_client = None

# --- KONSTANTA ---
HISTORY_KEY_PREFIX = "chat_history:"
HISTORY_MAX_TURNS = 4 
ESCALATION_KEY_PREFIX = "escalation_pending:"
ESCALATION_STATE_PREFIX = "escalation_state:" 
ESCALATION_EXPIRE_SEC = 900 # 15 Menit

# --- KONFIGURASI API AI ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODEL = "openai/gpt-oss-20b:free"
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434/api/generate")
OLLAMA_MODEL = "gemma2:2b"

# --- INISIALISASI MODEL RAG ---
model = None
collection = None 
try:
    model = SentenceTransformer('all-MiniLM-L6-v2')
    client = chromadb.PersistentClient(path="./chroma_db")
    collection = client.get_or_create_collection(name="haji_umrah_kb")
    logger.info("✅ ChromaDB & Model Loaded.")
except Exception as e:
    logger.error(f"FATAL: Error inisialisasi RAG: {e}")

# --- HELPER: DATABASE SQL ---
def get_packages_from_sql() -> str:
    """Mengambil data paket REAL-TIME dari PostgreSQL"""
    try:
        with get_db() as db:
            query = text("SELECT name, duration, price, airline, description FROM packages")
            result = db.execute(query).fetchall()
            
            if not result:
                return "TIDAK ADA DATA PAKET DI DATABASE SAAT INI."
            
            package_list = []
            for row in result:
                try:
                    price_fmt = f"Rp {int(row.price):,}".replace(",", ".")
                except:
                    price_fmt = str(row.price)

                info = (
                    f"- {row.name} ({row.duration}): {price_fmt}\n"
                    f"  Maskapai: {row.airline}. Info: {row.description}"
                )
                package_list.append(info)
            
            return "\n".join(package_list)
    except Exception as e:
        logger.error(f"❌ SQL Error: {e}")
        return "Gagal mengambil data database."

# --- HELPER: KONTAK & STATE ---
PHONE_REGEX = re.compile(r'((\+62|62|0)8[1-9][0-9]{7,10})\b')
EMAIL_REGEX = re.compile(r'[\w\.-]+@[\w\.-]+\.\w+')

def _find_dynamic_contact(message: str, default_contact: Optional[str]) -> str:
    phone_match = PHONE_REGEX.search(message)
    if phone_match: return phone_match.group(0)
    email_match = EMAIL_REGEX.search(message)
    if email_match: return email_match.group(0)
    if default_contact: return default_contact
    return "Tidak Diberikan"

def get_escalation_state(user_id: str) -> Optional[str]:
    if not redis_client: return None
    return redis_client.get(f"{ESCALATION_STATE_PREFIX}{user_id}")

def set_escalation_state(user_id: str, state: str, data: Dict = None):
    if not redis_client: return
    redis_client.set(f"{ESCALATION_STATE_PREFIX}{user_id}", state, ex=ESCALATION_EXPIRE_SEC)
    if data:
        redis_client.set(f"{ESCALATION_KEY_PREFIX}{user_id}", json.dumps(data), ex=ESCALATION_EXPIRE_SEC)

def clear_escalation_state(user_id: str):
    if not redis_client: return
    redis_client.delete(f"{ESCALATION_STATE_PREFIX}{user_id}", f"{ESCALATION_KEY_PREFIX}{user_id}")

def get_escalation_data(user_id: str) -> Optional[Dict]:
    if not redis_client: return None
    data = redis_client.get(f"{ESCALATION_KEY_PREFIX}{user_id}")
    return json.loads(data) if data else None

# --- HELPER: CHAT HISTORY ---
def get_chat_history(user_id: str) -> List[Dict]:
    if not redis_client: return []
    try:
        key = f"{HISTORY_KEY_PREFIX}{user_id}"
        hist = [json.loads(x) for x in redis_client.lrange(key, 0, (HISTORY_MAX_TURNS * 2) - 1)]
        hist.reverse()
        return hist
    except Exception: return []

def save_chat_history(user_id: str, user_message: str, ai_message: str):
    if not redis_client: return
    try:
        key = f"{HISTORY_KEY_PREFIX}{user_id}"
        redis_client.lpush(key, json.dumps({"role": "assistant", "content": ai_message}))
        redis_client.lpush(key, json.dumps({"role": "user", "content": user_message}))
        redis_client.ltrim(key, 0, (HISTORY_MAX_TURNS * 2) - 1)
    except Exception: pass

# --- AI LOGIC ---
def search_knowledge(query: str) -> list[str]:
    if not collection: return []
    try:
        res = collection.query(query_texts=[query], n_results=3)
        return res['documents'][0] if res['documents'] else []
    except: return []

def build_prompt(query: str, context_chunks: list[str]) -> Tuple[str, str]:
    sql_data = get_packages_from_sql()
    rag_context = "\n".join(context_chunks) if context_chunks else "Tidak ada info dokumen."

    system_prompt = f"""Anda adalah 'Asisten Inara', CS Travel Haji & Umrah.
    
DATA PAKET RESMI (GUNAKAN INI SEBAGAI ACUAN UTAMA):
===================================================
{sql_data}
===================================================

INSTRUKSI:
1. Jika user tanya harga/paket, WAJIB pakai data di atas. JANGAN halusinasi/mengarang paket lain.
2. Jika paket tidak ada di data (misal: Turki, Aqsa), tawarkan ESKALASI ke admin.
3. Jawab singkat, padat, ramah.
"""
    user_prompt = f"""Info Dokumen: {rag_context}\n\nPertanyaan: "{query}" """
    return system_prompt, user_prompt

def call_ai_with_fallback(sys_prompt: str, usr_prompt: str, history: List[Dict]) -> str:
    # 1. Try Groq
    if GROQ_API_KEY:
        try:
            msgs = [{"role": "system", "content": sys_prompt}] + history + [{"role": "user", "content": usr_prompt}]
            res = requests.post(GROQ_URL, headers={"Authorization": f"Bearer {GROQ_API_KEY}"}, 
                                json={"model": GROQ_MODEL, "messages": msgs, "temperature": 0.1}, timeout=10)
            if res.status_code == 200: return res.json()["choices"][0]["message"]["content"]
        except: pass
    
    # 2. Try OpenRouter
    if OPENROUTER_API_KEY:
        try:
            msgs = [{"role": "system", "content": sys_prompt}] + history + [{"role": "user", "content": usr_prompt}]
            res = requests.post(OPENROUTER_URL, headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"},
                                json={"model": OPENROUTER_MODEL, "messages": msgs}, timeout=20)
            if res.status_code == 200: return res.json()["choices"][0]["message"]["content"]
        except: pass
        
    return "Maaf, sistem sedang sibuk."

# --- LOGIC ESKALASI (IMPROVED) ---
def _is_affirmation(msg: str) -> bool:
    """Deteksi kata setuju/afirmasi dengan lebih akurat"""
    msg_clean = re.sub(r'[^\w\s]', '', msg.lower()).strip()
    
    # Daftar kata affirm (termasuk typo umum)
    affirm_keywords = [
        'ya', 'iya', 'ok', 'oke', 'okey', 'okay', 'baik', 'boleh', 
        'lanjut', 'siap', 'tolong', 'silakan', 'silahkan', 'mau', 
        'setuju', 'saya mau', 'iya boleh', 'ya boleh', 'bolej'  # typo umum
    ]
    
    return any(kw in msg_clean for kw in affirm_keywords)

def _is_negation(msg: str) -> bool:
    """Deteksi kata tolak/negasi"""
    msg_clean = msg.lower()
    negate_keywords = ['tidak', 'nggak', 'engga', 'gak', 'batal', 'nanti', 'jangan', 'ndak']
    return any(kw in msg_clean for kw in negate_keywords)

def should_escalate(msg: str, ai_res: str) -> Tuple[bool, str]:
    """Cek apakah perlu eskalasi"""
    msg = msg.lower()
    ai_res = ai_res.lower()
    
    # Trigger kata kunci dari user
    if any(x in msg for x in ["admin", "custom", "kustom", "keluarga", "mobil", "private"]): 
        return True, "Keyword User"
    
    # Trigger dari AI response
    if "bagaimana?" in ai_res and ("hubungkan" in ai_res or "admin" in ai_res): 
        return True, "AI Offer"
    
    return False, ""

# ==========================================
# MAIN HANDLER (FUNGSI UTAMA - FIXED)
# ==========================================
def get_ai_response(user_id: str, message: str, channel: str = "web", user_contact: Optional[str] = None) -> Dict:
    try:
        # 1. CEK STATE SAAT INI
        state = get_escalation_state(user_id)
        
        # Log untuk debugging
        logger.info(f"🔍 User: {user_id} | State: {state} | Message: {message}")
        
        # ---------------------------------------------------------
        # CASE A: STATE = MENUNGGU KONTAK (AWAITING_CONTACT)
        # ---------------------------------------------------------
        if state == "AWAITING_CONTACT":
            contact = _find_dynamic_contact(message, user_contact)
            
            if contact != "Tidak Diberikan":
                # Kirim ke Admin
                data = get_escalation_data(user_id) or {}
                notify_admin_whatsapp(user_id, contact, data.get("original_message", message), data.get("reason", "Input Kontak"))
                
                # Selesai
                clear_escalation_state(user_id)
                res = "Terima kasih! Kontak Anda sudah diterima. Tim Admin kami akan segera menghubungi Anda via WhatsApp. 🙏"
                save_chat_history(user_id, message, res)
                return {"response": res, "source": "System", "escalated": True, "escalation_reason": "Selesai"}
            else:
                # User tidak kasih format kontak yg benar
                res = "Mohon maaf, saya membutuhkan Nomor WhatsApp atau Email Anda untuk diteruskan ke admin.\n\nContoh:\n- 081234567890\n- email@example.com"
                return {"response": res, "source": "System", "escalated": True}

        # ---------------------------------------------------------
        # CASE B: STATE = MENUNGGU KONFIRMASI (AWAITING_CONFIRM)
        # ---------------------------------------------------------
        if state == "AWAITING_CONFIRM":
            logger.info(f"📝 Masuk state AWAITING_CONFIRM untuk user {user_id}")
            
            # Cek apakah user setuju
            if _is_affirmation(message):
                logger.info(f"✅ User SETUJU eskalasi")
                
                # Update state ke AWAITING_CONTACT
                data = get_escalation_data(user_id) or {"original_message": message, "reason": "Custom Paket"}
                set_escalation_state(user_id, "AWAITING_CONTACT", data)
                
                # RESPON LANGSUNG MINTA KONTAK
                res = "Baik, saya akan sambungkan Anda ke tim Admin kami. 😊\n\nBoleh dibantu informasikan Nomor WhatsApp atau Email Anda yang aktif?"
                save_chat_history(user_id, message, res)
                
                return {
                    "response": res, 
                    "source": "System", 
                    "escalated": True,
                    "escalation_reason": "User menyetujui eskalasi"
                }
            
            elif _is_negation(message):
                logger.info(f"❌ User MENOLAK eskalasi")
                # User menolak -> Hapus state, lanjut chat biasa
                clear_escalation_state(user_id)
                res = "Baik, tidak masalah. Apakah ada yang bisa saya bantu terkait paket yang sudah tersedia?"
                save_chat_history(user_id, message, res)
                return {"response": res, "source": "System", "escalated": False}
            
            else:
                # User nanya hal lain, anggap sebagai penolakan halus
                logger.info(f"⚠️ User response ambigu, anggap penolakan")
                clear_escalation_state(user_id)
                # Lanjut ke flow normal di bawah

        # ---------------------------------------------------------
        # CASE C: NORMAL CHAT FLOW (RAG + SQL)
        # ---------------------------------------------------------
        history = get_chat_history(user_id)
        context_chunks = search_knowledge(message)
        
        # Build Prompt (Disini SQL Data dimasukkan)
        sys_prompt, usr_prompt = build_prompt(message, context_chunks)
        
        # Call AI
        response_text = call_ai_with_fallback(sys_prompt, usr_prompt, history)
        
        # Cek Trigger Eskalasi Baru
        escalated, reason = should_escalate(message, response_text)
        
        if escalated:
            # Jika AI belum menawarkan secara eksplisit, tambahkan kalimat penawaran
            if "bagaimana?" not in response_text.lower() and "hubungkan" not in response_text.lower():
                response_text += "\n\nUntuk kebutuhan ini, saya bisa sambungkan Anda ke tim Admin kami. Bagaimana?"
            
            # Simpan state menunggu konfirmasi user
            set_escalation_state(user_id, "AWAITING_CONFIRM", {"original_message": message, "reason": reason})
            logger.info(f"🔔 Set state AWAITING_CONFIRM untuk user {user_id}")

        save_chat_history(user_id, message, response_text)
        
        return {
            "response": response_text,
            "source": "Hybrid (SQL+AI)",
            "escalated": escalated,
            "escalation_reason": reason
        }

    except Exception as e:
        logger.error(f"❌ System Error: {e}", exc_info=True)
        return {"response": "Maaf, terjadi kesalahan sistem.", "source": "Error", "escalated": False}