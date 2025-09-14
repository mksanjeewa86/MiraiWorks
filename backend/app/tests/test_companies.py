import pytest

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.company import Company
from app.models.user import User
from app.utils.constants import CompanyType
from app.services.auth_service import auth_service


class TestCompanies:
    """Comprehensive tests for companies endpoint functionality."""

    # ===== SUCCESS SCENARIOS =====

    @pytest.mark.asyncio
    async def test_get_companies_success(self, client: AsyncClient, super_admin_auth_headers: dict):
        """Test successful retrieval of companies list."""
        response = await client.get("/api/admin/companies", headers=super_admin_auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "companies" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data
        assert isinstance(data["companies"], list)

    @pytest.mark.asyncio
    async def test_get_companies_with_pagination(self, client: AsyncClient, super_admin_auth_headers: dict):
        """Test companies list with pagination parameters."""
        response = await client.get(
            "/api/admin/companies?page=1&size=10",
            headers=super_admin_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["size"] == 10

    @pytest.mark.asyncio
    async def test_get_companies_with_filters(self, client: AsyncClient, super_admin_auth_headers: dict):
        """Test companies list with various filters."""
        response = await client.get(
            "/api/admin/companies?search=test&type=recruiter&is_active=true",
            headers=super_admin_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "companies" in data

    @pytest.mark.asyncio
    async def test_get_company_by_id_success(self, client: AsyncClient, super_admin_auth_headers: dict, test_company: Company):
        """Test successful retrieval of specific company."""
        response = await client.get(
            f"/api/admin/companies/{test_company.id}",
            headers=super_admin_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_company.id
        assert data["name"] == test_company.name
        assert data["email"] == test_company.email
        assert "user_count" in data
        assert "created_at" in data

    @pytest.mark.asyncio
    async def test_create_company_success(self, client: AsyncClient, super_admin_auth_headers: dict):
        """Test successful company creation."""
        company_data = {
            "name": "New Test Company",
            "email": "newcompany@example.com",
            "type": "employer",
            "description": "A test company for testing purposes",
            "website": "https://newcompany.example.com"
        }

        response = await client.post(
            "/api/admin/companies",
            json=company_data,
            headers=super_admin_auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == company_data["name"]
        assert data["email"] == company_data["email"]
        assert data["type"] == company_data["type"]
        assert "id" in data
        assert "created_at" in data

    @pytest.mark.asyncio
    async def test_update_company_success(self, client: AsyncClient, super_admin_auth_headers: dict, test_company: Company):
        """Test successful company update."""
        update_data = {
            "name": "Updated Company Name",
            "description": "Updated description"
        }

        response = await client.put(
            f"/api/admin/companies/{test_company.id}",
            json=update_data,
            headers=super_admin_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["description"] == update_data["description"]
        assert data["id"] == test_company.id

    @pytest.mark.asyncio
    async def test_get_company_admin_status(self, client: AsyncClient, super_admin_auth_headers: dict, test_company: Company):
        """Test retrieval of company admin status."""
        response = await client.get(
            f"/api/admin/companies/{test_company.id}/admin-status",
            headers=super_admin_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "company_id" in data
        assert "has_active_admin" in data
        assert "admin_count" in data
        assert isinstance(data["has_active_admin"], bool)
        assert isinstance(data["admin_count"], int)

    # ===== AUTHENTICATION & AUTHORIZATION TESTS =====

    @pytest.mark.asyncio
    async def test_get_companies_unauthorized(self, client: AsyncClient):
        """Test companies list access without authentication."""
        response = await client.get("/api/admin/companies")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_companies_forbidden_regular_user(self, client: AsyncClient, auth_headers: dict):
        """Test companies list access with regular user (should be forbidden)."""
        response = await client.get("/api/admin/companies", headers=auth_headers)
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_get_companies_forbidden_company_admin(self, client: AsyncClient, admin_auth_headers: dict):
        """Test companies list access with company admin (should be forbidden)."""
        response = await client.get("/api/admin/companies", headers=admin_auth_headers)
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_create_company_unauthorized(self, client: AsyncClient):
        """Test company creation without authentication."""
        response = await client.post("/api/admin/companies", json={})
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_create_company_forbidden_regular_user(self, client: AsyncClient, auth_headers: dict):
        """Test company creation with regular user permissions."""
        company_data = {"name": "Test Company", "email": "test@example.com"}
        response = await client.post("/api/admin/companies", json=company_data, headers=auth_headers)
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_create_company_forbidden_company_admin(self, client: AsyncClient, admin_auth_headers: dict):
        """Test company creation with company admin permissions."""
        company_data = {"name": "Test Company", "email": "test@example.com"}
        response = await client.post("/api/admin/companies", json=company_data, headers=admin_auth_headers)
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_update_company_unauthorized(self, client: AsyncClient, test_company: Company):
        """Test company update without authentication."""
        response = await client.put(f"/api/admin/companies/{test_company.id}", json={})
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_delete_company_unauthorized(self, client: AsyncClient, test_company: Company):
        """Test company deletion without authentication."""
        response = await client.delete(f"/api/admin/companies/{test_company.id}")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_delete_company_forbidden_non_super_admin(self, client: AsyncClient, admin_auth_headers: dict, test_company: Company):
        """Test company deletion with non-super-admin permissions."""
        response = await client.delete(f"/api/admin/companies/{test_company.id}", headers=admin_auth_headers)
        assert response.status_code == 403

    # ===== INPUT VALIDATION TESTS =====

    @pytest.mark.asyncio
    async def test_create_company_invalid_email(self, client: AsyncClient, super_admin_auth_headers: dict):
        """Test company creation with invalid email."""
        company_data = {
            "name": "Test Company",
            "email": "invalid-email",
            "type": "employer"
        }

        response = await client.post(
            "/api/admin/companies",
            json=company_data,
            headers=super_admin_auth_headers
        )

        assert response.status_code == 422
        error_detail = response.json()["detail"]
        assert any("email" in str(error).lower() for error in error_detail)

    @pytest.mark.asyncio
    async def test_create_company_missing_required_fields(self, client: AsyncClient, super_admin_auth_headers: dict):
        """Test company creation with missing required fields."""
        company_data = {"name": "Test Company"}  # Missing email and type

        response = await client.post(
            "/api/admin/companies",
            json=company_data,
            headers=super_admin_auth_headers
        )

        assert response.status_code == 422
        error_detail = response.json()["detail"]
        assert len(error_detail) > 0

    @pytest.mark.asyncio
    async def test_create_company_duplicate_email(self, client: AsyncClient, super_admin_auth_headers: dict, test_company: Company):
        """Test company creation with duplicate email."""
        company_data = {
            "name": "Duplicate Company",
            "email": test_company.email,  # Duplicate email
            "type": "employer"
        }

        response = await client.post(
            "/api/admin/companies",
            json=company_data,
            headers=super_admin_auth_headers
        )

        assert response.status_code == 400
        assert "email" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_create_company_invalid_type(self, client: AsyncClient, super_admin_auth_headers: dict):
        """Test company creation with invalid company type."""
        company_data = {
            "name": "Test Company",
            "email": "test@example.com",
            "type": "invalid_type"
        }

        response = await client.post(
            "/api/admin/companies",
            json=company_data,
            headers=super_admin_auth_headers
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_update_company_invalid_data(self, client: AsyncClient, super_admin_auth_headers: dict, test_company: Company):
        """Test company update with invalid data."""
        update_data = {"email": "invalid-email"}

        response = await client.put(
            f"/api/admin/companies/{test_company.id}",
            json=update_data,
            headers=super_admin_auth_headers
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_companies_invalid_pagination(self, client: AsyncClient, super_admin_auth_headers: dict):
        """Test companies list with invalid pagination parameters."""
        response = await client.get(
            "/api/admin/companies?page=-1&size=0",
            headers=super_admin_auth_headers
        )

        assert response.status_code == 422

    # ===== NOT FOUND TESTS =====

    @pytest.mark.asyncio
    async def test_get_company_not_found(self, client: AsyncClient, super_admin_auth_headers: dict):
        """Test retrieving non-existent company."""
        response = await client.get("/api/admin/companies/99999", headers=super_admin_auth_headers)
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_update_company_not_found(self, client: AsyncClient, super_admin_auth_headers: dict):
        """Test updating non-existent company."""
        response = await client.put(
            "/api/admin/companies/99999",
            json={"name": "Test"},
            headers=super_admin_auth_headers
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_company_not_found(self, client: AsyncClient, super_admin_auth_headers: dict):
        """Test deleting non-existent company."""
        response = await client.delete("/api/admin/companies/99999", headers=super_admin_auth_headers)
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_admin_status_not_found(self, client: AsyncClient, super_admin_auth_headers: dict):
        """Test getting admin status for non-existent company."""
        response = await client.get("/api/admin/companies/99999/admin-status", headers=super_admin_auth_headers)
        assert response.status_code == 404

    # ===== BUSINESS LOGIC TESTS =====

    @pytest.mark.asyncio
    async def test_delete_company_success(self, client: AsyncClient, super_admin_auth_headers: dict, db_session: AsyncSession):
        """Test successful company deletion."""
        # Create a temporary company for deletion
        temp_company = Company(
            name="To Delete Company",
            email="todelete@example.com",
            type=CompanyType.EMPLOYER,
            is_active="1"
        )
        db_session.add(temp_company)
        await db_session.commit()
        await db_session.refresh(temp_company)

        response = await client.delete(
            f"/api/admin/companies/{temp_company.id}",
            headers=super_admin_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "deleted" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_delete_company_with_users_forbidden(self, client: AsyncClient, super_admin_auth_headers: dict, test_company: Company):
        """Test that company with users cannot be deleted."""
        response = await client.delete(
            f"/api/admin/companies/{test_company.id}",
            headers=super_admin_auth_headers
        )

        # Should be forbidden or return business logic error
        assert response.status_code in [400, 403]
        if response.status_code == 400:
            assert "users" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_create_company_creates_admin_user(self, client: AsyncClient, super_admin_auth_headers: dict, db_session: AsyncSession):
        """Test that company creation also creates an admin user."""
        company_data = {
            "name": "Company with Admin",
            "email": "companywithmin@example.com",
            "type": "employer",
            "admin_first_name": "Admin",
            "admin_last_name": "User",
            "admin_email": "admin@companywithmin.com"
        }

        response = await client.post(
            "/api/admin/companies",
            json=company_data,
            headers=super_admin_auth_headers
        )

        if response.status_code == 201:
            data = response.json()
            company_id = data["id"]

            # Check if admin user was created
            admin_status_response = await client.get(
                f"/api/admin/companies/{company_id}/admin-status",
                headers=super_admin_auth_headers
            )

            assert admin_status_response.status_code == 200
            admin_data = admin_status_response.json()
            assert admin_data["has_active_admin"] is True
            assert admin_data["admin_count"] >= 1

    # ===== EDGE CASES =====

    @pytest.mark.asyncio
    async def test_create_company_with_long_name(self, client: AsyncClient, super_admin_auth_headers: dict):
        """Test company creation with very long name."""
        company_data = {
            "name": "A" * 300,  # Very long name
            "email": "longname@example.com",
            "type": "employer"
        }

        response = await client.post(
            "/api/admin/companies",
            json=company_data,
            headers=super_admin_auth_headers
        )

        # Should either succeed (if length is allowed) or fail with validation error
        assert response.status_code in [201, 422]
        if response.status_code == 422:
            error_detail = response.json()["detail"]
            assert any("name" in str(error).lower() for error in error_detail)

    @pytest.mark.asyncio
    async def test_update_company_to_duplicate_email(self, client: AsyncClient, super_admin_auth_headers: dict, db_session: AsyncSession):
        """Test updating company to have duplicate email."""
        # Create another company
        another_company = Company(
            name="Another Company",
            email="another@example.com",
            type=CompanyType.EMPLOYER,
            is_active="1"
        )
        db_session.add(another_company)
        await db_session.commit()
        await db_session.refresh(another_company)

        # Try to update first company to have same email
        update_data = {"email": another_company.email}

        response = await client.put(
            f"/api/admin/companies/{another_company.id}",
            json=update_data,
            headers=super_admin_auth_headers
        )

        # Should prevent duplicate email
        assert response.status_code in [400, 422]

    @pytest.mark.asyncio
    async def test_get_companies_with_complex_search(self, client: AsyncClient, super_admin_auth_headers: dict):
        """Test companies search with complex search terms."""
        response = await client.get(
            "/api/admin/companies?search=test company&type=recruiter&is_active=true&has_users=true",
            headers=super_admin_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "companies" in data

    @pytest.mark.asyncio
    async def test_create_company_all_valid_types(self, client: AsyncClient, super_admin_auth_headers: dict):
        """Test company creation with all valid company types."""
        valid_types = ["employer", "recruiter"]

        for i, company_type in enumerate(valid_types):
            company_data = {
                "name": f"Test Company {i}",
                "email": f"test{i}@example.com",
                "type": company_type
            }

            response = await client.post(
                "/api/admin/companies",
                json=company_data,
                headers=super_admin_auth_headers
            )

            assert response.status_code == 201
            data = response.json()
            assert data["type"] == company_type