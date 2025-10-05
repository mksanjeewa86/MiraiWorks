import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.message import Message
from app.models.notification import Notification
from app.models.user import User

# Import moved to avoid circular import
# from app.endpoints.messaging_ws import connection_manager, is_user_online
# WebSocket functionality removed - using HTTP polling instead
from app.services.email_service import email_service

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self):
        self._email_debounce = {}  # Track last email sent per conversation to prevent spam

    async def create_notification(
        self,
        db: AsyncSession,
        user_id: int,
        notification_type: str,
        title: str,
        message: str,
        payload: dict | None = None,
    ) -> Notification:
        """Create a new in-app notification."""
        notification = Notification(
            user_id=user_id,
            type=notification_type,
            title=title,
            message=message,
            payload=payload,
        )

        db.add(notification)
        await db.commit()
        await db.refresh(notification)

        # Note: Real-time notifications now handled via HTTP polling
        # WebSocket functionality was removed from the messaging system
        logger.debug(f"Created notification {notification.id} for user {user_id}")

        return notification

    async def handle_new_message_notifications(
        self,
        db: AsyncSession,
        sender_id: int,
        recipient_id: int,
        message: Message,
    ) -> None:
        """Handle all notifications for a new message."""
        # Get sender and recipient with settings
        result = await db.execute(
            select(User)
            .options(selectinload(User.settings))
            .where(User.id.in_([sender_id, recipient_id]))
        )
        users = result.scalars().all()

        sender = next((u for u in users if u.id == sender_id), None)
        recipient = next((u for u in users if u.id == recipient_id), None)

        if not sender or not recipient:
            logger.error(
                f"Could not find sender {sender_id} or recipient {recipient_id}"
            )
            return

        # WebSocket functionality removed - assume user may need email notification
        recipient_online = False  # Always assume offline for email notifications

        # Always create in-app notification for message history
        await self.create_notification(
            db,
            recipient_id,
            "new_message",
            f"New message from {sender.full_name}",
            message.content[:100] + "..."
            if len(message.content) > 100
            else message.content,
            {
                "sender_id": sender_id,
                "sender_name": sender.full_name,
                "message_id": message.id,
                "conversation_url": f"/messages?user={sender_id}",
            },
        )

        # Check if recipient wants email notifications
        recipient_settings = recipient.settings
        if not recipient_settings or not recipient_settings.message_notifications:
            logger.info(f"Email notifications disabled for user {recipient_id}")
            return

        # Check debounce to prevent email spam (max 1 email per conversation per 5 minutes)
        conversation_key = (
            f"{min(sender_id, recipient_id)}_{max(sender_id, recipient_id)}"
        )
        now = datetime.now(timezone.utc)

        if conversation_key in self._email_debounce:
            last_email_time = self._email_debounce[conversation_key]
            if now - last_email_time < timedelta(minutes=5):
                logger.info(
                    f"Email notification debounced for conversation {conversation_key}"
                )
                return

        # Send email notification only if recipient is not currently online or not in the conversation
        if not recipient_online:
            success = await email_service.send_message_notification(
                recipient.email,
                recipient.full_name,
                sender.full_name,
                message.content,
                f"{email_service.app_base_url}/messages?user={sender_id}",
            )

            if success:
                self._email_debounce[conversation_key] = now
                logger.info(f"Email notification sent to {recipient.email}")
            else:
                logger.error(f"Failed to send email notification to {recipient.email}")

    async def get_user_notifications(
        self, db: AsyncSession, user_id: int, limit: int = 50, unread_only: bool = False
    ) -> list[Notification]:
        """Get notifications for a user."""
        query = (
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc(), Notification.id.desc())
            .limit(limit)
        )

        if unread_only:
            query = query.where(Notification.is_read is False)

        result = await db.execute(query)
        return result.scalars().all()

    async def mark_notifications_as_read(
        self, db: AsyncSession, user_id: int, notification_ids: list[int]
    ) -> int:
        """Mark specific notifications as read."""
        from sqlalchemy import update

        stmt = (
            update(Notification)
            .where(
                and_(
                    Notification.user_id == user_id,
                    Notification.id.in_(notification_ids),
                )
            )
            .values(is_read=True, read_at=datetime.now(timezone.utc))
        )

        result = await db.execute(stmt)
        await db.commit()
        return result.rowcount

    async def get_unread_count(self, db: AsyncSession, user_id: int) -> int:
        """Get count of unread notifications for a user."""
        from sqlalchemy import func

        result = await db.execute(
            select(func.count(Notification.id)).where(
                and_(Notification.user_id == user_id, Notification.is_read is False)
            )
        )
        return result.scalar() or 0


# Global instance
notification_service = NotificationService()
