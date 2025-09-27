from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.crud.user import user as user_crud
from app.database import get_db
from app.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.video_call import (
    CallTranscriptionInfo,
    RecordingConsentInfo,
    RecordingConsentRequest,
    TranscriptionSegmentCreate,
    TranscriptionSegmentInfo,
    TranscriptionStatus,
    VideoCallCreate,
    VideoCallInfo,
    VideoCallToken,
)
from app.services.permission_service import permission_service
from app.services.video_notification_service import video_notification_service
from app.services.video_service import video_service

router = APIRouter(prefix="/video-calls", tags=["video-calls"])


@router.post("/schedule", response_model=VideoCallInfo, status_code=status.HTTP_201_CREATED)
async def schedule_video_call(
    call_data: VideoCallCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Schedule a new video call for an interview."""
    # Check permissions
    if not await permission_service.can_schedule_interview(db, current_user, call_data.candidate_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to schedule interviews with this candidate"
        )

    # Create video call
    video_call = await crud.video_call.create_with_interviewer(
        db, obj_in=call_data, interviewer_id=current_user.id
    )

    # Get participant details for notifications
    candidate = await user_crud.get(db, id=call_data.candidate_id)
    if candidate:
        # Send email notifications
        await video_notification_service.send_interview_scheduled_notification(
            db, video_call, current_user, candidate
        )

    return video_call


@router.get("/room/{room_id}", response_model=VideoCallInfo)
async def get_video_call_by_room(
    room_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get video call details by room ID (human-readable code)."""
    video_call = await crud.video_call.get_by_room_id(db, room_id=room_id)

    if not video_call:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video call room not found"
        )

    # Check if user is participant
    if video_call.interviewer_id != current_user.id and video_call.candidate_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this video call"
        )

    return video_call


@router.get("/{call_id}", response_model=VideoCallInfo)
async def get_video_call(
    call_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get video call details."""
    video_call = await crud.video_call.get(db, id=call_id)

    if not video_call:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video call not found"
        )

    # Check if user is participant
    if video_call.interviewer_id != current_user.id and video_call.candidate_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this video call"
        )

    return video_call


@router.post("/room/{room_id}/join", response_model=dict)
async def join_video_call_by_room(
    room_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Join a video call by room ID (human-readable code)."""
    video_call = await crud.video_call.get_by_room_id(db, room_id=room_id)

    if not video_call:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video call room not found"
        )

    # Check if user is participant
    if video_call.interviewer_id != current_user.id and video_call.candidate_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a participant in this video call"
        )

    # Update call status to in_progress if it's the first participant
    if video_call.status == "scheduled":
        await crud.video_call.update_call_status(
            db, db_obj=video_call, status="in_progress", started_at=datetime.now(UTC)
        )

    # Add participant
    await crud.video_call.add_participant(
        db, video_call_id=video_call.id, user_id=current_user.id
    )

    return {"message": "Successfully joined the video call", "room_id": video_call.room_id}


@router.post("/{call_id}/join", response_model=dict)
async def join_video_call(
    call_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Join a video call."""
    video_call = await crud.video_call.get(db, id=call_id)

    if not video_call:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video call not found"
        )

    # Check if user is participant
    if video_call.interviewer_id != current_user.id and video_call.candidate_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a participant in this video call"
        )

    # Update call status to in_progress if it's the first participant
    print(f"DEBUG: Video call status before check: {video_call.status}")
    if video_call.status == "scheduled":
        print("DEBUG: Updating video call status to in_progress")
        await crud.video_call.update_call_status(
            db, db_obj=video_call, status="in_progress", started_at=datetime.now(UTC)
        )
        print(f"DEBUG: Video call status after update: {video_call.status}")
    else:
        print("DEBUG: Video call status is not 'scheduled', no update needed")

    # Add participant
    await crud.video_call.add_participant(
        db, video_call_id=call_id, user_id=current_user.id
    )

    return {"message": "Successfully joined the video call", "room_id": video_call.room_id}


@router.post("/room/{room_id}/leave", response_model=dict)
async def leave_video_call_by_room(
    room_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Leave a video call by room ID - any participant can leave."""
    video_call = await crud.video_call.get_by_room_id(db, room_id=room_id)

    if not video_call:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video call room not found"
        )

    # Check if user is participant
    if video_call.interviewer_id != current_user.id and video_call.candidate_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a participant in this video call"
        )

    # Update participant left time
    await crud.video_call.update_participant_left(
        db, video_call_id=video_call.id, user_id=current_user.id
    )

    # Check if this was the last participant
    active_participants = await crud.video_call.get_active_participants(db, video_call_id=video_call.id)

    if len(active_participants) == 0:
        # Last participant left, end the call
        video_call = await crud.video_call.update_call_status(
            db, db_obj=video_call, status="completed", ended_at=datetime.now(UTC)
        )
        return {"message": "Left call and ended session (last participant)", "call_ended": True}

    return {"message": "Successfully left the video call", "call_ended": False}


