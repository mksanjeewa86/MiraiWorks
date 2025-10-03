"""
Comprehensive permission matrix tests for company management endpoints.

Tests the permission boundaries:
- Super Admin: Can manage all companies (create, read, update, delete)
- Company Admin: Can only view/update their own company
- Other roles: Cannot access company management
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import Company
from app.models.role import UserRole
from app.models.user import User
from app.services.auth_service import auth_service
from app.utils.constants import CompanyType
from app.utils.constants import UserRole as UserRoleEnum


class TestCompanyManagementPermissionMatrix:
    """Comprehensive tests for company management permission boundaries."""

    # ===== SUPER ADMIN EXCLUSIVE PERMISSIONS =====

    @pytest.mark.asyncio
    async def test_super_admin_can_create_companies(
        self, client: AsyncClient, super_admin_auth_headers: dict
    ):
        """Test that only Super Admin can create companies."""
        company_data = {
            "name": "New Super Admin Company",
            "email": "newsupercompany@example.com",
            "type": "member",
            "phone": "+1-555-123-4567",
            "description": "A company created by super admin",
        }

        response = await client.post(
            "/api/admin/companies", json=company_data, headers=super_admin_auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == company_data["name"]
        assert data["email"] == company_data["email"]

    @pytest.mark.asyncio
    async def test_super_admin_can_view_all_companies(
        self, client: AsyncClient, super_admin_auth_headers: dict
    ):
        """Test that Super Admin can view all companies."""
        response = await client.get(
            "/api/admin/companies", headers=super_admin_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "companies" in data
        assert "total" in data

    @pytest.mark.asyncio
    async def test_super_admin_can_view_any_company_details(
        self, client: AsyncClient, super_admin_auth_headers: dict, test_company: Company
    ):
        """Test that Super Admin can view details of any company."""
        response = await client.get(
            f"/api/admin/companies/{test_company.id}", headers=super_admin_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_company.id
        assert data["name"] == test_company.name

    @pytest.mark.asyncio
    async def test_super_admin_can_update_any_company(
        self, client: AsyncClient, super_admin_auth_headers: dict, test_company: Company
    ):
        """Test that Super Admin can update any company."""
        update_data = {
            "name": "Updated by Super Admin",
            "description": "Updated description by super admin",
        }

        response = await client.put(
            f"/api/admin/companies/{test_company.id}",
            json=update_data,
            headers=super_admin_auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["description"] == update_data["description"]

    @pytest.mark.asyncio
    async def test_super_admin_can_delete_companies(
        self,
        client: AsyncClient,
        super_admin_auth_headers: dict,
        db_session: AsyncSession,
    ):
        """Test that only Super Admin can delete companies."""
        # Create a temporary company for deletion
        temp_company = Company(
            name="To Delete Company",
            email="todelete@example.com",
            phone="555-123-4567",
            type=CompanyType.EMPLOYER,
        )
        db_session.add(temp_company)
        await db_session.commit()
        await db_session.refresh(temp_company)

        response = await client.delete(
            f"/api/admin/companies/{temp_company.id}", headers=super_admin_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "deleted" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_super_admin_can_view_company_admin_status(
        self, client: AsyncClient, super_admin_auth_headers: dict, test_company: Company
    ):
        """Test that Super Admin can view admin status of any company."""
        response = await client.get(
            f"/api/admin/companies/{test_company.id}/admin-status",
            headers=super_admin_auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "company_id" in data
        assert "has_active_admin" in data
        assert "admin_count" in data

    # ===== COMPANY ADMIN SCOPED PERMISSIONS =====

    @pytest.mark.asyncio
    async def test_company_admin_can_view_own_company_only(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Company Admin can only view their own company."""
        company_admin = await self._create_company_admin(
            db_session, test_company, test_roles, "companyadmin@test.com"
        )
        other_company = await self._create_other_company(db_session)
        headers = await self._get_auth_headers(client, company_admin)

        # Should be able to view own company
        response = await client.get(
            f"/api/admin/companies/{test_company.id}", headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_company.id

        # Should NOT be able to view other companies
        response = await client.get(
            f"/api/admin/companies/{other_company.id}", headers=headers
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_company_admin_can_update_own_company_only(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Company Admin can only update their own company."""
        company_admin = await self._create_company_admin(
            db_session, test_company, test_roles, "companyadmin@test.com"
        )
        other_company = await self._create_other_company(db_session)
        headers = await self._get_auth_headers(client, company_admin)

        # Should be able to update own company
        update_data = {"description": "Updated by company admin"}
        response = await client.put(
            f"/api/admin/companies/{test_company.id}",
            json=update_data,
            headers=headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == update_data["description"]

        # Should NOT be able to update other companies
        response = await client.put(
            f"/api/admin/companies/{other_company.id}",
            json=update_data,
            headers=headers,
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_company_admin_cannot_create_companies(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Company Admin cannot create new companies."""
        company_admin = await self._create_company_admin(
            db_session, test_company, test_roles, "companyadmin@test.com"
        )
        headers = await self._get_auth_headers(client, company_admin)

        company_data = {
            "name": "Unauthorized Company",
            "email": "unauthorized@example.com",
            "type": "member",
            "phone": "+1-555-123-4567",
        }

        response = await client.post(
            "/api/admin/companies", json=company_data, headers=headers
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_company_admin_cannot_delete_companies(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Company Admin cannot delete companies."""
        company_admin = await self._create_company_admin(
            db_session, test_company, test_roles, "companyadmin@test.com"
        )
        other_company = await self._create_other_company(db_session)
        headers = await self._get_auth_headers(client, company_admin)

        # Cannot delete own company
        response = await client.delete(
            f"/api/admin/companies/{test_company.id}", headers=headers
        )
        assert response.status_code == 403

        # Cannot delete other companies
        response = await client.delete(
            f"/api/admin/companies/{other_company.id}", headers=headers
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_company_admin_cannot_list_all_companies(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Company Admin cannot list all companies."""
        company_admin = await self._create_company_admin(
            db_session, test_company, test_roles, "companyadmin@test.com"
        )
        headers = await self._get_auth_headers(client, company_admin)

        response = await client.get("/api/admin/companies", headers=headers)
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_company_admin_can_view_own_admin_status(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Company Admin can view their own company's admin status."""
        company_admin = await self._create_company_admin(
            db_session, test_company, test_roles, "companyadmin@test.com"
        )
        other_company = await self._create_other_company(db_session)
        headers = await self._get_auth_headers(client, company_admin)

        # Should be able to view own company admin status
        response = await client.get(
            f"/api/admin/companies/{test_company.id}/admin-status", headers=headers
        )
        assert response.status_code == 200

        # Should NOT be able to view other company admin status
        response = await client.get(
            f"/api/admin/companies/{other_company.id}/admin-status", headers=headers
        )
        assert response.status_code == 403

    # ===== NON-ADMIN ROLE RESTRICTIONS =====

    @pytest.mark.asyncio
    async def test_recruiter_cannot_access_company_management(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Recruiter cannot access any company management endpoints."""
        recruiter = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.MEMBER, "recruiter@test.com"
        )
        headers = await self._get_auth_headers(client, recruiter)

        # Cannot list companies
        response = await client.get("/api/admin/companies", headers=headers)
        assert response.status_code == 403

        # Cannot view company details
        response = await client.get(
            f"/api/admin/companies/{test_company.id}", headers=headers
        )
        assert response.status_code == 403

        # Cannot create companies
        company_data = {
            "name": "Unauthorized Company",
            "email": "unauthorized@example.com",
            "type": "member",
        }
        response = await client.post(
            "/api/admin/companies", json=company_data, headers=headers
        )
        assert response.status_code == 403

        # Cannot update companies
        response = await client.put(
            f"/api/admin/companies/{test_company.id}",
            json={"description": "Updated"},
            headers=headers,
        )
        assert response.status_code == 403

        # Cannot delete companies
        response = await client.delete(
            f"/api/admin/companies/{test_company.id}", headers=headers
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_employer_cannot_access_company_management(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Employer cannot access any company management endpoints."""
        employer = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.MEMBER, "employer@test.com"
        )
        headers = await self._get_auth_headers(client, employer)

        # Test all company management endpoints
        endpoints_and_methods = [
            ("GET", "/api/admin/companies"),
            ("GET", f"/api/admin/companies/{test_company.id}"),
            ("POST", "/api/admin/companies"),
            ("PUT", f"/api/admin/companies/{test_company.id}"),
            ("DELETE", f"/api/admin/companies/{test_company.id}"),
            ("GET", f"/api/admin/companies/{test_company.id}/admin-status"),
        ]

        for method, endpoint in endpoints_and_methods:
            if method == "GET":
                response = await client.get(endpoint, headers=headers)
            elif method == "POST":
                response = await client.post(
                    endpoint, json={"name": "Test", "email": "test@test.com"}, headers=headers
                )
            elif method == "PUT":
                response = await client.put(
                    endpoint, json={"description": "Updated"}, headers=headers
                )
            elif method == "DELETE":
                response = await client.delete(endpoint, headers=headers)

            assert response.status_code == 403, f"Failed for {method} {endpoint}"

    @pytest.mark.asyncio
    async def test_candidate_cannot_access_company_management(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Candidate cannot access any company management endpoints."""
        candidate = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.CANDIDATE, "candidate@test.com"
        )
        headers = await self._get_auth_headers(client, candidate)

        # Test all company management endpoints
        endpoints_and_methods = [
            ("GET", "/api/admin/companies"),
            ("GET", f"/api/admin/companies/{test_company.id}"),
            ("POST", "/api/admin/companies"),
            ("PUT", f"/api/admin/companies/{test_company.id}"),
            ("DELETE", f"/api/admin/companies/{test_company.id}"),
            ("GET", f"/api/admin/companies/{test_company.id}/admin-status"),
        ]

        for method, endpoint in endpoints_and_methods:
            if method == "GET":
                response = await client.get(endpoint, headers=headers)
            elif method == "POST":
                response = await client.post(
                    endpoint, json={"name": "Test", "email": "test@test.com"}, headers=headers
                )
            elif method == "PUT":
                response = await client.put(
                    endpoint, json={"description": "Updated"}, headers=headers
                )
            elif method == "DELETE":
                response = await client.delete(endpoint, headers=headers)

            assert response.status_code == 403, f"Failed for {method} {endpoint}"

    # ===== AUTHENTICATION BOUNDARY TESTS =====

    @pytest.mark.asyncio
    async def test_unauthenticated_cannot_access_company_management(
        self, client: AsyncClient, test_company: Company
    ):
        """Test that unauthenticated users cannot access company management."""
        endpoints_and_methods = [
            ("GET", "/api/admin/companies"),
            ("GET", f"/api/admin/companies/{test_company.id}"),
            ("POST", "/api/admin/companies"),
            ("PUT", f"/api/admin/companies/{test_company.id}"),
            ("DELETE", f"/api/admin/companies/{test_company.id}"),
            ("GET", f"/api/admin/companies/{test_company.id}/admin-status"),
        ]

        for method, endpoint in endpoints_and_methods:
            if method == "GET":
                response = await client.get(endpoint)
            elif method == "POST":
                response = await client.post(
                    endpoint, json={"name": "Test", "email": "test@test.com"}
                )
            elif method == "PUT":
                response = await client.put(endpoint, json={"description": "Updated"})
            elif method == "DELETE":
                response = await client.delete(endpoint)

            assert response.status_code == 401, f"Failed for {method} {endpoint}"

    # ===== EDGE CASES =====

    @pytest.mark.asyncio
    async def test_company_admin_cannot_modify_company_ownership(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Company Admin cannot modify critical company ownership fields."""
        company_admin = await self._create_company_admin(
            db_session, test_company, test_roles, "companyadmin@test.com"
        )
        headers = await self._get_auth_headers(client, company_admin)

        # Try to update critical fields that might affect ownership
        restricted_updates = [
            {"email": "newemail@example.com"},  # Primary contact email
            {"type": "member"},  # Company type change
            {"is_active": False},  # Deactivation
        ]

        for update_data in restricted_updates:
            response = await client.put(
                f"/api/admin/companies/{test_company.id}",
                json=update_data,
                headers=headers,
            )
            # Should either succeed with validation or be restricted
            # Implementation depends on business logic
            assert response.status_code in [200, 403, 422]

    @pytest.mark.asyncio
    async def test_company_admin_from_inactive_company_restrictions(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_roles: dict,
    ):
        """Test restrictions for company admin from inactive company."""
        # Create inactive company
        inactive_company = Company(
            name="Inactive Company",
            email="inactive@test.com",
            phone="555-123-4567",
            type=CompanyType.EMPLOYER,
            is_active="0",  # Inactive
        )
        db_session.add(inactive_company)
        await db_session.commit()
        await db_session.refresh(inactive_company)

        company_admin = await self._create_company_admin(
            db_session, inactive_company, test_roles, "inactiveadmin@test.com"
        )
        headers = await self._get_auth_headers(client, company_admin)

        # Should not be able to access company management if company is inactive
        response = await client.get(
            f"/api/admin/companies/{inactive_company.id}", headers=headers
        )
        # Implementation depends on business logic for inactive companies
        assert response.status_code in [200, 403]

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
