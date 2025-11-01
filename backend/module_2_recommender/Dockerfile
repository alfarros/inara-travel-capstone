# /module_2_recommender/Dockerfile (VERSI BENAR)
FROM python:3.10-slim

WORKDIR /app

# --- BAGIAN PENTING UNTUK scikit-surprise ---
# Install build tools (gcc, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

# Update pip
RUN pip install --upgrade pip
# -------------------------------------------

# Install dependensi Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Salin folder app
COPY ./app /app/app

# Salin skrip (opsional)
COPY ./scripts /app/scripts

# Salin model yang sudah dilatih
COPY ./models_store /app/models_store

# Port FastAPI
EXPOSE 8000

# Command default untuk menjalankan API
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]