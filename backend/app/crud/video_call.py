from typing import List, Optional
from datetime import datetime
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models.video_call import (
    VideoCall,
    CallParticipant,
    RecordingConsent,
    CallTranscription,
    TranscriptionSegment
)
from app.schemas.video_call import VideoCallCreate, VideoCallUpdate


class CRUDVideoCall(CRUDBase[VideoCall, VideoCallCreate, VideoCallUpdate]):
    async def create_with_interviewer(
        self, db: AsyncSession, *, obj_in: VideoCallCreate, interviewer_id: int
    ) -> VideoCall:
        """Create a new video call with the interviewer ID."""
        db_obj = VideoCall(
            **obj_in.model_dump(),
            interviewer_id=interviewer_id,
            room_id=self._generate_room_id()
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_by_room_id(self, db: AsyncSession, *, room_id: str) -> Optional[VideoCall]:
        """Get video call by room ID."""
        result = await db.execute(
            select(VideoCall).where(VideoCall.room_id == room_id)
        )
        return result.scalar_one_or_none()

    async def get_by_interview_id(self, db: AsyncSession, *, interview_id: int) -> Optional[VideoCall]:
        """Get video call by interview ID."""
        result = await db.execute(
            select(VideoCall)
            .where(VideoCall.interview_id == interview_id)
            .order_by(VideoCall.created_at.desc())
        )
        return result.scalars().first()

    async def get_user_video_calls(
        self, db: AsyncSession, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[VideoCall]:
        """Get video calls for a specific user (as interviewer or candidate)."""
        result = await db.execute(
            select(VideoCall)
            .where(
                (VideoCall.interviewer_id == user_id) | 
                (VideoCall.candidate_id == user_id)
            )
            .order_by(VideoCall.scheduled_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_upcoming_calls(
        self, db: AsyncSession, *, user_id: int, from_datetime: datetime
    ) -> List[VideoCall]:
        """Get upcoming video calls for a user."""
        result = await db.execute(
            select(VideoCall)
            .where(
                and_(
                    (VideoCall.interviewer_id == user_id) | 
                    (VideoCall.candidate_id == user_id),
                    VideoCall.scheduled_at >= from_datetime,
                    VideoCall.status.in_(["scheduled", "in_progress"])
                )
            )
            .order_by(VideoCall.scheduled_at.asc())
        )
        return result.scalars().all()

    async def update_call_status(
        self, db: AsyncSession, *, db_obj: VideoCall, status: str, **kwargs
    ) -> VideoCall:
        """Update video call status with additional fields."""
        update_data = {"status": status, **kwargs}
        return await self.update(db, db_obj=db_obj, obj_in=update_data)

    async def add_participant(
        self, db: AsyncSession, *, video_call_id: int, user_id: int, device_info: Optional[dict] = None
    ) -> CallParticipant:
        """Add a participant to the video call or return existing participant."""
        # Check if participant already exists
        result = await db.execute(
            select(CallParticipant).where(
                and_(
                    CallParticipant.video_call_id == video_call_id,
                    CallParticipant.user_id == user_id
                )
            )
        )
        existing_participant = result.scalar_one_or_none()

        if existing_participant:
            # Update joined_at time and device_info for existing participant
            existing_participant.joined_at = datetime.utcnow()
            if device_info:
                existing_participant.device_info = device_info
            # Clear left_at if they're rejoining
            existing_participant.left_at = None
            await db.commit()
            await db.refresh(existing_participant)
            return existing_participant

        # Create new participant
        participant = CallParticipant(
            video_call_id=video_call_id,
            user_id=user_id,
            joined_at=datetime.utcnow(),
            device_info=device_info
        )
        db.add(participant)
        await db.commit()
        await db.refresh(participant)
        return participant

    async def update_participant_left(
        self, db: AsyncSession, *, video_call_id: int, user_id: int
    ) -> Optional[CallParticipant]:
        """Update participant left time."""
        result = await db.execute(
            select(CallParticipant).where(
                and_(
                    CallParticipant.video_call_id == video_call_id,
                    CallParticipant.user_id == user_id
                )
            )
        )
        participant = result.scalar_one_or_none()
        if participant:
            participant.left_at = datetime.utcnow()
            await db.commit()
            await db.refresh(participant)
        return participant

    async def save_recording_consent(
        self, db: AsyncSession, *, video_call_id: int, user_id: int, consented: bool
    ) -> RecordingConsent:
        """Save user's recording consent."""
        # Check if consent already exists
        result = await db.execute(
            select(RecordingConsent).where(
                and_(
                    RecordingConsent.video_call_id == video_call_id,
                    RecordingConsent.user_id == user_id
                )
            )
        )
        consent = result.scalar_one_or_none()
        
        if consent:
            consent.consented = consented
            consent.consented_at = datetime.utcnow() if consented else None
        else:
            consent = RecordingConsent(
                video_call_id=video_call_id,
                user_id=user_id,
                consented=consented,
                consented_at=datetime.utcnow() if consented else None
            )
            db.add(consent)
        
        await db.commit()
        await db.refresh(consent)
        return consent

    async def get_call_consents(
        self, db: AsyncSession, *, video_call_id: int
    ) -> List[RecordingConsent]:
        """Get all recording consents for a video call."""
        result = await db.execute(
            select(RecordingConsent)
            .where(RecordingConsent.video_call_id == video_call_id)
            .options(selectinload(RecordingConsent.user))
        )
        return result.scalars().all()

    async def save_transcription_segment(
        self, db: AsyncSession, *, video_call_id: int, segment_data: dict
    ) -> TranscriptionSegment:
        """Save a real-time transcription segment."""
        segment = TranscriptionSegment(
            video_call_id=video_call_id,
            **segment_data
        )
        db.add(segment)
        await db.commit()
        await db.refresh(segment)
        return segment

    async def get_call_transcription(
        self, db: AsyncSession, *, video_call_id: int
    ) -> Optional[CallTranscription]:
        """Get transcription for a video call."""
        result = await db.execute(
            select(CallTranscription)
            .where(CallTranscription.video_call_id == video_call_id)
            .options(selectinload(CallTranscription.video_call))
        )
        return result.scalar_one_or_none()

    async def update_transcription_status(
        self, db: AsyncSession, *, video_call_id: int, status: str, **kwargs
    ) -> Optional[CallTranscription]:
        """Update transcription processing status."""
        result = await db.execute(
            select(CallTranscription).where(
                CallTranscription.video_call_id == video_call_id
            )
        )
        transcription = result.scalar_one_or_none()
        
        if not transcription:
            transcription = CallTranscription(
                video_call_id=video_call_id,
                processing_status=status,
                **kwargs
            )
            db.add(transcription)
        else:
            transcription.processing_status = status
            for key, value in kwargs.items():
                setattr(transcription, key, value)
        
        await db.commit()
        await db.refresh(transcription)
        return transcription

    async def get_active_participants(
        self, db: AsyncSession, *, video_call_id: int
    ) -> List[CallParticipant]:
        """Get active participants (those who haven't left yet)."""
        result = await db.execute(
            select(CallParticipant)
            .where(
                and_(
                    CallParticipant.video_call_id == video_call_id,
                    CallParticipant.left_at.is_(None)
                )
            )
        )
        return result.scalars().all()

    async def end_all_participants(
        self, db: AsyncSession, *, video_call_id: int
    ) -> None:
        """Mark all participants as having left the call."""
        active_participants = await self.get_active_participants(db, video_call_id=video_call_id)

        current_time = datetime.utcnow()
        for participant in active_participants:
            participant.left_at = current_time

        await db.commit()

    def _generate_room_id(self) -> str:
        """Generate a human-readable room ID for the video call."""
        import random
        import string

        # Generate a Google Meet style room code: xxx-yyyy-zzz
        def generate_segment(length: int) -> str:
            return ''.join(random.choices(string.ascii_lowercase, k=length))

        # Create three segments separated by dashes
        segment1 = generate_segment(3)
        segment2 = generate_segment(4)
        segment3 = generate_segment(3)

        return f"{segment1}-{segment2}-{segment3}"


video_call = CRUDVideoCall(VideoCall)