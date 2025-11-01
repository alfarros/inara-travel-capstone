# /module_2_recommender/app/logic.py
import pandas as pd
import pickle
from sqlalchemy.orm import Session
from sqlalchemy import text
import logging

MODEL_STORE_PATH = "./models_store"
logger = logging.getLogger(__name__)

# --- 1. Load Semua Model & Data ---
try:
    # Load Model CB
    cb_cosine_sim = pickle.load(open(f"{MODEL_STORE_PATH}/cb_cosine_sim.pkl", "rb"))
    cb_packages_df = pd.read_pickle(f"{MODEL_STORE_PATH}/cb_packages_df.pkl")
    # Buat mapping: package_id -> index
    cb_indices = pd.Series(cb_packages_df.index, index=cb_packages_df['package_id'])

    # Load Model CF
    cf_model_svd = pickle.load(open(f"{MODEL_STORE_PATH}/cf_svd_model.pkl", "rb"))
    cf_interactions_df = pd.read_pickle(f"{MODEL_STORE_PATH}/cf_interactions_df.pkl")
    cf_unique_package_ids = cf_interactions_df['package_id'].unique()
    
    logger.info("Semua model rekomendasi (CB & CF) berhasil di-load.")

except FileNotFoundError:
    logger.error(f"FATAL: File model tidak ditemukan di {MODEL_STORE_PATH}.")
    logger.error("Pastikan Anda sudah menjalankan skrip 'train_recommender.py'.")
    cb_cosine_sim, cb_packages_df, cf_model_svd = None, None, None
except Exception as e:
    logger.error(f"Error saat load model: {e}")
    cb_cosine_sim, cb_packages_df, cf_model_svd = None, None, None


# --- 2. Logika Helper (Query DB) ---
def get_user_interaction_count(db: Session, user_id: str) -> int:
    """Cek jumlah interaksi user untuk cold start."""
    # MENGAPA: Kita query 'interactions' yang di-load dari CSV
    result = db.execute(text(f"SELECT COUNT(DISTINCT package_id) FROM interactions WHERE user_id = :user_id"), {"user_id": user_id})
    return result.scalar_one_or_none() or 0

def get_last_viewed_package(db: Session, user_id: str) -> str:
    """Dapatkan paket terakhir dilihat (untuk CB cold start)."""
    result = db.execute(text(
        f"SELECT package_id FROM interactions WHERE user_id = :user_id "
        f"AND event_type = 'view' ORDER BY timestamp DESC LIMIT 1"
    ), {"user_id": user_id})
    return result.scalar_one_or_none()

def get_popular_packages(db: Session, n: int) -> list:
    """Fallback: Ambil paket paling populer (banyak di-book)."""
    result = db.execute(text(
        f"SELECT package_id, COUNT(package_id) as count FROM interactions "
        f"WHERE event_type = 'book' GROUP BY package_id ORDER BY count DESC LIMIT :n"
    ), {"n": n})
    return [row[0] for row in result.fetchall()]

def get_package_details(db: Session, package_ids: list) -> list:
    """Ambil detail paket dari DB berdasarkan list ID."""
    if not package_ids:
        return []
    
    # MENGAPA: 'placeholder' dinamis untuk query 'IN'
    placeholders = ", ".join([f"'{pid}'" for pid in package_ids])
    query = text(f"SELECT package_id, name, description, price FROM packages WHERE package_id IN ({placeholders})")
    
    result = db.execute(query)
    
    # Buat mapping hasil query
    results_map = {row[0]: {"package_id": row[0], "name": row[1], "description": row[2], "price": row[3]} for row in result.fetchall()}
    
    # Kembalikan dalam urutan asli
    return [results_map[pid] for pid in package_ids if pid in results_map]


# --- 3. Logika Rekomendasi Inti ---

def get_content_based_recs(package_id: str, n: int) -> list:
    """Dapatkan rekomendasi CB berdasarkan 1 package_id."""
    if cb_cosine_sim is None: return []
    
    try:
        idx = cb_indices[package_id]
        sim_scores = list(enumerate(cb_cosine_sim[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = sim_scores[1:n+1] # Ambil top-N (abaikan diri sendiri)
        
        pkg_indices = [i[0] for i in sim_scores]
        return cb_packages_df['package_id'].iloc[pkg_indices].tolist()
    except KeyError:
        logger.warning(f"CB Gagal: package_id {package_id} tidak ada di training set.")
        return []

def get_cf_recs(user_id: str, n: int) -> list:
    """Dapatkan rekomendasi CF (SVD) untuk user_id."""
    if cf_model_svd is None: return []

    # 1. Prediksi skor untuk semua paket yang *belum* di-rate user
    # (Untuk data dummy, kita prediksi saja semua)
    predictions = []
    for pkg_id in cf_unique_package_ids:
        # (uid, iid, r_ui)
        pred = cf_model_svd.predict(user_id, pkg_id, r_ui=0)
        predictions.append((pkg_id, pred.est)) # (package_id, estimated_score)
        
    # 2. Urutkan berdasarkan skor estimasi
    predictions.sort(key=lambda x: x[1], reverse=True)
    
    # 3. Ambil top-N package_ids
    top_n_ids = [pkg_id for pkg_id, score in predictions[:n]]
    return top_n_ids

def apply_business_rules(package_ids: list, db: Session) -> list:
    """
    Placeholder untuk aturan bisnis.
    Misal: Cek ketersediaan stok, jangan tampilkan paket kadaluarsa, dll.
    """
    # Untuk saat ini, kita anggap semua paket valid
    return package_ids