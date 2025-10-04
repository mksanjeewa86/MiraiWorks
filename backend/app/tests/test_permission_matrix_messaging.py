"""
Comprehensive permission matrix tests for messaging restrictions.

Tests the complex messaging permission rules:
- Super Admin: Can ONLY message Company Admins
- Company Admin: Can ONLY message Super Admins
- Recruiter/Employer: Can message each other and Candidates, but NOT Company Admins (except Super Admins)
- Candidate: Can message Recruiters, Employers, and other Candidates
- Cross-company restrictions apply to all roles
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


class TestMessagingPermissionMatrix:
    """Comprehensive tests for messaging permission boundaries."""

    # ===== SUPER ADMIN MESSAGING RESTRICTIONS =====

    @pytest.mark.asyncio
    async def test_super_admin_can_message_company_admins(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Super Admin can message Company Admins."""
        super_admin = await self._create_user_with_role(
            db_session,
            None,
            test_roles,
            UserRoleEnum.SYSTEM_ADMIN,
            "superadmin@test.com",
        )
        company_admin = await self._create_user_with_role(
            db_session,
            test_company,
            test_roles,
            UserRoleEnum.ADMIN,
            "companyadmin@test.com",
        )

        headers = await self._get_auth_headers(client, super_admin)
        message_data = {
            "recipient_id": company_admin.id,
            "content": "Hello from Super Admin",
            "type": "text",
        }

        response = await client.post(
            "/api/messages/send", json=message_data, headers=headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["content"] == message_data["content"]
        assert data["recipient_id"] == company_admin.id

    @pytest.mark.asyncio
    async def test_super_admin_cannot_message_recruiters(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Super Admin cannot message Recruiters."""
        super_admin = await self._create_user_with_role(
            db_session,
            None,
            test_roles,
            UserRoleEnum.SYSTEM_ADMIN,
            "superadmin@test.com",
        )
        recruiter = await self._create_user_with_role(
            db_session,
            test_company,
            test_roles,
            UserRoleEnum.MEMBER,
            "recruiter@test.com",
        )

        headers = await self._get_auth_headers(client, super_admin)
        message_data = {
            "recipient_id": recruiter.id,
            "content": "Hello from Super Admin",
            "type": "text",
        }

        response = await client.post(
            "/api/messages/send", json=message_data, headers=headers
        )

        assert response.status_code == 403
        assert "messaging restrictions" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_super_admin_cannot_message_employers(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Super Admin cannot message Employers."""
        super_admin = await self._create_user_with_role(
            db_session,
            None,
            test_roles,
            UserRoleEnum.SYSTEM_ADMIN,
            "superadmin@test.com",
        )
        employer = await self._create_user_with_role(
            db_session,
            test_company,
            test_roles,
            UserRoleEnum.MEMBER,
            "employer@test.com",
        )

        headers = await self._get_auth_headers(client, super_admin)
        message_data = {
            "recipient_id": employer.id,
            "content": "Hello from Super Admin",
            "type": "text",
        }

        response = await client.post(
            "/api/messages/send", json=message_data, headers=headers
        )

        assert response.status_code == 403
        assert "messaging restrictions" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_super_admin_cannot_message_candidates(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Super Admin cannot message Candidates."""
        super_admin = await self._create_user_with_role(
            db_session,
            None,
            test_roles,
            UserRoleEnum.SYSTEM_ADMIN,
            "superadmin@test.com",
        )
        candidate = await self._create_user_with_role(
            db_session,
            test_company,
            test_roles,
            UserRoleEnum.CANDIDATE,
            "candidate@test.com",
        )

        headers = await self._get_auth_headers(client, super_admin)
        message_data = {
            "recipient_id": candidate.id,
            "content": "Hello from Super Admin",
            "type": "text",
        }

        response = await client.post(
            "/api/messages/send", json=message_data, headers=headers
        )

        assert response.status_code == 403
        assert "messaging restrictions" in response.json()["detail"].lower()

    # ===== COMPANY ADMIN MESSAGING RESTRICTIONS =====

    @pytest.mark.asyncio
    async def test_company_admin_can_message_super_admins(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Company Admin can message Super Admins."""
        company_admin = await self._create_user_with_role(
            db_session,
            test_company,
            test_roles,
            UserRoleEnum.ADMIN,
            "companyadmin@test.com",
        )
        super_admin = await self._create_user_with_role(
            db_session,
            None,
            test_roles,
            UserRoleEnum.SYSTEM_ADMIN,
            "superadmin@test.com",
        )

        headers = await self._get_auth_headers(client, company_admin)
        message_data = {
            "recipient_id": super_admin.id,
            "content": "Hello from Company Admin",
            "type": "text",
        }

        response = await client.post(
            "/api/messages/send", json=message_data, headers=headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["content"] == message_data["content"]
        assert data["recipient_id"] == super_admin.id

    @pytest.mark.asyncio
    async def test_company_admin_cannot_message_recruiters(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Company Admin cannot message Recruiters."""
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

        headers = await self._get_auth_headers(client, company_admin)
        message_data = {
            "recipient_id": recruiter.id,
            "content": "Hello from Company Admin",
            "type": "text",
        }

        response = await client.post(
            "/api/messages/send", json=message_data, headers=headers
        )

        assert response.status_code == 403
        assert "messaging restrictions" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_company_admin_cannot_message_employers(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Company Admin cannot message Employers."""
        company_admin = await self._create_user_with_role(
            db_session,
            test_company,
            test_roles,
            UserRoleEnum.ADMIN,
            "companyadmin@test.com",
        )
        employer = await self._create_user_with_role(
            db_session,
            test_company,
            test_roles,
            UserRoleEnum.MEMBER,
            "employer@test.com",
        )

        headers = await self._get_auth_headers(client, company_admin)
        message_data = {
            "recipient_id": employer.id,
            "content": "Hello from Company Admin",
            "type": "text",
        }

        response = await client.post(
            "/api/messages/send", json=message_data, headers=headers
        )

        assert response.status_code == 403
        assert "messaging restrictions" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_company_admin_cannot_message_candidates(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Company Admin cannot message Candidates."""
        company_admin = await self._create_user_with_role(
            db_session,
            test_company,
            test_roles,
            UserRoleEnum.ADMIN,
            "companyadmin@test.com",
        )
        candidate = await self._create_user_with_role(
            db_session,
            test_company,
            test_roles,
            UserRoleEnum.CANDIDATE,
            "candidate@test.com",
        )

        headers = await self._get_auth_headers(client, company_admin)
        message_data = {
            "recipient_id": candidate.id,
            "content": "Hello from Company Admin",
            "type": "text",
        }

        response = await client.post(
            "/api/messages/send", json=message_data, headers=headers
        )

        assert response.status_code == 403
        assert "messaging restrictions" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_company_admin_cannot_message_other_company_admins(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Company Admin cannot message other Company Admins."""
        company_admin1 = await self._create_user_with_role(
            db_session,
            test_company,
            test_roles,
            UserRoleEnum.ADMIN,
            "companyadmin1@test.com",
        )

        other_company = await self._create_other_company(db_session)
        company_admin2 = await self._create_user_with_role(
            db_session,
            other_company,
            test_roles,
            UserRoleEnum.ADMIN,
            "companyadmin2@test.com",
        )

        headers = await self._get_auth_headers(client, company_admin1)
        message_data = {
            "recipient_id": company_admin2.id,
            "content": "Hello from Company Admin",
            "type": "text",
        }

        response = await client.post(
            "/api/messages/send", json=message_data, headers=headers
        )

        assert response.status_code == 403
        assert "messaging restrictions" in response.json()["detail"].lower()

    # ===== RECRUITER/EMPLOYER MESSAGING PERMISSIONS =====

    @pytest.mark.asyncio
    async def test_recruiter_can_message_employers(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Recruiter can message Employers in same company."""
        recruiter = await self._create_user_with_role(
            db_session,
            test_company,
            test_roles,
            UserRoleEnum.MEMBER,
            "recruiter@test.com",
        )
        employer = await self._create_user_with_role(
            db_session,
            test_company,
            test_roles,
            UserRoleEnum.MEMBER,
            "employer@test.com",
        )

        headers = await self._get_auth_headers(client, recruiter)
        message_data = {
            "recipient_id": employer.id,
            "content": "Hello from Recruiter",
            "type": "text",
        }

        response = await client.post(
            "/api/messages/send", json=message_data, headers=headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["content"] == message_data["content"]

    @pytest.mark.asyncio
    async def test_recruiter_can_message_candidates(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Recruiter can message Candidates."""
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

        headers = await self._get_auth_headers(client, recruiter)
        message_data = {
            "recipient_id": candidate.id,
            "content": "Hello from Recruiter",
            "type": "text",
        }

        response = await client.post(
            "/api/messages/send", json=message_data, headers=headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["content"] == message_data["content"]

    @pytest.mark.asyncio
    async def test_recruiter_can_message_other_recruiters(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Recruiter can message other Recruiters in same company."""
        recruiter1 = await self._create_user_with_role(
            db_session,
            test_company,
            test_roles,
            UserRoleEnum.MEMBER,
            "recruiter1@test.com",
        )
        recruiter2 = await self._create_user_with_role(
            db_session,
            test_company,
            test_roles,
            UserRoleEnum.MEMBER,
            "recruiter2@test.com",
        )

        headers = await self._get_auth_headers(client, recruiter1)
        message_data = {
            "recipient_id": recruiter2.id,
            "content": "Hello from Recruiter",
            "type": "text",
        }

        response = await client.post(
            "/api/messages/send", json=message_data, headers=headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["content"] == message_data["content"]

    @pytest.mark.asyncio
    async def test_recruiter_cannot_message_company_admins(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Recruiter cannot message Company Admins (except Super Admins)."""
        recruiter = await self._create_user_with_role(
            db_session,
            test_company,
            test_roles,
            UserRoleEnum.MEMBER,
            "recruiter@test.com",
        )
        company_admin = await self._create_user_with_role(
            db_session,
            test_company,
            test_roles,
            UserRoleEnum.ADMIN,
            "companyadmin@test.com",
        )

        headers = await self._get_auth_headers(client, recruiter)
        message_data = {
            "recipient_id": company_admin.id,
            "content": "Hello from Recruiter",
            "type": "text",
        }

        response = await client.post(
            "/api/messages/send", json=message_data, headers=headers
        )

        assert response.status_code == 403
        assert "company admin" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_employer_can_message_recruiters(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Employer can message Recruiters in same company."""
        employer = await self._create_user_with_role(
            db_session,
            test_company,
            test_roles,
            UserRoleEnum.MEMBER,
            "employer@test.com",
        )
        recruiter = await self._create_user_with_role(
            db_session,
            test_company,
            test_roles,
            UserRoleEnum.MEMBER,
            "recruiter@test.com",
        )

        headers = await self._get_auth_headers(client, employer)
        message_data = {
            "recipient_id": recruiter.id,
            "content": "Hello from Employer",
            "type": "text",
        }

        response = await client.post(
            "/api/messages/send", json=message_data, headers=headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["content"] == message_data["content"]

    @pytest.mark.asyncio
    async def test_employer_can_message_candidates(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Employer can message Candidates."""
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

        headers = await self._get_auth_headers(client, employer)
        message_data = {
            "recipient_id": candidate.id,
            "content": "Hello from Employer",
            "type": "text",
        }

        response = await client.post(
            "/api/messages/send", json=message_data, headers=headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["content"] == message_data["content"]

    @pytest.mark.asyncio
    async def test_employer_cannot_message_company_admins(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Employer cannot message Company Admins."""
        employer = await self._create_user_with_role(
            db_session,
            test_company,
            test_roles,
            UserRoleEnum.MEMBER,
            "employer@test.com",
        )
        company_admin = await self._create_user_with_role(
            db_session,
            test_company,
            test_roles,
            UserRoleEnum.ADMIN,
            "companyadmin@test.com",
        )

        headers = await self._get_auth_headers(client, employer)
        message_data = {
            "recipient_id": company_admin.id,
            "content": "Hello from Employer",
            "type": "text",
        }

        response = await client.post(
            "/api/messages/send", json=message_data, headers=headers
        )

        assert response.status_code == 403
        assert "company admin" in response.json()["detail"].lower()

    # ===== CANDIDATE MESSAGING PERMISSIONS =====

    @pytest.mark.asyncio
    async def test_candidate_can_message_recruiters(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Candidate can message Recruiters."""
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

        headers = await self._get_auth_headers(client, candidate)
        message_data = {
            "recipient_id": recruiter.id,
            "content": "Hello from Candidate",
            "type": "text",
        }

        response = await client.post(
            "/api/messages/send", json=message_data, headers=headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["content"] == message_data["content"]

    @pytest.mark.asyncio
    async def test_candidate_can_message_employers(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Candidate can message Employers."""
        candidate = await self._create_user_with_role(
            db_session,
            test_company,
            test_roles,
            UserRoleEnum.CANDIDATE,
            "candidate@test.com",
        )
        employer = await self._create_user_with_role(
            db_session,
            test_company,
            test_roles,
            UserRoleEnum.MEMBER,
            "employer@test.com",
        )

        headers = await self._get_auth_headers(client, candidate)
        message_data = {
            "recipient_id": employer.id,
            "content": "Hello from Candidate",
            "type": "text",
        }

        response = await client.post(
            "/api/messages/send", json=message_data, headers=headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["content"] == message_data["content"]

    @pytest.mark.asyncio
    async def test_candidate_can_message_other_candidates(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Candidate can message other Candidates."""
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

        headers = await self._get_auth_headers(client, candidate1)
        message_data = {
            "recipient_id": candidate2.id,
            "content": "Hello from Candidate",
            "type": "text",
        }

        response = await client.post(
            "/api/messages/send", json=message_data, headers=headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["content"] == message_data["content"]

    @pytest.mark.asyncio
    async def test_candidate_cannot_message_company_admins(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Candidate cannot message Company Admins."""
        candidate = await self._create_user_with_role(
            db_session,
            test_company,
            test_roles,
            UserRoleEnum.CANDIDATE,
            "candidate@test.com",
        )
        company_admin = await self._create_user_with_role(
            db_session,
            test_company,
            test_roles,
            UserRoleEnum.ADMIN,
            "companyadmin@test.com",
        )

        headers = await self._get_auth_headers(client, candidate)
        message_data = {
            "recipient_id": company_admin.id,
            "content": "Hello from Candidate",
            "type": "text",
        }

        response = await client.post(
            "/api/messages/send", json=message_data, headers=headers
        )

        assert response.status_code == 403
        assert "company admin" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_candidate_cannot_message_super_admins(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Candidate cannot message Super Admins."""
        candidate = await self._create_user_with_role(
            db_session,
            test_company,
            test_roles,
            UserRoleEnum.CANDIDATE,
            "candidate@test.com",
        )
        super_admin = await self._create_user_with_role(
            db_session,
            None,
            test_roles,
            UserRoleEnum.SYSTEM_ADMIN,
            "superadmin@test.com",
        )

        headers = await self._get_auth_headers(client, candidate)
        message_data = {
            "recipient_id": super_admin.id,
            "content": "Hello from Candidate",
            "type": "text",
        }

        response = await client.post(
            "/api/messages/send", json=message_data, headers=headers
        )

        assert response.status_code == 403
        assert "messaging restrictions" in response.json()["detail"].lower()

    # ===== CROSS-COMPANY MESSAGING RESTRICTIONS =====

    @pytest.mark.asyncio
    async def test_cross_company_messaging_restrictions(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that users cannot message users from other companies (except allowed roles)."""
        other_company = await self._create_other_company(db_session)

        recruiter1 = await self._create_user_with_role(
            db_session,
            test_company,
            test_roles,
            UserRoleEnum.MEMBER,
            "recruiter1@test.com",
        )
        recruiter2 = await self._create_user_with_role(
            db_session,
            other_company,
            test_roles,
            UserRoleEnum.MEMBER,
            "recruiter2@test.com",
        )

        headers = await self._get_auth_headers(client, recruiter1)
        message_data = {
            "recipient_id": recruiter2.id,
            "content": "Cross-company message",
            "type": "text",
        }

        response = await client.post(
            "/api/messages/send", json=message_data, headers=headers
        )

        assert response.status_code == 403
        assert "different company" in response.json()["detail"].lower()

    # ===== MESSAGE VIEWING RESTRICTIONS =====

    @pytest.mark.asyncio
    async def test_restricted_users_list_excludes_forbidden_recipients(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that restricted users list excludes users that cannot be messaged."""
        super_admin = await self._create_user_with_role(
            db_session,
            None,
            test_roles,
            UserRoleEnum.SYSTEM_ADMIN,
            "superadmin@test.com",
        )
        headers = await self._get_auth_headers(client, super_admin)

        response = await client.get("/api/messages/restricted-users", headers=headers)

        assert response.status_code == 200
        data = response.json()
        # Should contain IDs of users Super Admin cannot message
        assert "user_ids" in data

    @pytest.mark.asyncio
    async def test_message_participants_respects_restrictions(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that message participants endpoint respects messaging restrictions."""
        recruiter = await self._create_user_with_role(
            db_session,
            test_company,
            test_roles,
            UserRoleEnum.MEMBER,
            "recruiter@test.com",
        )
        headers = await self._get_auth_headers(client, recruiter)

        response = await client.get("/api/messages/participants", headers=headers)

        assert response.status_code == 200
        data = response.json()
        # Should only include users Recruiter can message
        for participant in data.get("participants", []):
            # Participants should not include Company Admins
            assert "admin" not in participant.get("roles", [])

    # ===== HELPER METHODS =====

    async def _create_user_with_role(
        self,
        db_session: AsyncSession,
        company: Company | None,
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
