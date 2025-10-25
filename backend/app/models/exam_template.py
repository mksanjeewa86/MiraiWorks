"""Exam template models."""

from typing import TYPE_CHECKING

from sqlalchemy import (
    JSON,
    Boolean,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.company import Company
    from app.models.user import User


class ExamTemplate(BaseModel):
    """Exam template model for reusable exam configurations."""

    __tablename__ = "exam_templates"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    exam_type: Mapped[str] = mapped_column(String(50), nullable=False)

    # Template configuration
    time_limit_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_attempts: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    passing_score: Mapped[float | None] = mapped_column(Integer, nullable=True)
    shuffle_questions: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    shuffle_options: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    # Result display settings
    show_score: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    show_correct_answers: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    show_results_immediately: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )

    # Monitoring settings
    enable_monitoring: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    enable_face_recognition: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    require_full_screen: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    # Question template data (stored as JSON)
    questions_template: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Template metadata
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    tags: Mapped[str | None] = mapped_column(
        String(500), nullable=True
    )  # Comma-separated

    # Ownership
    created_by_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    company_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("companies.id"), nullable=True
    )

    # Relationships
    created_by: Mapped["User"] = relationship("User", foreign_keys=[created_by_id])
    company: Mapped["Company | None"] = relationship(
        "Company", foreign_keys=[company_id]
    )
