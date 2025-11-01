from sqlalchemy import ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class InterviewNote(BaseModel):
    """Private notes that interview participants can add for themselves."""

    __tablename__ = "interview_notes"

    # References
    interview_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("interviews.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    participant_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Note content
    content: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    interview = relationship("Interview", back_populates="participant_notes")
    participant = relationship("User")

    # Ensure one note per participant per interview
    __table_args__ = (
        UniqueConstraint(
            "interview_id", "participant_id", name="uq_interview_participant_note"
        ),
    )
