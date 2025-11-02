# /module_2_recommender/scripts/load_safe_reviews.py
# PENGGANTI AMAN untuk skrip 'load_dummy_reviews.py'

import pandas as pd
from sqlalchemy import create_engine, text
import os
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- DB Setup ---
DB_USER = os.getenv("POSTGRES_USER", "admin")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "adminpass")
DB_NAME = os.getenv("POSTGRES_DB", "haji_umrah_db")
DB_HOST = "postgres-db"
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:5432/{DB_NAME}"

# Coba koneksi
engine = None
for _ in range(5):
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Koneksi Database (Postgres) sukses.")
        break
    except Exception as e:
        logger.warning(f"Koneksi DB gagal, mencoba lagi... Error: {e}")
        time.sleep(3)

if engine is None:
    logger.error("Gagal terhubung ke database. Abborting.")
    exit(1)

def load_data_safely():
    """
    Muat data dummy 'reviews.csv' ke tabel 'reviews' yang SUDAH ADA.
    Menggunakan 'append' dan menyesuaikan nama kolom.
    """
    table_name = "reviews"
    # Pastikan file dummy_data/reviews.csv ada
    # Path ini mengacu pada path di DALAM container
    csv_path = "/dummy_data/reviews.csv"
    
    try:
        # 1. Cek apakah data sudah ada
        with engine.connect() as conn:
            count = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
        
        if count > 0:
            logger.info(f"Tabel '{table_name}' sudah berisi {count} data. Proses load dilewati.")
            return

        # 2. Jika kosong, baca CSV
        logger.info(f"Tabel '{table_name}' kosong. Memuat data dari {csv_path}...")
        df = pd.read_csv(csv_path)
        
        # 3. [PENTING] Sesuaikan kolom CSV ke skema DB (models.py)
        #    CSV punya: review_id, review_text, timestamp, source, package_id, user_id
        #    DB butuh: comment, created_at, package_id, user_id, rating (opsional)
        
        # Ganti nama kolom
        df_renamed = df.rename(columns={
            "review_text": "comment",
            "timestamp": "created_at"
        })
        
        # Tambah kolom yang wajib ada di DB (sesuai models.py)
        # Kita beri 'rating' default jika tidak ada di CSV
        if 'rating' not in df_renamed.columns:
            df_renamed['rating'] = 4 # Beri rating 4
            
        # Set status default agar bisa diproses Modul 3
        df_renamed['sentiment_status'] = 'pending'
        
        # Pilih hanya kolom yang ada di tabel DB
        kolom_db = ['package_id', 'user_id', 'rating', 'comment', 'created_at', 'sentiment_status']
        df_final = df_renamed[kolom_db]

        # 4. Muat data ke DB dengan 'append'
        df_final.to_sql(table_name, engine, if_exists='append', index=False)
        
        logger.info(f"Data dummy review (aman) berhasil dimuat ke tabel '{table_name}'.")
        
    except FileNotFoundError:
        logger.error(f"ERROR: File '{csv_path}' tidak ditemukan di /dummy_data/.")
    except Exception as e:
        logger.error(f"Error saat memuat data: {e}", exc_info=True)

if __name__ == "__main__":
    load_data_safely()