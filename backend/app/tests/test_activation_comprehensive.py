"""
Comprehensive Backend Tests for Account Activation
Tests all scenarios, edge cases, and error conditions for user activation.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.models.company import Company
from app.models.role import Role, UserRole
from app.models.user_settings import UserSettings
from app.services.auth_service import auth_service
from app.utils.constants import UserRole as UserRoleEnum


@pytest.mark.asyncio
class TestAccountActivation:
    """Comprehensive tests for account activation functionality."""

    async def test_activation_success_flow(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """Test successful account activation with all required steps."""
        # Create test company
        company = Company(
            name="Test Activation Company",
            email="activation@test.com",
            phone="03-1234-5678",
            type="employer",
        )
        db_session.add(company)
        await db_session.commit()
        await db_session.refresh(company)

        # Create inactive user with temporary password
        temp_password = "TempPass123"
        hashed_password = auth_service.get_password_hash(temp_password)

        user = User(
            email="activate@test.com",
            first_name="Test",
            last_name="User",
            company_id=company.id,
            hashed_password=hashed_password,
            is_active=False,  # Key: user is inactive
            is_admin=False,
            require_2fa=False,
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        # Test activation
        activation_data = {
            "userId": user.id,
            "email": "activate@test.com",
            "temporaryPassword": temp_password,
            "newPassword": "NewSecure@123",
        }

        response = await client.post("/api/auth/activate", json=activation_data)

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert data["success"] is True
        assert data["message"] == "Account activated successfully"
        assert "access_token" in data
        assert "refresh_token" in data
        assert "user" in data

        # Verify user data in response
        user_data = data["user"]
        assert user_data["email"] == "activate@test.com"
        assert user_data["is_active"] is True

        # Verify database changes
        await db_session.refresh(user)
        assert user.is_active is True
        assert user.last_login is not None

        # Verify new password works
        new_password_valid = auth_service.verify_password(
            "NewSecure@123", user.hashed_password
        )
        assert new_password_valid is True

        # Verify old password no longer works
        old_password_valid = auth_service.verify_password(
            temp_password, user.hashed_password
        )
        assert old_password_valid is False

        # Verify user settings were created
        settings_result = await db_session.execute(
            select(UserSettings).where(UserSettings.user_id == user.id)
        )
        settings = settings_result.scalar_one_or_none()
        assert settings is not None
        assert settings.email_notifications is True

    async def test_activation_user_not_found(self, client: AsyncClient):
        """Test activation with non-existent user ID."""
        activation_data = {
            "userId": 99999,  # Non-existent user
            "email": "nonexistent@test.com",
            "temporaryPassword": "TempPass123",
            "newPassword": "NewSecure@123",
        }

        response = await client.post("/api/auth/activate", json=activation_data)

        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]

    async def test_activation_email_mismatch(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """Test activation with mismatched email address."""
        # Create test user
        user = User(
            email="correct@test.com",
            first_name="Test",
            last_name="User",
            hashed_password=auth_service.get_password_hash("TempPass123"),
            is_active=False,
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        activation_data = {
            "userId": user.id,
            "email": "wrong@test.com",  # Wrong email
            "temporaryPassword": "TempPass123",
            "newPassword": "NewSecure@123",
        }

        response = await client.post("/api/auth/activate", json=activation_data)

        assert response.status_code == 400
        assert "Email does not match user record" in response.json()["detail"]

    async def test_activation_already_active_user(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """Test activation attempt on already active user."""
        user = User(
            email="active@test.com",
            first_name="Active",
            last_name="User",
            hashed_password=auth_service.get_password_hash("TempPass123"),
            is_active=True,  # Already active
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        activation_data = {
            "userId": user.id,
            "email": "active@test.com",
            "temporaryPassword": "TempPass123",
            "newPassword": "NewSecure@123",
        }

        response = await client.post("/api/auth/activate", json=activation_data)

        assert response.status_code == 400
        assert "User account is already activated" in response.json()["detail"]

    async def test_activation_invalid_temporary_password(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """Test activation with incorrect temporary password."""
        user = User(
            email="temppass@test.com",
            first_name="TempPass",
            last_name="User",
            hashed_password=auth_service.get_password_hash("CorrectTempPass123"),
            is_active=False,
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        activation_data = {
            "userId": user.id,
            "email": "temppass@test.com",
            "temporaryPassword": "WrongTempPass123",  # Wrong password
            "newPassword": "NewSecure@123",
        }

        response = await client.post("/api/auth/activate", json=activation_data)

        assert response.status_code == 401
        assert "Invalid temporary password" in response.json()["detail"]

    async def test_activation_no_hashed_password(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """Test activation for user with no password set."""
        user = User(
            email="nopass@test.com",
            first_name="NoPass",
            last_name="User",
            hashed_password=None,  # No password set
            is_active=False,
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        activation_data = {
            "userId": user.id,
            "email": "nopass@test.com",
            "temporaryPassword": "AnyPassword123",
            "newPassword": "NewSecure@123",
        }

        response = await client.post("/api/auth/activate", json=activation_data)

        assert response.status_code == 401
        assert "Account not properly configured" in response.json()["detail"]

    async def test_activation_password_validation(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """Test activation with various new password formats."""
        user = User(
            email="passval@test.com",
            first_name="PassVal",
            last_name="User",
            hashed_password=auth_service.get_password_hash("TempPass123"),
            is_active=False,
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        # Test weak password
        weak_password_data = {
            "userId": user.id,
            "email": "passval@test.com",
            "temporaryPassword": "TempPass123",
            "newPassword": "weak",  # Too short
        }

        response = await client.post("/api/auth/activate", json=weak_password_data)
        assert response.status_code == 422  # Validation error

    async def test_activation_case_sensitivity(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """Test that temporary passwords are case-sensitive."""
        temp_password = "CaseSensitive123"
        user = User(
            email="case@test.com",
            first_name="Case",
            last_name="User",
            hashed_password=auth_service.get_password_hash(temp_password),
            is_active=False,
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        # Test with different case
        case_variations = [
            "casesensitive123",  # All lowercase
            "CASESENSITIVE123",  # All uppercase
            "caseSensitive123",  # Different camel case
        ]

        for wrong_case_password in case_variations:
            activation_data = {
                "userId": user.id,
                "email": "case@test.com",
                "temporaryPassword": wrong_case_password,
                "newPassword": "NewSecure@123",
            }

            response = await client.post("/api/auth/activate", json=activation_data)
            assert response.status_code == 401
            assert "Invalid temporary password" in response.json()["detail"]

    async def test_activation_whitespace_handling(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """Test activation with whitespace in passwords."""
        temp_password = "NoSpaces123"
        user = User(
            email="space@test.com",
            first_name="Space",
            last_name="User",
            hashed_password=auth_service.get_password_hash(temp_password),
            is_active=False,
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        # Test with leading/trailing spaces
        space_variations = [
            " NoSpaces123",  # Leading space
            "NoSpaces123 ",  # Trailing space
            " NoSpaces123 ",  # Both spaces
            "No Spaces123",  # Space in middle
        ]

        for spaced_password in space_variations:
            activation_data = {
                "userId": user.id,
                "email": "space@test.com",
                "temporaryPassword": spaced_password,
                "newPassword": "NewSecure@123",
            }

            response = await client.post("/api/auth/activate", json=activation_data)
            assert response.status_code == 401

    async def test_activation_company_admin_flow(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """Test activation flow for company admin user."""
        # Create company
        company = Company(
            name="Admin Test Company",
            email="admin@company.com",
            phone="03-1234-5678",
            type="employer",
            is_active="0",  # Company starts inactive (stored as string)
        )
        db_session.add(company)
        await db_session.commit()
        await db_session.refresh(company)

        # Create company admin role
        admin_role = Role(
            name=UserRoleEnum.COMPANY_ADMIN, description="Company Administrator"
        )
        db_session.add(admin_role)
        await db_session.commit()
        await db_session.refresh(admin_role)

        # Create company admin user
        admin_user = User(
            email="admin@company.com",
            first_name="Company",
            last_name="Admin",
            company_id=company.id,
            hashed_password=auth_service.get_password_hash("AdminTemp123"),
            is_active=False,
            is_admin=True,
            require_2fa=False,
        )
        db_session.add(admin_user)
        await db_session.commit()
        await db_session.refresh(admin_user)

        # Assign admin role
        user_role = UserRole(user_id=admin_user.id, role_id=admin_role.id)
        db_session.add(user_role)
        await db_session.commit()

        # Test activation
        activation_data = {
            "userId": admin_user.id,
            "email": "admin@company.com",
            "temporaryPassword": "AdminTemp123",
            "newPassword": "AdminSecure@123",
        }

        response = await client.post("/api/auth/activate", json=activation_data)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

        # Verify user is activated
        await db_session.refresh(admin_user)
        assert admin_user.is_active is True

        # Verify company is activated (when admin activates)
        await db_session.refresh(company)
        assert (
            company.is_active == "1"
        )  # Note: is_active is stored as string in database

    async def test_activation_missing_phone_default(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """Test that default phone number is added during activation."""
        user = User(
            email="phone@test.com",
            first_name="Phone",
            last_name="User",
            hashed_password=auth_service.get_password_hash("TempPass123"),
            phone=None,  # No phone number
            is_active=False,
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        activation_data = {
            "userId": user.id,
            "email": "phone@test.com",
            "temporaryPassword": "TempPass123",
            "newPassword": "NewSecure@123",
        }

        response = await client.post("/api/auth/activate", json=activation_data)

        assert response.status_code == 200

        # Verify default phone was added
        await db_session.refresh(user)
        assert user.phone == "+1-555-0100"

    async def test_activation_preserves_existing_phone(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """Test that existing phone number is preserved during activation."""
        existing_phone = "+81-90-1234-5678"
        user = User(
            email="existingphone@test.com",
            first_name="ExistingPhone",
            last_name="User",
            hashed_password=auth_service.get_password_hash("TempPass123"),
            phone=existing_phone,
            is_active=False,
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        activation_data = {
            "userId": user.id,
            "email": "existingphone@test.com",
            "temporaryPassword": "TempPass123",
            "newPassword": "NewSecure@123",
        }

        response = await client.post("/api/auth/activate", json=activation_data)

        assert response.status_code == 200

        # Verify phone number was preserved
        await db_session.refresh(user)
        assert user.phone == existing_phone

    async def test_activation_authentication_tokens(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """Test that valid authentication tokens are returned."""
        user = User(
            email="tokens@test.com",
            first_name="Tokens",
            last_name="User",
            hashed_password=auth_service.get_password_hash("TempPass123"),
            is_active=False,
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        activation_data = {
            "userId": user.id,
            "email": "tokens@test.com",
            "temporaryPassword": "TempPass123",
            "newPassword": "NewSecure@123",
        }

        response = await client.post("/api/auth/activate", json=activation_data)

        assert response.status_code == 200
        data = response.json()

        # Verify tokens are present and valid format
        assert "access_token" in data
        assert "refresh_token" in data
        assert "expires_in" in data
        assert isinstance(data["expires_in"], int)
        assert data["expires_in"] > 0

        # Test that tokens can be used for authentication
        headers = {"Authorization": f"Bearer {data['access_token']}"}
        me_response = await client.get("/api/auth/me", headers=headers)
        assert me_response.status_code == 200

        user_info = me_response.json()
        assert user_info["email"] == "tokens@test.com"
        assert user_info["is_active"] is True


@pytest.mark.asyncio
class TestActivationEdgeCases:
    """Test edge cases and unusual scenarios for activation."""

    async def test_activation_special_characters_password(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """Test activation with special characters in passwords."""
        temp_password = "Sp3c!@l#Ch@rs"
        user = User(
            email="special@test.com",
            first_name="Special",
            last_name="User",
            hashed_password=auth_service.get_password_hash(temp_password),
            is_active=False,
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        activation_data = {
            "userId": user.id,
            "email": "special@test.com",
            "temporaryPassword": temp_password,
            "newPassword": "N3wSp3c!@l#P@ss",
        }

        response = await client.post("/api/auth/activate", json=activation_data)
        assert response.status_code == 200

    async def test_activation_unicode_email(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """Test activation with unicode characters in email."""
        unicode_email = "test@例え.テスト"
        user = User(
            email=unicode_email,
            first_name="Unicode",
            last_name="User",
            hashed_password=auth_service.get_password_hash("TempPass123"),
            is_active=False,
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        activation_data = {
            "userId": user.id,
            "email": unicode_email,
            "temporaryPassword": "TempPass123",
            "newPassword": "NewSecure@123",
        }

        response = await client.post("/api/auth/activate", json=activation_data)
        assert response.status_code == 200

    async def test_activation_concurrent_attempts(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """Test multiple concurrent activation attempts (should only work once)."""
        user = User(
            email="concurrent@test.com",
            first_name="Concurrent",
            last_name="User",
            hashed_password=auth_service.get_password_hash("TempPass123"),
            is_active=False,
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        activation_data = {
            "userId": user.id,
            "email": "concurrent@test.com",
            "temporaryPassword": "TempPass123",
            "newPassword": "NewSecure@123",
        }

        # First activation should succeed
        response1 = await client.post("/api/auth/activate", json=activation_data)
        assert response1.status_code == 200

        # Second activation should fail (already activated)
        response2 = await client.post("/api/auth/activate", json=activation_data)
        assert response2.status_code == 400
        assert "already activated" in response2.json()["detail"]
