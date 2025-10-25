"""Recruiter profile model"""

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class RecruiterProfile(BaseModel):
    """Recruiter profile with recruitment focus and specializations"""

    __tablename__ = "recruiter_profiles"
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )

    # Professional info
    years_of_experience: Mapped[int | None] = mapped_column(Integer, nullable=True)
    specializations: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )  # Comma-separated or JSON
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Company information (if different from user.company)
    company_description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Recruitment focus
    industries: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )  # Industries they recruit for
    job_types: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )  # Full-time, Contract, etc.
    locations: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )  # Locations they hire for
    experience_levels: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )  # Junior, Mid, Senior, etc.

    # Contact preferences
    calendar_link: Mapped[str | None] = mapped_column(String(500), nullable=True)
    linkedin_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Activity stats (can be updated periodically)
    jobs_posted: Mapped[int | None] = mapped_column(Integer, default=0, nullable=True)
    candidates_placed: Mapped[int | None] = mapped_column(
        Integer, default=0, nullable=True
    )
    active_openings: Mapped[int | None] = mapped_column(
        Integer, default=0, nullable=True
    )

    # Display order for custom sections
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    user = relationship("User", back_populates="recruiter_profile")
