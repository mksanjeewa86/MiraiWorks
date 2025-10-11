from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.endpoints import API_ROUTES
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
from app.utils.constants import UserRole
from app.utils.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


async def validate_messaging_permission(
    db: AsyncSession, sender_id: int, recipient_id: int
):
    """Validate that sender can message recipient - only connected users can message."""
    from sqlalchemy import select, or_
    from app.models.user_connection import UserConnection

    # Get both users
    users = await message.get_users_with_roles(db, [sender_id, recipient_id])
    if len(users) != 2:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sender or recipient not found",
        )

    # Check if users are connected in user_connections table
    query = select(UserConnection).where(
        or_(
            (UserConnection.user_id == sender_id) & (UserConnection.connected_user_id == recipient_id),
            (UserConnection.user_id == recipient_id) & (UserConnection.connected_user_id == sender_id)
        ),
        UserConnection.is_active == True
    )

    result = await db.execute(query)
    connection = result.scalar_one_or_none()

    if not connection:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only message users you are connected with",
        )


@router.get(API_ROUTES.MESSAGES.CONVERSATIONS, response_model=ConversationListResponse)
async def get_conversations(
    search: str | None = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get list of users the current user has exchanged messages with."""
    conversations = await message_service.get_conversations(db, current_user.id, search)

    return ConversationListResponse(
        conversations=conversations, total=len(conversations)
    )


@router.get(API_ROUTES.MESSAGES.WITH_USER, response_model=MessageListResponse)
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


@router.post(API_ROUTES.MESSAGES.SEND, response_model=MessageInfo)
async def send_message(
    message_data: MessageCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Send a direct message to another user."""
    # Validate messaging permissions based on roles
    await validate_messaging_permission(db, current_user.id, message_data.recipient_id)

    new_message = await message_service.send_message(db, current_user.id, message_data)

    # Load with relationships for response
    message_with_relations = await message.get_message_with_relationships(
        db, new_message.id
    )

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


@router.post(API_ROUTES.MESSAGES.SEARCH, response_model=MessageListResponse)
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


@router.put(API_ROUTES.MESSAGES.MARK_READ_SINGLE)
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


@router.put(API_ROUTES.MESSAGES.MARK_READ_CONVERSATION)
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


@router.get(API_ROUTES.MESSAGES.PARTICIPANTS)
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


@router.get(API_ROUTES.MESSAGES.RESTRICTED_USERS)
async def get_restricted_user_ids(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get list of user IDs that current user cannot message."""
    # No restrictions - everyone can message everyone
    return {"restricted_user_ids": []}
