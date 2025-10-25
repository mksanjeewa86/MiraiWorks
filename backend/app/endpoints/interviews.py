import logging
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.endpoints import API_ROUTES
from app.crud.interview import interview as interview_crud
from app.crud.interview_note import interview_note as interview_note_crud
from app.crud.video_call import video_call as video_call_crud
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
from app.schemas.interview_note import InterviewNoteInfo, InterviewNoteUpdate
from app.schemas.video_call import VideoCallCreate, VideoCallInfo
from app.services.interview_service import interview_service
from app.utils.constants import InterviewStatus
from app.utils.datetime_utils import get_utc_now
from app.utils.permissions import is_company_admin, is_super_admin, requires_permission

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    API_ROUTES.INTERVIEWS.BASE_SLASH,
    response_model=InterviewInfo,
    status_code=status.HTTP_201_CREATED,
)
@requires_permission("interviews.create")
async def create_interview(
    interview_data: InterviewCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new interview."""
    employer_company_id = interview_data.employer_company_id or current_user.company_id
    if employer_company_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employer company context required",
        )

    recruiter_id = (
        interview_data.recruiter_id or interview_data.interviewer_id or current_user.id
    )

    interview = await interview_service.create_interview(
        db=db,
        candidate_id=interview_data.candidate_id,
        recruiter_id=recruiter_id,
        employer_company_id=employer_company_id,
        title=interview_data.title,
        description=interview_data.description,
        position_title=interview_data.position_title or interview_data.title,
        interview_type=interview_data.interview_type,
        created_by=current_user.id,
        status=interview_data.status,
        scheduled_start=interview_data.scheduled_start,
        scheduled_end=interview_data.scheduled_end,
        timezone=interview_data.timezone,
        location=interview_data.location,
        meeting_url=interview_data.meeting_url,
        video_call_type=interview_data.video_call_type,
        notes=interview_data.notes,
    )

    interview_with_relationships = await interview_crud.get_with_relationships(
        db, interview.id
    )

    return await _format_interview_response(db, interview_with_relationships)


@router.get(API_ROUTES.INTERVIEWS.BASE_SLASH, response_model=InterviewsListResponse)
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

    # Get total count using CRUD
    total = await interview_crud.get_user_interviews_count(
        db=db,
        user_id=current_user.id,
        status_filter=request.status,
        start_date=request.start_date,
        end_date=request.end_date,
    )

    # Format response
    formatted_interviews = []
    for interview in interviews:
        formatted_interviews.append(await _format_interview_response(db, interview))

    return InterviewsListResponse(
        interviews=formatted_interviews,
        total=total,
        has_more=request.offset + request.limit < total,
    )


@router.get(API_ROUTES.INTERVIEWS.BY_ID, response_model=InterviewInfo)
@requires_permission("interviews.read")
async def get_interview(
    interview_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get interview by ID."""
    interview = await interview_crud.get_with_relationships(db, interview_id)
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


@router.patch(API_ROUTES.INTERVIEWS.BY_ID, response_model=InterviewInfo)
@requires_permission("interviews.update")
async def update_interview(
    interview_id: int,
    interview_data: InterviewUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Update interview details."""
    interview = await interview_crud.get_with_relationships(db, interview_id)
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


@router.post(API_ROUTES.INTERVIEWS.PROPOSALS, response_model=ProposalInfo)
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


@router.post(API_ROUTES.INTERVIEWS.PROPOSAL_RESPOND, response_model=ProposalInfo)
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


@router.post(API_ROUTES.INTERVIEWS.CANCEL, response_model=InterviewInfo)
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


@router.post(API_ROUTES.INTERVIEWS.RESCHEDULE, response_model=InterviewInfo)
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


@router.get(API_ROUTES.INTERVIEWS.STATS_SUMMARY, response_model=InterviewStats)
@requires_permission("interviews.read")
async def get_interview_stats(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get interview statistics for the current user."""
    stats = await interview_crud.get_detailed_interview_stats(db, current_user.id)
    return InterviewStats(**stats)


@router.get(
    API_ROUTES.INTERVIEWS.CALENDAR_EVENTS, response_model=list[InterviewCalendarEvent]
)
@requires_permission("interviews.read")
async def get_interview_calendar_events(
    start_date: datetime | None = Query(None),
    end_date: datetime | None = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get interview events in calendar format."""
    interviews = await interview_crud.get_calendar_events(
        db, current_user.id, start_date, end_date
    )

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


@router.get(
    API_ROUTES.INTERVIEWS.CALENDAR_INTEGRATION_STATUS,
    response_model=CalendarIntegrationStatus,
)
async def get_calendar_integration_status(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get calendar integration status for the current user."""
    accounts = await interview_crud.get_calendar_accounts_by_user(db, current_user.id)

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
    active_proposal_count = await interview_crud.get_active_proposals_count(
        db, interview.id
    )

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
            id=interview.candidate.id if interview.candidate else 0,
            email=interview.candidate.email
            if interview.candidate
            else "unknown@example.com",
            full_name=interview.candidate.full_name
            if interview.candidate
            else "Unknown Candidate",
            role="candidate",
            company_name=interview.candidate.company.name
            if interview.candidate and interview.candidate.company
            else None,
        )
        if interview.candidate
        else ParticipantInfo(
            id=0,
            email="unknown@example.com",
            full_name="Unknown Candidate",
            role="candidate",
            company_name=None,
        ),
        recruiter=ParticipantInfo(
            id=interview.recruiter.id if interview.recruiter else 0,
            email=interview.recruiter.email
            if interview.recruiter
            else "unknown@example.com",
            full_name=interview.recruiter.full_name
            if interview.recruiter
            else "Unknown Recruiter",
            role="recruiter",
            company_name=interview.recruiter.company.name
            if interview.recruiter and interview.recruiter.company
            else None,
        )
        if interview.recruiter
        else ParticipantInfo(
            id=0,
            email="unknown@example.com",
            full_name="Unknown Recruiter",
            role="recruiter",
            company_name=None,
        ),
        employer_company_name=interview.employer_company.name
        if interview.employer_company
        else "Unknown Company",
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
    if is_company_admin(user) and user.company_id in [
        interview.employer_company_id,
        interview.recruiter_company_id,
    ]:
        return True

    # Employer users have access to interviews with their company
    return user.company_id == interview.employer_company_id


# Video Call Integration Endpoints


@router.post(API_ROUTES.INTERVIEWS.VIDEO_CALL, response_model=VideoCallInfo)
async def create_interview_video_call(
    interview_id: int,
    video_call_data: VideoCallCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a video call for an existing interview."""
    # Get interview
    interview = await interview_crud.get_with_relationships(db, interview_id)
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Interview not found"
        )

    # Check access
    if not await _check_interview_access(current_user, interview):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this interview",
        )

    # Check if video call already exists
    existing_call = await video_call_crud.get_by_interview_id(
        db, interview_id=interview_id
    )
    if existing_call:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Video call already exists for this interview",
        )

    # Create video call with interview link
    video_call_data.interview_id = interview_id
    video_call_data.candidate_id = interview.candidate_id

    # Use scheduled time from interview if not provided
    if not video_call_data.scheduled_at and interview.scheduled_start:
        video_call_data.scheduled_at = interview.scheduled_start

    video_call = await video_call_crud.create_with_interviewer(
        db, obj_in=video_call_data, interviewer_id=interview.recruiter_id
    )

    # Update interview with video meeting URL
    await interview_crud.update(
        db,
        db_obj=interview,
        obj_in={"meeting_url": f"/video-calls/{video_call.id}/join"},
    )

    return video_call


@router.get(API_ROUTES.INTERVIEWS.VIDEO_CALL, response_model=VideoCallInfo)
@requires_permission("interviews.read")
async def get_interview_video_call(
    interview_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the video call associated with an interview."""
    # Get interview
    interview = await interview_crud.get_with_relationships(db, interview_id)
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Interview not found"
        )

    # Check access
    if not await _check_interview_access(current_user, interview):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this interview",
        )

    # Get video call
    video_call = await video_call_crud.get_by_interview_id(
        db, interview_id=interview_id
    )
    if not video_call:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No video call found for this interview",
        )

    return video_call


