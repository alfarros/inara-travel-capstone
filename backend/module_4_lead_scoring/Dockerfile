# /module_4_lead_scoring/Dockerfile
FROM python:3.10-slim

WORKDIR /app

# --- TAMBAHKAN BAGIAN INI ---
# Install build tools (gcc, etc.) yang dibutuhkan scikit-surprise
RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*
    
RUN pip install --upgrade pip
# Install dependensi
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Salin folder app
COPY ./app /app/app

# Salin skrip (opsional)
COPY ./scripts /app/scripts

# Salin model yang sudah dilatih
COPY ./model_store /app/model_store

# Port FastAPI
EXPOSE 8001

# Command default untuk menjalankan API
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]