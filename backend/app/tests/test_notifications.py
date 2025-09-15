import pytest
from datetime import datetime, timedelta

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification
from app.models.user import User
from app.models.company import Company
from app.services.notification_service import notification_service


class TestNotifications:
    """Comprehensive tests for notifications endpoint functionality."""

    # ===== SUCCESS SCENARIOS =====

    @pytest.mark.asyncio
    async def test_get_notifications_success(self, client: AsyncClient, auth_headers: dict, test_user: User, db_session: AsyncSession):
        """Test successful retrieval of user notifications."""
        # Create test notifications
        notification1 = Notification(
            user_id=test_user.id,
            type="new_message",
            title="New Message",
            message="You have a new message",
            payload={"sender_id": 123},
            is_read=False
        )
        notification2 = Notification(
            user_id=test_user.id,
            type="interview_reminder",
            title="Interview Reminder",
            message="Interview in 1 hour",
            payload={"interview_id": 456},
            is_read=True,
            read_at=datetime.utcnow()
        )

        db_session.add(notification1)
        db_session.add(notification2)
        await db_session.commit()
        await db_session.refresh(notification1)
        await db_session.refresh(notification2)

        response = await client.get("/api/notifications/", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "notifications" in data
        assert len(data["notifications"]) == 2

        # Check notification structure
        notif = data["notifications"][0]  # Most recent first
        assert "id" in notif
        assert "type" in notif
        assert "title" in notif
        assert "message" in notif
        assert "payload" in notif
        assert "is_read" in notif
        assert "created_at" in notif
        assert "read_at" in notif

    @pytest.mark.asyncio
    async def test_get_notifications_with_limit(self, client: AsyncClient, auth_headers: dict, test_user: User, db_session: AsyncSession):
        """Test notifications retrieval with limit parameter."""
        # Create multiple notifications
        for i in range(5):
            notification = Notification(
                user_id=test_user.id,
                type="test",
                title=f"Test {i}",
                message=f"Test message {i}",
                is_read=False
            )
            db_session.add(notification)

        await db_session.commit()

        response = await client.get("/api/notifications/?limit=3", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data["notifications"]) == 3

    @pytest.mark.asyncio
    async def test_get_notifications_unread_only(self, client: AsyncClient, auth_headers: dict, test_user: User, db_session: AsyncSession):
        """Test notifications retrieval with unread_only filter."""
        # Create mixed read/unread notifications
        read_notification = Notification(
            user_id=test_user.id,
            type="test",
            title="Read Test",
            message="This is read",
            is_read=True,
            read_at=datetime.utcnow()
        )
        unread_notification = Notification(
            user_id=test_user.id,
            type="test",
            title="Unread Test",
            message="This is unread",
            is_read=False
        )

        db_session.add(read_notification)
        db_session.add(unread_notification)
        await db_session.commit()

        response = await client.get("/api/notifications/?unread_only=true", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data["notifications"]) == 1
        assert data["notifications"][0]["is_read"] is False

    @pytest.mark.asyncio
    async def test_get_unread_count_success(self, client: AsyncClient, auth_headers: dict, test_user: User, db_session: AsyncSession):
        """Test successful retrieval of unread notification count."""
        # Create mixed read/unread notifications
        for i in range(3):
            notification = Notification(
                user_id=test_user.id,
                type="test",
                title=f"Test {i}",
                message=f"Test message {i}",
                is_read=i % 2 == 0  # Alternate read/unread
            )
            db_session.add(notification)

        await db_session.commit()

        response = await client.get("/api/notifications/unread-count", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "unread_count" in data
        assert data["unread_count"] == 1  # Only one unread (index 1)

    @pytest.mark.asyncio
    async def test_mark_notifications_read_success(self, client: AsyncClient, auth_headers: dict, test_user: User, db_session: AsyncSession):
        """Test successfully marking specific notifications as read."""
        # Create unread notifications
        notifications = []
        for i in range(3):
            notification = Notification(
                user_id=test_user.id,
                type="test",
                title=f"Test {i}",
                message=f"Test message {i}",
                is_read=False
            )
            db_session.add(notification)
            notifications.append(notification)

        await db_session.commit()
        for notif in notifications:
            await db_session.refresh(notif)

        # Mark first two as read
        notification_ids = [notifications[0].id, notifications[1].id]

        response = await client.put(
            "/api/notifications/mark-read",
            json=notification_ids,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "2 notifications" in data["message"]

        # Verify notifications were marked as read
        await db_session.refresh(notifications[0])
        await db_session.refresh(notifications[1])
        await db_session.refresh(notifications[2])

        assert notifications[0].is_read is True
        assert notifications[1].is_read is True
        assert notifications[2].is_read is False

    @pytest.mark.asyncio
    async def test_mark_all_notifications_read_success(self, client: AsyncClient, auth_headers: dict, test_user: User, db_session: AsyncSession):
        """Test successfully marking all notifications as read."""
        # Create unread notifications
        notifications = []
        for i in range(3):
            notification = Notification(
                user_id=test_user.id,
                type="test",
                title=f"Test {i}",
                message=f"Test message {i}",
                is_read=False
            )
            db_session.add(notification)
            notifications.append(notification)

        await db_session.commit()

        response = await client.put("/api/notifications/mark-all-read", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "3 notifications" in data["message"]

        # Verify all notifications were marked as read
        for notif in notifications:
            await db_session.refresh(notif)
            assert notif.is_read is True

    @pytest.mark.asyncio
    async def test_mark_all_notifications_read_none_unread(self, client: AsyncClient, auth_headers: dict, test_user: User, db_session: AsyncSession):
        """Test marking all notifications as read when none are unread."""
        # Create already read notification
        notification = Notification(
            user_id=test_user.id,
            type="test",
            title="Test",
            message="Test message",
            is_read=True,
            read_at=datetime.utcnow()
        )
        db_session.add(notification)
        await db_session.commit()

        response = await client.put("/api/notifications/mark-all-read", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "No unread notifications"

    # ===== AUTHENTICATION & AUTHORIZATION TESTS =====

    @pytest.mark.asyncio
    async def test_get_notifications_unauthorized(self, client: AsyncClient):
        """Test notifications access without authentication."""
        response = await client.get("/api/notifications/")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_unread_count_unauthorized(self, client: AsyncClient):
        """Test unread count access without authentication."""
        response = await client.get("/api/notifications/unread-count")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_mark_notifications_read_unauthorized(self, client: AsyncClient):
        """Test marking notifications read without authentication."""
        response = await client.put("/api/notifications/mark-read", json=[1, 2, 3])
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_mark_all_notifications_read_unauthorized(self, client: AsyncClient):
        """Test marking all notifications read without authentication."""
        response = await client.put("/api/notifications/mark-all-read")
        assert response.status_code == 401

    # ===== INPUT VALIDATION TESTS =====

    @pytest.mark.asyncio
    async def test_get_notifications_invalid_limit(self, client: AsyncClient, auth_headers: dict):
        """Test notifications retrieval with invalid limit parameter."""
        # Test limit too high
        response = await client.get("/api/notifications/?limit=150", headers=auth_headers)
        assert response.status_code == 422

        # Test limit too low
        response = await client.get("/api/notifications/?limit=0", headers=auth_headers)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_mark_notifications_read_invalid_data(self, client: AsyncClient, auth_headers: dict):
        """Test marking notifications read with invalid data."""
        # Test with non-list data
        response = await client.put(
            "/api/notifications/mark-read",
            json="invalid",
            headers=auth_headers
        )
        assert response.status_code == 422

        # Test with empty list
        response = await client.put(
            "/api/notifications/mark-read",
            json=[],
            headers=auth_headers
        )
        assert response.status_code == 200  # Should succeed but mark 0

    @pytest.mark.asyncio
    async def test_mark_notifications_read_nonexistent_ids(self, client: AsyncClient, auth_headers: dict):
        """Test marking non-existent notification IDs as read."""
        response = await client.put(
            "/api/notifications/mark-read",
            json=[99999, 99998],
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "0 notifications" in data["message"]

    # ===== BUSINESS LOGIC TESTS =====

    @pytest.mark.asyncio
    async def test_notifications_user_isolation(self, client: AsyncClient, auth_headers: dict, test_user: User, test_company: "Company", db_session: AsyncSession):
        """Test that users can only see their own notifications."""
        # Create another user
        from app.services.auth_service import auth_service

        other_user = User(
            email="other@test.com",
            first_name="Other",
            last_name="User",
            company_id=test_company.id,
            hashed_password=auth_service.get_password_hash("password123"),
            is_active=True
        )
        db_session.add(other_user)
        await db_session.commit()
        await db_session.refresh(other_user)

        # Create notifications for both users
        user_notification = Notification(
            user_id=test_user.id,
            type="test",
            title="User Notification",
            message="For test user",
            is_read=False
        )
        other_notification = Notification(
            user_id=other_user.id,
            type="test",
            title="Other Notification",
            message="For other user",
            is_read=False
        )

        db_session.add(user_notification)
        db_session.add(other_notification)
        await db_session.commit()

        # Test user can only see their own notification
        response = await client.get("/api/notifications/", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data["notifications"]) == 1
        assert data["notifications"][0]["title"] == "User Notification"

    @pytest.mark.asyncio
    async def test_notifications_ordering(self, client: AsyncClient, auth_headers: dict, test_user: User, db_session: AsyncSession):
        """Test that notifications are ordered by creation date (newest first)."""
        # Create notifications with slight time differences
        now = datetime.utcnow()

        old_notification = Notification(
            user_id=test_user.id,
            type="test",
            title="Old Notification",
            message="Created first",
            is_read=False
        )
        old_notification.created_at = now - timedelta(hours=1)

        new_notification = Notification(
            user_id=test_user.id,
            type="test",
            title="New Notification",
            message="Created second",
            is_read=False
        )
        new_notification.created_at = now

        db_session.add(old_notification)
        db_session.add(new_notification)
        await db_session.commit()

        response = await client.get("/api/notifications/", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data["notifications"]) == 2
        # Newest should be first
        assert data["notifications"][0]["title"] == "New Notification"
        assert data["notifications"][1]["title"] == "Old Notification"

    @pytest.mark.asyncio
    async def test_mark_notifications_read_only_owned(self, client: AsyncClient, auth_headers: dict, test_user: User, test_company: "Company", db_session: AsyncSession):
        """Test that users can only mark their own notifications as read."""
        # Create another user
        from app.services.auth_service import auth_service

        other_user = User(
            email="other2@test.com",
            first_name="Other2",
            last_name="User",
            company_id=test_company.id,
            hashed_password=auth_service.get_password_hash("password123"),
            is_active=True
        )
        db_session.add(other_user)
        await db_session.commit()
        await db_session.refresh(other_user)

        # Create notification for other user
        other_notification = Notification(
            user_id=other_user.id,
            type="test",
            title="Other's Notification",
            message="Should not be marked as read",
            is_read=False
        )
        db_session.add(other_notification)
        await db_session.commit()
        await db_session.refresh(other_notification)

        # Try to mark other user's notification as read
        response = await client.put(
            "/api/notifications/mark-read",
            json=[other_notification.id],
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "0 notifications" in data["message"]  # Should mark 0 since it's not owned

        # Verify notification remains unread
        await db_session.refresh(other_notification)
        assert other_notification.is_read is False

    # ===== EDGE CASES =====

    @pytest.mark.asyncio
    async def test_get_notifications_empty_result(self, client: AsyncClient, auth_headers: dict):
        """Test notifications retrieval when user has no notifications."""
        response = await client.get("/api/notifications/", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["notifications"] == []

    @pytest.mark.asyncio
    async def test_get_unread_count_zero(self, client: AsyncClient, auth_headers: dict):
        """Test unread count when user has no unread notifications."""
        response = await client.get("/api/notifications/unread-count", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["unread_count"] == 0

    @pytest.mark.asyncio
    async def test_notifications_with_null_payload(self, client: AsyncClient, auth_headers: dict, test_user: User, db_session: AsyncSession):
        """Test notifications with null payload field."""
        notification = Notification(
            user_id=test_user.id,
            type="test",
            title="No Payload",
            message="Notification without payload",
            payload=None,
            is_read=False
        )
        db_session.add(notification)
        await db_session.commit()

        response = await client.get("/api/notifications/", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data["notifications"]) == 1
        assert data["notifications"][0]["payload"] is None

    @pytest.mark.asyncio
    async def test_mark_read_with_duplicate_ids(self, client: AsyncClient, auth_headers: dict, test_user: User, db_session: AsyncSession):
        """Test marking notifications as read with duplicate IDs."""
        notification = Notification(
            user_id=test_user.id,
            type="test",
            title="Test",
            message="Test message",
            is_read=False
        )
        db_session.add(notification)
        await db_session.commit()
        await db_session.refresh(notification)

        # Send duplicate IDs
        response = await client.put(
            "/api/notifications/mark-read",
            json=[notification.id, notification.id, notification.id],
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "1 notifications" in data["message"]  # Should only count once

    @pytest.mark.asyncio
    async def test_notification_read_timestamp(self, client: AsyncClient, auth_headers: dict, test_user: User, db_session: AsyncSession):
        """Test that read_at timestamp is set when marking notifications as read."""
        notification = Notification(
            user_id=test_user.id,
            type="test",
            title="Test",
            message="Test message",
            is_read=False
        )
        db_session.add(notification)
        await db_session.commit()
        await db_session.refresh(notification)

        # Mark as read
        response = await client.put(
            "/api/notifications/mark-read",
            json=[notification.id],
            headers=auth_headers
        )

        assert response.status_code == 200

        # Verify read_at is set
        await db_session.refresh(notification)
        assert notification.is_read is True
        assert notification.read_at is not None

    @pytest.mark.asyncio
    async def test_service_integration(self, test_user: User, db_session: AsyncSession):
        """Test direct integration with notification service."""
        # Test creating notification through service
        notification = await notification_service.create_notification(
            db_session,
            test_user.id,
            "test_type",
            "Test Title",
            "Test Message",
            {"test": "data"}
        )

        assert notification.id is not None
        assert notification.user_id == test_user.id
        assert notification.type == "test_type"
        assert notification.title == "Test Title"
        assert notification.message == "Test Message"
        assert notification.payload == {"test": "data"}
        assert notification.is_read is False

        # Test getting notifications through service
        notifications = await notification_service.get_user_notifications(
            db_session, test_user.id
        )
        assert len(notifications) == 1
        assert notifications[0].id == notification.id

        # Test unread count through service
        count = await notification_service.get_unread_count(db_session, test_user.id)
        assert count == 1

        # Test marking as read through service
        marked_count = await notification_service.mark_notifications_as_read(
            db_session, test_user.id, [notification.id]
        )
        assert marked_count == 1

        # Verify read status
        count = await notification_service.get_unread_count(db_session, test_user.id)
        assert count == 0