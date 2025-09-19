"""
Comprehensive tests for interview endpoints.

Tests all CRUD operations, validation, error handling, and interview workflow scenarios.
Following MiraiWorks testing standards with 100% endpoint coverage.
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient
from fastapi import HTTPException

from app.models.interview import Interview, InterviewProposal
from app.utils.constants import InterviewStatus


class TestInterviewEndpoints:
    """Comprehensive test suite for all interview endpoints."""

    @pytest.mark.asyncio
    async def test_create_interview_success(self, client: AsyncClient, auth_headers: dict):
        """Test successful interview creation with valid data."""
        interview_data = {
            "candidate_id": 1,
            "recruiter_id": 2,
            "employer_company_id": 1,
            "title": "Software Engineer Interview",
            "description": "Technical interview for senior position",
            "position_title": "Senior Software Engineer",
            "interview_type": "video"
        }

        with patch('app.services.interview_service.interview_service.create_interview') as mock_create, \
             patch('app.endpoints.interviews._format_interview_response') as mock_format:

            # Mock interview creation
            mock_interview = Interview(
                id=1,
                candidate_id=1,
                recruiter_id=2,
                employer_company_id=1,
                recruiter_company_id=1,
                title="Software Engineer Interview",
                status=InterviewStatus.PENDING_SCHEDULE.value,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            mock_create.return_value = mock_interview

            # Mock response formatting
            mock_format.return_value = {
                "id": 1,
                "title": "Software Engineer Interview",
                "status": InterviewStatus.PENDING_SCHEDULE.value,
                "interview_type": "video",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "candidate": {"id": 1, "email": "candidate@test.com", "full_name": "Test Candidate", "role": "candidate"},
                "recruiter": {"id": 2, "email": "recruiter@test.com", "full_name": "Test Recruiter", "role": "recruiter"},
                "employer_company_name": "Test Company"
            }

            response = await client.post(
                "/api/interviews/",
                json=interview_data,
                headers=auth_headers
            )

            assert response.status_code == 201
            data = response.json()
            assert data["title"] == interview_data["title"]
            assert data["status"] == InterviewStatus.PENDING_SCHEDULE.value
            assert "id" in data

    @pytest.mark.asyncio
    async def test_create_interview_validation_errors(self, client: AsyncClient, auth_headers: dict):
        """Test interview creation with validation errors."""
        # Test missing required fields
        incomplete_data = {
            "title": "Interview Title"
            # Missing candidate_id, recruiter_id, employer_company_id
        }

        response = await client.post(
            "/api/interviews/",
            json=incomplete_data,
            headers=auth_headers
        )

        assert response.status_code == 422
        error_detail = response.json()["detail"]
        required_fields = ["candidate_id", "recruiter_id", "employer_company_id"]
        for field in required_fields:
            assert any(field in str(error).lower() for error in error_detail)

        # Test empty title
        invalid_data = {
            "candidate_id": 1,
            "recruiter_id": 2,
            "employer_company_id": 1,
            "title": "",
            "interview_type": "video"
        }

        response = await client.post(
            "/api/interviews/",
            json=invalid_data,
            headers=auth_headers
        )

        assert response.status_code == 422

        # Test invalid interview type
        invalid_type_data = {
            "candidate_id": 1,
            "recruiter_id": 2,
            "employer_company_id": 1,
            "title": "Test Interview",
            "interview_type": "invalid_type"
        }

        response = await client.post(
            "/api/interviews/",
            json=invalid_type_data,
            headers=auth_headers
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_interview_unauthorized(self, client: AsyncClient):
        """Test interview creation without authentication."""
        interview_data = {
            "candidate_id": 1,
            "recruiter_id": 2,
            "employer_company_id": 1,
            "title": "Test Interview"
        }

        response = await client.post("/api/interviews/", json=interview_data)
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_interviews_success(self, client: AsyncClient, auth_headers: dict):
        """Test successful retrieval of interviews list."""
        with patch('app.services.interview_service.interview_service.get_user_interviews') as mock_get, \
             patch('app.crud.interview.interview.get_user_interviews_count') as mock_count, \
             patch('app.endpoints.interviews._format_interview_response') as mock_format:

            mock_interviews = [
                Interview(
                    id=1,
                    title="Interview 1",
                    status=InterviewStatus.PENDING_SCHEDULE.value,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                ),
                Interview(
                    id=2,
                    title="Interview 2",
                    status=InterviewStatus.SCHEDULED.value,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
            ]
            mock_get.return_value = mock_interviews
            mock_count.return_value = 2

            # Mock format response for each interview
            mock_format.side_effect = [
                {"id": 1, "title": "Interview 1", "status": "pending_schedule"},
                {"id": 2, "title": "Interview 2", "status": "scheduled"}
            ]

            response = await client.get("/api/interviews/", headers=auth_headers)

            assert response.status_code == 200
            data = response.json()
            assert "interviews" in data
            assert "total" in data
            assert "has_more" in data
            assert len(data["interviews"]) == 2

    @pytest.mark.asyncio
    async def test_get_interviews_with_filters(self, client: AsyncClient, auth_headers: dict):
        """Test interviews retrieval with filters."""
        params = {
            "status": InterviewStatus.SCHEDULED.value,
            "limit": 10,
            "offset": 0
        }

        with patch('app.services.interview_service.interview_service.get_user_interviews') as mock_get, \
             patch('app.crud.interview.interview.get_user_interviews_count') as mock_count:

            mock_get.return_value = []
            mock_count.return_value = 0

            response = await client.get("/api/interviews/", params=params, headers=auth_headers)

            assert response.status_code == 200
            data = response.json()
            assert data["total"] == 0
            assert len(data["interviews"]) == 0

    @pytest.mark.asyncio
    async def test_get_single_interview_success(self, client: AsyncClient, auth_headers: dict):
        """Test successful retrieval of single interview."""
        interview_id = 1

        with patch('app.services.interview_service.interview_service.get_interview_with_permissions') as mock_get, \
             patch('app.endpoints.interviews._format_interview_response') as mock_format:

            mock_interview = Interview(
                id=interview_id,
                title="Test Interview",
                status=InterviewStatus.SCHEDULED.value,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            mock_get.return_value = mock_interview

            mock_format.return_value = {
                "id": interview_id,
                "title": "Test Interview",
                "status": InterviewStatus.SCHEDULED.value
            }

            response = await client.get(f"/api/interviews/{interview_id}", headers=auth_headers)

            assert response.status_code == 200
            data = response.json()
            assert data["id"] == interview_id
            assert data["title"] == "Test Interview"

    @pytest.mark.asyncio
    async def test_get_single_interview_not_found(self, client: AsyncClient, auth_headers: dict):
        """Test retrieval of non-existent interview."""
        interview_id = 999

        with patch('app.services.interview_service.interview_service.get_interview_with_permissions') as mock_get:
            mock_get.side_effect = HTTPException(status_code=404, detail="Interview not found")

            response = await client.get(f"/api/interviews/{interview_id}", headers=auth_headers)

            assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_interview_success(self, client: AsyncClient, auth_headers: dict):
        """Test successful interview update."""
        interview_id = 1
        update_data = {
            "title": "Updated Interview Title",
            "description": "Updated description",
            "notes": "Additional notes"
        }

        with patch('app.services.interview_service.interview_service.update_interview') as mock_update, \
             patch('app.endpoints.interviews._format_interview_response') as mock_format:

            mock_interview = Interview(
                id=interview_id,
                title="Updated Interview Title",
                description="Updated description",
                notes="Additional notes",
                updated_at=datetime.utcnow()
            )
            mock_update.return_value = mock_interview

            mock_format.return_value = {
                "id": interview_id,
                "title": "Updated Interview Title",
                "description": "Updated description"
            }

            response = await client.patch(
                f"/api/interviews/{interview_id}",
                json=update_data,
                headers=auth_headers
            )

            assert response.status_code == 200
            data = response.json()
            assert data["title"] == update_data["title"]
            assert data["description"] == update_data["description"]

    @pytest.mark.asyncio
    async def test_create_proposal_success(self, client: AsyncClient, auth_headers: dict):
        """Test successful proposal creation."""
        interview_id = 1
        proposal_data = {
            "start_datetime": "2025-09-25T10:00:00Z",
            "end_datetime": "2025-09-25T11:00:00Z",
            "timezone": "UTC",
            "notes": "Proposed time slot"
        }

        with patch('app.services.interview_service.interview_service.create_time_proposal') as mock_create:
            mock_proposal = {
                "id": 1,
                "interview_id": interview_id,
                "start_datetime": "2025-09-25T10:00:00Z",
                "end_datetime": "2025-09-25T11:00:00Z",
                "status": "pending",
                "notes": "Proposed time slot",
                "created_at": datetime.utcnow().isoformat()
            }
            mock_create.return_value = mock_proposal

            response = await client.post(
                f"/api/interviews/{interview_id}/proposals",
                json=proposal_data,
                headers=auth_headers
            )

            assert response.status_code == 201
            data = response.json()
            assert data["interview_id"] == interview_id
            assert data["status"] == "pending"

    @pytest.mark.asyncio
    async def test_create_proposal_invalid_time_range(self, client: AsyncClient, auth_headers: dict):
        """Test proposal creation with end time before start time."""
        interview_id = 1
        proposal_data = {
            "start_datetime": "2025-09-25T11:00:00Z",
            "end_datetime": "2025-09-25T10:00:00Z",  # End before start
            "timezone": "UTC"
        }

        response = await client.post(
            f"/api/interviews/{interview_id}/proposals",
            json=proposal_data,
            headers=auth_headers
        )

        assert response.status_code == 422
        error_detail = response.json()["detail"]
        assert any("end datetime must be after start datetime" in str(error).lower() for error in error_detail)

    @pytest.mark.asyncio
    async def test_respond_to_proposal_accept(self, client: AsyncClient, auth_headers: dict):
        """Test accepting a time proposal."""
        interview_id = 1
        proposal_id = 1
        response_data = {
            "response": "accepted",
            "notes": "This time works for me"
        }

        with patch('app.services.interview_service.interview_service.respond_to_proposal') as mock_respond:
            mock_proposal = {
                "id": proposal_id,
                "interview_id": interview_id,
                "status": "accepted",
                "response_notes": "This time works for me"
            }
            mock_respond.return_value = mock_proposal

            response = await client.post(
                f"/api/interviews/{interview_id}/proposals/{proposal_id}/respond",
                json=response_data,
                headers=auth_headers
            )

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "accepted"
            assert data["response_notes"] == response_data["notes"]

    @pytest.mark.asyncio
    async def test_cancel_interview_success(self, client: AsyncClient, auth_headers: dict):
        """Test successful interview cancellation."""
        interview_id = 1
        cancel_data = {
            "reason": "Candidate no longer available"
        }

        with patch('app.services.interview_service.interview_service.cancel_interview') as mock_cancel, \
             patch('app.endpoints.interviews._format_interview_response') as mock_format:

            mock_interview = Interview(
                id=interview_id,
                status=InterviewStatus.CANCELLED.value,
                cancellation_reason="Candidate no longer available",
                cancelled_at=datetime.utcnow()
            )
            mock_cancel.return_value = mock_interview

            mock_format.return_value = {
                "id": interview_id,
                "status": InterviewStatus.CANCELLED.value,
                "cancellation_reason": "Candidate no longer available"
            }

            response = await client.post(
                f"/api/interviews/{interview_id}/cancel",
                json=cancel_data,
                headers=auth_headers
            )

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == InterviewStatus.CANCELLED.value
            assert data["cancellation_reason"] == cancel_data["reason"]

    @pytest.mark.asyncio
    async def test_reschedule_interview_success(self, client: AsyncClient, auth_headers: dict):
        """Test successful interview rescheduling."""
        interview_id = 1
        reschedule_data = {
            "new_start": "2025-09-26T14:00:00Z",
            "new_end": "2025-09-26T15:00:00Z",
            "reason": "Scheduling conflict resolved"
        }

        with patch('app.services.interview_service.interview_service.reschedule_interview') as mock_reschedule, \
             patch('app.endpoints.interviews._format_interview_response') as mock_format:

            mock_interview = Interview(
                id=interview_id,
                scheduled_start=datetime.fromisoformat("2025-09-26T14:00:00+00:00"),
                scheduled_end=datetime.fromisoformat("2025-09-26T15:00:00+00:00"),
                status=InterviewStatus.SCHEDULED.value
            )
            mock_reschedule.return_value = mock_interview

            mock_format.return_value = {
                "id": interview_id,
                "status": InterviewStatus.SCHEDULED.value,
                "scheduled_start": "2025-09-26T14:00:00Z",
                "scheduled_end": "2025-09-26T15:00:00Z"
            }

            response = await client.post(
                f"/api/interviews/{interview_id}/reschedule",
                json=reschedule_data,
                headers=auth_headers
            )

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == InterviewStatus.SCHEDULED.value

    @pytest.mark.asyncio
    async def test_get_interview_stats_success(self, client: AsyncClient, auth_headers: dict):
        """Test successful retrieval of interview statistics."""
        with patch('app.services.interview_service.interview_service.get_user_interview_stats') as mock_stats:
            mock_stats_data = {
                "total_interviews": 15,
                "by_status": {
                    "pending_schedule": 3,
                    "scheduled": 5,
                    "completed": 6,
                    "cancelled": 1
                },
                "by_type": {
                    "video": 10,
                    "phone": 3,
                    "in_person": 2
                },
                "upcoming_count": 8,
                "completed_count": 6,
                "average_duration_minutes": 45.5
            }
            mock_stats.return_value = mock_stats_data

            response = await client.get("/api/interviews/stats/summary", headers=auth_headers)

            assert response.status_code == 200
            data = response.json()
            assert data["total_interviews"] == 15
            assert "by_status" in data
            assert "by_type" in data
            assert data["upcoming_count"] == 8

    @pytest.mark.asyncio
    async def test_get_calendar_events_success(self, client: AsyncClient, auth_headers: dict):
        """Test successful retrieval of calendar events."""
        params = {
            "start_date": "2025-09-20T00:00:00Z",
            "end_date": "2025-09-27T23:59:59Z"
        }

        with patch('app.services.interview_service.interview_service.get_user_calendar_events') as mock_events:
            mock_events_data = [
                {
                    "interview_id": 1,
                    "title": "Interview with John Doe",
                    "start": "2025-09-22T10:00:00Z",
                    "end": "2025-09-22T11:00:00Z",
                    "status": "scheduled",
                    "participants": ["john@example.com", "recruiter@company.com"],
                    "location": "Zoom Meeting",
                    "meeting_url": "https://zoom.us/j/123456789"
                }
            ]
            mock_events.return_value = mock_events_data

            response = await client.get(
                "/api/interviews/calendar/events",
                params=params,
                headers=auth_headers
            )

            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["interview_id"] == 1
            assert data[0]["title"] == "Interview with John Doe"

    @pytest.mark.asyncio
    async def test_get_calendar_integration_status_success(self, client: AsyncClient, auth_headers: dict):
        """Test successful retrieval of calendar integration status."""
        with patch('app.services.interview_service.interview_service.get_calendar_integration_status') as mock_status:
            mock_status_data = {
                "has_google_calendar": True,
                "has_microsoft_calendar": False,
                "google_calendar_email": "user@gmail.com",
                "microsoft_calendar_email": None,
                "last_sync_at": "2025-09-19T12:00:00Z",
                "sync_enabled": True
            }
            mock_status.return_value = mock_status_data

            response = await client.get(
                "/api/interviews/calendar/integration-status",
                headers=auth_headers
            )

            assert response.status_code == 200
            data = response.json()
            assert data["has_google_calendar"] is True
            assert data["has_microsoft_calendar"] is False
            assert data["sync_enabled"] is True

    @pytest.mark.asyncio
    async def test_unauthorized_access_scenarios(self, client: AsyncClient):
        """Test all endpoints return 401 without authentication."""
        # Test all major endpoints without auth headers
        unauthorized_tests = [
            ("GET", "/api/interviews/"),
            ("POST", "/api/interviews/", {"title": "Test", "candidate_id": 1, "recruiter_id": 2, "employer_company_id": 1}),
            ("GET", "/api/interviews/1"),
            ("PATCH", "/api/interviews/1", {"title": "Updated"}),
            ("POST", "/api/interviews/1/proposals", {"start_datetime": "2025-09-25T10:00:00Z", "end_datetime": "2025-09-25T11:00:00Z"}),
            ("POST", "/api/interviews/1/cancel", {"reason": "Test"}),
            ("GET", "/api/interviews/stats/summary"),
            ("GET", "/api/interviews/calendar/events"),
            ("GET", "/api/interviews/calendar/integration-status"),
        ]

        for method, url, *data in unauthorized_tests:
            json_data = data[0] if data else None
            if method == "GET":
                response = await client.get(url)
            elif method == "POST":
                response = await client.post(url, json=json_data)
            elif method == "PATCH":
                response = await client.patch(url, json=json_data)

            assert response.status_code == 401, f"{method} {url} should return 401 without auth"

    @pytest.mark.asyncio
    async def test_validation_edge_cases(self, client: AsyncClient, auth_headers: dict):
        """Test various validation edge cases."""

        # Test exceeding cancellation reason length
        cancel_data = {
            "reason": "x" * 1001  # Exceeds 1000 character limit
        }

        response = await client.post(
            "/api/interviews/1/cancel",
            json=cancel_data,
            headers=auth_headers
        )

        assert response.status_code == 422

        # Test invalid proposal response
        response_data = {"response": "maybe"}  # Invalid response

        response = await client.post(
            "/api/interviews/1/proposals/1/respond",
            json=response_data,
            headers=auth_headers
        )

        assert response.status_code == 422

        # Test invalid date range for rescheduling
        reschedule_data = {
            "new_start": "2025-09-26T15:00:00Z",
            "new_end": "2025-09-26T14:00:00Z",  # End before start
        }

        response = await client.post(
            "/api/interviews/1/reschedule",
            json=reschedule_data,
            headers=auth_headers
        )

        assert response.status_code == 422

        # Test pagination limit boundary
        params = {"limit": 101}  # Exceeds maximum of 100

        response = await client.get("/api/interviews/", params=params, headers=auth_headers)

        assert response.status_code == 422

        # Test invalid status filter
        params = {"status": "invalid_status"}

        response = await client.get("/api/interviews/", params=params, headers=auth_headers)

        assert response.status_code == 422


# Helper functions for creating mock objects
def create_mock_interview(interview_id: int, status: str = "pending_schedule") -> Interview:
    """Helper function to create mock interview objects."""
    return Interview(
        id=interview_id,
        candidate_id=1,
        recruiter_id=2,
        employer_company_id=1,
        recruiter_company_id=1,
        title=f"Test Interview {interview_id}",
        status=status,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )


def create_mock_proposal(proposal_id: int, interview_id: int) -> InterviewProposal:
    """Helper function to create mock proposal objects."""
    start_time = datetime.utcnow() + timedelta(days=1)
    return InterviewProposal(
        id=proposal_id,
        interview_id=interview_id,
        proposed_by=1,
        proposer_role="candidate",
        start_datetime=start_time,
        end_datetime=start_time + timedelta(hours=1),
        status="pending",
        created_at=datetime.utcnow()
    )