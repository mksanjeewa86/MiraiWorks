from datetime import datetime
from typing import List, Optional

from sqlalchemy import and_, case, desc, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models.direct_message import DirectMessage
from app.models.role import Role, UserRole
from app.models.user import User
from app.schemas.direct_message import MessageSearchRequest


async def get_messages_between_users(
    db: AsyncSession,
    user1_id: int,
    user2_id: int,
    limit: int = 50,
    offset: int = 0,
) -> list[DirectMessage]:
    """Get messages between two users."""
    query = (
        select(DirectMessage)
        .where(
            or_(
                and_(
                    DirectMessage.sender_id == user1_id,
                    DirectMessage.receiver_id == user2_id,
                ),
                and_(
                    DirectMessage.sender_id == user2_id,
                    DirectMessage.receiver_id == user1_id,
                ),
            )
        )
        .options(
            selectinload(DirectMessage.sender), selectinload(DirectMessage.receiver)
        )
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


async def get_message_by_id(
    db: AsyncSession, message_id: int
) -> Optional[DirectMessage]:
    """Get message by ID."""
    result = await db.execute(
        select(DirectMessage)
        .where(DirectMessage.id == message_id)
        .options(
            selectinload(DirectMessage.sender), selectinload(DirectMessage.receiver)
        )
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
) -> list[dict]:
    """Get all users who have had conversations with the given user."""
    # Subquery to get the latest message for each conversation
    latest_message_subquery = (
        select(
            func.greatest(DirectMessage.sender_id, DirectMessage.receiver_id).label(
                "user1"
            ),
            func.least(DirectMessage.sender_id, DirectMessage.receiver_id).label(
                "user2"
            ),
            func.max(DirectMessage.created_at).label("latest_message_time"),
        )
        .where(
            or_(
                DirectMessage.sender_id == user_id, DirectMessage.receiver_id == user_id
            )
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
                case(
                    (
                        DirectMessage.read_at.is_(None)
                        & (DirectMessage.receiver_id == user_id),
                        1,
                    )
                )
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
                DirectMessage.created_at
                == latest_message_subquery.c.latest_message_time,
            ),
        )
        .join(
            User,
            User.id
            == case(
                (
                    latest_message_subquery.c.user1 == user_id,
                    latest_message_subquery.c.user2,
                ),
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


class CRUDDirectMessage(CRUDBase[DirectMessage, dict, dict]):
    """Direct message CRUD operations."""

    async def get_users_with_roles(self, db: AsyncSession, user_ids: List[int]) -> List[User]:
        """Get users with their roles by IDs."""
        result = await db.execute(
            select(User)
            .join(User.user_roles)
            .join(UserRole.role)
            .where(User.id.in_(user_ids))
            .options(selectinload(User.user_roles).selectinload(UserRole.role))
        )
        return result.scalars().all()

    async def get_message_with_relationships(self, db: AsyncSession, message_id: int) -> Optional[DirectMessage]:
        """Get message with sender and recipient relationships."""
        result = await db.execute(
            select(DirectMessage)
            .options(
                selectinload(DirectMessage.sender),
                selectinload(DirectMessage.recipient),
            )
            .where(DirectMessage.id == message_id)
        )
        return result.scalar_one_or_none()

    async def search_messages_with_count(
        self, db: AsyncSession, user_id: int, search_request: MessageSearchRequest
    ) -> tuple[List[DirectMessage], int]:
        """Search messages and get total count."""
        # Base query for messages
        base_conditions = or_(
            and_(
                DirectMessage.sender_id == user_id,
                DirectMessage.is_deleted_by_sender == False,
            ),
            and_(
                DirectMessage.recipient_id == user_id,
                DirectMessage.is_deleted_by_recipient == False,
            ),
        )

        # Messages query
        messages_query = (
            select(DirectMessage)
            .options(
                selectinload(DirectMessage.sender),
                selectinload(DirectMessage.recipient),
            )
            .where(base_conditions)
        )

        # Count query
        count_query = select(func.count(DirectMessage.id)).where(base_conditions)

        # Apply search filters
        if search_request.query:
            search_term = f"%{search_request.query}%"
            search_conditions = or_(
                DirectMessage.content.ilike(search_term),
                User.first_name.ilike(search_term),
                User.last_name.ilike(search_term),
                User.email.ilike(search_term),
            )
            messages_query = messages_query.join(DirectMessage.sender).where(search_conditions)
            count_query = count_query.join(DirectMessage.sender).where(search_conditions)

        if search_request.with_user_id:
            user_filter = or_(
                DirectMessage.sender_id == search_request.with_user_id,
                DirectMessage.recipient_id == search_request.with_user_id,
            )
            messages_query = messages_query.where(user_filter)
            count_query = count_query.where(user_filter)

        # Apply pagination and ordering
        messages_query = (
            messages_query.order_by(desc(DirectMessage.created_at))
            .offset(search_request.offset)
            .limit(search_request.limit)
        )

        # Execute queries
        messages_result = await db.execute(messages_query)
        count_result = await db.execute(count_query)

        return messages_result.scalars().all(), count_result.scalar() or 0

    async def get_message_participants(
        self, db: AsyncSession, current_user_id: int, current_user_roles: List[str], query: Optional[str] = None, limit: int = 50
    ) -> List[User]:
        """Get list of users current user can send messages to based on role restrictions."""
        # Build base query
        query_stmt = (
            select(User)
            .join(User.user_roles)
            .join(UserRole.role)
            .where(User.is_active == True, User.id != current_user_id)
            .options(
                selectinload(User.company),
                selectinload(User.user_roles).selectinload(UserRole.role),
            )
            .order_by(User.first_name, User.last_name)
            .limit(limit)
        )

        # Apply role-based filtering
        if "super_admin" in current_user_roles:
            # Super admin can message all company admins
            query_stmt = query_stmt.where(Role.name == "company_admin")
        elif "company_admin" in current_user_roles:
            # Company admin can ONLY message super admin (not other company admins)
            query_stmt = query_stmt.where(Role.name == "super_admin")
        # For other roles, no role-based filtering (can message anyone)

        # Apply search filter if provided
        if query:
            search_term = f"%{query}%"
            query_stmt = query_stmt.where(
                or_(
                    User.first_name.ilike(search_term),
                    User.last_name.ilike(search_term),
                    User.email.ilike(search_term),
                )
            )

        result = await db.execute(query_stmt)
        return result.scalars().all()


# Create the CRUD instance
direct_message = CRUDDirectMessage(DirectMessage)
