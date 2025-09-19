from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.utils.constants import TodoStatus

from .base import Base

if TYPE_CHECKING:
    from .user import User


class Todo(Base):
    __tablename__ = "todos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    owner_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    created_by: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    last_updated_by: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=TodoStatus.PENDING.value, index=True
    )
    priority: Mapped[str | None] = mapped_column(String(20), nullable=True)
    due_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expired_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    owner: Mapped[User] = relationship("User", foreign_keys=[owner_id], backref="todos")
    creator: Mapped[User | None] = relationship(
        "User", foreign_keys=[created_by], backref="created_todos"
    )
    updater: Mapped[User | None] = relationship(
        "User", foreign_keys=[last_updated_by], backref="updated_todos"
    )

    @property
    def is_completed(self) -> bool:
        return self.status == TodoStatus.COMPLETED.value

    @property
    def is_expired(self) -> bool:
        if self.status == TodoStatus.COMPLETED.value:
            return False
        if self.expired_at:
            return True
        if self.due_date:
            return self.due_date < datetime.utcnow()
        return False

    def mark_completed(self) -> None:
        self.status = TodoStatus.COMPLETED.value
        self.completed_at = datetime.utcnow()
        self.expired_at = None

    def mark_pending(self) -> None:
        self.status = TodoStatus.PENDING.value
        self.completed_at = None
        self.expired_at = None
