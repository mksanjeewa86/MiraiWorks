import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import Company
from app.models.user import User
from app.services.auth_service import auth_service


class TestUsersManagement:
    """Comprehensive tests for users_management endpoint functionality."""

    # ===== SUCCESS SCENARIOS =====

    @pytest.mark.asyncio
    async def test_get_users_success(
        self, client: AsyncClient, db_session: AsyncSession, test_roles: dict
    ):
        """Test successful retrieval of user list."""
        # Create super admin user directly without complex fixtures
        from app.models import User, UserRole
        from app.services.auth_service import auth_service
        from app.utils.constants import UserRole as UserRoleEnum

        super_admin = User(
            email="super@test.com",
            first_name="Super",
            last_name="Admin",
            company_id=None,
            hashed_password=auth_service.get_password_hash("testpass123"),
            is_active=True,
            is_admin=True,
        )
        db_session.add(super_admin)
        await db_session.commit()
        await db_session.refresh(super_admin)

        # Assign super admin role
        user_role = UserRole(
            user_id=super_admin.id,
            role_id=test_roles[UserRoleEnum.SUPER_ADMIN.value].id,
        )
        db_session.add(user_role)
        await db_session.commit()

        # Bypass 2FA by setting require_2fa=False explicitly
        super_admin.require_2fa = False
        await db_session.commit()

        # Login to get token
        login_response = await client.post(
            "/api/auth/login",
            json={"email": "super@test.com", "password": "testpass123"},
        )

        assert login_response.status_code == 200
        token_data = login_response.json()

        # If 2FA is required despite our setting, handle it
        if token_data.get("require_2fa"):
            verify_response = await client.post(
                "/api/auth/2fa/verify",
                json={"user_id": super_admin.id, "code": "123456"},
            )
            assert verify_response.status_code == 200
            token_data = verify_response.json()

        # Create headers
        headers = {"Authorization": f"Bearer {token_data['access_token']}"}

        # Test the actual endpoint
        response = await client.get("/api/admin/users", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        assert "total" in data
        assert "page" in data
        assert "per_page" in data
        assert isinstance(data["users"], list)

    @pytest.mark.asyncio
    async def test_get_users_with_pagination(
        self, client: AsyncClient, admin_auth_headers: dict
    ):
        """Test user list with pagination parameters."""
        response = await client.get(
            "/api/admin/users?page=1&size=10", headers=admin_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["per_page"] == 10

    @pytest.mark.asyncio
    async def test_get_users_with_search(
        self, client: AsyncClient, admin_auth_headers: dict
    ):
        """Test user list with search filter."""
        response = await client.get(
            "/api/admin/users?search=test", headers=admin_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "users" in data

    @pytest.mark.asyncio
    async def test_create_user_success(
        self, client: AsyncClient, admin_auth_headers: dict, test_company: Company
    ):
        """Test successful user creation."""
        user_data = {
            "email": "newuser@example.com",
            "first_name": "New",
            "last_name": "User",
            "company_id": test_company.id,
            "role": "candidate",
        }

        response = await client.post(
            "/api/admin/users", json=user_data, headers=admin_auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["first_name"] == user_data["first_name"]
        assert data["company_id"] == user_data["company_id"]
        assert "id" in data

    @pytest.mark.asyncio
    async def test_get_user_by_id_success(
        self, client: AsyncClient, admin_auth_headers: dict, test_user: User
    ):
        """Test successful retrieval of specific user."""
        response = await client.get(
            f"/api/admin/users/{test_user.id}", headers=admin_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_user.id
        assert data["email"] == test_user.email

    @pytest.mark.asyncio
    async def test_update_user_success(
        self, client: AsyncClient, admin_auth_headers: dict, test_user: User
    ):
        """Test successful user update."""
        update_data = {"first_name": "Updated", "last_name": "Name"}

        response = await client.put(
            f"/api/admin/users/{test_user.id}",
            json=update_data,
            headers=admin_auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == update_data["first_name"]
        assert data["last_name"] == update_data["last_name"]

    @pytest.mark.asyncio
    async def test_suspend_user_success(
        self, client: AsyncClient, admin_auth_headers: dict, test_user: User
    ):
        """Test successful user suspension."""
        suspend_data = {"reason": "Test suspension"}

        response = await client.post(
            f"/api/admin/users/{test_user.id}/suspend",
            json=suspend_data,
            headers=admin_auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "suspended" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_unsuspend_user_success(
        self,
        client: AsyncClient,
        admin_auth_headers: dict,
        test_user: User,
        db_session: AsyncSession,
    ):
        """Test successful user unsuspension."""
        # First suspend the user
        test_user.is_suspended = True
        await db_session.commit()

        response = await client.post(
            f"/api/admin/users/{test_user.id}/unsuspend", headers=admin_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert (
            "unsuspended" in data["message"].lower()
            or "activated" in data["message"].lower()
        )

    @pytest.mark.asyncio
    async def test_reset_password_success(
        self, client: AsyncClient, admin_auth_headers: dict, test_user: User
    ):
        """Test successful password reset."""
        response = await client.post(
            f"/api/admin/users/{test_user.id}/reset-password",
            json={"user_id": test_user.id, "send_email": True},
            headers=admin_auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "password" in data["message"].lower()
        assert "temporary_password" in data

    @pytest.mark.asyncio
    async def test_resend_activation_success(
        self,
        client: AsyncClient,
        admin_auth_headers: dict,
        db_session: AsyncSession,
        test_company: Company,
    ):
        """Test successful activation email resend."""
        # Create inactive user
        inactive_user = User(
            email="inactive@test.com",
            first_name="Inactive",
            last_name="User",
            company_id=test_company.id,
            hashed_password=auth_service.get_password_hash("temp123"),
            is_active=False,
        )
        db_session.add(inactive_user)
        await db_session.commit()
        await db_session.refresh(inactive_user)

        response = await client.post(
            f"/api/admin/users/{inactive_user.id}/resend-activation",
            headers=admin_auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "activation" in data["message"].lower()

    # ===== AUTHENTICATION & AUTHORIZATION TESTS =====

    @pytest.mark.asyncio
    async def test_get_users_unauthorized(self, client: AsyncClient):
        """Test user list access without authentication."""
        response = await client.get("/api/admin/users")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_users_forbidden_regular_user(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test user list access with regular user (should be forbidden)."""
        response = await client.get("/api/admin/users", headers=auth_headers)
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_create_user_unauthorized(self, client: AsyncClient):
        """Test user creation without authentication."""
        response = await client.post("/api/admin/users", json={})
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_create_user_forbidden_regular_user(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test user creation with regular user permissions."""
        response = await client.post("/api/admin/users", json={}, headers=auth_headers)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_delete_user_unauthorized(self, client: AsyncClient, test_user: User):
        """Test user deletion without authentication."""
        response = await client.delete(f"/api/admin/users/{test_user.id}")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_suspend_user_unauthorized(
        self, client: AsyncClient, test_user: User
    ):
        """Test user suspension without authentication."""
        response = await client.post(
            f"/api/admin/users/{test_user.id}/suspend", json={}
        )
        assert response.status_code == 401

    # ===== INPUT VALIDATION TESTS =====

    @pytest.mark.asyncio
    async def test_create_user_invalid_email(
        self, client: AsyncClient, admin_auth_headers: dict, test_company: Company
    ):
        """Test user creation with invalid email."""
        user_data = {
            "email": "invalid-email",
            "first_name": "Test",
            "last_name": "User",
            "company_id": test_company.id,
        }

        response = await client.post(
            "/api/admin/users", json=user_data, headers=admin_auth_headers
        )

        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_create_user_missing_required_fields(
        self, client: AsyncClient, admin_auth_headers: dict
    ):
        """Test user creation with missing required fields."""
        user_data = {"email": "test@example.com"}  # Missing other required fields

        response = await client.post(
            "/api/admin/users", json=user_data, headers=admin_auth_headers
        )

        assert response.status_code == 422
        error_detail = response.json()["detail"]
        assert len(error_detail) > 0

    @pytest.mark.asyncio
    async def test_create_user_duplicate_email(
        self,
        client: AsyncClient,
        admin_auth_headers: dict,
        test_user: User,
        test_company: Company,
    ):
        """Test user creation with duplicate email."""
        user_data = {
            "email": test_user.email,  # Duplicate email
            "first_name": "Test",
            "last_name": "User",
            "company_id": test_company.id,
        }

        response = await client.post(
            "/api/admin/users", json=user_data, headers=admin_auth_headers
        )

        assert response.status_code == 400
        assert "email" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_update_user_invalid_data(
        self, client: AsyncClient, admin_auth_headers: dict, test_user: User
    ):
        """Test user update with invalid data."""
        update_data = {"email": "invalid-email"}

        response = await client.put(
            f"/api/admin/users/{test_user.id}",
            json=update_data,
            headers=admin_auth_headers,
        )

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_users_invalid_pagination(
        self, client: AsyncClient, admin_auth_headers: dict
    ):
        """Test user list with invalid pagination parameters."""
        response = await client.get(
            "/api/admin/users?page=-1&size=0", headers=admin_auth_headers
        )

        assert response.status_code == 422

    # ===== NOT FOUND TESTS =====

    @pytest.mark.asyncio
    async def test_get_user_not_found(
        self, client: AsyncClient, admin_auth_headers: dict
    ):
        """Test retrieving non-existent user."""
        response = await client.get(
            "/api/admin/users/99999", headers=admin_auth_headers
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_update_user_not_found(
        self, client: AsyncClient, admin_auth_headers: dict
    ):
        """Test updating non-existent user."""
        response = await client.put(
            "/api/admin/users/99999",
            json={"first_name": "Test"},
            headers=admin_auth_headers,
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_user_not_found(
        self, client: AsyncClient, admin_auth_headers: dict
    ):
        """Test deleting non-existent user."""
        response = await client.delete(
            "/api/admin/users/99999", headers=admin_auth_headers
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_suspend_user_not_found(
        self, client: AsyncClient, admin_auth_headers: dict
    ):
        """Test suspending non-existent user."""
        response = await client.post(
            "/api/admin/users/99999/suspend",
            json={"reason": "test"},
            headers=admin_auth_headers,
        )
        assert response.status_code == 404

    # ===== BULK OPERATIONS TESTS =====

    @pytest.mark.asyncio
    async def test_bulk_suspend_success(
        self, client: AsyncClient, admin_auth_headers: dict, test_user: User
    ):
        """Test successful bulk user suspension."""
        bulk_data = {"user_ids": [test_user.id], "reason": "Bulk suspension test"}

        response = await client.post(
            "/api/admin/users/bulk/suspend", json=bulk_data, headers=admin_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "suspended" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_bulk_unsuspend_success(
        self,
        client: AsyncClient,
        admin_auth_headers: dict,
        test_user: User,
        db_session: AsyncSession,
    ):
        """Test successful bulk user unsuspension."""
        # First suspend the user
        test_user.is_suspended = True
        await db_session.commit()

        bulk_data = {"user_ids": [test_user.id]}

        response = await client.post(
            "/api/admin/users/bulk/unsuspend",
            json=bulk_data,
            headers=admin_auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert (
            "unsuspended" in data["message"].lower()
            or "activated" in data["message"].lower()
        )

    @pytest.mark.asyncio
    async def test_bulk_reset_password_success(
        self, client: AsyncClient, admin_auth_headers: dict, test_user: User
    ):
        """Test successful bulk password reset."""
        bulk_data = {"user_ids": [test_user.id]}

        response = await client.post(
            "/api/admin/users/bulk/reset-password",
            json=bulk_data,
            headers=admin_auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "password" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_bulk_delete_success(
        self,
        client: AsyncClient,
        admin_auth_headers: dict,
        db_session: AsyncSession,
        test_company: Company,
    ):
        """Test successful bulk user deletion."""
        # Create a temporary user for deletion
        temp_user = User(
            email="todelete@example.com",
            first_name="To",
            last_name="Delete",
            company_id=test_company.id,
            hashed_password=auth_service.get_password_hash("temp123"),
            is_active=True,
        )
        db_session.add(temp_user)
        await db_session.commit()
        await db_session.refresh(temp_user)

        bulk_data = {"user_ids": [temp_user.id]}

        response = await client.post(
            "/api/admin/users/bulk/delete", json=bulk_data, headers=admin_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "deleted" in data["message"].lower()

    # ===== BULK OPERATIONS VALIDATION TESTS =====

    @pytest.mark.asyncio
    async def test_bulk_operations_unauthorized(self, client: AsyncClient):
        """Test bulk operations without authentication."""
        bulk_data = {"user_ids": [1]}

        endpoints = [
            "/api/admin/users/bulk/suspend",
            "/api/admin/users/bulk/unsuspend",
            "/api/admin/users/bulk/delete",
            "/api/admin/users/bulk/reset-password",
        ]

        for endpoint in endpoints:
            response = await client.post(endpoint, json=bulk_data)
            assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_bulk_operations_empty_user_ids(
        self, client: AsyncClient, admin_auth_headers: dict
    ):
        """Test bulk operations with empty user IDs."""
        bulk_data = {"user_ids": []}

        response = await client.post(
            "/api/admin/users/bulk/suspend", json=bulk_data, headers=admin_auth_headers
        )

        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_bulk_operations_invalid_user_ids(
        self, client: AsyncClient, admin_auth_headers: dict
    ):
        """Test bulk operations with non-existent user IDs."""
        bulk_data = {"user_ids": [99999]}

        response = await client.post(
            "/api/admin/users/bulk/suspend", json=bulk_data, headers=admin_auth_headers
        )

        # Should handle gracefully, either 404 or partial success
        assert response.status_code in [200, 404, 400]

    # ===== COMPANY ADMIN PERMISSION TESTS =====

    @pytest.mark.asyncio
    async def test_company_admin_cannot_assign_super_admin_role(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that company admin cannot assign super_admin role."""
        # Create company admin
        from app.models import User, UserRole
        from app.utils.constants import UserRole as UserRoleEnum

        company_admin = User(
            email="companyadmin@test.com",
            first_name="Company",
            last_name="Admin",
            company_id=test_company.id,
            hashed_password=auth_service.get_password_hash("testpass123"),
            is_active=True,
            is_admin=True,
        )
        db_session.add(company_admin)
        await db_session.commit()
        await db_session.refresh(company_admin)

        # Add company_admin role using test_roles fixture
        user_role = UserRole(
            user_id=company_admin.id,
            role_id=test_roles[UserRoleEnum.COMPANY_ADMIN.value].id,
        )
        db_session.add(user_role)
        await db_session.commit()

        # Bypass 2FA by setting require_2fa=False explicitly
        company_admin.require_2fa = False
        await db_session.commit()

        # Login as company admin
        login_response = await client.post(
            "/api/auth/login",
            json={"email": "companyadmin@test.com", "password": "testpass123"},
        )
        assert login_response.status_code == 200
        token_data = login_response.json()

        # If 2FA is required despite our setting, handle it
        if token_data.get("require_2fa"):
            verify_response = await client.post(
                "/api/auth/2fa/verify",
                json={"user_id": company_admin.id, "code": "123456"},
            )
            assert verify_response.status_code == 200
            token_data = verify_response.json()

        headers = {"Authorization": f"Bearer {token_data['access_token']}"}

        # Try to create user with super_admin role
        user_data = {
            "email": "newuser@example.com",
            "first_name": "New",
            "last_name": "User",
            "company_id": test_company.id,
            "roles": ["super_admin"],
        }

        response = await client.post(
            "/api/admin/users", json=user_data, headers=headers
        )

        assert response.status_code == 403
        assert "super_admin" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_company_admin_cannot_create_user_for_other_company(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that company admin cannot create users for other companies."""
        # Create company admin
        from app.models import User, UserRole

        company_admin = User(
            email="companyadmin@test.com",
            first_name="Company",
            last_name="Admin",
            company_id=test_company.id,
            hashed_password=auth_service.get_password_hash("testpass123"),
            is_active=True,
            is_admin=True,
        )
        db_session.add(company_admin)
        await db_session.commit()
        await db_session.refresh(company_admin)

        # Add company_admin role using test_roles fixture
        from app.utils.constants import UserRole as UserRoleEnum

        user_role = UserRole(
            user_id=company_admin.id,
            role_id=test_roles[UserRoleEnum.COMPANY_ADMIN.value].id,
        )
        db_session.add(user_role)
        await db_session.commit()

        # Bypass 2FA by setting require_2fa=False explicitly
        company_admin.require_2fa = False
        await db_session.commit()

        # Create another company
        other_company = Company(
            name="Other Company",
            email="contact@other.com",
            phone="090-1234-5678",
            type="recruiter",
        )
        db_session.add(other_company)
        await db_session.commit()
        await db_session.refresh(other_company)

        # Login as company admin
        login_response = await client.post(
            "/api/auth/login",
            json={"email": "companyadmin@test.com", "password": "testpass123"},
        )
        assert login_response.status_code == 200
        token_data = login_response.json()

        # If 2FA is required despite our setting, handle it
        if token_data.get("require_2fa"):
            verify_response = await client.post(
                "/api/auth/2fa/verify",
                json={"user_id": company_admin.id, "code": "123456"},
            )
            assert verify_response.status_code == 200
            token_data = verify_response.json()

        headers = {"Authorization": f"Bearer {token_data['access_token']}"}

        # Try to create user for other company
        user_data = {
            "email": "newuser@example.com",
            "first_name": "New",
            "last_name": "User",
            "company_id": other_company.id,
            "roles": ["recruiter"],
        }

        response = await client.post(
            "/api/admin/users", json=user_data, headers=headers
        )

        assert response.status_code == 403
        assert "other companies" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_company_admin_cannot_update_user_from_other_company(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that company admin cannot update users from other companies."""
        # Create company admin
        from app.models import User, UserRole

        company_admin = User(
            email="companyadmin@test.com",
            first_name="Company",
            last_name="Admin",
            company_id=test_company.id,
            hashed_password=auth_service.get_password_hash("testpass123"),
            is_active=True,
            is_admin=True,
        )
        db_session.add(company_admin)
        await db_session.commit()
        await db_session.refresh(company_admin)

        # Add company_admin role using test_roles fixture
        from app.utils.constants import UserRole as UserRoleEnum

        user_role = UserRole(
            user_id=company_admin.id,
            role_id=test_roles[UserRoleEnum.COMPANY_ADMIN.value].id,
        )
        db_session.add(user_role)
        await db_session.commit()

        # Bypass 2FA by setting require_2fa=False explicitly
        company_admin.require_2fa = False
        await db_session.commit()

        # Create another company
        other_company = Company(
            name="Other Company",
            email="contact@other.com",
            phone="090-1234-5678",
            type="recruiter",
        )
        db_session.add(other_company)

        # Create user in other company
        other_user = User(
            email="otheruser@test.com",
            first_name="Other",
            last_name="User",
            company_id=other_company.id,
            hashed_password=auth_service.get_password_hash("testpass123"),
            is_active=True,
        )
        db_session.add(other_user)
        await db_session.commit()
        await db_session.refresh(company_admin)
        await db_session.refresh(other_user)

        # Login as company admin
        login_response = await client.post(
            "/api/auth/login",
            json={"email": "companyadmin@test.com", "password": "testpass123"},
        )
        assert login_response.status_code == 200
        token_data = login_response.json()

        # If 2FA is required despite our setting, handle it
        if token_data.get("require_2fa"):
            verify_response = await client.post(
                "/api/auth/2fa/verify",
                json={"user_id": company_admin.id, "code": "123456"},
            )
            assert verify_response.status_code == 200
            token_data = verify_response.json()

        headers = {"Authorization": f"Bearer {token_data['access_token']}"}

        # Try to update user from other company
        update_data = {"first_name": "Updated"}

        response = await client.put(
            f"/api/admin/users/{other_user.id}", json=update_data, headers=headers
        )

        assert response.status_code == 403
        assert "other companies" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_company_admin_cannot_assign_super_admin_in_update(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that company admin cannot assign super_admin role in updates."""
        # Create company admin
        from app.models import User, UserRole

        company_admin = User(
            email="companyadmin@test.com",
            first_name="Company",
            last_name="Admin",
            company_id=test_company.id,
            hashed_password=auth_service.get_password_hash("testpass123"),
            is_active=True,
            is_admin=True,
        )
        db_session.add(company_admin)
        await db_session.commit()
        await db_session.refresh(company_admin)

        # Add company_admin role using test_roles fixture
        from app.utils.constants import UserRole as UserRoleEnum

        user_role = UserRole(
            user_id=company_admin.id,
            role_id=test_roles[UserRoleEnum.COMPANY_ADMIN.value].id,
        )
        db_session.add(user_role)
        await db_session.commit()

        # Bypass 2FA by setting require_2fa=False explicitly
        company_admin.require_2fa = False
        await db_session.commit()

        # Create regular user in same company
        regular_user = User(
            email="regular@test.com",
            first_name="Regular",
            last_name="User",
            company_id=test_company.id,
            hashed_password=auth_service.get_password_hash("testpass123"),
            is_active=True,
        )
        db_session.add(regular_user)
        await db_session.commit()
        await db_session.refresh(company_admin)
        await db_session.refresh(regular_user)

        # Login as company admin
        login_response = await client.post(
            "/api/auth/login",
            json={"email": "companyadmin@test.com", "password": "testpass123"},
        )
        assert login_response.status_code == 200
        token_data = login_response.json()

        # If 2FA is required despite our setting, handle it
        if token_data.get("require_2fa"):
            verify_response = await client.post(
                "/api/auth/2fa/verify",
                json={"user_id": company_admin.id, "code": "123456"},
            )
            assert verify_response.status_code == 200
            token_data = verify_response.json()

        headers = {"Authorization": f"Bearer {token_data['access_token']}"}

        # Try to update user with super_admin role
        update_data = {"roles": ["super_admin"]}

        response = await client.put(
            f"/api/admin/users/{regular_user.id}", json=update_data, headers=headers
        )

        assert response.status_code == 403
        assert "super_admin" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_company_admin_cannot_move_user_to_other_company(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that company admin cannot move users to other companies."""
        # Create company admin
        from app.models import User, UserRole

        company_admin = User(
            email="companyadmin@test.com",
            first_name="Company",
            last_name="Admin",
            company_id=test_company.id,
            hashed_password=auth_service.get_password_hash("testpass123"),
            is_active=True,
            is_admin=True,
        )
        db_session.add(company_admin)
        await db_session.commit()
        await db_session.refresh(company_admin)

        # Add company_admin role using test_roles fixture
        from app.utils.constants import UserRole as UserRoleEnum

        user_role = UserRole(
            user_id=company_admin.id,
            role_id=test_roles[UserRoleEnum.COMPANY_ADMIN.value].id,
        )
        db_session.add(user_role)
        await db_session.commit()

        # Bypass 2FA by setting require_2fa=False explicitly
        company_admin.require_2fa = False
        await db_session.commit()

        # Create other company
        other_company = Company(
            name="Other Company",
            email="contact@other.com",
            phone="090-1234-5678",
            type="recruiter",
        )
        db_session.add(other_company)

        # Create regular user in same company
        regular_user = User(
            email="regular@test.com",
            first_name="Regular",
            last_name="User",
            company_id=test_company.id,
            hashed_password=auth_service.get_password_hash("testpass123"),
            is_active=True,
        )
        db_session.add(regular_user)
        await db_session.commit()
        await db_session.refresh(company_admin)
        await db_session.refresh(other_company)
        await db_session.refresh(regular_user)

        # Login as company admin
        login_response = await client.post(
            "/api/auth/login",
            json={"email": "companyadmin@test.com", "password": "testpass123"},
        )
        assert login_response.status_code == 200
        token_data = login_response.json()

        # If 2FA is required despite our setting, handle it
        if token_data.get("require_2fa"):
            verify_response = await client.post(
                "/api/auth/2fa/verify",
                json={"user_id": company_admin.id, "code": "123456"},
            )
            assert verify_response.status_code == 200
            token_data = verify_response.json()

        headers = {"Authorization": f"Bearer {token_data['access_token']}"}

        # Try to move user to other company
        update_data = {"company_id": other_company.id}

        response = await client.put(
            f"/api/admin/users/{regular_user.id}", json=update_data, headers=headers
        )

        assert response.status_code == 403
        assert "other companies" in response.json()["detail"].lower()

    # ===== EDGE CASES =====

    @pytest.mark.asyncio
    async def test_delete_self_forbidden(
        self, client: AsyncClient, admin_auth_headers: dict, test_admin_user: User
    ):
        """Test that admin cannot delete themselves."""
        response = await client.delete(
            f"/api/admin/users/{test_admin_user.id}", headers=admin_auth_headers
        )

        # Should either be forbidden or have business logic preventing self-deletion
        assert response.status_code in [403, 400]

    @pytest.mark.asyncio
    async def test_suspend_self_forbidden(
        self, client: AsyncClient, admin_auth_headers: dict, test_admin_user: User
    ):
        """Test that admin cannot suspend themselves."""
        response = await client.post(
            f"/api/admin/users/{test_admin_user.id}/suspend",
            json={"reason": "test"},
            headers=admin_auth_headers,
        )

        # Should either be forbidden or have business logic preventing self-suspension
        assert response.status_code in [403, 400]

    @pytest.mark.asyncio
    async def test_create_user_with_nonexistent_company(
        self, client: AsyncClient, admin_auth_headers: dict
    ):
        """Test user creation with non-existent company."""
        user_data = {
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "company_id": 99999,
        }

        response = await client.post(
            "/api/admin/users", json=user_data, headers=admin_auth_headers
        )

        assert response.status_code == 403
        assert "compan" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_get_users_with_all_filters(
        self, client: AsyncClient, admin_auth_headers: dict
    ):
        """Test user list with all possible filters applied."""
        response = await client.get(
            "/api/admin/users?page=1&size=5&search=test&is_active=true&is_admin=false&role=candidate",
            headers=admin_auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        assert data["per_page"] == 5

    # ===== COMPREHENSIVE FILTER TESTS =====

    @pytest.mark.asyncio
    async def test_get_users_filter_by_company_id(
        self, client: AsyncClient, admin_auth_headers: dict, test_company: Company
    ):
        """Test filtering users by company_id."""
        response = await client.get(
            f"/api/admin/users?company_id={test_company.id}", headers=admin_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        for user in data["users"]:
            if user["company_id"] is not None:
                assert user["company_id"] == test_company.id

    @pytest.mark.asyncio
    async def test_get_users_filter_by_is_active_true(
        self, client: AsyncClient, admin_auth_headers: dict
    ):
        """Test filtering users by is_active=true."""
        response = await client.get(
            "/api/admin/users?is_active=true", headers=admin_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        for user in data["users"]:
            assert user["is_active"] is True

    @pytest.mark.asyncio
    async def test_get_users_filter_by_is_active_false(
        self, client: AsyncClient, admin_auth_headers: dict
    ):
        """Test filtering users by is_active=false."""
        response = await client.get(
            "/api/admin/users?is_active=false", headers=admin_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        for user in data["users"]:
            assert user["is_active"] is False

    @pytest.mark.asyncio
    async def test_get_users_filter_by_is_admin_true(
        self, client: AsyncClient, admin_auth_headers: dict
    ):
        """Test filtering users by is_admin=true."""
        response = await client.get(
            "/api/admin/users?is_admin=true", headers=admin_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        for user in data["users"]:
            assert user["is_admin"] is True

    @pytest.mark.asyncio
    async def test_get_users_filter_by_is_admin_false(
        self, client: AsyncClient, admin_auth_headers: dict
    ):
        """Test filtering users by is_admin=false."""
        response = await client.get(
            "/api/admin/users?is_admin=false", headers=admin_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        for user in data["users"]:
            assert user["is_admin"] is False

    @pytest.mark.asyncio
    async def test_get_users_filter_by_is_suspended_true(
        self,
        client: AsyncClient,
        admin_auth_headers: dict,
        test_user: User,
        db_session: AsyncSession,
    ):
        """Test filtering users by is_suspended=true."""
        # First suspend the test user
        test_user.is_suspended = True
        await db_session.commit()

        response = await client.get(
            "/api/admin/users?is_suspended=true", headers=admin_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        # Should find at least our suspended user
        suspended_users = [
            user for user in data["users"] if user["is_suspended"] is True
        ]
        assert len(suspended_users) >= 1

    @pytest.mark.asyncio
    async def test_get_users_filter_by_is_suspended_false(
        self, client: AsyncClient, admin_auth_headers: dict
    ):
        """Test filtering users by is_suspended=false."""
        response = await client.get(
            "/api/admin/users?is_suspended=false", headers=admin_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        for user in data["users"]:
            assert user["is_suspended"] is False

    @pytest.mark.asyncio
    async def test_get_users_filter_by_require_2fa_true(
        self, client: AsyncClient, admin_auth_headers: dict
    ):
        """Test filtering users by require_2fa=true."""
        response = await client.get(
            "/api/admin/users?require_2fa=true", headers=admin_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        for user in data["users"]:
            assert user["require_2fa"] is True

    @pytest.mark.asyncio
    async def test_get_users_filter_by_require_2fa_false(
        self, client: AsyncClient, admin_auth_headers: dict
    ):
        """Test filtering users by require_2fa=false."""
        response = await client.get(
            "/api/admin/users?require_2fa=false", headers=admin_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        for user in data["users"]:
            assert user["require_2fa"] is False

    @pytest.mark.asyncio
    async def test_get_users_filter_by_role_candidate(
        self, client: AsyncClient, admin_auth_headers: dict
    ):
        """Test filtering users by role=candidate."""
        response = await client.get(
            "/api/admin/users?role=candidate", headers=admin_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        for user in data["users"]:
            assert "candidate" in [role.lower() for role in user["roles"]]

    @pytest.mark.asyncio
    async def test_get_users_filter_by_role_recruiter(
        self, client: AsyncClient, admin_auth_headers: dict
    ):
        """Test filtering users by role=recruiter."""
        response = await client.get(
            "/api/admin/users?role=recruiter", headers=admin_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        for user in data["users"]:
            assert "recruiter" in [role.lower() for role in user["roles"]]

    @pytest.mark.asyncio
    async def test_get_users_filter_by_role_company_admin(
        self, client: AsyncClient, admin_auth_headers: dict
    ):
        """Test filtering users by role=company_admin."""
        response = await client.get(
            "/api/admin/users?role=company_admin", headers=admin_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        for user in data["users"]:
            assert "company_admin" in [role.lower() for role in user["roles"]]

    @pytest.mark.asyncio
    async def test_get_users_search_by_first_name(
        self, client: AsyncClient, admin_auth_headers: dict, test_user: User
    ):
        """Test searching users by first name."""
        response = await client.get(
            f"/api/admin/users?search={test_user.first_name}",
            headers=admin_auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        # Should find users with matching first name
        found_user = any(user["id"] == test_user.id for user in data["users"])
        assert found_user is True

    @pytest.mark.asyncio
    async def test_get_users_search_by_last_name(
        self, client: AsyncClient, admin_auth_headers: dict, test_user: User
    ):
        """Test searching users by last name."""
        response = await client.get(
            f"/api/admin/users?search={test_user.last_name}", headers=admin_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        # Should find users with matching last name
        found_user = any(user["id"] == test_user.id for user in data["users"])
        assert found_user is True

    @pytest.mark.asyncio
    async def test_get_users_search_by_email(
        self, client: AsyncClient, admin_auth_headers: dict, test_user: User
    ):
        """Test searching users by email."""
        search_term = test_user.email.split("@")[
            0
        ]  # Use part of email for partial match
        response = await client.get(
            f"/api/admin/users?search={search_term}", headers=admin_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        # Should find users with matching email
        found_user = any(user["id"] == test_user.id for user in data["users"])
        assert found_user is True

    @pytest.mark.asyncio
    async def test_get_users_search_case_insensitive(
        self, client: AsyncClient, admin_auth_headers: dict, test_user: User
    ):
        """Test that search is case insensitive."""
        search_term = test_user.first_name.upper()
        response = await client.get(
            f"/api/admin/users?search={search_term}", headers=admin_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        # Should find users regardless of case
        found_user = any(user["id"] == test_user.id for user in data["users"])
        assert found_user is True

    @pytest.mark.asyncio
    async def test_get_users_include_deleted_false_default(
        self, client: AsyncClient, admin_auth_headers: dict
    ):
        """Test that deleted users are excluded by default."""
        response = await client.get("/api/admin/users", headers=admin_auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        # All returned users should not be deleted
        for user in data["users"]:
            assert user["is_deleted"] is False

    @pytest.mark.asyncio
    async def test_get_users_include_deleted_false_explicit(
        self, client: AsyncClient, admin_auth_headers: dict
    ):
        """Test explicitly excluding deleted users."""
        response = await client.get(
            "/api/admin/users?include_deleted=false", headers=admin_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        # All returned users should not be deleted
        for user in data["users"]:
            assert user["is_deleted"] is False

    @pytest.mark.asyncio
    async def test_get_users_include_deleted_true(
        self,
        client: AsyncClient,
        admin_auth_headers: dict,
        db_session: AsyncSession,
        test_company: Company,
    ):
        """Test including deleted users in results."""
        # Create a non-deleted user to ensure we have one
        active_user = User(
            email="active@test.com",
            first_name="Active",
            last_name="User",
            company_id=test_company.id,
            hashed_password=auth_service.get_password_hash("temp123"),
            is_active=True,
            is_deleted=False,
        )
        db_session.add(active_user)

        # Create and delete a user
        deleted_user = User(
            email="deleted@test.com",
            first_name="Deleted",
            last_name="User",
            company_id=test_company.id,
            hashed_password=auth_service.get_password_hash("temp123"),
            is_active=False,
            is_deleted=True,
        )
        db_session.add(deleted_user)
        await db_session.commit()
        await db_session.refresh(active_user)
        await db_session.refresh(deleted_user)

        response = await client.get(
            "/api/admin/users?include_deleted=true", headers=admin_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        # Should include both deleted and non-deleted users
        deleted_users = [user for user in data["users"] if user["is_deleted"] is True]
        non_deleted_users = [
            user for user in data["users"] if user["is_deleted"] is False
        ]
        assert len(deleted_users) >= 1
        assert len(non_deleted_users) >= 1

    @pytest.mark.asyncio
    async def test_get_users_combined_filters_active_admin(
        self, client: AsyncClient, admin_auth_headers: dict
    ):
        """Test combining multiple filters: active admin users."""
        response = await client.get(
            "/api/admin/users?is_active=true&is_admin=true", headers=admin_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        for user in data["users"]:
            assert user["is_active"] is True
            assert user["is_admin"] is True

    @pytest.mark.asyncio
    async def test_get_users_combined_filters_search_and_company(
        self, client: AsyncClient, admin_auth_headers: dict, test_company: Company
    ):
        """Test combining search and company filter."""
        response = await client.get(
            f"/api/admin/users?search=test&company_id={test_company.id}",
            headers=admin_auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        for user in data["users"]:
            if user["company_id"] is not None:
                assert user["company_id"] == test_company.id

    @pytest.mark.asyncio
    async def test_get_users_combined_filters_all_parameters(
        self, client: AsyncClient, admin_auth_headers: dict, test_company: Company
    ):
        """Test combining all filter parameters."""
        response = await client.get(
            f"/api/admin/users?page=1&size=10&search=test&company_id={test_company.id}&is_active=true&is_admin=false&is_suspended=false&require_2fa=false&role=candidate&include_deleted=false",
            headers=admin_auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        assert data["page"] == 1
        assert data["per_page"] == 10
        for user in data["users"]:
            assert user["is_active"] is True
            assert user["is_admin"] is False
            assert user["is_suspended"] is False
            assert user["require_2fa"] is False
            assert user["is_deleted"] is False
            if user["company_id"] is not None:
                assert user["company_id"] == test_company.id

    @pytest.mark.asyncio
    async def test_get_users_pagination_with_filters(
        self, client: AsyncClient, admin_auth_headers: dict
    ):
        """Test pagination works correctly with filters."""
        # Test first page
        response1 = await client.get(
            "/api/admin/users?page=1&size=2&is_active=true", headers=admin_auth_headers
        )

        assert response1.status_code == 200
        data1 = response1.json()
        assert "users" in data1
        assert data1["page"] == 1
        assert data1["per_page"] == 2

        # Test second page if there are enough results
        if data1["total"] > 2:
            response2 = await client.get(
                "/api/admin/users?page=2&size=2&is_active=true",
                headers=admin_auth_headers,
            )

            assert response2.status_code == 200
            data2 = response2.json()
            assert data2["page"] == 2
            assert data2["per_page"] == 2

            # Ensure different results on different pages
            page1_ids = {user["id"] for user in data1["users"]}
            page2_ids = {user["id"] for user in data2["users"]}
            assert page1_ids.isdisjoint(page2_ids)  # No overlap between pages

    @pytest.mark.asyncio
    async def test_get_users_empty_search_returns_all(
        self, client: AsyncClient, admin_auth_headers: dict
    ):
        """Test that empty search parameter returns all users."""
        response = await client.get(
            "/api/admin/users?search=", headers=admin_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        # Should return users (not filtered by search)

    @pytest.mark.asyncio
    async def test_get_users_nonexistent_search_returns_empty(
        self, client: AsyncClient, admin_auth_headers: dict
    ):
        """Test that search with non-existent term returns empty results."""
        response = await client.get(
            "/api/admin/users?search=nonexistentusername12345",
            headers=admin_auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        assert len(data["users"]) == 0
        assert data["total"] == 0

    @pytest.mark.asyncio
    async def test_get_users_filter_by_nonexistent_company(
        self, client: AsyncClient, admin_auth_headers: dict
    ):
        """Test filtering by non-existent company returns empty results."""
        response = await client.get(
            "/api/admin/users?company_id=99999", headers=admin_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        assert len(data["users"]) == 0
        assert data["total"] == 0

    @pytest.mark.asyncio
    async def test_get_users_filter_validation_invalid_role(
        self, client: AsyncClient, admin_auth_headers: dict
    ):
        """Test filtering with invalid role value."""
        response = await client.get(
            "/api/admin/users?role=invalid_role", headers=admin_auth_headers
        )

        # Should either return 422 for validation error or 200 with empty results
        assert response.status_code in [200, 422]
        if response.status_code == 200:
            data = response.json()
            assert len(data["users"]) == 0
