from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.video_call import video_call as video_call_crud
from app.models.video_call import VideoCall
from app.schemas.video_call import VideoCallCreate


class TestVideoCallCRUD:
    """Unit tests for video call CRUD operations."""

    @pytest.mark.asyncio
    async def test_create_video_call(self, db_session: AsyncSession, test_users: dict):
        """Test creating a video call."""
        recruiter = test_users["recruiter"]
        candidate = test_users["candidate"]

        call_data = VideoCallCreate(
            candidate_id=candidate.id,
            scheduled_at=datetime.now(UTC) + timedelta(hours=1),
            enable_transcription=True,
            transcription_language="ja",
        )

        video_call = await video_call_crud.create_with_interviewer(
            db_session, obj_in=call_data, interviewer_id=recruiter.id
        )

        assert video_call.id is not None
        assert video_call.interviewer_id == recruiter.id
        assert video_call.candidate_id == candidate.id
        assert video_call.status == "scheduled"
        assert video_call.transcription_enabled is True
        assert video_call.room_id is not None

    @pytest.mark.asyncio
    async def test_get_video_call_by_room_id(
        self, db_session: AsyncSession, test_video_call: VideoCall
    ):
        """Test getting video call by room ID."""
        result = await video_call_crud.get_by_room_id(
            db_session, room_id=test_video_call.room_id
        )

        assert result is not None
        assert result.id == test_video_call.id
        assert result.room_id == test_video_call.room_id

    @pytest.mark.asyncio
    async def test_get_video_call_by_interview_id(
        self, db_session: AsyncSession, test_video_call: VideoCall
    ):
        """Test getting video call by interview ID."""
        if test_video_call.interview_id:
            result = await video_call_crud.get_by_interview_id(
                db_session, interview_id=test_video_call.interview_id
            )
            assert result is not None
            assert result.id == test_video_call.id

    @pytest.mark.asyncio
    async def test_get_user_video_calls(
        self, db_session: AsyncSession, test_video_call: VideoCall
    ):
        """Test getting video calls for a user."""
        # Get calls for interviewer
        interviewer_calls = await video_call_crud.get_user_video_calls(
            db_session, user_id=test_video_call.interviewer_id
        )
        assert len(interviewer_calls) >= 1
        assert any(call.id == test_video_call.id for call in interviewer_calls)

        # Get calls for candidate
        candidate_calls = await video_call_crud.get_user_video_calls(
            db_session, user_id=test_video_call.candidate_id
        )
        assert len(candidate_calls) >= 1
        assert any(call.id == test_video_call.id for call in candidate_calls)

    @pytest.mark.asyncio
    async def test_get_upcoming_calls(self, db_session: AsyncSession, test_users: dict):
        """Test getting upcoming video calls."""
        recruiter = test_users["recruiter"]

        # Create a future call
        future_time = datetime.now(UTC) + timedelta(hours=2)
        call_data = VideoCallCreate(
            candidate_id=test_users["candidate"].id, scheduled_at=future_time
        )

        future_call = await video_call_crud.create_with_interviewer(
            db_session, obj_in=call_data, interviewer_id=recruiter.id
        )

        # Get upcoming calls
        upcoming = await video_call_crud.get_upcoming_calls(
            db_session, user_id=recruiter.id, from_datetime=datetime.now(UTC)
        )

        assert len(upcoming) >= 1
        assert any(call.id == future_call.id for call in upcoming)

    @pytest.mark.asyncio
    async def test_update_call_status(
        self, db_session: AsyncSession, test_video_call: VideoCall
    ):
        """Test updating video call status."""
        start_time = datetime.now(UTC)

        updated_call = await video_call_crud.update_call_status(
            db_session,
            db_obj=test_video_call,
            status="in_progress",
            started_at=start_time,
        )

        assert updated_call.status == "in_progress"
        # Compare without timezone since database stores timezone-naive datetime
        assert updated_call.started_at.replace(tzinfo=UTC) == start_time

    @pytest.mark.asyncio
    async def test_add_participant(
        self, db_session: AsyncSession, test_video_call: VideoCall
    ):
        """Test adding a participant to video call."""
        device_info = {"browser": "Chrome", "version": "91.0"}

        participant = await video_call_crud.add_participant(
            db_session,
            video_call_id=test_video_call.id,
            user_id=test_video_call.candidate_id,
            device_info=device_info,
        )

        assert participant.video_call_id == test_video_call.id
        assert participant.user_id == test_video_call.candidate_id
        assert participant.device_info == device_info
        assert participant.joined_at is not None

    @pytest.mark.asyncio
    async def test_update_participant_left(
        self, db_session: AsyncSession, test_video_call: VideoCall
    ):
        """Test updating participant left time."""
        # First add participant
        await video_call_crud.add_participant(
            db_session,
            video_call_id=test_video_call.id,
            user_id=test_video_call.interviewer_id,
        )

        # Update left time
        updated_participant = await video_call_crud.update_participant_left(
            db_session,
            video_call_id=test_video_call.id,
            user_id=test_video_call.interviewer_id,
        )

        assert updated_participant is not None
        assert updated_participant.left_at is not None

    @pytest.mark.asyncio
    async def test_save_recording_consent(
        self, db_session: AsyncSession, test_video_call: VideoCall
    ):
        """Test saving recording consent."""
        consent = await video_call_crud.save_recording_consent(
            db_session,
            video_call_id=test_video_call.id,
            user_id=test_video_call.candidate_id,
            consented=True,
        )

        assert consent.video_call_id == test_video_call.id
        assert consent.user_id == test_video_call.candidate_id
        assert consent.consented is True
        assert consent.consented_at is not None

    @pytest.mark.asyncio
    async def test_save_recording_consent_update(
        self, db_session: AsyncSession, test_video_call: VideoCall
    ):
        """Test updating existing recording consent."""
        # First consent
        await video_call_crud.save_recording_consent(
            db_session,
            video_call_id=test_video_call.id,
            user_id=test_video_call.interviewer_id,
            consented=True,
        )

        # Update consent
        updated_consent = await video_call_crud.save_recording_consent(
            db_session,
            video_call_id=test_video_call.id,
            user_id=test_video_call.interviewer_id,
            consented=False,
        )

        assert updated_consent.consented is False
        assert updated_consent.consented_at is None

    @pytest.mark.asyncio
    async def test_get_call_consents(
        self, db_session: AsyncSession, test_video_call: VideoCall
    ):
        """Test getting all consents for a video call."""
        # Add consents for both participants
        await video_call_crud.save_recording_consent(
            db_session,
            video_call_id=test_video_call.id,
            user_id=test_video_call.interviewer_id,
            consented=True,
        )
        await video_call_crud.save_recording_consent(
            db_session,
            video_call_id=test_video_call.id,
            user_id=test_video_call.candidate_id,
            consented=False,
        )

        consents = await video_call_crud.get_call_consents(
            db_session, video_call_id=test_video_call.id
        )

        assert len(consents) == 2
        consent_by_user = {c.user_id: c for c in consents}
        assert consent_by_user[test_video_call.interviewer_id].consented is True
        assert consent_by_user[test_video_call.candidate_id].consented is False

    @pytest.mark.asyncio
    async def test_save_transcription_segment(
        self, db_session: AsyncSession, test_video_call: VideoCall
    ):
        """Test saving a transcription segment."""
        segment_data = {
            "speaker_id": test_video_call.interviewer_id,
            "segment_text": "Hello, how are you today?",
            "start_time": 10.5,
            "end_time": 13.2,
            "confidence": 0.95,
        }

        segment = await video_call_crud.save_transcription_segment(
            db_session, video_call_id=test_video_call.id, segment_data=segment_data
        )

        assert segment.video_call_id == test_video_call.id
        assert segment.speaker_id == segment_data["speaker_id"]
        assert segment.segment_text == segment_data["segment_text"]
        assert segment.start_time == segment_data["start_time"]
        assert segment.end_time == segment_data["end_time"]
        assert segment.confidence == segment_data["confidence"]

    @pytest.mark.asyncio
    async def test_get_call_transcription(
        self, db_session: AsyncSession, test_video_call: VideoCall
    ):
        """Test getting call transcription."""
        # Create transcription
        await video_call_crud.update_transcription_status(
            db_session,
            video_call_id=test_video_call.id,
            status="completed",
            transcript_text="Sample transcript text",
            word_count=4,
        )

        transcription = await video_call_crud.get_call_transcription(
            db_session, video_call_id=test_video_call.id
        )

        assert transcription is not None
        assert transcription.video_call_id == test_video_call.id
        assert transcription.processing_status == "completed"
        assert transcription.transcript_text == "Sample transcript text"
        assert transcription.word_count == 4

    @pytest.mark.asyncio
    async def test_update_transcription_status(
        self, db_session: AsyncSession, test_video_call: VideoCall
    ):
        """Test updating transcription status."""
        # Create initial transcription
        transcription = await video_call_crud.update_transcription_status(
            db_session, video_call_id=test_video_call.id, status="processing"
        )

        assert transcription.processing_status == "processing"

        # Update to completed
        updated = await video_call_crud.update_transcription_status(
            db_session,
            video_call_id=test_video_call.id,
            status="completed",
            transcript_text="Final transcript",
            processed_at=datetime.now(UTC),
        )

        assert updated.processing_status == "completed"
        assert updated.transcript_text == "Final transcript"
        assert updated.processed_at is not None

    @pytest.mark.asyncio
    async def test_concurrent_call_limit(
        self, db_session: AsyncSession, test_users: dict
    ):
        """Test concurrent call creation for same user."""
        recruiter = test_users["recruiter"]
        candidate1 = test_users["candidate"]
        candidate2 = test_users["other_candidate"]

        # Create first call
        call_data1 = VideoCallCreate(
            candidate_id=candidate1.id,
            scheduled_at=datetime.now(UTC) + timedelta(hours=1),
        )

        call1 = await video_call_crud.create_with_interviewer(
            db_session, obj_in=call_data1, interviewer_id=recruiter.id
        )

        # Create overlapping call
        call_data2 = VideoCallCreate(
            candidate_id=candidate2.id,
            scheduled_at=datetime.now(UTC) + timedelta(minutes=30),
        )

        call2 = await video_call_crud.create_with_interviewer(
            db_session, obj_in=call_data2, interviewer_id=recruiter.id
        )

        # Both should be created successfully (business logic enforcement in endpoints)
        assert call1.id != call2.id
        assert call1.interviewer_id == call2.interviewer_id == recruiter.id
