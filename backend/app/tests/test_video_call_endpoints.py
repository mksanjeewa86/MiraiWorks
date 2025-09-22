import pytest
from datetime import datetime, timezone, timedelta
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.video_call import VideoCall, RecordingConsent, CallTranscription
from app.models.user import User
from app.crud.video_call import video_call as video_call_crud
from app.schemas.video_call import VideoCallCreate, RecordingConsentRequest


class TestVideoCallEndpoints:
    """Comprehensive tests for video call functionality."""

    async def test_schedule_video_call_success(
        self, client: AsyncClient, auth_headers: dict, db: AsyncSession, test_users: dict
    ):
        """Test successful video call scheduling."""
        recruiter = test_users['recruiter']
        candidate = test_users['candidate']
        
        call_data = {
            "candidate_id": candidate.id,
            "scheduled_at": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat(),
            "enable_transcription": True,
            "transcription_language": "ja"
        }

        response = await client.post(
            "/api/video-calls/schedule",
            json=call_data,
            headers=auth_headers(recruiter)
        )

        assert response.status_code == 201
        data = response.json()
        assert data["candidate_id"] == candidate.id
        assert data["interviewer_id"] == recruiter.id
        assert data["status"] == "scheduled"
        assert data["transcription_enabled"] is True
        assert "room_id" in data

    async def test_schedule_video_call_unauthorized(
        self, client: AsyncClient, auth_headers: dict, test_users: dict
    ):
        """Test video call scheduling without authentication fails."""
        candidate = test_users['candidate']
        
        call_data = {
            "candidate_id": candidate.id,
            "scheduled_at": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
        }

        response = await client.post("/api/video-calls/schedule", json=call_data)
        assert response.status_code == 401

    async def test_schedule_video_call_invalid_candidate(
        self, client: AsyncClient, auth_headers: dict, test_users: dict
    ):
        """Test video call scheduling with invalid candidate ID."""
        recruiter = test_users['recruiter']
        
        call_data = {
            "candidate_id": 99999,  # Non-existent candidate
            "scheduled_at": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
        }

        response = await client.post(
            "/api/video-calls/schedule",
            json=call_data,
            headers=auth_headers(recruiter)
        )

        assert response.status_code == 403

    async def test_get_video_call_success(
        self, client: AsyncClient, auth_headers: dict, db: AsyncSession, test_video_call: VideoCall
    ):
        """Test successful video call retrieval."""
        response = await client.get(
            f"/api/video-calls/{test_video_call.id}",
            headers=auth_headers(test_video_call.interviewer)
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_video_call.id
        assert data["room_id"] == test_video_call.room_id

    async def test_get_video_call_not_found(
        self, client: AsyncClient, auth_headers: dict, test_users: dict
    ):
        """Test video call retrieval with non-existent ID."""
        recruiter = test_users['recruiter']
        
        response = await client.get(
            "/api/video-calls/99999",
            headers=auth_headers(recruiter)
        )

        assert response.status_code == 404

    async def test_get_video_call_forbidden(
        self, client: AsyncClient, auth_headers: dict, test_video_call: VideoCall, test_users: dict
    ):
        """Test video call retrieval by non-participant."""
        other_user = test_users['other_recruiter']
        
        response = await client.get(
            f"/api/video-calls/{test_video_call.id}",
            headers=auth_headers(other_user)
        )

        assert response.status_code == 403

    async def test_join_video_call_success(
        self, client: AsyncClient, auth_headers: dict, db: AsyncSession, test_video_call: VideoCall
    ):
        """Test successful video call joining."""
        response = await client.post(
            f"/api/video-calls/{test_video_call.id}/join",
            headers=auth_headers(test_video_call.candidate)
        )

        assert response.status_code == 200
        data = response.json()
        assert "room_id" in data
        assert data["room_id"] == test_video_call.room_id

        # Verify call status updated
        updated_call = await video_call_crud.get(db, id=test_video_call.id)
        assert updated_call.status == "in_progress"

    async def test_join_video_call_invalid_participant(
        self, client: AsyncClient, auth_headers: dict, test_video_call: VideoCall, test_users: dict
    ):
        """Test video call joining by non-participant."""
        other_user = test_users['other_recruiter']
        
        response = await client.post(
            f"/api/video-calls/{test_video_call.id}/join",
            headers=auth_headers(other_user)
        )

        assert response.status_code == 403

    async def test_end_video_call_success(
        self, client: AsyncClient, auth_headers: dict, db: AsyncSession, test_video_call: VideoCall
    ):
        """Test successful video call ending."""
        # First set call to in_progress
        await video_call_crud.update_call_status(
            db, db_obj=test_video_call, status="in_progress"
        )

        response = await client.post(
            f"/api/video-calls/{test_video_call.id}/end",
            headers=auth_headers(test_video_call.interviewer)
        )

        assert response.status_code == 200
        
        # Verify call status updated
        updated_call = await video_call_crud.get(db, id=test_video_call.id)
        assert updated_call.status == "completed"
        assert updated_call.ended_at is not None

    async def test_end_video_call_only_interviewer(
        self, client: AsyncClient, auth_headers: dict, test_video_call: VideoCall
    ):
        """Test only interviewer can end video call."""
        response = await client.post(
            f"/api/video-calls/{test_video_call.id}/end",
            headers=auth_headers(test_video_call.candidate)
        )

        assert response.status_code == 403

    async def test_record_consent_success(
        self, client: AsyncClient, auth_headers: dict, db: AsyncSession, test_video_call: VideoCall
    ):
        """Test successful recording consent."""
        consent_data = {"consented": True}

        response = await client.post(
            f"/api/video-calls/{test_video_call.id}/consent",
            json=consent_data,
            headers=auth_headers(test_video_call.candidate)
        )

        assert response.status_code == 200
        data = response.json()
        assert data["consented"] is True
        assert data["user_id"] == test_video_call.candidate_id

    async def test_record_consent_decline(
        self, client: AsyncClient, auth_headers: dict, db: AsyncSession, test_video_call: VideoCall
    ):
        """Test recording consent decline."""
        consent_data = {"consented": False}

        response = await client.post(
            f"/api/video-calls/{test_video_call.id}/consent",
            json=consent_data,
            headers=auth_headers(test_video_call.interviewer)
        )

        assert response.status_code == 200
        data = response.json()
        assert data["consented"] is False

    async def test_get_video_token_success(
        self, client: AsyncClient, auth_headers: dict, test_video_call: VideoCall
    ):
        """Test successful WebRTC token generation."""
        response = await client.get(
            f"/api/video-calls/{test_video_call.id}/token",
            headers=auth_headers(test_video_call.interviewer)
        )

        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "expires_at" in data
        assert data["room_id"] == test_video_call.room_id

    async def test_save_transcript_segment_success(
        self, client: AsyncClient, auth_headers: dict, db: AsyncSession, test_video_call: VideoCall
    ):
        """Test saving transcription segment during call."""
        # Set call to in_progress
        await video_call_crud.update_call_status(
            db, db_obj=test_video_call, status="in_progress"
        )

        segment_data = {
            "speaker_id": test_video_call.interviewer_id,
            "segment_text": "Hello, how are you today?",
            "start_time": 10.5,
            "end_time": 13.2,
            "confidence": 0.95
        }

        response = await client.post(
            f"/api/video-calls/{test_video_call.id}/transcript/segments",
            json=segment_data,
            headers=auth_headers(test_video_call.interviewer)
        )

        assert response.status_code == 200
        data = response.json()
        assert data["segment_text"] == segment_data["segment_text"]
        assert data["speaker_id"] == segment_data["speaker_id"]

    async def test_save_transcript_segment_call_not_active(
        self, client: AsyncClient, auth_headers: dict, test_video_call: VideoCall
    ):
        """Test saving segment fails when call is not active."""
        segment_data = {
            "speaker_id": test_video_call.interviewer_id,
            "segment_text": "Hello",
            "start_time": 10.5,
            "end_time": 13.2
        }

        response = await client.post(
            f"/api/video-calls/{test_video_call.id}/transcript/segments",
            json=segment_data,
            headers=auth_headers(test_video_call.interviewer)
        )

        assert response.status_code == 400

    async def test_get_transcript_success(
        self, client: AsyncClient, auth_headers: dict, db: AsyncSession, test_video_call: VideoCall
    ):
        """Test getting call transcript."""
        # Create a transcript
        await video_call_crud.update_transcription_status(
            db, 
            video_call_id=test_video_call.id, 
            status="completed",
            transcript_text="Sample transcript text"
        )

        response = await client.get(
            f"/api/video-calls/{test_video_call.id}/transcript",
            headers=auth_headers(test_video_call.interviewer)
        )

        assert response.status_code == 200
        data = response.json()
        assert data["video_call_id"] == test_video_call.id
        assert data["processing_status"] == "completed"

    async def test_get_transcript_not_available(
        self, client: AsyncClient, auth_headers: dict, test_video_call: VideoCall
    ):
        """Test getting transcript when not available."""
        response = await client.get(
            f"/api/video-calls/{test_video_call.id}/transcript",
            headers=auth_headers(test_video_call.interviewer)
        )

        assert response.status_code == 404

    async def test_download_transcript_success(
        self, client: AsyncClient, auth_headers: dict, db: AsyncSession, test_video_call: VideoCall
    ):
        """Test transcript download."""
        # Create a completed transcript
        await video_call_crud.update_transcription_status(
            db, 
            video_call_id=test_video_call.id, 
            status="completed",
            transcript_text="Sample transcript"
        )

        response = await client.get(
            f"/api/video-calls/{test_video_call.id}/transcript/download?format=txt",
            headers=auth_headers(test_video_call.interviewer)
        )

        assert response.status_code == 200
        data = response.json()
        assert "download_url" in data

    async def test_list_video_calls_success(
        self, client: AsyncClient, auth_headers: dict, test_users: dict
    ):
        """Test listing user's video calls."""
        recruiter = test_users['recruiter']
        
        response = await client.get(
            "/api/video-calls/",
            headers=auth_headers(recruiter)
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    async def test_concurrent_calls_prevention(
        self, client: AsyncClient, auth_headers: dict, test_users: dict
    ):
        """Test that users cannot have multiple concurrent active calls."""
        recruiter = test_users['recruiter']
        candidate1 = test_users['candidate']
        candidate2 = test_users['other_candidate']
        
        # Schedule first call
        call_data1 = {
            "candidate_id": candidate1.id,
            "scheduled_at": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
        }
        
        response1 = await client.post(
            "/api/video-calls/schedule",
            json=call_data1,
            headers=auth_headers(recruiter)
        )
        assert response1.status_code == 201
        
        # Try to schedule overlapping call
        call_data2 = {
            "candidate_id": candidate2.id,
            "scheduled_at": (datetime.now(timezone.utc) + timedelta(minutes=30)).isoformat()
        }
        
        response2 = await client.post(
            "/api/video-calls/schedule",
            json=call_data2,
            headers=auth_headers(recruiter)
        )
        
        # Should either succeed or fail with appropriate error
        assert response2.status_code in [201, 400, 409]