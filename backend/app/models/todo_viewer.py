"""Todo Viewer model - tracks who can view a todo."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer
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

    # Relationships
    todo: Mapped[Todo] = relationship("Todo", back_populates="viewers")
    user: Mapped[User] = relationship(
        "User", foreign_keys=[user_id], backref="viewed_todos"
    )
    adder: Mapped[User | None] = relationship(
        "User", foreign_keys=[added_by], backref="added_todo_viewers"
    )
