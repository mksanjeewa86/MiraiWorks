from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
from app.utils.constants import InterviewStatus


class Interview(Base):
    __tablename__ = "interviews"

    id = Column(Integer, primary_key=True, index=True)
    
    # Participants
    candidate_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    recruiter_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True) 
    employer_company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    recruiter_company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Basic info
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    position_title = Column(String(255), nullable=True)
    
    # Status and workflow
    status = Column(String(50), nullable=False, default=InterviewStatus.PENDING_SCHEDULE.value, index=True)
    interview_type = Column(String(50), nullable=False, default='video')  # video, phone, in_person
    
    # Scheduling (finalized details)
    scheduled_start = Column(DateTime(timezone=True), nullable=True, index=True)
    scheduled_end = Column(DateTime(timezone=True), nullable=True)
    timezone = Column(String(100), nullable=True, default='UTC')
    location = Column(String(500), nullable=True)  # Meeting link or physical address
    
    # Meeting details
    meeting_url = Column(String(1000), nullable=True)  # Video meeting link
    meeting_id = Column(String(255), nullable=True)  # Meeting platform ID
    meeting_password = Column(String(100), nullable=True)
    
    # Additional data
    duration_minutes = Column(Integer, nullable=True, default=60)
    notes = Column(Text, nullable=True)
    preparation_notes = Column(Text, nullable=True)
    
    # Workflow tracking
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    confirmed_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    confirmed_at = Column(DateTime(timezone=True), nullable=True)
    cancelled_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    cancellation_reason = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    candidate = relationship("User", foreign_keys=[candidate_id])
    recruiter = relationship("User", foreign_keys=[recruiter_id])
    employer_company = relationship("Company", foreign_keys=[employer_company_id])
    recruiter_company = relationship("Company", foreign_keys=[recruiter_company_id])
    creator = relationship("User", foreign_keys=[created_by])
    confirmer = relationship("User", foreign_keys=[confirmed_by])
    canceller = relationship("User", foreign_keys=[cancelled_by])
    
    proposals = relationship("InterviewProposal", back_populates="interview", cascade="all, delete-orphan")
    synced_events = relationship("SyncedEvent", back_populates="interview", cascade="all, delete-orphan")
    meetings = relationship("Meeting", back_populates="interview", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Interview(id={self.id}, title='{self.title}', status='{self.status}', candidate_id={self.candidate_id})>"


class InterviewProposal(Base):
    __tablename__ = "interview_proposals"

    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("interviews.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Proposal details
    proposed_by = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    proposer_role = Column(String(50), nullable=False, index=True)  # candidate, employer, recruiter
    
    # Time slot
    start_datetime = Column(DateTime(timezone=True), nullable=False, index=True)
    end_datetime = Column(DateTime(timezone=True), nullable=False)
    timezone = Column(String(100), nullable=False, default='UTC')
    
    # Additional details
    location = Column(String(500), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Status
    status = Column(String(50), nullable=False, default='pending', index=True)  # pending, accepted, declined, expired
    
    # Response tracking
    responded_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    responded_at = Column(DateTime(timezone=True), nullable=True)
    response_notes = Column(Text, nullable=True)
    
    # Expiration
    expires_at = Column(DateTime(timezone=True), nullable=True, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    interview = relationship("Interview", back_populates="proposals")
    proposer = relationship("User", foreign_keys=[proposed_by])
    responder = relationship("User", foreign_keys=[responded_by])
    
    def __repr__(self):
        return f"<InterviewProposal(id={self.id}, interview_id={self.interview_id}, proposer_role='{self.proposer_role}', status='{self.status}')>"