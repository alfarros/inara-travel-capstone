# app/email_notification.py - VERSI PERBAIKAN
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Email configuration dari .env
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", SMTP_USER)
FROM_NAME = os.getenv("FROM_NAME", "Travel Haji & Umrah")

def send_email(
    to_email: str,
    subject: str,
    body_html: str,
    body_text: Optional[str] = None
) -> bool:
    """
    Kirim email menggunakan SMTP
    
    Args:
        to_email: Email tujuan
        subject: Subject email
        body_html: Konten email dalam HTML
        body_text: Konten email dalam plain text (fallback)
    
    Returns:
        bool: True jika berhasil, False jika gagal
    """
    if not SMTP_USER or not SMTP_PASSWORD:
        logger.warning("SMTP credentials not configured. Email not sent.")
        return False
    
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = f"{FROM_NAME} <{FROM_EMAIL}>"
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Attach plain text version
        if body_text:
            part_text = MIMEText(body_text, 'plain', 'utf-8')
            msg.attach(part_text)
        
        # Attach HTML version
        part_html = MIMEText(body_html, 'html', 'utf-8')
        msg.attach(part_html)
        
        # Send email
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        
        logger.info(f"✅ Email sent to {to_email}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to send email to {to_email}: {e}")
        return False

def send_admin_reply_notification(
    user_email: str,
    user_name: Optional[str],
    original_message: str,
    admin_reply: str,
    message_id: int
) -> bool:
    """
    Kirim notifikasi ke user bahwa admin sudah reply
    """
    subject = "Balasan dari Customer Service - Travel Haji & Umrah"
    
    # --- PERBAIKAN: Pindahkan logic .replace() ke luar f-string ---
    admin_reply_html = admin_reply.replace('\n', '<br>')
    # -------------------------------------------------------------
    
    # HTML body
    body_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: #2c5f2d; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0; }}
            .content {{ background: #f9f9f9; padding: 20px; border: 1px solid #ddd; }}
            .message-box {{ background: white; padding: 15px; margin: 15px 0; border-left: 4px solid #2c5f2d; }}
            .reply-box {{ background: #e8f5e9; padding: 15px; margin: 15px 0; border-left: 4px solid #4caf50; }}
            .footer {{ background: #f1f1f1; padding: 15px; text-align: center; font-size: 12px; color: #666; border-radius: 0 0 5px 5px; }}
            .button {{ display: inline-block; padding: 12px 24px; background: #2c5f2d; color: white; text-decoration: none; border-radius: 5px; margin: 10px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>🕌 Travel Haji & Umrah</h2>
                <p>Balasan dari Customer Service Kami</p>
            </div>
            
            <div class="content">
                <p>Halo {"<strong>" + user_name + "</strong>" if user_name else "Customer"},</p>
                
                <p>Tim Customer Service kami telah merespons pertanyaan Anda:</p>
                
                <div class="message-box">
                    <strong>Pertanyaan Anda:</strong><br>
                    {original_message}
                </div>
                
                <div class="reply-box">
                    <strong>💬 Balasan dari Customer Service:</strong><br>
                    {admin_reply_html}
                </div>
                
                <p>Jika Anda memiliki pertanyaan lebih lanjut, silakan reply email ini atau kunjungi website kami.</p>
                
                <center>
                    <a href="http://localhost:8008" class="button">Kunjungi Website Kami</a>
                </center>
            </div>
            
            <div class="footer">
                <p><strong>Travel Haji & Umrah</strong></p>
                <p>📞 WhatsApp: +62 896-3209-0214 | 📧 Email: {FROM_EMAIL}</p>
                <p style="font-size: 11px; color: #999;">
                    Email ini dikirim otomatis, mohon tidak membalas ke email ini.<br>
                    Untuk pertanyaan lebih lanjut, silakan hubungi customer service kami.
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Plain text fallback
    body_text = f"""
    Travel Haji & Umrah - Balasan dari Customer Service
    
    Halo {user_name if user_name else 'Customer'},
    
    Tim Customer Service kami telah merespons pertanyaan Anda:
    
    PERTANYAAN ANDA:
    {original_message}
    
    BALASAN DARI CUSTOMER SERVICE:
    {admin_reply}
    
    Jika Anda memiliki pertanyaan lebih lanjut, silakan hubungi kami.
    
    WhatsApp: +62 896-3209-0214
    Email: {FROM_EMAIL}
    Website: http://localhost:8008
    
    ---
    Travel Haji & Umrah
    Email otomatis - Mohon tidak membalas email ini
    """
    
    return send_email(user_email, subject, body_html, body_text)

def send_escalation_notification(
    user_email: str,
    user_name: Optional[str],
    message: str,
    estimated_response_time: str = "1-2 jam"
) -> bool:
    """
    Kirim notifikasi ke user bahwa pesannya telah di-escalate
    """
    subject = "Pesan Anda Sedang Ditangani - Travel Haji & Umrah"
    
    body_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: #2c5f2d; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0; }}
            .content {{ background: #f9f9f9; padding: 20px; border: 1px solid #ddd; }}
            .notice-box {{ background: #fff3cd; padding: 15px; margin: 15px 0; border-left: 4px solid #ffc107; }}
            .footer {{ background: #f1f1f1; padding: 15px; text-align: center; font-size: 12px; color: #666; border-radius: 0 0 5px 5px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>🕌 Travel Haji & Umrah</h2>
                <p>Konfirmasi Penerimaan Pesan</p>
            </div>
            
            <div class="content">
                <p>Halo {"<strong>" + user_name + "</strong>" if user_name else "Customer"},</p>
                
                <div class="notice-box">
                    <strong>⚠️ Pesan Anda Sedang Ditangani</strong><br><br>
                    Tim Customer Service kami telah menerima pertanyaan Anda dan sedang memproses permintaan Anda dengan prioritas tinggi.
                </div>
                
                <p><strong>Pesan Anda:</strong><br>
                {message}</p>
                
                <p><strong>Estimasi Waktu Respons:</strong> {estimated_response_time}</p>
                
                <p>Kami akan mengirimkan balasan melalui email ini secepatnya. Terima kasih atas kesabaran Anda.</p>
            </div>
            
            <div class="footer">
                <p><strong>Travel Haji & Umrah</strong></p>
                <p>📞 WhatsApp: +62 896-3209-0214 | 📧 Email: {FROM_EMAIL}</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    body_text = f"""
    Travel Haji & Umrah - Konfirmasi Penerimaan Pesan
    
    Halo {user_name if user_name else 'Customer'},
    
    ⚠️ PESAN ANDA SEDANG DITANGANI
    
    Tim Customer Service kami telah menerima pertanyaan Anda:
    {message}
    
    Estimasi Waktu Respons: {estimated_response_time}
    
    Kami akan mengirimkan balasan secepatnya.
    
    ---
    Travel Haji & Umrah
    WhatsApp: +62 896-3209-0214
    Email: {FROM_EMAIL}
    """
    
    return send_email(user_email, subject, body_html, body_text)

def send_welcome_email(user_email: str, user_name: Optional[str]) -> bool:
    """Kirim welcome email untuk user baru"""
    subject = "Selamat Datang di Travel Haji & Umrah"
    
    body_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: #2c5f2d; color: white; padding: 30px; text-align: center; border-radius: 5px 5px 0 0; }}
            .content {{ background: #f9f9f9; padding: 20px; border: 1px solid #ddd; }}
            .footer {{ background: #f1f1f1; padding: 15px; text-align: center; font-size: 12px; color: #666; border-radius: 0 0 5px 5px; }}
            .button {{ display: inline-block; padding: 12px 24px; background: #2c5f2d; color: white; text-decoration: none; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🕌 Selamat Datang!</h1>
                <p>Travel Haji & Umrah</p>
            </div>
            
            <div class="content">
                <p>Assalamu'alaikum {"<strong>" + user_name + "</strong>" if user_name else "Customer"},</p>
                
                <p>Terima kasih telah menghubungi kami! Kami siap membantu Anda dalam perencanaan ibadah Haji dan Umrah Anda.</p>
                
                <p><strong>Layanan Kami:</strong></p>
                <ul>
                    <li>🕋 Paket Haji & Umrah Terpercaya</li>
                    <li>✈️ Wisata Religi Internasional</li>
                    <li>📞 Customer Service 24/7</li>
                    <li>🎯 Konsultasi Gratis</li>
                </ul>
                
                <center>
                    <a href="http://localhost:8008" class="button">Mulai Chat Dengan Kami</a>
                </center>
            </div>
            
            <div class="footer">
                <p><strong>Travel Haji & Umrah</strong></p>
                <p>📞 WhatsApp: +62 896-3209-0214 | 📧 Email: {FROM_EMAIL}</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    body_text = f"""
    Selamat Datang di Travel Haji & Umrah
    
    Assalamu'alaikum {user_name if user_name else 'Customer'},
    
    Terima kasih telah menghubungi kami! Kami siap membantu Anda dalam perencanaan ibadah Haji dan Umrah.
    
    LAYANAN KAMI:
    - Paket Haji & Umrah Terpercaya
    - Wisata Religi Internasional
    - Customer Service 24/7
    - Konsultasi Gratis
    
    Kunjungi: http://localhost:8008
    WhatsApp: +62 896-3209-0214
    
    ---
    Travel Haji & Umrah
    """
    
    return send_email(user_email, subject, body_html, body_text)