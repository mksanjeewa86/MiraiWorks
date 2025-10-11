from fastapi import HTTPException, status
from sqlalchemy import and_, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.message import Message
from app.models.user import User
from app.schemas.message import (
    ConversationSummary,
    MessageCreate,
    MessageInfo,
    MessageSearchRequest,
)
from app.services.company_connection_service import company_connection_service
from app.utils.datetime_utils import get_utc_now
from app.utils.logging import get_logger

logger = get_logger(__name__)


class MessageService:
    def __init__(self):
        pass

    async def send_message(
        self, db: AsyncSession, sender_id: int, message_data: MessageCreate
    ) -> Message:
        """Send a direct message to another user."""
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

        # Validate company connection - users can only message if connected
        can_interact = await company_connection_service.can_users_interact(
            db, sender_id, message_data.recipient_id
        )

        if not can_interact:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot message this user. No company connection exists between you.",
            )

        # Create message
        message = Message(
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
            component="message",
        )

        return message

    async def get_messages_with_user(
        self,
        db: AsyncSession,
        current_user_id: int,
        other_user_id: int,
        limit: int = 50,
        before_id: int | None = None,
    ) -> list[Message]:
        """Get messages between current user and another user."""

        query = (
            select(Message)
            .options(
                selectinload(Message.sender),
                selectinload(Message.recipient),
                selectinload(Message.reply_to).selectinload(Message.sender),
            )
            .where(
                or_(
                    and_(
                        Message.sender_id == current_user_id,
                        Message.recipient_id == other_user_id,
                        Message.is_deleted_by_sender == False,
                    ),
                    and_(
                        Message.sender_id == other_user_id,
                        Message.recipient_id == current_user_id,
                        Message.is_deleted_by_recipient == False,
                    ),
                )
            )
            .order_by(Message.created_at)
        )

        if before_id:
            # For ascending order, we want messages with id > before_id for "load more older messages"
            # But since we changed to ascending, let's keep the same pagination behavior
            query = query.where(Message.id < before_id)

        query = query.limit(limit)
        result = await db.execute(query)
        messages = result.scalars().all()

        return list(
            messages
        )  # Return in ascending order (oldest first, newest at bottom)

    async def get_conversations(
        self, db: AsyncSession, user_id: int, search_query: str | None = None
    ) -> list[ConversationSummary]:
        """Get list of users the current user has exchanged messages with."""
        # SQLite-compatible approach: use CASE statements instead of greatest/least
        from sqlalchemy import case

        # Subquery to get the latest message between user and each other user
        latest_message_subquery = (
            select(
                case(
                    (
                        Message.sender_id > Message.recipient_id,
                        Message.sender_id,
                    ),
                    else_=Message.recipient_id,
                ).label("user1"),
                case(
                    (
                        Message.sender_id < Message.recipient_id,
                        Message.sender_id,
                    ),
                    else_=Message.recipient_id,
                ).label("user2"),
                func.max(Message.created_at).label("last_activity"),
            )
            .where(
                or_(
                    Message.sender_id == user_id,
                    Message.recipient_id == user_id,
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
                select(Message)
                .options(
                    selectinload(Message.sender),
                    selectinload(Message.recipient),
                )
                .where(
                    or_(
                        and_(
                            Message.sender_id == user_id,
                            Message.recipient_id == other_user_id,
                            Message.is_deleted_by_sender == False,
                        ),
                        and_(
                            Message.sender_id == other_user_id,
                            Message.recipient_id == user_id,
                            Message.is_deleted_by_recipient == False,
                        ),
                    )
                )
                .order_by(desc(Message.created_at))
                .limit(1)
            )
            latest_message = latest_msg_result.scalar_one_or_none()

            # Count unread messages from other user
            unread_result = await db.execute(
                select(func.count(Message.id)).where(
                    Message.sender_id == other_user_id,
                    Message.recipient_id == user_id,
                    Message.is_read == False,
                    Message.is_deleted_by_recipient == False,
                )
            )
            unread_count = unread_result.scalar()

            # Convert to response format
            last_message_info = None
            if latest_message:
                last_message_info = MessageInfo(
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
    ) -> list[Message]:
        """Search messages by content and sender name."""
        query = (
            select(Message)
            .options(
                selectinload(Message.sender),
                selectinload(Message.recipient),
            )
            .where(
                or_(
                    and_(
                        Message.sender_id == user_id,
                        Message.is_deleted_by_sender == False,
                    ),
                    and_(
                        Message.recipient_id == user_id,
                        Message.is_deleted_by_recipient == False,
                    ),
                )
            )
        )

        # Apply search filters
        if search_request.query:
            search_term = f"%{search_request.query}%"
            query = query.join(Message.sender).where(
                or_(
                    Message.content.ilike(search_term),
                    User.first_name.ilike(search_term),
                    User.last_name.ilike(search_term),
                    User.email.ilike(search_term),
                )
            )

        if search_request.with_user_id:
            query = query.where(
                or_(
                    Message.sender_id == search_request.with_user_id,
                    Message.recipient_id == search_request.with_user_id,
                )
            )

        query = (
            query.order_by(desc(Message.created_at))
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
            select(Message).where(
                Message.id.in_(message_ids),
                Message.recipient_id == user_id,
                Message.is_read == False,
            )
        )
        messages = result.scalars().all()

        count = 0
        for message in messages:
            message.is_read = True
            message.read_at = get_utc_now()
            count += 1

        if count > 0:
            await db.commit()
            logger.info(
                f"Marked {count} messages as read",
                user_id=user_id,
                component="message",
            )

        return count

    async def mark_conversation_as_read(
        self, db: AsyncSession, user_id: int, other_user_id: int
    ) -> int:
        """Mark all unread messages from another user as read."""
        result = await db.execute(
            select(Message).where(
                Message.sender_id == other_user_id,
                Message.recipient_id == user_id,
                Message.is_read == False,
                Message.is_deleted_by_recipient == False,
            )
        )
        messages = result.scalars().all()

        count = 0
        for message in messages:
            message.is_read = True
            message.read_at = get_utc_now()
            count += 1

        if count > 0:
            await db.commit()
            logger.info(
                f"Marked conversation as read - {count} messages",
                user_id=user_id,
                other_user_id=other_user_id,
                component="message",
            )

        return count


# Create singleton instance
message_service = MessageService()
