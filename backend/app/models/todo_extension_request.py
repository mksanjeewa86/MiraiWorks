"""Todo extension request model for tracking due date extension requests."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.utils.constants import ExtensionRequestStatus

if TYPE_CHECKING:
    from app.models.todo import Todo
    from app.models.user import User


class TodoExtensionRequest(BaseModel):
    """Model for todo due date extension requests."""

    __tablename__ = "todo_extension_requests"

    todo_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("todos.id", ondelete="CASCADE"), nullable=False, index=True
    )
    requested_by_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    creator_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Extension details
    requested_due_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)

    # Request status and workflow
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=ExtensionRequestStatus.PENDING.value,
        index=True,
    )

    # Response details
    response_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    responded_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    responded_by_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    # Soft delete fields
    is_deleted: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, index=True
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    deleted_by: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    # Relationships
    todo: Mapped[Todo] = relationship("Todo", back_populates="extension_requests")
    requested_by: Mapped[User] = relationship(
        "User", foreign_keys=[requested_by_id], back_populates="requested_extensions"
    )
    creator: Mapped[User] = relationship(
        "User", foreign_keys=[creator_id], back_populates="extension_requests_to_review"
    )
    responded_by: Mapped[User | None] = relationship(
        "User", foreign_keys=[responded_by_id], back_populates="extension_responses"
    )
    deleter: Mapped[User | None] = relationship(
        "User", foreign_keys=[deleted_by], backref="deleted_extension_requests"
    )

    def __repr__(self) -> str:
        return f"<TodoExtensionRequest(id={self.id}, todo_id={self.todo_id}, status={self.status})>"
