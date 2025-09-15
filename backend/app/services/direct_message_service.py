from datetime import datetime
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import and_, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.direct_message import DirectMessage
from app.models.user import User
from app.schemas.direct_message import (
    ConversationSummary,
    DirectMessageCreate,
    DirectMessageInfo,
    MessageSearchRequest,
)
from app.utils.logging import get_logger

logger = get_logger(__name__)


class DirectMessageService:
    def __init__(self):
        pass

    async def send_message(
        self, db: AsyncSession, sender_id: int, message_data: DirectMessageCreate
    ) -> DirectMessage:
        """Send a direct message to another user."""
        # Direct messaging - no restrictions by default

        # Verify recipient exists and is active
        recipient = await db.execute(
            select(User).where(
                User.id == message_data.recipient_id, User.is_active == True
            )
        )
        if not recipient.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Recipient not found"
            )

        # Create message
        message = DirectMessage(
            sender_id=sender_id,
            recipient_id=message_data.recipient_id,
            content=message_data.content,
            type=message_data.type,
            reply_to_id=message_data.reply_to_id,
            file_url=message_data.file_url,
            file_name=message_data.file_name,
            file_size=message_data.file_size,
            file_type=message_data.file_type,
        )

        db.add(message)
        await db.commit()
        await db.refresh(message)

        logger.info(
            "Direct message sent",
            sender_id=sender_id,
            recipient_id=message_data.recipient_id,
            message_id=message.id,
            component="direct_message",
        )

        return message

    async def get_messages_with_user(
        self,
        db: AsyncSession,
        current_user_id: int,
        other_user_id: int,
        limit: int = 50,
        before_id: Optional[int] = None,
    ) -> list[DirectMessage]:
        """Get messages between current user and another user."""

        query = (
            select(DirectMessage)
            .options(
                selectinload(DirectMessage.sender),
                selectinload(DirectMessage.recipient),
                selectinload(DirectMessage.reply_to).selectinload(DirectMessage.sender),
            )
            .where(
                or_(
                    and_(
                        DirectMessage.sender_id == current_user_id,
                        DirectMessage.recipient_id == other_user_id,
                        DirectMessage.is_deleted_by_sender == False,
                    ),
                    and_(
                        DirectMessage.sender_id == other_user_id,
                        DirectMessage.recipient_id == current_user_id,
                        DirectMessage.is_deleted_by_recipient == False,
                    ),
                )
            )
            .order_by(desc(DirectMessage.created_at))
        )

        if before_id:
            query = query.where(DirectMessage.id < before_id)

        query = query.limit(limit)
        result = await db.execute(query)
        messages = result.scalars().all()

        return list(messages)  # Return in descending order (newest first)

    async def get_conversations(
        self, db: AsyncSession, user_id: int, search_query: Optional[str] = None
    ) -> list[ConversationSummary]:
        """Get list of users the current user has exchanged messages with."""
        # SQLite-compatible approach: use CASE statements instead of greatest/least
        from sqlalchemy import case

        # Subquery to get the latest message between user and each other user
        latest_message_subquery = (
            select(
                case(
                    (DirectMessage.sender_id > DirectMessage.recipient_id, DirectMessage.sender_id),
                    else_=DirectMessage.recipient_id
                ).label("user1"),
                case(
                    (DirectMessage.sender_id < DirectMessage.recipient_id, DirectMessage.sender_id),
                    else_=DirectMessage.recipient_id
                ).label("user2"),
                func.max(DirectMessage.created_at).label("last_activity"),
            )
            .where(
                or_(
                    DirectMessage.sender_id == user_id,
                    DirectMessage.recipient_id == user_id,
                )
            )
            .group_by("user1", "user2")
            .subquery()
        )

        # Get conversation partners
        conversations = []
        result = await db.execute(
            select(
                latest_message_subquery.c.user1,
                latest_message_subquery.c.user2,
                latest_message_subquery.c.last_activity,
            ).order_by(desc(latest_message_subquery.c.last_activity))
        )

        for row in result.fetchall():
            other_user_id = row.user1 if row.user2 == user_id else row.user2

            # Get other user info
            other_user_result = await db.execute(
                select(User)
                .options(selectinload(User.company))
                .where(User.id == other_user_id)
            )
            other_user = other_user_result.scalar_one_or_none()
            if not other_user:
                continue

            # Apply search filter
            if search_query:
                search_lower = search_query.lower()
                if not (
                    search_lower in other_user.full_name.lower()
                    or search_lower in other_user.email.lower()
                ):
                    continue

            # Get latest message
            latest_msg_result = await db.execute(
                select(DirectMessage)
                .options(
                    selectinload(DirectMessage.sender),
                    selectinload(DirectMessage.recipient),
                )
                .where(
                    or_(
                        and_(
                            DirectMessage.sender_id == user_id,
                            DirectMessage.recipient_id == other_user_id,
                            DirectMessage.is_deleted_by_sender == False,
                        ),
                        and_(
                            DirectMessage.sender_id == other_user_id,
                            DirectMessage.recipient_id == user_id,
                            DirectMessage.is_deleted_by_recipient == False,
                        ),
                    )
                )
                .order_by(desc(DirectMessage.created_at))
                .limit(1)
            )
            latest_message = latest_msg_result.scalar_one_or_none()

            # Count unread messages from other user
            unread_result = await db.execute(
                select(func.count(DirectMessage.id)).where(
                    DirectMessage.sender_id == other_user_id,
                    DirectMessage.recipient_id == user_id,
                    DirectMessage.is_read == False,
                    DirectMessage.is_deleted_by_recipient == False,
                )
            )
            unread_count = unread_result.scalar()

            # Convert to response format
            last_message_info = None
            if latest_message:
                last_message_info = DirectMessageInfo(
                    id=latest_message.id,
                    sender_id=latest_message.sender_id,
                    recipient_id=latest_message.recipient_id,
                    sender_name=latest_message.sender.full_name,
                    recipient_name=latest_message.recipient.full_name,
                    sender_email=latest_message.sender.email,
                    recipient_email=latest_message.recipient.email,
                    content=latest_message.content,
                    type=latest_message.type,
                    is_read=latest_message.is_read,
                    reply_to_id=latest_message.reply_to_id,
                    file_url=latest_message.file_url,
                    file_name=latest_message.file_name,
                    file_size=latest_message.file_size,
                    file_type=latest_message.file_type,
                    created_at=latest_message.created_at,
                    read_at=latest_message.read_at,
                )

            conversation = ConversationSummary(
                other_user_id=other_user.id,
                other_user_name=other_user.full_name,
                other_user_email=other_user.email,
                other_user_company=other_user.company.name
                if other_user.company
                else None,
                last_message=last_message_info,
                unread_count=unread_count,
                last_activity=row.last_activity,
            )
            conversations.append(conversation)

        return conversations

    async def search_messages(
        self, db: AsyncSession, user_id: int, search_request: MessageSearchRequest
    ) -> list[DirectMessage]:
        """Search messages by content and sender name."""
        query = (
            select(DirectMessage)
            .options(
                selectinload(DirectMessage.sender),
                selectinload(DirectMessage.recipient),
            )
            .where(
                or_(
                    and_(
                        DirectMessage.sender_id == user_id,
                        DirectMessage.is_deleted_by_sender == False,
                    ),
                    and_(
                        DirectMessage.recipient_id == user_id,
                        DirectMessage.is_deleted_by_recipient == False,
                    ),
                )
            )
        )

        # Apply search filters
        if search_request.query:
            search_term = f"%{search_request.query}%"
            query = query.join(DirectMessage.sender).where(
                or_(
                    DirectMessage.content.ilike(search_term),
                    User.first_name.ilike(search_term),
                    User.last_name.ilike(search_term),
                    User.email.ilike(search_term),
                )
            )

        if search_request.with_user_id:
            query = query.where(
                or_(
                    DirectMessage.sender_id == search_request.with_user_id,
                    DirectMessage.recipient_id == search_request.with_user_id,
                )
            )

        query = (
            query.order_by(desc(DirectMessage.created_at))
            .offset(search_request.offset)
            .limit(search_request.limit)
        )

        result = await db.execute(query)
        return result.scalars().all()

    async def mark_messages_as_read(
        self, db: AsyncSession, user_id: int, message_ids: list[int]
    ) -> int:
        """Mark multiple messages as read."""
        # Only mark messages where user is the recipient
        result = await db.execute(
            select(DirectMessage).where(
                DirectMessage.id.in_(message_ids),
                DirectMessage.recipient_id == user_id,
                DirectMessage.is_read == False,
            )
        )
        messages = result.scalars().all()

        count = 0
        for message in messages:
            message.is_read = True
            message.read_at = datetime.utcnow()
            count += 1

        if count > 0:
            await db.commit()
            logger.info(
                f"Marked {count} messages as read",
                user_id=user_id,
                component="direct_message",
            )

        return count

    async def mark_conversation_as_read(
        self, db: AsyncSession, user_id: int, other_user_id: int
    ) -> int:
        """Mark all unread messages from another user as read."""
        result = await db.execute(
            select(DirectMessage).where(
                DirectMessage.sender_id == other_user_id,
                DirectMessage.recipient_id == user_id,
                DirectMessage.is_read == False,
                DirectMessage.is_deleted_by_recipient == False,
            )
        )
        messages = result.scalars().all()

        count = 0
        for message in messages:
            message.is_read = True
            message.read_at = datetime.utcnow()
            count += 1

        if count > 0:
            await db.commit()
            logger.info(
                f"Marked conversation as read - {count} messages",
                user_id=user_id,
                other_user_id=other_user_id,
                component="direct_message",
            )

        return count


# Create singleton instance
direct_message_service = DirectMessageService()
