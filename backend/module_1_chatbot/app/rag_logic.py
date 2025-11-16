# module_1_chatbot/app/rag_logic.py (FINAL FIX - State Management Diperbaiki)
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

from .whatsapp_handler import notify_admin_whatsapp

logger = logging.getLogger(__name__)
load_dotenv()

# --- Koneksi Redis ---
redis_client = None
try:
    redis_client = redis.Redis(
        host=os.getenv("REDIS_HOST", "redis-cache"), 
        port=6379, 
        db=0, 
        decode_responses=True
    )
    redis_client.ping()
    logger.info("✅ Koneksi ke Redis untuk chat history berhasil.")
except Exception as e:
    logger.error(f"❌ Gagal koneksi ke Redis: {e}. Chat history akan non-aktif.")
    redis_client = None

HISTORY_KEY_PREFIX = "chat_history:"
HISTORY_MAX_TURNS = 4 
ESCALATION_KEY_PREFIX = "escalation_pending:"
ESCALATION_STATE_PREFIX = "escalation_state:" # NEW: State machine
ESCALATION_EXPIRE_SEC = 900 # 15 menit

# --- KONFIGURASI AI ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODEL = "openai/gpt-oss-20b:free"
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434/api/generate")
OLLAMA_MODEL = "gemma2:2b"

# --- Inisialisasi Model & DB ---
model = None
collection = None 
try:
    model = SentenceTransformer('all-MiniLM-L6-v2')
    client = chromadb.PersistentClient(path="./chroma_db")
    collection_name = "haji_umrah_kb"
    collection = client.get_or_create_collection(name=collection_name)
    logger.info(f"✅ Collection '{collection_name}' dan model ST berhasil di-load.")
except Exception as e:
    logger.error(f"FATAL: Error saat inisialisasi model atau ChromaDB: {e}", exc_info=True)

# --- Fungsi Ekstraksi Kontak ---
PHONE_REGEX = re.compile(r'((\+62|62|0)8[1-9][0-9]{7,10})\b')
EMAIL_REGEX = re.compile(r'[\w\.-]+@[\w\.-]+\.\w+')

def _find_dynamic_contact(message: str, default_contact: Optional[str]) -> str:
    """Ekstrak kontak dari pesan atau gunakan default"""
    phone_match = PHONE_REGEX.search(message)
    if phone_match:
        number = phone_match.group(0)
        logger.info(f"📞 Kontak dinamis terdeteksi (Telepon): {number}")
        return number
    email_match = EMAIL_REGEX.search(message)
    if email_match:
        email = email_match.group(0)
        logger.info(f"📧 Kontak dinamis terdeteksi (Email): {email}")
        return email
    if default_contact:
        logger.info(f"📋 Menggunakan kontak default: {default_contact}")
        return default_contact
    logger.warning("⚠️ Kontak tidak ditemukan")
    return "Tidak Diberikan"

# --- State Management ---
def get_escalation_state(user_id: str) -> Optional[str]:
    """Get current escalation state: None, 'AWAITING_CONFIRM', 'AWAITING_CONTACT'"""
    if not redis_client: return None
    try:
        key = f"{ESCALATION_STATE_PREFIX}{user_id}"
        state = redis_client.get(key)
        logger.debug(f"🔍 State untuk {user_id}: {state}")
        return state
    except Exception as e:
        logger.error(f"Error get state: {e}")
        return None

def set_escalation_state(user_id: str, state: str, data: Dict = None):
    """Set escalation state with optional data"""
    if not redis_client: return
    try:
        state_key = f"{ESCALATION_STATE_PREFIX}{user_id}"
        redis_client.set(state_key, state, ex=ESCALATION_EXPIRE_SEC)
        
        if data:
            data_key = f"{ESCALATION_KEY_PREFIX}{user_id}"
            redis_client.set(data_key, json.dumps(data), ex=ESCALATION_EXPIRE_SEC)
        
        logger.info(f"💾 State {user_id} → {state}")
    except Exception as e:
        logger.error(f"Error set state: {e}")

