from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import dashboard as dashboard_crud
from app.database import get_db
from app.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.dashboard import ActivityItem, DashboardStats

router = APIRouter()


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get dashboard statistics."""
    stats = await dashboard_crud.get_stats(db)
    return DashboardStats(**stats)


@router.get("/activity", response_model=list[ActivityItem])
async def get_recent_activity(
    limit: int = Query(default=20, le=100),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get recent activity items."""
    recent_activities = []

    # Get recent users and interviews
    recent_users = await dashboard_crud.get_recent_users(db, limit // 2)
    recent_interviews = await dashboard_crud.get_recent_interviews(db, limit // 2)

    # Convert users to activity items
    for user in recent_users:
        recent_activities.append(
            ActivityItem(
                id=f"user_{user.id}",
                type="user",
                title="New User Registered",
                description=f"{user.full_name} joined the platform",
                timestamp=user.created_at,
                user_id=user.id,
                metadata={"user_email": user.email},
            )
        )

    # Convert interviews to activity items
    for interview in recent_interviews:
        recent_activities.append(
            ActivityItem(
                id=f"interview_{interview.id}",
                type="interview",
                title="Interview Scheduled",
                description=f"Interview scheduled for {interview.scheduled_at.strftime('%Y-%m-%d %H:%M')}",
                timestamp=interview.created_at,
                user_id=interview.candidate_id,
                metadata={
                    "interview_id": interview.id,
                    "interview_status": interview.status.value
                    if interview.status
                    else None,
                },
            )
        )

    # Sort by timestamp descending and limit
    recent_activities.sort(key=lambda x: x.timestamp, reverse=True)
    return recent_activities[:limit]
