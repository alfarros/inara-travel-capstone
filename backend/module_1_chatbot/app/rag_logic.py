# module_1_chatbot/app/rag_logic.py (FINAL FIX: ESKALASI & NO GHOST DATA)
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
ESCALATION_EXPIRE_SEC = 900
SQL_CACHE_KEY = "packages_cache"
SQL_CACHE_TTL = 300

# --- KONFIGURASI API AI ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.1-8b-instant" # Pakai model cepat
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODEL = "openai/gpt-3.5-turbo"

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

# --- SQL QUERY (SUMBER KEBENARAN) ---
def get_packages_from_sql() -> str:
    """Mengambil data paket (Cached)"""
    if redis_client:
        try:
            cached = redis_client.get(SQL_CACHE_KEY)
            if cached: return cached
        except: pass
    
    try:
        with get_db() as db:
            query = text("SELECT name, duration, price, airline, features, description FROM packages")
            result = db.execute(query).fetchall()
            
            if not result:
                return "⚠️ SAAT INI DATA PAKET KOSONG DI DATABASE."
            
            package_list = []
            for row in result:
                try:
                    price_fmt = f"Rp {int(row.price):,}".replace(",", ".")
                except:
                    price_fmt = str(row.price)
                
                features_str = ", ".join(row.features) if row.features else "-"

                info = (
                    f"📦 {row.name}\n"
                    f"   - Durasi: {row.duration}\n"
                    f"   - Harga: {price_fmt}\n"
                    f"   - Maskapai: {row.airline}\n"
                    f"   - Hotel/Fasilitas: {features_str}"
                )
                package_list.append(info)
            
            result_text = "\n\n".join(package_list)
            
            if redis_client:
                redis_client.set(SQL_CACHE_KEY, result_text, ex=SQL_CACHE_TTL)
            
            return result_text
            
    except Exception as e:
        logger.error(f"❌ SQL Error: {e}")
        return "Gagal mengambil data paket dari database."

# --- HELPER LOGIC ---
def _is_customization_request(query: str, packages_data: str) -> bool:
    """Cek apakah ini permintaan Custom/Aneh-aneh"""
    query_lower = query.lower()
    packages_lower = packages_data.lower()
    
    # Keywords yang memicu Custom
    triggers = [
        'kustom', 'custom', 'request', 'ubah', 'ganti', 'sesuaikan',
        'sendiri', 'private', 'rombongan', 'keluarga besar', 'diet',
        'sakit', 'kursi roda', 'lansia', 'bayi', 'hamil',
        'turki', 'aqsa', 'eropa', 'dubai', 'mesir' # Destinasi non-standar
    ]
    
    # Cek apakah destinasi tersebut MEMANG TIDAK ADA di data paket SQL
    for word in triggers:
        if word in query_lower:
            # Jika kata tersebut tidak ada di deskripsi paket SQL, berarti ini Custom request
            if word not in packages_lower:
                return True
                
    return False

def _is_commercial_query(query: str) -> bool:
    keywords = ['paket', 'harga', 'biaya', 'tarif', 'promo', 'sedia', 'ada apa', 'list', 'daftar']
    return any(k in query.lower() for k in keywords)

# --- KONTAK & AFFIRMATION (FIXED REGEX) ---
PHONE_REGEX = re.compile(r'((\+62|62|0)8[1-9][0-9]{7,10})\b')
EMAIL_REGEX = re.compile(r'[\w\.-]+@[\w\.-]+\.\w+')
AFFIRMATION_KEYWORDS = {'ya', 'iya', 'ok', 'oke', 'baik', 'boleh', 'lanjut', 'siap', 'mau', 'setuju', 'silakan', 'silahkan', 'gas', 'tolong'}

def _find_dynamic_contact(message: str, default_contact: Optional[str]) -> str:
    phone_match = PHONE_REGEX.search(message)
    if phone_match: return phone_match.group(0)
    email_match = EMAIL_REGEX.search(message)
    if email_match: return email_match.group(0)
    if default_contact: return default_contact
    return "Tidak Diberikan"

def _is_affirmation(msg: str) -> bool:
    # FIX 1: Ganti tanda baca dengan SPASI agar "boleh,silakan" jadi "boleh silakan"
    msg_clean = re.sub(r'[^\w\s]', ' ', msg.lower()).strip()
    
    # Cek exact match
    if msg_clean in AFFIRMATION_KEYWORDS: return True
    
    # Cek per kata
    words = msg_clean.split()
    if any(w in AFFIRMATION_KEYWORDS for w in words): return True
    
    return False

