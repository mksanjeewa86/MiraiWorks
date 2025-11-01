"""Job Preference model for user profiles."""

from datetime import date

from sqlalchemy import Boolean, Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class JobPreference(BaseModel):
    """Job preference settings for user profiles (mainly for candidates)."""

    __tablename__ = "profile_job_preferences"
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        unique=True,  # One preference record per user
    )

    # Job Type Preferences (comma-separated: Full-time, Part-time, Contract, Freelance)
    desired_job_types: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Salary Expectations
    desired_salary_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    desired_salary_max: Mapped[int | None] = mapped_column(Integer, nullable=True)
    salary_currency: Mapped[str] = mapped_column(
        String(10), default="USD", nullable=False
    )  # USD, JPY, EUR, etc.
    salary_period: Mapped[str] = mapped_column(
        String(20), default="yearly", nullable=False
    )  # yearly, monthly, hourly

    # Location Preferences
    willing_to_relocate: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    preferred_locations: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )  # Comma-separated list of locations

    # Work Mode Preferences (comma-separated: Remote, Hybrid, Onsite)
    work_mode_preferences: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Availability
    available_from: Mapped[date | None] = mapped_column(Date, nullable=True)
    notice_period_days: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Job Search Status
    job_search_status: Mapped[str] = mapped_column(
        String(50), default="not_looking", nullable=False
    )  # actively_looking, open_to_opportunities, not_looking

    # Additional Preferences
    preferred_industries: Mapped[str | None] = mapped_column(Text, nullable=True)
    preferred_company_sizes: Mapped[str | None] = mapped_column(Text, nullable=True)
    other_preferences: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )  # Free text for additional preferences

    # Relationships
    user = relationship("User", back_populates="job_preference")

    def __repr__(self):
        return f"<JobPreference(id={self.id}, user_id={self.user_id}, status='{self.job_search_status}')>"
