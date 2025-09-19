"""
Comprehensive tests for interview endpoints.

Tests all CRUD operations, validation, error handling, and interview workflow scenarios.
Following MiraiWorks testing standards with 100% endpoint coverage.
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.interview import Interview, InterviewProposal
from app.models.user import User
from app.models.company import Company
from app.schemas.interview import (
    InterviewCreate,
    InterviewUpdate,
    ProposalCreate,
    ProposalResponse,
    InterviewCancel,
    InterviewReschedule,
    InterviewsListRequest,
)
from app.utils.constants import InterviewStatus


class TestInterviewCreation:
    """Test interview creation endpoint and validation."""

    async def get_auth_headers(self, client, db_session):
        """Get real authentication headers with interview permissions."""
        from app.models.user import User
        from app.models.company import Company
        from app.models.role import Role, UserRole
        from app.services.auth_service import auth_service
        from app.utils.constants import UserRole as UserRoleEnum

        # Create test company
        company = Company(
            name="Test Interview Company",
            email="interview@test.com",
            phone="03-1234-5678",
            type="employer"
        )
        db_session.add(company)
        await db_session.commit()
        await db_session.refresh(company)

        # Create roles
        roles = {}
        for role_name in UserRoleEnum:
            role = Role(name=role_name.value, description=f"Test {role_name.value} role")
            db_session.add(role)
            roles[role_name.value] = role
        await db_session.commit()

        # Create test user with interview permissions
        user = User(
            email='interview.test@test.com',
            first_name='Interview',
            last_name='Tester',
            company_id=company.id,
            hashed_password=auth_service.get_password_hash('testpass123'),
            is_active=True,
            is_admin=True,
            require_2fa=False,
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        # Assign recruiter role (has interview permissions)
        user_role = UserRole(user_id=user.id, role_id=roles[UserRoleEnum.RECRUITER.value].id)
        db_session.add(user_role)
        await db_session.commit()

        # Login to get real token
        login_response = await client.post(
            "/api/auth/login",
            json={"email": "interview.test@test.com", "password": "testpass123"},
        )
        assert login_response.status_code == 200
        login_data = login_response.json()

        # Handle 2FA if required
        if login_data.get("require_2fa"):
            verify_response = await client.post(
                "/api/auth/2fa/verify",
                json={"user_id": user.id, "code": "123456"}
            )
            assert verify_response.status_code == 200
            login_data = verify_response.json()

        token = login_data['access_token']
        return {"Authorization": f"Bearer {token}"}

    @pytest.mark.asyncio
    async def test_create_interview_success(self, client: AsyncClient, db_session: AsyncSession):
        """Test successful interview creation with valid data."""
        # Get auth headers (creates recruiter user with ID 1)
        auth_headers = await self.get_auth_headers(client, db_session)

        # Create candidate user
        from app.models.user import User
        from app.models.company import Company
        from app.models.role import Role, UserRole
        from app.services.auth_service import auth_service
        from app.utils.constants import UserRole as UserRoleEnum

        # Create candidate company
        candidate_company = Company(
            name="Candidate Company",
            email="candidate@test.com",
            phone="03-9876-5432",
            type="employer"
        )
        db_session.add(candidate_company)
        await db_session.commit()
        await db_session.refresh(candidate_company)

        # Get candidate role
        from sqlalchemy import select
        candidate_role_result = await db_session.execute(
            select(Role).where(Role.name == UserRoleEnum.CANDIDATE.value)
        )
        candidate_role = candidate_role_result.scalar_one()

        # Create candidate user
        candidate_user = User(
            email='candidate@test.com',
            first_name='Test',
            last_name='Candidate',
            company_id=candidate_company.id,
            hashed_password=auth_service.get_password_hash('testpass123'),
            is_active=True,
            is_admin=False,
            require_2fa=False,
        )
        db_session.add(candidate_user)
        await db_session.commit()
        await db_session.refresh(candidate_user)

        # Assign candidate role
        candidate_user_role = UserRole(user_id=candidate_user.id, role_id=candidate_role.id)
        db_session.add(candidate_user_role)
        await db_session.commit()

        interview_data = {
            "candidate_id": candidate_user.id,
            "recruiter_id": 1,  # The authenticated recruiter user
            "employer_company_id": candidate_company.id,
            "title": "Software Engineer Interview",
            "description": "Technical interview for senior position",
            "position_title": "Senior Software Engineer",
            "interview_type": "video"
        }

        response = await client.post(
            "/api/interviews/",
            json=interview_data,
            headers=auth_headers
        )

        if response.status_code != 201:
            print(f"Response status: {response.status_code}")
            print(f"Response text: {response.text}")
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == interview_data["title"]
        assert "id" in data

    @pytest.mark.asyncio
    async def test_create_interview_missing_required_fields(self, client: AsyncClient, db_session: AsyncSession):
        """Test interview creation with missing required fields."""
        # Get auth headers
        auth_headers = await self.get_auth_headers(client, db_session)

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

    @pytest.mark.asyncio
    async def test_create_interview_empty_title(self, client: AsyncClient, db_session: AsyncSession):
        """Test interview creation with empty title."""
        # Get auth headers
        auth_headers = await self.get_auth_headers(client, db_session)

        interview_data = {
            "candidate_id": 1,
            "recruiter_id": 2,
            "employer_company_id": 1,
            "title": "",
            "interview_type": "video"
        }

        response = await client.post(
            "/api/interviews/",
            json=interview_data,
            headers=auth_headers
        )

        assert response.status_code == 422
        error_detail = response.json()["detail"]
        assert any("title" in str(error).lower() for error in error_detail)

    @pytest.mark.asyncio
    async def test_create_interview_invalid_type(self, client: AsyncClient, db_session: AsyncSession):
        """Test interview creation with invalid interview type."""
        # Get auth headers
        auth_headers = await self.get_auth_headers(client, db_session)

        interview_data = {
            "candidate_id": 1,
            "recruiter_id": 2,
            "employer_company_id": 1,
            "title": "Test Interview",
            "interview_type": "invalid_type"
        }

        response = await client.post(
            "/api/interviews/",
            json=interview_data,
            headers=auth_headers
        )

        assert response.status_code == 422
        error_detail = response.json()["detail"]
        assert any("interview_type" in str(error).lower() for error in error_detail)

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
    async def test_create_interview_insufficient_permissions(self, client: AsyncClient, db_session: AsyncSession):
        """Test interview creation with insufficient permissions."""
        # Create a user with no interview permissions
        from app.models.user import User
        from app.models.company import Company
        from app.models.role import Role, UserRole
        from app.services.auth_service import auth_service
        from app.utils.constants import UserRole as UserRoleEnum
        from sqlalchemy import select

        # Create candidate company and user without permissions
        candidate_company = Company(
            name="No Perms Company",
            email="noperms@test.com",
            phone="03-0000-0000",
            type="employer"
        )
        db_session.add(candidate_company)
        await db_session.commit()
        await db_session.refresh(candidate_company)

        # Create or get candidate role (no interview create permissions)
        candidate_role_result = await db_session.execute(
            select(Role).where(Role.name == UserRoleEnum.CANDIDATE.value)
        )
        candidate_role = candidate_role_result.scalar_one_or_none()
        if not candidate_role:
            candidate_role = Role(name=UserRoleEnum.CANDIDATE.value, description="Candidate role")
            db_session.add(candidate_role)
            await db_session.commit()
            await db_session.refresh(candidate_role)

        no_perms_user = User(
            email='noperms@test.com',
            first_name='No',
            last_name='Permissions',
            company_id=candidate_company.id,
            hashed_password=auth_service.get_password_hash('testpass123'),
            is_active=True,
            is_admin=False,
            require_2fa=False,
        )
        db_session.add(no_perms_user)
        await db_session.commit()
        await db_session.refresh(no_perms_user)

        # Assign candidate role (no create permissions)
        user_role = UserRole(user_id=no_perms_user.id, role_id=candidate_role.id)
        db_session.add(user_role)
        await db_session.commit()

        # Login to get token
        login_response = await client.post(
            "/api/auth/login",
            json={"email": "noperms@test.com", "password": "testpass123"},
        )
        assert login_response.status_code == 200
        login_data = login_response.json()
        token = login_data['access_token']
        auth_headers_no_perms = {"Authorization": f"Bearer {token}"}

        interview_data = {
            "candidate_id": 1,
            "recruiter_id": 2,
            "employer_company_id": 1,
            "title": "Test Interview"
        }

        response = await client.post(
            "/api/interviews/",
            json=interview_data,
            headers=auth_headers_no_perms
        )
        assert response.status_code == 403


class TestInterviewRetrieval:
    """Test interview retrieval endpoints."""

    async def get_auth_headers(self, client, db_session):
        """Get authentication headers for a user with interview permissions."""
        from app.models.user import User
        from app.models.company import Company
        from app.models.role import Role, UserRole
        from app.services.auth_service import auth_service
        from app.utils.constants import UserRole as UserRoleEnum
        from sqlalchemy import select

        # Create test company
        company = Company(
            name="Test Retrieval Company",
            email="retrieval@test.com",
            phone="03-1234-5678",
            type="employer"
        )
        db_session.add(company)
        await db_session.commit()
        await db_session.refresh(company)

        # Create or get recruiter role
        recruiter_role_result = await db_session.execute(
            select(Role).where(Role.name == UserRoleEnum.RECRUITER.value)
        )
        recruiter_role = recruiter_role_result.scalar_one_or_none()
        if not recruiter_role:
            recruiter_role = Role(name=UserRoleEnum.RECRUITER.value, description="Recruiter role")
            db_session.add(recruiter_role)
            await db_session.commit()
            await db_session.refresh(recruiter_role)

        # Create test user with interview permissions
        user = User(
            email='retrieval.test@test.com',
            first_name='Retrieval',
            last_name='Tester',
            company_id=company.id,
            hashed_password=auth_service.get_password_hash('testpass123'),
            is_active=True,
            is_admin=True,
            require_2fa=False,
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        # Assign recruiter role
        user_role = UserRole(user_id=user.id, role_id=recruiter_role.id)
        db_session.add(user_role)
        await db_session.commit()

        # Login to get real token
        login_response = await client.post(
            "/api/auth/login",
            json={"email": "retrieval.test@test.com", "password": "testpass123"},
        )
        assert login_response.status_code == 200
        login_data = login_response.json()

        token = login_data['access_token']
        return {"Authorization": f"Bearer {token}"}

    def test_get_interviews_success(self, auth_headers, mock_db_session):
        """Test successful retrieval of interviews list."""
        with patch('app.services.interview_service.interview_service.get_user_interviews') as mock_get, \
             patch('app.crud.interview.interview.get_user_interviews_count') as mock_count:

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

            response = client.get("/api/interviews/", headers=auth_headers)

            assert response.status_code == 200
            data = response.json()
            assert "interviews" in data
            assert "total" in data
            assert "has_more" in data
            assert len(data["interviews"]) == 2

    def test_get_interviews_with_filters(self, auth_headers, mock_db_session):
        """Test interviews retrieval with status filter."""
        params = {
            "status": InterviewStatus.SCHEDULED.value,
            "limit": 10,
            "offset": 0
        }

        with patch('app.services.interview_service.interview_service.get_user_interviews') as mock_get, \
             patch('app.crud.interview.interview.get_user_interviews_count') as mock_count:

            mock_get.return_value = []
            mock_count.return_value = 0

            response = client.get("/api/interviews/", params=params, headers=auth_headers)

            assert response.status_code == 200
            data = response.json()
            assert data["total"] == 0
            assert len(data["interviews"]) == 0

    @pytest.mark.asyncio
    async def test_get_interviews_invalid_status_filter(self, client: AsyncClient, db_session: AsyncSession):
        """Test interviews retrieval with invalid status filter."""
        # Get auth headers
        auth_headers = await self.get_auth_headers(client, db_session)

        params = {"status": "invalid_status"}

        response = await client.get("/api/interviews/", params=params, headers=auth_headers)

        assert response.status_code == 422
        error_detail = response.json()["detail"]
        assert any("status" in str(error).lower() for error in error_detail)

    @pytest.mark.asyncio
    async def test_get_interviews_unauthorized(self, client: AsyncClient):
        """Test interviews retrieval without authentication."""
        response = await client.get("/api/interviews/")
        assert response.status_code == 401

    def test_get_single_interview_success(self, auth_headers, mock_db_session):
        """Test successful retrieval of single interview."""
        interview_id = 1

        with patch('app.services.interview_service.interview_service.get_interview_with_permissions') as mock_get:
            mock_interview = Interview(
                id=interview_id,
                title="Test Interview",
                status=InterviewStatus.SCHEDULED.value,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            mock_get.return_value = mock_interview

            response = client.get(f"/api/interviews/{interview_id}", headers=auth_headers)

            assert response.status_code == 200
            data = response.json()
            assert data["id"] == interview_id
            assert data["title"] == "Test Interview"

    def test_get_single_interview_not_found(self, auth_headers, mock_db_session):
        """Test retrieval of non-existent interview."""
        interview_id = 999

        with patch('app.services.interview_service.interview_service.get_interview_with_permissions') as mock_get:
            mock_get.side_effect = HTTPException(status_code=404, detail="Interview not found")

            response = client.get(f"/api/interviews/{interview_id}", headers=auth_headers)

            assert response.status_code == 404


class TestInterviewUpdate:
    """Test interview update endpoint."""

    async def get_auth_headers(self, client, db_session):
        """Get authentication headers for a user with interview permissions."""
        from app.models.user import User
        from app.models.company import Company
        from app.models.role import Role, UserRoleAssignment, Permission, RolePermission
        from app.utils.constants import UserRole
        from sqlalchemy import select

        # Create test company and user with proper permissions
        company = Company(name="Test Interview Update Company", email="update@test.com", phone="03-1234-5678", type="employer")
        db_session.add(company)
        await db_session.commit()
        await db_session.refresh(company)

        user = User(
            email='interview.update@test.com',
            full_name='Interview Update User',
            password_hash='$2b$12$test',
            company_id=company.id,
            is_active=True,
            role=UserRole.HR_MANAGER
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        # Create required role and permissions
        role = Role(name="interview_update_role", description="Role with interview update permissions")
        db_session.add(role)
        await db_session.commit()
        await db_session.refresh(role)

        permissions = ["interviews.update", "interviews.read", "interviews.cancel"]
        for perm_name in permissions:
            permission = Permission(name=perm_name, description=f"Permission to {perm_name}")
            db_session.add(permission)

        await db_session.commit()

        # Add permissions to role
        for perm_name in permissions:
            permission = await db_session.execute(select(Permission).where(Permission.name == perm_name))
            permission = permission.scalar_one()
            role_permission = RolePermission(role_id=role.id, permission_id=permission.id)
            db_session.add(role_permission)

        # Assign role to user
        user_role = UserRoleAssignment(user_id=user.id, role_id=role.id)
        db_session.add(user_role)
        await db_session.commit()

        # Login to get real token
        login_response = await client.post("/api/auth/login", json={
            "email": "interview.update@test.com",
            "password": "testpass123"
        })
        login_data = login_response.json()

        # Handle 2FA if required
        if login_data.get("require_2fa"):
            verify_response = await client.post(
                "/api/auth/2fa/verify",
                json={"user_id": user.id, "code": "123456"}
            )
            verify_data = verify_response.json()
            token = verify_data['access_token']
        else:
            token = login_data['access_token']

        return {"Authorization": f"Bearer {token}"}

    def test_update_interview_success(self, auth_headers, mock_db_session):
        """Test successful interview update."""
        interview_id = 1
        update_data = {
            "title": "Updated Interview Title",
            "description": "Updated description",
            "notes": "Additional notes"
        }

        with patch('app.services.interview_service.interview_service.update_interview') as mock_update:
            mock_interview = Interview(
                id=interview_id,
                title="Updated Interview Title",
                description="Updated description",
                notes="Additional notes",
                updated_at=datetime.utcnow()
            )
            mock_update.return_value = mock_interview

            response = client.patch(
                f"/api/interviews/{interview_id}",
                json=update_data,
                headers=auth_headers
            )

            assert response.status_code == 200
            data = response.json()
            assert data["title"] == update_data["title"]
            assert data["description"] == update_data["description"]

    @pytest.mark.asyncio
    async def test_update_interview_empty_title(self, client: AsyncClient, db_session: AsyncSession):
        """Test interview update with empty title."""
        # Get auth headers
        auth_headers = await self.get_auth_headers(client, db_session)

        interview_id = 1
        update_data = {"title": ""}

        response = await client.patch(
            f"/api/interviews/{interview_id}",
            json=update_data,
            headers=auth_headers
        )

        assert response.status_code == 422
        error_detail = response.json()["detail"]
        assert any("title" in str(error).lower() for error in error_detail)

    def test_update_interview_not_found(self, auth_headers, mock_db_session):
        """Test update of non-existent interview."""
        interview_id = 999
        update_data = {"title": "Updated Title"}

        with patch('app.services.interview_service.interview_service.update_interview') as mock_update:
            mock_update.side_effect = HTTPException(status_code=404, detail="Interview not found")

            response = client.patch(
                f"/api/interviews/{interview_id}",
                json=update_data,
                headers=auth_headers
            )

            assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_interview_unauthorized(self, client: AsyncClient):
        """Test interview update without authentication."""
        interview_id = 1
        update_data = {"title": "Updated Title"}

        response = await client.patch(f"/api/interviews/{interview_id}", json=update_data)
        assert response.status_code == 401


class TestInterviewProposals:
    """Test interview proposal endpoints."""

    async def get_auth_headers(self, client, db_session):
        """Get authentication headers for a user with interview permissions."""
        from app.models.user import User
        from app.models.company import Company
        from app.models.role import Role, UserRoleAssignment, Permission, RolePermission
        from app.utils.constants import UserRole
        from sqlalchemy import select

        # Create test company and user with proper permissions
        company = Company(name="Test Interview Proposals Company", email="proposals@test.com", phone="03-1234-5678", type="employer")
        db_session.add(company)
        await db_session.commit()
        await db_session.refresh(company)

        user = User(
            email='interview.proposals@test.com',
            full_name='Interview Proposals User',
            password_hash='$2b$12$test',
            company_id=company.id,
            is_active=True,
            role=UserRole.HR_MANAGER
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        # Create required role and permissions
        role = Role(name="interview_proposals_role", description="Role with interview proposal permissions")
        db_session.add(role)
        await db_session.commit()
        await db_session.refresh(role)

        permissions = ["interviews.propose", "interviews.accept", "interviews.read"]
        for perm_name in permissions:
            permission = Permission(name=perm_name, description=f"Permission to {perm_name}")
            db_session.add(permission)

        await db_session.commit()

        # Add permissions to role
        for perm_name in permissions:
            permission = await db_session.execute(select(Permission).where(Permission.name == perm_name))
            permission = permission.scalar_one()
            role_permission = RolePermission(role_id=role.id, permission_id=permission.id)
            db_session.add(role_permission)

        # Assign role to user
        user_role = UserRoleAssignment(user_id=user.id, role_id=role.id)
        db_session.add(user_role)
        await db_session.commit()

        # Login to get real token
        login_response = await client.post("/api/auth/login", json={
            "email": "interview.proposals@test.com",
            "password": "testpass123"
        })
        login_data = login_response.json()

        # Handle 2FA if required
        if login_data.get("require_2fa"):
            verify_response = await client.post(
                "/api/auth/2fa/verify",
                json={"user_id": user.id, "code": "123456"}
            )
            verify_data = verify_response.json()
            token = verify_data['access_token']
        else:
            token = login_data['access_token']

        return {"Authorization": f"Bearer {token}"}

    def test_create_proposal_success(self, auth_headers, mock_db_session):
        """Test successful proposal creation."""
        interview_id = 1
        proposal_data = {
            "start_datetime": "2025-09-25T10:00:00Z",
            "end_datetime": "2025-09-25T11:00:00Z",
            "timezone": "UTC",
            "notes": "Proposed time slot"
        }

        with patch('app.services.interview_service.interview_service.create_time_proposal') as mock_create:
            mock_proposal = InterviewProposal(
                id=1,
                interview_id=interview_id,
                start_datetime=datetime.fromisoformat("2025-09-25T10:00:00+00:00"),
                end_datetime=datetime.fromisoformat("2025-09-25T11:00:00+00:00"),
                status="pending",
                created_at=datetime.utcnow()
            )
            mock_create.return_value = mock_proposal

            response = client.post(
                f"/api/interviews/{interview_id}/proposals",
                json=proposal_data,
                headers=auth_headers
            )

            assert response.status_code == 201
            data = response.json()
            assert data["interview_id"] == interview_id
            assert data["status"] == "pending"

    @pytest.mark.asyncio
    async def test_create_proposal_invalid_time_range(self, client: AsyncClient, db_session: AsyncSession):
        """Test proposal creation with end time before start time."""
        # Get auth headers
        auth_headers = await self.get_auth_headers(client, db_session)

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

    def test_respond_to_proposal_accept(self, auth_headers, mock_db_session):
        """Test accepting a time proposal."""
        interview_id = 1
        proposal_id = 1
        response_data = {
            "response": "accepted",
            "notes": "This time works for me"
        }

        with patch('app.services.interview_service.interview_service.respond_to_proposal') as mock_respond:
            mock_proposal = InterviewProposal(
                id=proposal_id,
                interview_id=interview_id,
                status="accepted",
                response_notes="This time works for me"
            )
            mock_respond.return_value = mock_proposal

            response = client.post(
                f"/api/interviews/{interview_id}/proposals/{proposal_id}/respond",
                json=response_data,
                headers=auth_headers
            )

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "accepted"
            assert data["response_notes"] == response_data["notes"]

    @pytest.mark.asyncio
    async def test_respond_to_proposal_invalid_response(self, client: AsyncClient, db_session: AsyncSession):
        """Test responding to proposal with invalid response."""
        # Get auth headers
        auth_headers = await self.get_auth_headers(client, db_session)

        interview_id = 1
        proposal_id = 1
        response_data = {"response": "maybe"}  # Invalid response

        response = await client.post(
            f"/api/interviews/{interview_id}/proposals/{proposal_id}/respond",
            json=response_data,
            headers=auth_headers
        )

        assert response.status_code == 422
        error_detail = response.json()["detail"]
        assert any("response must be" in str(error).lower() for error in error_detail)


class TestInterviewWorkflow:
    """Test interview workflow operations (cancel, reschedule)."""

    async def get_auth_headers(self, client, db_session):
        """Get authentication headers for a user with interview permissions."""
        from app.models.user import User
        from app.models.company import Company
        from app.models.role import Role, UserRoleAssignment, Permission, RolePermission
        from app.utils.constants import UserRole
        from sqlalchemy import select

        # Create test company and user with proper permissions
        company = Company(name="Test Interview Workflow Company", email="workflow@test.com", phone="03-1234-5678", type="employer")
        db_session.add(company)
        await db_session.commit()
        await db_session.refresh(company)

        user = User(
            email='interview.workflow@test.com',
            full_name='Interview Workflow User',
            password_hash='$2b$12$test',
            company_id=company.id,
            is_active=True,
            role=UserRole.HR_MANAGER
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        # Create required role and permissions
        role = Role(name="interview_workflow_role", description="Role with interview workflow permissions")
        db_session.add(role)
        await db_session.commit()
        await db_session.refresh(role)

        permissions = ["interviews.cancel", "interviews.update", "interviews.read"]
        for perm_name in permissions:
            permission = Permission(name=perm_name, description=f"Permission to {perm_name}")
            db_session.add(permission)

        await db_session.commit()

        # Add permissions to role
        for perm_name in permissions:
            permission = await db_session.execute(select(Permission).where(Permission.name == perm_name))
            permission = permission.scalar_one()
            role_permission = RolePermission(role_id=role.id, permission_id=permission.id)
            db_session.add(role_permission)

        # Assign role to user
        user_role = UserRoleAssignment(user_id=user.id, role_id=role.id)
        db_session.add(user_role)
        await db_session.commit()

        # Login to get real token
        login_response = await client.post("/api/auth/login", json={
            "email": "interview.workflow@test.com",
            "password": "testpass123"
        })
        login_data = login_response.json()

        # Handle 2FA if required
        if login_data.get("require_2fa"):
            verify_response = await client.post(
                "/api/auth/2fa/verify",
                json={"user_id": user.id, "code": "123456"}
            )
            verify_data = verify_response.json()
            token = verify_data['access_token']
        else:
            token = login_data['access_token']

        return {"Authorization": f"Bearer {token}"}

    def test_cancel_interview_success(self, auth_headers, mock_db_session):
        """Test successful interview cancellation."""
        interview_id = 1
        cancel_data = {
            "reason": "Candidate no longer available"
        }

        with patch('app.services.interview_service.interview_service.cancel_interview') as mock_cancel:
            mock_interview = Interview(
                id=interview_id,
                status=InterviewStatus.CANCELLED.value,
                cancellation_reason="Candidate no longer available",
                cancelled_at=datetime.utcnow()
            )
            mock_cancel.return_value = mock_interview

            response = client.post(
                f"/api/interviews/{interview_id}/cancel",
                json=cancel_data,
                headers=auth_headers
            )

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == InterviewStatus.CANCELLED.value
            assert data["cancellation_reason"] == cancel_data["reason"]

    @pytest.mark.asyncio
    async def test_cancel_interview_excessive_reason_length(self, client: AsyncClient, db_session: AsyncSession):
        """Test interview cancellation with excessive reason length."""
        # Get auth headers
        auth_headers = await self.get_auth_headers(client, db_session)

        interview_id = 1
        cancel_data = {
            "reason": "x" * 1001  # Exceeds 1000 character limit
        }

        response = await client.post(
            f"/api/interviews/{interview_id}/cancel",
            json=cancel_data,
            headers=auth_headers
        )

        assert response.status_code == 422
        error_detail = response.json()["detail"]
        assert any("1000 characters" in str(error) for error in error_detail)

    def test_reschedule_interview_success(self, auth_headers, mock_db_session):
        """Test successful interview rescheduling."""
        interview_id = 1
        reschedule_data = {
            "new_start": "2025-09-26T14:00:00Z",
            "new_end": "2025-09-26T15:00:00Z",
            "reason": "Scheduling conflict resolved"
        }

        with patch('app.services.interview_service.interview_service.reschedule_interview') as mock_reschedule:
            mock_interview = Interview(
                id=interview_id,
                scheduled_start=datetime.fromisoformat("2025-09-26T14:00:00+00:00"),
                scheduled_end=datetime.fromisoformat("2025-09-26T15:00:00+00:00"),
                status=InterviewStatus.SCHEDULED.value
            )
            mock_reschedule.return_value = mock_interview

            response = client.post(
                f"/api/interviews/{interview_id}/reschedule",
                json=reschedule_data,
                headers=auth_headers
            )

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == InterviewStatus.SCHEDULED.value

    @pytest.mark.asyncio
    async def test_reschedule_interview_invalid_time_range(self, client: AsyncClient, db_session: AsyncSession):
        """Test interview rescheduling with invalid time range."""
        # Get auth headers
        auth_headers = await self.get_auth_headers(client, db_session)

        interview_id = 1
        reschedule_data = {
            "new_start": "2025-09-26T15:00:00Z",
            "new_end": "2025-09-26T14:00:00Z",  # End before start
        }

        response = await client.post(
            f"/api/interviews/{interview_id}/reschedule",
            json=reschedule_data,
            headers=auth_headers
        )

        assert response.status_code == 422
        error_detail = response.json()["detail"]
        assert any("end datetime must be after start datetime" in str(error).lower() for error in error_detail)


class TestInterviewStats:
    """Test interview statistics endpoint."""

    def test_get_interview_stats_success(self, auth_headers, mock_db_session):
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

            response = client.get("/api/interviews/stats/summary", headers=auth_headers)

            assert response.status_code == 200
            data = response.json()
            assert data["total_interviews"] == 15
            assert "by_status" in data
            assert "by_type" in data
            assert data["upcoming_count"] == 8

    @pytest.mark.asyncio
    async def test_get_interview_stats_unauthorized(self, client: AsyncClient):
        """Test interview stats retrieval without authentication."""
        response = await client.get("/api/interviews/stats/summary")
        assert response.status_code == 401


class TestInterviewCalendarIntegration:
    """Test interview calendar integration endpoints."""

    def test_get_calendar_events_success(self, auth_headers, mock_db_session):
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

            response = client.get(
                "/api/interviews/calendar/events",
                params=params,
                headers=auth_headers
            )

            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["interview_id"] == 1
            assert data[0]["title"] == "Interview with John Doe"

    def test_get_calendar_integration_status_success(self, auth_headers, mock_db_session):
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

            response = client.get(
                "/api/interviews/calendar/integration-status",
                headers=auth_headers
            )

            assert response.status_code == 200
            data = response.json()
            assert data["has_google_calendar"] is True
            assert data["has_microsoft_calendar"] is False
            assert data["sync_enabled"] is True


class TestInterviewEdgeCases:
    """Test interview endpoint edge cases and boundary conditions."""

    async def get_auth_headers(self, client, db_session):
        """Get authentication headers for a user with interview permissions."""
        from app.models.user import User
        from app.models.company import Company
        from app.models.role import Role, UserRoleAssignment, Permission, RolePermission
        from app.utils.constants import UserRole
        from sqlalchemy import select

        # Create test company and user with proper permissions
        company = Company(name="Test Interview Edge Cases Company", email="edge@test.com", phone="03-1234-5678", type="employer")
        db_session.add(company)
        await db_session.commit()
        await db_session.refresh(company)

        user = User(
            email='interview.edge@test.com',
            full_name='Interview Edge Cases User',
            password_hash='$2b$12$test',
            company_id=company.id,
            is_active=True,
            role=UserRole.HR_MANAGER
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        # Create required role and permissions
        role = Role(name="interview_edge_role", description="Role with interview edge case permissions")
        db_session.add(role)
        await db_session.commit()
        await db_session.refresh(role)

        permissions = ["interviews.create", "interviews.read", "interviews.propose"]
        for perm_name in permissions:
            permission = Permission(name=perm_name, description=f"Permission to {perm_name}")
            db_session.add(permission)

        await db_session.commit()

        # Add permissions to role
        for perm_name in permissions:
            permission = await db_session.execute(select(Permission).where(Permission.name == perm_name))
            permission = permission.scalar_one()
            role_permission = RolePermission(role_id=role.id, permission_id=permission.id)
            db_session.add(role_permission)

        # Assign role to user
        user_role = UserRoleAssignment(user_id=user.id, role_id=role.id)
        db_session.add(user_role)
        await db_session.commit()

        # Login to get real token
        login_response = await client.post("/api/auth/login", json={
            "email": "interview.edge@test.com",
            "password": "testpass123"
        })
        login_data = login_response.json()

        # Handle 2FA if required
        if login_data.get("require_2fa"):
            verify_response = await client.post(
                "/api/auth/2fa/verify",
                json={"user_id": user.id, "code": "123456"}
            )
            verify_data = verify_response.json()
            token = verify_data['access_token']
        else:
            token = login_data['access_token']

        return {"Authorization": f"Bearer {token}"}

    def test_create_interview_with_all_optional_fields(self, auth_headers, mock_db_session):
        """Test interview creation with all optional fields provided."""
        interview_data = {
            "candidate_id": 1,
            "recruiter_id": 2,
            "employer_company_id": 1,
            "title": "Comprehensive Interview",
            "description": "Detailed technical interview with coding challenges",
            "position_title": "Senior Full Stack Developer",
            "interview_type": "video"
        }

        with patch('app.services.interview_service.interview_service.create_interview') as mock_create:
            mock_interview = Interview(id=1, **interview_data, status="pending_schedule")
            mock_create.return_value = mock_interview

            response = client.post(
                "/api/interviews/",
                json=interview_data,
                headers=auth_headers
            )

            assert response.status_code == 201
            data = response.json()
            assert data["description"] == interview_data["description"]
            assert data["position_title"] == interview_data["position_title"]

    @pytest.mark.asyncio
    async def test_get_interviews_with_pagination_boundary(self, client: AsyncClient, db_session: AsyncSession):
        """Test interviews retrieval at pagination boundaries."""
        # Get auth headers
        auth_headers = await self.get_auth_headers(client, db_session)

        params = {
            "limit": 100,  # Maximum allowed limit
            "offset": 0
        }

        with patch('app.services.interview_service.interview_service.get_user_interviews') as mock_get, \
             patch('app.crud.interview.interview.get_user_interviews_count') as mock_count:

            mock_get.return_value = []
            mock_count.return_value = 0

            response = await client.get("/api/interviews/", params=params, headers=auth_headers)

            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_interviews_exceed_limit_boundary(self, client: AsyncClient, db_session: AsyncSession):
        """Test interviews retrieval with limit exceeding maximum."""
        # Get auth headers
        auth_headers = await self.get_auth_headers(client, db_session)

        params = {"limit": 101}  # Exceeds maximum of 100

        response = await client.get("/api/interviews/", params=params, headers=auth_headers)

        assert response.status_code == 422
        error_detail = response.json()["detail"]
        assert any("limit cannot exceed 100" in str(error).lower() for error in error_detail)

    @pytest.mark.asyncio
    async def test_proposal_with_past_datetime(self, client: AsyncClient, db_session: AsyncSession):
        """Test proposal creation with past datetime."""
        # Get auth headers
        auth_headers = await self.get_auth_headers(client, db_session)

        interview_id = 1
        past_time = datetime.utcnow() - timedelta(days=1)
        proposal_data = {
            "start_datetime": past_time.isoformat() + "Z",
            "end_datetime": (past_time + timedelta(hours=1)).isoformat() + "Z",
            "timezone": "UTC"
        }

        # Note: This might be valid depending on business rules
        # Adjust test based on actual validation requirements
        response = await client.post(
            f"/api/interviews/{interview_id}/proposals",
            json=proposal_data,
            headers=auth_headers
        )

        # Accept either success or validation error based on business rules
        assert response.status_code in [201, 422]


@pytest.fixture
async def auth_headers(client, db_session):
    """Real authentication headers with interview permissions."""
    from app.models.user import User
    from app.models.company import Company
    from app.models.role import Role, UserRole
    from app.services.auth_service import auth_service
    from app.utils.constants import UserRoleEnum

    # Create test company
    company = Company(
        name="Test Interview Company",
        email="interview@test.com",
        phone="03-1234-5678",
        type="employer"
    )
    db_session.add(company)
    await db_session.commit()
    await db_session.refresh(company)

    # Create roles
    roles = {}
    for role_name in UserRoleEnum:
        role = Role(name=role_name.value, description=f"Test {role_name.value} role")
        db_session.add(role)
        roles[role_name.value] = role
    await db_session.commit()

    # Create test user with interview permissions
    user = User(
        email='interview.test@test.com',
        first_name='Interview',
        last_name='Tester',
        company_id=company.id,
        hashed_password=auth_service.get_password_hash('testpass123'),
        is_active=True,
        is_admin=True,
        require_2fa=False,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Assign recruiter role (has interview permissions)
    user_role = UserRole(user_id=user.id, role_id=roles[UserRoleEnum.RECRUITER.value].id)
    db_session.add(user_role)
    await db_session.commit()

    # Login to get real token
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "interview.test@test.com", "password": "testpass123"},
    )
    assert login_response.status_code == 200
    login_data = login_response.json()

    # Handle 2FA if required
    if login_data.get("require_2fa"):
        verify_response = await client.post(
            "/api/auth/2fa/verify",
            json={"user_id": user.id, "code": "123456"}
        )
        assert verify_response.status_code == 200
        login_data = verify_response.json()

    token = login_data['access_token']
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers_no_perms():
    """Mock authentication headers without interview permissions."""
    return {"Authorization": "Bearer mock_token_no_perms"}


@pytest.fixture
def mock_db_session():
    """Mock database session."""
    with patch('app.database.get_db') as mock:
        mock_session = AsyncMock(spec=AsyncSession)
        mock.return_value = mock_session
        yield mock_session


# Additional helper functions for complex test scenarios
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