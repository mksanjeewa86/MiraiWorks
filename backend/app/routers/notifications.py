from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_active_user
from app.models.user import User
from app.services.notification_service import notification_service

router = APIRouter()


@router.get("/")
async def get_notifications(
    limit: int = Query(50, ge=1, le=100),
    unread_only: bool = Query(False),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get user's notifications."""
    notifications = await notification_service.get_user_notifications(
        db, current_user.id, limit, unread_only
    )
    
    return {
        "notifications": [
            {
                "id": n.id,
                "type": n.type,
                "title": n.title,
                "message": n.message,
                "payload": n.payload,
                "is_read": n.is_read,
                "created_at": n.created_at,
                "read_at": n.read_at,
            }
            for n in notifications
        ]
    }


@router.get("/unread-count")
async def get_unread_count(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get count of unread notifications."""
    count = await notification_service.get_unread_count(db, current_user.id)
    return {"unread_count": count}


@router.put("/mark-read")
async def mark_notifications_read(
    notification_ids: List[int],
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark notifications as read."""
    count = await notification_service.mark_notifications_as_read(
        db, current_user.id, notification_ids
    )
    
    return {"message": f"Marked {count} notifications as read"}


@router.put("/mark-all-read")
async def mark_all_notifications_read(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark all notifications as read."""
    # Get all unread notification IDs
    notifications = await notification_service.get_user_notifications(
        db, current_user.id, limit=1000, unread_only=True
    )
    
    notification_ids = [n.id for n in notifications]
    
    if notification_ids:
        count = await notification_service.mark_notifications_as_read(
            db, current_user.id, notification_ids
        )
        return {"message": f"Marked {count} notifications as read"}
    else:
        return {"message": "No unread notifications"}