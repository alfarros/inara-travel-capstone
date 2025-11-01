# /module_3_sentiment/scheduler.py
from apscheduler.schedulers.blocking import BlockingScheduler
from sqlalchemy import create_engine, text
import pandas as pd
import os
import time
import logging

# Import logika AI
from analysis import sentiment_logic

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
for attempt in range(10):
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Koneksi Database (Postgres) sukses untuk Scheduler Modul 3.")
        break
    except Exception as e:
        logger.warning(f"Koneksi DB gagal (percobaan {attempt+1}/10), mencoba lagi... Error: {e}")
        time.sleep(5)

if engine is None:
    logger.error("Gagal total terhubung ke database. Scheduler berhenti.")
    exit(1)

def run_analysis_job():
    """
    Job utama:
    1. Ambil ulasan yang belum dianalisis dari DB.
    2. Jalankan analisis (Sentiment, Aspect, Priority).
    3. Simpan hasilnya kembali ke DB.
    """
    logger.info("Scheduler: Memulai job analisis ulasan...")

    # Validasi engine tersedia
    if engine is None:
        logger.error("Scheduler: Koneksi database tidak tersedia. Job dibatalkan.")
        return

    # 1. Ambil data yang 'sentiment' nya masih NULL
    try:
        query = "SELECT review_id, review_text FROM reviews WHERE sentiment IS NULL"
        df = pd.read_sql(query, engine)
    except Exception as e:
        logger.error(f"Gagal mengambil data dari tabel 'reviews': {e}")
        return

    if df.empty:
        logger.info("Scheduler: Tidak ada ulasan baru untuk dianalisis.")
        return

    logger.info(f"Scheduler: Ditemukan {len(df)} ulasan baru.")
    
    results = []
    for index, row in df.iterrows():
        review_text = row['review_text']  # RENAMED: was 'text'
        
        try:
            # 2. Jalankan Analisis
            sentiment, score = sentiment_logic.analyze_review_sentiment(review_text)
            aspect = sentiment_logic.detect_aspect(review_text)
            priority = sentiment_logic.classify_priority(sentiment, aspect)
            
            results.append({
                "review_id": row['review_id'],
                "sentiment": sentiment,
                "aspect": aspect,
                "priority": priority
            })
            logger.info(f"Analyzed review_id {row['review_id']}: {sentiment}, {aspect}, {priority}")
        except Exception as e:
            logger.error(f"Gagal menganalisis review_id {row['review_id']}: {e}")
            continue

    if not results:
        logger.warning("Tidak ada hasil analisis yang berhasil.")
        return

    # 3. Simpan hasil ke DB (Update)
    try:
        # PERBAIKAN: Gunakan engine.connect() dengan context manager
        with engine.connect() as conn:
            # Gunakan transaction
            with conn.begin():
                for res in results:
                    conn.execute(
                        text(
                            "UPDATE reviews SET sentiment = :sentiment, aspect = :aspect, "
                            "priority = :priority WHERE review_id = :review_id"
                        ),
                        res
                    )
        logger.info(f"Scheduler: {len(results)} ulasan berhasil dianalisis dan disimpan.")
    except Exception as e:
        logger.error(f"Scheduler: Gagal menyimpan hasil analisis ke DB: {e}", exc_info=True)


# --- Setup Scheduler ---
scheduler = BlockingScheduler()

# Jalankan 10 detik setelah startup untuk data dummy
scheduler.add_job(
    run_analysis_job, 
    'date', 
    run_date=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() + 10))
)

# Jalankan setiap 1 jam untuk data baru
scheduler.add_job(run_analysis_job, 'interval', hours=1)

if __name__ == "__main__":
    logger.info("Scheduler Analisis Sentimen dimulai...")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler dihentikan.")
    except Exception as e:
        logger.error(f"Error saat menjalankan scheduler: {e}", exc_info=True)