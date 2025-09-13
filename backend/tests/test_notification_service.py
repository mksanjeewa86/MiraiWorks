"""Tests for NotificationService."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.endpoints.messaging_ws import connection_manager
from app.models.direct_message import DirectMessage
from app.models.notification import Notification
from app.models.user import User
from app.services.notification_service import notification_service


class TestNotificationService:
    """Test suite for NotificationService."""

    @pytest.mark.asyncio
    async def test_create_notification_success(
        self, db_session: AsyncSession, test_user: User
    ):
        """Test successful notification creation."""
        result = await notification_service.create_notification(
            db_session,
            user_id=test_user.id,
            notification_type="new_message",
            title="New Message",
            message="You have received a new message",
            payload={"sender_id": 2, "message_id": 1},
        )

        assert result is not None
        assert result.user_id == test_user.id
        assert result.type == "new_message"
        assert result.title == "New Message"
        assert result.message == "You have received a new message"
        assert result.payload == {"sender_id": 2, "message_id": 1}
        assert result.is_read is False

        # Verify notification was saved to database
        stmt = select(Notification).where(Notification.id == result.id)
        db_result = await db_session.execute(stmt)
        db_notification = db_result.scalar_one_or_none()

        assert db_notification is not None
        assert db_notification.title == "New Message"

    @pytest.mark.asyncio
    @patch("app.endpoints.messaging_ws.is_user_online")
    @patch.object(connection_manager, "send_to_user")
    async def test_create_notification_sends_realtime_when_online(
        self,
        mock_send_to_user: AsyncMock,
        mock_is_user_online: MagicMock,
        db_session: AsyncSession,
        test_user: User,
    ):
        """Test that real-time notification is sent when user is online."""
        # Mock user as online
        mock_is_user_online.return_value = True
        mock_send_to_user.return_value = None

        result = await notification_service.create_notification(
            db_session,
            user_id=test_user.id,
            notification_type="new_message",
            title="New Message",
            message="You have received a new message",
        )

        # Verify WebSocket message was sent
        mock_send_to_user.assert_called_once()
        call_args = mock_send_to_user.call_args
        assert call_args[0][0] == test_user.id  # User ID

        # Verify message content
        ws_message = call_args[0][1]
        assert ws_message.type == "notification"
        assert ws_message.data["id"] == result.id
        assert ws_message.data["title"] == "New Message"

    @pytest.mark.asyncio
    @patch("app.endpoints.messaging_ws.is_user_online")
    @patch.object(connection_manager, "send_to_user")
    async def test_create_notification_no_realtime_when_offline(
        self,
        mock_send_to_user: AsyncMock,
        mock_is_user_online: MagicMock,
        db_session: AsyncSession,
        test_user: User,
    ):
        """Test that no real-time notification is sent when user is offline."""
        # Mock user as offline
        mock_is_user_online.return_value = False

        await notification_service.create_notification(
            db_session,
            user_id=test_user.id,
            notification_type="new_message",
            title="New Message",
            message="You have received a new message",
        )

        # Verify no WebSocket message was sent
        mock_send_to_user.assert_not_called()

    @pytest.mark.asyncio
    @patch("app.endpoints.messaging_ws.is_user_online")
    @patch("app.services.email_service.email_service.send_message_notification")
    async def test_handle_new_message_notifications_email_enabled(
        self,
        mock_send_email: AsyncMock,
        mock_is_user_online: MagicMock,
        db_session: AsyncSession,
        test_user: User,
        test_user2: User,
    ):
        """Test email notification when user has email notifications enabled."""
        # Mock user as offline to trigger email
        mock_is_user_online.return_value = False
        mock_send_email.return_value = True

        # Create a message
        message = DirectMessage(
            sender_id=test_user.id,
            recipient_id=test_user2.id,
            content="Test email notification message",
            type="text",
        )
        db_session.add(message)
        await db_session.commit()
        await db_session.refresh(message)

        await notification_service.handle_new_message_notifications(
            db_session, test_user.id, test_user2.id, message
        )

        # Verify email was sent
        mock_send_email.assert_called_once()
        call_args = mock_send_email.call_args[0]  # Get positional arguments
        assert call_args[0] == test_user2.email
        assert call_args[1] == "Test2 User2"  # test_user2.full_name
        assert call_args[2] == "Test User"  # test_user.full_name
        assert call_args[3] == "Test email notification message"

    @pytest.mark.asyncio
    @patch("app.endpoints.messaging_ws.is_user_online")
    @patch("app.services.email_service.email_service.send_message_notification")
    async def test_handle_new_message_notifications_email_disabled(
        self,
        mock_send_email: AsyncMock,
        mock_is_user_online: MagicMock,
        db_session: AsyncSession,
        test_user: User,
        test_admin_user: User,  # Admin has email notifications disabled
    ):
        """Test no email notification when user has email notifications disabled."""
        # Mock user as offline
        mock_is_user_online.return_value = False

        # Create a message to admin user (who has email notifications disabled)
        message = DirectMessage(
            sender_id=test_user.id,
            recipient_id=test_admin_user.id,
            content="Test message to admin",
            type="text",
        )
        db_session.add(message)
        await db_session.commit()
        await db_session.refresh(message)

        await notification_service.handle_new_message_notifications(
            db_session, test_user.id, test_admin_user.id, message
        )

        # Verify no email was sent
        mock_send_email.assert_not_called()

    @pytest.mark.asyncio
    @patch("app.endpoints.messaging_ws.is_user_online")
    @patch("app.services.email_service.email_service.send_message_notification")
    async def test_email_debouncing(
        self,
        mock_send_email: AsyncMock,
        mock_is_user_online: MagicMock,
        db_session: AsyncSession,
        test_user: User,
        test_user2: User,
    ):
        """Test email notification debouncing."""
        # Mock user as offline
        mock_is_user_online.return_value = False
        mock_send_email.return_value = True

        # Create first message
        message1 = DirectMessage(
            sender_id=test_user.id,
            recipient_id=test_user2.id,
            content="First message",
            type="text",
        )
        db_session.add(message1)
        await db_session.commit()
        await db_session.refresh(message1)

        # Send first message - should trigger email
        await notification_service.handle_new_message_notifications(
            db_session, test_user.id, test_user2.id, message1
        )

        assert mock_send_email.call_count == 1

        # Create second message immediately after
        message2 = DirectMessage(
            sender_id=test_user.id,
            recipient_id=test_user2.id,
            content="Second message",
            type="text",
        )
        db_session.add(message2)
        await db_session.commit()
        await db_session.refresh(message2)

        # Send second message - should NOT trigger email due to debouncing
        await notification_service.handle_new_message_notifications(
            db_session, test_user.id, test_user2.id, message2
        )

        # Should still be only 1 email sent
        assert mock_send_email.call_count == 1

    @pytest.mark.asyncio
    async def test_get_user_notifications(
        self, db_session: AsyncSession, test_user: User, test_notification: Notification
    ):
        """Test retrieving user notifications."""
        # Create additional notifications
        for i in range(3):
            notification = Notification(
                user_id=test_user.id,
                type="test_notification",
                title=f"Test Notification {i+1}",
                message=f"Test message {i+1}",
                is_read=i == 0,  # First one is read
            )
            db_session.add(notification)

        await db_session.commit()

        # Get all notifications
        all_notifications = await notification_service.get_user_notifications(
            db_session, test_user.id, limit=50
        )

        assert len(all_notifications) == 4  # 3 new + 1 from fixture

        # Get only unread notifications
        unread_notifications = await notification_service.get_user_notifications(
            db_session, test_user.id, limit=50, unread_only=True
        )

        assert len(unread_notifications) == 3  # Should exclude the read one

    @pytest.mark.asyncio
    async def test_get_user_notifications_with_limit(
        self, db_session: AsyncSession, test_user: User
    ):
        """Test notification retrieval with limit."""
        # Create 10 notifications with individual flushes to ensure proper timestamps
        for i in range(10):
            notification = Notification(
                user_id=test_user.id,
                type="test_notification",
                title=f"Test Notification {i+1}",
                message=f"Test message {i+1}",
                is_read=False,
            )
            db_session.add(notification)
            await db_session.flush()  # Flush each one to get proper timestamp

        await db_session.commit()

        # Get with limit of 5
        limited_notifications = await notification_service.get_user_notifications(
            db_session, test_user.id, limit=5
        )

        assert len(limited_notifications) == 5

        # Should be ordered by created_at descending (newest first)
        assert limited_notifications[0].title == "Test Notification 10"

    @pytest.mark.asyncio
    async def test_mark_notifications_as_read(
        self, db_session: AsyncSession, test_user: User
    ):
        """Test marking notifications as read."""
        # Create unread notifications
        notification_ids = []
        for i in range(3):
            notification = Notification(
                user_id=test_user.id,
                type="test_notification",
                title=f"Test Notification {i+1}",
                message=f"Test message {i+1}",
                is_read=False,
            )
            db_session.add(notification)
            await db_session.flush()
            notification_ids.append(notification.id)

        await db_session.commit()

        # Mark first 2 as read
        count = await notification_service.mark_notifications_as_read(
            db_session, test_user.id, notification_ids[:2]
        )

        assert count == 2

        # Verify they are marked as read
        stmt = select(Notification).where(Notification.id.in_(notification_ids[:2]))
        result = await db_session.execute(stmt)
        read_notifications = result.scalars().all()

        for notification in read_notifications:
            assert notification.is_read is True
            assert notification.read_at is not None

        # Verify third one is still unread
        stmt = select(Notification).where(Notification.id == notification_ids[2])
        result = await db_session.execute(stmt)
        unread_notification = result.scalar_one()

        assert unread_notification.is_read is False
        assert unread_notification.read_at is None

    @pytest.mark.asyncio
    async def test_mark_notifications_as_read_only_own(
        self, db_session: AsyncSession, test_user: User, test_user2: User
    ):
        """Test that users can only mark their own notifications as read."""
        # Create notification for test_user2
        notification = Notification(
            user_id=test_user2.id,
            type="test_notification",
            title="Test Notification",
            message="Test message",
            is_read=False,
        )
        db_session.add(notification)
        await db_session.commit()

        # Try to mark it as read by test_user (should fail)
        count = await notification_service.mark_notifications_as_read(
            db_session, test_user.id, [notification.id]
        )

        assert count == 0  # No notifications marked as read

        # Verify notification is still unread
        await db_session.refresh(notification)
        assert notification.is_read is False

    @pytest.mark.asyncio
    async def test_get_unread_count(
        self,
        db_session: AsyncSession,
        test_user: User,
        test_notification: Notification,  # This is unread by default
    ):
        """Test getting unread notification count."""
        # Create additional notifications
        for i in range(4):
            notification = Notification(
                user_id=test_user.id,
                type="test_notification",
                title=f"Test Notification {i+1}",
                message=f"Test message {i+1}",
                is_read=i < 2,  # First 2 are read, last 2 are unread
            )
            db_session.add(notification)

        await db_session.commit()

        unread_count = await notification_service.get_unread_count(
            db_session, test_user.id
        )

        # Should be 3 unread (2 from loop + 1 from fixture)
        assert unread_count == 3

    @pytest.mark.asyncio
    async def test_get_unread_count_no_notifications(
        self,
        db_session: AsyncSession,
        test_user2: User,  # User without notifications
    ):
        """Test unread count when user has no notifications."""
        unread_count = await notification_service.get_unread_count(
            db_session, test_user2.id
        )

        assert unread_count == 0

    @pytest.mark.asyncio
    async def test_handle_new_message_notifications_creates_in_app_notification(
        self, db_session: AsyncSession, test_user: User, test_user2: User
    ):
        """Test that in-app notification is always created for new messages."""
        # Create a message
        message = DirectMessage(
            sender_id=test_user.id,
            recipient_id=test_user2.id,
            content="Test in-app notification message",
            type="text",
        )
        db_session.add(message)
        await db_session.commit()
        await db_session.refresh(message)

        initial_count = await notification_service.get_unread_count(
            db_session, test_user2.id
        )

        await notification_service.handle_new_message_notifications(
            db_session, test_user.id, test_user2.id, message
        )

        # Check that a notification was created
        final_count = await notification_service.get_unread_count(
            db_session, test_user2.id
        )

        assert final_count == initial_count + 1

        # Get the created notification
        notifications = await notification_service.get_user_notifications(
            db_session, test_user2.id, limit=1, unread_only=True
        )

        assert len(notifications) >= 1
        latest_notification = notifications[0]
        assert latest_notification.type == "new_message"
        assert latest_notification.title == f"New message from {test_user.full_name}"
        assert "Test in-app notification message" in latest_notification.message

    @pytest.mark.asyncio
    async def test_long_message_content_truncation(
        self, db_session: AsyncSession, test_user: User, test_user2: User
    ):
        """Test that long message content is truncated in notifications."""
        # Create a very long message
        long_content = "A" * 200  # 200 characters

        message = DirectMessage(
            sender_id=test_user.id,
            recipient_id=test_user2.id,
            content=long_content,
            type="text",
        )
        db_session.add(message)
        await db_session.commit()
        await db_session.refresh(message)

        await notification_service.handle_new_message_notifications(
            db_session, test_user.id, test_user2.id, message
        )

        # Get the created notification
        notifications = await notification_service.get_user_notifications(
            db_session, test_user2.id, limit=1, unread_only=True
        )

        assert len(notifications) >= 1
        notification = notifications[0]

        # Message should be truncated to 100 chars + "..."
        assert len(notification.message) <= 103  # 100 + "..."
        assert notification.message.endswith("...")

    @pytest.mark.asyncio
    async def test_notification_payload_structure(
        self, db_session: AsyncSession, test_user: User, test_user2: User
    ):
        """Test notification payload contains correct message metadata."""
        message = DirectMessage(
            sender_id=test_user.id,
            recipient_id=test_user2.id,
            content="Test payload message",
            type="text",
        )
        db_session.add(message)
        await db_session.commit()
        await db_session.refresh(message)

        await notification_service.handle_new_message_notifications(
            db_session, test_user.id, test_user2.id, message
        )

        # Get the created notification
        notifications = await notification_service.get_user_notifications(
            db_session, test_user2.id, limit=1, unread_only=True
        )

        assert len(notifications) >= 1
        notification = notifications[0]

        # Check payload structure
        assert notification.payload is not None
        assert "sender_id" in notification.payload
        assert "sender_name" in notification.payload
        assert "message_id" in notification.payload
        assert "conversation_url" in notification.payload

        assert notification.payload["sender_id"] == test_user.id
        assert notification.payload["sender_name"] == test_user.full_name
        assert notification.payload["message_id"] == message.id
        assert f"user={test_user.id}" in notification.payload["conversation_url"]