# --- STATE MANAGEMENT ---
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

# --- HISTORY ---
def get_chat_history(user_id: str) -> List[Dict]:
    if not redis_client: return []
    try:
        key = f"{HISTORY_KEY_PREFIX}{user_id}"
        hist = [json.loads(x) for x in redis_client.lrange(key, 0, (HISTORY_MAX_TURNS * 2) - 1)]
        hist.reverse()
        return hist
    except: return []

def save_chat_history(user_id: str, user_message: str, ai_message: str):
    if not redis_client: return
    try:
        key = f"{HISTORY_KEY_PREFIX}{user_id}"
        redis_client.lpush(key, json.dumps({"role": "assistant", "content": ai_message}))
        redis_client.lpush(key, json.dumps({"role": "user", "content": user_message}))
        redis_client.ltrim(key, 0, (HISTORY_MAX_TURNS * 2) - 1)
    except: pass

# --- RAG SEARCH ---
def search_knowledge(query: str) -> list[str]:
    if not collection: return []
    try:
        res = collection.query(query_texts=[query], n_results=2)
        return res['documents'][0] if res['documents'] else []
    except: return []

# --- PROMPT BUILDER (FIXED GHOST DATA) ---
def build_prompt(query: str, context_chunks: list[str], sql_data: str) -> Tuple[str, str]:
    
    # Deteksi Intent
    is_commercial = _is_commercial_query(query)
    is_custom = _is_customization_request(query, sql_data)

    # --- LOGIC 1: CUSTOM REQUEST ---
    if is_custom:
        # Prompt khusus untuk menghandle penolakan halus dan tawaran eskalasi
        system_prompt = """Anda adalah 'Asisten Inara'.
Tugas: Mengidentifikasi kebutuhan khusus user yang TIDAK ADA di daftar paket standar.

INSTRUKSI PENTING:
1. Jangan mencoba menjual paket yang tidak sesuai.
2. Akui kebutuhan user (misal: "Saya mengerti Anda butuh paket Turkey...").
3. Jelaskan bahwa paket tersebut belum tersedia di sistem, TAPI tim Admin bisa mengaturnya.
4. AKHIRI dengan tawaran menghubungkan ke Admin.

Contoh Respon:
"Saat ini paket tersebut belum tersedia di katalog sistem kami. Namun, untuk kebutuhan khusus seperti ini, tim Admin kami bisa membantunya secara manual. Apakah boleh saya hubungkan Anda ke Admin?"
"""
        rag_context = "" # Kosongkan RAG biar tidak halusinasi

    # --- LOGIC 2: TANYA PAKET (COMMERCIAL) ---
    elif is_commercial:
        # FIX 2: JANGAN GUNAKAN RAG CONTEXT DISINI! 
        # Kita hanya mau pakai SQL Data agar 'Paket Haji Plus' (dummy) tidak muncul.
        rag_context = "" 
        
        system_prompt = f"""Anda adalah 'Asisten Inara'.
Berikut adalah KATALOG RESMI yang tersedia saat ini (Live Database):

{sql_data}

ATURAN MENJAWAB:
1. HANYA sebutkan paket yang tertulis di atas.
2. JANGAN sebutkan paket lain (seperti Haji Plus, Turki, Eropa) jika tidak ada di daftar di atas.
3. Jika user tanya paket yang tidak ada, katakan tidak ada.
4. Tampilkan dengan format rapi (Nama, Harga, Durasi).
"""

    # --- LOGIC 3: TANYA UMUM (RAG AKTIF) ---
    else:
        # RAG dipakai hanya untuk pertanyaan umum (doa, sejarah, tips)
        rag_text = "\n".join(context_chunks) if context_chunks else "Tidak ada info."
        rag_context = f"Referensi Pengetahuan:\n{rag_text}"
        
        system_prompt = """Anda adalah 'Asisten Inara'. 
Jawab pertanyaan seputar ibadah Haji & Umrah dengan ramah dan singkat berdasarkan referensi yang diberikan."""

    # Final User Prompt
    user_prompt = f"""{rag_context}

Pertanyaan User: "{query}"
"""
    return system_prompt, user_prompt

