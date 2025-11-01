from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int | None] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(
        String(50), nullable=False, unique=True, index=True
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    user_roles = relationship(
        "UserRole", back_populates="role", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Role(id={self.id}, name='{self.name}')>"


class UserRole(Base):
    __tablename__ = "user_roles"

    id: Mapped[int | None] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    scope: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )  # Additional scoping (e.g., company-specific)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="user_roles")
    role = relationship("Role", back_populates="user_roles")

    def __repr__(self):
        return f"<UserRole(user_id={self.user_id}, role_id={self.role_id}, scope='{self.scope}')>"
