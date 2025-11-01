from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import func, or_, select

if TYPE_CHECKING:
    from app.models.calendar_integration import ExternalCalendarAccount
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.crud.base import CRUDBase
from app.models.interview import Interview, InterviewProposal
from app.models.user import User
from app.schemas.interview import InterviewCreate, InterviewUpdate
from app.utils.constants import InterviewStatus
from app.utils.datetime_utils import get_utc_now


class CRUDInterview(CRUDBase[Interview, InterviewCreate, InterviewUpdate]):
    """Interview CRUD operations."""

    async def get(self, db: AsyncSession, id: int) -> Interview | None:
        """Get interview by id, excluding soft-deleted records."""
        result = await db.execute(
            select(Interview).where(Interview.id == id, ~Interview.is_deleted)
        )
        return result.scalar_one_or_none()

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> list[Interview]:
        """Get multiple interviews, excluding soft-deleted records."""
        result = await db.execute(
            select(Interview)
            .where(~Interview.is_deleted)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_with_relationships(
        self, db: AsyncSession, interview_id: int
    ) -> Interview | None:
        """Get interview with all relationships loaded, excluding soft-deleted."""
        # First get the interview
        result = await db.execute(
            select(Interview).where(
                Interview.id == interview_id, ~Interview.is_deleted
            )
        )
        interview = result.scalar_one_or_none()

        if not interview:
            return None

        # Manually load relationships to ensure they work
        if interview.candidate_id:
            candidate_result = await db.execute(
                select(User)
                .options(joinedload(User.company))
                .where(User.id == interview.candidate_id)
            )
            interview.candidate = candidate_result.scalar_one_or_none()

        if interview.recruiter_id:
            recruiter_result = await db.execute(
                select(User)
                .options(joinedload(User.company))
                .where(User.id == interview.recruiter_id)
            )
            interview.recruiter = recruiter_result.scalar_one_or_none()

        # Load employer company
        if interview.employer_company_id:
            from app.models.company import Company

            company_result = await db.execute(
                select(Company).where(Company.id == interview.employer_company_id)
            )
            interview.employer_company = company_result.scalar_one_or_none()

        # Load creator
        if interview.created_by:
            creator_result = await db.execute(
                select(User).where(User.id == interview.created_by)
            )
            interview.creator = creator_result.scalar_one_or_none()

        # Load proposals (keeping selectinload as it might work better for collections)
        proposals_result = await db.execute(
            select(InterviewProposal).where(
                InterviewProposal.interview_id == interview_id
            )
        )
        interview.proposals = proposals_result.scalars().all()

        return interview

    async def get_user_interviews(
        self,
        db: AsyncSession,
        user_id: int,
        status_filter: InterviewStatus | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Interview]:
        """Get interviews for a specific user, excluding soft-deleted."""
        query = (
            select(Interview)
            .options(
                selectinload(Interview.candidate),
                selectinload(Interview.recruiter),
                selectinload(Interview.employer_company),
                selectinload(Interview.creator),
                selectinload(Interview.proposals),
            )
            .where(
                or_(
                    Interview.candidate_id == user_id,
                    Interview.recruiter_id == user_id,
                    Interview.created_by == user_id,
                ),
                ~Interview.is_deleted,
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
        return list(result.scalars().all())

    async def get_user_interviews_count(
        self,
        db: AsyncSession,
        user_id: int,
        status_filter: InterviewStatus | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> int:
        """Get count of interviews for a specific user, excluding soft-deleted."""
        query = select(func.count(Interview.id)).where(
            or_(
                Interview.candidate_id == user_id,
                Interview.recruiter_id == user_id,
                Interview.created_by == user_id,
            ),
            ~Interview.is_deleted,
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
    ) -> list[Interview]:
        """Get upcoming interviews for a user, excluding soft-deleted."""
        now = get_utc_now()
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
                Interview.status.in_(
                    [InterviewStatus.SCHEDULED, InterviewStatus.CONFIRMED]
                ),
                ~Interview.is_deleted,
            )
            .order_by(Interview.scheduled_start.asc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_interview_stats(self, db: AsyncSession, user_id: int) -> dict:
        """Get interview statistics for a user, excluding soft-deleted."""
        # Get counts by status
        total_result = await db.execute(
            select(func.count(Interview.id)).where(
                or_(
                    Interview.candidate_id == user_id,
                    Interview.recruiter_id == user_id,
                    Interview.created_by == user_id,
                ),
                ~Interview.is_deleted,
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
                ~Interview.is_deleted,
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
                ~Interview.is_deleted,
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
                ~Interview.is_deleted,
            )
        )
        cancelled = cancelled_result.scalar() or 0

        return {
            "total": total,
            "scheduled": scheduled,
            "completed": completed,
            "cancelled": cancelled,
        }

    async def get_detailed_interview_stats(
        self, db: AsyncSession, user_id: int
    ) -> dict:
        """Get detailed interview statistics for a user, excluding soft-deleted."""
        # Base condition for user's interviews
        base_condition = or_(
            Interview.candidate_id == user_id,
            Interview.recruiter_id == user_id,
            Interview.created_by == user_id,
        )

        # Add soft delete filter
        not_deleted_condition = ~Interview.is_deleted

        # Total interviews
        total_result = await db.execute(
            select(func.count()).select_from(
                select(Interview)
                .where(base_condition, not_deleted_condition)
                .subquery()
            )
        )
        total_interviews = total_result.scalar()

        # By status
        status_result = await db.execute(
            select(Interview.status, func.count(Interview.id))
            .where(base_condition, not_deleted_condition)
            .group_by(Interview.status)
        )
        by_status = {row[0]: row[1] for row in status_result.all()}

        # By type
        type_result = await db.execute(
            select(Interview.interview_type, func.count(Interview.id))
            .where(base_condition, not_deleted_condition)
            .group_by(Interview.interview_type)
        )
        by_type = {row[0]: row[1] for row in type_result.all()}

        # Upcoming interviews
        upcoming_result = await db.execute(
            select(func.count(Interview.id)).where(
                base_condition,
                not_deleted_condition,
                Interview.scheduled_start > get_utc_now(),
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
                not_deleted_condition,
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
            "average_duration_minutes": float(average_duration)
            if average_duration
            else None,
        }

    async def get_calendar_events(
        self,
        db: AsyncSession,
        user_id: int,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[Interview]:
        """Get interview events in calendar format, excluding soft-deleted."""
        query = (
            select(Interview)
            .options(
                selectinload(Interview.candidate), selectinload(Interview.recruiter)
            )
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
                ~Interview.is_deleted,
            )
        )

        if start_date:
            query = query.where(Interview.scheduled_start >= start_date)
        if end_date:
            query = query.where(Interview.scheduled_start <= end_date)

        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_active_proposals_count(
        self, db: AsyncSession, interview_id: int
    ) -> int:
        """Get count of active proposals for an interview."""
        active_proposals_result = await db.execute(
            select(func.count(InterviewProposal.id)).where(
                InterviewProposal.interview_id == interview_id,
                InterviewProposal.status == "pending",
                InterviewProposal.expires_at > get_utc_now(),
            )
        )
        return active_proposals_result.scalar() or 0

    async def get_calendar_accounts_by_user(
        self, db: AsyncSession, user_id: int
    ) -> list[ExternalCalendarAccount]:
        """Get active calendar accounts for a user."""
        from app.models.calendar_integration import ExternalCalendarAccount

        result = await db.execute(
            select(ExternalCalendarAccount).where(
                ExternalCalendarAccount.user_id == user_id,
                ExternalCalendarAccount.is_active,
            )
        )
        return list(result.scalars().all())


class CRUDInterviewProposal(CRUDBase[InterviewProposal, Any, Any]):
    """Interview proposal CRUD operations."""

    async def get_by_interview(
        self, db: AsyncSession, interview_id: int
    ) -> list[InterviewProposal]:
        """Get proposals for a specific interview."""
        result = await db.execute(
            select(InterviewProposal)
            .options(selectinload(InterviewProposal.proposer))
            .where(InterviewProposal.interview_id == interview_id)
            .order_by(InterviewProposal.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_pending_proposals(
        self, db: AsyncSession, user_id: int
    ) -> list[InterviewProposal]:
        """Get pending proposals for a user."""
        result = await db.execute(
            select(InterviewProposal)
            .options(
                selectinload(InterviewProposal.interview).selectinload(
                    Interview.candidate
                ),
                selectinload(InterviewProposal.interview).selectinload(
                    Interview.recruiter
                ),
                selectinload(InterviewProposal.proposer),
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
        return list(result.scalars().all())


# Create the CRUD instances
interview = CRUDInterview(Interview)
interview_proposal = CRUDInterviewProposal(InterviewProposal)
