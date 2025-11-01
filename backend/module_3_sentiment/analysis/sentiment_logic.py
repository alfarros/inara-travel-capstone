# /module_3_sentiment/analysis/sentiment_logic.py
from transformers import pipeline
import logging
from typing import Tuple

# --- 1. Load Model (Sekali Saja) ---
MODEL_NAME = "mdhugol/indonesia-bert-sentiment-classification"

# Mapping label model ke sentiment yang lebih jelas
LABEL_MAPPING = {
    "LABEL_0": "NEGATIVE",  # Negatif
    "LABEL_1": "NEUTRAL",   # Netral
    "LABEL_2": "POSITIVE"   # Positif
}

try:
    # Set logging transformers ke ERROR agar tidak "berisik"
    logging.getLogger("transformers").setLevel(logging.ERROR)
    
    print(f"Memuat model sentiment: {MODEL_NAME}...")
    sentiment_pipeline = pipeline(
        "sentiment-analysis",
        model=MODEL_NAME,
        tokenizer=MODEL_NAME,
        device=-1  # CPU mode, set to 0 for GPU
    )
    print("Model sentiment berhasil di-load.")
except Exception as e:
    print(f"FATAL: Gagal memuat model Hugging Face: {e}")
    sentiment_pipeline = None

# --- 2. Logika Aspect-Based (ABSA) ---
ASPECT_KEYWORDS = {
    "Hotel": ["hotel", "kamar", "inap", "penginapan", "kasur", "bersih", "kotor", "sempit"],
    "Pemandu": ["pemandu", "muthawif", "tour guide", "sabar", "jelas", "ramah", "kasar"],
    "Transportasi": ["transportasi", "bus", "pesawat", "telat", "nyaman", "macet", "panas"],
    "Makanan": ["makanan", "katering", "menu", "variatif", "rasa", "enak", "hambar", "kurang"]
}

def detect_aspect(review_text: str) -> str:
    """Deteksi aspek dari ulasan berdasarkan keyword."""
    if not review_text: 
        return "Umum"
    
    review_lower = review_text.lower()
    detected_aspects = []
    
    for aspect, keywords in ASPECT_KEYWORDS.items():
        if any(keyword in review_lower for keyword in keywords):
            detected_aspects.append(aspect)
            
    if not detected_aspects:
        return "Umum"
    
    return ", ".join(detected_aspects)

# --- 3. Logika Analisis ---
def analyze_review_sentiment(review_text: str) -> Tuple[str, float]:
    """Jalankan pipeline sentiment dan mapping label."""
    
    # Validasi input
    if not review_text or not isinstance(review_text, str):
        print(f"WARNING: Input tidak valid: {review_text}")
        return "ERROR", 0.0
    
    if not sentiment_pipeline:
        print("ERROR: Model sentiment belum di-load!")
        return "ERROR", 0.0
        
    try:
        # Truncate text agar sesuai limit model (512 token)
        truncated_text = review_text[:512]
        
        # Prediksi
        result = sentiment_pipeline(truncated_text)[0]
        
        # Mapping label (LABEL_0/1/2 -> NEGATIVE/NEUTRAL/POSITIVE)
        raw_label = result['label']
        mapped_label = LABEL_MAPPING.get(raw_label, "UNKNOWN")
        score = result['score']
        
        print(f"Sentiment Analysis: '{truncated_text[:50]}...' -> {mapped_label} ({score:.2f})")
        
        return mapped_label, score
        
    except Exception as e:
        print(f"ERROR saat prediksi sentiment: {e}")
        import traceback
        traceback.print_exc()
        return "ERROR", 0.0

# --- 4. Logika Prioritas ---
def classify_priority(sentiment: str, aspect: str) -> str:
    """Tentukan prioritas keluhan berdasarkan aturan bisnis."""
    
    if sentiment == "NEGATIVE":
        if "Hotel" in aspect or "Transportasi" in aspect:
            return "Kritis"
        elif "Pemandu" in aspect or "Makanan" in aspect:
            return "Tinggi"
        else:
            return "Sedang"
    elif sentiment == "POSITIVE":
        return "Rendah"
    else:  # NEUTRAL atau ERROR
        return "Rendah"