@router.post("/{call_id}/leave", response_model=dict)
async def leave_video_call(
    call_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Leave a video call - any participant can leave."""
    video_call = await crud.video_call.get(db, id=call_id)

    if not video_call:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video call not found"
        )

    # Check if user is participant
    if video_call.interviewer_id != current_user.id and video_call.candidate_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a participant in this video call"
        )

    # Update participant left time
    await crud.video_call.update_participant_left(
        db, video_call_id=call_id, user_id=current_user.id
    )

    # Check if this was the last participant
    active_participants = await crud.video_call.get_active_participants(db, video_call_id=call_id)

    if len(active_participants) == 0:
        # Last participant left, end the call
        video_call = await crud.video_call.update_call_status(
            db, db_obj=video_call, status="completed", ended_at=datetime.now(UTC)
        )
        return {"message": "Left call and ended session (last participant)", "call_ended": True}

    return {"message": "Successfully left the video call", "call_ended": False}


@router.post("/{call_id}/end", response_model=VideoCallInfo)
async def end_video_call(
    call_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """End a video call - only interviewer can force end."""
    video_call = await crud.video_call.get(db, id=call_id)

    if not video_call:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video call not found"
        )

    # Check if user is the interviewer
    if video_call.interviewer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the interviewer can force end the video call"
        )

    # Update all participants left time
    await crud.video_call.end_all_participants(db, video_call_id=call_id)

    # Update call status
    video_call = await crud.video_call.update_call_status(
        db, db_obj=video_call, status="completed", ended_at=datetime.now(UTC)
    )

    return video_call


@router.post("/room/{room_id}/consent", response_model=RecordingConsentInfo)
async def record_consent_by_room(
    room_id: str,
    consent_data: RecordingConsentRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Record user's consent for call recording by room ID."""
    video_call = await crud.video_call.get_by_room_id(db, room_id=room_id)

    if not video_call:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video call room not found"
        )

    # Check if user is participant
    if video_call.interviewer_id != current_user.id and video_call.candidate_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a participant in this video call"
        )

    consent = await crud.video_call.save_recording_consent(
        db, video_call_id=video_call.id, user_id=current_user.id, consented=consent_data.consented
    )

    return consent


@router.post("/{call_id}/consent", response_model=RecordingConsentInfo)
async def record_consent(
    call_id: int,
    consent_data: RecordingConsentRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Record user's consent for call recording."""
    video_call = await crud.video_call.get(db, id=call_id)

    if not video_call:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video call not found"
        )

    # Check if user is participant
    if video_call.interviewer_id != current_user.id and video_call.candidate_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a participant in this video call"
        )

    consent = await crud.video_call.save_recording_consent(
        db, video_call_id=call_id, user_id=current_user.id, consented=consent_data.consented
    )

    return consent


@router.get("/{call_id}/token", response_model=VideoCallToken)
async def get_video_token(
    call_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get WebRTC token for joining the video call."""
    video_call = await crud.video_call.get(db, id=call_id)

    if not video_call:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video call not found"
        )

    # Check if user is participant
    if video_call.interviewer_id != current_user.id and video_call.candidate_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a participant in this video call"
        )

    # Generate token using video service
    token_data = await video_service.generate_token(
        room_id=video_call.room_id,
        user_id=current_user.id,
        user_name=current_user.full_name or current_user.email
    )

    return token_data


@router.get("/{call_id}/transcript", response_model=CallTranscriptionInfo)
async def get_call_transcript(
    call_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get transcript for a completed video call."""
    video_call = await crud.video_call.get(db, id=call_id)

    if not video_call:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video call not found"
        )

    # Check if user is participant
    if video_call.interviewer_id != current_user.id and video_call.candidate_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this transcript"
        )

    transcript = await crud.video_call.get_call_transcription(db, video_call_id=call_id)

    if not transcript:
        # Return empty transcript for calls that haven't started transcription yet
        from datetime import datetime
        return CallTranscriptionInfo(
            id=0,
            video_call_id=call_id,
            transcript_url=None,
            transcript_text=None,
            language=video_call.transcription_language,
            processing_status=TranscriptionStatus.PENDING,
            word_count=0,
            created_at=datetime.now(UTC),
            processed_at=None,
            segments=[]
        )

    return transcript


@router.post("/{call_id}/transcript/segments", response_model=TranscriptionSegmentInfo)
async def save_transcript_segment(
    call_id: int,
    segment: TranscriptionSegmentCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Save a real-time transcription segment during the call."""
    video_call = await crud.video_call.get(db, id=call_id)

    if not video_call:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video call not found"
        )

    # Check if user is participant
    if video_call.interviewer_id != current_user.id and video_call.candidate_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a participant in this video call"
        )

    # Check if call is in progress
    if video_call.status != "in_progress":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only save segments during an active call"
        )

    saved_segment = await crud.video_call.save_transcription_segment(
        db, video_call_id=call_id, segment_data=segment.model_dump()
    )

    return saved_segment


@router.get("/{call_id}/transcript/download")
async def download_transcript(
    call_id: int,
    format: str = "txt",
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Download transcript in specified format (txt, pdf, srt)."""
    video_call = await crud.video_call.get(db, id=call_id)

    if not video_call:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video call not found"
        )

    # Check if user is participant
    if video_call.interviewer_id != current_user.id and video_call.candidate_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to download this transcript"
        )

    transcript = await crud.video_call.get_call_transcription(db, video_call_id=call_id)

    if not transcript or transcript.processing_status != "completed":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transcript not available for download"
        )

    # Generate download URL using transcription service
    download_url = await video_service.generate_transcript_download(
        transcript_id=transcript.id,
        format=format
    )

    return {"download_url": download_url}


@router.get("/", response_model=list[VideoCallInfo])
async def list_video_calls(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """List video calls for the current user."""
    video_calls = await crud.video_call.get_user_video_calls(
        db, user_id=current_user.id, skip=skip, limit=limit
    )
    return video_calls
