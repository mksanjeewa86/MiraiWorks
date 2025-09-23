"""Integration tests covering recruitment scenarios around jobs and interviews."""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.role import Role, UserRole
from app.models.user import User
from app.services.interview_service import interview_service
from app.utils.constants import UserRole as UserRoleEnum


async def create_position(
    client: AsyncClient,
    headers: dict,
    *,
    title: str,
    company_id: int,
) -> dict:
    payload = {
        "title": title,
        "description": "Test description",
        "requirements": "Testing",
        "location": "Remote",
        "job_type": "full_time",
        "company_id": company_id,
    }
    response = await client.post("/api/positions", json=payload, headers=headers)
    assert response.status_code == 201
    return response.json()


@pytest.mark.asyncio
async def test_employer_creates_and_lists_job(
    client: AsyncClient,
    auth_headers: dict,
    test_employer_user: User,
):
    created_position = await create_position(
        client,
        auth_headers,
        title="QA Engineer",
        company_id=test_employer_user.company_id,
    )

    publish_response = await client.patch(
        f"/api/positions/{created_position['id']}/status",
        json={"status": "published"},
        headers=auth_headers,
    )
    assert publish_response.status_code == 200

    list_response = await client.get(
        "/api/positions",
        headers=auth_headers,
        params={"company_id": test_employer_user.company_id, "status": "published"},
    )
    assert list_response.status_code == 200
    positions = list_response.json()["positions"]
    assert any(position["id"] == created_position["id"] for position in positions)


@pytest.mark.asyncio
async def test_admin_updates_job_status(
    client: AsyncClient,
    auth_headers: dict,
    admin_auth_headers: dict,
    test_employer_user: User,
):
    position = await create_position(
        client,
        auth_headers,
        title="Data Analyst",
        company_id=test_employer_user.company_id,
    )

    response = await client.patch(
        f"/api/positions/{position['id']}/status",
        json={"status": "closed"},
        headers=admin_auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["status"] == "closed"


@pytest.mark.asyncio
async def test_interview_created_for_job_candidate(
    client: AsyncClient,
    auth_headers: dict,
    db_session: AsyncSession,
    test_employer_user: User,
    test_candidate_only_user: User,
    test_roles: dict[str, Role],
):
    start = datetime.utcnow() + timedelta(days=2)

    # Ensure employer can act as recruiter in service validation
    result = await db_session.execute(
        select(UserRole).where(
            UserRole.user_id == test_employer_user.id,
            UserRole.role_id == test_roles[UserRoleEnum.RECRUITER.value].id,
        )
    )
    if result.scalar_one_or_none() is None:
        db_session.add(
            UserRole(
                user_id=test_employer_user.id,
                role_id=test_roles[UserRoleEnum.RECRUITER.value].id,
            )
        )
        await db_session.commit()
    interview = await interview_service.create_interview(
        db=db_session,
        candidate_id=test_candidate_only_user.id,
        recruiter_id=test_employer_user.id,
        employer_company_id=test_employer_user.company_id,
        title=f"Screening {uuid4().hex[:6]}",
        interview_type="video",
        created_by=test_employer_user.id,
        scheduled_start=start,
        scheduled_end=start + timedelta(hours=1),
        timezone="UTC",
    )

    response = await client.get(
        "/api/interviews",
        headers=auth_headers,
        params={
            "status": "pending_schedule",
            "recruiter_id": test_employer_user.id,
            "employer_company_id": test_employer_user.company_id,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert any(item["id"] == interview.id for item in data["interviews"])
