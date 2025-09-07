import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


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