@router.delete(API_ROUTES.INTERVIEWS.VIDEO_CALL)
@requires_permission("interviews.update")
async def delete_interview_video_call(
    interview_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove video call from an interview."""
    # Get interview
    interview = await interview_crud.get_with_relationships(db, interview_id)
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Interview not found"
        )

    # Check access
    if not await _check_interview_access(current_user, interview):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this interview",
        )

    # Get video call
    video_call = await video_call_crud.get_by_interview_id(
        db, interview_id=interview_id
    )
    if not video_call:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No video call found for this interview",
        )

    # Check if call is in progress
    if video_call.status == "in_progress":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete an active video call",
        )

    # Delete video call
    await video_call_crud.remove(db, id=video_call.id)

    # Clear meeting URL from interview
    await interview_crud.update(db, db_obj=interview, obj_in={"meeting_url": None})

    return {"message": "Video call removed successfully"}


@router.delete(API_ROUTES.INTERVIEWS.BY_ID)
@requires_permission("interviews.delete")
async def delete_interview(
    interview_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete an interview."""
    # Get interview with relationships
    interview = await interview_crud.get_with_relationships(db, interview_id)
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Interview not found"
        )

    # Check access permissions
    if not await _check_interview_access(current_user, interview):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this interview",
        )

    # Prevent deletion of in-progress or completed interviews
    if interview.status in [InterviewStatus.IN_PROGRESS, InterviewStatus.COMPLETED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete interview with status '{interview.status}'. Only scheduled or cancelled interviews can be deleted.",
        )

    # Delete the interview
    await interview_crud.remove(db, id=interview_id)

    return {"message": "Interview deleted successfully"}


