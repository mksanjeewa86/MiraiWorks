
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.messages import message
from app.database import get_db
from app.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.message import (
    ConversationListResponse,
    MessageCreate,
    MessageInfo,
    MessageListResponse,
    MessageReadRequest,
    MessageSearchRequest,
)
from app.services.message_service import message_service
from app.services.notification_service import notification_service
from app.utils.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


async def validate_messaging_permission(
    db: AsyncSession, sender_id: int, recipient_id: int
):
    """Validate that sender can message recipient based on role restrictions."""
    # Get both users with their roles
    users = await message.get_users_with_roles(db, [sender_id, recipient_id])
    if len(users) != 2:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sender or recipient not found",
        )

    # Identify sender and recipient
    sender = next(u for u in users if u.id == sender_id)
    recipient = next(u for u in users if u.id == recipient_id)

    # Get user roles
    sender_roles = [ur.role.name for ur in sender.user_roles]
    recipient_roles = [ur.role.name for ur in recipient.user_roles]

    # Check messaging permissions
    if "super_admin" in sender_roles:
        # Super admin can only message company admins
        if "company_admin" not in recipient_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Super admin can only message company admins",
            )
    elif "company_admin" in sender_roles:
        # Company admin can only message super admins
        if "super_admin" not in recipient_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Company admins can only message super admins",
            )
    # Other roles can message anyone except company admins
    elif "company_admin" in recipient_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only super admins can message company admins",
        )


