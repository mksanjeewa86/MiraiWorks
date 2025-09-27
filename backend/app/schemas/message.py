from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class MessageBase(BaseModel):
    content: str = Field(
        ..., min_length=1, description="Message content cannot be empty"
    )
    type: str = "text"
    file_url: str | None = None
    file_name: str | None = None
    file_size: int | None = None
    file_type: str | None = None


class MessageCreate(MessageBase):
    recipient_id: int
    reply_to_id: int | None = None


class MessageInfo(MessageBase):
    id: int
    sender_id: int
    recipient_id: int
    sender_name: str
    recipient_name: str
    sender_email: str
    recipient_email: str
    is_read: bool
    reply_to_id: int | None = None
    created_at: datetime
    read_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class ConversationSummary(BaseModel):
    """Summary of messages between two users."""

    other_user_id: int
    other_user_name: str
    other_user_email: str
    other_user_company: str | None = None
    last_message: MessageInfo | None = None
    unread_count: int
    last_activity: datetime

    model_config = ConfigDict(from_attributes=True)


class MessageSearchRequest(BaseModel):
    query: str | None = None  # Search in message content and sender names
    with_user_id: int | None = None  # Filter messages with specific user
    limit: int = 50
    offset: int = 0


class MessageListResponse(BaseModel):
    messages: list[MessageInfo]
    total: int
    has_more: bool


class ConversationListResponse(BaseModel):
    conversations: list[ConversationSummary]
    total: int


class MessageReadRequest(BaseModel):
    message_ids: list[int]
