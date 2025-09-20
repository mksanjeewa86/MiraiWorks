import pytest
from httpx import AsyncClient

from app.models.user import User


@pytest.mark.asyncio
async def test_fixtures_work(client: AsyncClient, test_user: User):
    """Test if the new fixture setup works."""
    # Test that fixtures are properly created
    assert client is not None
    assert test_user is not None
    assert test_user.email == "test@example.com"

    # Test basic API call
    response = await client.get("/api/auth/me")
    # Should fail with 401 since no auth headers
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_auth_headers_work(
    client: AsyncClient,
    auth_headers: dict,
    test_employer_user: User,
):
    """Test if auth headers fixture works."""
    assert auth_headers is not None
    assert "Authorization" in auth_headers

    # Test authenticated API call
    response = await client.get("/api/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_employer_user.email