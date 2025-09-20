"""Integration tests for notification endpoints."""

import pytest

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification
from app.models.notification import Notification
from app.services.notification_service import notification_service
from app.models.user import User

async def create_notification(
    db_session: AsyncSession,
    *,
    user_id: int,
    notification_type: str = "test",
    title: str = "Test Title",
    message: str = "Test message",
    payload: dict | None = None,
) -> Notification:
    """Create a notification via the service to mirror production usage."""
    notification = await notification_service.create_notification(
        db_session,
        user_id,
        notification_type,
        title,
        message,
        payload,
    )
    return notification


@pytest.mark.asyncio
async def test_list_notifications_returns_created_items(
    client: AsyncClient,
    auth_headers: dict,
    db_session: AsyncSession,
    test_employer_user: User,
):
    first = await create_notification(
        db_session,
        user_id=test_employer_user.id,
        title="First",
        message="First message",
    )
    second = await create_notification(
        db_session,
        user_id=test_employer_user.id,
        title="Second",
        message="Second message",
    )

    response = await client.get("/api/notifications/", headers=auth_headers)

    assert response.status_code == 200
    payload = response.json()
    ids = [item["id"] for item in payload["notifications"]]
    assert second.id in ids and first.id in ids


@pytest.mark.asyncio
async def test_list_notifications_honours_limit(
    client: AsyncClient,
    auth_headers: dict,
    db_session: AsyncSession,
    test_employer_user: User,
):
    for index in range(3):
        await create_notification(
            db_session,
            user_id=test_employer_user.id,
            title=f"Notification {index}",
            message=f"Body {index}",
        )

    response = await client.get(
        "/api/notifications/",
        headers=auth_headers,
        params={"limit": 2},
    )

    assert response.status_code == 200
    assert len(response.json()["notifications"]) == 2


@pytest.mark.asyncio
async def test_unread_only_filter_returns_unread_notifications(
    client: AsyncClient,
    auth_headers: dict,
    db_session: AsyncSession,
    test_employer_user: User,
):
    unread = await create_notification(
        db_session,
        user_id=test_employer_user.id,
        title="Unread",
        message="Unread message",
    )
    read = await create_notification(
        db_session,
        user_id=test_employer_user.id,
        title="Read",
        message="Read message",
    )
    read.is_read = True
    await db_session.commit()

    response = await client.get(
        "/api/notifications/",
        headers=auth_headers,
        params={"unread_only": True},
    )

    assert response.status_code == 200
    ids = [item["id"] for item in response.json()["notifications"]]
    assert unread.id in ids
    assert read.id not in ids


@pytest.mark.asyncio
async def test_unread_count_endpoint(
    client: AsyncClient,
    auth_headers: dict,
    db_session: AsyncSession,
    test_employer_user: User,
):
    await create_notification(db_session, user_id=test_employer_user.id)
    second = await create_notification(db_session, user_id=test_employer_user.id)
    second.is_read = True
    await db_session.commit()

    response = await client.get(
        "/api/notifications/unread-count", headers=auth_headers
    )

    assert response.status_code == 200
    assert response.json()["unread_count"] == 1


@pytest.mark.asyncio
async def test_mark_notifications_read_endpoint(
    client: AsyncClient,
    auth_headers: dict,
    db_session: AsyncSession,
    test_employer_user: User,
):
    notification = await create_notification(db_session, user_id=test_employer_user.id)

    response = await client.put(
        "/api/notifications/mark-read",
        headers=auth_headers,
        json=[notification.id],
    )

    assert response.status_code == 200
    await db_session.refresh(notification)
    assert notification.is_read is True
    assert notification.read_at is not None


@pytest.mark.asyncio
async def test_mark_all_notifications_read_endpoint(
    client: AsyncClient,
    auth_headers: dict,
    db_session: AsyncSession,
    test_employer_user: User,
):
    first = await create_notification(db_session, user_id=test_employer_user.id)
    second = await create_notification(db_session, user_id=test_employer_user.id)

    response = await client.put(
        "/api/notifications/mark-all-read", headers=auth_headers
    )

    assert response.status_code == 200
    await db_session.refresh(first)
    await db_session.refresh(second)
    assert first.is_read and second.is_read
