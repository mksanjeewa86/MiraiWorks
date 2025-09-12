from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_active_user
from app.models.company import Company
from app.models.interview import Interview
from app.models.message import Conversation
from app.models.resume import Resume
from app.models.user import User
from app.schemas.dashboard import ActivityItem, DashboardStats

router = APIRouter()


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get dashboard statistics."""
    # Get total counts
    total_users_result = await db.execute(
        select(func.count(User.id)).where(User.is_active == True)
    )
    total_users = total_users_result.scalar() or 0

    total_companies_result = await db.execute(
        select(func.count(Company.id)).where(Company.is_active == True)
    )
    total_companies = total_companies_result.scalar() or 0

    total_interviews_result = await db.execute(select(func.count(Interview.id)))
    total_interviews = total_interviews_result.scalar() or 0

    total_resumes_result = await db.execute(select(func.count(Resume.id)))
    total_resumes = total_resumes_result.scalar() or 0

    # Active conversations (conversations with messages in last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    active_conversations_result = await db.execute(
        select(func.count(Conversation.id.distinct())).where(
            Conversation.updated_at >= thirty_days_ago
        )
    )
    active_conversations = active_conversations_result.scalar() or 0

    return DashboardStats(
        total_users=total_users,
        total_companies=total_companies,
        total_interviews=total_interviews,
        total_resumes=total_resumes,
        active_conversations=active_conversations,
    )


@router.get("/activity", response_model=list[ActivityItem])
async def get_recent_activity(
    limit: int = Query(default=20, le=100),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get recent activity items."""
    # For now, return some mock activity items
    # In a real implementation, you'd query various tables for recent activities

    recent_activities = []

    # Get recent users (last 7 days)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recent_users_result = await db.execute(
        select(User)
        .where(User.created_at >= seven_days_ago, User.is_active == True)
        .order_by(User.created_at.desc())
        .limit(limit // 2)
    )
    recent_users = recent_users_result.scalars().all()

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

    # Get recent interviews (last 7 days)
    recent_interviews_result = await db.execute(
        select(Interview)
        .where(Interview.created_at >= seven_days_ago)
        .order_by(Interview.created_at.desc())
        .limit(limit // 2)
    )
    recent_interviews = recent_interviews_result.scalars().all()

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
