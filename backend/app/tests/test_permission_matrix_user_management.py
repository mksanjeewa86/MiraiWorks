"""
Comprehensive permission matrix tests for user management endpoints.

Tests the permission boundaries between:
- Super Admin: Can manage all users across all companies
- Company Admin: Can only manage users within their company
- Recruiter/Employer/Candidate: Cannot manage users
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import Company
from app.models.role import UserRole
from app.models.user import User
from app.services.auth_service import auth_service
from app.utils.constants import UserRole as UserRoleEnum


class TestUserManagementPermissionMatrix:
    """Comprehensive tests for user management permission boundaries."""

    # ===== SUPER ADMIN PERMISSIONS =====

    @pytest.mark.asyncio
    async def test_super_admin_can_create_users_any_company(
        self, client: AsyncClient, super_admin_auth_headers: dict, test_company: Company
    ):
        """Test that Super Admin can create users for any company."""
        user_data = {
            "email": "newuser@example.com",
            "first_name": "New",
            "last_name": "User",
            "company_id": test_company.id,
            "role": "candidate",
        }

        response = await client.post(
            "/api/admin/users", json=user_data, headers=super_admin_auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["company_id"] == user_data["company_id"]

    @pytest.mark.asyncio
    async def test_super_admin_can_view_users_any_company(
        self, client: AsyncClient, super_admin_auth_headers: dict, test_company: Company
    ):
        """Test that Super Admin can view users from any company."""
        response = await client.get(
            f"/api/admin/users?company_id={test_company.id}",
            headers=super_admin_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "users" in data

    @pytest.mark.asyncio
    async def test_super_admin_can_update_users_any_company(
        self, client: AsyncClient, super_admin_auth_headers: dict, test_user: User
    ):
        """Test that Super Admin can update users from any company."""
        update_data = {"first_name": "Updated by Super Admin"}

        response = await client.put(
            f"/api/admin/users/{test_user.id}",
            json=update_data,
            headers=super_admin_auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == update_data["first_name"]

    @pytest.mark.asyncio
    async def test_super_admin_can_delete_users_any_company(
        self,
        client: AsyncClient,
        super_admin_auth_headers: dict,
        db_session: AsyncSession,
        test_company: Company,
    ):
        """Test that Super Admin can delete users from any company."""
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

        response = await client.delete(
            f"/api/admin/users/{temp_user.id}", headers=super_admin_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "deleted" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_super_admin_can_suspend_users_any_company(
        self, client: AsyncClient, super_admin_auth_headers: dict, test_user: User
    ):
        """Test that Super Admin can suspend users from any company."""
        suspend_data = {"reason": "Super Admin suspension"}

        response = await client.post(
            f"/api/admin/users/{test_user.id}/suspend",
            json=suspend_data,
            headers=super_admin_auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "suspended" in data["message"].lower()

    # ===== COMPANY ADMIN SCOPED PERMISSIONS =====

    @pytest.mark.asyncio
    async def test_company_admin_can_view_own_company_users_only(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Company Admin can only view users from their own company."""
        # Create company admin
        company_admin = await self._create_company_admin(
            db_session, test_company, test_roles, "companyadmin@test.com"
        )

        # Create another company with users
        other_company = await self._create_other_company(db_session)

        headers = await self._get_auth_headers(client, company_admin)

        # Should be able to view own company users
        response = await client.get(
            f"/api/admin/users?company_id={test_company.id}", headers=headers
        )
        assert response.status_code == 200

        # Should NOT be able to view other company users
        response = await client.get(
            f"/api/admin/users?company_id={other_company.id}", headers=headers
        )
        assert response.status_code == 403
        assert "other companies" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_company_admin_can_create_users_own_company_only(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Company Admin can only create users for their own company."""
        company_admin = await self._create_company_admin(
            db_session, test_company, test_roles, "companyadmin@test.com"
        )
        other_company = await self._create_other_company(db_session)
        headers = await self._get_auth_headers(client, company_admin)

        # Should be able to create user for own company
        user_data = {
            "email": "newuser@company.com",
            "first_name": "New",
            "last_name": "User",
            "company_id": test_company.id,
            "role": "candidate",
        }

        response = await client.post(
            "/api/admin/users", json=user_data, headers=headers
        )
        assert response.status_code == 201

        # Should NOT be able to create user for other company
        user_data["email"] = "otheruser@company.com"
        user_data["company_id"] = other_company.id

        response = await client.post(
            "/api/admin/users", json=user_data, headers=headers
        )
        assert response.status_code == 403
        assert "other companies" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_company_admin_can_update_own_company_users_only(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Company Admin can only update users from their own company."""
        company_admin = await self._create_company_admin(
            db_session, test_company, test_roles, "companyadmin@test.com"
        )
        other_company = await self._create_other_company(db_session)

        # Create user in other company
        other_user = await self._create_user_in_company(db_session, other_company)

        headers = await self._get_auth_headers(client, company_admin)
        update_data = {"first_name": "Updated"}

        # Should NOT be able to update user from other company
        response = await client.put(
            f"/api/admin/users/{other_user.id}", json=update_data, headers=headers
        )
        assert response.status_code == 403
        assert "other companies" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_company_admin_can_delete_own_company_users_only(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Company Admin can only delete users from their own company."""
        company_admin = await self._create_company_admin(
            db_session, test_company, test_roles, "companyadmin@test.com"
        )
        other_company = await self._create_other_company(db_session)
        other_user = await self._create_user_in_company(db_session, other_company)

        headers = await self._get_auth_headers(client, company_admin)

        # Should NOT be able to delete user from other company
        response = await client.delete(
            f"/api/admin/users/{other_user.id}", headers=headers
        )
        assert response.status_code == 403
        assert "other companies" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_company_admin_can_suspend_own_company_users_only(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Company Admin can only suspend users from their own company."""
        company_admin = await self._create_company_admin(
            db_session, test_company, test_roles, "companyadmin@test.com"
        )
        other_company = await self._create_other_company(db_session)
        other_user = await self._create_user_in_company(db_session, other_company)

        headers = await self._get_auth_headers(client, company_admin)
        suspend_data = {"reason": "Test suspension"}

        # Should NOT be able to suspend user from other company
        response = await client.post(
            f"/api/admin/users/{other_user.id}/suspend",
            json=suspend_data,
            headers=headers,
        )
        assert response.status_code == 403
        assert "other companies" in response.json()["detail"].lower()

    # ===== ROLE ASSIGNMENT RESTRICTIONS =====

    @pytest.mark.asyncio
    async def test_company_admin_cannot_assign_super_admin_role(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Company Admin cannot assign super_admin role."""
        company_admin = await self._create_company_admin(
            db_session, test_company, test_roles, "companyadmin@test.com"
        )
        headers = await self._get_auth_headers(client, company_admin)

        user_data = {
            "email": "newuser@example.com",
            "first_name": "New",
            "last_name": "User",
            "company_id": test_company.id,
            "roles": ["system_admin"],
        }

        response = await client.post(
            "/api/admin/users", json=user_data, headers=headers
        )

        assert response.status_code == 403
        assert "system_admin" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_company_admin_cannot_update_to_super_admin_role(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Company Admin cannot update user to super_admin role."""
        company_admin = await self._create_company_admin(
            db_session, test_company, test_roles, "companyadmin@test.com"
        )
        regular_user = await self._create_user_in_company(db_session, test_company)

        headers = await self._get_auth_headers(client, company_admin)
        update_data = {"roles": ["system_admin"]}

        response = await client.put(
            f"/api/admin/users/{regular_user.id}", json=update_data, headers=headers
        )

        assert response.status_code == 403
        assert "system_admin" in response.json()["detail"].lower()

    # ===== NON-ADMIN ROLE RESTRICTIONS =====

    @pytest.mark.asyncio
    async def test_recruiter_cannot_create_users(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Recruiter cannot create users."""
        recruiter = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.MEMBER, "recruiter@test.com"
        )
        headers = await self._get_auth_headers(client, recruiter)

        user_data = {
            "email": "newuser@example.com",
            "first_name": "New",
            "last_name": "User",
            "company_id": test_company.id,
            "role": "candidate",
        }

        response = await client.post(
            "/api/admin/users", json=user_data, headers=headers
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_recruiter_cannot_update_users(
        self, client: AsyncClient, db_session: AsyncSession, test_company: Company, test_roles: dict
    ):
        """Test that Recruiter cannot update users."""
        recruiter = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.MEMBER, "recruiter@test.com"
        )
        target_user = await self._create_user_in_company(db_session, test_company)

        headers = await self._get_auth_headers(client, recruiter)
        update_data = {"first_name": "Updated"}

        response = await client.put(
            f"/api/admin/users/{target_user.id}", json=update_data, headers=headers
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_recruiter_cannot_delete_users(
        self, client: AsyncClient, db_session: AsyncSession, test_company: Company, test_roles: dict
    ):
        """Test that Recruiter cannot delete users."""
        recruiter = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.MEMBER, "recruiter@test.com"
        )
        target_user = await self._create_user_in_company(db_session, test_company)

        headers = await self._get_auth_headers(client, recruiter)

        response = await client.delete(
            f"/api/admin/users/{target_user.id}", headers=headers
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_recruiter_cannot_suspend_users(
        self, client: AsyncClient, db_session: AsyncSession, test_company: Company, test_roles: dict
    ):
        """Test that Recruiter cannot suspend users."""
        recruiter = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.MEMBER, "recruiter@test.com"
        )
        target_user = await self._create_user_in_company(db_session, test_company)

        headers = await self._get_auth_headers(client, recruiter)
        suspend_data = {"reason": "Test suspension"}

        response = await client.post(
            f"/api/admin/users/{target_user.id}/suspend",
            json=suspend_data,
            headers=headers,
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_recruiter_cannot_view_users(
        self, client: AsyncClient, db_session: AsyncSession, test_company: Company, test_roles: dict
    ):
        """Test that Recruiter cannot view user management endpoints."""
        recruiter = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.MEMBER, "recruiter@test.com"
        )
        headers = await self._get_auth_headers(client, recruiter)

        response = await client.get("/api/admin/users", headers=headers)
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_employer_cannot_manage_users(
        self, client: AsyncClient, db_session: AsyncSession, test_company: Company, test_roles: dict
    ):
        """Test that Employer cannot perform any user management operations."""
        employer = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.MEMBER, "employer@test.com"
        )
        target_user = await self._create_user_in_company(db_session, test_company)
        headers = await self._get_auth_headers(client, employer)

        # Cannot view users
        response = await client.get("/api/admin/users", headers=headers)
        assert response.status_code == 403

        # Cannot create users
        user_data = {
            "email": "newuser@example.com",
            "first_name": "New",
            "last_name": "User",
            "company_id": test_company.id,
            "role": "candidate",
        }
        response = await client.post("/api/admin/users", json=user_data, headers=headers)
        assert response.status_code == 403

        # Cannot update users
        response = await client.put(
            f"/api/admin/users/{target_user.id}",
            json={"first_name": "Updated"},
            headers=headers,
        )
        assert response.status_code == 403

        # Cannot delete users
        response = await client.delete(f"/api/admin/users/{target_user.id}", headers=headers)
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_candidate_cannot_manage_users(
        self, client: AsyncClient, db_session: AsyncSession, test_company: Company, test_roles: dict
    ):
        """Test that Candidate cannot perform any user management operations."""
        candidate = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.CANDIDATE, "candidate@test.com"
        )
        target_user = await self._create_user_in_company(db_session, test_company)
        headers = await self._get_auth_headers(client, candidate)

        # Cannot view users
        response = await client.get("/api/admin/users", headers=headers)
        assert response.status_code == 403

        # Cannot create users
        user_data = {
            "email": "newuser@example.com",
            "first_name": "New",
            "last_name": "User",
            "company_id": test_company.id,
            "role": "candidate",
        }
        response = await client.post("/api/admin/users", json=user_data, headers=headers)
        assert response.status_code == 403

        # Cannot update users
        response = await client.put(
            f"/api/admin/users/{target_user.id}",
            json={"first_name": "Updated"},
            headers=headers,
        )
        assert response.status_code == 403

        # Cannot delete users
        response = await client.delete(f"/api/admin/users/{target_user.id}", headers=headers)
        assert response.status_code == 403

    # ===== BULK OPERATIONS PERMISSION TESTS =====

    @pytest.mark.asyncio
    async def test_company_admin_bulk_operations_own_company_only(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Company Admin bulk operations are restricted to own company."""
        company_admin = await self._create_company_admin(
            db_session, test_company, test_roles, "companyadmin@test.com"
        )
        other_company = await self._create_other_company(db_session)
        other_user = await self._create_user_in_company(db_session, other_company)

        headers = await self._get_auth_headers(client, company_admin)

        # Should NOT be able to bulk suspend users from other company
        bulk_data = {"user_ids": [other_user.id], "reason": "Bulk suspension test"}
        response = await client.post(
            "/api/admin/users/bulk/suspend", json=bulk_data, headers=headers
        )
        assert response.status_code == 403

        # Should NOT be able to bulk delete users from other company
        bulk_data = {"user_ids": [other_user.id]}
        response = await client.post(
            "/api/admin/users/bulk/delete", json=bulk_data, headers=headers
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_non_admin_roles_cannot_bulk_operations(
        self, client: AsyncClient, db_session: AsyncSession, test_company: Company, test_roles: dict
    ):
        """Test that non-admin roles cannot perform bulk operations."""
        recruiter = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.MEMBER, "recruiter@test.com"
        )
        target_user = await self._create_user_in_company(db_session, test_company)
        headers = await self._get_auth_headers(client, recruiter)

        bulk_data = {"user_ids": [target_user.id]}

        # Cannot bulk suspend
        bulk_data["reason"] = "Test"
        response = await client.post(
            "/api/admin/users/bulk/suspend", json=bulk_data, headers=headers
        )
        assert response.status_code == 403

        # Cannot bulk delete
        del bulk_data["reason"]
        response = await client.post(
            "/api/admin/users/bulk/delete", json=bulk_data, headers=headers
        )
        assert response.status_code == 403

        # Cannot bulk reset password
        response = await client.post(
            "/api/admin/users/bulk/reset-password", json=bulk_data, headers=headers
        )
        assert response.status_code == 403

    # ===== HELPER METHODS =====

    async def _create_company_admin(
        self, db_session: AsyncSession, company: Company, test_roles: dict, email: str
    ) -> User:
        """Create a company admin user."""
        return await self._create_user_with_role(
            db_session, company, test_roles, UserRoleEnum.ADMIN, email
        )

    async def _create_user_with_role(
        self,
        db_session: AsyncSession,
        company: Company,
        test_roles: dict,
        role: UserRoleEnum,
        email: str,
    ) -> User:
        """Create a user with specified role."""
        user = User(
            email=email,
            first_name="Test",
            last_name="User",
            company_id=company.id,
            hashed_password=auth_service.get_password_hash("testpass123"),
            is_active=True,
            is_admin=(role in [UserRoleEnum.SYSTEM_ADMIN, UserRoleEnum.ADMIN]),
            require_2fa=False,
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        # Assign role
        user_role = UserRole(
            user_id=user.id,
            role_id=test_roles[role.value].id,
        )
        db_session.add(user_role)
        await db_session.commit()

        return user

    async def _create_other_company(self, db_session: AsyncSession) -> Company:
        """Create another company for cross-company testing."""
        from app.models.company import Company
        from app.utils.constants import CompanyType

        other_company = Company(
            name="Other Test Company",
            email="other@test.com",
            phone="090-9876-5432",
            type=CompanyType.EMPLOYER,
        )
        db_session.add(other_company)
        await db_session.commit()
        await db_session.refresh(other_company)
        return other_company

    async def _create_user_in_company(
        self, db_session: AsyncSession, company: Company
    ) -> User:
        """Create a regular user in specified company."""
        user = User(
            email=f"user{company.id}@test.com",
            first_name="Test",
            last_name="User",
            company_id=company.id,
            hashed_password=auth_service.get_password_hash("testpass123"),
            is_active=True,
            require_2fa=False,
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        return user

    async def _get_auth_headers(self, client: AsyncClient, user: User) -> dict:
        """Get authentication headers for a user."""
        login_response = await client.post(
            "/api/auth/login",
            json={"email": user.email, "password": "testpass123"},
        )
        assert login_response.status_code == 200
        token_data = login_response.json()

        # Handle 2FA if required
        if token_data.get("require_2fa"):
            verify_response = await client.post(
                "/api/auth/2fa/verify",
                json={"user_id": user.id, "code": "123456"},
            )
            assert verify_response.status_code == 200
            token_data = verify_response.json()

        return {"Authorization": f"Bearer {token_data['access_token']}"}
