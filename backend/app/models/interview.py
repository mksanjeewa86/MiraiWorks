from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.utils.constants import InterviewStatus


class Interview(BaseModel):
    __tablename__ = "interviews"

    # Participants
    candidate_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    recruiter_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    employer_company_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    recruiter_company_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Workflow relationship
    workflow_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("workflows.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Basic info
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    position_title: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Status and workflow
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=InterviewStatus.PENDING_SCHEDULE.value,
        index=True,
    )
    interview_type: Mapped[str] = mapped_column(
        String(50), nullable=False, default="video"
    )  # video, phone, in_person

    # Scheduling (finalized details)
    scheduled_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    scheduled_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    timezone: Mapped[str | None] = mapped_column(String(100), nullable=True, default="UTC")
    location: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Meeting details
    meeting_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    video_call_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    meeting_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    meeting_password: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Additional data
    duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True, default=60)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    preparation_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Workflow tracking
    created_by: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    confirmed_by: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancelled_by: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancellation_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Soft delete
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships (using noload to prevent lazy loading in async context)
    candidate = relationship("User", foreign_keys=[candidate_id], lazy="noload")
    recruiter = relationship("User", foreign_keys=[recruiter_id], lazy="noload")
    employer_company = relationship(
        "Company", foreign_keys=[employer_company_id], lazy="noload"
    )
    recruiter_company = relationship(
        "Company", foreign_keys=[recruiter_company_id], lazy="noload"
    )
    creator = relationship("User", foreign_keys=[created_by], lazy="noload")
    confirmer = relationship("User", foreign_keys=[confirmed_by], lazy="noload")
    canceller = relationship("User", foreign_keys=[cancelled_by], lazy="noload")

    # Workflow relationship
    workflow = relationship("Workflow", foreign_keys=[workflow_id], lazy="noload")

    proposals = relationship(
        "InterviewProposal",
        back_populates="interview",
        cascade="all, delete-orphan",
        lazy="noload",
    )
    synced_events = relationship(
        "SyncedEvent",
        back_populates="interview",
        cascade="all, delete-orphan",
        lazy="noload",
    )
    meetings = relationship(
        "Meeting",
        back_populates="interview",
        cascade="all, delete-orphan",
        lazy="noload",
    )
    participant_notes = relationship(
        "InterviewNote",
        back_populates="interview",
        cascade="all, delete-orphan",
        lazy="noload",
    )

    def __repr__(self):
        return f"<Interview(id={self.id}, title='{self.title}', status='{self.status}', candidate_id={self.candidate_id})>"


class InterviewProposal(BaseModel):
    __tablename__ = "interview_proposals"
    interview_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("interviews.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Proposal details
    proposed_by: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    proposer_role: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # candidate, employer, recruiter

    # Time slot
    start_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    end_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    timezone: Mapped[str] = mapped_column(String(100), nullable=False, default="UTC")

    # Additional details
    location: Mapped[str | None] = mapped_column(String(500), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Status
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="pending", index=True
    )  # pending, accepted, declined, expired

    # Response tracking
    responded_by: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    responded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    response_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Expiration
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)

    # Relationships
    interview = relationship("Interview", back_populates="proposals")
    proposer = relationship("User", foreign_keys=[proposed_by])
    responder = relationship("User", foreign_keys=[responded_by])

    def __repr__(self):
        return f"<InterviewProposal(id={self.id}, interview_id={self.interview_id}, proposer_role='{self.proposer_role}', status='{self.status}')>"
