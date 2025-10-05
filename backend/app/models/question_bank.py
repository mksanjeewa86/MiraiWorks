"""Question bank models for reusable exam questions."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.utils.datetime_utils import get_utc_now

if TYPE_CHECKING:
    from app.models.company import Company
    from app.models.exam import ExamQuestion
    from app.models.user import User


class QuestionBank(Base):
    """Reusable question pools for exams."""

    __tablename__ = "question_banks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Classification
    exam_type: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # "spi", "skill", "aptitude", etc.
    category: Mapped[str | None] = mapped_column(
        String(100), nullable=True, index=True
    )  # "verbal", "math", "logic", "programming"
    difficulty: Mapped[str | None] = mapped_column(
        String(20), nullable=True
    )  # "easy", "medium", "hard", "mixed"

    # Access control
    is_public: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, index=True
    )  # True = global bank, False = company-specific
    company_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("companies.id", ondelete="SET NULL"), nullable=True, index=True
    )  # NULL = global bank

    # Metadata
    created_by: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=get_utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=get_utc_now,
        onupdate=get_utc_now,
        nullable=False,
    )

    # Relationships
    company: Mapped["Company | None"] = relationship(
        "Company", foreign_keys=[company_id]
    )
    creator: Mapped["User"] = relationship("User", foreign_keys=[created_by])
    questions: Mapped[list["QuestionBankItem"]] = relationship(
        "QuestionBankItem", back_populates="bank", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<QuestionBank(id={self.id}, name='{self.name}', exam_type='{self.exam_type}')>"


class QuestionBankItem(Base):
    """Individual questions in a question bank."""

    __tablename__ = "question_bank_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    bank_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("question_banks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Question content
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    question_type: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # Uses QuestionType enum
    order_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Scoring and difficulty
    points: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    difficulty: Mapped[str | None] = mapped_column(
        String(20), nullable=True, index=True
    )  # "easy", "medium", "hard"

    # Multiple choice / Single choice options
    options: Mapped[dict | None] = mapped_column(
        JSON, nullable=True
    )  # {"A": "Option 1", "B": "Option 2"}
    correct_answers: Mapped[list | None] = mapped_column(
        JSON, nullable=True
    )  # ["A", "B"] for multiple choice, ["A"] for single

    # Explanation and metadata
    explanation: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )  # Explanation of correct answer
    tags: Mapped[list | None] = mapped_column(
        JSON, nullable=True
    )  # ["programming", "python", "loops"] for categorization

    # Text input / Essay settings
    max_length: Mapped[int | None] = mapped_column(Integer, nullable=True)
    min_length: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Rating settings
    rating_scale: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )  # 1-5, 1-10, etc.

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=get_utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=get_utc_now,
        onupdate=get_utc_now,
        nullable=False,
    )

    # Relationships
    bank: Mapped["QuestionBank"] = relationship(
        "QuestionBank", back_populates="questions"
    )
    used_in_exams: Mapped[list["ExamQuestion"]] = relationship(
        "ExamQuestion",
        foreign_keys="ExamQuestion.source_question_id",
        back_populates="source_question",
    )

    def __repr__(self) -> str:
        return f"<QuestionBankItem(id={self.id}, bank_id={self.bank_id}, type='{self.question_type}')>"
