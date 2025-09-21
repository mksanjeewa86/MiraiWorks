"""Focused integration tests for message endpoints."""

import pytest
from typing import Optional

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.message import Message
from app.models.role import Role, UserRole
from app.models.user import User
from app.schemas.message import MessageCreate
from app.services.message_service import message_service
from app.utils.constants import UserRole as UserRoleEnum
from app.services.auth_service import auth_service


async def create_user_with_role(
    db_session: AsyncSession,
    *,
    roles: dict[str, Role],
    email: str,
    role: UserRoleEnum,
    company_id: Optional[int],
    password: str = "password123",
    first_name: str = "Test",
    last_name: str = "User",
) -> User:
    """Create an active user and attach the requested role."""
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


async def ensure_role(
    db_session: AsyncSession, roles: dict[str, Role], role: UserRoleEnum
) -> Role:
    """Guarantee the requested role exists in the provided mapping."""
    existing = roles.get(role.value)
    if existing:
        return existing

    role_obj = Role(name=role.value, description=f"Autocreated {role.value}")
    db_session.add(role_obj)
    await db_session.commit()
    await db_session.refresh(role_obj)
    roles[role.value] = role_obj
    return role_obj


@pytest.mark.asyncio
async def test_send_message_creates_record(
    client: AsyncClient,
    auth_headers: dict,
    db_session: AsyncSession,
    test_employer_user: User,
    test_roles: dict[str, Role],
):
    await ensure_role(db_session, test_roles, UserRoleEnum.RECRUITER)
    recipient = await create_user_with_role(
        db_session,
        roles=test_roles,
        email="recipient@test.com",
        role=UserRoleEnum.RECRUITER,
        company_id=test_employer_user.company_id,
    )

    payload = {"recipient_id": recipient.id, "content": "Hello there", "type": "text"}
    response = await client.post(
        "/api/messages/send", json=payload, headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["sender_id"] == test_employer_user.id
    assert data["recipient_id"] == recipient.id
    assert data["content"] == "Hello there"

    stored = await db_session.execute(
        select(Message).where(Message.id == data["id"])
    )
    message = stored.scalar_one()
    assert message.content == "Hello there"


@pytest.mark.asyncio
async def test_get_conversations_returns_latest(
    client: AsyncClient,
    auth_headers: dict,
    db_session: AsyncSession,
    test_employer_user: User,
    test_roles: dict[str, Role],
):
    await ensure_role(db_session, test_roles, UserRoleEnum.RECRUITER)
    partner = await create_user_with_role(
        db_session,
        roles=test_roles,
        email="dm-partner@test.com",
        role=UserRoleEnum.RECRUITER,
        company_id=test_employer_user.company_id,
    )

    for idx in range(2):
        await message_service.send_message(
            db_session,
            sender_id=test_employer_user.id,
            message_data=MessageCreate(
                recipient_id=partner.id,
                content=f"Ping {idx}",
                type="text",
            ),
        )

    response = await client.get(
        "/api/messages/conversations", headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    conversation = next(
        convo for convo in data["conversations"] if convo["other_user_id"] == partner.id
    )
    assert conversation["last_message"]["content"].startswith("Ping")


@pytest.mark.asyncio
async def test_get_messages_with_user_returns_thread(
    client: AsyncClient,
    auth_headers: dict,
    db_session: AsyncSession,
    test_employer_user: User,
    test_roles: dict[str, Role],
):
    await ensure_role(db_session, test_roles, UserRoleEnum.RECRUITER)
    partner = await create_user_with_role(
        db_session,
        roles=test_roles,
        email="thread-user@test.com",
        role=UserRoleEnum.RECRUITER,
        company_id=test_employer_user.company_id,
    )

    await message_service.send_message(
        db_session,
        sender_id=test_employer_user.id,
        message_data=MessageCreate(
            recipient_id=partner.id,
            content="Hello",
            type="text",
        ),
    )
    await message_service.send_message(
        db_session,
        sender_id=partner.id,
        message_data=MessageCreate(
            recipient_id=test_employer_user.id,
            content="Hi!",
            type="text",
        ),
    )

    response = await client.get(
        f"/api/messages/with/{partner.id}", headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    contents = {msg["content"] for msg in data["messages"]}
    assert contents == {"Hello", "Hi!"}


@pytest.mark.asyncio
async def test_mark_messages_as_read(
    client: AsyncClient,
    auth_headers: dict,
    db_session: AsyncSession,
    test_employer_user: User,
    test_roles: dict[str, Role],
):
    await ensure_role(db_session, test_roles, UserRoleEnum.RECRUITER)
    sender = await create_user_with_role(
        db_session,
        roles=test_roles,
        email="unread@test.com",
        role=UserRoleEnum.RECRUITER,
        company_id=test_employer_user.company_id,
    )

    message = await message_service.send_message(
        db_session,
        sender_id=sender.id,
        message_data=MessageCreate(
            recipient_id=test_employer_user.id,
            content="Unread",
            type="text",
        ),
    )

    response = await client.put(
        "/api/messages/mark-read",
        headers=auth_headers,
        json={"message_ids": [message.id]},
    )

    assert response.status_code == 200

    await db_session.refresh(message)
    assert message.is_read is True
    assert message.read_at is not None


@pytest.mark.asyncio
async def test_search_messages_finds_matches(
    client: AsyncClient,
    auth_headers: dict,
    db_session: AsyncSession,
    test_employer_user: User,
    test_roles: dict[str, Role],
):
    await ensure_role(db_session, test_roles, UserRoleEnum.RECRUITER)
    partner = await create_user_with_role(
        db_session,
        roles=test_roles,
        email="search-user@test.com",
        role=UserRoleEnum.RECRUITER,
        company_id=test_employer_user.company_id,
    )

    await message_service.send_message(
        db_session,
        sender_id=test_employer_user.id,
        message_data=MessageCreate(
            recipient_id=partner.id,
            content="Meeting notes summary",
            type="text",
        ),
    )

    response = await client.post(
        "/api/messages/search",
        headers=auth_headers,
        json={"query": "summary", "limit": 5, "offset": 0},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert any("summary" in msg["content"].lower() for msg in data["messages"])
