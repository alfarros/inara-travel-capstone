# /module_payments/app/midtrans_handler.py
import os
import midtransclient
from dotenv import load_dotenv
import logging
from sqlalchemy.orm import Session
from sqlalchemy import text # Untuk contoh update DB
import json
logger = logging.getLogger(__name__)

# Load konfigurasi Midtrans
load_dotenv(dotenv_path='.env.payments')
MIDTRANS_SERVER_KEY = os.getenv("MIDTRANS_SERVER_KEY")
MIDTRANS_IS_PRODUCTION = os.getenv("MIDTRANS_IS_PRODUCTION", "false").lower() == "true"

# --- Inisialisasi Midtrans Client (Snap) ---
# MENGAPA Snap? Paling mudah diintegrasikan di frontend.
snap = None
if MIDTRANS_SERVER_KEY:
    snap = midtransclient.Snap(
        is_production=MIDTRANS_IS_PRODUCTION,
        server_key=MIDTRANS_SERVER_KEY
        # client_key tidak wajib di backend
    )
    logger.info(f"Midtrans Snap Client initialized. Production Mode: {MIDTRANS_IS_PRODUCTION}")
else:
    logger.error("MIDTRANS_SERVER_KEY tidak ditemukan di environment variables!")

def create_midtrans_transaction(order_id: str, gross_amount: int, items: list, customer: dict) -> dict | None:
    """
    Membuat transaksi di Midtrans dan mengembalikan token.
    """
    if not snap:
        logger.error("Midtrans client belum diinisialisasi.")
        return None

    # Siapkan parameter transaksi
    # MENGAPA order_id unik? Agar tidak bentrok saat notifikasi.
    transaction_details = {
        'order_id': order_id,
        'gross_amount': gross_amount
    }

    # Ubah format item sesuai spesifikasi Midtrans
    item_details_midtrans = [item.dict() for item in items]

    # Ubah format customer
    customer_details_midtrans = customer.dict()

    # Buat request payload lengkap
    payload = {
        "transaction_details": transaction_details,
        "item_details": item_details_midtrans,
        "customer_details": customer_details_midtrans,
        # Tambahan: Callback URL (opsional jika frontend handle)
        # "callbacks": {
        #     "finish": "https://tokokita.com/finish"
        # }
    }

    try:
        logger.info(f"Membuat transaksi Midtrans untuk Order ID: {order_id}...")
        transaction = snap.create_transaction(payload)
        logger.info(f"Transaksi Midtrans berhasil dibuat. Token: {transaction.get('token')}")
        # Kembalikan token dan redirect_url
        return {
            "transaction_token": transaction.get('token'),
            "redirect_url": transaction.get('redirect_url')
        }
    except Exception as e:
        logger.error(f"Error saat membuat transaksi Midtrans: {e}", exc_info=True)
        # Cek jika error API (misal 401 karena Server Key salah)
        if hasattr(e, 'response') and e.response:
             logger.error(f"Midtrans API Response: {e.response.status_code} - {e.response.text}")
        return None

def handle_midtrans_notification(notification_payload: dict, db: Session) -> bool:
    """
    Memproses notifikasi dari Midtrans (webhook).
    """
    if not snap or not MIDTRANS_SERVER_KEY: # Butuh Server Key untuk validasi
        logger.error("Midtrans client/server key belum siap untuk validasi notifikasi.")
        return False # Kembalikan False agar API return error

    try:
        # --- VALIDASI SIGNATURE (SANGAT PENTING!) ---
        # MENGAPA? Untuk memastikan notifikasi benar-benar dari Midtrans.
        # Library midtransclient TIDAK punya fungsi validasi langsung.
        # Kita harus hitung hash SHA512 manual.
        order_id = notification_payload.get('order_id')
        status_code = notification_payload.get('status_code')
        gross_amount = notification_payload.get('gross_amount')
        signature_key = notification_payload.get('signature_key')

        # String yang di-hash: order_id + status_code + gross_amount + server_key
        my_key_str = f"{order_id}{status_code}{gross_amount}{MIDTRANS_SERVER_KEY}"

        import hashlib
        my_signature_key = hashlib.sha512(my_key_str.encode()).hexdigest()

        if my_signature_key != signature_key:
            logger.error(f"VALIDASI GAGAL! Signature key tidak cocok untuk Order ID: {order_id}.")
            # JANGAN proses status jika validasi gagal
            return False # Kembalikan False -> API return 403 Forbidden
        # --- Akhir Validasi Signature ---

        logger.info(f"Notifikasi Midtrans DITERIMA & VALID untuk Order ID: {order_id}")

        transaction_status = notification_payload.get('transaction_status')
        fraud_status = notification_payload.get('fraud_status')
        payment_type = notification_payload.get('payment_type')

        logger.info(f"Status Transaksi: {transaction_status}, Fraud Status: {fraud_status}, Tipe: {payment_type}")

        # --- Logika Update Status Pesanan di Database Anda ---
        # Ini hanya CONTOH. Sesuaikan dengan tabel dan logika Anda.
        new_status = "pending" # Default

        if transaction_status == 'capture':
            if fraud_status == 'accept':
                new_status = 'paid'
        elif transaction_status == 'settlement':
            new_status = 'paid'
        elif transaction_status == 'cancel' or transaction_status == 'deny' or transaction_status == 'expire':
            new_status = 'failed'
        elif transaction_status == 'pending':
            new_status = 'pending'

        logger.info(f"Order ID {order_id}: Update status di DB menjadi '{new_status}'")

        try:
            # Ganti 'orders' dengan nama tabel Anda
            # Ganti 'order_status' dengan nama kolom status Anda
            update_query = text("""
                UPDATE orders SET order_status = :status, midtrans_payload = :payload
                WHERE order_id = :order_id
            """)
            result = db.execute(update_query, {
                "status": new_status,
                "payload": json.dumps(notification_payload), # Simpan payload asli
                "order_id": order_id
            })
            db.commit()

            # Cek apakah ada baris yang diupdate
            if result.rowcount > 0:
                 logger.info(f"Order ID {order_id}: Status berhasil diupdate di DB.")
            else:
                 logger.warning(f"Order ID {order_id} tidak ditemukan di database untuk diupdate.")
                 # Mungkin perlu logic tambahan di sini (misal: buat entry baru?)

        except Exception as db_err:
            logger.error(f"Gagal update status Order ID {order_id} di DB: {db_err}")
            db.rollback()
            return False # Kembalikan False jika gagal update DB -> API return 500

        return True # Kembalikan True jika sukses -> API return 200 OK

    except Exception as e:
        logger.error(f"Error memproses notifikasi Midtrans: {e}", exc_info=True)
        return False # Kembalikan False -> API return 500