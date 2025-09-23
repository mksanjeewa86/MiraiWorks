"""MBTI personality test models."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Dict, Any

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.utils.constants import MBTITestStatus

if TYPE_CHECKING:
    from app.models.user import User


class MBTITest(Base):
    """Model for MBTI personality test results."""

    __tablename__ = "mbti_tests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True
    )
    
    # Test status and results
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=MBTITestStatus.NOT_TAKEN.value, index=True
    )
    mbti_type: Mapped[str | None] = mapped_column(
        String(4), nullable=True, index=True
    )  # e.g., "INTJ"
    
    # Dimension scores (0-100, higher means second trait)
    # E/I: 0 = strong E, 100 = strong I
    # S/N: 0 = strong S, 100 = strong N  
    # T/F: 0 = strong T, 100 = strong F
    # J/P: 0 = strong J, 100 = strong P
    extraversion_introversion_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sensing_intuition_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    thinking_feeling_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    judging_perceiving_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    
    # Test answers and metadata
    answers: Mapped[Dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    test_version: Mapped[str | None] = mapped_column(String(10), nullable=True, default="1.0")
    
    # Timing information
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    
    # Audit fields
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    user: Mapped[User] = relationship("User", back_populates="mbti_test")

    @property
    def is_completed(self) -> bool:
        """Check if the test is completed."""
        return self.status == MBTITestStatus.COMPLETED.value and self.mbti_type is not None

    @property
    def completion_percentage(self) -> int:
        """Get test completion percentage."""
        if self.status == MBTITestStatus.NOT_TAKEN.value:
            return 0
        elif self.status == MBTITestStatus.COMPLETED.value:
            return 100
        else:
            # Calculate based on answers if in progress
            if self.answers:
                total_questions = 60  # Standard MBTI test has 60 questions
                answered = len([q for q in self.answers.values() if q is not None])
                return min(int((answered / total_questions) * 100), 99)
            return 0

    @property
    def dimension_preferences(self) -> Dict[str, str]:
        """Get the preferred trait for each dimension."""
        if not self.is_completed:
            return {}
        
        return {
            "E_I": "I" if self.extraversion_introversion_score > 50 else "E",
            "S_N": "N" if self.sensing_intuition_score > 50 else "S", 
            "T_F": "F" if self.thinking_feeling_score > 50 else "T",
            "J_P": "P" if self.judging_perceiving_score > 50 else "J"
        }

    @property
    def strength_scores(self) -> Dict[str, int]:
        """Get strength scores for each preference (0-50 scale)."""
        if not self.is_completed:
            return {}
        
        return {
            "E_I": abs(self.extraversion_introversion_score - 50),
            "S_N": abs(self.sensing_intuition_score - 50),
            "T_F": abs(self.thinking_feeling_score - 50), 
            "J_P": abs(self.judging_perceiving_score - 50)
        }

    def calculate_mbti_type(self) -> str:
        """Calculate MBTI type from dimension scores."""
        if not all([
            self.extraversion_introversion_score is not None,
            self.sensing_intuition_score is not None,
            self.thinking_feeling_score is not None,
            self.judging_perceiving_score is not None
        ]):
            raise ValueError("All dimension scores must be set to calculate MBTI type")
        
        prefs = self.dimension_preferences
        return f"{prefs['E_I']}{prefs['S_N']}{prefs['T_F']}{prefs['J_P']}"

    def __repr__(self) -> str:
        return f"<MBTITest(id={self.id}, user_id={self.user_id}, type={self.mbti_type}, status={self.status})>"


class MBTIQuestion(Base):
    """Model for MBTI test questions."""

    __tablename__ = "mbti_questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Question details
    question_number: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    dimension: Mapped[str] = mapped_column(String(4), nullable=False, index=True)  # E_I, S_N, T_F, J_P
    direction: Mapped[str] = mapped_column(String(1), nullable=False)  # "+" or "-" 
    
    # Question text in multiple languages
    question_text_en: Mapped[str] = mapped_column(Text, nullable=False)
    question_text_ja: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Answer options
    option_a_en: Mapped[str] = mapped_column(Text, nullable=False)
    option_a_ja: Mapped[str] = mapped_column(Text, nullable=False)
    option_b_en: Mapped[str] = mapped_column(Text, nullable=False)
    option_b_ja: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Scoring (which option corresponds to which trait)
    option_a_trait: Mapped[str] = mapped_column(String(1), nullable=False)  # E, I, S, N, T, F, J, P
    option_b_trait: Mapped[str] = mapped_column(String(1), nullable=False)
    
    # Question metadata
    version: Mapped[str] = mapped_column(String(10), nullable=False, default="1.0")
    is_active: Mapped[bool] = mapped_column(Integer, nullable=False, default=True)
    
    # Audit fields
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __repr__(self) -> str:
        return f"<MBTIQuestion(id={self.id}, number={self.question_number}, dimension={self.dimension})>"