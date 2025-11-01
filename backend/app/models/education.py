"""Education model for user profiles."""

from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class ProfileEducation(BaseModel):
    """Education entries for user profiles."""

    __tablename__ = "profile_educations"
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Institution Information
    institution_name: Mapped[str] = mapped_column(String(255), nullable=False)
    institution_logo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Degree Information
    degree_type: Mapped[str] = mapped_column(String(100), nullable=False)
    field_of_study: Mapped[str] = mapped_column(String(255), nullable=False)

    # Duration
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    graduation_year: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Academic Performance
    gpa: Mapped[Decimal | None] = mapped_column(Numeric(3, 2), nullable=True)
    gpa_max: Mapped[Decimal | None] = mapped_column(Numeric(3, 2), nullable=True)

    # Additional Information
    honors_awards: Mapped[str | None] = mapped_column(Text, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Display Order
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    user = relationship("User", back_populates="educations")

    def __repr__(self):
        return f"<Education(id={self.id}, user_id={self.user_id}, institution='{self.institution_name}', degree='{self.degree_type}')>"
