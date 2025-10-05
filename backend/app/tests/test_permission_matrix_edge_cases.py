from datetime import datetime, timedelta, timezone

import pytest
from httpx import AsyncClient
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.attachment import Attachment
from app.models.company import Company
from app.models.user import User
from app.schemas.user import UserRole
from app.services.auth_service import AuthService


class TestPermissionMatrixEdgeCases:
    """
    Edge case tests for permission matrix scenarios.
    Tests token expiration, role changes, account deactivation, and complex permission scenarios.
    """

    @pytest.fixture
    async def setup_edge_case_scenario(self, db: AsyncSession):
        """Setup complex scenario for edge case testing."""

        # Create test company
        company = Company(
            name="EdgeCase Corp",
            description="Company for edge case testing",
            industry="Technology",
            size="medium",
            location="Tokyo",
            is_active=True,
        )
        db.add(company)
        await db.flush()

        # Create Super Admin
        super_admin = User(
            email="superadmin@system.com",
            hashed_password="hashed_password",
            company_id=None,
            role=UserRole.SUPER_ADMIN,
            is_active=True,
            is_verified=True,
            first_name="Super",
            last_name="Admin",
        )
        db.add(super_admin)

        # Create Company Admin
        company_admin = User(
            email="admin@edgecase.com",
            hashed_password="hashed_password",
            company_id=company.id,
            role=UserRole.COMPANY_ADMIN,
            is_active=True,
            is_verified=True,
            first_name="Company",
            last_name="Admin",
        )
        db.add(company_admin)

        # Create Recruiter
        recruiter = User(
            email="recruiter@edgecase.com",
            hashed_password="hashed_password",
            company_id=company.id,
            role=UserRole.RECRUITER,
            is_active=True,
            is_verified=True,
            first_name="Test",
            last_name="Recruiter",
        )
        db.add(recruiter)

        # Create Candidate
        candidate = User(
            email="candidate@email.com",
            hashed_password="hashed_password",
            company_id=None,
            role=UserRole.CANDIDATE,
            is_active=True,
            is_verified=True,
            first_name="Test",
            last_name="Candidate",
        )
        db.add(candidate)

        # Create inactive user
        inactive_user = User(
            email="inactive@edgecase.com",
            hashed_password="hashed_password",
            company_id=company.id,
            role=UserRole.RECRUITER,
            is_active=False,
            is_verified=True,
            first_name="Inactive",
            last_name="User",
        )
        db.add(inactive_user)

        # Create unverified user
        unverified_user = User(
            email="unverified@edgecase.com",
            hashed_password="hashed_password",
            company_id=company.id,
            role=UserRole.EMPLOYER,
            is_active=True,
            is_verified=False,
            first_name="Unverified",
            last_name="User",
        )
        db.add(unverified_user)

        await db.commit()
        await db.refresh(company)
        await db.refresh(super_admin)
        await db.refresh(company_admin)
        await db.refresh(recruiter)
        await db.refresh(candidate)
        await db.refresh(inactive_user)
        await db.refresh(unverified_user)

        return {
            "company": company,
            "system_admin": super_admin,
            "admin": company_admin,
            "member": recruiter,
            "candidate": candidate,
            "inactive_user": inactive_user,
            "unverified_user": unverified_user,
        }

    def _create_auth_headers(self, user: User) -> dict:
        """Create authentication headers for a user."""
        auth_service = AuthService()
        access_token = auth_service.create_access_token(data={"sub": user.email})
        return {"Authorization": f"Bearer {access_token}"}

    def _create_expired_token(self, user: User) -> str:
        """Create an expired JWT token for testing."""
        from app.config import settings

        # Create token that expired 1 hour ago
        expire = datetime.now(timezone.utc) - timedelta(hours=1)
        to_encode = {"sub": user.email, "exp": expire}

        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")

    def _create_malformed_token(self) -> str:
        """Create a malformed JWT token for testing."""
        return "malformed.jwt.token.here"

    async def test_expired_token_access_denied(
        self, client: AsyncClient, setup_edge_case_scenario: dict
    ):
        """Test that expired tokens are rejected."""
        scenario = setup_edge_case_scenario
        expired_token = self._create_expired_token(scenario["admin"])
        headers = {"Authorization": f"Bearer {expired_token}"}

        # Try to access protected endpoint with expired token
        response = await client.get("/api/admin/users", headers=headers)
        assert response.status_code == 401

        # Try to create user with expired token
        user_data = {
            "email": "newuser@edgecase.com",
            "role": "member",
            "company_id": scenario["company"].id,
        }

        response = await client.post(
            "/api/admin/users", json=user_data, headers=headers
        )
        assert response.status_code == 401

    async def test_malformed_token_access_denied(
        self, client: AsyncClient, setup_edge_case_scenario: dict
    ):
        """Test that malformed tokens are rejected."""
        malformed_token = self._create_malformed_token()
        headers = {"Authorization": f"Bearer {malformed_token}"}

        # Try to access protected endpoint with malformed token
        response = await client.get("/api/admin/users", headers=headers)
        assert response.status_code == 401

        # Try to create position with malformed token
        position_data = {
            "title": "Software Engineer",
            "description": "Great opportunity",
        }

        response = await client.post(
            "/api/positions", json=position_data, headers=headers
        )
        assert response.status_code == 401

    async def test_inactive_user_access_denied(
        self, client: AsyncClient, setup_edge_case_scenario: dict
    ):
        """Test that inactive users cannot access resources."""
        scenario = setup_edge_case_scenario
        inactive_headers = self._create_auth_headers(scenario["inactive_user"])

        # Try to access users endpoint
        response = await client.get("/api/admin/users", headers=inactive_headers)
        assert response.status_code == 401

        # Try to create position
        position_data = {"title": "Backend Developer", "description": "Backend role"}

        response = await client.post(
            "/api/positions", json=position_data, headers=inactive_headers
        )
        assert response.status_code == 401

    async def test_unverified_user_access_restrictions(
        self, client: AsyncClient, setup_edge_case_scenario: dict
    ):
        """Test that unverified users have limited access."""
        scenario = setup_edge_case_scenario
        unverified_headers = self._create_auth_headers(scenario["unverified_user"])

        # Unverified users should not access admin endpoints
        response = await client.get("/api/admin/users", headers=unverified_headers)
        assert response.status_code == 401

        # Unverified users should not create positions
        position_data = {"title": "Data Scientist", "description": "Data science role"}

        response = await client.post(
            "/api/positions", json=position_data, headers=unverified_headers
        )
        assert response.status_code == 401

    async def test_role_change_permission_update(
        self, client: AsyncClient, db: AsyncSession, setup_edge_case_scenario: dict
    ):
        """Test that permissions are updated when user role changes."""
        scenario = setup_edge_case_scenario
        super_admin_headers = self._create_auth_headers(scenario["system_admin"])

        # Recruiter initially can create positions
        recruiter_headers = self._create_auth_headers(scenario["member"])
        position_data = {
            "title": "Initial Position",
            "description": "Position before role change",
        }

        response = await client.post(
            "/api/positions", json=position_data, headers=recruiter_headers
        )
        assert response.status_code == 201

        # Change recruiter to candidate
        update_data = {"role": "candidate"}
        response = await client.put(
            f"/api/admin/users/{scenario['recruiter'].id}",
            json=update_data,
            headers=super_admin_headers,
        )
        assert response.status_code == 200

        # Refresh the recruiter object to get updated role
        await db.refresh(scenario["member"])

        # Create new auth headers with updated role
        updated_headers = self._create_auth_headers(scenario["member"])

        # Now as candidate, should not be able to create positions
        position_data = {
            "title": "Position After Role Change",
            "description": "This should fail",
        }

        response = await client.post(
            "/api/positions", json=position_data, headers=updated_headers
        )
        assert response.status_code == 403

    async def test_company_deactivation_access_denied(
        self, client: AsyncClient, db: AsyncSession, setup_edge_case_scenario: dict
    ):
        """Test that users from deactivated companies cannot access resources."""
        scenario = setup_edge_case_scenario
        super_admin_headers = self._create_auth_headers(scenario["system_admin"])

        # Company admin initially can access users
        admin_headers = self._create_auth_headers(scenario["admin"])
        response = await client.get("/api/admin/users", headers=admin_headers)
        assert response.status_code == 200

        # Deactivate the company
        company_update = {"is_active": False}
        response = await client.put(
            f"/api/admin/companies/{scenario['company'].id}",
            json=company_update,
            headers=super_admin_headers,
        )
        assert response.status_code == 200

        # Refresh company object
        await db.refresh(scenario["company"])

        # Now company admin should not be able to access resources
        response = await client.get("/api/admin/users", headers=admin_headers)
        assert response.status_code == 403

    async def test_concurrent_permission_checks(
        self, client: AsyncClient, setup_edge_case_scenario: dict
    ):
        """Test permission checks under concurrent access scenarios."""
        scenario = setup_edge_case_scenario
        admin_headers = self._create_auth_headers(scenario["admin"])
        recruiter_headers = self._create_auth_headers(scenario["member"])

        # Multiple users trying to create positions simultaneously
        position_data_1 = {
            "title": "Concurrent Position 1",
            "description": "First concurrent position",
        }
        position_data_2 = {
            "title": "Concurrent Position 2",
            "description": "Second concurrent position",
        }

        # Both should succeed (both have permission)
        import asyncio

        responses = await asyncio.gather(
            client.post("/api/positions", json=position_data_1, headers=admin_headers),
            client.post(
                "/api/positions", json=position_data_2, headers=recruiter_headers
            ),
            return_exceptions=True,
        )

        assert responses[0].status_code == 201
        assert responses[1].status_code == 201

    async def test_permission_boundary_at_resource_limits(
        self, client: AsyncClient, db: AsyncSession, setup_edge_case_scenario: dict
    ):
        """Test permissions at resource limits and quotas."""
        scenario = setup_edge_case_scenario
        admin_headers = self._create_auth_headers(scenario["admin"])

        # Test creating maximum allowed resources
        # Company admin should be able to create multiple users up to limit
        for i in range(5):  # Assuming limit of 5 for testing
            user_data = {
                "email": f"user{i}@edgecase.com",
                "role": "candidate",
                "company_id": scenario["company"].id,
                "first_name": f"User{i}",
                "last_name": "Test",
            }

            response = await client.post(
                "/api/admin/users", json=user_data, headers=admin_headers
            )
            assert response.status_code == 201

    async def test_cross_functional_permission_validation(
        self, client: AsyncClient, db: AsyncSession, setup_edge_case_scenario: dict
    ):
        """Test complex scenarios involving multiple functional areas."""
        scenario = setup_edge_case_scenario

        # Create position
        recruiter_headers = self._create_auth_headers(scenario["member"])
        position_data = {"title": "Full Stack Developer", "description": "Complex role"}

        position_response = await client.post(
            "/api/positions", json=position_data, headers=recruiter_headers
        )
        assert position_response.status_code == 201
        position = position_response.json()

        # Create interview for the position
        interview_data = {
            "position_id": position["id"],
            "candidate_id": scenario["candidate"].id,
            "scheduled_at": "2024-02-01T10:00:00",
            "duration_minutes": 60,
            "interview_type": "technical",
        }

        interview_response = await client.post(
            "/api/interviews", json=interview_data, headers=recruiter_headers
        )
        assert interview_response.status_code == 201
        interview = interview_response.json()

        # Candidate should be able to view their interview
        candidate_headers = self._create_auth_headers(scenario["candidate"])
        response = await client.get(
            f"/api/interviews/{interview['id']}", headers=candidate_headers
        )
        assert response.status_code == 200

        # But candidate should not be able to modify the interview
        update_data = {"status": "completed"}
        response = await client.put(
            f"/api/interviews/{interview['id']}",
            json=update_data,
            headers=candidate_headers,
        )
        assert response.status_code == 403

    async def test_permission_inheritance_edge_cases(
        self, client: AsyncClient, setup_edge_case_scenario: dict
    ):
        """Test edge cases in permission inheritance."""
        scenario = setup_edge_case_scenario

        # Super admin should inherit all company admin permissions
        super_admin_headers = self._create_auth_headers(scenario["system_admin"])

        # Create user in company (should work as Super Admin)
        user_data = {
            "email": "inherited@edgecase.com",
            "role": "member",
            "company_id": scenario["company"].id,
            "first_name": "Inherited",
            "last_name": "User",
        }

        response = await client.post(
            "/api/admin/users", json=user_data, headers=super_admin_headers
        )
        assert response.status_code == 201

        # Super admin should also have recruiter permissions
        position_data = {
            "title": "Inherited Position",
            "description": "Position created by Super Admin",
        }

        response = await client.post(
            "/api/positions", json=position_data, headers=super_admin_headers
        )
        assert response.status_code == 201

    async def test_nested_resource_permission_validation(
        self, client: AsyncClient, db: AsyncSession, setup_edge_case_scenario: dict
    ):
        """Test permissions on nested resources."""
        scenario = setup_edge_case_scenario

        # Create a file
        recruiter_headers = self._create_auth_headers(scenario["member"])
        file_info = Attachment(
            original_filename="Test Document.pdf",
            s3_key="test/documents/test_document.pdf",
            s3_bucket="test-bucket",
            file_size=1024,
            mime_type="application/pdf",
            sha256_hash="1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
            owner_id=scenario["member"].id,
            is_available=True,
        )
        db.add(file_info)
        await db.commit()
        await db.refresh(file_info)

        # Create todo that references the file
        todo_data = {
            "title": "Review Document",
            "description": "Review the uploaded document",
            "assigned_to": scenario["member"].id,
            "related_file_id": file_info.id,
            "priority": "medium",
            "due_date": "2024-02-01",
        }

        company_admin_headers = self._create_auth_headers(scenario["admin"])
        todo_response = await client.post(
            "/api/todos", json=todo_data, headers=company_admin_headers
        )
        assert todo_response.status_code == 201

        # Assigned user should be able to view both todo and file
        response = await client.get(
            f"/api/todos/{todo_response.json()['id']}", headers=recruiter_headers
        )
        assert response.status_code == 200

        response = await client.get(
            f"/api/attachments/{file_info.id}", headers=recruiter_headers
        )
        assert response.status_code == 200

        # Candidate should not be able to access either
        candidate_headers = self._create_auth_headers(scenario["candidate"])
        response = await client.get(
            f"/api/todos/{todo_response.json()['id']}", headers=candidate_headers
        )
        assert response.status_code == 403

        response = await client.get(
            f"/api/attachments/{file_info.id}", headers=candidate_headers
        )
        assert response.status_code == 403

    async def test_api_rate_limiting_permission_interaction(
        self, client: AsyncClient, setup_edge_case_scenario: dict
    ):
        """Test interaction between rate limiting and permissions."""
        scenario = setup_edge_case_scenario
        candidate_headers = self._create_auth_headers(scenario["candidate"])

        # Make multiple rapid requests that should be forbidden
        # Even with rate limiting, permissions should be checked first
        for _i in range(10):
            response = await client.get("/api/admin/users", headers=candidate_headers)
            assert (
                response.status_code == 403
            )  # Should be permission error, not rate limit

    async def test_session_invalidation_edge_cases(
        self, client: AsyncClient, db: AsyncSession, setup_edge_case_scenario: dict
    ):
        """Test edge cases around session invalidation."""
        scenario = setup_edge_case_scenario
        recruiter_headers = self._create_auth_headers(scenario["member"])

        # User can initially access resource
        response = await client.get("/api/positions", headers=recruiter_headers)
        assert response.status_code == 200

        # Deactivate user
        super_admin_headers = self._create_auth_headers(scenario["system_admin"])
        update_data = {"is_active": False}
        response = await client.put(
            f"/api/admin/users/{scenario['recruiter'].id}",
            json=update_data,
            headers=super_admin_headers,
        )
        assert response.status_code == 200

        # Refresh user object
        await db.refresh(scenario["member"])

        # Same token should now be invalid
        response = await client.get("/api/positions", headers=recruiter_headers)
        assert response.status_code == 401

    async def test_permission_matrix_boundary_transitions(
        self, client: AsyncClient, db: AsyncSession, setup_edge_case_scenario: dict
    ):
        """Test transitions between different permission states."""
        scenario = setup_edge_case_scenario
        super_admin_headers = self._create_auth_headers(scenario["system_admin"])

        # Create a user with minimum permissions (candidate)
        minimal_user = User(
            email="minimal@edgecase.com",
            hashed_password="hashed_password",
            company_id=None,
            role=UserRole.CANDIDATE,
            is_active=True,
            is_verified=True,
            first_name="Minimal",
            last_name="User",
        )
        db.add(minimal_user)
        await db.commit()
        await db.refresh(minimal_user)

        minimal_headers = self._create_auth_headers(minimal_user)

        # Candidate cannot access admin functions
        response = await client.get("/api/admin/users", headers=minimal_headers)
        assert response.status_code == 403

        # Promote to recruiter
        update_data = {"role": "member", "company_id": scenario["company"].id}
        response = await client.put(
            f"/api/admin/users/{minimal_user.id}",
            json=update_data,
            headers=super_admin_headers,
        )
        assert response.status_code == 200

        # Refresh user and create new headers
        await db.refresh(minimal_user)
        updated_headers = self._create_auth_headers(minimal_user)

        # Now can create positions
        position_data = {
            "title": "Promoted User Position",
            "description": "Position after promotion",
        }
        response = await client.post(
            "/api/positions", json=position_data, headers=updated_headers
        )
        assert response.status_code == 201

        # But still cannot access all admin functions
        response = await client.get("/api/admin/companies", headers=updated_headers)
        assert response.status_code == 403

    async def test_permission_matrix_data_consistency(
        self, client: AsyncClient, db: AsyncSession, setup_edge_case_scenario: dict
    ):
        """Test data consistency in permission-controlled operations."""
        scenario = setup_edge_case_scenario
        admin_headers = self._create_auth_headers(scenario["admin"])

        # Create user and immediately try to assign permissions
        user_data = {
            "email": "consistency@edgecase.com",
            "role": "member",
            "company_id": scenario["company"].id,
            "first_name": "Consistency",
            "last_name": "Test",
        }

        user_response = await client.post(
            "/api/admin/users", json=user_data, headers=admin_headers
        )
        assert user_response.status_code == 201
        new_user = user_response.json()

        # Immediately try to create a todo for the new user
        todo_data = {
            "title": "Welcome Task",
            "description": "First task for new user",
            "assigned_to": new_user["id"],
            "priority": "low",
            "due_date": "2024-02-15",
        }

        todo_response = await client.post(
            "/api/todos", json=todo_data, headers=admin_headers
        )
        assert todo_response.status_code == 201

        # Verify the new user can access their assigned todo
        new_user_headers = self._create_auth_headers(
            User(
                id=new_user["id"],
                email=new_user["email"],
                role=UserRole.RECRUITER,
                company_id=scenario["company"].id,
            )
        )

        response = await client.get(
            f"/api/todos/{todo_response.json()['id']}", headers=new_user_headers
        )
        assert response.status_code == 200
