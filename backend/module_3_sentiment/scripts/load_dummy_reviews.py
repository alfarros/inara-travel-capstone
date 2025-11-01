# /module_3_sentiment/scripts/load_dummy_reviews.py
import pandas as pd
from sqlalchemy import create_engine, text
import os
import time

DB_USER = os.getenv("POSTGRES_USER", "admin")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "adminpass")
DB_NAME = os.getenv("POSTGRES_DB", "haji_umrah_db")
DB_HOST = "postgres-db" # Nama service dari docker-compose

# Coba koneksi
engine = None
for _ in range(5):
    try:
        DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:5432/{DB_NAME}"
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("Koneksi Database (Postgres) sukses untuk Modul 3.")
        break
    except Exception as e:
        print(f"Koneksi DB gagal, mencoba lagi... Error: {e}")
        time.sleep(3)

if engine is None:
    print("Gagal terhubung ke database. Abborting.")
    exit(1)

def create_table_and_load_data():
    """
    Buat tabel 'reviews' jika belum ada dan isi dengan data dummy.
    """
    table_name = "reviews"
    csv_path = "/dummy_data/reviews.csv"
    
    try:
        df = pd.read_csv(csv_path)
        # Tambahkan kolom untuk hasil analisis
        df['sentiment'] = None
        df['aspect'] = None
        df['priority'] = None
        
        # Buat tabel (atau ganti jika sudah ada)
        df.to_sql(table_name, engine, if_exists='replace', index=False)
        print(f"Tabel '{table_name}' berhasil dibuat dan data dummy dimuat.")
        
    except FileNotFoundError:
        print(f"ERROR: File '{csv_path}' tidak ditemukan.")
    except Exception as e:
        print(f"Error saat memuat data: {e}")

if __name__ == "__main__":
    create_table_and_load_data()