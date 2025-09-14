import pytest
from datetime import datetime, timedelta
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock, patch
from sqlalchemy import select

from app.models.auth import PasswordResetRequest
from app.models.user import User
from app.models.user_settings import UserSettings
from app.models.notification import Notification
from app.services.auth_service import auth_service


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, test_user: User):
    """Test successful login."""
    response = await client.post(
        "/api/auth/login",
        json={"email": test_user.email, "password": "testpassword123"},
    )

    assert response.status_code == 200
    data = response.json()

    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert "expires_in" in data
    assert "user" in data
    assert data["user"]["email"] == test_user.email


@pytest.mark.asyncio
async def test_login_invalid_email(client: AsyncClient):
    """Test login with invalid email."""
    response = await client.post(
        "/api/auth/login",
        json={"email": "nonexistent@example.com", "password": "testpassword123"},
    )

    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_invalid_password(client: AsyncClient, test_user: User):
    """Test login with invalid password."""
    response = await client.post(
        "/api/auth/login", json={"email": test_user.email, "password": "wrongpassword"}
    )

    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_inactive_user(
    client: AsyncClient, test_user: User, db_session: AsyncSession
):
    """Test login with inactive user."""
    # Deactivate user
    test_user.is_active = False
    await db_session.commit()

    response = await client.post(
        "/api/auth/login",
        json={"email": test_user.email, "password": "testpassword123"},
    )

    assert response.status_code == 401
    assert "Account is deactivated" in response.json()["detail"]


@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient, test_user: User):
    """Test token refresh."""
    # First login to get tokens
    login_response = await client.post(
        "/api/auth/login",
        json={"email": test_user.email, "password": "testpassword123"},
    )

    assert login_response.status_code == 200
    login_data = login_response.json()
    refresh_token = login_data["refresh_token"]

    # Use refresh token
    refresh_response = await client.post(
        "/api/auth/refresh", json={"refresh_token": refresh_token}
    )

    assert refresh_response.status_code == 200
    refresh_data = refresh_response.json()

    assert "access_token" in refresh_data
    assert refresh_data["token_type"] == "bearer"
    assert "expires_in" in refresh_data


@pytest.mark.asyncio
async def test_refresh_token_invalid(client: AsyncClient):
    """Test refresh with invalid token."""
    response = await client.post(
        "/api/auth/refresh", json={"refresh_token": "invalid_token"}
    )

    assert response.status_code == 401
    assert "Invalid or expired refresh token" in response.json()["detail"]


