"""Privacy settings model for user profiles"""

from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base
import enum


class ProfileVisibility(str, enum.Enum):
    """Profile visibility levels"""
    PUBLIC = "public"
    RECRUITERS_ONLY = "recruiters"
    PRIVATE = "private"


class PrivacySettings(Base):
    """Privacy settings for user profiles"""

    __tablename__ = "privacy_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True
    )

    # Profile Visibility
    profile_visibility: Mapped[str] = mapped_column(
        String(20),
        default=ProfileVisibility.PUBLIC.value,
        nullable=False
    )

    # Searchability
    searchable: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Contact Information Visibility
    show_email: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    show_phone: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Profile Section Visibility
    show_work_experience: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    show_education: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    show_skills: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    show_certifications: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    show_projects: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    show_resume: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="privacy_settings")

    def __repr__(self) -> str:
        return f"<PrivacySettings(user_id={self.user_id}, visibility={self.profile_visibility})>"
