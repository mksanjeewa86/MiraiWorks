from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.utils.datetime_utils import get_utc_now

if TYPE_CHECKING:
    from app.models.todo import Todo
    from app.models.user import User


class TodoViewerMemo(BaseModel):
    __tablename__ = "todo_viewer_memos"
    __table_args__ = (
        UniqueConstraint('todo_id', 'user_id', name='uq_todo_viewer_memo'),
    )

    todo_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("todos.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    memo: Mapped[str | None] = mapped_column(Text, nullable=True)

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
    todo: Mapped[Todo] = relationship("Todo", backref="viewer_memos")
    user: Mapped[User] = relationship("User", foreign_keys=[user_id], backref="todo_viewer_memos")
    deleter: Mapped[User | None] = relationship(
        "User", foreign_keys=[deleted_by], backref="deleted_viewer_memos"
    )
