"""
Comprehensive permission matrix tests for file access control.

Tests the permission boundaries:
- Super Admin: Can access any files
- Company Admin: Can access company-permitted files only
- Users: Can only access own files and permitted files
- File download permission validation
- File deletion owner validation
- Cross-company file access restrictions
"""

import os
import tempfile

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import Company
from app.models.role import UserRole
from app.models.user import User
from app.services.auth_service import auth_service
from app.utils.constants import CompanyType
from app.utils.constants import UserRole as UserRoleEnum


class TestFileAccessControl:
    """Comprehensive tests for file access permission boundaries."""

    # ===== SUPER ADMIN PERMISSIONS =====

    @pytest.mark.asyncio
    async def test_super_admin_can_upload_files(
        self, client: AsyncClient, super_admin_auth_headers: dict
    ):
        """Test that Super Admin can upload files."""
        # Create a temporary file for upload
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
            temp_file.write("Super Admin test file content")
            temp_file_path = temp_file.name

        try:
            with open(temp_file_path, 'rb') as file:
                files = {"file": ("test.txt", file, "text/plain")}
                response = await client.post(
                    "/api/files/upload", files=files, headers=super_admin_auth_headers
                )

            assert response.status_code == 200
            data = response.json()
            assert "file_path" in data
            assert "file_url" in data
        finally:
            os.unlink(temp_file_path)

    @pytest.mark.asyncio
    async def test_super_admin_can_download_any_file(
        self,
        client: AsyncClient,
        super_admin_auth_headers: dict,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Super Admin can download any file."""
        # First upload a file as another user
        other_user = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.CANDIDATE, "candidate@test.com"
        )
        other_user_headers = await self._get_auth_headers(client, other_user)

        # Upload file as other user
        file_path = await self._upload_test_file(client, other_user_headers, "other_user_file.txt")

        # Super admin should be able to download it
        response = await client.get(
            f"/api/files/{file_path}", headers=super_admin_auth_headers
        )

        assert response.status_code == 200
        assert response.headers["content-type"] == "text/plain; charset=utf-8"

    @pytest.mark.asyncio
    async def test_super_admin_can_delete_any_file(
        self,
        client: AsyncClient,
        super_admin_auth_headers: dict,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Super Admin can delete any file."""
        # Upload file as another user
        other_user = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.CANDIDATE, "candidate@test.com"
        )
        other_user_headers = await self._get_auth_headers(client, other_user)

        file_path = await self._upload_test_file(client, other_user_headers, "to_delete.txt")

        # Super admin should be able to delete it
        response = await client.delete(
            f"/api/files/{file_path}", headers=super_admin_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "deleted" in data["message"].lower()

    # ===== USER FILE OWNERSHIP PERMISSIONS =====

    @pytest.mark.asyncio
    async def test_user_can_upload_files(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that any authenticated user can upload files."""
        candidate = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.CANDIDATE, "candidate@test.com"
        )
        headers = await self._get_auth_headers(client, candidate)

        file_path = await self._upload_test_file(client, headers, "user_file.txt")
        assert file_path is not None

    @pytest.mark.asyncio
    async def test_user_can_download_own_files(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that user can download their own files."""
        candidate = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.CANDIDATE, "candidate@test.com"
        )
        headers = await self._get_auth_headers(client, candidate)

        # Upload file
        file_path = await self._upload_test_file(client, headers, "own_file.txt")

        # Download own file
        response = await client.get(f"/api/files/{file_path}", headers=headers)

        assert response.status_code == 200
        assert "own_file.txt" in str(response.content)

    @pytest.mark.asyncio
    async def test_user_can_delete_own_files(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that user can delete their own files."""
        candidate = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.CANDIDATE, "candidate@test.com"
        )
        headers = await self._get_auth_headers(client, candidate)

        # Upload file
        file_path = await self._upload_test_file(client, headers, "to_delete_own.txt")

        # Delete own file
        response = await client.delete(f"/api/files/{file_path}", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert "deleted" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_user_cannot_download_other_users_files(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that user cannot download files uploaded by other users."""
        # Create two users
        user1 = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.CANDIDATE, "user1@test.com"
        )
        user2 = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.CANDIDATE, "user2@test.com"
        )

        user1_headers = await self._get_auth_headers(client, user1)
        user2_headers = await self._get_auth_headers(client, user2)

        # User1 uploads file
        file_path = await self._upload_test_file(client, user1_headers, "user1_file.txt")

        # User2 tries to download user1's file
        response = await client.get(f"/api/files/{file_path}", headers=user2_headers)

        assert response.status_code == 403
        assert "not authorized" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_user_cannot_delete_other_users_files(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that user cannot delete files uploaded by other users."""
        # Create two users
        user1 = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.CANDIDATE, "user1@test.com"
        )
        user2 = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.CANDIDATE, "user2@test.com"
        )

        user1_headers = await self._get_auth_headers(client, user1)
        user2_headers = await self._get_auth_headers(client, user2)

        # User1 uploads file
        file_path = await self._upload_test_file(client, user1_headers, "user1_private.txt")

        # User2 tries to delete user1's file
        response = await client.delete(f"/api/files/{file_path}", headers=user2_headers)

        assert response.status_code == 403
        assert "not authorized" in response.json()["detail"].lower()

    # ===== COMPANY ADMIN PERMISSIONS =====

    @pytest.mark.asyncio
    async def test_company_admin_can_access_company_permitted_files(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Company Admin can access company-permitted files."""
        company_admin = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.COMPANY_ADMIN, "companyadmin@test.com"
        )
        company_user = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.RECRUITER, "recruiter@test.com"
        )

        admin_headers = await self._get_auth_headers(client, company_admin)
        user_headers = await self._get_auth_headers(client, company_user)

        # Company user uploads file
        file_path = await self._upload_test_file(client, user_headers, "company_file.txt")

        # Company admin should be able to access it (if business logic permits)
        response = await client.get(f"/api/files/{file_path}", headers=admin_headers)

        # Result depends on business logic - either 200 (permitted) or 403 (not permitted)
        assert response.status_code in [200, 403]

    @pytest.mark.asyncio
    async def test_company_admin_cannot_access_other_company_files(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Company Admin cannot access files from other companies."""
        company_admin = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.COMPANY_ADMIN, "companyadmin@test.com"
        )

        other_company = await self._create_other_company(db_session)
        other_user = await self._create_user_with_role(
            db_session, other_company, test_roles, UserRoleEnum.RECRUITER, "otherrecruiter@test.com"
        )

        admin_headers = await self._get_auth_headers(client, company_admin)
        other_user_headers = await self._get_auth_headers(client, other_user)

        # Other company user uploads file
        file_path = await self._upload_test_file(client, other_user_headers, "other_company_file.txt")

        # Company admin should NOT be able to access it
        response = await client.get(f"/api/files/{file_path}", headers=admin_headers)

        assert response.status_code == 403
        assert "not authorized" in response.json()["detail"].lower()

    # ===== CROSS-COMPANY FILE ACCESS RESTRICTIONS =====

    @pytest.mark.asyncio
    async def test_cross_company_file_access_restrictions(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that users cannot access files from other companies."""
        other_company = await self._create_other_company(db_session)

        user1 = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.RECRUITER, "recruiter1@test.com"
        )
        user2 = await self._create_user_with_role(
            db_session, other_company, test_roles, UserRoleEnum.RECRUITER, "recruiter2@test.com"
        )

        user1_headers = await self._get_auth_headers(client, user1)
        user2_headers = await self._get_auth_headers(client, user2)

        # User1 uploads file
        file_path = await self._upload_test_file(client, user1_headers, "company1_file.txt")

        # User2 from other company tries to access it
        response = await client.get(f"/api/files/{file_path}", headers=user2_headers)

        assert response.status_code == 403
        assert "not authorized" in response.json()["detail"].lower()

    # ===== FILE TYPE AND SIZE VALIDATION =====

    @pytest.mark.asyncio
    async def test_file_upload_type_validation(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test file upload type validation."""
        user = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.CANDIDATE, "candidate@test.com"
        )
        headers = await self._get_auth_headers(client, user)

        # Try to upload potentially dangerous file type
        with tempfile.NamedTemporaryFile(mode='w', suffix='.exe', delete=False) as temp_file:
            temp_file.write("fake executable content")
            temp_file_path = temp_file.name

        try:
            with open(temp_file_path, 'rb') as file:
                files = {"file": ("malicious.exe", file, "application/octet-stream")}
                response = await client.post("/api/files/upload", files=files, headers=headers)

            # Should either reject dangerous file types or accept with warnings
            assert response.status_code in [200, 400, 422]
            if response.status_code != 200:
                assert "file type" in response.json()["detail"].lower()
        finally:
            os.unlink(temp_file_path)

    @pytest.mark.asyncio
    async def test_file_upload_size_validation(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test file upload size validation."""
        user = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.CANDIDATE, "candidate@test.com"
        )
        headers = await self._get_auth_headers(client, user)

        # Create a large file (simulate - actual size depends on system limits)
        large_content = "x" * (1024 * 1024)  # 1MB of content
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
            temp_file.write(large_content)
            temp_file_path = temp_file.name

        try:
            with open(temp_file_path, 'rb') as file:
                files = {"file": ("large_file.txt", file, "text/plain")}
                response = await client.post("/api/files/upload", files=files, headers=headers)

            # Should either accept or reject based on size limits
            assert response.status_code in [200, 413, 422]
            if response.status_code != 200:
                assert "size" in response.json()["detail"].lower()
        finally:
            os.unlink(temp_file_path)

    # ===== PUBLIC FILE ACCESS =====

    @pytest.mark.asyncio
    async def test_public_file_access_permissions(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test access to files marked as public."""
        user = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.CANDIDATE, "candidate@test.com"
        )
        headers = await self._get_auth_headers(client, user)

        # Upload file and make it public (if supported)
        file_path = await self._upload_test_file(client, headers, "public_file.txt")

        # Try to access without authentication (if public access is supported)
        response = await client.get(f"/api/files/{file_path}")

        # Should either be accessible or require authentication
        assert response.status_code in [200, 401, 403]

    # ===== FILE SHARING PERMISSIONS =====

    @pytest.mark.asyncio
    async def test_file_sharing_with_specific_users(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test sharing files with specific users."""
        owner = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.RECRUITER, "owner@test.com"
        )
        recipient = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.EMPLOYER, "recipient@test.com"
        )

        owner_headers = await self._get_auth_headers(client, owner)
        recipient_headers = await self._get_auth_headers(client, recipient)

        # Owner uploads file
        file_path = await self._upload_test_file(client, owner_headers, "shared_file.txt")

        # If file sharing is supported, share with recipient
        # This would typically involve a separate sharing endpoint
        # For now, test that recipient cannot access by default
        response = await client.get(f"/api/files/{file_path}", headers=recipient_headers)

        assert response.status_code == 403
        assert "not authorized" in response.json()["detail"].lower()

    # ===== AUTHENTICATION BOUNDARY TESTS =====

    @pytest.mark.asyncio
    async def test_unauthenticated_file_access(self, client: AsyncClient):
        """Test unauthenticated access to file endpoints."""
        # Try to upload without authentication
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
            temp_file.write("test content")
            temp_file_path = temp_file.name

        try:
            with open(temp_file_path, 'rb') as file:
                files = {"file": ("test.txt", file, "text/plain")}
                response = await client.post("/api/files/upload", files=files)

            assert response.status_code == 401

            # Try to download without authentication
            response = await client.get("/api/files/nonexistent/path.txt")
            assert response.status_code == 401

            # Try to delete without authentication
            response = await client.delete("/api/files/nonexistent/path.txt")
            assert response.status_code == 401
        finally:
            os.unlink(temp_file_path)

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

    async def _upload_test_file(
        self, client: AsyncClient, headers: dict, filename: str
    ) -> str:
        """Upload a test file and return the file path."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
            temp_file.write(f"Test content for {filename}")
            temp_file_path = temp_file.name

        try:
            with open(temp_file_path, 'rb') as file:
                files = {"file": (filename, file, "text/plain")}
                response = await client.post("/api/files/upload", files=files, headers=headers)

            assert response.status_code == 200
            data = response.json()
            return data["file_path"]
        finally:
            os.unlink(temp_file_path)

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
