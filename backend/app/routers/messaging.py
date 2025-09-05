import logging
from typing import Optional

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request
from fastapi import status
from sqlalchemy import desc
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.dependencies import check_rate_limit
from app.dependencies import get_client_ip
from app.dependencies import get_current_active_user
from app.models.attachment import Attachment
from app.models.message import Conversation
from app.models.message import Message
from app.models.message import MessageRead
from app.models.user import User
from app.schemas.message import AttachmentInfo
from app.schemas.message import AttachmentScanComplete
from app.schemas.message import ConversationCreate
from app.schemas.message import ConversationInfo
from app.schemas.message import ConversationListRequest
from app.schemas.message import ConversationListResponse
from app.schemas.message import ConversationParticipant
from app.schemas.message import FileUploadRequest
from app.schemas.message import FileUploadResponse
from app.schemas.message import MessageCreate
from app.schemas.message import MessageInfo
from app.schemas.message import MessageListRequest
from app.schemas.message import MessageListResponse
from app.schemas.message import MessageReadRequest
from app.services.antivirus_service import antivirus_service
from app.services.messaging_service import messaging_service
from app.services.storage_service import storage_service
from app.utils.constants import VirusStatus

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/conversations", response_model=ConversationListResponse)
async def get_conversations(
    request: ConversationListRequest = Depends(),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's conversations with pagination."""
    # Base query for conversations user participates in
    query = select(Conversation).options(
        selectinload(Conversation.participants),
        selectinload(Conversation.messages).selectinload(Message.sender).options(
            selectinload(Message.attachments)
        )
    ).join(Conversation.participants).where(
        User.id == current_user.id,
        Conversation.is_active == True
    ).order_by(desc(Conversation.updated_at))
    
    # Apply search filter
    if request.search:
        # Search in conversation title or participant names
        search_term = f"%{request.search}%"
        query = query.where(
            or_(
                Conversation.title.ilike(search_term),
                Conversation.participants.any(User.first_name.ilike(search_term)),
                Conversation.participants.any(User.last_name.ilike(search_term)),
                Conversation.participants.any(User.email.ilike(search_term))
            )
        )
    
    # Count total
    count_result = await db.execute(
        select(func.count()).select_from(query.subquery())
    )
    total = count_result.scalar()
    
    # Apply pagination
    paginated_query = query.offset(request.offset).limit(request.limit)
    result = await db.execute(paginated_query)
    conversations = result.unique().scalars().all()
    
    # Convert to response format
    conversation_infos = []
    for conv in conversations:
        # Get last message
        last_message = None
        if conv.messages:
            last_msg = conv.messages[-1]  # Already ordered by created_at
            last_message = MessageInfo(
                id=last_msg.id,
                type=last_msg.type,
                content=last_msg.content,
                is_edited=last_msg.is_edited,
                sender_id=last_msg.sender_id,
                sender_name=last_msg.sender.full_name,
                sender_email=last_msg.sender.email,
                attachments=[
                    AttachmentInfo(
                        id=att.id,
                        original_filename=att.original_filename,
                        mime_type=att.mime_type,
                        file_size=att.file_size,
                        file_size_mb=att.file_size_mb,
                        is_image=att.is_image,
                        is_document=att.is_document,
                        is_available=att.is_available,
                        virus_status=att.virus_status,
                        created_at=att.created_at
                    ) for att in last_msg.attachments
                ],
                created_at=last_msg.created_at,
                updated_at=last_msg.updated_at
            )
        
        # Get unread count
        unread_result = await db.execute(
            select(func.count(Message.id)).where(
                Message.conversation_id == conv.id,
                Message.sender_id != current_user.id,
                ~Message.message_reads.any(MessageRead.user_id == current_user.id)
            )
        )
        unread_count = unread_result.scalar()
        
        conversation_infos.append(ConversationInfo(
            id=conv.id,
            title=conv.title,
            type=conv.type,
            is_active=conv.is_active,
            participants=[
                ConversationParticipant(
                    id=p.id,
                    email=p.email,
                    full_name=p.full_name,
                    company_name=p.company.name if p.company else None
                ) for p in conv.participants if p.id != current_user.id
            ],
            last_message=last_message,
            unread_count=unread_count,
            created_at=conv.created_at,
            updated_at=conv.updated_at
        ))
    
    return ConversationListResponse(
        conversations=conversation_infos,
        total=total,
        has_more=request.offset + request.limit < total
    )


@router.post("/conversations", response_model=ConversationInfo)
async def create_conversation(
    conversation_data: ConversationCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new conversation."""
    conversation = await messaging_service.create_conversation(
        db,
        current_user.id,
        conversation_data.participant_ids,
        conversation_data.title
    )
    
    # Load with relationships for response
    result = await db.execute(
        select(Conversation)
        .options(selectinload(Conversation.participants))
        .where(Conversation.id == conversation.id)
    )
    conversation = result.scalar_one()
    
    return ConversationInfo(
        id=conversation.id,
        title=conversation.title,
        type=conversation.type,
        is_active=conversation.is_active,
        participants=[
            ConversationParticipant(
                id=p.id,
                email=p.email,
                full_name=p.full_name,
                company_name=p.company.name if p.company else None
            ) for p in conversation.participants if p.id != current_user.id
        ],
        created_at=conversation.created_at,
        updated_at=conversation.updated_at
    )


@router.get("/conversations/{conversation_id}/messages", response_model=MessageListResponse)
async def get_conversation_messages(
    conversation_id: int,
    request: MessageListRequest = Depends(),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get messages from a conversation."""
    messages = await messaging_service.get_conversation_messages(
        db, conversation_id, current_user.id, request.limit, request.before_id
    )
    
    # Get read status for messages
    message_ids = [m.id for m in messages]
    read_result = await db.execute(
        select(MessageRead.message_id).where(
            MessageRead.user_id == current_user.id,
            MessageRead.message_id.in_(message_ids)
        )
    )
    read_message_ids = set(read_result.scalars().all())
    
    # Convert to response format
    message_infos = []
    for msg in messages:
        # Generate download URLs for available attachments
        attachments = []
        for att in msg.attachments:
            download_url = None
            if att.is_available and att.virus_status == VirusStatus.CLEAN.value:
                try:
                    download_url = storage_service.get_presigned_url(att.s3_key)
                except Exception as e:
                    logger.error(f"Failed to generate download URL for attachment {att.id}: {e}")
            
            attachments.append(AttachmentInfo(
                id=att.id,
                original_filename=att.original_filename,
                mime_type=att.mime_type,
                file_size=att.file_size,
                file_size_mb=att.file_size_mb,
                is_image=att.is_image,
                is_document=att.is_document,
                is_available=att.is_available,
                virus_status=att.virus_status,
                download_url=download_url,
                created_at=att.created_at
            ))
        
        # Handle reply_to
        reply_to = None
        if msg.reply_to:
            reply_to = MessageInfo(
                id=msg.reply_to.id,
                type=msg.reply_to.type,
                content=msg.reply_to.content,
                sender_id=msg.reply_to.sender_id,
                sender_name=msg.reply_to.sender.full_name,
                sender_email=msg.reply_to.sender.email,
                created_at=msg.reply_to.created_at,
                updated_at=msg.reply_to.updated_at,
                attachments=[],  # Don't include nested attachments for replies
                is_read=msg.reply_to.id in read_message_ids
            )
        
        message_infos.append(MessageInfo(
            id=msg.id,
            type=msg.type,
            content=msg.content,
            is_edited=msg.is_edited,
            edited_content=msg.edited_content,
            sender_id=msg.sender_id,
            sender_name=msg.sender.full_name,
            sender_email=msg.sender.email,
            reply_to_id=msg.reply_to_id,
            reply_to=reply_to,
            attachments=attachments,
            is_read=msg.id in read_message_ids,
            created_at=msg.created_at,
            updated_at=msg.updated_at
        ))
    
    return MessageListResponse(
        messages=message_infos,
        has_more=len(messages) == request.limit,
        conversation_id=conversation_id
    )


@router.post("/conversations/{conversation_id}/messages", response_model=MessageInfo)
async def send_message(
    conversation_id: int,
    message_data: MessageCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Send a message in a conversation."""
    message = await messaging_service.send_message(
        db,
        conversation_id,
        current_user.id,
        message_data.content,
        message_data.type,
        message_data.reply_to_id
    )
    
    # Load with relationships
    result = await db.execute(
        select(Message)
        .options(
            selectinload(Message.sender),
            selectinload(Message.reply_to).selectinload(Message.sender),
            selectinload(Message.attachments)
        )
        .where(Message.id == message.id)
    )
    message = result.scalar_one()
    
    # Convert to response
    reply_to = None
    if message.reply_to:
        reply_to = MessageInfo(
            id=message.reply_to.id,
            type=message.reply_to.type,
            content=message.reply_to.content,
            sender_id=message.reply_to.sender_id,
            sender_name=message.reply_to.sender.full_name,
            sender_email=message.reply_to.sender.email,
            created_at=message.reply_to.created_at,
            updated_at=message.reply_to.updated_at,
            attachments=[],
            is_read=True
        )
    
    message_info = MessageInfo(
        id=message.id,
        type=message.type,
        content=message.content,
        sender_id=message.sender_id,
        sender_name=message.sender.full_name,
        sender_email=message.sender.email,
        reply_to_id=message.reply_to_id,
        reply_to=reply_to,
        attachments=[],
        created_at=message.created_at,
        updated_at=message.updated_at
    )
    
    # TODO: Broadcast message via WebSocket
    
    return message_info


@router.post("/conversations/{conversation_id}/attachments/presign", response_model=FileUploadResponse)
async def create_file_upload(
    conversation_id: int,
    file_request: FileUploadRequest,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create presigned URL for file upload."""
    # Check conversation access
    can_access, reason = await messaging_service.rules_service.can_access_conversation(
        db, current_user.id, conversation_id
    )
    if not can_access:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=reason)
    
    # Rate limiting for uploads
    client_ip = get_client_ip(request)
    if not await check_rate_limit(f"upload:{client_ip}", limit=10, window=300):  # 10 uploads per 5 minutes
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many upload requests"
        )
    
    # Generate S3 key
    s3_key = storage_service.generate_s3_key(
        current_user.id, 
        file_request.filename, 
        "chat-attachments"
    )
    
    # Create attachment record
    attachment = Attachment(
        owner_id=current_user.id,
        original_filename=file_request.filename,
        s3_key=s3_key,
        s3_bucket=storage_service.bucket,
        mime_type=file_request.mime_type,
        file_size=file_request.file_size,
        sha256_hash="",  # Will be updated after upload
        virus_status=VirusStatus.PENDING.value,
        upload_ip=client_ip
    )
    
    db.add(attachment)
    await db.commit()
    await db.refresh(attachment)
    
    # Generate presigned upload URL
    upload_data = storage_service.get_presigned_upload_url(s3_key)
    
    return FileUploadResponse(
        upload_url=upload_data["upload_url"],
        s3_key=s3_key,
        expires_at=upload_data["expires_at"],
        attachment_id=attachment.id
    )


@router.post("/attachments/{attachment_id}/scan-complete")
async def attachment_scan_complete(
    attachment_id: int,
    scan_result: AttachmentScanComplete,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark attachment scan as complete (called by worker after virus scan)."""
    # This endpoint would typically be called by a background worker
    # For now, we'll trigger the scan directly
    success = await antivirus_service.scan_attachment(db, attachment_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Scan failed"
        )
    
    return {"message": "Scan completed"}


@router.post("/conversations/{conversation_id}/messages/{message_id}/read")
async def mark_message_read(
    conversation_id: int,
    message_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark specific message as read."""
    read_count = await messaging_service.mark_messages_as_read(
        db, conversation_id, current_user.id, message_id
    )
    
    return {"message": f"Marked {read_count} messages as read"}


@router.post("/conversations/{conversation_id}/read")
async def mark_conversation_read(
    conversation_id: int,
    read_request: MessageReadRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark all messages up to a point as read."""
    read_count = await messaging_service.mark_messages_as_read(
        db, conversation_id, current_user.id, read_request.up_to_message_id
    )
    
    return {"message": f"Marked {read_count} messages as read"}


@router.get("/participants/search")
async def search_conversation_participants(
    query: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get list of users current user can start conversations with."""
    participants = await messaging_service.rules_service.get_allowed_conversation_participants(
        db, current_user.id
    )
    
    # Apply search filter
    if query:
        query_lower = query.lower()
        participants = [
            p for p in participants
            if query_lower in p["full_name"].lower() or 
               query_lower in p["email"].lower()
        ]
    
    return {"participants": participants}