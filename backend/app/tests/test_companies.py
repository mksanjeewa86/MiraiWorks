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
            "phone": "+1-555-123-4567",
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
            "type": "employer",
            "phone": "+1-555-123-4567"
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
            "type": "employer",
            "phone": "+1-555-123-4567"
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
            phone="555-123-4567",
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
    async def test_delete_company_with_users_forbidden(self, client: AsyncClient, super_admin_auth_headers: dict, test_company: Company, test_user: User):
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
            "phone": "+1-555-123-4567",
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
            "type": "employer",
            "phone": "+1-555-123-4567"
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
    async def test_update_company_to_duplicate_email(self, client: AsyncClient, super_admin_auth_headers: dict, test_company: Company, db_session: AsyncSession):
        """Test updating company to have duplicate email."""
        # Create another company
        another_company = Company(
            name="Another Company",
            email="another@example.com",
            phone="+1-555-987-6543",
            type=CompanyType.EMPLOYER,
            is_active="1"
        )
        db_session.add(another_company)
        await db_session.commit()
        await db_session.refresh(another_company)

        # Try to update test_company to have same email as another_company
        update_data = {"email": another_company.email}

        response = await client.put(
            f"/api/admin/companies/{test_company.id}",
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
                "type": company_type,
                "phone": f"+1-555-123-456{i}"
            }

            response = await client.post(
                "/api/admin/companies",
                json=company_data,
                headers=super_admin_auth_headers
            )

            assert response.status_code == 201
            data = response.json()
            assert data["type"] == company_type

    # ===== COMPREHENSIVE FILTER TESTS =====

    @pytest.mark.asyncio
    async def test_get_companies_filter_by_search_name(self, client: AsyncClient, super_admin_auth_headers: dict, test_company: Company):
        """Test filtering companies by search term matching name."""
        search_term = test_company.name[:3]  # Use first 3 characters for partial match
        response = await client.get(
            f"/api/admin/companies?search={search_term}",
            headers=super_admin_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "companies" in data
        # Should find companies with matching name
        found_company = any(company["id"] == test_company.id for company in data["companies"])
        assert found_company is True

    @pytest.mark.asyncio
    async def test_get_companies_filter_by_search_email(self, client: AsyncClient, super_admin_auth_headers: dict, test_company: Company):
        """Test filtering companies by search term matching email."""
        search_term = test_company.email.split('@')[0]  # Use part of email for partial match
        response = await client.get(
            f"/api/admin/companies?search={search_term}",
            headers=super_admin_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "companies" in data
        # Should find companies with matching email
        found_company = any(company["id"] == test_company.id for company in data["companies"])
        assert found_company is True

    @pytest.mark.asyncio
    async def test_get_companies_search_case_insensitive(self, client: AsyncClient, super_admin_auth_headers: dict, test_company: Company):
        """Test that company search is case insensitive."""
        search_term = test_company.name.upper()
        response = await client.get(
            f"/api/admin/companies?search={search_term}",
            headers=super_admin_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "companies" in data
        # Should find companies regardless of case
        found_company = any(company["id"] == test_company.id for company in data["companies"])
        assert found_company is True

    @pytest.mark.asyncio
    async def test_get_companies_filter_by_type_employer(self, client: AsyncClient, super_admin_auth_headers: dict):
        """Test filtering companies by type=employer."""
        response = await client.get(
            "/api/admin/companies?company_type=employer",
            headers=super_admin_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "companies" in data
        for company in data["companies"]:
            assert company["type"] == "employer"

    @pytest.mark.asyncio
    async def test_get_companies_filter_by_type_recruiter(self, client: AsyncClient, super_admin_auth_headers: dict):
        """Test filtering companies by type=recruiter."""
        response = await client.get(
            "/api/admin/companies?company_type=recruiter",
            headers=super_admin_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "companies" in data
        for company in data["companies"]:
            assert company["type"] == "recruiter"

    @pytest.mark.asyncio
    async def test_get_companies_filter_by_is_active_true(self, client: AsyncClient, super_admin_auth_headers: dict):
        """Test filtering companies by is_active=true."""
        response = await client.get(
            "/api/admin/companies?is_active=true",
            headers=super_admin_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "companies" in data
        for company in data["companies"]:
            assert company["is_active"] is True

    @pytest.mark.asyncio
    async def test_get_companies_filter_by_is_active_false(self, client: AsyncClient, super_admin_auth_headers: dict, db_session: AsyncSession):
        """Test filtering companies by is_active=false."""
        # Create an inactive company
        inactive_company = Company(
            name="Inactive Company",
            email="inactive@test.com",
            phone="555-123-4567",
            type=CompanyType.EMPLOYER,
            is_active="0"  # Inactive
        )
        db_session.add(inactive_company)
        await db_session.commit()
        await db_session.refresh(inactive_company)

        response = await client.get(
            "/api/admin/companies?is_active=false",
            headers=super_admin_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "companies" in data
        for company in data["companies"]:
            assert company["is_active"] is False
        # Should find at least our inactive company
        inactive_companies = [company for company in data["companies"] if company["is_active"] is False]
        assert len(inactive_companies) >= 1

    @pytest.mark.asyncio
    async def test_get_companies_filter_by_is_demo_true(self, client: AsyncClient, super_admin_auth_headers: dict, db_session: AsyncSession):
        """Test filtering companies by is_demo=true."""
        # Create a demo company
        demo_company = Company(
            name="Demo Company",
            email="demo@test.com",
            phone="555-123-4567",
            type=CompanyType.EMPLOYER,
            is_active="1",
            is_demo=True
        )
        db_session.add(demo_company)
        await db_session.commit()
        await db_session.refresh(demo_company)

        response = await client.get(
            "/api/admin/companies?is_demo=true",
            headers=super_admin_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "companies" in data
        for company in data["companies"]:
            assert company["is_demo"] is True
        # Should find at least our demo company
        demo_companies = [company for company in data["companies"] if company["is_demo"] is True]
        assert len(demo_companies) >= 1

    @pytest.mark.asyncio
    async def test_get_companies_filter_by_is_demo_false(self, client: AsyncClient, super_admin_auth_headers: dict):
        """Test filtering companies by is_demo=false."""
        response = await client.get(
            "/api/admin/companies?is_demo=false",
            headers=super_admin_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "companies" in data
        for company in data["companies"]:
            assert company["is_demo"] is False

    @pytest.mark.asyncio
    async def test_get_companies_include_deleted_false_default(self, client: AsyncClient, super_admin_auth_headers: dict):
        """Test that deleted companies are excluded by default."""
        response = await client.get(
            "/api/admin/companies",
            headers=super_admin_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "companies" in data
        # All returned companies should not be deleted
        for company in data["companies"]:
            assert company["is_deleted"] is False

    @pytest.mark.asyncio
    async def test_get_companies_include_deleted_false_explicit(self, client: AsyncClient, super_admin_auth_headers: dict):
        """Test explicitly excluding deleted companies."""
        response = await client.get(
            "/api/admin/companies?include_deleted=false",
            headers=super_admin_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "companies" in data
        # All returned companies should not be deleted
        for company in data["companies"]:
            assert company["is_deleted"] is False

    @pytest.mark.asyncio
    async def test_get_companies_include_deleted_true(self, client: AsyncClient, super_admin_auth_headers: dict, test_company: "Company", db_session: AsyncSession):
        """Test including deleted companies in results."""
        # Create and delete a company
        deleted_company = Company(
            name="Deleted Company",
            email="deleted@test.com",
            phone="555-123-4567",
            type=CompanyType.EMPLOYER,
            is_active="0",
            is_deleted=True
        )
        db_session.add(deleted_company)
        await db_session.commit()
        await db_session.refresh(deleted_company)

        response = await client.get(
            "/api/admin/companies?include_deleted=true",
            headers=super_admin_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "companies" in data
        # Should include both deleted and non-deleted companies
        deleted_companies = [company for company in data["companies"] if company["is_deleted"] is True]
        non_deleted_companies = [company for company in data["companies"] if company["is_deleted"] is False]
        assert len(deleted_companies) >= 1
        assert len(non_deleted_companies) >= 1

    @pytest.mark.asyncio
    async def test_get_companies_pagination_with_size(self, client: AsyncClient, super_admin_auth_headers: dict):
        """Test companies pagination with specific page size."""
        response = await client.get(
            "/api/admin/companies?page=1&size=5",
            headers=super_admin_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "companies" in data
        assert data["page"] == 1
        assert data["size"] == 5
        assert len(data["companies"]) <= 5

    @pytest.mark.asyncio
    async def test_get_companies_pagination_multiple_pages(self, client: AsyncClient, super_admin_auth_headers: dict):
        """Test companies pagination across multiple pages."""
        # Test first page
        response1 = await client.get(
            "/api/admin/companies?page=1&size=2",
            headers=super_admin_auth_headers
        )

        assert response1.status_code == 200
        data1 = response1.json()
        assert data1["page"] == 1
        assert data1["size"] == 2

        # Test second page if there are enough results
        if data1["total"] > 2:
            response2 = await client.get(
                "/api/admin/companies?page=2&size=2",
                headers=super_admin_auth_headers
            )

            assert response2.status_code == 200
            data2 = response2.json()
            assert data2["page"] == 2
            assert data2["size"] == 2

            # Ensure different results on different pages
            page1_ids = {company["id"] for company in data1["companies"]}
            page2_ids = {company["id"] for company in data2["companies"]}
            assert page1_ids.isdisjoint(page2_ids)  # No overlap between pages

    @pytest.mark.asyncio
    async def test_get_companies_combined_filters_type_and_active(self, client: AsyncClient, super_admin_auth_headers: dict):
        """Test combining type and active status filters."""
        response = await client.get(
            "/api/admin/companies?company_type=employer&is_active=true",
            headers=super_admin_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "companies" in data
        for company in data["companies"]:
            assert company["type"] == "employer"
            assert company["is_active"] is True

    @pytest.mark.asyncio
    async def test_get_companies_combined_filters_search_and_type(self, client: AsyncClient, super_admin_auth_headers: dict):
        """Test combining search and type filters."""
        response = await client.get(
            "/api/admin/companies?search=test&company_type=employer",
            headers=super_admin_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "companies" in data
        for company in data["companies"]:
            assert company["type"] == "employer"

    @pytest.mark.asyncio
    async def test_get_companies_combined_filters_all_parameters(self, client: AsyncClient, super_admin_auth_headers: dict):
        """Test combining all filter parameters."""
        response = await client.get(
            "/api/admin/companies?page=1&size=10&search=test&company_type=employer&is_active=true&is_demo=false&include_deleted=false",
            headers=super_admin_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "companies" in data
        assert data["page"] == 1
        assert data["size"] == 10
        for company in data["companies"]:
            assert company["type"] == "employer"
            assert company["is_active"] is True
            assert company["is_demo"] is False
            assert company["is_deleted"] is False

    @pytest.mark.asyncio
    async def test_get_companies_empty_search_returns_all(self, client: AsyncClient, super_admin_auth_headers: dict):
        """Test that empty search parameter returns all companies."""
        response = await client.get(
            "/api/admin/companies?search=",
            headers=super_admin_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "companies" in data
        # Should return companies (not filtered by search)

    @pytest.mark.asyncio
    async def test_get_companies_nonexistent_search_returns_empty(self, client: AsyncClient, super_admin_auth_headers: dict):
        """Test that search with non-existent term returns empty results."""
        response = await client.get(
            "/api/admin/companies?search=nonexistentcompanyname12345",
            headers=super_admin_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "companies" in data
        assert len(data["companies"]) == 0
        assert data["total"] == 0

    @pytest.mark.asyncio
    async def test_get_companies_filter_validation_invalid_type(self, client: AsyncClient, super_admin_auth_headers: dict):
        """Test filtering with invalid company type."""
        response = await client.get(
            "/api/admin/companies?company_type=invalid_type",
            headers=super_admin_auth_headers
        )

        # Should either return 422 for validation error or 200 with empty results
        assert response.status_code in [200, 422]
        if response.status_code == 200:
            data = response.json()
            assert len(data["companies"]) == 0

    @pytest.mark.asyncio
    async def test_get_companies_pagination_boundary_conditions(self, client: AsyncClient, super_admin_auth_headers: dict):
        """Test pagination boundary conditions."""
        # Test page beyond available results
        response = await client.get(
            "/api/admin/companies?page=1000&size=10",
            headers=super_admin_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "companies" in data
        assert data["page"] == 1000
        assert len(data["companies"]) == 0  # Should be empty for page beyond results

    @pytest.mark.asyncio
    async def test_get_companies_filter_by_multiple_types(self, client: AsyncClient, super_admin_auth_headers: dict, db_session: AsyncSession):
        """Test that filtering works correctly with different company types."""
        # Create companies of different types
        employer_company = Company(
            name="Employer Test",
            email="employer@test.com",
            phone="555-123-4567",
            type=CompanyType.EMPLOYER,
            is_active="1"
        )
        recruiter_company = Company(
            name="Recruiter Test",
            email="recruiter@test.com",
            phone="555-123-4568",
            type=CompanyType.RECRUITER,
            is_active="1"
        )
        db_session.add(employer_company)
        db_session.add(recruiter_company)
        await db_session.commit()

        # Test employer filter
        employer_response = await client.get(
            "/api/admin/companies?company_type=employer",
            headers=super_admin_auth_headers
        )

        assert employer_response.status_code == 200
        employer_data = employer_response.json()
        employer_companies = [c for c in employer_data["companies"] if c["type"] == "employer"]
        assert len(employer_companies) >= 1

        # Test recruiter filter
        recruiter_response = await client.get(
            "/api/admin/companies?company_type=recruiter",
            headers=super_admin_auth_headers
        )

        assert recruiter_response.status_code == 200
        recruiter_data = recruiter_response.json()
        recruiter_companies = [c for c in recruiter_data["companies"] if c["type"] == "recruiter"]
        assert len(recruiter_companies) >= 1

    @pytest.mark.asyncio
    async def test_get_companies_deleted_field_in_response(self, client: AsyncClient, super_admin_auth_headers: dict):
        """Test that deleted fields are included in company response."""
        response = await client.get(
            "/api/admin/companies?include_deleted=true",
            headers=super_admin_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "companies" in data
        for company in data["companies"]:
            # Verify deleted fields are present
            assert "is_deleted" in company
            assert "deleted_at" in company
            assert "deleted_by" in company
            assert isinstance(company["is_deleted"], bool)

    @pytest.mark.asyncio
    async def test_get_companies_filter_combination_with_pagination(self, client: AsyncClient, super_admin_auth_headers: dict):
        """Test that filters work correctly with pagination."""
        response = await client.get(
            "/api/admin/companies?page=1&size=5&company_type=employer&is_active=true",
            headers=super_admin_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "companies" in data
        assert data["page"] == 1
        assert data["size"] == 5
        assert len(data["companies"]) <= 5
        for company in data["companies"]:
            assert company["type"] == "employer"
            assert company["is_active"] is True