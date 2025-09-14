from typing import List, Optional

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models.message import Conversation, Message, MessageRead
from app.models.user import User


class CRUDMessaging(CRUDBase[Conversation, dict, dict]):
    """Messaging CRUD operations."""

    async def get_conversations_with_pagination(
        self,
        db: AsyncSession,
        user_id: int,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[List[Conversation], int]:
        """Get user's conversations with pagination and search."""
        # Base query for conversations user participates in
        query = (
            select(Conversation)
            .options(
                selectinload(Conversation.participants).selectinload(User.company),
                selectinload(Conversation.messages).selectinload(Message.sender),
                selectinload(Conversation.messages).selectinload(Message.attachments),
            )
            .join(Conversation.participants)
            .where(User.id == user_id, Conversation.is_active == True)
            .order_by(desc(Conversation.updated_at))
        )

        # Apply search filter
        if search:
            search_term = f"%{search}%"
            from sqlalchemy import or_
            query = query.where(
                or_(
                    Conversation.title.ilike(search_term),
                    Conversation.participants.any(User.first_name.ilike(search_term)),
                    Conversation.participants.any(User.last_name.ilike(search_term)),
                    Conversation.participants.any(User.email.ilike(search_term)),
                )
            )

        # Count total
        count_result = await db.execute(select(func.count()).select_from(query.subquery()))
        total = count_result.scalar()

        # Apply pagination
        paginated_query = query.offset(offset).limit(limit)
        result = await db.execute(paginated_query)
        conversations = result.unique().scalars().all()

        return conversations, total

    async def get_unread_count_for_conversation(
        self, db: AsyncSession, conversation_id: int, user_id: int
    ) -> int:
        """Get unread count for a specific conversation."""
        unread_result = await db.execute(
            select(func.count(Message.id)).where(
                Message.conversation_id == conversation_id,
                Message.sender_id != user_id,
                ~Message.message_reads.any(MessageRead.user_id == user_id),
            )
        )
        return unread_result.scalar()

    async def get_conversation_with_relationships(
        self, db: AsyncSession, conversation_id: int
    ) -> Optional[Conversation]:
        """Get conversation with participants loaded."""
        result = await db.execute(
            select(Conversation)
            .options(selectinload(Conversation.participants))
            .where(Conversation.id == conversation_id)
        )
        return result.scalar_one_or_none()

    async def get_message_read_status(
        self, db: AsyncSession, message_ids: List[int], user_id: int
    ) -> set[int]:
        """Get read status for messages by user."""
        read_result = await db.execute(
            select(MessageRead.message_id).where(
                MessageRead.user_id == user_id,
                MessageRead.message_id.in_(message_ids),
            )
        )
        return set(read_result.scalars().all())

    async def get_message_with_relationships(
        self, db: AsyncSession, message_id: int
    ) -> Optional[Message]:
        """Get message with sender and reply relationships."""
        result = await db.execute(
            select(Message)
            .options(
                selectinload(Message.sender),
                selectinload(Message.reply_to).selectinload(Message.sender),
                selectinload(Message.attachments),
            )
            .where(Message.id == message_id)
        )
        return result.scalar_one_or_none()

    async def get_latest_message_id_in_conversation(
        self, db: AsyncSession, conversation_id: int
    ) -> Optional[int]:
        """Get the latest message ID in a conversation."""
        latest_message_result = await db.execute(
            select(Message.id)
            .where(Message.conversation_id == conversation_id)
            .order_by(desc(Message.id))
            .limit(1)
        )
        return latest_message_result.scalar()


# Create the CRUD instance
messaging = CRUDMessaging(Conversation)