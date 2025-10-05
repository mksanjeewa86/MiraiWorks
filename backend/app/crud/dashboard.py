from datetime import datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import Company
from app.models.exam import Exam, ExamAssignment, ExamSession
from app.models.interview import Interview
from app.models.message import Message
from app.models.resume import Resume
from app.models.user import User


class CRUDDashboard:
    """Dashboard CRUD operations."""

    async def get_stats(self, db: AsyncSession) -> dict:
        """Get dashboard statistics."""
        # Get total counts in parallel
        total_users_result = await db.execute(
            select(func.count(User.id)).where(User.is_active is True)
        )
        total_users = total_users_result.scalar() or 0

        total_companies_result = await db.execute(
            select(func.count(Company.id)).where(Company.is_active is True)
        )
        total_companies = total_companies_result.scalar() or 0

        total_interviews_result = await db.execute(select(func.count(Interview.id)))
        total_interviews = total_interviews_result.scalar() or 0

        total_resumes_result = await db.execute(select(func.count(Resume.id)))
        total_resumes = total_resumes_result.scalar() or 0

        # Active conversations (conversations with messages in last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        active_conversations_result = await db.execute(
            select(func.count(Message.id.distinct())).where(
                Message.created_at >= thirty_days_ago
            )
        )
        active_conversations = active_conversations_result.scalar() or 0

        # Exam statistics
        total_exams_result = await db.execute(select(func.count(Exam.id)))
        total_exams = total_exams_result.scalar() or 0

        total_exam_assignments_result = await db.execute(
            select(func.count(ExamAssignment.id))
        )
        total_exam_assignments = total_exam_assignments_result.scalar() or 0

        total_exam_sessions_result = await db.execute(
            select(func.count(ExamSession.id))
        )
        total_exam_sessions = total_exam_sessions_result.scalar() or 0

        completed_exam_sessions_result = await db.execute(
            select(func.count(ExamSession.id)).where(ExamSession.status == "completed")
        )
        completed_exam_sessions = completed_exam_sessions_result.scalar() or 0

        # Average exam score (for completed sessions with scores)
        avg_score_result = await db.execute(
            select(func.avg(ExamSession.final_score)).where(
                ExamSession.status == "completed",
                ExamSession.final_score.isnot(None),
            )
        )
        avg_exam_score = avg_score_result.scalar()

        return {
            "total_users": total_users,
            "total_companies": total_companies,
            "total_interviews": total_interviews,
            "total_resumes": total_resumes,
            "active_conversations": active_conversations,
            "total_exams": total_exams,
            "total_exam_assignments": total_exam_assignments,
            "total_exam_sessions": total_exam_sessions,
            "completed_exam_sessions": completed_exam_sessions,
            "avg_exam_score": round(avg_exam_score, 2) if avg_exam_score else None,
        }

    async def get_recent_users(self, db: AsyncSession, limit: int = 10) -> list[User]:
        """Get recent users (last 7 days)."""
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        result = await db.execute(
            select(User)
            .where(User.created_at >= seven_days_ago, User.is_active is True)
            .order_by(User.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()

    async def get_recent_interviews(
        self, db: AsyncSession, limit: int = 10
    ) -> list[Interview]:
        """Get recent interviews (last 7 days)."""
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        result = await db.execute(
            select(Interview)
            .where(Interview.created_at >= seven_days_ago)
            .order_by(Interview.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()

    async def get_recent_companies(
        self, db: AsyncSession, limit: int = 10
    ) -> list[Company]:
        """Get recent companies (last 7 days)."""
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        result = await db.execute(
            select(Company)
            .where(Company.created_at >= seven_days_ago, Company.is_active is True)
            .order_by(Company.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()

    async def get_recent_resumes(
        self, db: AsyncSession, limit: int = 10
    ) -> list[Resume]:
        """Get recent resumes (last 7 days)."""
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        result = await db.execute(
            select(Resume)
            .where(Resume.created_at >= seven_days_ago)
            .order_by(Resume.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()

    async def get_recent_exam_sessions(
        self, db: AsyncSession, limit: int = 10
    ) -> list[ExamSession]:
        """Get recent exam sessions (last 7 days)."""
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        result = await db.execute(
            select(ExamSession)
            .where(ExamSession.created_at >= seven_days_ago)
            .order_by(ExamSession.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()


# Create the CRUD instance
dashboard = CRUDDashboard()
