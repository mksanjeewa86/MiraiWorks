from datetime import datetime, timedelta
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.calendar_integration import CalendarIntegration
from app.models.company import Company
from app.models.interview import Interview
from app.models.user import User
from app.schemas.interview import InterviewCreate, ProposalCreate, ProposalResponse
from app.services.interview_service import InterviewService
from app.utils.constants import InterviewStatus, ProposalStatus


class TestInterviewService:
    @pytest.fixture
    async def interview_service(self):
        return InterviewService()

    @pytest.fixture
    async def company(self, db_session: AsyncSession):
        company = Company(
            name="Test Company",
            domain="test.com",
            industry="Technology",
            size="10-50",
            is_active=True,
        )
        db_session.add(company)
        await db_session.commit()
        await db_session.refresh(company)
        return company

    @pytest.fixture
    async def candidate_user(self, db_session: AsyncSession, company):
        user = User(
            email="candidate@test.com",
            full_name="Test Candidate",
            password_hash="hashed_password",
            role="candidate",
            company_id=company.id,
            is_active=True,
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        return user

    @pytest.fixture
    async def recruiter_user(self, db_session: AsyncSession, company):
        user = User(
            email="recruiter@test.com",
            full_name="Test Recruiter",
            password_hash="hashed_password",
            role="recruiter",
            company_id=company.id,
            is_active=True,
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        return user

    @pytest.fixture
    async def employer_company(self, db_session: AsyncSession):
        company = Company(
            name="Employer Company",
            domain="employer.com",
            industry="Technology",
            size="100-500",
            is_active=True,
        )
        db_session.add(company)
        await db_session.commit()
        await db_session.refresh(company)
        return company

    @pytest.fixture
    async def interview(
        self, db_session: AsyncSession, candidate_user, recruiter_user, employer_company
    ):
        interview = Interview(
            candidate_id=candidate_user.id,
            recruiter_id=recruiter_user.id,
            employer_company_id=employer_company.id,
            title="Technical Interview",
            description="Python development role interview",
            position_title="Senior Python Developer",
            interview_type="video",
            status=InterviewStatus.PENDING_SCHEDULE.value,
            created_by=recruiter_user.id,
        )
        db_session.add(interview)
        await db_session.commit()
        await db_session.refresh(interview)
        return interview

    async def test_create_interview(
        self,
        db_session: AsyncSession,
        interview_service: InterviewService,
        candidate_user: User,
        recruiter_user: User,
        employer_company: Company,
    ):
        """Test creating a new interview."""
        interview_data = InterviewCreate(
            candidate_id=candidate_user.id,
            recruiter_id=recruiter_user.id,
            employer_company_id=employer_company.id,
            title="Backend Developer Interview",
            description="Technical interview for backend position",
            position_title="Backend Developer",
            interview_type="video",
        )

        interview = await interview_service.create_interview(
            db_session, interview_data, recruiter_user.id
        )

        assert interview.id is not None
        assert interview.title == "Backend Developer Interview"
        assert interview.candidate_id == candidate_user.id
        assert interview.recruiter_id == recruiter_user.id
        assert interview.status == InterviewStatus.PENDING_SCHEDULE.value
        assert interview.created_by == recruiter_user.id

    async def test_get_interview(
        self,
        db_session: AsyncSession,
        interview_service: InterviewService,
        interview: Interview,
    ):
        """Test getting interview details."""
        retrieved_interview = await interview_service.get_interview(
            db_session, interview.id
        )

        assert retrieved_interview.id == interview.id
        assert retrieved_interview.title == interview.title
        assert retrieved_interview.status == interview.status

    async def test_get_interview_not_found(
        self, db_session: AsyncSession, interview_service: InterviewService
    ):
        """Test getting non-existent interview."""
        interview = await interview_service.get_interview(db_session, 99999)
        assert interview is None

    async def test_create_proposal(
        self,
        db_session: AsyncSession,
        interview_service: InterviewService,
        interview: Interview,
        recruiter_user: User,
    ):
        """Test creating an interview time proposal."""
        proposal_data = ProposalCreate(
            start_datetime=datetime.utcnow() + timedelta(days=1),
            end_datetime=datetime.utcnow() + timedelta(days=1, hours=1),
            timezone="UTC",
            location="Video conference",
            notes="Initial proposal for technical interview",
        )

        proposal = await interview_service.create_proposal(
            db_session, interview.id, proposal_data, recruiter_user.id
        )

        assert proposal.id is not None
        assert proposal.interview_id == interview.id
        assert proposal.proposed_by == recruiter_user.id
        assert proposal.status == ProposalStatus.PENDING.value
        assert proposal.location == "Video conference"

    async def test_create_proposal_for_scheduled_interview(
        self,
        db_session: AsyncSession,
        interview_service: InterviewService,
        interview: Interview,
        recruiter_user: User,
    ):
        """Test creating proposal for already scheduled interview should fail."""
        # Mark interview as scheduled
        interview.status = InterviewStatus.SCHEDULED.value
        await interview.save(db_session)

        proposal_data = ProposalCreate(
            start_datetime=datetime.utcnow() + timedelta(days=1),
            end_datetime=datetime.utcnow() + timedelta(days=1, hours=1),
            timezone="UTC",
        )

        with pytest.raises(ValueError, match="Interview is already scheduled"):
            await interview_service.create_proposal(
                db_session, interview.id, proposal_data, recruiter_user.id
            )

    async def test_respond_to_proposal(
        self,
        db_session: AsyncSession,
        interview_service: InterviewService,
        interview: Interview,
        recruiter_user: User,
        candidate_user: User,
    ):
        """Test responding to an interview proposal."""
        # Create a proposal first
        proposal_data = ProposalCreate(
            start_datetime=datetime.utcnow() + timedelta(days=1),
            end_datetime=datetime.utcnow() + timedelta(days=1, hours=1),
            timezone="UTC",
        )

        proposal = await interview_service.create_proposal(
            db_session, interview.id, proposal_data, recruiter_user.id
        )

        # Respond to proposal
        response_data = ProposalResponse(
            response="accepted", notes="Looking forward to the interview"
        )

        updated_proposal = await interview_service.respond_to_proposal(
            db_session, proposal.id, response_data, candidate_user.id
        )

        assert updated_proposal.status == ProposalStatus.ACCEPTED.value
        assert updated_proposal.responded_by == candidate_user.id
        assert updated_proposal.response_notes == "Looking forward to the interview"
        assert updated_proposal.responded_at is not None

        # Check that interview is now scheduled
        await db_session.refresh(interview)
        assert interview.status == InterviewStatus.SCHEDULED.value
        assert interview.scheduled_start == proposal.start_datetime
        assert interview.scheduled_end == proposal.end_datetime

    async def test_respond_to_proposal_declined(
        self,
        db_session: AsyncSession,
        interview_service: InterviewService,
        interview: Interview,
        recruiter_user: User,
        candidate_user: User,
    ):
        """Test declining an interview proposal."""
        # Create a proposal
        proposal_data = ProposalCreate(
            start_datetime=datetime.utcnow() + timedelta(days=1),
            end_datetime=datetime.utcnow() + timedelta(days=1, hours=1),
            timezone="UTC",
        )

        proposal = await interview_service.create_proposal(
            db_session, interview.id, proposal_data, recruiter_user.id
        )

        # Decline proposal
        response_data = ProposalResponse(
            response="declined", notes="Time doesn't work for me"
        )

        updated_proposal = await interview_service.respond_to_proposal(
            db_session, proposal.id, response_data, candidate_user.id
        )

        assert updated_proposal.status == ProposalStatus.DECLINED.value
        assert updated_proposal.responded_by == candidate_user.id

        # Interview should still be pending schedule
        await db_session.refresh(interview)
        assert interview.status == InterviewStatus.PENDING_SCHEDULE.value

    async def test_cancel_interview(
        self,
        db_session: AsyncSession,
        interview_service: InterviewService,
        interview: Interview,
        recruiter_user: User,
    ):
        """Test cancelling an interview."""
        cancelled_interview = await interview_service.cancel_interview(
            db_session, interview.id, "Position filled", recruiter_user.id
        )

        assert cancelled_interview.status == InterviewStatus.CANCELLED.value
        assert cancelled_interview.cancellation_reason == "Position filled"
        assert cancelled_interview.cancelled_by == recruiter_user.id
        assert cancelled_interview.cancelled_at is not None

    async def test_reschedule_interview(
        self,
        db_session: AsyncSession,
        interview_service: InterviewService,
        interview: Interview,
        recruiter_user: User,
    ):
        """Test rescheduling an interview."""
        # First schedule the interview
        interview.status = InterviewStatus.SCHEDULED.value
        interview.scheduled_start = datetime.utcnow() + timedelta(days=1)
        interview.scheduled_end = datetime.utcnow() + timedelta(days=1, hours=1)
        await interview.save(db_session)

        new_start = datetime.utcnow() + timedelta(days=2)
        new_end = datetime.utcnow() + timedelta(days=2, hours=1)

        rescheduled_interview = await interview_service.reschedule_interview(
            db_session,
            interview.id,
            new_start,
            new_end,
            "Conflict in schedule",
            recruiter_user.id,
        )

        assert rescheduled_interview.scheduled_start == new_start
        assert rescheduled_interview.scheduled_end == new_end
        assert rescheduled_interview.status == InterviewStatus.SCHEDULED.value

    async def test_get_user_interviews(
        self,
        db_session: AsyncSession,
        interview_service: InterviewService,
        interview: Interview,
        candidate_user: User,
    ):
        """Test getting interviews for a specific user."""
        interviews = await interview_service.get_user_interviews(
            db_session, candidate_user.id, limit=10
        )

        assert len(interviews) == 1
        assert interviews[0].id == interview.id

    async def test_check_interview_conflicts_no_calendar(
        self,
        db_session: AsyncSession,
        interview_service: InterviewService,
        interview: Interview,
    ):
        """Test conflict checking without calendar integration."""
        # Schedule the interview
        interview.status = InterviewStatus.SCHEDULED.value
        interview.scheduled_start = datetime.utcnow() + timedelta(days=1)
        interview.scheduled_end = datetime.utcnow() + timedelta(days=1, hours=1)
        await interview.save(db_session)

        conflicts = await interview_service.check_interview_conflicts(
            db_session, interview.id
        )

        # Should return empty list when no calendar integration
        assert conflicts == []

    @patch("app.services.calendar_service.CalendarService.list_events")
    async def test_check_interview_conflicts_with_calendar(
        self,
        mock_list_events,
        db_session: AsyncSession,
        interview_service: InterviewService,
        interview: Interview,
        candidate_user: User,
    ):
        """Test conflict checking with calendar integration."""
        # Create calendar integration for candidate
        calendar_integration = CalendarIntegration(
            user_id=candidate_user.id,
            provider="google",
            email=candidate_user.email,
            access_token="test_token",
            calendar_id="primary",
            sync_enabled=True,
            is_active=True,
        )
        db_session.add(calendar_integration)
        await db_session.commit()

        # Schedule the interview
        interview.status = InterviewStatus.SCHEDULED.value
        interview.scheduled_start = datetime.utcnow() + timedelta(days=1)
        interview.scheduled_end = datetime.utcnow() + timedelta(days=1, hours=1)
        await interview.save(db_session)

        # Mock conflicting event
        mock_list_events.return_value = {
            "items": [
                {
                    "id": "conflict_event",
                    "summary": "Conflicting Meeting",
                    "start": {
                        "dateTime": (
                            datetime.utcnow() + timedelta(days=1, minutes=30)
                        ).isoformat()
                    },
                    "end": {
                        "dateTime": (
                            datetime.utcnow() + timedelta(days=1, hours=1, minutes=30)
                        ).isoformat()
                    },
                }
            ]
        }

        conflicts = await interview_service.check_interview_conflicts(
            db_session, interview.id
        )

        assert len(conflicts) > 0
        mock_list_events.assert_called_once()

    async def test_get_interview_statistics(
        self,
        db_session: AsyncSession,
        interview_service: InterviewService,
        interview: Interview,
    ):
        """Test getting interview statistics."""
        stats = await interview_service.get_interview_statistics(db_session)

        assert stats.total_interviews == 1
        assert InterviewStatus.PENDING_SCHEDULE.value in stats.by_status
        assert stats.by_status[InterviewStatus.PENDING_SCHEDULE.value] == 1
        assert "video" in stats.by_type
        assert stats.by_type["video"] == 1

    async def test_proposal_expiration(
        self,
        db_session: AsyncSession,
        interview_service: InterviewService,
        interview: Interview,
        recruiter_user: User,
    ):
        """Test proposal with expiration time."""
        proposal_data = ProposalCreate(
            start_datetime=datetime.utcnow() + timedelta(days=1),
            end_datetime=datetime.utcnow() + timedelta(days=1, hours=1),
            timezone="UTC",
        )

        proposal = await interview_service.create_proposal(
            db_session,
            interview.id,
            proposal_data,
            recruiter_user.id,
            expires_in_hours=24,
        )

        assert proposal.expires_at is not None
        assert proposal.expires_at > datetime.utcnow()

    async def test_multiple_proposals_for_interview(
        self,
        db_session: AsyncSession,
        interview_service: InterviewService,
        interview: Interview,
        recruiter_user: User,
    ):
        """Test creating multiple proposals for the same interview."""
        # Create first proposal
        proposal_data_1 = ProposalCreate(
            start_datetime=datetime.utcnow() + timedelta(days=1),
            end_datetime=datetime.utcnow() + timedelta(days=1, hours=1),
            timezone="UTC",
            notes="First option",
        )

        proposal1 = await interview_service.create_proposal(
            db_session, interview.id, proposal_data_1, recruiter_user.id
        )

        # Create second proposal
        proposal_data_2 = ProposalCreate(
            start_datetime=datetime.utcnow() + timedelta(days=2),
            end_datetime=datetime.utcnow() + timedelta(days=2, hours=1),
            timezone="UTC",
            notes="Alternative time",
        )

        proposal2 = await interview_service.create_proposal(
            db_session, interview.id, proposal_data_2, recruiter_user.id
        )

        assert proposal1.id != proposal2.id
        assert proposal1.interview_id == proposal2.interview_id

        # Get all proposals for the interview
        proposals = await interview_service.get_interview_proposals(
            db_session, interview.id
        )
        assert len(proposals) == 2


class TestInterviewAPI:
    """Test interview API endpoints."""

    @pytest.fixture
    async def auth_headers(self, authenticated_user):
        return {"Authorization": f"Bearer {authenticated_user['access_token']}"}

    def test_create_interview(self, client: TestClient, auth_headers):
        """Test creating an interview via API."""
        interview_data = {
            "candidate_id": 1,
            "recruiter_id": 2,
            "employer_company_id": 1,
            "title": "API Test Interview",
            "description": "Testing interview creation via API",
            "position_title": "Software Engineer",
            "interview_type": "video",
        }

        response = client.post(
            "/api/v1/interviews/", json=interview_data, headers=auth_headers
        )

        assert response.status_code in [200, 201]
        data = response.json()
        assert data["title"] == "API Test Interview"
        assert data["interview_type"] == "video"

    def test_create_interview_invalid_data(self, client: TestClient, auth_headers):
        """Test creating interview with invalid data."""
        interview_data = {
            "candidate_id": 1,
            "recruiter_id": 2,
            # Missing required fields
            "title": "",  # Empty title should fail validation
            "interview_type": "invalid_type",
        }

        response = client.post(
            "/api/v1/interviews/", json=interview_data, headers=auth_headers
        )

        assert response.status_code == 422

    def test_get_interview(self, client: TestClient, auth_headers):
        """Test getting interview details."""
        response = client.get("/api/v1/interviews/1", headers=auth_headers)

        # Should either return interview data or 404
        assert response.status_code in [200, 404]

    def test_create_proposal(self, client: TestClient, auth_headers):
        """Test creating interview proposal via API."""
        proposal_data = {
            "start_datetime": "2024-12-01T10:00:00Z",
            "end_datetime": "2024-12-01T11:00:00Z",
            "timezone": "UTC",
            "location": "Conference Room A",
            "notes": "Initial time proposal",
        }

        response = client.post(
            "/api/v1/interviews/1/proposals", json=proposal_data, headers=auth_headers
        )

        # Should either create proposal or return error for non-existent interview
        assert response.status_code in [200, 201, 404]

    def test_respond_to_proposal(self, client: TestClient, auth_headers):
        """Test responding to proposal via API."""
        response_data = {"response": "accepted", "notes": "This time works perfectly"}

        response = client.post(
            "/api/v1/interviews/proposals/1/respond",
            json=response_data,
            headers=auth_headers,
        )

        # Should either process response or return 404 for non-existent proposal
        assert response.status_code in [200, 404]

    def test_cancel_interview(self, client: TestClient, auth_headers):
        """Test cancelling interview via API."""
        cancel_data = {"reason": "Position has been filled"}

        response = client.patch(
            "/api/v1/interviews/1/cancel", json=cancel_data, headers=auth_headers
        )

        assert response.status_code in [200, 404]

    def test_get_interview_statistics(self, client: TestClient, auth_headers):
        """Test getting interview statistics."""
        response = client.get("/api/v1/interviews/stats", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "total_interviews" in data
        assert "by_status" in data
        assert "by_type" in data

    def test_list_interviews_with_filters(self, client: TestClient, auth_headers):
        """Test listing interviews with filters."""
        params = {"status": "pending_schedule", "limit": 10, "offset": 0}

        response = client.get(
            "/api/v1/interviews/", params=params, headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "interviews" in data
        assert "total" in data
        assert "has_more" in data