# Interview Notes Endpoints


@router.get(API_ROUTES.INTERVIEWS.NOTES, response_model=InterviewNoteInfo)
async def get_interview_note(
    interview_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current user's private note for an interview."""
    # Get interview to check access
    interview = await interview_crud.get_with_relationships(db, interview_id)
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Interview not found"
        )

    # Check if user has access to the interview
    if not await _check_interview_access(current_user, interview):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this interview",
        )

    # Get the user's note for this interview
    note = await interview_note_crud.get_by_interview_and_participant(
        db, interview_id=interview_id, participant_id=current_user.id
    )

    if not note:
        # Return empty note if none exists
        return InterviewNoteInfo(
            id=0,
            interview_id=interview_id,
            participant_id=current_user.id,
            content=None,
            created_at=get_utc_now(),
            updated_at=get_utc_now(),
        )

    return note


@router.put(API_ROUTES.INTERVIEWS.NOTES, response_model=InterviewNoteInfo)
async def update_interview_note(
    interview_id: int,
    note_data: InterviewNoteUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Update current user's private note for an interview."""
    # Get interview to check access
    interview = await interview_crud.get_with_relationships(db, interview_id)
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Interview not found"
        )

    # Check if user has access to the interview
    if not await _check_interview_access(current_user, interview):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this interview",
        )

    # Create or update the user's note
    note = await interview_note_crud.create_or_update(
        db,
        interview_id=interview_id,
        participant_id=current_user.id,
        content=note_data.content,
    )

    return note


@router.delete(API_ROUTES.INTERVIEWS.NOTES)
async def delete_interview_note(
    interview_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete current user's private note for an interview."""
    # Get interview to check access
    interview = await interview_crud.get_with_relationships(db, interview_id)
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Interview not found"
        )

    # Check if user has access to the interview
    if not await _check_interview_access(current_user, interview):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this interview",
        )

    # Delete the user's note
    deleted = await interview_note_crud.delete_by_interview_and_participant(
        db, interview_id=interview_id, participant_id=current_user.id
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Note not found"
        )

    return {"message": "Interview note deleted successfully"}
