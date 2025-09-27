"""TodoViewer model for many-to-many viewers relationship."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.todo import Todo
    from app.models.user import User


class TodoViewer(Base):
    __tablename__ = "todo_viewers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    todo_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("todos.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    added_by: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    added_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )

    # Relationships
    todo: Mapped[Todo] = relationship("Todo", back_populates="viewers")
    user: Mapped[User] = relationship("User", foreign_keys=[user_id])
    added_by_user: Mapped[User | None] = relationship("User", foreign_keys=[added_by])

    def __repr__(self):
        return f"<TodoViewer(todo_id={self.todo_id}, user_id={self.user_id})>"
