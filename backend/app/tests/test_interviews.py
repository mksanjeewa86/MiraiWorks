"""Realistic integration tests for interview endpoints."""

from datetime import timedelta
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.interview import interview as interview_crud
from app.models.interview import Interview
from app.models.role import Role, UserRole
from app.models.user import User
from app.services.auth_service import auth_service
from app.services.interview_service import interview_service
from app.utils.constants import InterviewStatus
from app.utils.constants import UserRole as UserRoleEnum
from app.utils.datetime_utils import get_utc_now


async def create_user_with_role(
    db_session: AsyncSession,
    *,
    email: str,
    role: Role,
    company_id: int | None,
    password: str = "password123",
    first_name: str = "Test",
    last_name: str = "User",
) -> User:
    """Create a user and attach a role for test scenarios."""
    user = User(
        email=email,
        first_name=first_name,
        last_name=last_name,
        company_id=company_id,
        hashed_password=auth_service.get_password_hash(password),
        is_active=True,
        require_2fa=False,
    )
    db_session.add(user)
    await db_session.flush()

    db_session.add(UserRole(user_id=user.id, role_id=role.id))
    await db_session.commit()
    await db_session.refresh(user)
    return user


async def create_sample_interview(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_headers: dict,
    roles_map: dict[str, Role],
    employer_user: User,
    candidate_user: User,
    *,
    title: str = "Senior Engineer Interview",
) -> tuple[dict, User, dict]:
    """Create a fully populated interview via the API for reuse in tests."""
    recruiter = await create_user_with_role(
        db_session,
        email=f"recruiter+{uuid4().hex[:8]}@example.com",
        role=roles_map[UserRoleEnum.MEMBER.value],
        company_id=employer_user.company_id,
        first_name="Recruiter",
        last_name="User",
    )

    start = get_utc_now() + timedelta(days=2)
    payload = {
        "candidate_id": candidate_user.id,
        "recruiter_id": recruiter.id,
        "employer_company_id": employer_user.company_id,
        "title": title,
        "description": "Screening interview",
        "interview_type": "video",
        "scheduled_start": start.isoformat(),
        "scheduled_end": (start + timedelta(hours=1)).isoformat(),
        "timezone": "UTC",
    }

    response = await client.post("/api/interviews/", json=payload, headers=auth_headers)
    assert response.status_code == 201
    return response.json(), recruiter, payload


async def create_interview_model(
    db_session: AsyncSession,
    roles_map: dict[str, Role],
    employer_user: User,
    candidate_user: User,
    *,
    title: str = "Service Interview",
) -> tuple[Interview, User]:
    """Create an interview directly via the service layer for DB-centric tests."""
    recruiter = await create_user_with_role(
        db_session,
        email=f"svc-recruiter+{uuid4().hex[:8]}@example.com",
        role=roles_map[UserRoleEnum.MEMBER.value],
        company_id=employer_user.company_id,
        first_name="Recruiter",
        last_name="Service",
    )

    # Ensure the candidate user's session state is fresh
    await db_session.refresh(candidate_user)

    start = get_utc_now() + timedelta(days=3)
    assert employer_user.company_id is not None
    interview = await interview_service.create_interview(
        db=db_session,
        candidate_id=candidate_user.id,
        recruiter_id=recruiter.id,
        employer_company_id=employer_user.company_id,
        title=title,
        description="Service-created interview",
        position_title=title,
        interview_type="video",
        created_by=employer_user.id,
        scheduled_start=start,
        scheduled_end=start + timedelta(hours=1),
        timezone="UTC",
    )

    full_interview = await interview_crud.get_with_relationships(
        db_session, interview.id
    )
    assert full_interview is not None
    return full_interview, recruiter


@pytest.mark.asyncio
async def test_create_interview_success(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_headers: dict,
    test_roles: dict[str, Role],
    test_employer_user: User,
    test_candidate_only_user: User,
):
    interview, recruiter, payload = await create_sample_interview(
        client,
        db_session,
        auth_headers,
        test_roles,
        test_employer_user,
        test_candidate_only_user,
    )

    assert interview["title"] == payload["title"]
    assert interview["candidate"]["id"] == test_candidate_only_user.id
    assert interview["member"]["id"] == recruiter.id
    assert interview["status"] == InterviewStatus.PENDING_SCHEDULE.value