def clear_escalation_state(user_id: str):
    """Clear all escalation state"""
    if not redis_client: return
    try:
        state_key = f"{ESCALATION_STATE_PREFIX}{user_id}"
        data_key = f"{ESCALATION_KEY_PREFIX}{user_id}"
        redis_client.delete(state_key, data_key)
        logger.info(f"🗑️ State cleared untuk {user_id}")
    except Exception as e:
        logger.error(f"Error clear state: {e}")

def get_escalation_data(user_id: str) -> Optional[Dict]:
    """Get escalation data"""
    if not redis_client: return None
    try:
        data_key = f"{ESCALATION_KEY_PREFIX}{user_id}"
        data_json = redis_client.get(data_key)
        if data_json:
            return json.loads(data_json)
        return None
    except Exception as e:
        logger.error(f"Error get data: {e}")
        return None

# --- Fungsi Chat History ---
def get_chat_history(user_id: str) -> List[Dict]:
    if not redis_client: return []
    try:
        key = f"{HISTORY_KEY_PREFIX}{user_id}"
        history_json_list = redis_client.lrange(key, 0, (HISTORY_MAX_TURNS * 2) - 1)
        history = [json.loads(item) for item in history_json_list]
        history.reverse() 
        return history
    except Exception as e:
        logger.error(f"Gagal mengambil history user {user_id} dari Redis: {e}")
        return []

def save_chat_history(user_id: str, user_message: str, ai_message: str):
    if not redis_client: return
    try:
        key = f"{HISTORY_KEY_PREFIX}{user_id}"
        redis_client.lpush(key, json.dumps({"role": "assistant", "content": ai_message}))
        redis_client.lpush(key, json.dumps({"role": "user", "content": user_message}))
        redis_client.ltrim(key, 0, (HISTORY_MAX_TURNS * 2) - 1)
        logger.debug(f"💾 History disimpan untuk user {user_id}")
    except Exception as e:
        logger.error(f"Gagal menyimpan history user {user_id} ke Redis: {e}")

# --- Fungsi RAG & AI ---
def search_knowledge(query_text: str, n_results: int = 3) -> list[str]:
    if collection is None: return []
    try:
        results = collection.query(query_texts=[query_text], n_results=n_results)
        if results and 'documents' in results and results['documents'][0]:
            return results['documents'][0]
        logger.warning(f"Query '{query_text}' tidak menghasilkan dokumen dari ChromaDB.")
        return []
    except Exception as e:
        logger.error(f"Error saat search ChromaDB: {e}", exc_info=True)
        return []

def build_prompt(query: str, context_chunks: list[str]) -> Tuple[str, str]:
    system_prompt = """Anda adalah asisten virtual ahli untuk agen travel Haji & Umrah.
Nama Anda 'Asisten Inara'. Anda ramah, profesional, dan sangat membantu.
CARA MENJAWAB:
1. **PRIORITAS UTAMA**: Gunakan informasi dari "KONTEKS DATABASE" jika tersedia (info paket/review).
2. **PENGETAHUAN UMUM**: Jika konteks tidak mencukupi ATAU pertanyaan bersifat umum (tata cara haji, doa, dll), gunakan pengetahuan Anda.
3. **KONVERSASI**: Perhatikan riwayat chat sebelumnya (jika ada) untuk memberikan jawaban yang reaktif dan kontekstual.
4. **LOGIKA ESKALASI**: 
   Jika user meminta paket kustom atau layanan tambahan yang TIDAK ADA di konteks (seperti "umrah plus Mesir", "mobil pribadi", "paket keluarga besar"):
   - Sampaikan dengan sopan bahwa permintaan tersebut bersifat **khusus (custom)** dan perlu dicek ketersediaannya.
   - JANGAN menawarkan paket lain yang tidak relevan (seperti 'Plus Turki' jika ditanya 'Mesir').
   - HARUS **proaktif menawarkan** untuk meneruskan permintaan ini ke tim admin agar bisa dicarikan solusi. 
   - Gunakan frasa natural seperti: "Baik, untuk permintaan khusus seperti mobil pribadi, ini perlu dikoordinasikan lebih lanjut dengan tim kami. Saya bisa bantu teruskan pertanyaan Anda ke admin agar bisa segera dicek ketersediaan dan biayanya, bagaimana?"
   - Jika user setuju (memberikan afirmasi), JANGAN ulangi penawaran, tapi minta kontak mereka (misal: "Baik, Boleh informasikan email atau nomor WhatsApp Anda yang aktif agar bisa dihubungi oleh tim kami?").
"""
    if not context_chunks:
        context_str = "KONTEKS DATABASE: [Tidak ada informasi paket/review spesifik dari database untuk pertanyaan ini]"
    else:
        context_str = "KONTEKS DATABASE (Informasi Paket & Review):\n" + "\n---\n".join(context_chunks)

    user_prompt = f"""{context_str}
---
Pertanyaan Pelanggan: "{query}"
---
Jawab pertanyaan pelanggan berdasarkan prioritas dan peraturan di atas, perhatikan juga riwayat chat sebelumnya."""
    return system_prompt, user_prompt

