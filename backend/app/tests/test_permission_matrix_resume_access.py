"""
Comprehensive permission matrix tests for resume access control.

Tests the permission boundaries:
- Candidate: Can create, update, delete own resumes only
- Super Admin: Can view any resume
- Company Admin: Can view applied candidate resumes from their company only
- Recruiter: Can view applied candidate resumes from their company only
- Employer: Can view applied candidate resumes from their company only
- Cross-company access restrictions apply
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import Company
from app.models.resume import Resume
from app.models.role import UserRole
from app.models.user import User
from app.services.auth_service import auth_service
from app.utils.constants import CompanyType
from app.utils.constants import UserRole as UserRoleEnum


class TestResumeAccessControl:
    """Comprehensive tests for resume access permission boundaries."""

    # ===== CANDIDATE EXCLUSIVE CREATION RIGHTS =====

    @pytest.mark.asyncio
    async def test_candidate_can_create_resume(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that only Candidates can create resumes."""
        candidate = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.CANDIDATE, "candidate@test.com"
        )
        headers = await self._get_auth_headers(client, candidate)

        resume_data = {
            "title": "Software Engineer Resume",
            "professional_summary": "Experienced software engineer",
            "skills": ["Python", "JavaScript", "React"],
            "experience": [
                {
                    "company": "Tech Corp",
                    "position": "Developer",
                    "start_date": "2020-01-01",
                    "end_date": "2023-01-01",
                    "description": "Developed web applications"
                }
            ]
        }

        response = await client.post(
            "/api/resumes/", json=resume_data, headers=headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == resume_data["title"]
        assert data["user_id"] == candidate.id

    @pytest.mark.asyncio
    async def test_candidate_can_update_own_resume(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Candidate can update their own resume."""
        candidate = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.CANDIDATE, "candidate@test.com"
        )
        resume = await self._create_resume_for_candidate(db_session, candidate)
        headers = await self._get_auth_headers(client, candidate)

        update_data = {
            "title": "Updated Resume Title",
            "professional_summary": "Updated summary",
        }

        response = await client.put(
            f"/api/resumes/{resume.id}", json=update_data, headers=headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == update_data["title"]
        assert data["professional_summary"] == update_data["professional_summary"]

    @pytest.mark.asyncio
    async def test_candidate_can_delete_own_resume(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Candidate can delete their own resume."""
        candidate = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.CANDIDATE, "candidate@test.com"
        )
        resume = await self._create_resume_for_candidate(db_session, candidate)
        headers = await self._get_auth_headers(client, candidate)

        response = await client.delete(
            f"/api/resumes/{resume.id}", headers=headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "deleted" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_candidate_can_view_own_resumes(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Candidate can view their own resumes."""
        candidate = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.CANDIDATE, "candidate@test.com"
        )
        resume = await self._create_resume_for_candidate(db_session, candidate)
        headers = await self._get_auth_headers(client, candidate)

        # View resume list
        response = await client.get("/api/resumes/", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["resumes"]) >= 1

        # View specific resume
        response = await client.get(f"/api/resumes/{resume.id}", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == resume.id

    @pytest.mark.asyncio
    async def test_candidate_cannot_view_other_candidate_resumes(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Candidate cannot view other candidates' resumes."""
        candidate1 = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.CANDIDATE, "candidate1@test.com"
        )
        candidate2 = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.CANDIDATE, "candidate2@test.com"
        )
        other_resume = await self._create_resume_for_candidate(db_session, candidate2)
        headers = await self._get_auth_headers(client, candidate1)

        response = await client.get(f"/api/resumes/{other_resume.id}", headers=headers)
        assert response.status_code == 403
        assert "not authorized" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_candidate_cannot_update_other_candidate_resumes(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Candidate cannot update other candidates' resumes."""
        candidate1 = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.CANDIDATE, "candidate1@test.com"
        )
        candidate2 = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.CANDIDATE, "candidate2@test.com"
        )
        other_resume = await self._create_resume_for_candidate(db_session, candidate2)
        headers = await self._get_auth_headers(client, candidate1)

        update_data = {"title": "Unauthorized Update"}

        response = await client.put(
            f"/api/resumes/{other_resume.id}", json=update_data, headers=headers
        )
        assert response.status_code == 403
        assert "not authorized" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_candidate_cannot_delete_other_candidate_resumes(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Candidate cannot delete other candidates' resumes."""
        candidate1 = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.CANDIDATE, "candidate1@test.com"
        )
        candidate2 = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.CANDIDATE, "candidate2@test.com"
        )
        other_resume = await self._create_resume_for_candidate(db_session, candidate2)
        headers = await self._get_auth_headers(client, candidate1)

        response = await client.delete(f"/api/resumes/{other_resume.id}", headers=headers)
        assert response.status_code == 403
        assert "not authorized" in response.json()["detail"].lower()

    # ===== NON-CANDIDATE CREATION RESTRICTIONS =====

    @pytest.mark.asyncio
    async def test_super_admin_cannot_create_resumes(
        self,
        client: AsyncClient,
        super_admin_auth_headers: dict,
    ):
        """Test that Super Admin cannot create resumes."""
        resume_data = {
            "title": "Super Admin Resume",
            "professional_summary": "This should not be allowed",
        }

        response = await client.post(
            "/api/resumes/", json=resume_data, headers=super_admin_auth_headers
        )
        assert response.status_code == 403
        assert "candidates only" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_company_admin_cannot_create_resumes(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Company Admin cannot create resumes."""
        company_admin = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.ADMIN, "companyadmin@test.com"
        )
        headers = await self._get_auth_headers(client, company_admin)

        resume_data = {
            "title": "Company Admin Resume",
            "professional_summary": "This should not be allowed",
        }

        response = await client.post(
            "/api/resumes/", json=resume_data, headers=headers
        )
        assert response.status_code == 403
        assert "candidates only" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_recruiter_cannot_create_resumes(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Recruiter cannot create resumes."""
        recruiter = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.MEMBER, "recruiter@test.com"
        )
        headers = await self._get_auth_headers(client, recruiter)

        resume_data = {
            "title": "Recruiter Resume",
            "professional_summary": "This should not be allowed",
        }

        response = await client.post(
            "/api/resumes/", json=resume_data, headers=headers
        )
        assert response.status_code == 403
        assert "candidates only" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_employer_cannot_create_resumes(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Employer cannot create resumes."""
        employer = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.MEMBER, "employer@test.com"
        )
        headers = await self._get_auth_headers(client, employer)

        resume_data = {
            "title": "Employer Resume",
            "professional_summary": "This should not be allowed",
        }

        response = await client.post(
            "/api/resumes/", json=resume_data, headers=headers
        )
        assert response.status_code == 403
        assert "candidates only" in response.json()["detail"].lower()

    # ===== SUPER ADMIN VIEWING PERMISSIONS =====

    @pytest.mark.asyncio
    async def test_super_admin_can_view_any_resume(
        self,
        client: AsyncClient,
        super_admin_auth_headers: dict,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Super Admin can view any resume."""
        candidate = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.CANDIDATE, "candidate@test.com"
        )
        resume = await self._create_resume_for_candidate(db_session, candidate)

        response = await client.get(
            f"/api/resumes/{resume.id}", headers=super_admin_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == resume.id

    @pytest.mark.asyncio
    async def test_super_admin_cannot_update_candidate_resumes(
        self,
        client: AsyncClient,
        super_admin_auth_headers: dict,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Super Admin cannot update candidate resumes."""
        candidate = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.CANDIDATE, "candidate@test.com"
        )
        resume = await self._create_resume_for_candidate(db_session, candidate)

        update_data = {"title": "Updated by Super Admin"}

        response = await client.put(
            f"/api/resumes/{resume.id}", json=update_data, headers=super_admin_auth_headers
        )
        assert response.status_code == 403
        assert "owner only" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_super_admin_cannot_delete_candidate_resumes(
        self,
        client: AsyncClient,
        super_admin_auth_headers: dict,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Super Admin cannot delete candidate resumes."""
        candidate = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.CANDIDATE, "candidate@test.com"
        )
        resume = await self._create_resume_for_candidate(db_session, candidate)

        response = await client.delete(
            f"/api/resumes/{resume.id}", headers=super_admin_auth_headers
        )
        assert response.status_code == 403
        assert "owner only" in response.json()["detail"].lower()

    # ===== COMPANY SCOPED VIEWING PERMISSIONS =====

    @pytest.mark.asyncio
    async def test_company_admin_can_view_applied_candidate_resumes_own_company(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Company Admin can view applied candidate resumes from their company."""
        company_admin = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.ADMIN, "companyadmin@test.com"
        )
        candidate = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.CANDIDATE, "candidate@test.com"
        )
        resume = await self._create_resume_for_candidate(db_session, candidate)

        # Simulate application to company job (this would be done through job application system)
        await self._simulate_job_application(db_session, candidate, test_company, resume)

        headers = await self._get_auth_headers(client, company_admin)

        response = await client.get(f"/api/resumes/{resume.id}", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == resume.id

    @pytest.mark.asyncio
    async def test_company_admin_cannot_view_non_applied_candidate_resumes(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Company Admin cannot view resumes of candidates who haven't applied."""
        company_admin = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.ADMIN, "companyadmin@test.com"
        )
        candidate = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.CANDIDATE, "candidate@test.com"
        )
        resume = await self._create_resume_for_candidate(db_session, candidate)

        # No job application - should not be able to view
        headers = await self._get_auth_headers(client, company_admin)

        response = await client.get(f"/api/resumes/{resume.id}", headers=headers)
        assert response.status_code == 403
        assert "not applied" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_company_admin_cannot_view_other_company_candidate_resumes(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Company Admin cannot view resumes from other company candidates."""
        company_admin = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.ADMIN, "companyadmin@test.com"
        )

        other_company = await self._create_other_company(db_session)
        other_candidate = await self._create_user_with_role(
            db_session, other_company, test_roles, UserRoleEnum.CANDIDATE, "othercandidate@test.com"
        )
        other_resume = await self._create_resume_for_candidate(db_session, other_candidate)

        headers = await self._get_auth_headers(client, company_admin)

        response = await client.get(f"/api/resumes/{other_resume.id}", headers=headers)
        assert response.status_code == 403
        assert "different company" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_recruiter_can_view_applied_candidate_resumes_own_company(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Recruiter can view applied candidate resumes from their company."""
        recruiter = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.MEMBER, "recruiter@test.com"
        )
        candidate = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.CANDIDATE, "candidate@test.com"
        )
        resume = await self._create_resume_for_candidate(db_session, candidate)

        # Simulate application to company job
        await self._simulate_job_application(db_session, candidate, test_company, resume)

        headers = await self._get_auth_headers(client, recruiter)

        response = await client.get(f"/api/resumes/{resume.id}", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == resume.id

    @pytest.mark.asyncio
    async def test_recruiter_cannot_view_non_applied_candidate_resumes(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Recruiter cannot view resumes of candidates who haven't applied."""
        recruiter = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.MEMBER, "recruiter@test.com"
        )
        candidate = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.CANDIDATE, "candidate@test.com"
        )
        resume = await self._create_resume_for_candidate(db_session, candidate)

        headers = await self._get_auth_headers(client, recruiter)

        response = await client.get(f"/api/resumes/{resume.id}", headers=headers)
        assert response.status_code == 403
        assert "not applied" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_employer_can_view_applied_candidate_resumes_own_company(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Employer can view applied candidate resumes from their company."""
        employer = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.MEMBER, "employer@test.com"
        )
        candidate = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.CANDIDATE, "candidate@test.com"
        )
        resume = await self._create_resume_for_candidate(db_session, candidate)

        # Simulate application to company job
        await self._simulate_job_application(db_session, candidate, test_company, resume)

        headers = await self._get_auth_headers(client, employer)

        response = await client.get(f"/api/resumes/{resume.id}", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == resume.id

    # ===== CROSS-COMPANY ACCESS RESTRICTIONS =====

    @pytest.mark.asyncio
    async def test_cross_company_resume_access_restrictions(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that users cannot access resumes from other companies."""
        other_company = await self._create_other_company(db_session)

        recruiter = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.MEMBER, "recruiter@test.com"
        )
        other_candidate = await self._create_user_with_role(
            db_session, other_company, test_roles, UserRoleEnum.CANDIDATE, "othercandidate@test.com"
        )
        other_resume = await self._create_resume_for_candidate(db_session, other_candidate)

        headers = await self._get_auth_headers(client, recruiter)

        response = await client.get(f"/api/resumes/{other_resume.id}", headers=headers)
        assert response.status_code == 403
        assert "different company" in response.json()["detail"].lower()

    # ===== RESUME SHARING AND PUBLIC ACCESS =====

    @pytest.mark.asyncio
    async def test_candidate_can_create_share_link(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Candidate can create share links for their resumes."""
        candidate = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.CANDIDATE, "candidate@test.com"
        )
        resume = await self._create_resume_for_candidate(db_session, candidate)
        headers = await self._get_auth_headers(client, candidate)

        share_data = {"expiry": "2024-12-31"}

        response = await client.post(
            f"/api/resumes/{resume.id}/share", json=share_data, headers=headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "share_token" in data
        assert "share_url" in data

    @pytest.mark.asyncio
    async def test_non_owner_cannot_create_share_link(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that non-owners cannot create share links for resumes."""
        candidate1 = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.CANDIDATE, "candidate1@test.com"
        )
        candidate2 = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.CANDIDATE, "candidate2@test.com"
        )
        resume = await self._create_resume_for_candidate(db_session, candidate2)

        headers = await self._get_auth_headers(client, candidate1)
        share_data = {"expiry": "2024-12-31"}

        response = await client.post(
            f"/api/resumes/{resume.id}/share", json=share_data, headers=headers
        )
        assert response.status_code == 403
        assert "owner only" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_candidate_can_generate_pdf(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Candidate can generate PDF of their resume."""
        candidate = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.CANDIDATE, "candidate@test.com"
        )
        resume = await self._create_resume_for_candidate(db_session, candidate)
        headers = await self._get_auth_headers(client, candidate)

        response = await client.get(f"/api/resumes/{resume.id}/pdf", headers=headers)

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"

    # ===== AUTHENTICATION BOUNDARY TESTS =====

    @pytest.mark.asyncio
    async def test_unauthenticated_cannot_access_resumes(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that unauthenticated users cannot access resumes."""
        candidate = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.CANDIDATE, "candidate@test.com"
        )
        resume = await self._create_resume_for_candidate(db_session, candidate)

        endpoints = [
            ("GET", "/api/resumes/"),
            ("POST", "/api/resumes/"),
            ("GET", f"/api/resumes/{resume.id}"),
            ("PUT", f"/api/resumes/{resume.id}"),
            ("DELETE", f"/api/resumes/{resume.id}"),
            ("POST", f"/api/resumes/{resume.id}/share"),
            ("GET", f"/api/resumes/{resume.id}/pdf"),
        ]

        for method, endpoint in endpoints:
            if method == "GET":
                response = await client.get(endpoint)
            elif method == "POST":
                response = await client.post(endpoint, json={"title": "Test"})
            elif method == "PUT":
                response = await client.put(endpoint, json={"title": "Updated"})
            elif method == "DELETE":
                response = await client.delete(endpoint)

            assert response.status_code == 401, f"Failed for {method} {endpoint}"

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

    async def _create_resume_for_candidate(
        self, db_session: AsyncSession, candidate: User
    ) -> Resume:
        """Create a resume for a candidate."""
        resume = Resume(
            user_id=candidate.id,
            title="Test Resume",
            professional_summary="Test summary",
            is_public=False,
        )
        db_session.add(resume)
        await db_session.commit()
        await db_session.refresh(resume)
        return resume

    async def _simulate_job_application(
        self,
        db_session: AsyncSession,
        candidate: User,
        company: Company,
        resume: Resume,
    ):
        """Simulate a job application to enable resume viewing permissions."""
        # This would typically create a job application record
        # For testing purposes, we'll set a flag or create a mock application
        # Implementation depends on the actual job application model
        pass

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
