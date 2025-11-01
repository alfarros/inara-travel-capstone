# /module_payments/app/main.py - VERSI PERBAIKAN (FINAL)
from fastapi import FastAPI, Depends, HTTPException, Request
from sqlalchemy.orm import Session
import logging
from . import schemas, models
from .database import get_db, engine
from .models import User, Package, Booking, Base
from fastapi.middleware.cors import CORSMiddleware 
from datetime import datetime

# --- INI IMPORT YANG HILANG ---
from .midtrans_handler import create_midtrans_transaction, handle_midtrans_notification
# -------------------------------

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Buat tabel di DB jika belum ada
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API Pembayaran & Booking (Modul 7)",
    description="Menangani pembuatan booking dan transaksi Midtrans."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/create-transaction", response_model=schemas.CreateTransactionResponse)
def create_new_transaction(
    request: schemas.CreateTransactionRequest, 
    db: Session = Depends(get_db)
):
    """
    Endpoint utama untuk Frontend (React).
    Menerima detail pesanan, membuat booking di DB, dan memanggil Midtrans.
    """
    
    # 1. Validasi Data
    db_user = db.query(User).filter(User.email == request.customer.email).first()
    if not db_user:
        # Di skenario production, kita harusnya melempar error.
        # Untuk capstone, kita bisa buat user 'dummy' jika tidak ada.
        logger.warning(f"Customer email {request.customer.email} tidak ditemukan. Membuat user dummy.")
        db_user = User(
            email=request.customer.email,
            first_name=request.customer.first_name,
            last_name=request.customer.last_name,
            phone_number=request.customer.phone,
            hashed_password="DUMMY_PASSWORD_CHANGE_ME" # Tidak aman, hanya untuk tes
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

    # Validasi paket
    try:
        package_id_int = int(request.items[0].id)
    except (ValueError, IndexError, TypeError):
        raise HTTPException(status_code=422, detail="Item ID paket tidak valid.")

    db_package = db.query(Package).filter(Package.package_id == package_id_int).first()
    if not db_package:
        raise HTTPException(status_code=404, detail=f"Paket dengan ID {package_id_int} tidak ditemukan")

    # 2. Buat Transaksi di DB Anda
    # (Pindahkan order_id ke sini agar bisa disimpan di DB dulu)
    order_id = f"INARA-{db_package.package_id}-{db_user.user_id}-{int(datetime.now().timestamp())}"
    
    new_booking = Booking(
        user_id=db_user.user_id,
        package_id=db_package.package_id,
        order_id=order_id,
        total_amount=request.gross_amount,
        status="pending"
    )
    
    try:
        db.add(new_booking)
        db.commit()
        db.refresh(new_booking)
        logger.info(f"Booking {order_id} berhasil disimpan ke DB.")
    except Exception as e:
        db.rollback()
        logger.error(f"Gagal menyimpan booking ke DB: {e}")
        raise HTTPException(status_code=500, detail=f"Gagal menyimpan booking: {str(e)}")

    # 3. Panggil Midtrans Handler (Menggunakan fungsi dari midtrans_handler.py)
    transaction_response = create_midtrans_transaction(
        order_id=order_id,
        gross_amount=request.gross_amount,
        items=request.items,
        customer=request.customer
    )

    if not transaction_response:
        # Jika Midtrans gagal, booking di DB tetap ada (status 'pending')
        raise HTTPException(status_code=500, detail="Gagal membuat transaksi Midtrans")

    # 4. Simpan redirect_url ke DB Anda
    new_booking.midtrans_redirect_url = transaction_response.get("redirect_url")
    db.commit()

    return schemas.CreateTransactionResponse(
        order_id=order_id,
        transaction_token=transaction_response["transaction_token"],
        redirect_url=transaction_response["redirect_url"]
    )

@app.post("/webhook/midtrans")
async def midtrans_notification_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Endpoint untuk menerima notifikasi dari Midtrans (Webhook).
    """
    try:
        notification_payload = await request.json()
        logger.info(f"Menerima webhook Midtrans untuk Order ID: {notification_payload.get('order_id')}")

        # Panggil handler untuk validasi dan update DB
        # (Sekarang ini sudah ter-import dengan benar)
        success = handle_midtrans_notification(notification_payload, db)

        if success:
            return {"status": "ok"}
        else:
            raise HTTPException(status_code=403, detail="Signature key tidak valid atau update DB gagal.")

    except Exception as e:
        logger.error(f"Error pada Midtrans webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))