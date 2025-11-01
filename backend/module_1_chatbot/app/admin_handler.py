# app/admin_handler.py - Updated dengan Email Notification
from fastapi import APIRouter, Request, Form, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import Optional
import secrets
import os
import logging
from .database import (
    get_pending_messages, 
    get_resolved_messages,
    get_message_by_id,
    update_message_status,
    get_stats
)
from .whatsapp_handler import send_whatsapp_message
from .email_notification import send_admin_reply_notification

logger = logging.getLogger(__name__)
router = APIRouter()
templates = Jinja2Templates(directory="templates")
security = HTTPBasic()

# Admin credentials dari .env
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

def verify_admin(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    """Verify admin credentials menggunakan HTTP Basic Auth"""
    correct_username = secrets.compare_digest(credentials.username, ADMIN_USERNAME)
    correct_password = secrets.compare_digest(credentials.password, ADMIN_PASSWORD)
    
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

@router.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard(
    request: Request, 
    admin: str = Depends(verify_admin)
):
    """Dashboard admin - lihat semua pending messages dari web & WA"""
    try:
        pending = get_pending_messages()
        resolved = get_resolved_messages(limit=20)
        stats = get_stats()
        
        return templates.TemplateResponse("admin_dashboard.html", {
            "request": request,
            "admin_name": admin,
            "pending_messages": pending,
            "resolved_messages": resolved,
            "stats": stats
        })
    except Exception as e:
        logger.error(f"Error loading admin dashboard: {e}", exc_info=True)
        return HTMLResponse(
            content=f"<h1>Error loading dashboard</h1><p>{str(e)}</p>",
            status_code=500
        )

@router.post("/admin/reply")
async def admin_reply(
    message_id: int = Form(...),
    reply_text: str = Form(...),
    admin: str = Depends(verify_admin)
):
    """Admin reply ke user (otomatis ke channel yang sesuai + email)"""
    try:
        # Find message
        message = get_message_by_id(message_id)
        if not message:
            raise HTTPException(status_code=404, detail="Message not found")
        
        # Update status di database
        success_db = update_message_status(message_id, reply_text, admin)
        if not success_db:
            raise HTTPException(status_code=500, detail="Failed to update message status")
        
        # Send ke user berdasarkan channel
        success_send = True
        error_msg = None
        
        if message["channel"] == "whatsapp":
            # Kirim via WhatsApp
            phone = message["user_id"]
            wa_message = f"*Balasan dari Customer Service:*\n\n{reply_text}"
            success_send = send_whatsapp_message(phone, wa_message)
            if not success_send:
                error_msg = "Failed to send WhatsApp message"
        
        else:  # web
            # Kirim via Email
            user_email = message["user_contact"]
            if user_email and "@" in user_email:
                try:
                    email_sent = send_admin_reply_notification(
                        user_email=user_email,
                        user_name=None,  # Could extract from message if stored
                        original_message=message["user_message"],
                        admin_reply=reply_text,
                        message_id=message_id
                    )
                    if not email_sent:
                        error_msg = "Failed to send email notification"
                        success_send = False
                except Exception as e:
                    logger.error(f"Error sending email: {e}")
                    error_msg = f"Email error: {str(e)}"
                    success_send = False
            else:
                logger.warning(f"No valid email for web user {message['user_id']}")
                error_msg = "No valid email address for user"
                success_send = False
        
        # Return response
        if success_send:
            logger.info(f"✅ Admin {admin} replied to message #{message_id}")
            return {
                "status": "success",
                "message": f"Reply sent via {message['channel']}",
                "message_id": message_id
            }
        else:
            logger.error(f"Failed to send reply via {message['channel']}: {error_msg}")
            return {
                "status": "partial_success",
                "message": f"Reply saved but failed to send: {error_msg}",
                "message_id": message_id
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in admin reply: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/admin/message/{message_id}", response_class=HTMLResponse)
async def view_message_detail(
    request: Request,
    message_id: int,
    admin: str = Depends(verify_admin)
):
    """View detail message untuk admin"""
    message = get_message_by_id(message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    return templates.TemplateResponse("message_detail.html", {
        "request": request,
        "message": message,
        "admin_name": admin
    })

@router.get("/admin/stats")
async def get_admin_stats(admin: str = Depends(verify_admin)):
    """Get statistics untuk monitoring"""
    return get_stats()

@router.post("/admin/bulk-action")
async def bulk_action(
    action: str = Form(...),
    message_ids: str = Form(...),  # Comma-separated IDs
    admin: str = Depends(verify_admin)
):
    """Bulk action untuk multiple messages"""
    try:
        ids = [int(id.strip()) for id in message_ids.split(",") if id.strip()]
        
        if action == "mark_resolved":
            for msg_id in ids:
                update_message_status(msg_id, "[Marked as resolved by admin]", admin)
            return {"status": "success", "action": action, "count": len(ids)}
        
        # Tambahkan action lain jika diperlukan
        return {"status": "unknown_action", "action": action}
        
    except Exception as e:
        logger.error(f"Bulk action error: {e}")
        raise HTTPException(status_code=500, detail=str(e))