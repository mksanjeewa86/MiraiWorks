from typing import List, Optional
from datetime import datetime
from sqlalchemy import and_, case, desc, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.direct_message import DirectMessage
from app.models.user import User


async def get_messages_between_users(
    db: AsyncSession,
    user1_id: int,
    user2_id: int,
    limit: int = 50,
    offset: int = 0,
) -> List[DirectMessage]:
    """Get messages between two users."""
    query = (
        select(DirectMessage)
        .where(
            or_(
                and_(DirectMessage.sender_id == user1_id, DirectMessage.receiver_id == user2_id),
                and_(DirectMessage.sender_id == user2_id, DirectMessage.receiver_id == user1_id),
            )
        )
        .options(selectinload(DirectMessage.sender), selectinload(DirectMessage.receiver))
        .order_by(desc(DirectMessage.created_at))
        .offset(offset)
        .limit(limit)
    )
    
    result = await db.execute(query)
    return list(reversed(result.scalars().all()))


async def create_message(
    db: AsyncSession,
    sender_id: int,
    receiver_id: int,
    content: str,
    message_type: str = "text",
) -> DirectMessage:
    """Create a new direct message."""
    message = DirectMessage(
        sender_id=sender_id,
        receiver_id=receiver_id,
        content=content,
        type=message_type,
    )
    db.add(message)
    await db.commit()
    await db.refresh(message)
    return message


async def get_message_by_id(db: AsyncSession, message_id: int) -> Optional[DirectMessage]:
    """Get message by ID."""
    result = await db.execute(
        select(DirectMessage)
        .where(DirectMessage.id == message_id)
        .options(selectinload(DirectMessage.sender), selectinload(DirectMessage.receiver))
    )
    return result.scalar_one_or_none()


async def mark_messages_as_read(
    db: AsyncSession,
    sender_id: int,
    receiver_id: int,
) -> int:
    """Mark all messages from sender to receiver as read."""
    query = (
        update(DirectMessage)
        .where(
            and_(
                DirectMessage.sender_id == sender_id,
                DirectMessage.receiver_id == receiver_id,
                DirectMessage.read_at.is_(None),
            )
        )
        .values(read_at=datetime.utcnow())
    )
    
    result = await db.execute(query)
    await db.commit()
    return result.rowcount


async def get_conversation_partners(
    db: AsyncSession,
    user_id: int,
) -> List[dict]:
    """Get all users who have had conversations with the given user."""
    # Subquery to get the latest message for each conversation
    latest_message_subquery = (
        select(
            func.greatest(DirectMessage.sender_id, DirectMessage.receiver_id).label("user1"),
            func.least(DirectMessage.sender_id, DirectMessage.receiver_id).label("user2"),
            func.max(DirectMessage.created_at).label("latest_message_time"),
        )
        .where(
            or_(DirectMessage.sender_id == user_id, DirectMessage.receiver_id == user_id)
        )
        .group_by(
            func.greatest(DirectMessage.sender_id, DirectMessage.receiver_id),
            func.least(DirectMessage.sender_id, DirectMessage.receiver_id),
        )
        .subquery()
    )
    
    # Query to get conversation partners with latest message info
    query = (
        select(
            User.id,
            User.first_name,
            User.last_name,
            User.email,
            DirectMessage.content.label("last_message"),
            DirectMessage.created_at.label("last_message_time"),
            DirectMessage.sender_id.label("last_sender_id"),
            func.count(
                case((DirectMessage.read_at.is_(None) & (DirectMessage.receiver_id == user_id), 1))
            ).label("unread_count"),
        )
        .select_from(latest_message_subquery)
        .join(
            DirectMessage,
            and_(
                or_(
                    and_(
                        DirectMessage.sender_id == latest_message_subquery.c.user1,
                        DirectMessage.receiver_id == latest_message_subquery.c.user2,
                    ),
                    and_(
                        DirectMessage.sender_id == latest_message_subquery.c.user2,
                        DirectMessage.receiver_id == latest_message_subquery.c.user1,
                    ),
                ),
                DirectMessage.created_at == latest_message_subquery.c.latest_message_time,
            ),
        )
        .join(
            User,
            User.id == case(
                (latest_message_subquery.c.user1 == user_id, latest_message_subquery.c.user2),
                else_=latest_message_subquery.c.user1,
            ),
        )
        .group_by(
            User.id,
            User.first_name,
            User.last_name,
            User.email,
            DirectMessage.content,
            DirectMessage.created_at,
            DirectMessage.sender_id,
        )
        .order_by(desc(DirectMessage.created_at))
    )
    
    result = await db.execute(query)
    return [dict(row._mapping) for row in result]


async def get_unread_message_count(db: AsyncSession, user_id: int) -> int:
    """Get total unread message count for user."""
    query = select(func.count(DirectMessage.id)).where(
        and_(
            DirectMessage.receiver_id == user_id,
            DirectMessage.read_at.is_(None),
        )
    )
    
    result = await db.execute(query)
    return result.scalar() or 0