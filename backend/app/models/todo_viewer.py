"""Todo Viewer model - tracks who can view a todo."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.todo import Todo
    from app.models.user import User


class TodoViewer(BaseModel):
    """Model for todo viewers - users who can view but not edit a todo.

    Viewers have read-only access to a todo. Only the creator can add/remove viewers.
    Viewers cannot see other viewers or the assignee (if different from themselves).
    """

    __tablename__ = "todo_viewers"

    todo_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("todos.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    added_by: Mapped[int] = mapped_column(
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
    todo: Mapped[Todo] = relationship("Todo", back_populates="viewers")
    user: Mapped[User] = relationship(
        "User", foreign_keys=[user_id], backref="viewed_todos"
    )
    adder: Mapped[User | None] = relationship(
        "User", foreign_keys=[added_by], backref="added_todo_viewers"
    )
    deleter: Mapped[User | None] = relationship(
        "User", foreign_keys=[deleted_by], backref="deleted_todo_viewers"
    )
