"""Focused integration tests for authentication endpoints."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


async def _login(client: AsyncClient, email: str, password: str):
    """Helper to post to the login endpoint."""
    return await client.post(
        "/api/auth/login",
        json={"email": email, "password": password},
    )


@pytest.mark.asyncio
async def test_login_success_returns_tokens(client: AsyncClient, test_user: User):
    response = await _login(client, test_user.email, "testpassword123")

    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == test_user.email
    assert "access_token" in data and data["access_token"]
    assert "refresh_token" in data and data["refresh_token"]


@pytest.mark.asyncio
async def test_login_rejects_invalid_credentials(client: AsyncClient):
    response = await _login(client, "unknown@example.com", "badpass")

    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]


@pytest.mark.asyncio
async def test_refresh_token_cycle(client: AsyncClient, test_user: User):
    login_response = await _login(client, test_user.email, "testpassword123")
    refresh_token = login_response.json()["refresh_token"]

    refresh_response = await client.post(
        "/api/auth/refresh", json={"refresh_token": refresh_token}
    )

    assert refresh_response.status_code == 200
    data = refresh_response.json()
    assert data["token_type"] == "bearer"
    assert "access_token" in data and data["access_token"]


@pytest.mark.asyncio
async def test_refresh_token_invalid_returns_401(client: AsyncClient):
    response = await client.post(
        "/api/auth/refresh", json={"refresh_token": "not-a-real-token"}
    )

    assert response.status_code == 401
    assert "Invalid" in response.json()["detail"]


@pytest.mark.asyncio
async def test_change_password_allows_new_login(
    client: AsyncClient,
    auth_headers: dict,
    test_employer_user: User,
    db_session: AsyncSession,
):
    new_password = "freshpass123"

    change_response = await client.post(
        "/api/auth/change-password",
        headers=auth_headers,
        json={
            "current_password": "employerpassword123",
            "new_password": new_password,
        },
    )
    assert change_response.status_code == 200

    # Old password should now fail
    old_login = await _login(client, test_employer_user.email, "employerpassword123")
    assert old_login.status_code == 401

    # New password should succeed
    new_login = await _login(client, test_employer_user.email, new_password)
    assert new_login.status_code == 200


@pytest.mark.asyncio
async def test_get_current_user_returns_profile(
    client: AsyncClient, auth_headers: dict, test_employer_user: User
):
    response = await client.get("/api/auth/me", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_employer_user.id
    assert data["email"] == test_employer_user.email


# Remember Me Feature Tests
@pytest.mark.asyncio
async def test_login_with_remember_me_creates_30_day_token(
    client: AsyncClient, test_user: User, db_session: AsyncSession
):
    """Test that rememberMe=True creates a refresh token with 30-day expiration."""
    from datetime import timedelta

    from sqlalchemy import select

    from app.models.auth import RefreshToken
    from app.utils.datetime_utils import get_utc_now

    response = await client.post(
        "/api/auth/login",
        json={
            "email": test_user.email,
            "password": "testpassword123",
            "rememberMe": True,
        },
    )

    assert response.status_code == 200
    refresh_token_value = response.json()["refresh_token"]

    # Fetch the refresh token from database
    result = await db_session.execute(
        select(RefreshToken).where(RefreshToken.user_id == test_user.id)
    )
    token_record = result.scalars().first()

    assert token_record is not None
    assert token_record.remember_me is True

    # Check expiration is approximately 30 days
    expected_expiry = get_utc_now() + timedelta(days=30)
    time_diff = abs((token_record.expires_at - expected_expiry).total_seconds())
    assert time_diff < 60, "Token expiration should be approximately 30 days"


@pytest.mark.asyncio
async def test_login_without_remember_me_creates_7_day_token(
    client: AsyncClient, test_user: User, db_session: AsyncSession
):
    """Test that rememberMe=False creates a refresh token with 7-day expiration."""
    from datetime import timedelta

    from sqlalchemy import select

    from app.models.auth import RefreshToken
    from app.utils.datetime_utils import get_utc_now

    response = await client.post(
        "/api/auth/login",
        json={
            "email": test_user.email,
            "password": "testpassword123",
            "rememberMe": False,
        },
    )

    assert response.status_code == 200

    # Fetch the refresh token from database
    result = await db_session.execute(
        select(RefreshToken).where(RefreshToken.user_id == test_user.id)
    )
    token_record = result.scalars().first()

    assert token_record is not None
    assert token_record.remember_me is False

    # Check expiration is approximately 7 days
    expected_expiry = get_utc_now() + timedelta(days=7)
    time_diff = abs((token_record.expires_at - expected_expiry).total_seconds())
    assert time_diff < 60, "Token expiration should be approximately 7 days"


@pytest.mark.asyncio
async def test_login_default_remember_me_creates_7_day_token(
    client: AsyncClient, test_user: User, db_session: AsyncSession
):
    """Test that omitting rememberMe defaults to False (7-day token)."""
    from datetime import timedelta

    from sqlalchemy import select

    from app.models.auth import RefreshToken
    from app.utils.datetime_utils import get_utc_now

    response = await client.post(
        "/api/auth/login",
        json={"email": test_user.email, "password": "testpassword123"},
        # rememberMe omitted - should default to False
    )

    assert response.status_code == 200

    # Fetch the refresh token from database
    result = await db_session.execute(
        select(RefreshToken).where(RefreshToken.user_id == test_user.id)
    )
    token_record = result.scalars().first()

    assert token_record is not None
    assert token_record.remember_me is False

    # Check expiration is approximately 7 days
    expected_expiry = get_utc_now() + timedelta(days=7)
    time_diff = abs((token_record.expires_at - expected_expiry).total_seconds())
    assert time_diff < 60, "Token expiration should default to 7 days"
