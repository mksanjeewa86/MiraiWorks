from datetime import datetime, timedelta
from typing import List

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import Company
from app.models.interview import Interview
from app.models.message import Conversation
from app.models.resume import Resume
from app.models.user import User


class CRUDDashboard:
    """Dashboard CRUD operations."""

    async def get_stats(self, db: AsyncSession) -> dict:
        """Get dashboard statistics."""
        # Get total counts in parallel
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

        return {
            "total_users": total_users,
            "total_companies": total_companies,
            "total_interviews": total_interviews,
            "total_resumes": total_resumes,
            "active_conversations": active_conversations,
        }

    async def get_recent_users(self, db: AsyncSession, limit: int = 10) -> List[User]:
        """Get recent users (last 7 days)."""
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        result = await db.execute(
            select(User)
            .where(User.created_at >= seven_days_ago, User.is_active == True)
            .order_by(User.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()

    async def get_recent_interviews(self, db: AsyncSession, limit: int = 10) -> List[Interview]:
        """Get recent interviews (last 7 days)."""
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        result = await db.execute(
            select(Interview)
            .where(Interview.created_at >= seven_days_ago)
            .order_by(Interview.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()

    async def get_recent_companies(self, db: AsyncSession, limit: int = 10) -> List[Company]:
        """Get recent companies (last 7 days)."""
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        result = await db.execute(
            select(Company)
            .where(Company.created_at >= seven_days_ago, Company.is_active == True)
            .order_by(Company.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()

    async def get_recent_resumes(self, db: AsyncSession, limit: int = 10) -> List[Resume]:
        """Get recent resumes (last 7 days)."""
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        result = await db.execute(
            select(Resume)
            .where(Resume.created_at >= seven_days_ago)
            .order_by(Resume.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()


# Create the CRUD instance
dashboard = CRUDDashboard()