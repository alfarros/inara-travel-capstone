# /module_4_lead_scoring/app/main.py
from fastapi import FastAPI, HTTPException
from . import schemas, logic
import logging

app = FastAPI(
    title="API Predictive Lead Scoring (Modul 4)",
    description="Memberikan skor probabilitas konversi lead (0-100). Latensi <200ms.",
    version="1.0.0"
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cek model saat startup
if not logic.model or not logic.encoder or not logic.explainer:
    logger.error("API STARTUP GAGAL: Artefak model tidak di-load.")
    # (Di produksi, ini harusnya menghentikan startup)

@app.get("/_health", status_code=200)
def health_check():
    return {"status": "OK", "model_loaded": logic.model is not None}

@app.post("/score_lead/{lead_id}", response_model=schemas.ScoringResponse)
def score_lead(lead_id: str, features: schemas.LeadFeaturesInput):
    """
    Menghitung skor lead berdasarkan fitur perilaku dan demografis.
    """
    if not logic.model:
        raise HTTPException(status_code=503, detail="Model tidak tersedia.")

    try:
        # 1. Preprocessing Input
        processed_df = logic.preprocess_input(features)
        
        # 2. Prediksi Skor & Alasan SHAP
        score, reason = logic.get_score_and_reason(processed_df)
        
        # 3. Aturan Bisnis (Contoh: > 75 dianggap 'Hot')
        is_hot_lead = score > 75 # Threshold ini bisa di-tuning
        
        # (Opsional: Log prediksi ini ke database/audit trail)
        logger.info(f"Scored Lead {lead_id}: Score={score}, Hot={is_hot_lead}, Reason='{reason}'")

        return {
            "lead_id": lead_id,
            "score": score,
            "is_hot_lead": is_hot_lead,
            "reason": reason
        }
        
    except ValueError as ve:
         logger.error(f"Value error scoring lead {lead_id}: {ve}")
         raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error scoring lead {lead_id}: {e}")
        raise HTTPException(status_code=500, detail="Gagal memproses skor lead.")