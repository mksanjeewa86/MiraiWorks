"""Targeted integration tests covering advanced interview endpoints."""

from datetime import datetime, timedelta
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


async def create_user_with_role(
    db_session: AsyncSession,
    *,
    roles: dict[str, Role],
    email: str,
    role: UserRoleEnum,
    company_id: int | None,
    password: str = "password123",
    first_name: str = "Test",
    last_name: str = "User",
) -> User:
    """Create an active user and attach a specific role."""
    user = User(
        email=email,
        first_name=first_name,
        last_name=last_name,
        company_id=company_id,
        hashed_password=auth_service.get_password_hash(password),
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    db_session.add(UserRole(user_id=user.id, role_id=roles[role.value].id))
    await db_session.commit()
    return user


async def create_interview_record(
    db_session: AsyncSession,
    roles: dict[str, Role],
    employer_user: User,
    candidate_user: User,
    *,
    title: str = "Senior Engineer Interview",
) -> tuple[Interview, User]:
    """Create an interview through the service layer for reuse in tests."""
    recruiter = await create_user_with_role(
        db_session,
        roles=roles,
        email=f"recruiter+{uuid4().hex}@example.com",
        role=UserRoleEnum.RECRUITER,
        company_id=employer_user.company_id,
        first_name="Recruiter",
        last_name="User",
    )

    start = datetime.utcnow() + timedelta(days=2)
    interview = await interview_service.create_interview(
        db=db_session,
        candidate_id=candidate_user.id,
        recruiter_id=recruiter.id,
        employer_company_id=employer_user.company_id,
        title=title,
        description="Screening interview",
        position_title=title,
        interview_type="video",
        created_by=employer_user.id,
        scheduled_start=start,
        scheduled_end=start + timedelta(hours=1),
        timezone="UTC",
    )

    full = await interview_crud.get_with_relationships(db_session, interview.id)
    return full, recruiter


async def confirm_interview(
    db_session: AsyncSession,
    interview: Interview,
    employer_user: User,
    candidate_user: User,
) -> Interview:
    """Confirm an interview by creating and accepting a proposal."""
    start = datetime.utcnow() + timedelta(days=3)
    proposal = await interview_service.create_proposal(
        db=db_session,
        interview_id=interview.id,
        proposed_by=employer_user.id,
        start_datetime=start,
        end_datetime=start + timedelta(hours=1),
        timezone="UTC",
    )

    await interview_service.respond_to_proposal(
        db=db_session,
        proposal_id=proposal.id,
        response="accepted",
        responded_by=candidate_user.id,
    )

    return await interview_crud.get_with_relationships(db_session, interview.id)


@pytest.mark.asyncio
async def test_calendar_events_include_confirmed_interview(
    client: AsyncClient,
    auth_headers: dict,
    db_session: AsyncSession,
    test_employer_user: User,
    test_candidate_only_user: User,
    test_roles: dict[str, Role],
):
    interview, _ = await create_interview_record(
        db_session, test_roles, test_employer_user, test_candidate_only_user
    )
    interview = await confirm_interview(
        db_session, interview, test_employer_user, test_candidate_only_user
    )

    response = await client.get("/api/interviews/calendar/events", headers=auth_headers)

    assert response.status_code == 200
    events = response.json()
    assert any(event["interview_id"] == interview.id for event in events)


@pytest.mark.asyncio
async def test_interview_list_filters_by_status(
    client: AsyncClient,
    auth_headers: dict,
    db_session: AsyncSession,
    test_employer_user: User,
    test_candidate_only_user: User,
    test_roles: dict[str, Role],
):
    pending_interview, _ = await create_interview_record(
        db_session,
        test_roles,
        test_employer_user,
        test_candidate_only_user,
        title="Pending Interview",
    )
    confirmed_interview, _ = await create_interview_record(
        db_session,
        test_roles,
        test_employer_user,
        test_candidate_only_user,
        title="Confirmed Interview",
    )
    await confirm_interview(
        db_session,
        confirmed_interview,
        test_employer_user,
        test_candidate_only_user,
    )

    response = await client.get(
        "/api/interviews/",
        headers=auth_headers,
        params={
            "status": InterviewStatus.CONFIRMED.value,
            "recruiter_id": confirmed_interview.recruiter_id,
            "employer_company_id": test_employer_user.company_id,
        },
    )

    assert response.status_code == 200
    data = response.json()
    ids = [record["id"] for record in data["interviews"]]
    assert confirmed_interview.id in ids
    assert pending_interview.id not in ids


@pytest.mark.asyncio
async def test_calendar_events_respects_date_filters(
    client: AsyncClient,
    auth_headers: dict,
    db_session: AsyncSession,
    test_employer_user: User,
    test_candidate_only_user: User,
    test_roles: dict[str, Role],
):
    interview, _ = await create_interview_record(
        db_session, test_roles, test_employer_user, test_candidate_only_user
    )
    await confirm_interview(
        db_session, interview, test_employer_user, test_candidate_only_user
    )

    future_window = datetime.utcnow() + timedelta(days=30)
    response = await client.get(
        "/api/interviews/calendar/events",
        headers=auth_headers,
        params={"start_date": future_window.isoformat()},
    )

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_stats_summary_reports_confirmed_interview(
    client: AsyncClient,
    auth_headers: dict,
    db_session: AsyncSession,
    test_employer_user: User,
    test_candidate_only_user: User,
    test_roles: dict[str, Role],
):
    interview, _ = await create_interview_record(
        db_session, test_roles, test_employer_user, test_candidate_only_user
    )
    await confirm_interview(
        db_session, interview, test_employer_user, test_candidate_only_user
    )

    response = await client.get("/api/interviews/stats/summary", headers=auth_headers)

    assert response.status_code == 200
    stats = response.json()
    assert stats["total_interviews"] >= 1
    assert stats["by_status"].get(InterviewStatus.CONFIRMED.value, 0) >= 1
