from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.dependencies.auth import get_current_admin
from app.models.category import Category
from app.models.project import Project
from app.models.contact_message import ContactMessage
from app.models.notification import Notification
from app.schemas.auth import AdminProfile

router = APIRouter(prefix="/dashboard", tags=["Admin Dashboard"])


@router.get("/stats")
def get_dashboard_stats(
    db: Session = Depends(get_db),
    _: AdminProfile = Depends(get_current_admin),
):
    """Admin: Return overview counts and latest activity for dashboard home."""
    total_projects = db.query(Project).count()
    total_categories = db.query(Category).count()
    total_messages = db.query(ContactMessage).count()
    unread_messages = db.query(ContactMessage).filter(ContactMessage.is_read.is_(False)).count()
    total_notifications = db.query(Notification).count()
    active_notifications = db.query(Notification).filter(Notification.is_active.is_(True)).count()

    latest_messages = (
        db.query(ContactMessage)
        .order_by(ContactMessage.created_at.desc())
        .limit(5)
        .all()
    )

    return {
        "total_projects": total_projects,
        "total_categories": total_categories,
        "total_messages": total_messages,
        "unread_messages": unread_messages,
        "total_notifications": total_notifications,
        "active_notifications": active_notifications,
        "latest_messages": [
            {
                "id": m.id,
                "name": m.name,
                "email": m.email,
                "message": m.message[:80] + ("..." if len(m.message) > 80 else ""),
                "is_read": m.is_read,
                "created_at": m.created_at,
            }
            for m in latest_messages
        ],
    }
