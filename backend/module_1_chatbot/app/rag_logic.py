# app/rag_logic.py (Versi Diperbaiki)
import os
import requests
import chromadb
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import logging
from typing import Tuple, Optional, Dict, List
import json
import redis

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

# --- KONFIGURASI AI ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"  # Diperbaiki: Hapus spasi
GROQ_MODEL = "llama-3.3-70b-versatile"
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"  # Diperbaiki: Hapus spasi
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

# --- Fungsi Chat History ---
def get_chat_history(user_id: str) -> List[Dict]:
    if not redis_client:
        return []
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
    if not redis_client:
        return
    try:
        key = f"{HISTORY_KEY_PREFIX}{user_id}"
        redis_client.lpush(key, json.dumps({"role": "assistant", "content": ai_message}))
        redis_client.lpush(key, json.dumps({"role": "user", "content": user_message}))
        redis_client.ltrim(key, 0, (HISTORY_MAX_TURNS * 2) - 1)
        redis_client.expire(key, 14400)
    except Exception as e:
        logger.error(f"Gagal menyimpan history user {user_id} ke Redis: {e}")

# --- Fungsi RAG & AI ---
def search_knowledge(query_text: str, n_results: int = 3) -> list[str]:
    if collection is None:
        return []
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

# --- Fungsi Panggilan AI ---

def call_groq_api(system_prompt: str, user_prompt: str, history: List[Dict]) -> Optional[str]:
    if not GROQ_API_KEY:
        return None
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_prompt})

    model_to_use = GROQ_MODEL
    if "Anda adalah classifier" in system_prompt:
        model_to_use = "llama3-8b-8192" # Model lebih cepat untuk klasifikasi

    payload = {"model": model_to_use, "messages": messages, "temperature": 0.0, "max_tokens": 800}
    try:
        logger.info(f"Mencoba Groq API (model: {model_to_use})...")
        response = requests.post(GROQ_URL, headers=headers, json=payload, timeout=15)
        response.raise_for_status()
        data = response.json()
        if "choices" in data and data["choices"]:
            return data["choices"][0]["message"]["content"].strip()
        return None
    except Exception as e:
        logger.error(f"Groq API error: {e}")
        return None

def call_openrouter_api(system_prompt: str, user_prompt: str, history: List[Dict]) -> Optional[str]:
    if not OPENROUTER_API_KEY:
        return None
    headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json", "HTTP-Referer": "http://localhost:8008", "X-Title": "Chatbot Haji Umrah"}
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_prompt})

    model_to_use = OPENROUTER_MODEL
    temp = 0.3
    if "Anda adalah classifier" in system_prompt:
        model_to_use = "openai/gpt-3.5-turbo" # Model cepat untuk klasifikasi
        temp = 0.0

    payload = {"model": model_to_use, "messages": messages, "temperature": temp, "max_tokens": 800}
    try:
        logger.info(f"Mencoba OpenRouter API (model: {model_to_use})...")
        response = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        if "choices" in data and data["choices"]:
            return data["choices"][0]["message"]["content"].strip()
        return None
    except Exception as e:
        logger.error(f"OpenRouter API error: {e}")
        return None