# --- Fungsi AI Fallback ---
def call_groq_api(system_prompt: str, user_prompt: str, history: List[Dict]) -> Optional[str]:
    if not GROQ_API_KEY: return None
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_prompt})
    model_to_use = GROQ_MODEL
    if "Anda adalah classifier" in system_prompt: model_to_use = "llama3-8b-8192"
    payload = {"model": model_to_use, "messages": messages, "temperature": 0.0, "max_tokens": 800}
    try:
        logger.info(f"Mencoba Groq API (model: {model_to_use})...")
        response = requests.post(GROQ_URL, headers=headers, json=payload, timeout=15)
        response.raise_for_status()
        data = response.json()
        if "choices" in data and data["choices"]: return data["choices"][0]["message"]["content"].strip()
        return None
    except Exception as e:
        logger.error(f"Groq API error: {e}")
        return None

def call_openrouter_api(system_prompt: str, user_prompt: str, history: List[Dict]) -> Optional[str]:
    if not OPENROUTER_API_KEY: return None
    headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json", "HTTP-Referer": "http://localhost:8008", "X-Title": "Chatbot Haji Umrah"}
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_prompt})
    model_to_use = OPENROUTER_MODEL
    temp = 0.3
    if "Anda adalah classifier" in system_prompt:
        model_to_use = "openai/gpt-3.5-turbo"
        temp = 0.0
    payload = {"model": model_to_use, "messages": messages, "temperature": temp, "max_tokens": 800}
    try:
        logger.info(f"Mencoba OpenRouter API (model: {model_to_use})...")
        response = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        if "choices" in data and data["choices"]: return data["choices"][0]["message"]["content"].strip()
        return None
    except Exception as e:
        logger.error(f"OpenRouter API error: {e}")
        return None

