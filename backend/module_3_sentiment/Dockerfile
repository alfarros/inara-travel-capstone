FROM python:3.10-slim

WORKDIR /app

# Install dependensi
COPY requirements.txt .

# --- PERBAIKAN ---
# Tambahkan 'sed' untuk membersihkan hash yang mungkin ada di cache
# Ini akan menjamin file requirements.txt bersih sebelum pip install
RUN sed -i 's/ --hash=.*//' requirements.txt && pip install --no-cache-dir -r requirements.txt

# Salin semua folder & file
COPY ./analysis /app/analysis
COPY ./scripts /app/scripts
COPY dashboard.py .
COPY scheduler.py .

# Port Streamlit
EXPOSE 8501

# Command default untuk menjalankan Streamlit
# Kita akan override ini di docker-compose untuk scheduler
CMD ["streamlit", "run", "dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]
