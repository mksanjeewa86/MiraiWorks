from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class DirectMessageBase(BaseModel):
    content: str = Field(..., min_length=1, description="Message content cannot be empty")
    type: str = "text"
    file_url: Optional[str] = None
    file_name: Optional[str] = None
    file_size: Optional[int] = None
    file_type: Optional[str] = None


class DirectMessageCreate(DirectMessageBase):
    recipient_id: int
    reply_to_id: Optional[int] = None


class DirectMessageInfo(DirectMessageBase):
    id: int
    sender_id: int
    recipient_id: int
    sender_name: str
    recipient_name: str
    sender_email: str
    recipient_email: str
    is_read: bool
    reply_to_id: Optional[int] = None
    created_at: datetime
    read_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ConversationSummary(BaseModel):
    """Summary of messages between two users."""

    other_user_id: int
    other_user_name: str
    other_user_email: str
    other_user_company: Optional[str] = None
    last_message: Optional[DirectMessageInfo] = None
    unread_count: int
    last_activity: datetime

    model_config = ConfigDict(from_attributes=True)


class MessageSearchRequest(BaseModel):
    query: Optional[str] = None  # Search in message content and sender names
    with_user_id: Optional[int] = None  # Filter messages with specific user
    limit: int = 50
    offset: int = 0


class MessageListResponse(BaseModel):
    messages: list[DirectMessageInfo]
    total: int
    has_more: bool


class ConversationListResponse(BaseModel):
    conversations: list[ConversationSummary]
    total: int


class MessageReadRequest(BaseModel):
    message_ids: list[int]
