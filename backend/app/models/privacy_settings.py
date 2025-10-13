"""Privacy settings model for user profiles"""

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.schemas.privacy_settings import ProfileVisibility

if TYPE_CHECKING:
    from app.models.user import User


class PrivacySettings(BaseModel):
    """Privacy settings for user profiles"""

    __tablename__ = "privacy_settings"
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

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="privacy_settings")

    def __repr__(self) -> str:
        return f"<PrivacySettings(user_id={self.user_id}, visibility={self.profile_visibility})>"
