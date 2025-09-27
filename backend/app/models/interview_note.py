from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class InterviewNote(Base):
    """Private notes that interview participants can add for themselves."""
    __tablename__ = "interview_notes"

    id = Column(Integer, primary_key=True, index=True)

    # References
    interview_id = Column(
        Integer,
        ForeignKey("interviews.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    participant_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Note content
    content = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # Relationships
    interview = relationship("Interview", back_populates="participant_notes")
    participant = relationship("User")

    # Ensure one note per participant per interview
    __table_args__ = (
        UniqueConstraint("interview_id", "participant_id", name="uq_interview_participant_note"),
    )
