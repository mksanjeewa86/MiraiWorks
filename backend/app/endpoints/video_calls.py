from typing import List
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.crud.user import user as user_crud
from app.schemas.video_call import (
    VideoCallCreate,
    VideoCallUpdate,
    VideoCallInfo,
    VideoCallToken,
    RecordingConsentRequest,
    RecordingConsentInfo,
    TranscriptionSegmentCreate,
    TranscriptionSegmentInfo,
    CallTranscriptionInfo,
)
from app.database import get_db
from app.dependencies import get_current_active_user
from app.models.user import User
from app.services.video_service import video_service
from app.services.permission_service import permission_service
from app.services.video_notification_service import video_notification_service

router = APIRouter(prefix="/video-calls", tags=["video-calls"])


@router.post("/schedule", response_model=VideoCallInfo)
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
    if video_call.status == "scheduled":
        await crud.video_call.update_call_status(
            db, db_obj=video_call, status="in_progress", started_at=datetime.now(timezone.utc)
        )
    
    # Add participant
    await crud.video_call.add_participant(
        db, video_call_id=call_id, user_id=current_user.id
    )
    
    return {"message": "Successfully joined the video call", "room_id": video_call.room_id}


@router.post("/{call_id}/end", response_model=VideoCallInfo)
async def end_video_call(
    call_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """End a video call."""
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
            detail="Only the interviewer can end the video call"
        )
    
    # Update participant left time
    await crud.video_call.update_participant_left(
        db, video_call_id=call_id, user_id=current_user.id
    )
    
    # Update call status
    video_call = await crud.video_call.update_call_status(
        db, db_obj=video_call, status="completed", ended_at=datetime.now(timezone.utc)
    )
    
    return video_call


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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transcript not available for this call"
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


@router.get("/", response_model=List[VideoCallInfo])
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