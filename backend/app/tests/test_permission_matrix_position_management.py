"""
Comprehensive permission matrix tests for position/job management.

Tests the permission boundaries:
- Super Admin: Can create/update/delete any jobs across all companies
- Company Admin: Can create/update/delete jobs within their company only
- Recruiter: Can create/update/delete jobs within their company only
- Employer: Can create/update/delete jobs within their company only
- Candidate: Cannot create/update/delete jobs, can only view public jobs
- Cross-company restrictions apply to all company-scoped roles
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import Company
from app.models.position import Position
from app.models.role import UserRole
from app.models.user import User
from app.services.auth_service import auth_service
from app.utils.constants import CompanyType
from app.utils.constants import UserRole as UserRoleEnum


class TestPositionManagementPermissionMatrix:
    """Comprehensive tests for position management permission boundaries."""

    # ===== SUPER ADMIN PERMISSIONS =====

    @pytest.mark.asyncio
    async def test_super_admin_can_create_jobs_any_company(
        self,
        client: AsyncClient,
        super_admin_auth_headers: dict,
        test_company: Company,
    ):
        """Test that Super Admin can create jobs for any company."""
        position_data = {
            "title": "Super Admin Created Job",
            "description": "Job created by super admin",
            "requirements": "Admin requirements",
            "location": "Global",
            "job_type": "full_time",
            "salary_min": 100000,
            "salary_max": 150000,
            "company_id": test_company.id,
        }

        response = await client.post(
            "/api/positions", json=position_data, headers=super_admin_auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == position_data["title"]
        assert data["company_id"] == test_company.id

    @pytest.mark.asyncio
    async def test_super_admin_can_view_all_jobs(
        self,
        client: AsyncClient,
        super_admin_auth_headers: dict,
        db_session: AsyncSession,
        test_company: Company,
    ):
        """Test that Super Admin can view all jobs across companies."""
        # Create job in test company
        job = await self._create_position_for_company(db_session, test_company)

        response = await client.get(
            f"/api/positions/{job.id}", headers=super_admin_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == job.id

    @pytest.mark.asyncio
    async def test_super_admin_can_update_any_job(
        self,
        client: AsyncClient,
        super_admin_auth_headers: dict,
        db_session: AsyncSession,
        test_company: Company,
    ):
        """Test that Super Admin can update jobs from any company."""
        job = await self._create_position_for_company(db_session, test_company)

        update_data = {
            "title": "Updated by Super Admin",
            "description": "Updated description",
        }

        response = await client.put(
            f"/api/positions/{job.id}", json=update_data, headers=super_admin_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == update_data["title"]

    @pytest.mark.asyncio
    async def test_super_admin_can_delete_any_job(
        self,
        client: AsyncClient,
        super_admin_auth_headers: dict,
        db_session: AsyncSession,
        test_company: Company,
    ):
        """Test that Super Admin can delete jobs from any company."""
        job = await self._create_position_for_company(db_session, test_company)

        response = await client.delete(
            f"/api/positions/{job.id}", headers=super_admin_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "deleted" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_super_admin_can_view_job_statistics(
        self, client: AsyncClient, super_admin_auth_headers: dict
    ):
        """Test that Super Admin can view job statistics."""
        response = await client.get(
            "/api/positions/statistics", headers=super_admin_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "total_positions" in data or "statistics" in data

    # ===== COMPANY ADMIN SCOPED PERMISSIONS =====

    @pytest.mark.asyncio
    async def test_company_admin_can_create_jobs_own_company(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Company Admin can create jobs for their own company."""
        company_admin = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.COMPANY_ADMIN, "companyadmin@test.com"
        )
        headers = await self._get_auth_headers(client, company_admin)

        position_data = {
            "title": "Company Admin Job",
            "description": "Job created by company admin",
            "requirements": "Company requirements",
            "location": "Company Location",
            "job_type": "full_time",
            "salary_min": 80000,
            "salary_max": 120000,
            "company_id": test_company.id,
        }

        response = await client.post(
            "/api/positions", json=position_data, headers=headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == position_data["title"]
        assert data["company_id"] == test_company.id

    @pytest.mark.asyncio
    async def test_company_admin_cannot_create_jobs_other_company(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Company Admin cannot create jobs for other companies."""
        company_admin = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.COMPANY_ADMIN, "companyadmin@test.com"
        )
        other_company = await self._create_other_company(db_session)
        headers = await self._get_auth_headers(client, company_admin)

        position_data = {
            "title": "Unauthorized Job",
            "description": "Job for other company",
            "company_id": other_company.id,
        }

        response = await client.post(
            "/api/positions", json=position_data, headers=headers
        )

        assert response.status_code == 403
        assert "other company" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_company_admin_can_update_own_company_jobs(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Company Admin can update jobs from their own company."""
        company_admin = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.COMPANY_ADMIN, "companyadmin@test.com"
        )
        job = await self._create_position_for_company(db_session, test_company)
        headers = await self._get_auth_headers(client, company_admin)

        update_data = {"title": "Updated by Company Admin"}

        response = await client.put(
            f"/api/positions/{job.id}", json=update_data, headers=headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == update_data["title"]

    @pytest.mark.asyncio
    async def test_company_admin_cannot_update_other_company_jobs(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Company Admin cannot update jobs from other companies."""
        company_admin = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.COMPANY_ADMIN, "companyadmin@test.com"
        )
        other_company = await self._create_other_company(db_session)
        other_job = await self._create_position_for_company(db_session, other_company)
        headers = await self._get_auth_headers(client, company_admin)

        update_data = {"title": "Unauthorized Update"}

        response = await client.put(
            f"/api/positions/{other_job.id}", json=update_data, headers=headers
        )

        assert response.status_code == 403
        assert "not authorized" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_company_admin_can_delete_own_company_jobs(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Company Admin can delete jobs from their own company."""
        company_admin = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.COMPANY_ADMIN, "companyadmin@test.com"
        )
        job = await self._create_position_for_company(db_session, test_company)
        headers = await self._get_auth_headers(client, company_admin)

        response = await client.delete(f"/api/positions/{job.id}", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert "deleted" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_company_admin_cannot_delete_other_company_jobs(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Company Admin cannot delete jobs from other companies."""
        company_admin = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.COMPANY_ADMIN, "companyadmin@test.com"
        )
        other_company = await self._create_other_company(db_session)
        other_job = await self._create_position_for_company(db_session, other_company)
        headers = await self._get_auth_headers(client, company_admin)

        response = await client.delete(f"/api/positions/{other_job.id}", headers=headers)

        assert response.status_code == 403
        assert "not authorized" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_company_admin_can_view_company_job_statistics(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Company Admin can view their company's job statistics."""
        company_admin = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.COMPANY_ADMIN, "companyadmin@test.com"
        )
        headers = await self._get_auth_headers(client, company_admin)

        response = await client.get(
            f"/api/positions/statistics?company_id={test_company.id}", headers=headers
        )

        assert response.status_code == 200
        # Should only show statistics for their company

    # ===== RECRUITER PERMISSIONS =====

    @pytest.mark.asyncio
    async def test_recruiter_can_create_jobs_own_company(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Recruiter can create jobs for their own company."""
        recruiter = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.RECRUITER, "recruiter@test.com"
        )
        headers = await self._get_auth_headers(client, recruiter)

        position_data = {
            "title": "Recruiter Job",
            "description": "Job created by recruiter",
            "company_id": test_company.id,
        }

        response = await client.post(
            "/api/positions", json=position_data, headers=headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == position_data["title"]

    @pytest.mark.asyncio
    async def test_recruiter_cannot_create_jobs_other_company(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Recruiter cannot create jobs for other companies."""
        recruiter = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.RECRUITER, "recruiter@test.com"
        )
        other_company = await self._create_other_company(db_session)
        headers = await self._get_auth_headers(client, recruiter)

        position_data = {
            "title": "Unauthorized Recruiter Job",
            "description": "Job for other company",
            "company_id": other_company.id,
        }

        response = await client.post(
            "/api/positions", json=position_data, headers=headers
        )

        assert response.status_code == 403
        assert "other company" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_recruiter_can_update_own_company_jobs(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Recruiter can update jobs from their own company."""
        recruiter = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.RECRUITER, "recruiter@test.com"
        )
        job = await self._create_position_for_company(db_session, test_company)
        headers = await self._get_auth_headers(client, recruiter)

        update_data = {"title": "Updated by Recruiter"}

        response = await client.put(
            f"/api/positions/{job.id}", json=update_data, headers=headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == update_data["title"]

    @pytest.mark.asyncio
    async def test_recruiter_cannot_update_other_company_jobs(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Recruiter cannot update jobs from other companies."""
        recruiter = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.RECRUITER, "recruiter@test.com"
        )
        other_company = await self._create_other_company(db_session)
        other_job = await self._create_position_for_company(db_session, other_company)
        headers = await self._get_auth_headers(client, recruiter)

        update_data = {"title": "Unauthorized Update"}

        response = await client.put(
            f"/api/positions/{other_job.id}", json=update_data, headers=headers
        )

        assert response.status_code == 403
        assert "not authorized" in response.json()["detail"].lower()

    # ===== EMPLOYER PERMISSIONS =====

    @pytest.mark.asyncio
    async def test_employer_can_create_jobs_own_company(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Employer can create jobs for their own company."""
        employer = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.EMPLOYER, "employer@test.com"
        )
        headers = await self._get_auth_headers(client, employer)

        position_data = {
            "title": "Employer Job",
            "description": "Job created by employer",
            "company_id": test_company.id,
        }

        response = await client.post(
            "/api/positions", json=position_data, headers=headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == position_data["title"]

    @pytest.mark.asyncio
    async def test_employer_cannot_create_jobs_other_company(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Employer cannot create jobs for other companies."""
        employer = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.EMPLOYER, "employer@test.com"
        )
        other_company = await self._create_other_company(db_session)
        headers = await self._get_auth_headers(client, employer)

        position_data = {
            "title": "Unauthorized Employer Job",
            "description": "Job for other company",
            "company_id": other_company.id,
        }

        response = await client.post(
            "/api/positions", json=position_data, headers=headers
        )

        assert response.status_code == 403
        assert "other company" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_employer_can_update_own_company_jobs(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Employer can update jobs from their own company."""
        employer = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.EMPLOYER, "employer@test.com"
        )
        job = await self._create_position_for_company(db_session, test_company)
        headers = await self._get_auth_headers(client, employer)

        update_data = {"title": "Updated by Employer"}

        response = await client.put(
            f"/api/positions/{job.id}", json=update_data, headers=headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == update_data["title"]

    # ===== CANDIDATE RESTRICTIONS =====

    @pytest.mark.asyncio
    async def test_candidate_cannot_create_jobs(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Candidate cannot create jobs."""
        candidate = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.CANDIDATE, "candidate@test.com"
        )
        headers = await self._get_auth_headers(client, candidate)

        position_data = {
            "title": "Candidate Job",
            "description": "Job by candidate (should fail)",
            "company_id": test_company.id,
        }

        response = await client.post(
            "/api/positions", json=position_data, headers=headers
        )

        assert response.status_code == 403
        assert "not enough permissions" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_candidate_cannot_update_jobs(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Candidate cannot update jobs."""
        candidate = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.CANDIDATE, "candidate@test.com"
        )
        job = await self._create_position_for_company(db_session, test_company)
        headers = await self._get_auth_headers(client, candidate)

        update_data = {"title": "Unauthorized Update"}

        response = await client.put(
            f"/api/positions/{job.id}", json=update_data, headers=headers
        )

        assert response.status_code == 403
        assert "not enough permissions" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_candidate_cannot_delete_jobs(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Candidate cannot delete jobs."""
        candidate = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.CANDIDATE, "candidate@test.com"
        )
        job = await self._create_position_for_company(db_session, test_company)
        headers = await self._get_auth_headers(client, candidate)

        response = await client.delete(f"/api/positions/{job.id}", headers=headers)

        assert response.status_code == 403
        assert "not enough permissions" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_candidate_can_view_public_jobs(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Candidate can view public jobs."""
        candidate = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.CANDIDATE, "candidate@test.com"
        )
        job = await self._create_position_for_company(db_session, test_company, status="published")
        headers = await self._get_auth_headers(client, candidate)

        # Can view public job list
        response = await client.get("/api/positions", headers=headers)
        assert response.status_code == 200

        # Can view specific public job
        response = await client.get(f"/api/positions/{job.id}", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == job.id

    @pytest.mark.asyncio
    async def test_candidate_cannot_view_draft_jobs(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Candidate cannot view draft jobs."""
        candidate = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.CANDIDATE, "candidate@test.com"
        )
        draft_job = await self._create_position_for_company(db_session, test_company, status="draft")
        headers = await self._get_auth_headers(client, candidate)

        response = await client.get(f"/api/positions/{draft_job.id}", headers=headers)
        assert response.status_code == 403
        assert "not published" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_candidate_cannot_view_job_statistics(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Candidate cannot view job statistics."""
        candidate = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.CANDIDATE, "candidate@test.com"
        )
        headers = await self._get_auth_headers(client, candidate)

        response = await client.get("/api/positions/statistics", headers=headers)
        assert response.status_code == 403
        assert "admin access required" in response.json()["detail"].lower()

    # ===== COMPANY POSITIONS ACCESS =====

    @pytest.mark.asyncio
    async def test_company_positions_access_restrictions(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that company positions endpoint respects company scoping."""
        recruiter = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.RECRUITER, "recruiter@test.com"
        )
        other_company = await self._create_other_company(db_session)
        headers = await self._get_auth_headers(client, recruiter)

        # Can access own company positions
        response = await client.get(
            f"/api/positions/company/{test_company.id}", headers=headers
        )
        assert response.status_code == 200

        # Cannot access other company positions
        response = await client.get(
            f"/api/positions/company/{other_company.id}", headers=headers
        )
        assert response.status_code == 403
        assert "other company" in response.json()["detail"].lower()

    # ===== BULK OPERATIONS PERMISSIONS =====

    @pytest.mark.asyncio
    async def test_bulk_operations_company_scoping(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that bulk operations respect company scoping."""
        recruiter = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.RECRUITER, "recruiter@test.com"
        )
        other_company = await self._create_other_company(db_session)

        # Create jobs in both companies
        own_job = await self._create_position_for_company(db_session, test_company)
        other_job = await self._create_position_for_company(db_session, other_company)

        headers = await self._get_auth_headers(client, recruiter)

        # Try to bulk update jobs including other company job
        bulk_data = {
            "position_ids": [own_job.id, other_job.id],
            "status": "published"
        }

        response = await client.patch(
            "/api/positions/bulk/status", json=bulk_data, headers=headers
        )

        # Should either fail completely or only update own company jobs
        assert response.status_code in [403, 200]
        if response.status_code == 200:
            # If partial success, verify only own company jobs were updated
            data = response.json()
            updated_ids = [pos["id"] for pos in data]
            assert own_job.id in updated_ids
            assert other_job.id not in updated_ids

    # ===== AUTHENTICATION BOUNDARY TESTS =====

    @pytest.mark.asyncio
    async def test_unauthenticated_position_access(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
    ):
        """Test unauthenticated access to position endpoints."""
        job = await self._create_position_for_company(db_session, test_company)

        # Can view public positions list (no auth required)
        response = await client.get("/api/positions")
        assert response.status_code == 200

        # Can view specific public position (no auth required)
        response = await client.get(f"/api/positions/{job.id}")
        assert response.status_code == 200

        # Cannot create positions without auth
        position_data = {"title": "Unauthorized Job"}
        response = await client.post("/api/positions", json=position_data)
        assert response.status_code == 401

        # Cannot update positions without auth
        response = await client.put(f"/api/positions/{job.id}", json={"title": "Updated"})
        assert response.status_code == 401

        # Cannot delete positions without auth
        response = await client.delete(f"/api/positions/{job.id}")
        assert response.status_code == 401

        # Cannot view statistics without auth
        response = await client.get("/api/positions/statistics")
        assert response.status_code == 401

    # ===== HELPER METHODS =====

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
            company_id=company.id if company else None,
            hashed_password=auth_service.get_password_hash("testpass123"),
            is_active=True,
            is_admin=(role in [UserRoleEnum.SUPER_ADMIN, UserRoleEnum.COMPANY_ADMIN]),
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

    async def _create_position_for_company(
        self, db_session: AsyncSession, company: Company, status: str = "published", posted_by_user: User | None = None
    ) -> Position:
        """Create a position for a company."""
        # Create a default user if none provided
        if posted_by_user is None:
            posted_by_user = User(
                email=f"position_poster_{company.id}@test.com",
                first_name="Poster",
                last_name="User",
                password_hash=auth_service.get_password_hash("testpass123"),
                is_active=True,
                company_id=company.id,
            )
            db_session.add(posted_by_user)
            await db_session.flush()

        position = Position(
            title="Test Position",
            description="Test job description",
            requirements="Test requirements",
            location="Test Location",
            job_type="full_time",
            salary_min=80000,
            salary_max=120000,
            company_id=company.id,
            status=status,
            slug=f"test-position-{company.id}",
            posted_by=posted_by_user.id,
        )
        db_session.add(position)
        await db_session.commit()
        await db_session.refresh(position)
        return position

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
