import logging
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.dependencies import get_current_active_user
from app.models.interview import Interview, InterviewProposal
from app.models.user import User
from app.schemas.interview import (
    CalendarIntegrationStatus,
    InterviewCalendarEvent,
    InterviewCancel,
    InterviewCreate,
    InterviewInfo,
    InterviewReschedule,
    InterviewsListRequest,
    InterviewsListResponse,
    InterviewStats,
    InterviewUpdate,
    ParticipantInfo,
    ProposalCreate,
    ProposalInfo,
    ProposalResponse,
)
from app.services.interview_service import interview_service
from app.utils.constants import InterviewStatus
from app.utils.permissions import is_company_admin, is_super_admin, requires_permission

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=InterviewInfo)
@requires_permission("interviews.create")
async def create_interview(
    interview_data: InterviewCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new interview."""
    interview = await interview_service.create_interview(
        db=db,
        candidate_id=interview_data.candidate_id,
        recruiter_id=interview_data.recruiter_id,
        employer_company_id=interview_data.employer_company_id,
        title=interview_data.title,
        description=interview_data.description,
        position_title=interview_data.position_title,
        interview_type=interview_data.interview_type,
        created_by=current_user.id,
    )

    return await _format_interview_response(db, interview)


@router.get("/", response_model=InterviewsListResponse)
@requires_permission("interviews.read")
async def get_interviews(
    request: InterviewsListRequest = Depends(),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get list of interviews with filtering."""
    interviews = await interview_service.get_user_interviews(
        db=db,
        user_id=current_user.id,
        status_filter=request.status,
        start_date=request.start_date,
        end_date=request.end_date,
        limit=request.limit,
        offset=request.offset,
    )

    # Get total count
    count_query = select(func.count(Interview.id)).where(
        or_(
            Interview.candidate_id == current_user.id,
            Interview.recruiter_id == current_user.id,
            Interview.created_by == current_user.id,
        )
    )

    if request.status:
        count_query = count_query.where(Interview.status == request.status)
    if request.start_date:
        count_query = count_query.where(Interview.scheduled_start >= request.start_date)
    if request.end_date:
        count_query = count_query.where(Interview.scheduled_start <= request.end_date)

    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Format response
    formatted_interviews = []
    for interview in interviews:
        formatted_interviews.append(await _format_interview_response(db, interview))

    return InterviewsListResponse(
        interviews=formatted_interviews,
        total=total,
        has_more=request.offset + request.limit < total,
    )


@router.get("/{interview_id}", response_model=InterviewInfo)
@requires_permission("interviews.read")
async def get_interview(
    interview_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get interview by ID."""
    result = await db.execute(
        select(Interview)
        .options(
            selectinload(Interview.candidate),
            selectinload(Interview.recruiter),
            selectinload(Interview.employer_company),
            selectinload(Interview.recruiter_company),
            selectinload(Interview.proposals).selectinload(InterviewProposal.proposer),
            selectinload(Interview.proposals).selectinload(InterviewProposal.responder),
        )
        .where(Interview.id == interview_id)
    )

    interview = result.scalar_one_or_none()
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Interview not found"
        )

    # Check access permissions
    if not await _check_interview_access(current_user, interview):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    return await _format_interview_response(db, interview)


@router.patch("/{interview_id}", response_model=InterviewInfo)
@requires_permission("interviews.update")
async def update_interview(
    interview_id: int,
    interview_data: InterviewUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Update interview details."""
    result = await db.execute(
        select(Interview)
        .options(
            selectinload(Interview.candidate),
            selectinload(Interview.recruiter),
            selectinload(Interview.employer_company),
        )
        .where(Interview.id == interview_id)
    )

    interview = result.scalar_one_or_none()
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Interview not found"
        )

    # Check access permissions
    if not await _check_interview_access(current_user, interview):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    # Update fields
    if interview_data.title is not None:
        interview.title = interview_data.title
    if interview_data.description is not None:
        interview.description = interview_data.description
    if interview_data.position_title is not None:
        interview.position_title = interview_data.position_title
    if interview_data.interview_type is not None:
        interview.interview_type = interview_data.interview_type
    if interview_data.location is not None:
        interview.location = interview_data.location
    if interview_data.meeting_url is not None:
        interview.meeting_url = interview_data.meeting_url
    if interview_data.notes is not None:
        interview.notes = interview_data.notes

    await db.commit()

    return await _format_interview_response(db, interview)


@router.post("/{interview_id}/proposals", response_model=ProposalInfo)
@requires_permission("interviews.propose")
async def create_proposal(
    interview_id: int,
    proposal_data: ProposalCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new time proposal for an interview."""
    proposal = await interview_service.create_proposal(
        db=db,
        interview_id=interview_id,
        proposed_by=current_user.id,
        start_datetime=proposal_data.start_datetime,
        end_datetime=proposal_data.end_datetime,
        timezone=proposal_data.timezone,
        location=proposal_data.location,
        notes=proposal_data.notes,
    )

    return await _format_proposal_response(db, proposal)


@router.post(
    "/{interview_id}/proposals/{proposal_id}/respond", response_model=ProposalInfo
)
@requires_permission("interviews.accept")
async def respond_to_proposal(
    interview_id: int,
    proposal_id: int,
    response_data: ProposalResponse,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Respond to a time proposal (accept or decline)."""
    proposal = await interview_service.respond_to_proposal(
        db=db,
        proposal_id=proposal_id,
        response=response_data.response,
        responded_by=current_user.id,
        response_notes=response_data.notes,
    )

    return await _format_proposal_response(db, proposal)


@router.post("/{interview_id}/cancel", response_model=InterviewInfo)
@requires_permission("interviews.cancel")
async def cancel_interview(
    interview_id: int,
    cancel_data: InterviewCancel,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Cancel an interview."""
    interview = await interview_service.cancel_interview(
        db=db,
        interview_id=interview_id,
        cancelled_by=current_user.id,
        reason=cancel_data.reason,
    )

    return await _format_interview_response(db, interview)


@router.post("/{interview_id}/reschedule", response_model=InterviewInfo)
@requires_permission("interviews.update")
async def reschedule_interview(
    interview_id: int,
    reschedule_data: InterviewReschedule,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Reschedule an interview."""
    interview = await interview_service.reschedule_interview(
        db=db,
        interview_id=interview_id,
        new_start=reschedule_data.new_start,
        new_end=reschedule_data.new_end,
        rescheduled_by=current_user.id,
        reason=reschedule_data.reason,
    )

    return await _format_interview_response(db, interview)


@router.get("/stats/summary", response_model=InterviewStats)
@requires_permission("interviews.read")
async def get_interview_stats(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get interview statistics for the current user."""
    # Base query for user's interviews
    base_query = select(Interview).where(
        or_(
            Interview.candidate_id == current_user.id,
            Interview.recruiter_id == current_user.id,
            Interview.created_by == current_user.id,
        )
    )

    # Total interviews
    total_result = await db.execute(
        select(func.count()).select_from(base_query.subquery())
    )
    total_interviews = total_result.scalar()

    # By status
    status_result = await db.execute(
        select(Interview.status, func.count(Interview.id))
        .where(
            or_(
                Interview.candidate_id == current_user.id,
                Interview.recruiter_id == current_user.id,
                Interview.created_by == current_user.id,
            )
        )
        .group_by(Interview.status)
    )
    by_status = {status: count for status, count in status_result.all()}

    # By type
    type_result = await db.execute(
        select(Interview.interview_type, func.count(Interview.id))
        .where(
            or_(
                Interview.candidate_id == current_user.id,
                Interview.recruiter_id == current_user.id,
                Interview.created_by == current_user.id,
            )
        )
        .group_by(Interview.interview_type)
    )
    by_type = {itype: count for itype, count in type_result.all()}

    # Upcoming interviews
    upcoming_result = await db.execute(
        select(func.count(Interview.id)).where(
            or_(
                Interview.candidate_id == current_user.id,
                Interview.recruiter_id == current_user.id,
                Interview.created_by == current_user.id,
            ),
            Interview.scheduled_start > datetime.utcnow(),
            Interview.status.in_(
                [InterviewStatus.CONFIRMED.value, InterviewStatus.IN_PROGRESS.value]
            ),
        )
    )
    upcoming_count = upcoming_result.scalar()

    # Completed interviews
    completed_count = by_status.get(InterviewStatus.COMPLETED.value, 0)

    # Average duration
    duration_result = await db.execute(
        select(func.avg(Interview.duration_minutes)).where(
            or_(
                Interview.candidate_id == current_user.id,
                Interview.recruiter_id == current_user.id,
                Interview.created_by == current_user.id,
            ),
            Interview.duration_minutes.is_not(None),
        )
    )
    average_duration = duration_result.scalar()

    return InterviewStats(
        total_interviews=total_interviews,
        by_status=by_status,
        by_type=by_type,
        upcoming_count=upcoming_count,
        completed_count=completed_count,
        average_duration_minutes=float(average_duration) if average_duration else None,
    )


@router.get("/calendar/events", response_model=list[InterviewCalendarEvent])
@requires_permission("interviews.read")
async def get_interview_calendar_events(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get interview events in calendar format."""
    query = (
        select(Interview)
        .options(selectinload(Interview.candidate), selectinload(Interview.recruiter))
        .where(
            or_(
                Interview.candidate_id == current_user.id,
                Interview.recruiter_id == current_user.id,
                Interview.created_by == current_user.id,
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
    interviews = result.scalars().all()

    calendar_events = []
    for interview in interviews:
        participants = []
        if interview.candidate.email:
            participants.append(interview.candidate.email)
        if interview.recruiter.email:
            participants.append(interview.recruiter.email)

        calendar_events.append(
            InterviewCalendarEvent(
                interview_id=interview.id,
                title=interview.title,
                start=interview.scheduled_start,
                end=interview.scheduled_end
                or (interview.scheduled_start + timedelta(hours=1)),
                status=interview.status,
                participants=participants,
                location=interview.location,
                meeting_url=interview.meeting_url,
            )
        )

    return calendar_events


@router.get("/calendar/integration-status", response_model=CalendarIntegrationStatus)
async def get_calendar_integration_status(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get calendar integration status for the current user."""
    from app.models.calendar_integration import ExternalCalendarAccount

    result = await db.execute(
        select(ExternalCalendarAccount).where(
            ExternalCalendarAccount.user_id == current_user.id,
            ExternalCalendarAccount.is_active == True,
        )
    )
    accounts = result.scalars().all()

    google_account = next((acc for acc in accounts if acc.provider == "google"), None)
    microsoft_account = next(
        (acc for acc in accounts if acc.provider == "microsoft"), None
    )

    # Get latest sync time
    latest_sync = None
    sync_enabled = False

    for account in accounts:
        if account.sync_enabled:
            sync_enabled = True
        if account.last_sync_at and (
            not latest_sync or account.last_sync_at > latest_sync
        ):
            latest_sync = account.last_sync_at

    return CalendarIntegrationStatus(
        has_google_calendar=google_account is not None,
        has_microsoft_calendar=microsoft_account is not None,
        google_calendar_email=google_account.email if google_account else None,
        microsoft_calendar_email=microsoft_account.email if microsoft_account else None,
        last_sync_at=latest_sync,
        sync_enabled=sync_enabled,
    )


# Helper functions
async def _format_interview_response(
    db: AsyncSession, interview: Interview
) -> InterviewInfo:
    """Format interview for API response."""
    # Get active proposals count
    active_proposals_result = await db.execute(
        select(func.count(InterviewProposal.id)).where(
            InterviewProposal.interview_id == interview.id,
            InterviewProposal.status == "pending",
            InterviewProposal.expires_at > datetime.utcnow(),
        )
    )
    active_proposal_count = active_proposals_result.scalar()

    # Format proposals
    formatted_proposals = []
    for proposal in interview.proposals:
        formatted_proposals.append(await _format_proposal_response(db, proposal))

    return InterviewInfo(
        id=interview.id,
        title=interview.title,
        description=interview.description,
        position_title=interview.position_title,
        status=interview.status,
        interview_type=interview.interview_type,
        candidate=ParticipantInfo(
            id=interview.candidate.id,
            email=interview.candidate.email,
            full_name=interview.candidate.full_name,
            role="candidate",
            company_name=interview.candidate.company.name
            if interview.candidate.company
            else None,
        ),
        recruiter=ParticipantInfo(
            id=interview.recruiter.id,
            email=interview.recruiter.email,
            full_name=interview.recruiter.full_name,
            role="recruiter",
            company_name=interview.recruiter.company.name
            if interview.recruiter.company
            else None,
        ),
        employer_company_name=interview.employer_company.name,
        scheduled_start=interview.scheduled_start,
        scheduled_end=interview.scheduled_end,
        timezone=interview.timezone,
        location=interview.location,
        meeting_url=interview.meeting_url,
        duration_minutes=interview.duration_minutes,
        notes=interview.notes,
        preparation_notes=interview.preparation_notes,
        created_by=interview.created_by,
        confirmed_by=interview.confirmed_by,
        confirmed_at=interview.confirmed_at,
        cancelled_by=interview.cancelled_by,
        cancelled_at=interview.cancelled_at,
        cancellation_reason=interview.cancellation_reason,
        proposals=formatted_proposals,
        active_proposal_count=active_proposal_count,
        created_at=interview.created_at,
        updated_at=interview.updated_at,
    )


async def _format_proposal_response(
    db: AsyncSession, proposal: InterviewProposal
) -> ProposalInfo:
    """Format proposal for API response."""
    return ProposalInfo(
        id=proposal.id,
        interview_id=proposal.interview_id,
        proposed_by=proposal.proposed_by,
        proposer_name=proposal.proposer.full_name,
        proposer_role=proposal.proposer_role,
        start_datetime=proposal.start_datetime,
        end_datetime=proposal.end_datetime,
        timezone=proposal.timezone,
        location=proposal.location,
        notes=proposal.notes,
        status=proposal.status,
        responded_by=proposal.responded_by,
        responder_name=proposal.responder.full_name if proposal.responder else None,
        responded_at=proposal.responded_at,
        response_notes=proposal.response_notes,
        expires_at=proposal.expires_at,
        created_at=proposal.created_at,
    )


async def _check_interview_access(user: User, interview: Interview) -> bool:
    """Check if user has access to the interview."""
    # Super admin has access to everything
    if is_super_admin(user):
        return True

    # Participants have access
    if user.id in [
        interview.candidate_id,
        interview.recruiter_id,
        interview.created_by,
    ]:
        return True

    # Company admin has access to interviews in their company
    if is_company_admin(user):
        if user.company_id in [
            interview.employer_company_id,
            interview.recruiter_company_id,
        ]:
            return True

    # Employer users have access to interviews with their company
    if user.company_id == interview.employer_company_id:
        return True

    return False
