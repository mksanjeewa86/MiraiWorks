from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.endpoints import API_ROUTES
from app.crud.dashboard import dashboard
from app.database import get_db
from app.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.dashboard import ActivityItem, DashboardStats

router = APIRouter()


@router.get(API_ROUTES.DASHBOARD.STATS, response_model=DashboardStats)
async def get_dashboard_stats(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get dashboard statistics."""
    stats = await dashboard.get_stats(db)
    return DashboardStats(**stats)


@router.get(API_ROUTES.DASHBOARD.ACTIVITY, response_model=list[ActivityItem])
async def get_recent_activity(
    limit: int = Query(default=20, le=100),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get recent activity items."""
    recent_activities = []

    # Get recent users, interviews, and exam sessions
    items_per_type = limit // 3
    recent_users = await dashboard.get_recent_users(db, items_per_type)
    recent_interviews = await dashboard.get_recent_interviews(db, items_per_type)
    recent_exam_sessions = await dashboard.get_recent_exam_sessions(db, items_per_type)

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
                description=f"Interview scheduled for {interview.scheduled_start.strftime('%Y-%m-%d %H:%M') if interview.scheduled_start else 'TBD'}",
                timestamp=interview.created_at,
                user_id=interview.candidate_id,
                metadata={
                    "interview_id": interview.id,
                    "interview_status": interview.status,
                },
            )
        )

    # Convert exam sessions to activity items
    for session in recent_exam_sessions:
        status_label = session.status.replace("_", " ").title()
        description = f"Exam {status_label}"
        if session.status == "completed" and session.score is not None:
            description += f" - Score: {session.score:.1f}%"

        recent_activities.append(
            ActivityItem(
                id=f"exam_session_{session.id}",
                type="exam",
                title="Exam Activity",
                description=description,
                timestamp=session.created_at,
                user_id=session.candidate_id,
                metadata={
                    "session_id": session.id,
                    "exam_id": session.exam_id,
                    "status": session.status,
                    "score": session.score,
                },
            )
        )

    # Sort by timestamp descending and limit
    recent_activities.sort(key=lambda x: x.timestamp, reverse=True)
    return recent_activities[:limit]
