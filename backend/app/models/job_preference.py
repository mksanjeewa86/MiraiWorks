"""Job Preference model for user profiles."""

from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.models.base import TimestampMixin
from app.database import Base


class JobPreference(Base, TimestampMixin):
    """Job preference settings for user profiles (mainly for candidates)."""

    __tablename__ = "profile_job_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        unique=True,  # One preference record per user
    )

    # Job Type Preferences (comma-separated: Full-time, Part-time, Contract, Freelance)
    desired_job_types = Column(Text, nullable=True)

    # Salary Expectations
    desired_salary_min = Column(Integer, nullable=True)  # Minimum salary
    desired_salary_max = Column(Integer, nullable=True)  # Maximum salary
    salary_currency = Column(String(10), default="USD", nullable=False)  # USD, JPY, EUR, etc.
    salary_period = Column(String(20), default="yearly", nullable=False)  # yearly, monthly, hourly

    # Location Preferences
    willing_to_relocate = Column(Boolean, default=False, nullable=False)
    preferred_locations = Column(Text, nullable=True)  # Comma-separated list of locations

    # Work Mode Preferences (comma-separated: Remote, Hybrid, Onsite)
    work_mode_preferences = Column(Text, nullable=True)

    # Availability
    available_from = Column(Date, nullable=True)  # When can start working
    notice_period_days = Column(Integer, nullable=True)  # Notice period in days

    # Job Search Status
    job_search_status = Column(
        String(50), default="not_looking", nullable=False
    )  # actively_looking, open_to_opportunities, not_looking

    # Additional Preferences
    preferred_industries = Column(Text, nullable=True)  # Comma-separated
    preferred_company_sizes = Column(Text, nullable=True)  # Startup, SME, Enterprise
    other_preferences = Column(Text, nullable=True)  # Free text for additional preferences

    # Relationships
    user = relationship("User", back_populates="job_preference")

    def __repr__(self):
        return f"<JobPreference(id={self.id}, user_id={self.user_id}, status='{self.job_search_status}')>"
