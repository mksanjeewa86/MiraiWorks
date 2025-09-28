"""Connection invitation model for managing connection requests between users."""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, Enum as SQLEnum, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class InvitationStatus(str, Enum):
    """Status of connection invitations."""
    PENDING = "pending"     # Invitation sent, awaiting response
    ACCEPTED = "accepted"   # Invitation accepted (should create connection)
    REJECTED = "rejected"   # Invitation declined
    CANCELLED = "cancelled" # Sender cancelled the invitation


class ConnectionInvitation(Base):
    """Model for connection invitations between users."""

    __tablename__ = "connection_invitations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Invitation participants
    sender_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    receiver_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Invitation details
    status: Mapped[str] = mapped_column(
        SQLEnum(InvitationStatus),
        nullable=False,
        default=InvitationStatus.PENDING
    )

    # Optional message
    message: Mapped[str] = mapped_column(String(500), nullable=True)

    # Timestamps
    sent_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )
    responded_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    # Relationships
    sender: Mapped["User"] = relationship(
        "User",
        foreign_keys=[sender_id],
        back_populates="sent_invitations"
    )
    receiver: Mapped["User"] = relationship(
        "User",
        foreign_keys=[receiver_id],
        back_populates="received_invitations"
    )

    # Ensure no duplicate invitations
    __table_args__ = (
        UniqueConstraint('sender_id', 'receiver_id', name='unique_connection_invitation'),
    )

    def __repr__(self) -> str:
        return (
            f"<ConnectionInvitation(id={self.id}, "
            f"sender_id={self.sender_id}, "
            f"receiver_id={self.receiver_id}, "
            f"status={self.status})>"
        )