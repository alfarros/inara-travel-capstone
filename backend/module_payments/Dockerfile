# /module_payments/Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Update pip & Install dependensi
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Salin folder app
COPY ./app /app/app

# Salin file .env khusus pembayaran
COPY .env.payments .

# Port FastAPI (Pilih port unik, misal 8010)
EXPOSE 8010

# Command default
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8010"]