@pytest.mark.asyncio
async def test_create_interview_rejects_non_candidate(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_headers: dict,
    test_roles: dict[str, Role],
    test_employer_user: User,
):
    recruiter = await create_user_with_role(
        db_session,
        email="recruiter@example.com",
        role=test_roles[UserRoleEnum.MEMBER.value],
        company_id=test_employer_user.company_id,
    )

    non_candidate = await create_user_with_role(
        db_session,
        email="notcandidate@example.com",
        role=test_roles[UserRoleEnum.MEMBER.value],
        company_id=test_employer_user.company_id,
    )

    start = get_utc_now() + timedelta(days=1)
    payload = {
        "candidate_id": non_candidate.id,
        "recruiter_id": recruiter.id,
        "employer_company_id": test_employer_user.company_id,
        "title": "Invalid Candidate Interview",
        "interview_type": "video",
        "scheduled_start": start.isoformat(),
        "scheduled_end": (start + timedelta(hours=1)).isoformat(),
        "timezone": "UTC",
    }

    response = await client.post("/api/interviews/", json=payload, headers=auth_headers)
    assert response.status_code == 400
    assert "not a candidate" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_get_interviews_returns_created_interview(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_headers: dict,
    test_roles: dict[str, Role],
    test_employer_user: User,
    test_candidate_only_user: User,
):
    interview, recruiter, _ = await create_sample_interview(
        client,
        db_session,
        auth_headers,
        test_roles,
        test_employer_user,
        test_candidate_only_user,
    )

    params = {
        "recruiter_id": recruiter.id,
        "employer_company_id": test_employer_user.company_id,
    }
    response = await client.get("/api/interviews/", params=params, headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["interviews"][0]["id"] == interview["id"]


@pytest.mark.asyncio
async def test_update_interview_title(
    db_session: AsyncSession,
    test_roles: dict[str, Role],
    test_employer_user: User,
    test_candidate_only_user: User,
):
    interview, _ = await create_interview_model(
        db_session,
        test_roles,
        test_employer_user,
        test_candidate_only_user,
        title="Initial Title",
    )

    interview.title = "Updated Interview Title"
    await db_session.commit()

    updated = await interview_crud.get_with_relationships(db_session, interview.id)
    assert updated is not None
    assert updated.title == "Updated Interview Title"


@pytest.mark.asyncio
async def test_proposal_lifecycle(
    db_session: AsyncSession,
    test_roles: dict[str, Role],
    test_employer_user: User,
    test_candidate_only_user: User,
):
    interview, _ = await create_interview_model(
        db_session,
        test_roles,
        test_employer_user,
        test_candidate_only_user,
    )

    start = get_utc_now() + timedelta(days=5)
    proposal = await interview_service.create_proposal(
        db=db_session,
        interview_id=interview.id,
        proposed_by=test_employer_user.id,
        start_datetime=start,
        end_datetime=start + timedelta(hours=1),
        timezone="UTC",
    )
    assert proposal.status == "pending"

    response = await interview_service.respond_to_proposal(
        db=db_session,
        proposal_id=proposal.id,
        response="accepted",
        responded_by=test_candidate_only_user.id,
    )
    assert response is not None
    assert response.status == "accepted"

    refreshed = await interview_crud.get_with_relationships(db_session, interview.id)
    assert refreshed is not None
    assert refreshed.status == InterviewStatus.CONFIRMED.value


@pytest.mark.asyncio
async def test_interview_stats_reflect_confirmed_interview(
    db_session: AsyncSession,
    test_roles: dict[str, Role],
    test_employer_user: User,
    test_candidate_only_user: User,
):
    interview, _ = await create_interview_model(
        db_session,
        test_roles,
        test_employer_user,
        test_candidate_only_user,
    )

    start = get_utc_now() + timedelta(days=6)
    proposal = await interview_service.create_proposal(
        db=db_session,
        interview_id=interview.id,
        proposed_by=test_employer_user.id,
        start_datetime=start,
        end_datetime=start + timedelta(hours=1),
        timezone="UTC",
    )
    await interview_service.respond_to_proposal(
        db=db_session,
        proposal_id=proposal.id,
        response="accepted",
        responded_by=test_candidate_only_user.id,
    )

    stats = await interview_crud.get_interview_stats(db_session, test_employer_user.id)
    assert stats.get("total", 0) >= 1


@pytest.mark.asyncio
async def test_cancel_interview_updates_status(
    db_session: AsyncSession,
    test_roles: dict[str, Role],
    test_employer_user: User,
    test_candidate_only_user: User,
):
    interview, _ = await create_interview_model(
        db_session,
        test_roles,
        test_employer_user,
        test_candidate_only_user,
    )

    cancelled = await interview_service.cancel_interview(
        db=db_session,
        interview_id=interview.id,
        cancelled_by=test_employer_user.id,
        reason="Schedule conflict",
    )

    assert cancelled.status == InterviewStatus.CANCELLED.value
    assert cancelled.cancellation_reason == "Schedule conflict"
