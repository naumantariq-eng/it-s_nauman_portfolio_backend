from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.dependencies.auth import get_current_admin
from app.models.notification import Notification
from app.schemas.notification import (
    NotificationCreate,
    NotificationUpdate,
    NotificationResponse,
    NotificationStatusUpdate,
)
from app.schemas.auth import AdminProfile

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", response_model=List[NotificationResponse])
def get_active_notifications(db: Session = Depends(get_db)):
    """Public: Fetch active notifications for portfolio modal and navbar bell icon."""
    notifications = (
        db.query(Notification)
        .filter(Notification.is_active.is_(True))
        .order_by(Notification.created_at.desc())
        .all()
    )
    return notifications


@router.get("/all", response_model=List[NotificationResponse])
def get_all_notifications_admin(
    db: Session = Depends(get_db),
    _: AdminProfile = Depends(get_current_admin),
):
    """Admin: Fetch all notifications (both active and inactive)."""
    notifications = db.query(Notification).order_by(Notification.created_at.desc()).all()
    return notifications


@router.post("", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
def create_notification(
    notification_in: NotificationCreate,
    db: Session = Depends(get_db),
    _: AdminProfile = Depends(get_current_admin),
):
    """Admin: Create a new notification (Achievement, Project, Announcement, General)."""
    notification = Notification(
        title=notification_in.title.strip(),
        message=notification_in.message.strip(),
        type=notification_in.type.strip().lower(),
        is_active=notification_in.is_active,
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


@router.put("/{notification_id}", response_model=NotificationResponse)
def update_notification(
    notification_id: int,
    notification_in: NotificationUpdate,
    db: Session = Depends(get_db),
    _: AdminProfile = Depends(get_current_admin),
):
    """Admin: Update an existing notification's details."""
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found.")

    if notification_in.title is not None:
        notification.title = notification_in.title.strip()
    if notification_in.message is not None:
        notification.message = notification_in.message.strip()
    if notification_in.type is not None:
        notification.type = notification_in.type.strip().lower()
    if notification_in.is_active is not None:
        notification.is_active = notification_in.is_active

    db.commit()
    db.refresh(notification)
    return notification


@router.patch("/{notification_id}/status", response_model=NotificationResponse)
def toggle_notification_status(
    notification_id: int,
    status_in: NotificationStatusUpdate,
    db: Session = Depends(get_db),
    _: AdminProfile = Depends(get_current_admin),
):
    """Admin: Activate or deactivate a notification."""
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found.")

    notification.is_active = status_in.is_active
    db.commit()
    db.refresh(notification)
    return notification


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    _: AdminProfile = Depends(get_current_admin),
):
    """Admin: Permanently delete a notification."""
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found.")

    db.delete(notification)
    db.commit()
    return None
