"""
System Update Model

System-wide updates that are visible to all users without creating individual notification records.
Only system administrators can create these updates.
"""

from typing import TYPE_CHECKING, Optional

from sqlalchemy import JSON, Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.user import User


class SystemUpdate(BaseModel):
    """
    System-wide update announcements.

    These are visible to all users and are not tied to individual user notification records.
    Only system administrators can create and manage these updates.
    """

    __tablename__ = "system_updates"
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    tags: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Track who created this update
    created_by_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    # Relationships
    created_by: Mapped[Optional["User"]] = relationship(
        "User", back_populates="system_updates_created", foreign_keys=[created_by_id]
    )

    def __repr__(self) -> str:
        return f"<SystemUpdate {self.id}: {self.title}>"
