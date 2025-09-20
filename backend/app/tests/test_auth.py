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
