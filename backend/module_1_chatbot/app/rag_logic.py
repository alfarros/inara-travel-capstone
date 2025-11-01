# app/rag_logic.py - VERSI PERBAIKAN LENGKAP
import os
import requests
import chromadb
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import logging
from typing import Tuple, Optional, Dict
from .database import save_to_admin_queue

logger = logging.getLogger(__name__)
load_dotenv()

# --- KONFIGURASI 3 PROVIDER AI ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
# --- PERUBAHAN MODEL SESUAI PERMINTAAN ---
OPENROUTER_MODEL = "openai/gpt-oss-20b:free"

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434/api/generate")
OLLAMA_MODEL = "gemma2:2b"

# --- Inisialisasi Model & DB ---
model = None
collection = None

# --- BLOK PERBAIKAN (NameError dan Collection not exist) ---
try:
    logger.info("Memulai inisialisasi model SentenceTransformer...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    logger.info("✅ Model SentenceTransformer berhasil di-load.")

    # 1. Definisikan 'client' DAHULU
    logger.info("Memulai inisialisasi ChromaDB Client...")
    client = chromadb.PersistentClient(path="./chroma_db")
    logger.info("✅ ChromaDB Client berhasil dibuat.")

    # 2. BARU gunakan 'client' untuk get_or_create_collection
    logger.info("Mencoba mendapatkan ATAU membuat collection 'haji_umrah_kb'...")
    collection = client.get_or_create_collection(name="haji_umrah_kb")
    logger.info("✅ Collection 'haji_umrah_kb' berhasil didapatkan/dibuat.")

except Exception as e:
    logger.error(f"FATAL: Error saat inisialisasi model atau ChromaDB: {e}", exc_info=True)
    model = None
    collection = None
# --- AKHIR BLOK PERBAIKAN ---


def search_knowledge(query_text: str, n_results: int = 3) -> list[str]:
    """Mencari dokumen relevan dari Vector DB (ChromaDB)."""
    if collection is None:
        logger.error("search_knowledge dipanggil tapi collection ChromaDB belum siap.")
        return []
    try:
        results = collection.query(query_texts=[query_text], n_results=n_results)
        if results and 'documents' in results and results['documents'] and results['documents'][0]:
            return results['documents'][0]
        else:
            logger.warning(f"Query '{query_text}' tidak menghasilkan dokumen dari ChromaDB.")
            return []
    except Exception as e:
        logger.error(f"Error saat search ChromaDB: {e}", exc_info=True)
        return []

def build_prompt(query: str, context_chunks: list[str]) -> Tuple[str, str]:
    """Membangun System Prompt dan User Prompt."""
    system_prompt = """Anda adalah asisten virtual ahli untuk agen travel Haji & Umrah yang berpengalaman.
Tugas Anda adalah membantu pelanggan dengan pengetahuan mendalam tentang:
- Ibadah Haji dan Umrah (rukun, tata cara, doa, sejarah, hukum syariat)
- Paket perjalanan Haji & Umrah
- Wisata religi dan ziarah (Madinah, Makkah, Palestina, Turki, Mesir, dll)
- Tips perjalanan dan persiapan (dokumen, kesehatan, perlengkapan)
- Destinasi wisata setelah ibadah (Dubai, Istanbul, Cairo, dll)

CARA MENJAWAB:
1. **PRIORITAS UTAMA**: Gunakan informasi dari "KONTEKS DATABASE" jika tersedia.
2. **PENGETAHUAN UMUM**: Jika konteks tidak mencukupi, gunakan pengetahuan Anda.
3. **GABUNGAN**: Kombinasikan konteks database dengan pengetahuan umum.

PERATURAN PENTING:
- JANGAN mengarang harga atau detail paket yang tidak ada di konteks
- Untuk harga/paket spesifik: HANYA gunakan informasi dari konteks database
- Selalu ramah, informatif, dan menggunakan Bahasa Indonesia yang baik
- Akhiri dengan tawaran bantuan lebih lanjut jika relevan"""

    if not context_chunks:
        context_str = """KONTEKS DATABASE: 
[Tidak ada informasi paket spesifik dari database untuk pertanyaan ini]

Namun saya dapat membantu Anda dengan pengetahuan umum tentang Haji, Umrah, dan wisata religi."""
    else:
        context_str = "KONTEKS DATABASE (Informasi Paket & Kebijakan Agen):\n" + "\n---\n".join(context_chunks)

    user_prompt = f"""{context_str}

---
Pertanyaan Pelanggan: "{query}"
---

INSTRUKSI MENJAWAB:
- Jika pertanyaan tentang HARGA/PAKET SPESIFIK: Gunakan hanya info dari "KONTEKS DATABASE" di atas
- Jika pertanyaan tentang PENGETAHUAN UMUM: Jawab dengan lengkap menggunakan pengetahuan Anda
- Berikan jawaban yang lengkap, informatif, dan membantu"""
    
    return system_prompt, user_prompt

def call_groq_api(system_prompt: str, user_prompt: str) -> Optional[str]:
    """Memanggil Groq API (Prioritas 1)."""
    if not GROQ_API_KEY or len(GROQ_API_KEY) < 20:
        logger.warning("GROQ_API_KEY tidak dikonfigurasi.")
        return None

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 800
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
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            logger.warning("⚠️ Groq rate limit reached, switching to backup...")
        else:
            logger.error(f"Groq API error {e.response.status_code}: {e}")
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
        "temperature": 0.3,
        "max_tokens": 800
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
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            logger.warning("⚠️ OpenRouter rate limit reached, switching to backup...")
        else:
            logger.error(f"OpenRouter API error {e.response.status_code}: {e}")
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
        "options": {
            "temperature": 0.3,
            "num_predict": 800
        }
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
    # Priority 1: Groq
    result = call_groq_api(system_prompt, user_prompt)
    if result:
        return result
    
    # Priority 2: OpenRouter
    result = call_openrouter_api(system_prompt, user_prompt)
    if result:
        return result
    
    # Priority 3: Ollama
    result = call_ollama_api(system_prompt, user_prompt)
    if result:
        return result
    
    # Semua provider gagal
    logger.error("❌ Semua AI provider gagal!")
    return "Mohon maaf, semua layanan AI sedang tidak tersedia. Silakan coba lagi dalam beberapa saat atau hubungi admin."

def should_escalate_to_admin(message: str, response: str) -> Tuple[bool, str]:
    """
    Menentukan apakah message harus di-escalate ke admin.
    Returns: (should_escalate: bool, reason: str)
    """
    message_lower = message.lower()
    
    # Keywords yang memerlukan human support
    escalation_keywords = [
        "komplain", "kecewa", "marah", "tidak puas", "refund", "batal",
        "ganti rugi", "lapor", "keluhan", "masalah serius", "tidak profesional",
        "tertipu", "penipuan", "tidak sesuai", "janji palsu",
        "booking", "pesan paket", "daftar", "reservasi", "konfirmasi pembayaran"
    ]
    
    # Cek apakah ada keyword escalation
    for keyword in escalation_keywords:
        if keyword in message_lower:
            reason = f"Terdeteksi keyword '{keyword}' yang memerlukan penanganan admin"
            logger.info(f"🚨 Escalation triggered: {reason}")
            return True, reason
    
    # Cek jika AI response mengandung "hubungi admin" atau sejenisnya
    response_lower = response.lower()
    if any(phrase in response_lower for phrase in ["hubungi admin", "kontak customer service", "tim kami akan"]):
        reason = "AI merekomendasikan kontak langsung dengan admin"
        logger.info(f"🚨 Escalation triggered: {reason}")
        return True, reason
    
    return False, ""

def get_ai_response(
    user_id: str, 
    message: str, 
    channel: str = "web",
    user_contact: Optional[str] = None
) -> Dict:
    """
    FUNGSI UTAMA: Mendapatkan AI response dengan escalation logic.
    
    Args:
        user_id: ID user (email/phone)
        message: Pertanyaan user
        channel: "web" atau "whatsapp"
        user_contact: Email atau nomor WA untuk followup
    
    Returns:
        {
            "response": str,
            "source": str,
            "escalated": bool,
            "escalation_reason": str (optional)
        }
    """
    try:
        # 1. Search knowledge base
        context_chunks = search_knowledge(message, n_results=3)
        
        # 2. Build prompt
        system_prompt, user_prompt = build_prompt(message, context_chunks)
        
        # 3. Call AI
        ai_response = call_ai_with_fallback(system_prompt, user_prompt)
        
        # 4. Check if escalation needed
        should_escalate, escalation_reason = should_escalate_to_admin(message, ai_response)
        
        # 5. Save to admin queue if escalated
        if should_escalate:
            try:
                message_id = save_to_admin_queue(
                    user_id=user_id,
                    channel=channel,
                    message=message,
                    ai_response=ai_response,
                    reason=escalation_reason,
                    user_contact=user_contact
                )
                logger.info(f"📢 Message #{message_id} escalated to admin")
                
                # Tambahkan notifikasi ke response
                escalation_notice = f"\n\n⚠️ *Pesan Anda telah diteruskan ke tim Customer Service kami untuk penanganan lebih lanjut.*"
                ai_response += escalation_notice
                
            except Exception as e:
                logger.error(f"Error saving to admin queue: {e}")
        
        # 6. Determine source
        source = "AI + Knowledge Base" if context_chunks else "AI (General Knowledge)"
        
        return {
            "response": ai_response,
            "source": source,
            "escalated": should_escalate,
            "escalation_reason": escalation_reason if should_escalate else None
        }
        
    except Exception as e:
        logger.error(f"Error in get_ai_response: {e}", exc_info=True)
        return {
            "response": "Mohon maaf, terjadi kesalahan sistem. Silakan coba lagi atau hubungi admin.",
            "source": "error",
            "escalated": True,
            "escalation_reason": f"SYSTEM_ERROR: {str(e)}"
        }