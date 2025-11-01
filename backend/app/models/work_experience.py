"""Work Experience model for user profiles."""

from datetime import date

from sqlalchemy import Boolean, Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class ProfileWorkExperience(BaseModel):
    """Work experience entries for user profiles."""

    __tablename__ = "profile_work_experiences"
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Company Information
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    company_logo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Position Information
    position_title: Mapped[str] = mapped_column(String(255), nullable=False)
    employment_type: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )  # Full-time, Part-time, Contract, etc.
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Duration
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_current: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Description
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Skills used (stored as comma-separated values for now, could be normalized later)
    skills: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Display Order
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    user = relationship("User", back_populates="work_experiences")

    def __repr__(self):
        return f"<WorkExperience(id={self.id}, user_id={self.user_id}, company='{self.company_name}', position='{self.position_title}')>"
