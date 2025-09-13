from datetime import datetime
from typing import Optional

from pydantic import BaseModel, validator

from app.utils.constants import MessageType


class ConversationParticipant(BaseModel):
    id: int
    email: str
    full_name: str
    company_name: Optional[str]
    is_online: bool = False

    class Config:
        from_attributes = True


class AttachmentInfo(BaseModel):
    id: int
    original_filename: str
    mime_type: str
    file_size: int
    file_size_mb: float
    is_image: bool
    is_document: bool
    is_available: bool
    virus_status: str
    download_url: Optional[str] = None  # Presigned URL for download
    created_at: datetime

    class Config:
        from_attributes = True


class MessageInfo(BaseModel):
    id: int
    type: str
    content: Optional[str]
    is_edited: bool = False
    edited_content: Optional[str] = None
    sender_id: int
    sender_name: str
    sender_email: str
    reply_to_id: Optional[int] = None
    reply_to: Optional["MessageInfo"] = None
    attachments: list[AttachmentInfo] = []
    is_read: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ConversationInfo(BaseModel):
    id: int
    title: Optional[str]
    type: str
    is_active: bool
    participants: list[ConversationParticipant]
    last_message: Optional[MessageInfo] = None
    unread_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ConversationCreate(BaseModel):
    participant_ids: list[int]
    title: Optional[str] = None

    @validator("participant_ids")
    def validate_participants(cls, v):
        if not v:
            raise ValueError("At least one participant is required")
        if len(v) > 50:  # Reasonable limit for group conversations
            raise ValueError("Too many participants")
        return v


class MessageCreate(BaseModel):
    content: str
    type: MessageType = MessageType.TEXT
    reply_to_id: Optional[int] = None

    @validator("content")
    def validate_content(cls, v):
        if not v or not v.strip():
            raise ValueError("Message content cannot be empty")
        if len(v) > 10000:  # 10KB limit
            raise ValueError("Message content too long")
        return v.strip()


class MessageUpdate(BaseModel):
    content: str

    @validator("content")
    def validate_content(cls, v):
        if not v or not v.strip():
            raise ValueError("Message content cannot be empty")
        if len(v) > 10000:
            raise ValueError("Message content too long")
        return v.strip()


class FileUploadRequest(BaseModel):
    filename: str
    mime_type: str
    file_size: int

    @validator("filename")
    def validate_filename(cls, v):
        if not v or not v.strip():
            raise ValueError("Filename is required")
        # Sanitize filename
        safe_chars = set(
            "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-_ "
        )
        if not all(c in safe_chars for c in v):
            raise ValueError("Filename contains invalid characters")
        return v.strip()

    @validator("file_size")
    def validate_file_size(cls, v):
        max_size = 100 * 1024 * 1024  # 100MB
        if v > max_size:
            raise ValueError(f"File size exceeds limit of {max_size // (1024*1024)}MB")
        if v <= 0:
            raise ValueError("File size must be positive")
        return v


class FileUploadResponse(BaseModel):
    upload_url: str
    s3_key: str
    expires_at: str
    attachment_id: int


class ConversationListRequest(BaseModel):
    search: Optional[str] = None
    limit: int = 20
    offset: int = 0

    @validator("limit")
    def validate_limit(cls, v):
        if v > 100:
            raise ValueError("Limit cannot exceed 100")
        return v


class MessageListRequest(BaseModel):
    limit: int = 50
    before_id: Optional[int] = None

    @validator("limit")
    def validate_limit(cls, v):
        if v > 100:
            raise ValueError("Limit cannot exceed 100")
        return v


class MessageReadRequest(BaseModel):
    up_to_message_id: int


class ConversationListResponse(BaseModel):
    conversations: list[ConversationInfo]
    total: int
    has_more: bool


class MessageListResponse(BaseModel):
    messages: list[MessageInfo]
    has_more: bool
    conversation_id: int


class TypingIndicator(BaseModel):
    conversation_id: int
    is_typing: bool


class AttachmentScanComplete(BaseModel):
    attachment_id: int
    virus_status: str
    is_available: bool
    scan_result: Optional[str] = None


# Update forward references
MessageInfo.model_rebuild()
ConversationInfo.model_rebuild()
