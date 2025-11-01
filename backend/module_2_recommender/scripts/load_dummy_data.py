# /module_2_recommender/scripts/load_dummy_data.py
import pandas as pd
from sqlalchemy import create_engine
import os
import time

# MENGAPA: Kita butuh data ini di Postgres agar API FastAPI
# bisa mengambil detail paket secara real-time.

# Gunakan variabel lingkungan dari docker-compose
DB_USER = os.getenv("POSTGRES_USER", "admin")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "adminpass")
DB_NAME = os.getenv("POSTGRES_DB", "haji_umrah_db")
DB_HOST = "postgres-db" # Nama service dari docker-compose

# Coba koneksi beberapa kali jika DB belum siap
engine = None
for _ in range(5):
    try:
        DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:5432/{DB_NAME}"
        engine = create_engine(DATABASE_URL)
        engine.connect()
        print("Koneksi Database (Postgres) sukses.")
        break
    except Exception as e:
        print(f"Koneksi DB gagal, mencoba lagi... Error: {e}")
        time.sleep(3)

if engine is None:
    print("Gagal terhubung ke database. Abborting.")
    exit(1)

def load_data(csv_path, table_name):
    try:
        # Lokasi /dummy_data/ adalah root di dalam container
        df = pd.read_csv(f"/dummy_data/{csv_path}")
        df.to_sql(table_name, engine, if_exists='replace', index=False)
        print(f"Data '{csv_path}' berhasil dimuat ke tabel '{table_name}'.")
    except FileNotFoundError:
        print(f"ERROR: File '{csv_path}' tidak ditemukan di /dummy_data/")
        print("Pastikan Anda sudah membuat folder /dummy_data di root proyek.")
    except Exception as e:
        print(f"Error saat memuat data: {e}")

if __name__ == "__main__":
    load_data("packages.csv", "packages")
    load_data("interactions.csv", "interactions")