# --- AI CALL ---
def call_ai_with_fallback(sys_prompt: str, usr_prompt: str, history: List[Dict]) -> str:
    msgs = [{"role": "system", "content": sys_prompt}] + history + [{"role": "user", "content": usr_prompt}]
    
    # Groq (Fast)
    if GROQ_API_KEY:
        try:
            res = requests.post(GROQ_URL, headers={"Authorization": f"Bearer {GROQ_API_KEY}"}, 
                                json={"model": GROQ_MODEL, "messages": msgs, "temperature": 0.1}, timeout=8)
            if res.status_code == 200: return res.json()["choices"][0]["message"]["content"]
        except: pass

    # OpenRouter (Backup)
    if OPENROUTER_API_KEY:
        try:
            res = requests.post(OPENROUTER_URL, headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"},
                                json={"model": OPENROUTER_MODEL, "messages": msgs}, timeout=15)
            if res.status_code == 200: return res.json()["choices"][0]["message"]["content"]
        except: pass
        
    return "Maaf, sedang ada gangguan koneksi AI."

# --- MAIN LOGIC ---
def get_ai_response(user_id: str, message: str, channel: str = "web", user_contact: Optional[str] = None) -> Dict:
    try:
        # 1. CEK STATE ESKALASI
        state = get_escalation_state(user_id)
        
        # A. MENUNGGU KONTAK
        if state == "AWAITING_CONTACT":
            contact = _find_dynamic_contact(message, user_contact)
            if contact != "Tidak Diberikan":
                data = get_escalation_data(user_id) or {}
                notify_admin_whatsapp(user_id, contact, data.get("original_message", message), "Kontak Diterima")
                clear_escalation_state(user_id)
                res = "Terima kasih! Data kontak sudah diterima. Tim kami akan segera menghubungi via WhatsApp. 🙏"
                save_chat_history(user_id, message, res)
                return {"response": res, "source": "System", "escalated": True, "escalation_reason": "Selesai"}
            else:
                return {"response": "Mohon informasikan Nomor WhatsApp atau Email Anda (Contoh: 0812xxxx).", "source": "System", "escalated": True}

        # B. MENUNGGU KONFIRMASI (DISINI TADI ERORNYA)
        if state == "AWAITING_CONFIRM":
            if _is_affirmation(message):
                # User setuju ("Boleh, silakan")
                set_escalation_state(user_id, "AWAITING_CONTACT", get_escalation_data(user_id))
                
                # Langsung return response minta WA
                quick_res = "Baik. Boleh dibantu informasikan Nomor WhatsApp atau Email Anda yang aktif?"
                save_chat_history(user_id, message, quick_res)
                return {"response": quick_res, "source": "System", "escalated": True}
            else:
                # User nolak/ngomong lain, hapus state dan lanjut ke normal flow
                clear_escalation_state(user_id)

        # 2. NORMAL FLOW
        sql_data = get_packages_from_sql()
        context_chunks = search_knowledge(message)
        history = get_chat_history(user_id)
        
        # Build Prompt (Dengan filter ghost data)
        sys_prompt, usr_prompt = build_prompt(message, context_chunks, sql_data)
        
        # Call AI
        response_text = call_ai_with_fallback(sys_prompt, usr_prompt, history)
        
        # Cek Trigger Eskalasi Baru
        escalated = False
        reason = None
        
        # Deteksi Custom Request (via Helper)
        if _is_customization_request(message, sql_data):
            escalated = True
            reason = "Permintaan Custom"
        
        # Deteksi Keyword User Minta Admin
        if "admin" in message.lower() and "hubun" in message.lower():
            escalated = True
            reason = "Request User"

        # Deteksi Jawaban AI (AI menawarkan bantuan)
        if "hubungkan" in response_text.lower() and "admin" in response_text.lower() and "bagaimana" in response_text.lower():
            escalated = True
            reason = "AI Offer"

        if escalated:
            # Pastikan kalimat tanya ada
            if "boleh saya" not in response_text.lower() and "bagaimana" not in response_text.lower():
                response_text += "\n\nApakah boleh saya hubungkan Anda ke Admin untuk detailnya?"
            
            set_escalation_state(user_id, "AWAITING_CONFIRM", {"original_message": message, "reason": reason})

        save_chat_history(user_id, message, response_text)
        
        return {
            "response": response_text,
            "source": "Hybrid",
            "escalated": escalated,
            "escalation_reason": reason
        }

    except Exception as e:
        logger.error(f"Error: {e}")
        return {"response": "Maaf, sistem sedang sibuk.", "source": "Error", "escalated": False}