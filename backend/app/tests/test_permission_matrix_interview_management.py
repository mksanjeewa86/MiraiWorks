"""
Comprehensive permission matrix tests for interview management.

Tests the permission boundaries:
- Super Admin: Can manage any interviews across all companies
- Company Admin: Can manage company-related interviews only
- Recruiter: Can manage company-related interviews only
- Employer: Can manage company-related interviews only
- Candidate: Can only update/cancel own interviews, cannot create interviews
- Cross-company restrictions apply to all company-scoped roles
"""

from datetime import timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import Company
from app.models.interview import Interview
from app.models.position import Position
from app.models.role import UserRole
from app.models.user import User
from app.services.auth_service import auth_service
from app.utils.constants import CompanyType
from app.utils.constants import UserRole as UserRoleEnum
from app.utils.datetime_utils import get_utc_now


class TestInterviewManagementPermissionMatrix:
    """Comprehensive tests for interview management permission boundaries."""

    # ===== SUPER ADMIN PERMISSIONS =====

    @pytest.mark.asyncio
    async def test_super_admin_can_create_interviews_any_company(
        self,
        client: AsyncClient,
        super_admin_auth_headers: dict,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Super Admin can create interviews for any company."""
        # Create participants
        recruiter = await self._create_user_with_role(
            db_session,
            test_company,
            test_roles,
            UserRoleEnum.MEMBER,
            "recruiter@test.com",
        )
        candidate = await self._create_user_with_role(
            db_session,
            test_company,
            test_roles,
            UserRoleEnum.CANDIDATE,
            "candidate@test.com",
        )
        position = await self._create_position_for_company(db_session, test_company)

        interview_data = {
            "position_id": position.id,
            "candidate_id": candidate.id,
            "interviewer_id": recruiter.id,
            "scheduled_at": (get_utc_now() + timedelta(days=1)).isoformat(),
            "duration_minutes": 60,
            "interview_type": "technical",
            "location": "Conference Room A",
        }

        response = await client.post(
            "/api/interviews", json=interview_data, headers=super_admin_auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["position_id"] == position.id
        assert data["candidate_id"] == candidate.id

    @pytest.mark.asyncio
    async def test_super_admin_can_view_any_interview(
        self,
        client: AsyncClient,
        super_admin_auth_headers: dict,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Super Admin can view any interview."""
        interview = await self._create_interview_for_company(
            db_session, test_company, test_roles
        )

        response = await client.get(
            f"/api/interviews/{interview.id}", headers=super_admin_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == interview.id

    @pytest.mark.asyncio
    async def test_super_admin_can_update_any_interview(
        self,
        client: AsyncClient,
        super_admin_auth_headers: dict,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Super Admin can update any interview."""
        interview = await self._create_interview_for_company(
            db_session, test_company, test_roles
        )

        update_data = {
            "location": "Updated by Super Admin",
            "duration_minutes": 90,
        }

        response = await client.put(
            f"/api/interviews/{interview.id}",
            json=update_data,
            headers=super_admin_auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["location"] == update_data["location"]
        assert data["duration_minutes"] == update_data["duration_minutes"]

    @pytest.mark.asyncio
    async def test_super_admin_can_cancel_any_interview(
        self,
        client: AsyncClient,
        super_admin_auth_headers: dict,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Super Admin can cancel any interview."""
        interview = await self._create_interview_for_company(
            db_session, test_company, test_roles
        )

        cancel_data = {"reason": "Cancelled by Super Admin"}

        response = await client.post(
            f"/api/interviews/{interview.id}/cancel",
            json=cancel_data,
            headers=super_admin_auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "cancelled" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_super_admin_can_delete_any_interview(
        self,
        client: AsyncClient,
        super_admin_auth_headers: dict,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Super Admin can delete any interview."""
        interview = await self._create_interview_for_company(
            db_session, test_company, test_roles
        )

        response = await client.delete(
            f"/api/interviews/{interview.id}", headers=super_admin_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "deleted" in data["message"].lower()

    # ===== COMPANY ADMIN SCOPED PERMISSIONS =====

    @pytest.mark.asyncio
    async def test_company_admin_can_create_interviews_own_company(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Company Admin can create interviews for their company."""
        company_admin = await self._create_user_with_role(
            db_session,
            test_company,
            test_roles,
            UserRoleEnum.ADMIN,
            "companyadmin@test.com",
        )
        recruiter = await self._create_user_with_role(
            db_session,
            test_company,
            test_roles,
            UserRoleEnum.MEMBER,
            "recruiter@test.com",
        )
        candidate = await self._create_user_with_role(
            db_session,
            test_company,
            test_roles,
            UserRoleEnum.CANDIDATE,
            "candidate@test.com",
        )
        position = await self._create_position_for_company(db_session, test_company)

        headers = await self._get_auth_headers(client, company_admin)

        interview_data = {
            "position_id": position.id,
            "candidate_id": candidate.id,
            "interviewer_id": recruiter.id,
            "scheduled_at": (get_utc_now() + timedelta(days=1)).isoformat(),
            "duration_minutes": 60,
            "interview_type": "behavioral",
        }

        response = await client.post(
            "/api/interviews", json=interview_data, headers=headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["position_id"] == position.id

    @pytest.mark.asyncio
    async def test_company_admin_cannot_create_interviews_other_company(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Company Admin cannot create interviews for other companies."""
        company_admin = await self._create_user_with_role(
            db_session,
            test_company,
            test_roles,
            UserRoleEnum.ADMIN,
            "companyadmin@test.com",
        )
        other_company = await self._create_other_company(db_session)
        other_position = await self._create_position_for_company(
            db_session, other_company
        )
        other_candidate = await self._create_user_with_role(
            db_session,
            other_company,
            test_roles,
            UserRoleEnum.CANDIDATE,
            "othercandidate@test.com",
        )

        headers = await self._get_auth_headers(client, company_admin)

        interview_data = {
            "position_id": other_position.id,
            "candidate_id": other_candidate.id,
            "interviewer_id": company_admin.id,
            "scheduled_at": (get_utc_now() + timedelta(days=1)).isoformat(),
        }

        response = await client.post(
            "/api/interviews", json=interview_data, headers=headers
        )

        assert response.status_code == 403
        assert "other company" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_company_admin_can_view_company_interviews_only(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Company Admin can only view company-related interviews."""
        company_admin = await self._create_user_with_role(
            db_session,
            test_company,
            test_roles,
            UserRoleEnum.ADMIN,
            "companyadmin@test.com",
        )

        # Create interview in own company
        own_interview = await self._create_interview_for_company(
            db_session, test_company, test_roles
        )

        # Create interview in other company
        other_company = await self._create_other_company(db_session)
        other_interview = await self._create_interview_for_company(
            db_session, other_company, test_roles
        )

        headers = await self._get_auth_headers(client, company_admin)

        # Should be able to view own company interview
        response = await client.get(
            f"/api/interviews/{own_interview.id}", headers=headers
        )
        assert response.status_code == 200

        # Should NOT be able to view other company interview
        response = await client.get(
            f"/api/interviews/{other_interview.id}", headers=headers
        )
        assert response.status_code == 403
        assert "not related" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_company_admin_can_update_company_interviews_only(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Company Admin can only update company-related interviews."""
        company_admin = await self._create_user_with_role(
            db_session,
            test_company,
            test_roles,
            UserRoleEnum.ADMIN,
            "companyadmin@test.com",
        )

        own_interview = await self._create_interview_for_company(
            db_session, test_company, test_roles
        )
        other_company = await self._create_other_company(db_session)
        other_interview = await self._create_interview_for_company(
            db_session, other_company, test_roles
        )

        headers = await self._get_auth_headers(client, company_admin)
        update_data = {"location": "Updated by Company Admin"}

        # Should be able to update own company interview
        response = await client.put(
            f"/api/interviews/{own_interview.id}", json=update_data, headers=headers
        )
        assert response.status_code == 200

        # Should NOT be able to update other company interview
        response = await client.put(
            f"/api/interviews/{other_interview.id}", json=update_data, headers=headers
        )
        assert response.status_code == 403
        assert "not related" in response.json()["detail"].lower()

    # ===== RECRUITER PERMISSIONS =====

    @pytest.mark.asyncio
    async def test_recruiter_can_create_interviews_own_company(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Recruiter can create interviews for their company."""
        recruiter = await self._create_user_with_role(
            db_session,
            test_company,
            test_roles,
            UserRoleEnum.MEMBER,
            "recruiter@test.com",
        )
        candidate = await self._create_user_with_role(
            db_session,
            test_company,
            test_roles,
            UserRoleEnum.CANDIDATE,
            "candidate@test.com",
        )
        position = await self._create_position_for_company(db_session, test_company)

        headers = await self._get_auth_headers(client, recruiter)

        interview_data = {
            "position_id": position.id,
            "candidate_id": candidate.id,
            "interviewer_id": recruiter.id,
            "scheduled_at": (get_utc_now() + timedelta(days=1)).isoformat(),
            "duration_minutes": 45,
        }

        response = await client.post(
            "/api/interviews", json=interview_data, headers=headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["interviewer_id"] == recruiter.id

    @pytest.mark.asyncio
    async def test_recruiter_cannot_create_interviews_other_company(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Recruiter cannot create interviews for other companies."""
        recruiter = await self._create_user_with_role(
            db_session,
            test_company,
            test_roles,
            UserRoleEnum.MEMBER,
            "recruiter@test.com",
        )
        other_company = await self._create_other_company(db_session)
        other_position = await self._create_position_for_company(
            db_session, other_company
        )
        other_candidate = await self._create_user_with_role(
            db_session,
            other_company,
            test_roles,
            UserRoleEnum.CANDIDATE,
            "othercandidate@test.com",
        )

        headers = await self._get_auth_headers(client, recruiter)

        interview_data = {
            "position_id": other_position.id,
            "candidate_id": other_candidate.id,
            "interviewer_id": recruiter.id,
            "scheduled_at": (get_utc_now() + timedelta(days=1)).isoformat(),
        }

        response = await client.post(
            "/api/interviews", json=interview_data, headers=headers
        )

        assert response.status_code == 403
        assert "other company" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_recruiter_can_manage_own_company_interviews(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Recruiter can manage interviews related to their company."""
        recruiter = await self._create_user_with_role(
            db_session,
            test_company,
            test_roles,
            UserRoleEnum.MEMBER,
            "recruiter@test.com",
        )
        interview = await self._create_interview_for_company(
            db_session, test_company, test_roles
        )

        headers = await self._get_auth_headers(client, recruiter)

        # Can view company-related interview
        response = await client.get(f"/api/interviews/{interview.id}", headers=headers)
        assert response.status_code == 200

        # Can update company-related interview
        update_data = {"notes": "Updated by recruiter"}
        response = await client.put(
            f"/api/interviews/{interview.id}", json=update_data, headers=headers
        )
        assert response.status_code == 200

        # Can cancel company-related interview
        cancel_data = {"reason": "Cancelled by recruiter"}
        response = await client.post(
            f"/api/interviews/{interview.id}/cancel", json=cancel_data, headers=headers
        )
        assert response.status_code == 200

    # ===== EMPLOYER PERMISSIONS =====

    @pytest.mark.asyncio
    async def test_employer_can_create_interviews_own_company(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Employer can create interviews for their company."""
        employer = await self._create_user_with_role(
            db_session,
            test_company,
            test_roles,
            UserRoleEnum.MEMBER,
            "employer@test.com",
        )
        candidate = await self._create_user_with_role(
            db_session,
            test_company,
            test_roles,
            UserRoleEnum.CANDIDATE,
            "candidate@test.com",
        )
        position = await self._create_position_for_company(db_session, test_company)

        headers = await self._get_auth_headers(client, employer)

        interview_data = {
            "position_id": position.id,
            "candidate_id": candidate.id,
            "interviewer_id": employer.id,
            "scheduled_at": (get_utc_now() + timedelta(days=1)).isoformat(),
            "duration_minutes": 30,
        }

        response = await client.post(
            "/api/interviews", json=interview_data, headers=headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["interviewer_id"] == employer.id

    @pytest.mark.asyncio
    async def test_employer_can_manage_own_company_interviews(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Employer can manage interviews related to their company."""
        employer = await self._create_user_with_role(
            db_session,
            test_company,
            test_roles,
            UserRoleEnum.MEMBER,
            "employer@test.com",
        )
        interview = await self._create_interview_for_company(
            db_session, test_company, test_roles
        )

        headers = await self._get_auth_headers(client, employer)

        # Can view company-related interview
        response = await client.get(f"/api/interviews/{interview.id}", headers=headers)
        assert response.status_code == 200

        # Can update company-related interview
        update_data = {"feedback": "Updated by employer"}
        response = await client.put(
            f"/api/interviews/{interview.id}", json=update_data, headers=headers
        )
        assert response.status_code == 200

    # ===== CANDIDATE RESTRICTED PERMISSIONS =====

    @pytest.mark.asyncio
    async def test_candidate_cannot_create_interviews(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Candidate cannot create interviews."""
        candidate = await self._create_user_with_role(
            db_session,
            test_company,
            test_roles,
            UserRoleEnum.CANDIDATE,
            "candidate@test.com",
        )
        recruiter = await self._create_user_with_role(
            db_session,
            test_company,
            test_roles,
            UserRoleEnum.MEMBER,
            "recruiter@test.com",
        )
        position = await self._create_position_for_company(db_session, test_company)

        headers = await self._get_auth_headers(client, candidate)

        interview_data = {
            "position_id": position.id,
            "candidate_id": candidate.id,
            "interviewer_id": recruiter.id,
            "scheduled_at": (get_utc_now() + timedelta(days=1)).isoformat(),
        }

        response = await client.post(
            "/api/interviews", json=interview_data, headers=headers
        )

        assert response.status_code == 403
        assert "cannot create" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_candidate_can_view_own_interviews_only(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Candidate can only view their own interviews."""
        candidate1 = await self._create_user_with_role(
            db_session,
            test_company,
            test_roles,
            UserRoleEnum.CANDIDATE,
            "candidate1@test.com",
        )
        candidate2 = await self._create_user_with_role(
            db_session,
            test_company,
            test_roles,
            UserRoleEnum.CANDIDATE,
            "candidate2@test.com",
        )

        # Create interviews for both candidates
        own_interview = await self._create_interview_for_candidate(
            db_session, test_company, test_roles, candidate1
        )
        other_interview = await self._create_interview_for_candidate(
            db_session, test_company, test_roles, candidate2
        )

        headers = await self._get_auth_headers(client, candidate1)

        # Can view own interview
        response = await client.get(
            f"/api/interviews/{own_interview.id}", headers=headers
        )
        assert response.status_code == 200

        # Cannot view other candidate's interview
        response = await client.get(
            f"/api/interviews/{other_interview.id}", headers=headers
        )
        assert response.status_code == 403
        assert "not your interview" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_candidate_can_update_own_interviews_only(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Candidate can only update their own interviews."""
        candidate1 = await self._create_user_with_role(
            db_session,
            test_company,
            test_roles,
            UserRoleEnum.CANDIDATE,
            "candidate1@test.com",
        )
        candidate2 = await self._create_user_with_role(
            db_session,
            test_company,
            test_roles,
            UserRoleEnum.CANDIDATE,
            "candidate2@test.com",
        )

        own_interview = await self._create_interview_for_candidate(
            db_session, test_company, test_roles, candidate1
        )
        other_interview = await self._create_interview_for_candidate(
            db_session, test_company, test_roles, candidate2
        )

        headers = await self._get_auth_headers(client, candidate1)
        update_data = {"candidate_notes": "Updated by candidate"}

        # Can update own interview
        response = await client.put(
            f"/api/interviews/{own_interview.id}", json=update_data, headers=headers
        )
        assert response.status_code == 200

        # Cannot update other candidate's interview
        response = await client.put(
            f"/api/interviews/{other_interview.id}", json=update_data, headers=headers
        )
        assert response.status_code == 403
        assert "not your interview" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_candidate_can_cancel_own_interviews_only(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Candidate can only cancel their own interviews."""
        candidate1 = await self._create_user_with_role(
            db_session,
            test_company,
            test_roles,
            UserRoleEnum.CANDIDATE,
            "candidate1@test.com",
        )
        candidate2 = await self._create_user_with_role(
            db_session,
            test_company,
            test_roles,
            UserRoleEnum.CANDIDATE,
            "candidate2@test.com",
        )

        own_interview = await self._create_interview_for_candidate(
            db_session, test_company, test_roles, candidate1
        )
        other_interview = await self._create_interview_for_candidate(
            db_session, test_company, test_roles, candidate2
        )

        headers = await self._get_auth_headers(client, candidate1)
        cancel_data = {"reason": "Cancelled by candidate"}

        # Can cancel own interview
        response = await client.post(
            f"/api/interviews/{own_interview.id}/cancel",
            json=cancel_data,
            headers=headers,
        )
        assert response.status_code == 200

        # Cannot cancel other candidate's interview
        response = await client.post(
            f"/api/interviews/{other_interview.id}/cancel",
            json=cancel_data,
            headers=headers,
        )
        assert response.status_code == 403
        assert "not your interview" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_candidate_cannot_delete_interviews(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Candidate cannot delete interviews even their own."""
        candidate = await self._create_user_with_role(
            db_session,
            test_company,
            test_roles,
            UserRoleEnum.CANDIDATE,
            "candidate@test.com",
        )
        own_interview = await self._create_interview_for_candidate(
            db_session, test_company, test_roles, candidate
        )

        headers = await self._get_auth_headers(client, candidate)

        response = await client.delete(
            f"/api/interviews/{own_interview.id}", headers=headers
        )
        assert response.status_code == 403
        assert "cannot delete" in response.json()["detail"].lower()

    # ===== INTERVIEW PROPOSALS PERMISSIONS =====

    @pytest.mark.asyncio
    async def test_interview_proposals_company_scoping(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that interview proposal operations respect company scoping."""
        recruiter = await self._create_user_with_role(
            db_session,
            test_company,
            test_roles,
            UserRoleEnum.MEMBER,
            "recruiter@test.com",
        )
        interview = await self._create_interview_for_company(
            db_session, test_company, test_roles
        )

        headers = await self._get_auth_headers(client, recruiter)

        # Can create proposal for company interview
        proposal_data = {
            "proposed_time": (get_utc_now() + timedelta(days=2)).isoformat(),
            "message": "Alternative time proposal",
        }

        response = await client.post(
            f"/api/interviews/{interview.id}/proposals",
            json=proposal_data,
            headers=headers,
        )
        assert response.status_code == 201

        # Can view proposals for company interview
        response = await client.get(
            f"/api/interviews/{interview.id}/proposals", headers=headers
        )
        assert response.status_code == 200

    # ===== CALENDAR AND STATISTICS PERMISSIONS =====

    @pytest.mark.asyncio
    async def test_interview_calendar_company_scoping(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that interview calendar respects company scoping."""
        recruiter = await self._create_user_with_role(
            db_session,
            test_company,
            test_roles,
            UserRoleEnum.MEMBER,
            "recruiter@test.com",
        )
        headers = await self._get_auth_headers(client, recruiter)

        response = await client.get(
            "/api/interviews/calendar?start_date=2024-01-01&end_date=2024-12-31",
            headers=headers,
        )

        assert response.status_code == 200
        data = response.json()
        # Should only show interviews related to recruiter's company
        assert "events" in data

    @pytest.mark.asyncio
    async def test_interview_statistics_company_scoping(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that interview statistics respect company scoping."""
        recruiter = await self._create_user_with_role(
            db_session,
            test_company,
            test_roles,
            UserRoleEnum.MEMBER,
            "recruiter@test.com",
        )
        headers = await self._get_auth_headers(client, recruiter)

        response = await client.get("/api/interviews/statistics", headers=headers)

        assert response.status_code == 200
        data = response.json()
        # Should only show statistics for recruiter's company
        assert "total_interviews" in data or "statistics" in data

    @pytest.mark.asyncio
    async def test_candidate_cannot_view_interview_statistics(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Candidate cannot view interview statistics."""
        candidate = await self._create_user_with_role(
            db_session,
            test_company,
            test_roles,
            UserRoleEnum.CANDIDATE,
            "candidate@test.com",
        )
        headers = await self._get_auth_headers(client, candidate)

        response = await client.get("/api/interviews/statistics", headers=headers)
        assert response.status_code == 403
        assert "access required" in response.json()["detail"].lower()

    # ===== AUTHENTICATION BOUNDARY TESTS =====

    @pytest.mark.asyncio
    async def test_unauthenticated_interview_access(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test unauthenticated access to interview endpoints."""
        interview = await self._create_interview_for_company(
            db_session, test_company, test_roles
        )

        endpoints = [
            ("GET", "/api/interviews"),
            ("POST", "/api/interviews"),
            ("GET", f"/api/interviews/{interview.id}"),
            ("PUT", f"/api/interviews/{interview.id}"),
            ("DELETE", f"/api/interviews/{interview.id}"),
            ("POST", f"/api/interviews/{interview.id}/cancel"),
            ("GET", f"/api/interviews/{interview.id}/proposals"),
            ("POST", f"/api/interviews/{interview.id}/proposals"),
            ("GET", "/api/interviews/statistics"),
            ("GET", "/api/interviews/calendar"),
        ]

        for method, endpoint in endpoints:
            if method == "GET":
                response = await client.get(endpoint)
            elif method == "POST":
                response = await client.post(endpoint, json={"test": "data"})
            elif method == "PUT":
                response = await client.put(endpoint, json={"test": "data"})
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

    async def _create_position_for_company(
        self,
        db_session: AsyncSession,
        company: Company,
        posted_by_user: User | None = None,
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
            company_id=company.id,
            status="published",
            slug=f"test-position-{company.id}",
            posted_by=posted_by_user.id,
        )
        db_session.add(position)
        await db_session.commit()
        await db_session.refresh(position)
        return position

    async def _create_interview_for_company(
        self, db_session: AsyncSession, company: Company, test_roles: dict
    ) -> Interview:
        """Create an interview for a company."""
        recruiter = await self._create_user_with_role(
            db_session,
            company,
            test_roles,
            UserRoleEnum.MEMBER,
            f"recruiter{company.id}@test.com",
        )
        candidate = await self._create_user_with_role(
            db_session,
            company,
            test_roles,
            UserRoleEnum.CANDIDATE,
            f"candidate{company.id}@test.com",
        )
        position = await self._create_position_for_company(db_session, company)

        interview = Interview(
            position_id=position.id,
            candidate_id=candidate.id,
            interviewer_id=recruiter.id,
            scheduled_at=get_utc_now() + timedelta(days=1),
            duration_minutes=60,
            interview_type="technical",
            status="scheduled",
            location="Conference Room",
        )
        db_session.add(interview)
        await db_session.commit()
        await db_session.refresh(interview)
        return interview

    async def _create_interview_for_candidate(
        self,
        db_session: AsyncSession,
        company: Company,
        test_roles: dict,
        candidate: User,
    ) -> Interview:
        """Create an interview for a specific candidate."""
        recruiter = await self._create_user_with_role(
            db_session,
            company,
            test_roles,
            UserRoleEnum.MEMBER,
            f"recruiter{candidate.id}@test.com",
        )
        position = await self._create_position_for_company(db_session, company)

        interview = Interview(
            position_id=position.id,
            candidate_id=candidate.id,
            interviewer_id=recruiter.id,
            scheduled_at=get_utc_now() + timedelta(days=1),
            duration_minutes=60,
            interview_type="behavioral",
            status="scheduled",
            location="Conference Room",
        )
        db_session.add(interview)
        await db_session.commit()
        await db_session.refresh(interview)
        return interview

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
