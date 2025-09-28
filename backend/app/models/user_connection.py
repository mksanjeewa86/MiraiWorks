"""Simple user connection model."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Boolean, UniqueConstraint, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class UserConnection(Base):
    """Simple user-to-user connections."""

    __tablename__ = "user_connections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # The two users in this connection
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    connected_user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Simple active status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Creation tracking
    creation_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="manual",
        comment="Type of creation: 'automatic' or 'manual'"
    )
    created_by: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="User who created this connection (NULL for automatic creation)"
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="sent_connections"
    )
    connected_user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[connected_user_id],
        back_populates="received_connections"
    )
    creator: Mapped["User | None"] = relationship(
        "User",
        foreign_keys=[created_by],
        post_update=True
    )

    # Ensure no duplicate connections
    __table_args__ = (
        UniqueConstraint('user_id', 'connected_user_id', name='unique_user_connection'),
    )

    def __repr__(self) -> str:
        return f"<UserConnection(user_id={self.user_id}, connected_user_id={self.connected_user_id}, active={self.is_active}, type={self.creation_type})>"