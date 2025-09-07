from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.dependencies import get_current_active_user
from app.models.direct_message import DirectMessage
from app.models.user import User
from app.schemas.direct_message import (
    ConversationListResponse,
    ConversationSummary,
    DirectMessageCreate,
    DirectMessageInfo,
    MessageListResponse,
    MessageReadRequest,
    MessageSearchRequest,
)
from app.services.direct_message_service import direct_message_service
from app.utils.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("/conversations", response_model=ConversationListResponse)
async def get_conversations(
    search: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get list of users the current user has exchanged messages with."""
    conversations = await direct_message_service.get_conversations(
        db, current_user.id, search
    )
    
    return ConversationListResponse(
        conversations=conversations,
        total=len(conversations)
    )


@router.get("/with/{other_user_id}", response_model=MessageListResponse)
async def get_messages_with_user(
    other_user_id: int,
    limit: int = 50,
    before_id: Optional[int] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get messages between current user and another user."""
    messages = await direct_message_service.get_messages_with_user(
        db, current_user.id, other_user_id, limit, before_id
    )
    
    # Convert to response format
    message_infos = []
    for msg in messages:
        message_info = DirectMessageInfo(
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
            created_at=msg.created_at,
            read_at=msg.read_at,
        )
        message_infos.append(message_info)

    return MessageListResponse(
        messages=message_infos,
        total=len(message_infos),
        has_more=len(messages) == limit
    )


@router.post("/send", response_model=DirectMessageInfo)
async def send_message(
    message_data: DirectMessageCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Send a direct message to another user."""
    message = await direct_message_service.send_message(
        db, current_user.id, message_data
    )

    # Load with relationships for response
    result = await db.execute(
        select(DirectMessage)
        .options(
            selectinload(DirectMessage.sender),
            selectinload(DirectMessage.recipient),
        )
        .where(DirectMessage.id == message.id)
    )
    message = result.scalar_one()

    return DirectMessageInfo(
        id=message.id,
        sender_id=message.sender_id,
        recipient_id=message.recipient_id,
        sender_name=message.sender.full_name,
        recipient_name=message.recipient.full_name,
        sender_email=message.sender.email,
        recipient_email=message.recipient.email,
        content=message.content,
        type=message.type,
        is_read=message.is_read,
        reply_to_id=message.reply_to_id,
        created_at=message.created_at,
        read_at=message.read_at,
    )


@router.post("/search", response_model=MessageListResponse)
async def search_messages(
    search_request: MessageSearchRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Search messages by content and sender name."""
    messages = await direct_message_service.search_messages(
        db, current_user.id, search_request
    )
    
    # Get total count for same search
    count_query = (
        select(func.count(DirectMessage.id))
        .where(
            or_(
                and_(
                    DirectMessage.sender_id == current_user.id,
                    DirectMessage.is_deleted_by_sender == False,
                ),
                and_(
                    DirectMessage.recipient_id == current_user.id,
                    DirectMessage.is_deleted_by_recipient == False,
                ),
            )
        )
    )
    
    if search_request.query:
        search_term = f"%{search_request.query}%"
        count_query = count_query.join(DirectMessage.sender).where(
            or_(
                DirectMessage.content.ilike(search_term),
                User.first_name.ilike(search_term),
                User.last_name.ilike(search_term),
                User.email.ilike(search_term),
            )
        )
    
    if search_request.with_user_id:
        count_query = count_query.where(
            or_(
                DirectMessage.sender_id == search_request.with_user_id,
                DirectMessage.recipient_id == search_request.with_user_id,
            )
        )
    
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Convert to response format
    message_infos = []
    for msg in messages:
        message_info = DirectMessageInfo(
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
            created_at=msg.created_at,
            read_at=msg.read_at,
        )
        message_infos.append(message_info)

    return MessageListResponse(
        messages=message_infos,
        total=total,
        has_more=(search_request.offset + len(messages)) < total
    )


@router.put("/mark-read")
async def mark_messages_as_read(
    read_request: MessageReadRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark specific messages as read."""
    count = await direct_message_service.mark_messages_as_read(
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
    count = await direct_message_service.mark_conversation_as_read(
        db, current_user.id, other_user_id
    )
    
    return {"message": f"Marked {count} messages as read"}


@router.get("/participants/search")
async def search_message_participants(
    query: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get list of users current user can send messages to."""
    participants = await rules_service.get_allowed_conversation_participants(
        db, current_user.id
    )

    # Apply search filter
    if query:
        query_lower = query.lower()
        participants = [
            p
            for p in participants
            if query_lower in p["full_name"].lower()
            or query_lower in p["email"].lower()
        ]

    return {"participants": participants}