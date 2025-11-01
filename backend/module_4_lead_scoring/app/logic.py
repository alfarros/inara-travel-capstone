# /module_4_lead_scoring/app/logic.py
import xgboost as xgb
import shap
import joblib
import pandas as pd
import numpy as np
import json
import logging
import os
from pathlib import Path
from .schemas import LeadFeaturesInput

MODEL_STORE_PATH = os.getenv("MODEL_STORE_PATH", "/app/model_store")
logger = logging.getLogger(__name__)

# --- Load Model & Artefak (Sekali saat startup) ---
try:
    # Model XGBoost
    model = xgb.Booster()
    model.load_model(f"{MODEL_STORE_PATH}/lead_scorer.json")
    logger.info("✓ Model XGBoost loaded")
    
    # Encoder
    encoder = joblib.load(f"{MODEL_STORE_PATH}/one_hot_encoder.joblib")
    logger.info("✓ OneHotEncoder loaded")
    
    # Urutan Kolom
    with open(f"{MODEL_STORE_PATH}/feature_columns.json", "r") as f:
        TRAINING_COLUMNS = json.load(f)
    logger.info(f"✓ Feature columns loaded ({len(TRAINING_COLUMNS)} features)")
    
    # SHAP Explainer (OPTIONAL - tidak wajib untuk API berjalan)
    explainer = None
    shap_paths = [
        f"{MODEL_STORE_PATH}/shap_explainer.joblib",
        f"{MODEL_STORE_PATH}/shap_explainer.pkl"
    ]
    
    for shap_path in shap_paths:
        if Path(shap_path).exists() and Path(shap_path).stat().st_size > 0:
            try:
                explainer = joblib.load(shap_path)
                logger.info(f"✓ SHAP Explainer loaded from {shap_path}")
                break
            except Exception as e:
                logger.warning(f"Failed to load SHAP from {shap_path}: {e}")
    
    if explainer is None:
        logger.warning("⚠ SHAP Explainer not available. Will use fallback explanations.")
    
    logger.info(f"✓ Model Lead Scoring berhasil di-load dari {MODEL_STORE_PATH}")
    
except FileNotFoundError as e:
    logger.error(f"FATAL: Artefak model tidak ditemukan di {MODEL_STORE_PATH}")
    logger.error(f"Detail error: {e}")
    logger.error("Pastikan Anda sudah menjalankan skrip 'train_lead_scorer.py'.")
    model, encoder, explainer, TRAINING_COLUMNS = None, None, None, []
except Exception as e:
    logger.error(f"Error saat load artefak model: {e}")
    import traceback
    logger.error(traceback.format_exc())
    model, encoder, explainer, TRAINING_COLUMNS = None, None, None, []

def preprocess_input(data: LeadFeaturesInput) -> pd.DataFrame:
    """
    Mengubah input Pydantic menjadi DataFrame yang siap
    diproses oleh XGBoost (termasuk One-Hot Encoding).
    """
    if not encoder or not TRAINING_COLUMNS:
        raise ValueError("Encoder atau daftar kolom training belum di-load.")

    input_dict = data.dict()
    df = pd.DataFrame([input_dict])
    
    # Identifikasi kolom kategorikal (harus sama dengan saat training)
    categorical_cols = encoder.feature_names_in_
    
    # Terapkan One-Hot Encoding
    encoded_cats = encoder.transform(df[categorical_cols])
    encoded_cols = encoder.get_feature_names_out(categorical_cols)
    encoded_cats_df = pd.DataFrame(encoded_cats, columns=encoded_cols, index=df.index)
    
    # Gabungkan dengan kolom numerik
    df_processed = pd.concat([df.drop(categorical_cols, axis=1), encoded_cats_df], axis=1)
    
    # Reindex agar urutan kolom SAMA PERSIS dengan training
    df_final = df_processed.reindex(columns=TRAINING_COLUMNS, fill_value=0)
    
    return df_final

def get_score_and_reason(features_df: pd.DataFrame) -> tuple:
    """Mendapatkan skor probabilitas dan alasan."""
    if not model:
        raise ValueError("Model belum di-load.")
        
    # 1. Prediksi Probabilitas
    dmatrix = xgb.DMatrix(features_df, feature_names=TRAINING_COLUMNS)
    probability = model.predict(dmatrix)[0]
    score = int(probability * 100)
    
    # 2. Analisis SHAP (jika tersedia)
    reason = "Model prediction based on input features"
    
    if explainer:
        try:
            shap_values_output = explainer.shap_values(features_df)
            
            # Cek tipe output SHAP
            if isinstance(shap_values_output, list) and len(shap_values_output) > 1:
                shap_values_for_positive_class = shap_values_output[1][0]
            else:
                shap_values_for_positive_class = shap_values_output[0]

            # Temukan fitur dengan |SHAP value| tertinggi
            abs_shap = np.abs(shap_values_for_positive_class)
            max_impact_idx = np.argmax(abs_shap)
            feature_name = TRAINING_COLUMNS[max_impact_idx]
            feature_value = features_df.iloc[0, max_impact_idx]
            shap_value = shap_values_for_positive_class[max_impact_idx]

            direction = "menaikkan" if shap_value > 0 else "menurunkan"
            reason = (f"Fitur paling berpengaruh ({direction} skor): "
                      f"{feature_name} = {feature_value:.2f}")

        except Exception as e:
            logger.warning(f"Gagal menghitung SHAP: {e}")
            
            # Fallback: gunakan feature importance dari model
            try:
                feature_importance = model.get_score(importance_type='weight')
                if feature_importance:
                    top_feature = max(feature_importance.items(), key=lambda x: x[1])
                    feature_idx = TRAINING_COLUMNS.index(top_feature[0])
                    feature_value = features_df.iloc[0, feature_idx]
                    reason = f"Top feature: {top_feature[0]} = {feature_value:.2f}"
            except:
                pass
    
    return score, reason