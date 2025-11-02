# /module_2_recommender/scripts/train_recommender.py
# --- VERSI SEMPURNA DENGAN HYBRID DATA SOURCE ---

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from surprise import SVD, Dataset, Reader
import pickle
import os
import time
from sqlalchemy import create_engine
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Memulai proses training model rekomendasi...")

# === 1. KONFIGURASI PATH ===
# Path data dummy (hanya untuk fallback)
DATA_PATH = "/dummy_data"
# Path penyimpanan model di dalam container
MODEL_STORE_PATH = "/app/models_store" 

# Pastikan folder models_store ada
os.makedirs(MODEL_STORE_PATH, exist_ok=True)


# === 2. KONEKSI DATABASE (Baru) ===
# Mengambil koneksi dari environment, sama seperti load_dummy_data.py
DB_USER = os.getenv("POSTGRES_USER", "admin")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "adminpass")
DB_NAME = os.getenv("POSTGRES_DB", "haji_umrah_db")
DB_HOST = "postgres-db" # Nama service dari docker-compose

engine = None
for i in range(5):
    try:
        DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:5432/{DB_NAME}"
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
             conn.execute("SELECT 1")
        logger.info(f"✅ Koneksi Database (Postgres) sukses di percobaan {i+1}.")
        break
    except Exception as e:
        logger.warning(f"Koneksi DB gagal, mencoba lagi... ({i+1}/5) Error: {e}")
        time.sleep(3)

if engine is None:
    logger.error("❌ Gagal terhubung ke database. Proses training dibatalkan.")
    exit(1)


# === 3. FUNGSI TRAINING MODEL ===

def train_content_based(db_engine):
    """
    Melatih Model Content-Based (CB)
    SUMBER DATA: Langsung dari tabel 'packages' di PostgreSQL.
    """
    logger.info("--- Melatih Model Content-Based (TF-IDF) ---")
    try:
        # [SEMPURNA] Ambil data paket terbaru dari DB, bukan CSV
        query = "SELECT package_id, name, description, category FROM packages"
        df_packages = pd.read_sql(query, db_engine)
        
        if df_packages.empty:
            logger.error("Tabel 'packages' di DB kosong. CB Training gagal.")
            return

        logger.info(f"Mengambil {len(df_packages)} paket dari DB untuk training CB.")
        
        # Gabungkan fitur teks untuk TF-IDF
        # (Pastikan 'category' ada di tabel 'packages' Anda)
        df_packages['content_text'] = df_packages['name'].fillna('') + ' ' + \
                                      df_packages['description'].fillna('') + ' ' + \
                                      df_packages['category'].fillna('')
    
        tfidf = TfidfVectorizer(stop_words=None)
        tfidf_matrix = tfidf.fit_transform(df_packages['content_text'])
        cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
        
        # Simpan model dan data
        pickle.dump(cosine_sim, open(f"{MODEL_STORE_PATH}/cb_cosine_sim.pkl", "wb"))
        pickle.dump(tfidf, open(f"{MODEL_STORE_PATH}/cb_tfidf_vectorizer.pkl", "wb"))
        df_packages.to_pickle(f"{MODEL_STORE_PATH}/cb_packages_df.pkl")
        
        logger.info("✅ Model Content-Based berhasil disimpan.")

    except Exception as e:
        logger.error(f"❌ Error saat melatih model CB: {e}", exc_info=True)

def train_collaborative_filtering(db_engine):
    """
    Melatih Model Collaborative Filtering (CF)
    LOGIKA HYBRID: Cek tabel 'reviews' di DB, jika kosong, pakai 'interactions.csv'.
    """
    logger.info("--- Melatih Model Collaborative Filtering (SVD) ---")
    df_for_training = None
    MIN_REVIEWS_FOR_TRAINING = 10 # Butuh minimal 10 review untuk train dari DB

    try:
        # [SEMPURNA] Cek jumlah data di tabel 'reviews'
        query_count = "SELECT COUNT(*) FROM reviews"
        review_count = pd.read_sql(query_count, db_engine).iloc[0, 0]
        
        if review_count >= MIN_REVIEWS_FOR_TRAINING:
            # --- LOGIKA 1: Ambil dari DB (Live Data) ---
            logger.info(f"Ditemukan {review_count} reviews di DB. Melatih dari tabel 'reviews'...")
            query = "SELECT user_id, package_id, rating FROM reviews"
            df_for_training = pd.read_sql(query, db_engine)

        else:
            # --- LOGIKA 2: Fallback ke CSV (Initial Data) ---
            logger.warning(f"Reviews di DB tidak cukup ({review_count}). Fallback ke 'interactions.csv'...")
            csv_path = f"{DATA_PATH}/interactions.csv"
            if not os.path.exists(csv_path):
                 logger.error(f"Fallback gagal! File {csv_path} tidak ditemukan.")
                 return
                 
            df_interactions = pd.read_csv(csv_path)
            # Buat 'rating' dummy: view=1, book=5
            df_interactions['rating'] = df_interactions['event_type'].apply(lambda x: 5 if x == 'book' else 1)
            df_for_training = df_interactions[['user_id', 'package_id', 'rating']]
            logger.info(f"Melatih dari {len(df_for_training)} data 'interactions.csv'.")

        # --- Proses Training (Sama seperti sebelumnya) ---
        if df_for_training is None or df_for_training.empty:
            logger.error("Tidak ada data untuk melatih CF. Proses dibatalkan.")
            return

        reader = Reader(rating_scale=(1, 5))
        data = Dataset.load_from_df(df_for_training, reader)
        
        trainset = data.build_full_trainset()
        model_svd = SVD(n_factors=50, n_epochs=20, random_state=42)
        model_svd.fit(trainset)
        
        # Simpan model
        pickle.dump(model_svd, open(f"{MODEL_STORE_PATH}/cf_svd_model.pkl", "wb"))
        # Simpan data yang digunakan untuk training (penting untuk logic.py)
        df_for_training.to_pickle(f"{MODEL_STORE_PATH}/cf_interactions_df.pkl")

        logger.info("✅ Model Collaborative Filtering (SVD) berhasil disimpan.")

    except Exception as e:
        logger.error(f"❌ Error saat melatih model CF: {e}", exc_info=True)


# === 4. EKSEKUSI TRAINING ===
if __name__ == "__main__":
    if engine:
        train_content_based(engine)
        train_collaborative_filtering(engine)
        logger.info("\n--- ✅ Proses Training Selesai ---")
        logger.info(f"Artefak model disimpan di {MODEL_STORE_PATH}")
    else:
        logger.error("Training dibatalkan karena koneksi DB gagal.")