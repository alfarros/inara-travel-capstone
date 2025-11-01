# Proyek Backend Platform Haji & Umrah

Repositori ini berisi seluruh backend, AI, dan layanan data untuk platform travel.

## Arsitektur

Arsitektur ini berbasis microservices yang diorkestrasi oleh Docker Compose. Layanan utama meliputi:
* `postgres-db`: Database utama (PostgreSQL).
* `redis-cache`: Cache latensi rendah (Redis).
* `rasa-server` & `rasa-action-server`: (Modul 1) Endpoint Chatbot AI.
* `recommender-api`: (Modul 2) API Sistem Rekomendasi Hybrid.
* `sentiment-dashboard` & `sentiment-scheduler`: (Modul 3) Dasbor dan scraper sentimen.
* `lead-scoring-api`: (Modul 4) API Skor Prospek Prediktif.
* `price-monitor-scheduler` & `price-monitor-dashboard`: (Modul 5) Scraper dan dasbor harga.
* `reporting-scheduler`: (Modul 6) Generator laporan otomatis.

## Setup Lingkungan Lokal

**Prasyarat:**
1.  **Docker**
2.  **Docker Compose**
3.  **Git**

**Langkah-langkah Menjalankan:**

1.  **Clone repositori:**
    ```bash
    git clone [URL_REPO_ANDA]
    cd haji_umrah_platform
    ```

2.  **Siapkan Model & Konfigurasi:**
    * **Modul 1 (Chatbot):** Latih model Rasa pertama Anda.
        ```bash
        cd module_1_chatbot
        # (Pastikan Docker berjalan)
        docker-compose run --rm rasa-server rasa train
        cd ..
        ```
    * **Modul 2, 3, 4:** Jalankan *notebook* pelatihan (`.ipynb`) di dalam direktori `notebooks/` masing-masing modul untuk menghasilkan file model (`.pkl`, `.bin`, `.json`) yang diperlukan di direktori `models_store/`.

3.  **Jalankan Seluruh Stack:**
    Dari direktori root (`/haji_umrah_platform`), jalankan:
    ```bash
    docker-compose up --build
    ```

4.  **Akses Layanan:**
    * **Postgres DB:** `localhost:5432`
    * **Redis:** `localhost:6379`
    * **Chatbot (Rasa API):** `http://localhost:5005`
    * **Recommender API (Docs):** `http://localhost:8000/docs`
    * **Lead Scoring API (Docs):** `http://localhost:8001/docs`
    * **Sentiment Dashboard:** `http://localhost:8501`
    * **Price Monitor Dashboard:** `http://localhost:8502`

## Panduan Troubleshooting

* **Error `permission denied` pada volume Docker:** Pastikan Docker memiliki izin untuk menulis ke direktori proyek.
* **Layanan API (FastAPI) gagal start:** Periksa `requirements.txt` di modul tersebut. Jalankan `docker-compose build --no-cache [nama_layanan]` untuk membangun ulang *image*.
* **Rasa gagal terhubung ke Action Server:** Pastikan `action_endpoint` di `endpoints.yml` menunjuk ke `http://rasa-action-server:5055/webhook`.
* **Model .pkl / .bin tidak ditemukan:** Pastikan Anda telah menjalankan *notebook* pelatihan dan file model tersimpan di direktori `models_store/` yang benar.