from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.dependencies.auth import get_current_admin
from app.models.contact_message import ContactMessage
from app.schemas.contact import ContactCreate, ContactResponse, ContactStatusUpdate
from app.schemas.auth import AdminProfile

router = APIRouter(prefix="/contact", tags=["Contact Messages"])


@router.post("", status_code=status.HTTP_201_CREATED)
def submit_contact_form(
    contact_in: ContactCreate,
    db: Session = Depends(get_db),
):
    """
    Public: Submit a message via the portfolio contact form.
    Persists directly into Neon PostgreSQL (Zero SMTP / Zero external mail dependency).
    """
    full_message = contact_in.message.strip()
    if contact_in.subject and contact_in.subject.strip():
        full_message = f"Subject: {contact_in.subject.strip()}\n\n{full_message}"

    message = ContactMessage(
        name=contact_in.name.strip(),
        email=contact_in.email.strip().lower(),
        message=full_message,
        is_read=False,
    )
    db.add(message)
    db.commit()
    db.refresh(message)

    return {
        "status": "success",
        "message": "Thank you! Your message has been received and stored securely.",
        "id": message.id,
    }


@router.get("/messages", response_model=List[ContactResponse])
def get_all_messages(
    unread_only: bool = False,
    db: Session = Depends(get_db),
    _: AdminProfile = Depends(get_current_admin),
):
    """Admin: View all submitted contact messages, latest first."""
    query = db.query(ContactMessage)
    if unread_only:
        query = query.filter(ContactMessage.is_read.is_(False))

    messages = query.order_by(ContactMessage.created_at.desc()).all()
    return messages


@router.patch("/messages/{message_id}/read", response_model=ContactResponse)
def toggle_message_read_status(
    message_id: int,
    status_in: Optional[ContactStatusUpdate] = None,
    db: Session = Depends(get_db),
    _: AdminProfile = Depends(get_current_admin),
):
    """Admin: Mark a message as read or unread."""
    message = db.query(ContactMessage).filter(ContactMessage.id == message_id).first()
    if not message:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found.")

    if status_in is not None:
        message.is_read = status_in.is_read
    else:
        message.is_read = not message.is_read

    db.commit()
    db.refresh(message)
    return message


@router.delete("/messages/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_message(
    message_id: int,
    db: Session = Depends(get_db),
    _: AdminProfile = Depends(get_current_admin),
):
    """Admin: Permanently delete a contact message from the database."""
    message = db.query(ContactMessage).filter(ContactMessage.id == message_id).first()
    if not message:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found.")

    db.delete(message)
    db.commit()
    return None