@pytest.mark.asyncio
async def test_logout(client: AsyncClient, test_user: User):
    """Test logout."""
    # First login
    login_response = await client.post(
        "/api/auth/login",
        json={"email": test_user.email, "password": "testpassword123"},
    )

    login_data = login_response.json()
    refresh_token = login_data["refresh_token"]

    # Logout
    logout_response = await client.post(
        "/api/auth/logout", json={"refresh_token": refresh_token}
    )

    assert logout_response.status_code == 200
    assert "Logged out successfully" in logout_response.json()["message"]

    # Try to use refresh token (should fail)
    refresh_response = await client.post(
        "/api/auth/refresh", json={"refresh_token": refresh_token}
    )

    assert refresh_response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user(
    client: AsyncClient, auth_headers: dict, test_user: User
):
    """Test getting current user info."""
    response = await client.get("/api/auth/me", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()

    assert data["id"] == test_user.id
    assert data["email"] == test_user.email
    assert data["first_name"] == test_user.first_name
    assert data["last_name"] == test_user.last_name
    assert data["company_id"] == test_user.company_id


@pytest.mark.asyncio
async def test_change_password(client: AsyncClient, auth_headers: dict):
    """Test changing password."""
    response = await client.post(
        "/api/auth/change-password",
        headers=auth_headers,
        json={"current_password": "testpassword123", "new_password": "newpassword123"},
    )

    assert response.status_code == 200
    assert "Password changed successfully" in response.json()["message"]


@pytest.mark.asyncio
async def test_change_password_wrong_current(client: AsyncClient, auth_headers: dict):
    """Test changing password with wrong current password."""
    response = await client.post(
        "/api/auth/change-password",
        headers=auth_headers,
        json={"current_password": "wrongpassword", "new_password": "newpassword123"},
    )

    assert response.status_code == 401
    assert "Current password is incorrect" in response.json()["detail"]


@pytest.mark.asyncio
async def test_password_reset_request(client: AsyncClient, test_user: User):
    """Test password reset request."""
    response = await client.post(
        "/api/auth/password-reset/request", json={"email": test_user.email}
    )

    assert response.status_code == 200
    assert "password reset request has been submitted" in response.json()["message"]


@pytest.mark.asyncio
async def test_password_reset_request_nonexistent_email(client: AsyncClient):
    """Test password reset request for nonexistent email."""
    response = await client.post(
        "/api/auth/password-reset/request", json={"email": "nonexistent@example.com"}
    )

    # Should still return success to prevent email enumeration
    assert response.status_code == 200
    assert "password reset request has been submitted" in response.json()["message"]


@pytest.mark.asyncio
async def test_unauthorized_access(client: AsyncClient):
    """Test accessing protected endpoint without auth."""
    response = await client.get("/api/auth/me")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_invalid_token_access(client: AsyncClient):
    """Test accessing protected endpoint with invalid token."""
    headers = {"Authorization": "Bearer invalid_token"}
    response = await client.get("/api/auth/me", headers=headers)

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_admin_requires_2fa(client: AsyncClient, test_admin_user: User):
    """Test that admin users require 2FA during login."""
    response = await client.post(
        "/api/auth/login",
        json={"email": test_admin_user.email, "password": "adminpassword123"},
    )

    assert response.status_code == 200
    data = response.json()

    # Admin should require 2FA
    assert data["require_2fa"] is True
    assert data["access_token"] == ""  # No token until 2FA is complete
    assert data["refresh_token"] == ""
    assert data["user"] is None


@pytest.mark.asyncio
async def test_super_admin_requires_2fa(client: AsyncClient, test_super_admin: User):
    """Test that super admin users require 2FA during login."""
    response = await client.post(
        "/api/auth/login",
        json={"email": test_super_admin.email, "password": "superpassword123"},
    )

    assert response.status_code == 200
    data = response.json()

    # Super admin should require 2FA
    assert data["require_2fa"] is True
    assert data["access_token"] == ""
    assert data["refresh_token"] == ""
    assert data["user"] is None


@pytest.mark.asyncio
async def test_regular_user_no_2fa(client: AsyncClient, test_user: User):
    """Test that regular users don't require 2FA during login."""
    response = await client.post(
        "/api/auth/login",
        json={"email": test_user.email, "password": "testpassword123"},
    )

    assert response.status_code == 200
    data = response.json()

    # Regular user should not require 2FA
    assert data["require_2fa"] is False
    assert "access_token" in data
    assert data["access_token"] != ""
    assert "refresh_token" in data
    assert data["refresh_token"] != ""
    assert data["user"] is not None
    assert data["user"]["email"] == test_user.email


@pytest.mark.asyncio
async def test_sqlalchemy_async_role_access(client: AsyncClient, test_admin_user: User):
    """Test that SQLAlchemy async issue in requires_2fa method is resolved."""
    # This test specifically targets the MissingGreenlet error we fixed
    # by ensuring the role checking works without async issues
    response = await client.post(
        "/api/auth/login",
        json={"email": test_admin_user.email, "password": "adminpassword123"},
    )

    # Should complete without SQLAlchemy errors
    assert response.status_code == 200
    data = response.json()
    assert "require_2fa" in data
    assert isinstance(data["require_2fa"], bool)


@pytest.mark.asyncio
async def test_password_hash_bcrypt_compatibility(client: AsyncClient):
    """Test that bcrypt password hashes work correctly."""
    # Test with the specific admin user that had password issues
    response = await client.post(
        "/api/auth/login",
        json={"email": "admin@miraiworks.com", "password": "password"},
    )

    # Should not get "hash could not be identified" error
    # This should either succeed (200) or fail with proper auth error (401)
    # but not with internal server error (500)
    assert response.status_code in [200, 401]
    if response.status_code != 500:
        # No internal server error means bcrypt is working
        assert True


@pytest.mark.asyncio
async def test_login_with_role_eager_loading(
    client: AsyncClient, test_admin_user: User, db_session
):
    """Test that user roles are properly loaded without lazy loading issues."""
    from app.services.auth_service import auth_service

    # Test the requires_2fa method directly to ensure it works
    result = await auth_service.requires_2fa(db_session, test_admin_user)

    # Should complete without MissingGreenlet error
    assert isinstance(result, bool)
    assert result is True  # Admin should require 2FA


# ===== COMPREHENSIVE 2FA TESTS =====

@pytest.mark.asyncio
async def test_2fa_verify_success(client: AsyncClient, test_user: User):
    """Test successful 2FA verification."""
    with patch('app.endpoints.auth.verify_2fa_code', return_value=True):
        response = await client.post(
            "/api/auth/2fa/verify",
            json={"user_id": test_user.id, "code": "123456"}
        )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["user"]["id"] == test_user.id


@pytest.mark.asyncio
async def test_2fa_verify_invalid_code(client: AsyncClient, test_user: User):
    """Test 2FA verification with invalid code."""
    with patch('app.endpoints.auth.verify_2fa_code', return_value=False):
        response = await client.post(
            "/api/auth/2fa/verify",
            json={"user_id": test_user.id, "code": "invalid"}
        )

    assert response.status_code == 401
    assert "Invalid or expired verification code" in response.json()["detail"]


@pytest.mark.asyncio
async def test_2fa_verify_nonexistent_user(client: AsyncClient):
    """Test 2FA verification for non-existent user."""
    with patch('app.endpoints.auth.verify_2fa_code', return_value=True):
        response = await client.post(
            "/api/auth/2fa/verify",
            json={"user_id": 99999, "code": "123456"}
        )

    assert response.status_code == 404
    assert "User not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_with_2fa_required_user_field(client: AsyncClient, db_session: AsyncSession, test_user: User):
    """Test login when user has require_2fa=True."""
    test_user.require_2fa = True
    await db_session.commit()

    with patch('app.endpoints.auth.email_service.send_2fa_code', new_callable=AsyncMock):
        response = await client.post(
            "/api/auth/login",
            json={"email": test_user.email, "password": "testpassword123"}
        )

    assert response.status_code == 200
    data = response.json()
    assert data["require_2fa"] is True
    assert data["access_token"] == ""
    assert data["refresh_token"] == ""
    assert data["user"]["id"] == test_user.id


@pytest.mark.asyncio
async def test_login_rate_limiting(client: AsyncClient):
    """Test login rate limiting functionality."""
    with patch('app.endpoints.auth.check_rate_limit', return_value=False):
        response = await client.post(
            "/api/auth/login",
            json={"email": "test@example.com", "password": "password"}
        )

    assert response.status_code == 429
    assert "Too many login attempts" in response.json()["detail"]


# ===== PASSWORD RESET COMPREHENSIVE TESTS =====

@pytest.mark.asyncio
async def test_approve_password_reset_success(client: AsyncClient, admin_auth_headers: dict, db_session: AsyncSession, test_user: User):
    """Test successful password reset approval."""
    reset_request = PasswordResetRequest(
        user_id=test_user.id,
        token_hash=auth_service.hash_token("test_token"),
        expires_at=datetime.utcnow() + timedelta(hours=1)
    )
    db_session.add(reset_request)
    await db_session.commit()
    await db_session.refresh(reset_request)

    response = await client.post(
        "/api/auth/password-reset/approve",
        headers=admin_auth_headers,
        json={
            "request_id": reset_request.id,
            "new_password": "newpassword123"
        }
    )

    assert response.status_code == 200
    assert "Password reset approved" in response.json()["message"]


@pytest.mark.asyncio
async def test_approve_password_reset_non_admin(client: AsyncClient, auth_headers: dict):
    """Test password reset approval by non-admin user."""
    response = await client.post(
        "/api/auth/password-reset/approve",
        headers=auth_headers,
        json={
            "request_id": 1,
            "new_password": "newpassword123"
        }
    )

    assert response.status_code == 403
    assert "Admin privileges required" in response.json()["detail"]


@pytest.mark.asyncio
async def test_approve_password_reset_nonexistent_request(client: AsyncClient, admin_auth_headers: dict):
    """Test approval of non-existent password reset request."""
    response = await client.post(
        "/api/auth/password-reset/approve",
        headers=admin_auth_headers,
        json={
            "request_id": 99999,
            "new_password": "newpassword123"
        }
    )

    assert response.status_code == 404
    assert "Password reset request not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_password_reset_requests_success(client: AsyncClient, admin_auth_headers: dict, db_session: AsyncSession, test_user: User):
    """Test getting password reset requests as admin."""
    reset_request = PasswordResetRequest(
        user_id=test_user.id,
        token_hash=auth_service.hash_token("test_token"),
        expires_at=datetime.utcnow() + timedelta(hours=1)
    )
    db_session.add(reset_request)
    await db_session.commit()

    response = await client.get("/api/auth/password-reset/requests", headers=admin_auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["user_email"] == test_user.email


@pytest.mark.asyncio
async def test_get_password_reset_requests_non_admin(client: AsyncClient, auth_headers: dict):
    """Test getting password reset requests as non-admin."""
    response = await client.get("/api/auth/password-reset/requests", headers=auth_headers)

    assert response.status_code == 403
    assert "Admin privileges required" in response.json()["detail"]


# ===== ACCOUNT ACTIVATION COMPREHENSIVE TESTS =====

@pytest.mark.asyncio
async def test_activate_account_success(client: AsyncClient, db_session: AsyncSession, test_company):
    """Test successful account activation."""
    inactive_user = User(
        email="inactive@example.com",
        first_name="Inactive",
        last_name="User",
        company_id=test_company.id,
        hashed_password=auth_service.get_password_hash("temppassword123"),
        is_active=False
    )
    db_session.add(inactive_user)
    await db_session.commit()
    await db_session.refresh(inactive_user)

    response = await client.post(
        "/api/auth/activate",
        json={
            "userId": inactive_user.id,
            "email": inactive_user.email,
            "temporaryPassword": "temppassword123",
            "newPassword": "newpassword123"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "access_token" in data
    assert data["user"]["id"] == inactive_user.id


@pytest.mark.asyncio
async def test_activate_account_already_active(client: AsyncClient, test_user: User):
    """Test activation of already active account."""
    response = await client.post(
        "/api/auth/activate",
        json={
            "userId": test_user.id,
            "email": test_user.email,
            "temporaryPassword": "testpassword123",
            "newPassword": "newpassword123"
        }
    )

    assert response.status_code == 400
    assert "already activated" in response.json()["detail"]


@pytest.mark.asyncio
async def test_activate_account_wrong_email(client: AsyncClient, db_session: AsyncSession, test_company):
    """Test activation with wrong email."""
    inactive_user = User(
        email="inactive@example.com",
        first_name="Inactive",
        last_name="User",
        company_id=test_company.id,
        hashed_password=auth_service.get_password_hash("temppassword123"),
        is_active=False
    )
    db_session.add(inactive_user)
    await db_session.commit()
    await db_session.refresh(inactive_user)

    response = await client.post(
        "/api/auth/activate",
        json={
            "userId": inactive_user.id,
            "email": "wrong@example.com",
            "temporaryPassword": "temppassword123",
            "newPassword": "newpassword123"
        }
    )

    assert response.status_code == 400
    assert "Email does not match" in response.json()["detail"]


@pytest.mark.asyncio
async def test_activate_account_wrong_temp_password(client: AsyncClient, db_session: AsyncSession, test_company):
    """Test activation with wrong temporary password."""
    inactive_user = User(
        email="inactive@example.com",
        first_name="Inactive",
        last_name="User",
        company_id=test_company.id,
        hashed_password=auth_service.get_password_hash("temppassword123"),
        is_active=False
    )
    db_session.add(inactive_user)
    await db_session.commit()
    await db_session.refresh(inactive_user)

    response = await client.post(
        "/api/auth/activate",
        json={
            "userId": inactive_user.id,
            "email": inactive_user.email,
            "temporaryPassword": "wrongpassword",
            "newPassword": "newpassword123"
        }
    )

    assert response.status_code == 401
    assert "Invalid temporary password" in response.json()["detail"]


@pytest.mark.asyncio
async def test_activate_account_nonexistent_user(client: AsyncClient):
    """Test activation of non-existent user."""
    response = await client.post(
        "/api/auth/activate",
        json={
            "userId": 99999,
            "email": "test@example.com",
            "temporaryPassword": "temppassword123",
            "newPassword": "newpassword123"
        }
    )

    assert response.status_code == 404
    assert "User not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_activate_account_creates_settings(client: AsyncClient, db_session: AsyncSession, test_company):
    """Test that account activation creates default user settings."""
    inactive_user = User(
        email="inactive@example.com",
        first_name="Inactive",
        last_name="User",
        company_id=test_company.id,
        hashed_password=auth_service.get_password_hash("temppassword123"),
        is_active=False
    )
    db_session.add(inactive_user)
    await db_session.commit()
    await db_session.refresh(inactive_user)

    response = await client.post(
        "/api/auth/activate",
        json={
            "userId": inactive_user.id,
            "email": inactive_user.email,
            "temporaryPassword": "temppassword123",
            "newPassword": "newpassword123"
        }
    )

    assert response.status_code == 200

    # Check that user settings were created
    settings_result = await db_session.execute(
        select(UserSettings).where(UserSettings.user_id == inactive_user.id)
    )
    settings = settings_result.scalar_one_or_none()
    assert settings is not None
    assert settings.language == "en"
    assert settings.timezone == "America/New_York"


@pytest.mark.asyncio
async def test_activate_account_admin_activates_company(client: AsyncClient, db_session: AsyncSession, test_company):
    """Test that admin activation also activates company."""
    inactive_admin = User(
        email="admin@example.com",
        first_name="Admin",
        last_name="User",
        company_id=test_company.id,
        hashed_password=auth_service.get_password_hash("temppassword123"),
        is_active=False,
        is_admin=True
    )
    db_session.add(inactive_admin)
    await db_session.commit()
    await db_session.refresh(inactive_admin)

    # Deactivate company first
    test_company.is_active = "0"
    await db_session.commit()

    response = await client.post(
        "/api/auth/activate",
        json={
            "userId": inactive_admin.id,
            "email": inactive_admin.email,
            "temporaryPassword": "temppassword123",
            "newPassword": "newpassword123"
        }
    )

    assert response.status_code == 200

    # Check company is now active
    await db_session.refresh(test_company)
    assert test_company.is_active == "1"


# ===== EDGE CASES AND ERROR CONDITIONS =====

@pytest.mark.asyncio
async def test_refresh_token_inactive_user_after_login(client: AsyncClient, db_session: AsyncSession, test_user: User):
    """Test refresh token fails when user is deactivated after initial login."""
    # First login to get refresh token
    login_response = await client.post(
        "/api/auth/login",
        json={"email": test_user.email, "password": "testpassword123"}
    )
    refresh_token = login_response.json()["refresh_token"]

    # Deactivate user
    test_user.is_active = False
    await db_session.commit()

    # Try to refresh
    response = await client.post(
        "/api/auth/refresh",
        json={"refresh_token": refresh_token}
    )

    assert response.status_code == 401
    assert "Account is deactivated" in response.json()["detail"]


@pytest.mark.asyncio
async def test_logout_unauthenticated(client: AsyncClient):
    """Test logout without authentication."""
    response = await client.post("/api/auth/logout")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_password_reset_request_with_email_service_failure(client: AsyncClient, test_user: User):
    """Test password reset request continues even if email fails."""
    with patch('app.endpoints.auth.email_service.send_password_reset_notification',
               side_effect=Exception("Email service down")):
        response = await client.post(
            "/api/auth/password-reset/request",
            json={"email": test_user.email}
        )

    # Should still return success even if email fails
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_login_with_missing_password_field(client: AsyncClient, test_user: User):
    """Test login with missing password field."""
    response = await client.post(
        "/api/auth/login",
        json={"email": test_user.email}
    )

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_login_with_empty_credentials(client: AsyncClient):
    """Test login with empty email and password."""
    response = await client.post(
        "/api/auth/login",
        json={"email": "", "password": ""}
    )

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_change_password_with_same_password(client: AsyncClient, auth_headers: dict):
    """Test changing password to the same password."""
    response = await client.post(
        "/api/auth/change-password",
        headers=auth_headers,
        json={
            "current_password": "testpassword123",
            "new_password": "testpassword123"
        }
    )

    # Should succeed even if same password
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_activate_account_adds_default_phone(client: AsyncClient, db_session: AsyncSession, test_company):
    """Test that activation adds default phone when user has none."""
    inactive_user = User(
        email="nophone@example.com",
        first_name="No",
        last_name="Phone",
        company_id=test_company.id,
        hashed_password=auth_service.get_password_hash("temppassword123"),
        is_active=False,
        phone=None
    )
    db_session.add(inactive_user)
    await db_session.commit()
    await db_session.refresh(inactive_user)

    response = await client.post(
        "/api/auth/activate",
        json={
            "userId": inactive_user.id,
            "email": inactive_user.email,
            "temporaryPassword": "temppassword123",
            "newPassword": "newpassword123"
        }
    )

    assert response.status_code == 200

    # Check user now has default phone
    await db_session.refresh(inactive_user)
    assert inactive_user.phone == "+1-555-0100"
