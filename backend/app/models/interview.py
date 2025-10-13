from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.models.base import BaseModel
from app.utils.constants import InterviewStatus


class Interview(BaseModel):
    __tablename__ = "interviews"

    # Participants
    candidate_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    recruiter_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    employer_company_id = Column(
        Integer,
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    recruiter_company_id = Column(
        Integer,
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Workflow relationship
    workflow_id = Column(
        Integer,
        ForeignKey("workflows.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Basic info
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    position_title = Column(String(255), nullable=True)

    # Status and workflow
    status = Column(
        String(50),
        nullable=False,
        default=InterviewStatus.PENDING_SCHEDULE.value,
        index=True,
    )
    interview_type = Column(
        String(50), nullable=False, default="video"
    )  # video, phone, in_person

    # Scheduling (finalized details)
    scheduled_start = Column(DateTime(timezone=True), nullable=True, index=True)
    scheduled_end = Column(DateTime(timezone=True), nullable=True)
    timezone = Column(String(100), nullable=True, default="UTC")
    location = Column(String(500), nullable=True)  # Meeting link or physical address

    # Meeting details
    meeting_url = Column(String(1000), nullable=True)  # Video meeting link
    video_call_type = Column(String(50), nullable=True)  # system_generated, custom_url
    meeting_id = Column(String(255), nullable=True)  # Meeting platform ID
    meeting_password = Column(String(100), nullable=True)

    # Additional data
    duration_minutes = Column(Integer, nullable=True, default=60)
    notes = Column(Text, nullable=True)
    preparation_notes = Column(Text, nullable=True)

    # Workflow tracking
    created_by = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    confirmed_by = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    confirmed_at = Column(DateTime(timezone=True), nullable=True)
    cancelled_by = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    cancellation_reason = Column(Text, nullable=True)

    # Soft delete
    is_deleted = Column(Boolean, nullable=False, default=False, index=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

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
    interview_id = Column(
        Integer,
        ForeignKey("interviews.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Proposal details
    proposed_by = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    proposer_role = Column(
        String(50), nullable=False, index=True
    )  # candidate, employer, recruiter

    # Time slot
    start_datetime = Column(DateTime(timezone=True), nullable=False, index=True)
    end_datetime = Column(DateTime(timezone=True), nullable=False)
    timezone = Column(String(100), nullable=False, default="UTC")

    # Additional details
    location = Column(String(500), nullable=True)
    notes = Column(Text, nullable=True)

    # Status
    status = Column(
        String(50), nullable=False, default="pending", index=True
    )  # pending, accepted, declined, expired

    # Response tracking
    responded_by = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    responded_at = Column(DateTime(timezone=True), nullable=True)
    response_notes = Column(Text, nullable=True)

    # Expiration
    expires_at = Column(DateTime(timezone=True), nullable=True, index=True)

    # Relationships
    interview = relationship("Interview", back_populates="proposals")
    proposer = relationship("User", foreign_keys=[proposed_by])
    responder = relationship("User", foreign_keys=[responded_by])

    def __repr__(self):
        return f"<InterviewProposal(id={self.id}, interview_id={self.interview_id}, proposer_role='{self.proposer_role}', status='{self.status}')>"
