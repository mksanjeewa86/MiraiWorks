"""Targeted recruitment workflow integration tests."""

from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.position import Position
from app.models.user import User


async def create_position(
    client: AsyncClient,
    headers: dict,
    *,
    title: str,
    company_id: int,
) -> dict:
    payload = {
        "title": title,
        "description": "Position description",
        "requirements": "Requirements",
        "location": "Remote",
        "job_type": "full_time",
        "company_id": company_id,
    }
    response = await client.post("/api/positions", json=payload, headers=headers)
    assert response.status_code == 201
    return response.json()


@pytest.mark.asyncio
async def test_job_statistics_endpoint(
    client: AsyncClient,
    auth_headers: dict,
    admin_auth_headers: dict,
    test_employer_user: User,
):
    position = await create_position(
        client,
        auth_headers,
        title=f"Platform Engineer {uuid4().hex[:4]}",
        company_id=test_employer_user.company_id,
    )

    await client.patch(
        f"/api/positions/{position['id']}/status",
        json={"status": "published"},
        headers=auth_headers,
    )

    stats_response = await client.get(
        "/api/positions/statistics", headers=admin_auth_headers
    )
    assert stats_response.status_code == 200
    data = stats_response.json()
    assert data["total_positions"] >= 1


@pytest.mark.asyncio
async def test_job_search_returns_matching_titles(
    client: AsyncClient,
    auth_headers: dict,
    test_employer_user: User,
):
    position = await create_position(
        client,
        auth_headers,
        title="Data Scientist",
        company_id=test_employer_user.company_id,
    )

    await client.patch(
        f"/api/positions/{position['id']}/status",
        json={"status": "published"},
        headers=auth_headers,
    )

    search_response = await client.get(
        "/api/positions",
        params={"search": "Data"},
    )
    assert search_response.status_code == 200
    positions = search_response.json()["positions"]
    assert any(
        "Data Scientist" in position_info["title"] for position_info in positions
    )


@pytest.mark.asyncio
async def test_employer_updates_job_details(
    client: AsyncClient,
    auth_headers: dict,
    db_session: AsyncSession,
    test_employer_user: User,
):
    position = await create_position(
        client,
        auth_headers,
        title="QA Specialist",
        company_id=test_employer_user.company_id,
    )

    update_payload = {"summary": "Quality assurance specialist", "status": "published"}
    response = await client.put(
        f"/api/positions/{position['id']}",
        json=update_payload,
        headers=auth_headers,
    )

    assert response.status_code == 200
    result = await db_session.execute(
        select(Position).where(Position.id == position["id"])
    )
    stored = result.scalar_one()
    assert stored.summary == "Quality assurance specialist"
