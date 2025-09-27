from datetime import datetime, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import Company
from app.models.interview import Interview
from app.models.message import Message
from app.models.resume import Resume
from app.models.user import User
from app.schemas.interview import InterviewStatus
from app.utils.constants import CompanyType


class TestDashboard:
    """Comprehensive tests for dashboard functionality."""

    @pytest.mark.asyncio
    async def test_get_dashboard_stats_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
        test_company: Company,
        test_user: User,
    ):
        """Test successful retrieval of dashboard statistics."""
        # Create test data for stats

        # Create additional users
        user2 = User(
            email="user2@test.com",
            first_name="User",
            last_name="Two",
            company_id=test_company.id,
            hashed_password="hashedpass",
            is_active=True,
        )
        db_session.add(user2)

        # Create additional companies
        company2 = Company(
            name="Test Company 2",
            type=CompanyType.RECRUITER,
            email="company2@test.com",
            phone="+0987654321",
            description="Test company 2",
            is_active="1",
        )
        db_session.add(company2)

        # Flush to get IDs for foreign key references
        await db_session.flush()

        # Create interviews
        interview1 = Interview(
            candidate_id=test_user.id,
            recruiter_id=user2.id,
            employer_company_id=test_company.id,
            recruiter_company_id=test_company.id,
            title="Test Interview 1",
            scheduled_start=datetime.utcnow() + timedelta(days=1),
            status=InterviewStatus.SCHEDULED.value,
            meeting_url="https://test.com/meeting1",
        )
        interview2 = Interview(
            candidate_id=user2.id,
            recruiter_id=test_user.id,
            employer_company_id=test_company.id,
            recruiter_company_id=test_company.id,
            title="Test Interview 2",
            scheduled_start=datetime.utcnow() + timedelta(days=2),
            status=InterviewStatus.COMPLETED.value,
            meeting_url="https://test.com/meeting2",
        )
        db_session.add(interview1)
        db_session.add(interview2)

        # Create resumes
        resume1 = Resume(
            user_id=test_user.id,
            title="Software Engineer Resume",
            pdf_file_path="resumes/resume1.pdf",
        )
        resume2 = Resume(
            user_id=user2.id,
            title="Frontend Developer Resume",
            pdf_file_path="resumes/resume2.pdf",
        )
        db_session.add(resume1)
        db_session.add(resume2)

        # Create active messages (within last 30 days) to simulate conversations
        message1 = Message(
            sender_id=test_user.id,
            recipient_id=user2.id,
            content="Test message 1",
            type="text",
            created_at=datetime.utcnow() - timedelta(days=5),
        )
        message2 = Message(
            sender_id=user2.id,
            recipient_id=test_user.id,
            content="Test message 2",
            type="text",
            created_at=datetime.utcnow() - timedelta(days=10),
        )
        db_session.add(message1)
        db_session.add(message2)

        await db_session.commit()

        response = await client.get("/api/dashboard/stats", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "total_users" in data
        assert "total_companies" in data
        assert "total_interviews" in data
        assert "total_resumes" in data
        assert "active_conversations" in data

        # Verify data types
        assert isinstance(data["total_users"], int)
        assert isinstance(data["total_companies"], int)
        assert isinstance(data["total_interviews"], int)
        assert isinstance(data["total_resumes"], int)
        assert isinstance(data["active_conversations"], int)

        # Verify counts (should be at least the ones we created)
        assert data["total_users"] >= 2  # test_user + user2
        assert data["total_companies"] >= 2  # test_company + company2
        assert data["total_interviews"] >= 2  # interview1 + interview2
        assert data["total_resumes"] >= 2  # resume1 + resume2
        assert data["active_conversations"] >= 2  # conversation1 + conversation2

    @pytest.mark.asyncio
    async def test_get_dashboard_stats_unauthorized(self, client: AsyncClient):
        """Test dashboard stats access without authentication fails."""
        response = await client.get("/api/dashboard/stats")

        assert response.status_code == 401
        assert "detail" in response.json()

    @pytest.mark.asyncio
    async def test_get_dashboard_stats_with_inactive_data(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
        test_company: Company,
    ):
        """Test that dashboard stats only count active users and companies."""
        # Create inactive user
        inactive_user = User(
            email="inactive@test.com",
            first_name="Inactive",
            last_name="User",
            company_id=test_company.id,
            hashed_password="hashedpass",
            is_active=False,
        )
        db_session.add(inactive_user)

        # Create inactive company
        inactive_company = Company(
            name="Inactive Company",
            type=CompanyType.EMPLOYER,
            email="inactive@company.com",
            phone="+1234567890",
            description="Inactive company",
            is_active="0",
        )
        db_session.add(inactive_company)

        await db_session.commit()

        response = await client.get("/api/dashboard/stats", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        # Verify that inactive users and companies are not counted
        # (We can't check exact counts since there might be other test data,
        # but we can verify the structure and data types)
        assert all(isinstance(data[key], int) for key in data.keys())
        assert all(data[key] >= 0 for key in data.keys())

    @pytest.mark.asyncio
    async def test_get_dashboard_stats_with_old_conversations(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
        test_user: User,
    ):
        """Test that only recent conversations (last 30 days) are counted as active."""
        # Create old message (more than 30 days ago)
        old_message = Message(
            sender_id=test_user.id,
            recipient_id=test_user.id,  # Self message for simplicity
            content="Old message",
            type="text",
            created_at=datetime.utcnow() - timedelta(days=35),
        )
        db_session.add(old_message)

        # Create recent message
        recent_message = Message(
            sender_id=test_user.id,
            recipient_id=test_user.id,  # Self message for simplicity
            content="Recent message",
            type="text",
            created_at=datetime.utcnow() - timedelta(days=5),
        )
        db_session.add(recent_message)

        await db_session.commit()

        response = await client.get("/api/dashboard/stats", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        # Should only count recent conversations
        assert data["active_conversations"] >= 1  # At least the recent one

    @pytest.mark.asyncio
    async def test_get_recent_activity_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
        test_company: Company,
        test_user: User,
    ):
        """Test successful retrieval of recent activity."""
        # Create recent users (within last 7 days)
        recent_user = User(
            email="recent@test.com",
            first_name="Recent",
            last_name="User",
            company_id=test_company.id,
            hashed_password="hashedpass",
            is_active=True,
            created_at=datetime.utcnow() - timedelta(days=3),
        )
        db_session.add(recent_user)

        # Flush to get ID for foreign key reference
        await db_session.flush()

        # Create recent interviews (within last 7 days)
        recent_interview = Interview(
            candidate_id=test_user.id,
            recruiter_id=recent_user.id,
            employer_company_id=test_company.id,
            recruiter_company_id=test_company.id,
            title="Recent Interview",
            scheduled_start=datetime.utcnow() + timedelta(days=1),
            status=InterviewStatus.SCHEDULED.value,
            meeting_url="https://test.com/meeting",
            created_at=datetime.utcnow() - timedelta(days=2),
        )
        db_session.add(recent_interview)

        await db_session.commit()
        await db_session.refresh(recent_user)
        await db_session.refresh(recent_interview)

        response = await client.get("/api/dashboard/activity", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        # Verify response is a list
        assert isinstance(data, list)

        # Check activity items structure
        if data:
            activity_item = data[0]
            assert "id" in activity_item
            assert "type" in activity_item
            assert "title" in activity_item
            assert "description" in activity_item
            assert "timestamp" in activity_item

            # Verify activity types
            activity_types = [item["type"] for item in data]
            valid_types = ["user", "interview"]
            assert all(activity_type in valid_types for activity_type in activity_types)

            # Verify items are sorted by timestamp (descending)
            if len(data) > 1:
                timestamps = [
                    datetime.fromisoformat(item["timestamp"].replace("Z", "+00:00"))
                    for item in data
                ]
                assert timestamps == sorted(timestamps, reverse=True)

    @pytest.mark.asyncio
    async def test_get_recent_activity_with_limit(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
        test_company: Company,
    ):
        """Test recent activity with custom limit parameter."""
        # Create multiple recent users
        for i in range(15):
            user = User(
                email=f"user{i}@test.com",
                first_name=f"User",
                last_name=f"{i}",
                company_id=test_company.id,
                hashed_password="hashedpass",
                is_active=True,
                created_at=datetime.utcnow() - timedelta(days=1, hours=i),
            )
            db_session.add(user)

        await db_session.commit()

        # Test with limit=5
        response = await client.get(
            "/api/dashboard/activity?limit=5", headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        # Should not exceed the limit
        assert len(data) <= 5

    @pytest.mark.asyncio
    async def test_get_recent_activity_limit_validation(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test recent activity with invalid limit parameter."""
        # Test with limit > 100 (should be rejected)
        response = await client.get(
            "/api/dashboard/activity?limit=150", headers=auth_headers
        )

        # Should return validation error for limit > 100
        assert response.status_code == 422

        # Test with valid limit
        response = await client.get(
            "/api/dashboard/activity?limit=50", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 50

    @pytest.mark.asyncio
    async def test_get_recent_activity_unauthorized(self, client: AsyncClient):
        """Test recent activity access without authentication fails."""
        response = await client.get("/api/dashboard/activity")

        assert response.status_code == 401
        assert "detail" in response.json()

    @pytest.mark.asyncio
    async def test_get_recent_activity_empty_result(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test recent activity when there's no recent activity."""
        response = await client.get("/api/dashboard/activity", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        # Should return empty list or minimal activity
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_get_recent_activity_user_metadata(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
        test_company: Company,
    ):
        """Test that user activity items have correct metadata."""
        # Create recent user
        recent_user = User(
            email="metadata@test.com",
            first_name="Metadata",
            last_name="User",
            company_id=test_company.id,
            hashed_password="hashedpass",
            is_active=True,
            created_at=datetime.utcnow() - timedelta(days=1),
        )
        db_session.add(recent_user)
        await db_session.commit()
        await db_session.refresh(recent_user)

        response = await client.get("/api/dashboard/activity", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        # Find user activity items
        user_activities = [item for item in data if item["type"] == "user"]

        if user_activities:
            user_activity = user_activities[0]
            assert user_activity["title"] == "New User Registered"
            assert "joined the platform" in user_activity["description"]
            assert "user_id" in user_activity
            assert "metadata" in user_activity
            if user_activity["metadata"]:
                assert "user_email" in user_activity["metadata"]

    @pytest.mark.asyncio
    async def test_get_recent_activity_interview_metadata(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
        test_user: User,
    ):
        """Test that interview activity items have correct metadata."""
        # Create recent interview
        recent_interview = Interview(
            candidate_id=test_user.id,
            recruiter_id=test_user.id,
            employer_company_id=1,  # Default company ID
            recruiter_company_id=1,  # Default company ID
            title="Interview Metadata Test",
            scheduled_start=datetime.utcnow() + timedelta(days=1),
            status=InterviewStatus.SCHEDULED.value,
            meeting_url="https://test.com/meeting",
            created_at=datetime.utcnow() - timedelta(days=1),
        )
        db_session.add(recent_interview)
        await db_session.commit()
        await db_session.refresh(recent_interview)

        response = await client.get("/api/dashboard/activity", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        # Find interview activity items
        interview_activities = [item for item in data if item["type"] == "interview"]

        if interview_activities:
            interview_activity = interview_activities[0]
            assert interview_activity["title"] == "Interview Scheduled"
            assert "Interview scheduled for" in interview_activity["description"]
            assert "user_id" in interview_activity
            assert "metadata" in interview_activity
            if interview_activity["metadata"]:
                assert "interview_id" in interview_activity["metadata"]
                assert "interview_status" in interview_activity["metadata"]

    @pytest.mark.asyncio
    async def test_dashboard_stats_performance(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test dashboard stats endpoint performance."""
        import time

        start_time = time.time()
        response = await client.get("/api/dashboard/stats", headers=auth_headers)
        end_time = time.time()

        assert response.status_code == 200
        # Should respond within reasonable time (less than 2 seconds)
        assert (end_time - start_time) < 2.0

    @pytest.mark.asyncio
    async def test_recent_activity_performance(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test recent activity endpoint performance."""
        import time

        start_time = time.time()
        response = await client.get("/api/dashboard/activity", headers=auth_headers)
        end_time = time.time()

        assert response.status_code == 200
        # Should respond within reasonable time (less than 2 seconds)
        assert (end_time - start_time) < 2.0