def call_ollama_api(system_prompt: str, user_prompt: str, history: List[Dict]) -> Optional[str]:
    full_prompt = system_prompt
    for msg in history: full_prompt += f"\n\n{msg['role']}: {msg['content']}"
    full_prompt += f"\n\nuser: {user_prompt}"
    temp = 0.3
    if "Anda adalah classifier" in system_prompt: temp = 0.0
    payload = {"model": OLLAMA_MODEL, "prompt": full_prompt, "stream": False, "options": {"temperature": temp, "num_predict": 800}}
    try:
        logger.info(f"Mencoba Ollama API (model: {OLLAMA_MODEL})...")
        response = requests.post(OLLAMA_URL, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        if "response" in data: return data["response"].strip()
        return None
    except Exception as e:
        logger.error(f"Ollama API error: {e}")
        return None

def call_ai_with_fallback(system_prompt: str, user_prompt: str, history: List[Dict]) -> str:
    result = call_groq_api(system_prompt, user_prompt, history)
    if result: return result
    result = call_openrouter_api(system_prompt, user_prompt, history)
    if result: return result
    result = call_ollama_api(system_prompt, user_prompt, history)
    if result: return result
    if "Anda adalah classifier" in system_prompt:
        logger.error("❌ Semua AI provider gagal untuk KLASIFIKASI INTENT!")
        return "OTHER"
    logger.error("❌ Semua AI provider gagal!")
    return "Mohon maaf, semua layanan AI sedang tidak tersedia. Silakan coba lagi."

# --- Fungsi Logika Eskalasi ---
def _classify_escalation_intent(user_message: str) -> str:
    """Klasifikasi intent user: AFFIRM, NEGATE, atau OTHER"""
    logger.debug(f"🔍 Klasifikasi intent untuk: '{user_message}'")
    system_prompt = """Anda adalah classifier. User baru saja ditawari bantuan oleh admin ("...bagaimana?").
Tugas Anda adalah membaca balasan user dan menentukan niatnya.
FOKUS pada niat utama untuk 'melanjutkan', abaikan komentar tambahan.
- Jika user setuju/menerima tawaran (misal: "ya", "boleh", "ok", "tolong bantu", "siap", "lanjutkan"), balas HANYA dengan kata: AFFIRM
- Jika user menolak tawaran (misal: "tidak", "nanti saja", "tidak usah"), balas HANYA dengan kata: NEGATE
- Jika user bertanya hal lain / tidak jelas (misal: "kenapa?", "adminnya siapa?"), balas HANYA dengan kata: OTHER
"""
    result = call_ai_with_fallback(system_prompt, user_message, history=[])
    result_upper = result.strip().upper()
    if "AFFIRM" in result_upper:
        logger.debug("✅ Klasifikasi Intent: AFFIRM")
        return "AFFIRM"
    if "NEGATE" in result_upper:
        logger.debug("❌ Klasifikasi Intent: NEGATE")
        return "NEGATE"
    logger.debug("❓ Klasifikasi Intent: OTHER")
    return "OTHER"

def should_escalate_to_admin(message: str, ai_response: str) -> Tuple[bool, str]:
    """Deteksi apakah perlu eskalasi BARU"""
    message_lower = message.lower()
    response_lower = ai_response.lower()

    # Deteksi eskalasi dari keyword user
    keyword_triggers = [
        "admin", "customer service", "bicara", "langsung", "manusia", 
        "paket khusus", "custom package", "keluarga", "rombongan", "mobil pribadi",
        "kustom", "kustomisasi" 
    ]
    for keyword in keyword_triggers:
        if keyword in message_lower:
            reason = f"User meminta penanganan khusus (keyword: '{keyword}')"
            logger.info(f"🚨 Eskalasi Terdeteksi (Keyword): {reason}")
            return True, reason

    # Deteksi komplain
    complaint_triggers = ["komplain", "kecewa", "marah", "tidak puas", "refund", "batal", "keluhan", "masalah serius"]
    for keyword in complaint_triggers:
        if keyword in message_lower:
            reason = f"User komplain (keyword: '{keyword}')"
            logger.info(f"🚨 Eskalasi Terdeteksi (Komplain): {reason}")
            return True, reason

    # Deteksi dari respons AI
    ai_triggers = ["meneruskan ke admin", "tim kami akan membantu", "hubungi admin", "permintaan khusus", "dikoordinasikan lebih lanjut", "tim kami ya"]
    for trigger in ai_triggers:
        if trigger in response_lower:
            if len(message_lower.split()) > 2: 
                reason = f"AI menawarkan eskalasi (trigger: '{trigger}')"
                logger.info(f"🚨 Eskalasi Terdeteksi (AI Trigger): {reason}")
                return True, reason
                
    return False, ""

def _is_simple_affirmation(message: str) -> bool:
    """Deteksi afirmasi sederhana tanpa memanggil AI"""
    message_clean = re.sub(r'[\W_]+', ' ', message.lower()).strip()
    
    # Afirmasi eksplisit
    affirm_keywords = ['boleh', 'ya', 'ok', 'oke', 'silakan', 'lanjut', 'mau', 'setuju', 'iya', 'baik']
    
    # Cek kata tunggal
    if message_clean in affirm_keywords:
        logger.debug(f"✅ Afirmasi sederhana terdeteksi: '{message_clean}'")
        return True
    
    # Cek kombinasi umum
    words = message_clean.split()
    if len(words) <= 3:
        affirm_combos = [
            ['boleh', 'silakan'], ['ya', 'boleh'], ['ya', 'mau'], 
            ['ok', 'boleh'], ['oke', 'lanjut'], ['baik', 'lanjut']
        ]
        for combo in affirm_combos:
            if all(word in words for word in combo):
                logger.debug(f"✅ Afirmasi combo terdeteksi: {words}")
                return True
    
    return False

# --- FUNGSI UTAMA ---
def get_ai_response(
    user_id: str,
    message: str,
    channel: str = "web",
    user_contact: Optional[str] = None
) -> Dict:
    """
    FUNGSI UTAMA dengan STATE MACHINE yang DIPERBAIKI
    
    States:
    - None: Normal chat
    - AWAITING_CONFIRM: Menunggu user confirm eskalasi (ya/tidak)
    - AWAITING_CONTACT: Menunggu user berikan kontak
    """
    try:
        logger.info(f"📩 Processing message from {user_id}: '{message}'")
        
        # Get state & history
        current_state = get_escalation_state(user_id)
        history = get_chat_history(user_id) if redis_client else []
        logger.info(f"🔄 Current State: {current_state} | History length: {len(history)}")
        
        # Debug: Log state keys
        if redis_client:
            state_key = f"{ESCALATION_STATE_PREFIX}{user_id}"
            data_key = f"{ESCALATION_KEY_PREFIX}{user_id}"
            logger.debug(f"🔑 Redis keys - State: {state_key} | Data: {data_key}")
            logger.debug(f"🔑 State value: {redis_client.get(state_key)}")
            logger.debug(f"🔑 Data value: {redis_client.get(data_key)}")
        
        # ============================================================
        # STATE: AWAITING_CONTACT (User sudah confirm, butuh kontak)
        # ============================================================
        if current_state == "AWAITING_CONTACT":
            logger.info(f"📋 State: Menunggu kontak dari {user_id}")
            
            user_contact_info = _find_dynamic_contact(message, user_contact)
            
            if user_contact_info != "Tidak Diberikan":
                logger.info(f"✅ Kontak diterima: {user_contact_info}")
                
                # Load escalation data
                escalation_data = get_escalation_data(user_id)
                original_message = escalation_data.get("original_message", message) if escalation_data else message
                escalation_reason = escalation_data.get("reason", "User memberikan kontak") if escalation_data else "User memberikan kontak"
                
                ai_response = "Terima kasih! Permintaan Anda dan kontak Anda telah kami teruskan ke tim admin. Admin akan segera menghubungi Anda. 🙏"
                
                # KIRIM NOTIFIKASI WA
                try:
                    logger.info(f"📤 Mengirim notifikasi WA ke admin...")
                    notify_admin_whatsapp(
                        user_id=user_id,
                        user_contact=user_contact_info,
                        user_message=original_message,
                        reason=escalation_reason
                    )
                    logger.info(f"✅✅✅ Notifikasi WA BERHASIL dikirim ke admin!")
                except Exception as e:
                    logger.error(f"❌ GAGAL mengirim notifikasi WA: {e}", exc_info=True)
                    ai_response += "\n\n⚠️ Catatan: Terjadi kendala teknis dalam mengirim notifikasi ke admin, namun data Anda telah tersimpan."

                save_chat_history(user_id, message, ai_response)
                clear_escalation_state(user_id)
                
                return {
                    "response": ai_response,
                    "source": "Eskalasi Selesai",
                    "escalated": True,
                    "escalation_reason": escalation_reason
                }
            else:
                # Kontak tidak valid
                logger.warning(f"⚠️ Kontak tidak valid: '{message}'")
                ai_response = "Maaf, sepertinya itu bukan email atau nomor WhatsApp yang valid. Mohon informasikan kontak Anda yang benar agar tim kami bisa menghubungi (contoh: 08123456789 atau email@domain.com)."
                save_chat_history(user_id, message, ai_response)
                return {
                    "response": ai_response,
                    "source": "Eskalasi (Menunggu Kontak)",
                    "escalated": True,
                    "escalation_reason": "Menunggu info kontak valid"
                }
        
        # ============================================================
        # STATE: AWAITING_CONFIRM (User diminta konfirmasi eskalasi)
        # ============================================================
        if current_state == "AWAITING_CONFIRM":
            logger.info(f"🔍 State: Menunggu konfirmasi eskalasi dari {user_id}")
            
            # Klasifikasi intent
            if _is_simple_affirmation(message):
                intent = "AFFIRM"
            else:
                intent = _classify_escalation_intent(message)
            
            logger.info(f"🎯 Intent: {intent}")
            
            if intent == "AFFIRM":
                logger.info(f"✅ User SETUJU eskalasi")
                
                # Response yang lebih natural tanpa mengulang konteks
                ai_response = "Baik, tim kami akan segera membantu Anda. Boleh informasikan email atau nomor WhatsApp Anda yang aktif agar bisa segera dihubungi oleh tim kami?"
                
                # Update state ke AWAITING_CONTACT (data sudah tersimpan sebelumnya)
                escalation_data = get_escalation_data(user_id)
                set_escalation_state(user_id, "AWAITING_CONTACT", escalation_data)
                
                save_chat_history(user_id, message, ai_response)
                return {
                    "response": ai_response,
                    "source": "Eskalasi (Menunggu Kontak)",
                    "escalated": True,
                    "escalation_reason": "User mengkonfirmasi eskalasi"
                }
            
            elif intent == "NEGATE":
                logger.info(f"❌ User MENOLAK eskalasi")
                clear_escalation_state(user_id)
                # Fall through ke normal chat
            
            # else (intent == "OTHER"): Fall through ke normal chat

        # ============================================================
        # STATE: NORMAL CHAT (atau lanjut dari NEGATE/OTHER)
        # ============================================================
        logger.info(f"💬 State: Chat normal untuk {user_id}")
        
        # RAG: Cari di knowledge base
        context_chunks = search_knowledge(message, n_results=3)
        context_found = bool(context_chunks)
        
        # Build prompt & call AI
        system_prompt, user_prompt = build_prompt(message, context_chunks)
        ai_response = call_ai_with_fallback(system_prompt, user_prompt, history)
        
        # Cek apakah perlu eskalasi BARU
        should_escalate, escalation_reason = should_escalate_to_admin(message, ai_response)

        if should_escalate:
            logger.info(f"🚨 ESKALASI BARU: {escalation_reason}")
            
            # Tambahkan notice eskalasi jika belum ada
            if not any(s in ai_response.lower() for s in ["admin", "tim kami", "bagaimana?"]):
                escalation_notice = (
                    "\n\n⚠️ *Permintaan Anda sepertinya bersifat khusus.* "
                    "Saya bisa bantu teruskan ke tim admin kami untuk dicarikan solusi, bagaimana?"
                )
                ai_response += escalation_notice
            
            # Set state ke AWAITING_CONFIRM & simpan data
            escalation_data = {
                "original_message": message,
                "reason": escalation_reason
            }
            set_escalation_state(user_id, "AWAITING_CONFIRM", escalation_data)
        
        # Simpan ke history
        save_chat_history(user_id, message, ai_response)
        
        source = "AI + Knowledge Base" if context_found else "AI (General Knowledge)"

        return {
            "response": ai_response,
            "source": source,
            "escalated": should_escalate,
            "escalation_reason": escalation_reason if should_escalate else None
        }

    except Exception as e:
        logger.error(f"❌ FATAL ERROR in get_ai_response: {e}", exc_info=True)
        return {
            "response": "Mohon maaf, terjadi kesalahan sistem. Silakan coba lagi atau hubungi admin kami.",
            "source": "error",
            "escalated": True,
            "escalation_reason": f"SYSTEM_ERROR: {str(e)}"
        }