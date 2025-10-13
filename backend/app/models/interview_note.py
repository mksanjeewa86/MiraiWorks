from sqlalchemy import Column, ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class InterviewNote(BaseModel):
    """Private notes that interview participants can add for themselves."""

    __tablename__ = "interview_notes"

    # References
    interview_id = Column(
        Integer,
        ForeignKey("interviews.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    participant_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Note content
    content = Column(Text, nullable=True)

    # Relationships
    interview = relationship("Interview", back_populates="participant_notes")
    participant = relationship("User")

    # Ensure one note per participant per interview
    __table_args__ = (
        UniqueConstraint(
            "interview_id", "participant_id", name="uq_interview_participant_note"
        ),
    )
