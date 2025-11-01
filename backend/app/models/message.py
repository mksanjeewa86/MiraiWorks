from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.utils.constants import MessageType


class Message(BaseModel):
    """Message between two users."""

    __tablename__ = "messages"
    sender_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    recipient_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    type: Mapped[str] = mapped_column(
        String(50), nullable=False, default=MessageType.TEXT.value, index=True
    )
    is_read: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, index=True
    )
    is_deleted_by_sender: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    is_deleted_by_recipient: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    reply_to_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("messages.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    file_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    file_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    file_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    file_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    read_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    sender = relationship("User", foreign_keys=[sender_id])
    recipient = relationship("User", foreign_keys=[recipient_id])
    reply_to = relationship(
        "Message", remote_side="messages.c.id", foreign_keys=[reply_to_id]
    )
    attachments = relationship("Attachment", back_populates="message")

    def __repr__(self):
        return f"<Message(id={self.id}, sender_id={self.sender_id}, recipient_id={self.recipient_id})>"

    def is_visible_to_user(self, user_id: int) -> bool:
        """Check if message is visible to the given user."""
        if user_id == self.sender_id:
            return not self.is_deleted_by_sender
        elif user_id == self.recipient_id:
            return not self.is_deleted_by_recipient
        return False
