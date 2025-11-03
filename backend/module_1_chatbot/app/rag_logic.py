# app/rag_logic.py (Versi Pangkas + Perbaikan Sesuai Rencana Dummy .txt)
import os
import requests
import chromadb
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import logging
from typing import Tuple, Optional, Dict

# Import notifikasi WA, bukan DB
from .whatsapp_handler import notify_admin_whatsapp

logger = logging.getLogger(__name__)
load_dotenv()

# --- KONFIGURASI AI (Tetap sama) ---
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
collection = None # <-- [FIX] Kita hanya butuh SATU collection
try:
    logger.info("Memulai inisialisasi model SentenceTransformer...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    logger.info("✅ Model SentenceTransformer berhasil di-load.")
    
    logger.info("Memulai inisialisasi ChromaDB Client...")
    client = chromadb.PersistentClient(path="./chroma_db")
    logger.info("✅ ChromaDB Client berhasil dibuat.")

    # [FIX] Gunakan get_or_create_collection untuk 'haji_umrah_kb'
    collection_name = "haji_umrah_kb"
    collection = client.get_or_create_collection(name=collection_name)
    logger.info(f"✅ Collection '{collection_name}' berhasil didapatkan.")

except Exception as e:
    logger.error(f"FATAL: Error saat inisialisasi model atau ChromaDB: {e}", exc_info=True)

def search_knowledge(query_text: str, n_results: int = 3) -> list[str]:
    """[FIX] Mencari dokumen relevan dari SATU collection."""
    if collection is None:
        logger.error("search_knowledge dipanggil tapi collection ChromaDB belum siap.")
        return []
    
    try:
        results = collection.query(query_texts=[query_text], n_results=n_results)
        if results and 'documents' in results and results['documents'][0]:
            return results['documents'][0]
        else:
            logger.warning(f"Query '{query_text}' tidak menghasilkan dokumen dari ChromaDB.")
            return []
        
    except Exception as e:
        logger.error(f"Error saat search ChromaDB: {e}", exc_info=True)
        return []

# (Fungsi build_prompt, call_groq_api, call_openrouter_api, call_ollama_api, call_ai_with_fallback biarkan sama)
# ...
def build_prompt(query: str, context_chunks: list[str]) -> Tuple[str, str]:
    """Membangun System Prompt dan User Prompt."""
    system_prompt = """Anda adalah asisten virtual ahli untuk agen travel Haji & Umrah.
Tugas Anda adalah membantu pelanggan dengan pengetahuan mendalam tentang:
- Ibadah Haji dan Umrah (rukun, tata cara, doa, sejarah, hukum syariat)
- Paket perjalanan (dari konteks)
- Review pelanggan (dari konteks)

CARA MENJAWAB:
1. **PRIORITAS UTAMA**: Gunakan informasi dari "KONTEKS DATABASE" jika tersedia (info paket/review).
2. **PENGETAHUAN UMUM**: Jika konteks tidak mencukupi ATAU pertanyaan bersifat umum (tata cara haji, doa, dll), gunakan pengetahuan Anda.
3. **GABUNGAN**: Kombinasikan konteks database dengan pengetahuan umum.

PERATURAN PENTING:
- JANGAN mengarang harga atau detail paket yang tidak ada di konteks
- Selalu ramah, informatif, dan menggunakan Bahasa Indonesia yang baik"""

    if not context_chunks:
        context_str = """KONTEKS DATABASE: 
[Tidak ada informasi paket/review spesifik dari database untuk pertanyaan ini]
"""
    else:
        context_str = "KONTEKS DATABASE (Informasi Paket & Review):\n" + "\n---\n".join(context_chunks)

    user_prompt = f"""{context_str}
---
Pertanyaan Pelanggan: "{query}"
---
Jawab pertanyaan pelanggan berdasarkan prioritas dan peraturan di atas."""
    
    return system_prompt, user_prompt

def call_groq_api(system_prompt: str, user_prompt: str) -> Optional[str]:
    """Memanggil Groq API (Prioritas 1)."""
    if not GROQ_API_KEY or len(GROQ_API_KEY) < 20:
        logger.warning("GROQ_API_KEY tidak dikonfigurasi.")
        return None
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.3, "max_tokens": 800
    }
    try:
        logger.info(f"Mencoba Groq API (model: {GROQ_MODEL})...")
        response = requests.post(GROQ_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        if "choices" in data and data["choices"]:
            content = data["choices"][0]["message"]["content"]
            logger.info("✅ Groq API berhasil!")
            return content.strip()
        return None
    except Exception as e:
        logger.error(f"Groq API error: {e}")
        return None

def call_openrouter_api(system_prompt: str, user_prompt: str) -> Optional[str]:
    """Memanggil OpenRouter API (Backup 1)."""
    if not OPENROUTER_API_KEY or "sk-or-" not in OPENROUTER_API_KEY:
        logger.warning("OPENROUTER_API_KEY tidak dikonfigurasi.")
        return None
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8008",
        "X-Title": "Chatbot Haji Umrah"
    }
    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.3, "max_tokens": 800
    }
    try:
        logger.info(f"Mencoba OpenRouter API (model: {OPENROUTER_MODEL})...")
        response = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        if "choices" in data and data["choices"]:
            content = data["choices"][0]["message"]["content"]
            logger.info("✅ OpenRouter API berhasil!")
            return content.strip()
        return None
    except Exception as e:
        logger.error(f"OpenRouter API error: {e}")
        return None