@router.get("/conversations", response_model=ConversationListResponse)
async def get_conversations(
    search: str | None = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get list of users the current user has exchanged messages with."""
    conversations = await message_service.get_conversations(
        db, current_user.id, search
    )

    return ConversationListResponse(
        conversations=conversations, total=len(conversations)
    )


@router.get("/with/{other_user_id}", response_model=MessageListResponse)
async def get_messages_with_user(
    other_user_id: int,
    limit: int = 50,
    before_id: int | None = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get messages between current user and another user."""
    messages = await message_service.get_messages_with_user(
        db, current_user.id, other_user_id, limit, before_id
    )

    # Convert to response format
    message_infos = []
    for msg in messages:
        message_info = MessageInfo(
            id=msg.id,
            sender_id=msg.sender_id,
            recipient_id=msg.recipient_id,
            sender_name=msg.sender.full_name,
            recipient_name=msg.recipient.full_name,
            sender_email=msg.sender.email,
            recipient_email=msg.recipient.email,
            content=msg.content,
            type=msg.type,
            is_read=msg.is_read,
            reply_to_id=msg.reply_to_id,
            file_url=msg.file_url,
            file_name=msg.file_name,
            file_size=msg.file_size,
            file_type=msg.file_type,
            created_at=msg.created_at,
            read_at=msg.read_at,
        )
        message_infos.append(message_info)

    return MessageListResponse(
        messages=message_infos,
        total=len(message_infos),
        has_more=len(messages) == limit,
    )


@router.post("/send", response_model=MessageInfo)
async def send_message(
    message_data: MessageCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Send a direct message to another user."""
    # Validate messaging permissions based on roles
    await validate_messaging_permission(db, current_user.id, message_data.recipient_id)

    new_message = await message_service.send_message(
        db, current_user.id, message_data
    )

    # Load with relationships for response
    message_with_relations = await message.get_message_with_relationships(db, new_message.id)

    # Handle notifications (email and in-app)
    await notification_service.handle_new_message_notifications(
        db, current_user.id, message_with_relations.recipient_id, message_with_relations
    )

    return MessageInfo(
        id=message_with_relations.id,
        sender_id=message_with_relations.sender_id,
        recipient_id=message_with_relations.recipient_id,
        sender_name=message_with_relations.sender.full_name,
        recipient_name=message_with_relations.recipient.full_name,
        sender_email=message_with_relations.sender.email,
        recipient_email=message_with_relations.recipient.email,
        content=message_with_relations.content,
        type=message_with_relations.type,
        is_read=message_with_relations.is_read,
        reply_to_id=message_with_relations.reply_to_id,
        file_url=message_with_relations.file_url,
        file_name=message_with_relations.file_name,
        file_size=message_with_relations.file_size,
        file_type=message_with_relations.file_type,
        created_at=message_with_relations.created_at,
        read_at=message_with_relations.read_at,
    )


@router.post("/search", response_model=MessageListResponse)
async def search_messages(
    search_request: MessageSearchRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Search messages by content and sender name."""
    messages, total = await message.search_messages_with_count(
        db, current_user.id, search_request
    )

    # Convert to response format
    message_infos = []
    for msg in messages:
        message_info = MessageInfo(
            id=msg.id,
            sender_id=msg.sender_id,
            recipient_id=msg.recipient_id,
            sender_name=msg.sender.full_name,
            recipient_name=msg.recipient.full_name,
            sender_email=msg.sender.email,
            recipient_email=msg.recipient.email,
            content=msg.content,
            type=msg.type,
            is_read=msg.is_read,
            reply_to_id=msg.reply_to_id,
            file_url=msg.file_url,
            file_name=msg.file_name,
            file_size=msg.file_size,
            file_type=msg.file_type,
            created_at=msg.created_at,
            read_at=msg.read_at,
        )
        message_infos.append(message_info)

    return MessageListResponse(
        messages=message_infos,
        total=total,
        has_more=(search_request.offset + len(messages)) < total,
    )


@router.put("/mark-read")
async def mark_messages_as_read(
    read_request: MessageReadRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark specific messages as read."""
    count = await message_service.mark_messages_as_read(
        db, current_user.id, read_request.message_ids
    )

    return {"message": f"Marked {count} messages as read"}


@router.put("/mark-conversation-read/{other_user_id}")
async def mark_conversation_as_read(
    other_user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark all messages from another user as read."""
    count = await message_service.mark_conversation_as_read(
        db, current_user.id, other_user_id
    )

    return {"message": f"Marked {count} messages as read"}


@router.get("/participants")
async def get_message_participants(
    query: str | None = None,
    limit: int = 50,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get list of users current user can send messages to."""
    # Get current user's roles to determine filtering logic
    current_user_roles = [user_role.role.name for user_role in current_user.user_roles]

    # Get users using CRUD method
    users = await message.get_message_participants(
        db, current_user.id, current_user_roles, query, limit
    )

    # Format response
    participants = []
    for user in users:
        participants.append(
            {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "company_name": user.company.name if user.company else None,
                "is_online": False,  # Could be enhanced with presence tracking
            }
        )

    return {"participants": participants}


@router.get("/restricted-users")
async def get_restricted_user_ids(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get list of user IDs that current user cannot message."""
    from sqlalchemy import select

    from app.models.role import Role
    from app.models.role import UserRole

    # Get current user's roles
    current_user_roles = [user_role.role.name for user_role in current_user.user_roles]

    # Determine which users are restricted based on messaging rules
    restricted_user_ids = []

    if "super_admin" in current_user_roles:
        # Super admin can only message company admins, so restrict non-company-admin users
        query = (
            select(User.id)
            .join(UserRole, User.id == UserRole.user_id)
            .join(Role, UserRole.role_id == Role.id)
            .where(Role.name != "company_admin")
            .where(User.is_active is True)
            .where(User.is_deleted is False)
        )
        result = await db.execute(query)
        restricted_user_ids = [user_id for user_id, in result.fetchall()]

    elif "company_admin" in current_user_roles:
        # Company admin can only message super admins, so restrict non-super-admin users
        query = (
            select(User.id)
            .join(UserRole, User.id == UserRole.user_id)
            .join(Role, UserRole.role_id == Role.id)
            .where(Role.name != "super_admin")
            .where(User.is_active is True)
            .where(User.is_deleted is False)
        )
        result = await db.execute(query)
        restricted_user_ids = [user_id for user_id, in result.fetchall()]

    else:
        # Other users can message anyone except company admins
        query = (
            select(User.id)
            .join(UserRole, User.id == UserRole.user_id)
            .join(Role, UserRole.role_id == Role.id)
            .where(Role.name == "company_admin")
            .where(User.is_active is True)
            .where(User.is_deleted is False)
        )
        result = await db.execute(query)
        restricted_user_ids = [user_id for user_id, in result.fetchall()]

    return {"restricted_user_ids": restricted_user_ids}