def call_ollama_api(system_prompt: str, user_prompt: str, history: List[Dict]) -> Optional[str]:
    full_prompt = system_prompt
    for msg in history:
        full_prompt += f"\n\n{msg['role']}: {msg['content']}"
    full_prompt += f"\n\nuser: {user_prompt}"

    temp = 0.3
    if "Anda adalah classifier" in system_prompt:
        temp = 0.0

    payload = {"model": OLLAMA_MODEL, "prompt": full_prompt, "stream": False, "options": {"temperature": temp, "num_predict": 800}}
    try:
        logger.info(f"Mencoba Ollama API (model: {OLLAMA_MODEL})...")
        response = requests.post(OLLAMA_URL, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        if "response" in data:
            return data["response"].strip()
        return None
    except Exception as e:
        logger.error(f"Ollama API error: {e}")
        return None

def call_ai_with_fallback(system_prompt: str, user_prompt: str, history: List[Dict]) -> str:
    result = call_groq_api(system_prompt, user_prompt, history)
    if result:
        return result
    result = call_openrouter_api(system_prompt, user_prompt, history)
    if result:
        return result
    result = call_ollama_api(system_prompt, user_prompt, history)
    if result:
        return result

    # Jika kita mencoba klasifikasi dan gagal, default ke 'OTHER' agar tidak error
    if "Anda adalah classifier" in system_prompt:
        logger.error("❌ Semua AI provider gagal untuk KLASIFIKASI INTENT!")
        return "OTHER"

    logger.error("❌ Semua AI provider gagal!")
    return "Mohon maaf, semua layanan AI sedang tidak tersedia. Silakan coba lagi."

def _classify_escalation_intent(user_message: str) -> str:
    """
    Menggunakan AI untuk mengklasifikasikan niat user sebagai respons
    terhadap tawaran eskalasi.
    """
    logger.debug(f"Mencoba klasifikasi intent untuk: '{user_message}'")

    system_prompt = """Anda adalah classifier. User baru saja ditawari bantuan oleh admin ("...bagaimana?").
Tugas Anda adalah membaca balasan user dan menentukan niatnya.
FOKUS pada niat utama untuk 'melanjutkan', abaikan komentar tambahan seperti "menarik", "keren", "bagus".

- Jika user setuju/menerima tawaran (misal: "ya", "boleh", "ok", "tolong bantu", "siap", "lanjutkan", "urus saja", "okeh, menarik, silakan"), balas HANYA dengan kata: AFFIRM
- Jika user menolak tawaran (misal: "tidak", "nanti saja", "tidak usah", "gausah"), balas HANYA dengan kata: NEGATE
- Jika user bertanya hal lain / tidak jelas / ragu-ragu (misal: "kenapa?", "adminnya siapa?", "memang bisa?", "biayanya berapa?"), balas HANYA dengan kata: OTHER
"""

    # Memanggil AI hanya dengan prompt ini (tanpa history)
    result = call_ai_with_fallback(system_prompt, user_message, history=[])
    result_upper = result.strip().upper()

    if "AFFIRM" in result_upper:
        logger.debug("Klasifikasi Intent: AFFIRM")
        return "AFFIRM"
    if "NEGATE" in result_upper:
        logger.debug("Klasifikasi Intent: NEGATE")
        return "NEGATE"

    logger.debug("Klasifikasi Intent: OTHER")
    return "OTHER"

def should_escalate_to_admin(message: str, ai_response: str) -> Tuple[bool, str]:
    message_lower = message.lower()
    response_lower = ai_response.lower()

    # 1. Eskalasi berdasarkan Keyword (Permintaan langsung)
    keyword_triggers = ["admin", "customer service", "bicara", "langsung", "manusia", "paket khusus", "custom package", "keluarga", "rombongan", "mobil pribadi"]
    for keyword in keyword_triggers:
        if keyword in message_lower:
            reason = f"User meminta penanganan khusus (keyword: '{keyword}')"
            logger.info(f"🚨 Eskalasi (Keyword): {reason}")
            return True, reason

    # 2. Eskalasi berdasarkan Keyword (Komplain)
    complaint_triggers = ["komplain", "kecewa", "marah", "tidak puas", "refund", "batal", "keluhan", "masalah serius", "tidak profesional", "tertipu", "penipuan"]
    for keyword in complaint_triggers:
        if keyword in message_lower:
            reason = f"User komplain (keyword: '{keyword}')"
            logger.info(f"🚨 Eskalasi (Komplain): {reason}")
            return True, reason

    # 3. Eskalasi berdasarkan Jawaban AI (AI menawarkan eskalasi)
    ai_triggers = ["meneruskan ke admin", "tim kami akan membantu", "hubungi admin", "permintaan khusus", "dikoordinasikan lebih lanjut", "tim kami ya"]
    for trigger in ai_triggers:
        if trigger in response_lower:
            if len(message_lower.split()) > 2: # Pastikan bukan sapaan singkat
                reason = f"AI menawarkan eskalasi (trigger: '{trigger}')"
                logger.info(f"🚨 Eskalasi (AI Trigger): {reason}")
                return True, reason

    return False, ""

def get_ai_response(
    user_id: str,
    message: str,
    channel: str = "web",
    user_contact: Optional[str] = None
) -> Dict:
    """
    FUNGSI UTAMA: Mendapatkan AI response dengan state eskalasi.
    """
    try:
        # 1. Ambil history chat
        history = get_chat_history(user_id)

        # --- [LOGIKA REAKTIF VERSI BARU] ---
        last_ai_message = ""
        if history and history[-1]["role"] == "assistant":
            last_ai_message = history[-1]["content"].lower()

        # Cek apakah AI di giliran sebelumnya baru saja menawarkan eskalasi
        if any(s in last_ai_message for s in ["bagaimana?", "tim kami?", "admin?", "teruskan?"]):

            # Gunakan AI classifier untuk cek niat user
            intent = _classify_escalation_intent(message)

            # Jika user setuju (bukan lagi cek keyword)
            if intent == "AFFIRM":

                logger.info(f"🚨 User ({user_id}) mengkonfirmasi eskalasi (Intent: AFFIRM).")

                # Buat respons manual, JANGAN panggil AI
                ai_response = "Baik, tim kami akan segera membantu Anda. Boleh informasikan email atau nomor WhatsApp Anda yang aktif agar bisa segera dihubungi oleh tim kami?"
                escalation_reason = "User mengkonfirmasi eskalasi"

                # Simpan ke history
                save_chat_history(user_id, message, ai_response)

                # Return respons manual
                return {
                    "response": ai_response,
                    "source": "Eskalasi Dikonfirmasi (Intent)",
                    "escalated": True,
                    "escalation_reason": escalation_reason
                }

            elif intent == "NEGATE":
                logger.info(f"User ({user_id}) menolak eskalasi (Intent: NEGATE). Melanjutkan chat.")
                # Biarkan alur berlanjut ke RAG/AI normal di bawah.

            # else (intent == "OTHER"):
                # User bertanya hal lain, biarkan AI normal yang menjawab
                # Biarkan alur berlanjut ke RAG/AI normal di bawah.

        # --- [AKHIR LOGIKA REAKTIF VERSI BARU] ---

        # --- Jika BUKAN konfirmasi, lanjutkan alur normal ---

        # 2. Search knowledge base
        context_chunks = search_knowledge(message, n_results=3)
        context_found = bool(context_chunks)

        # 3. Build prompt
        system_prompt, user_prompt = build_prompt(message, context_chunks)

        # 4. Call AI (dengan history)
        ai_response = call_ai_with_fallback(system_prompt, user_prompt, history)

        # Simpan jawaban bersih SEBELUM menambah notifikasi
        clean_ai_response = ai_response

        # 5. Check for escalation (HANYA eskalasi BARU)
        should_escalate, escalation_reason = should_escalate_to_admin(message, ai_response)

        # 6. Kirim Notifikasi WA jika eskalasi BARU
        if should_escalate:
            try:
                notify_admin_whatsapp(
                    user_id=user_id,
                    user_contact=user_contact,
                    user_message=message,
                    reason=escalation_reason
                )
                logger.info(f"📢 Notifikasi eskalasi (baru) dikirim ke Admin WA")

                # Cek apakah AI sudah menawarkan eskalasi
                if not any(s in ai_response.lower() for s in ["admin", "tim kami"]):
                    # Jika belum, tambahkan notifikasi manual
                    escalation_notice = (
                        "\n\n⚠️ *Pertanyaan Anda terdeteksi memerlukan penanganan khusus dan telah diteruskan "
                        "ke Customer Service kami.*\n\nAdmin kami akan segera menghubungi Anda."
                    )
                    ai_response += escalation_notice

            except Exception as e:
                logger.error(f"Error mengirim notifikasi eskalasi (baru): {e}")

        # 7. Simpan history ke Redis
        save_chat_history(user_id, message, clean_ai_response)

        # 8. Determine source
        source = "AI + Knowledge Base" if context_found else "AI (General Knowledge)"

        return {
            "response": ai_response,
            "source": source,
            "escalated": should_escalate,
            "escalation_reason": escalation_reason if should_escalate else None
        }

    except Exception as e:
        logger.error(f"Error in get_ai_response: {e}", exc_info=True)
        return {
            "response": "Mohon maaf, terjadi kesalahan sistem. Silakan coba lagi.",
            "source": "error",
            "escalated": True,
            "escalation_reason": f"SYSTEM_ERROR: {str(e)}"
        }
