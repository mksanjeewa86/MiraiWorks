"""Integration tests for user settings and profile endpoints."""

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.user_settings import UserSettings


@pytest.mark.asyncio
async def test_get_settings_returns_defaults(
    client: AsyncClient,
    auth_headers: dict,
    test_employer_user: User,
):
    response = await client.get("/api/user/settings", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["job_title"] is None
    assert data["email_notifications"] is True
    assert data["require_2fa"] is False


@pytest.mark.asyncio
async def test_update_settings_persists_changes(
    client: AsyncClient,
    auth_headers: dict,
    db_session: AsyncSession,
    test_employer_user: User,
):
    payload = {
        "job_title": "Engineering Manager",
        "bio": "Leads the platform team",
        "email_notifications": False,
        "push_notifications": True,
        "require_2fa": True,
    }

    response = await client.put(
        "/api/user/settings", json=payload, headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["job_title"] == "Engineering Manager"
    assert data["email_notifications"] is False
    assert data["push_notifications"] is True
    assert data["require_2fa"] is True

    # Check persistence in database
    result = await db_session.execute(
        select(UserSettings).where(UserSettings.user_id == test_employer_user.id)
    )
    stored = result.scalar_one()
    assert stored.job_title == "Engineering Manager"


@pytest.mark.asyncio
async def test_sms_notifications_require_phone(
    client: AsyncClient,
    auth_headers: dict,
    test_employer_user: User,
):
    payload = {"sms_notifications": True}

    response = await client.put(
        "/api/user/settings", json=payload, headers=auth_headers
    )

    assert response.status_code == 400
    assert "phone number" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_profile_update_updates_user_and_settings(
    client: AsyncClient,
    auth_headers: dict,
    db_session: AsyncSession,
    test_employer_user: User,
):
    payload = {
        "first_name": "Alex",
        "last_name": "Johnson",
        "phone": "+1234567890",
        "job_title": "Principal Engineer",
        "bio": "Works on critical systems",
    }

    response = await client.put("/api/user/profile", json=payload, headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "Alex"
    assert data["job_title"] == "Principal Engineer"

    await db_session.refresh(test_employer_user)
    assert test_employer_user.first_name == "Alex"

    result = await db_session.execute(
        select(UserSettings).where(UserSettings.user_id == test_employer_user.id)
    )
    stored = result.scalar_one()
    assert stored.bio == "Works on critical systems"
