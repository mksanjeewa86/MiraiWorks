from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models.interview import Interview, InterviewProposal
from app.schemas.interview import InterviewCreate, InterviewUpdate
from app.utils.constants import InterviewStatus


class CRUDInterview(CRUDBase[Interview, InterviewCreate, InterviewUpdate]):
    """Interview CRUD operations."""

    async def get_with_relationships(self, db: AsyncSession, interview_id: int) -> Optional[Interview]:
        """Get interview with all relationships loaded."""
        result = await db.execute(
            select(Interview)
            .options(
                selectinload(Interview.candidate),
                selectinload(Interview.recruiter),
                selectinload(Interview.employer_company),
                selectinload(Interview.created_by_user),
                selectinload(Interview.proposals),
            )
            .where(Interview.id == interview_id)
        )
        return result.scalar_one_or_none()

    async def get_user_interviews(
        self,
        db: AsyncSession,
        user_id: int,
        status_filter: Optional[InterviewStatus] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Interview]:
        """Get interviews for a specific user."""
        query = (
            select(Interview)
            .options(
                selectinload(Interview.candidate),
                selectinload(Interview.recruiter),
                selectinload(Interview.employer_company),
                selectinload(Interview.created_by_user),
                selectinload(Interview.proposals),
            )
            .where(
                or_(
                    Interview.candidate_id == user_id,
                    Interview.recruiter_id == user_id,
                    Interview.created_by == user_id,
                )
            )
            .order_by(Interview.scheduled_start.desc())
        )

        if status_filter:
            query = query.where(Interview.status == status_filter)
        if start_date:
            query = query.where(Interview.scheduled_start >= start_date)
        if end_date:
            query = query.where(Interview.scheduled_start <= end_date)

        query = query.offset(offset).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    async def get_user_interviews_count(
        self,
        db: AsyncSession,
        user_id: int,
        status_filter: Optional[InterviewStatus] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> int:
        """Get count of interviews for a specific user."""
        query = select(func.count(Interview.id)).where(
            or_(
                Interview.candidate_id == user_id,
                Interview.recruiter_id == user_id,
                Interview.created_by == user_id,
            )
        )

        if status_filter:
            query = query.where(Interview.status == status_filter)
        if start_date:
            query = query.where(Interview.scheduled_start >= start_date)
        if end_date:
            query = query.where(Interview.scheduled_start <= end_date)

        result = await db.execute(query)
        return result.scalar() or 0

    async def get_upcoming_interviews(
        self, db: AsyncSession, user_id: int, limit: int = 10
    ) -> List[Interview]:
        """Get upcoming interviews for a user."""
        now = datetime.utcnow()
        result = await db.execute(
            select(Interview)
            .options(
                selectinload(Interview.candidate),
                selectinload(Interview.recruiter),
                selectinload(Interview.employer_company),
            )
            .where(
                or_(
                    Interview.candidate_id == user_id,
                    Interview.recruiter_id == user_id,
                    Interview.created_by == user_id,
                ),
                Interview.scheduled_start >= now,
                Interview.status.in_([InterviewStatus.SCHEDULED, InterviewStatus.CONFIRMED]),
            )
            .order_by(Interview.scheduled_start.asc())
            .limit(limit)
        )
        return result.scalars().all()

    async def get_interview_stats(self, db: AsyncSession, user_id: int) -> dict:
        """Get interview statistics for a user."""
        # Get counts by status
        total_result = await db.execute(
            select(func.count(Interview.id)).where(
                or_(
                    Interview.candidate_id == user_id,
                    Interview.recruiter_id == user_id,
                    Interview.created_by == user_id,
                )
            )
        )
        total = total_result.scalar() or 0

        scheduled_result = await db.execute(
            select(func.count(Interview.id)).where(
                or_(
                    Interview.candidate_id == user_id,
                    Interview.recruiter_id == user_id,
                    Interview.created_by == user_id,
                ),
                Interview.status == InterviewStatus.SCHEDULED,
            )
        )
        scheduled = scheduled_result.scalar() or 0

        completed_result = await db.execute(
            select(func.count(Interview.id)).where(
                or_(
                    Interview.candidate_id == user_id,
                    Interview.recruiter_id == user_id,
                    Interview.created_by == user_id,
                ),
                Interview.status == InterviewStatus.COMPLETED,
            )
        )
        completed = completed_result.scalar() or 0

        cancelled_result = await db.execute(
            select(func.count(Interview.id)).where(
                or_(
                    Interview.candidate_id == user_id,
                    Interview.recruiter_id == user_id,
                    Interview.created_by == user_id,
                ),
                Interview.status == InterviewStatus.CANCELLED,
            )
        )
        cancelled = cancelled_result.scalar() or 0

        return {
            "total": total,
            "scheduled": scheduled,
            "completed": completed,
            "cancelled": cancelled,
        }

    async def get_detailed_interview_stats(self, db: AsyncSession, user_id: int) -> Dict:
        """Get detailed interview statistics for a user."""
        # Base condition for user's interviews
        base_condition = or_(
            Interview.candidate_id == user_id,
            Interview.recruiter_id == user_id,
            Interview.created_by == user_id,
        )

        # Total interviews
        total_result = await db.execute(
            select(func.count()).select_from(
                select(Interview).where(base_condition).subquery()
            )
        )
        total_interviews = total_result.scalar()

        # By status
        status_result = await db.execute(
            select(Interview.status, func.count(Interview.id))
            .where(base_condition)
            .group_by(Interview.status)
        )
        by_status = {status: count for status, count in status_result.all()}

        # By type
        type_result = await db.execute(
            select(Interview.interview_type, func.count(Interview.id))
            .where(base_condition)
            .group_by(Interview.interview_type)
        )
        by_type = {itype: count for itype, count in type_result.all()}

        # Upcoming interviews
        upcoming_result = await db.execute(
            select(func.count(Interview.id)).where(
                base_condition,
                Interview.scheduled_start > datetime.utcnow(),
                Interview.status.in_(
                    [InterviewStatus.CONFIRMED.value, InterviewStatus.IN_PROGRESS.value]
                ),
            )
        )
        upcoming_count = upcoming_result.scalar()

        # Average duration
        duration_result = await db.execute(
            select(func.avg(Interview.duration_minutes)).where(
                base_condition,
                Interview.duration_minutes.is_not(None),
            )
        )
        average_duration = duration_result.scalar()

        return {
            "total_interviews": total_interviews,
            "by_status": by_status,
            "by_type": by_type,
            "upcoming_count": upcoming_count,
            "completed_count": by_status.get(InterviewStatus.COMPLETED.value, 0),
            "average_duration_minutes": float(average_duration) if average_duration else None,
        }

    async def get_calendar_events(
        self, db: AsyncSession, user_id: int, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None
    ) -> List[Interview]:
        """Get interview events in calendar format."""
        query = (
            select(Interview)
            .options(selectinload(Interview.candidate), selectinload(Interview.recruiter))
            .where(
                or_(
                    Interview.candidate_id == user_id,
                    Interview.recruiter_id == user_id,
                    Interview.created_by == user_id,
                ),
                Interview.scheduled_start.is_not(None),
                Interview.status.in_(
                    [
                        InterviewStatus.CONFIRMED.value,
                        InterviewStatus.IN_PROGRESS.value,
                        InterviewStatus.COMPLETED.value,
                    ]
                ),
            )
        )

        if start_date:
            query = query.where(Interview.scheduled_start >= start_date)
        if end_date:
            query = query.where(Interview.scheduled_start <= end_date)

        result = await db.execute(query)
        return result.scalars().all()

    async def get_active_proposals_count(self, db: AsyncSession, interview_id: int) -> int:
        """Get count of active proposals for an interview."""
        active_proposals_result = await db.execute(
            select(func.count(InterviewProposal.id)).where(
                InterviewProposal.interview_id == interview_id,
                InterviewProposal.status == "pending",
                InterviewProposal.expires_at > datetime.utcnow(),
            )
        )
        return active_proposals_result.scalar() or 0


class CRUDInterviewProposal(CRUDBase[InterviewProposal, dict, dict]):
    """Interview proposal CRUD operations."""

    async def get_by_interview(self, db: AsyncSession, interview_id: int) -> List[InterviewProposal]:
        """Get proposals for a specific interview."""
        result = await db.execute(
            select(InterviewProposal)
            .options(selectinload(InterviewProposal.created_by_user))
            .where(InterviewProposal.interview_id == interview_id)
            .order_by(InterviewProposal.created_at.desc())
        )
        return result.scalars().all()

    async def get_pending_proposals(self, db: AsyncSession, user_id: int) -> List[InterviewProposal]:
        """Get pending proposals for a user."""
        result = await db.execute(
            select(InterviewProposal)
            .options(
                selectinload(InterviewProposal.interview).selectinload(Interview.candidate),
                selectinload(InterviewProposal.interview).selectinload(Interview.recruiter),
                selectinload(InterviewProposal.created_by_user),
            )
            .join(Interview)
            .where(
                or_(
                    Interview.candidate_id == user_id,
                    Interview.recruiter_id == user_id,
                ),
                InterviewProposal.status == "pending",
            )
            .order_by(InterviewProposal.created_at.desc())
        )
        return result.scalars().all()

    async def get_calendar_accounts_by_user(self, db: AsyncSession, user_id: int) -> List:
        """Get active calendar accounts for a user."""
        from app.models.calendar_integration import ExternalCalendarAccount

        result = await db.execute(
            select(ExternalCalendarAccount).where(
                ExternalCalendarAccount.user_id == user_id,
                ExternalCalendarAccount.is_active == True,
            )
        )
        return result.scalars().all()


# Create the CRUD instances
interview = CRUDInterview(Interview)
interview_proposal = CRUDInterviewProposal(InterviewProposal)