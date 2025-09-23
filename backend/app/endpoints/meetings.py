from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.meeting import (
    MeetingCreate,
    MeetingJoinRequest,
    MeetingJoinResponse,
    MeetingListParams,
    MeetingListResponse,
    MeetingResponse,
    MeetingUpdate,
)
from app.dependencies import get_current_user
from app.services.meeting_service import MeetingService
from app.utils.permissions import requires_permission

router = APIRouter(prefix="/meetings", tags=["meetings"])


@router.post("/", response_model=MeetingResponse)
async def create_meeting(
    meeting_data: MeetingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new meeting"""
    meeting_service = MeetingService(db)
    return meeting_service.create_meeting(meeting_data, current_user)


@router.get("/", response_model=MeetingListResponse)
async def list_meetings(
    status: str = Query(None, description="Filter by meeting status"),
    meeting_type: str = Query(None, description="Filter by meeting type"),
    start_date: str = Query(None, description="Filter by start date (ISO format)"),
    end_date: str = Query(None, description="Filter by end date (ISO format)"),
    participant_id: int = Query(None, description="Filter by participant user ID"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List meetings with filtering and pagination"""

    params = MeetingListParams(
        status=status,
        meeting_type=meeting_type,
        start_date=start_date,
        end_date=end_date,
        participant_id=participant_id,
        page=page,
        limit=limit,
    )

    meeting_service = MeetingService(db)
    result = meeting_service.list_meetings(params, current_user)

    return MeetingListResponse(**result)


@router.get("/{meeting_id}", response_model=MeetingResponse)
async def get_meeting(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get meeting by ID"""
    meeting_service = MeetingService(db)
    return meeting_service.get_meeting_by_id(meeting_id, current_user)


@router.get("/room/{room_id}", response_model=MeetingResponse)
async def get_meeting_by_room_id(
    room_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get meeting by room ID"""
    meeting_service = MeetingService(db)
    return meeting_service.get_meeting_by_room_id(room_id, current_user)


@router.put("/{meeting_id}", response_model=MeetingResponse)
async def update_meeting(
    meeting_id: int,
    update_data: MeetingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update meeting"""
    meeting_service = MeetingService(db)
    return meeting_service.update_meeting(meeting_id, update_data, current_user)


@router.post("/join/{room_id}", response_model=MeetingJoinResponse)
async def join_meeting(
    room_id: str,
    join_request: MeetingJoinRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Join a meeting room"""
    meeting_service = MeetingService(db)
    return MeetingJoinResponse(
        **meeting_service.join_meeting(room_id, join_request.access_code, current_user)
    )


@router.post("/leave/{room_id}")
async def leave_meeting(
    room_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Leave a meeting room"""
    meeting_service = MeetingService(db)
    return meeting_service.leave_meeting(room_id, current_user)


@router.delete("/{meeting_id}")
@requires_permission("meeting.delete")
async def delete_meeting(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete meeting (admin only)"""
    meeting_service = MeetingService(db)
    meeting = meeting_service.get_meeting_by_id(meeting_id, current_user)

    # Additional validation for deletion
    if not meeting_service._can_modify_meeting(current_user, meeting):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this meeting",
        )

    db.delete(meeting)
    db.commit()

    return {"message": "Meeting deleted successfully"}


# Recording endpoints
@router.get("/{meeting_id}/recordings")
async def list_meeting_recordings(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List recordings for a meeting"""
    meeting_service = MeetingService(db)
    meeting = meeting_service.get_meeting_by_id(meeting_id, current_user)

    return {
        "recordings": [
            {
                "id": recording.id,
                "filename": recording.filename,
                "duration_seconds": recording.duration_seconds,
                "status": recording.status,
                "created_at": recording.created_at,
                "file_size": recording.file_size,
            }
            for recording in meeting.recordings
        ]
    }


@router.get("/{meeting_id}/transcripts")
async def list_meeting_transcripts(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List transcripts for a meeting"""
    meeting_service = MeetingService(db)
    meeting = meeting_service.get_meeting_by_id(meeting_id, current_user)

    return {
        "transcripts": [
            {
                "id": transcript.id,
                "language": transcript.language,
                "confidence_score": transcript.confidence_score,
                "word_count": transcript.word_count,
                "status": transcript.status,
                "created_at": transcript.created_at,
            }
            for transcript in meeting.transcripts
        ]
    }


@router.get("/{meeting_id}/summaries")
async def list_meeting_summaries(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List summaries for a meeting"""
    meeting_service = MeetingService(db)
    meeting = meeting_service.get_meeting_by_id(meeting_id, current_user)

    return {
        "summaries": [
            {
                "id": summary.id,
                "ai_model": summary.ai_model,
                "confidence_score": summary.confidence_score,
                "is_final": summary.is_final,
                "status": summary.status,
                "created_at": summary.created_at,
            }
            for summary in meeting.summaries
        ]
    }


@router.get("/{meeting_id}/transcripts/{transcript_id}")
async def get_meeting_transcript(
    meeting_id: int,
    transcript_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get full transcript content"""
    meeting_service = MeetingService(db)
    meeting = meeting_service.get_meeting_by_id(meeting_id, current_user)

    transcript = next((t for t in meeting.transcripts if t.id == transcript_id), None)
    if not transcript:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Transcript not found"
        )

    return {
        "id": transcript.id,
        "transcript_text": transcript.transcript_text,
        "transcript_json": transcript.transcript_json,
        "language": transcript.language,
        "confidence_score": transcript.confidence_score,
        "word_count": transcript.word_count,
        "speaker_count": transcript.speaker_count,
        "speakers_identified": transcript.speakers_identified,
        "status": transcript.status,
        "created_at": transcript.created_at,
    }


@router.get("/{meeting_id}/summaries/{summary_id}")
async def get_meeting_summary(
    meeting_id: int,
    summary_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get full summary content"""
    meeting_service = MeetingService(db)
    meeting = meeting_service.get_meeting_by_id(meeting_id, current_user)

    summary = next((s for s in meeting.summaries if s.id == summary_id), None)
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Summary not found"
        )

    return {
        "id": summary.id,
        "summary_text": summary.summary_text,
        "key_points": summary.key_points,
        "action_items": summary.action_items,
        "sentiment_analysis": summary.sentiment_analysis,
        "ai_model": summary.ai_model,
        "confidence_score": summary.confidence_score,
        "is_final": summary.is_final,
        "reviewed_by": summary.reviewed_by,
        "reviewed_at": summary.reviewed_at,
        "status": summary.status,
        "created_at": summary.created_at,
    }
