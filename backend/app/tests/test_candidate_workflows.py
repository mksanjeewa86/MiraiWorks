"""Focused integration tests for candidate-facing workflows."""

import pytest
from sqlalchemy import select

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.role import Role, UserRole
from app.models.user import User
from app.services.auth_service import auth_service
from app.utils.constants import UserRole as UserRoleEnum


async def ensure_role(
    db_session: AsyncSession, roles: dict[str, Role], role: UserRoleEnum
) -> Role:
    existing = roles.get(role.value)
    if existing:
        return existing

    role_obj = Role(name=role.value, description=f"Auto {role.value}")
    db_session.add(role_obj)
    await db_session.commit()
    await db_session.refresh(role_obj)
    roles[role.value] = role_obj
    return role_obj


@pytest.mark.asyncio
async def test_admin_can_list_candidates(
    client: AsyncClient,
    admin_auth_headers: dict,
    db_session: AsyncSession,
    test_roles: dict[str, Role],
    test_admin_user: User,
):
    await ensure_role(db_session, test_roles, UserRoleEnum.CANDIDATE)

    candidate = User(
        email="workflow.candidate@example.com",
        first_name="Workflow",
        last_name="Candidate",
        company_id=test_admin_user.company_id,
        hashed_password=auth_service.get_password_hash("candidatepass"),
        is_active=True,
    )
    db_session.add(candidate)
    await db_session.commit()
    await db_session.refresh(candidate)

    db_session.add(
        UserRole(
            user_id=candidate.id, role_id=test_roles[UserRoleEnum.CANDIDATE.value].id
        )
    )
    await db_session.commit()

    response = await client.get(
        "/api/admin/users",
        headers=admin_auth_headers,
        params={"role": "candidate", "size": 100},
    )

    assert response.status_code == 200
    users = response.json()["users"]
    assert any(user["email"] == candidate.email for user in users)


@pytest.mark.asyncio
async def test_candidate_can_view_published_jobs(
    client: AsyncClient,
    auth_headers: dict,
    candidate_headers: dict,
    test_employer_user: User,
):
    job_payload = {
        "title": "Backend Developer",
        "description": "Build APIs",
        "requirements": "Python",
        "location": "Remote",
        "job_type": "full_time",
        "company_id": test_employer_user.company_id,
    }

    create_response = await client.post(
        "/api/jobs", json=job_payload, headers=auth_headers
    )
    assert create_response.status_code == 201
    job = create_response.json()

    publish_response = await client.patch(
        f"/api/jobs/{job['id']}/status",
        json={"status": "published"},
        headers=auth_headers,
    )
    assert publish_response.status_code == 200

    list_response = await client.get("/api/jobs", headers=candidate_headers)
    assert list_response.status_code == 200
    jobs = list_response.json()["jobs"]
    assert any(item["id"] == job["id"] for item in jobs)


@pytest.mark.asyncio
async def test_candidate_updates_profile(
    client: AsyncClient,
    candidate_headers: dict,
    db_session: AsyncSession,
    test_candidate_only_user: User,
):
    payload = {
        "first_name": "Updated",
        "last_name": "Candidate",
        "phone": "+15550001111",
        "bio": "Ready for new challenges",
    }

    response = await client.put(
        "/api/user/profile", json=payload, headers=candidate_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "Updated"

    await db_session.refresh(test_candidate_only_user)
    assert test_candidate_only_user.first_name == "Updated"