def call_ollama_api(system_prompt: str, user_prompt: str) -> Optional[str]:
    """Memanggil Ollama API Lokal (Backup 2)."""
    full_prompt = f"{system_prompt}\n\n{user_prompt}"
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": full_prompt,
        "stream": False,
        "options": {"temperature": 0.3, "num_predict": 800}
    }
    try:
        logger.info(f"Mencoba Ollama API (model: {OLLAMA_MODEL})...")
        response = requests.post(OLLAMA_URL, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        if "response" in data:
            content = data["response"]
            logger.info("✅ Ollama API berhasil!")
            return content.strip()
        return None
    except Exception as e:
        logger.error(f"Ollama API error: {e}")
        return None

def call_ai_with_fallback(system_prompt: str, user_prompt: str) -> str:
    """Memanggil AI dengan fallback mechanism."""
    result = call_groq_api(system_prompt, user_prompt)
    if result: return result
    result = call_openrouter_api(system_prompt, user_prompt)
    if result: return result
    result = call_ollama_api(system_prompt, user_prompt)
    if result: return result
    
    logger.error("❌ Semua AI provider gagal!")
    return "Mohon maaf, semua layanan AI sedang tidak tersedia. Silakan coba lagi."
# ...

def should_escalate_to_admin(message: str, context_found: bool) -> Tuple[bool, str]:
    """
    [LOGIKA BARU] Menentukan apakah message harus di-escalate.
    """
    message_lower = message.lower()
    
    # 1. Eskalasi berdasarkan Keyword (Permintaan langsung)
    keyword_triggers = [
        "admin", "customer service", "bicara", "langsung", "manusia", 
        "paket khusus", "custom package", "keluarga saya", "rombongan"
    ]
    for keyword in keyword_triggers:
        if keyword in message_lower:
            reason = f"User meminta bicara langsung (keyword: '{keyword}')"
            logger.info(f"🚨 Eskalasi (Keyword): {reason}")
            return True, reason
            
    # 2. Eskalasi berdasarkan Keyword (Komplain)
    complaint_triggers = [
        "komplain", "kecewa", "marah", "tidak puas", "refund", "batal",
        "keluhan", "masalah serius", "tidak profesional", "tertipu", "penipuan"
    ]
    for keyword in complaint_triggers:
        if keyword in message_lower:
            reason = f"User komplain (keyword: '{keyword}')"
            logger.info(f"🚨 Eskalasi (Komplain): {reason}")
            return True, reason
            
    # 3. Eskalasi berdasarkan Kompleksitas
    greeting_triggers = ["halo", "hai", "assalamualaikum", "pagi", "siang", "sore", "malam", "terima kasih", "makasih"]
    is_greeting = any(greet in message_lower for greet in greeting_triggers)

    if not context_found and not is_greeting:
        reason = "Pertanyaan kompleks (tidak ada di KB) & bukan sapaan"
        logger.info(f"🚨 Eskalasi (Kompleks): {reason}")
        return True, reason

    return False, ""

def get_ai_response(
    user_id: str, 
    message: str, 
    channel: str = "web",
    user_contact: Optional[str] = None
) -> Dict:
    """
    FUNGSI UTAMA: Mendapatkan AI response dengan eskalasi via Notifikasi WA.
    """
    try:
        # 1. Search knowledge base
        context_chunks = search_knowledge(message, n_results=3) # <-- [FIX] n_results=3
        context_found = bool(context_chunks)
        
        # 2. Build prompt
        system_prompt, user_prompt = build_prompt(message, context_chunks)
        
        # 3. Call AI
        ai_response = call_ai_with_fallback(system_prompt, user_prompt)
        
        # 4. Check if escalation needed (Logika Baru)
        should_escalate, escalation_reason = should_escalate_to_admin(message, context_found)
        
        # 5. Kirim Notifikasi WA jika eskalasi
        if should_escalate:
            try:
                notify_admin_whatsapp(
                    user_id=user_id,
                    user_contact=user_contact,
                    user_message=message,
                    reason=escalation_reason
                )
                logger.info(f"📢 Notifikasi eskalasi dikirim ke Admin WA")
                
                escalation_notice = (
                    "\n\n⚠️ *Pertanyaan Anda terdeteksi kompleks dan telah diteruskan "
                    "ke Customer Service kami.*\n\nAdmin kami akan segera menghubungi Anda "
                    f"(melalui {user_contact if user_contact else 'kontak Anda'}) untuk bantuan lebih lanjut."
                )
                ai_response += escalation_notice
                
            except Exception as e:
                logger.error(f"Error mengirim notifikasi eskalasi: {e}")
        
        # 6. Determine source
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