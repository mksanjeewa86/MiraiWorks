from datetime import datetime, timedelta

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Table,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.db_types import CompatLONGTEXT as LONGTEXT

from .base import Base

# Association table for meeting participants
meeting_participants = Table(
    "meeting_participants",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column(
        "meeting_id",
        Integer,
        ForeignKey("meetings.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column(
        "user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    ),
    Column("role", String(20), nullable=False),  # ParticipantRole
    Column("status", String(20), nullable=False, default="invited"),
    Column("joined_at", DateTime, nullable=True),
    Column("left_at", DateTime, nullable=True),
    Column("can_record", Boolean, nullable=False, default=False),
    Column(
        "recording_consent", Boolean, nullable=True
    ),  # True/False/None for not decided
    Column("created_at", DateTime, nullable=False, default=datetime.utcnow),
    Column(
        "updated_at",
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    ),
    UniqueConstraint("meeting_id", "user_id", name="unique_meeting_user"),
    Index("idx_meeting_participants_meeting", "meeting_id"),
    Index("idx_meeting_participants_user", "user_id"),
)


class Meeting(Base):
    __tablename__ = "meetings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    interview_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("interviews.id", ondelete="SET NULL"), nullable=True
    )

    # Meeting metadata
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    meeting_type: Mapped[str] = mapped_column(String(20), nullable=False)  # MeetingType
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="scheduled")

    # Scheduling
    scheduled_start: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    scheduled_end: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    actual_start: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    actual_end: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # WebRTC and access
    room_id: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    access_code: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )  # Optional PIN

    # Recording settings
    recording_enabled: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    recording_status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="not_started"
    )
    recording_consent_required: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True
    )

    # Transcription and summary
    transcription_enabled: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    auto_summary: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Company context for RBAC
    company_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )

    # Metadata
    created_by: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    interview = relationship("Interview", back_populates="meetings")
    company = relationship("Company")
    creator = relationship("User", foreign_keys=[created_by])
    participants = relationship(
        "User", secondary=meeting_participants, back_populates="meetings"
    )
    recordings = relationship(
        "MeetingRecording", back_populates="meeting", cascade="all, delete-orphan"
    )
    transcripts = relationship(
        "MeetingTranscript", back_populates="meeting", cascade="all, delete-orphan"
    )
    summaries = relationship(
        "MeetingSummary", back_populates="meeting", cascade="all, delete-orphan"
    )

    # Indexes
    __table_args__ = (
        Index("idx_meetings_room_id", "room_id"),
        Index("idx_meetings_company", "company_id"),
        Index("idx_meetings_status", "status"),
        Index("idx_meetings_scheduled_start", "scheduled_start"),
        Index("idx_meetings_interview", "interview_id"),
    )

    @property
    def duration_minutes(self) -> int | None:
        """Calculate actual meeting duration in minutes"""
        if self.actual_start and self.actual_end:
            return int((self.actual_end - self.actual_start).total_seconds() / 60)
        return None

    @property
    def is_active(self) -> bool:
        """Check if meeting is currently active"""
        return self.status in ["starting", "in_progress"]

    @property
    def can_join(self) -> bool:
        """Check if meeting can be joined now"""
        now = datetime.utcnow()
        # Allow joining 15 minutes before scheduled start and up to 2 hours after
        start_window = self.scheduled_start - timedelta(minutes=15)
        end_window = self.scheduled_start + timedelta(hours=2)
        return start_window <= now <= end_window and self.status in [
            "scheduled",
            "starting",
            "in_progress",
        ]


class MeetingRecording(Base):
    __tablename__ = "meeting_recordings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    meeting_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False
    )

    # Recording metadata
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)  # bytes
    duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Storage details
    storage_path: Mapped[str] = mapped_column(String(500), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)

    # Processing status
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="processing"
    )
    processing_started_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )
    processing_completed_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )
    processing_error: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Access control
    is_public: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    access_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )

    # Metadata
    recorded_by: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    meeting = relationship("Meeting", back_populates="recordings")
    recorded_by_user = relationship("User", foreign_keys=[recorded_by])

    # Indexes
    __table_args__ = (
        Index("idx_meeting_recordings_meeting", "meeting_id"),
        Index("idx_meeting_recordings_status", "status"),
        Index("idx_meeting_recordings_created", "created_at"),
    )


class MeetingTranscript(Base):
    __tablename__ = "meeting_transcripts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    meeting_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False
    )
    recording_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("meeting_recordings.id", ondelete="SET NULL"), nullable=True
    )

    # Transcript content
    transcript_text: Mapped[str] = mapped_column(LONGTEXT, nullable=False)
    transcript_json: Mapped[str | None] = mapped_column(
        LONGTEXT, nullable=True
    )  # Structured data with timestamps, speakers
    language: Mapped[str] = mapped_column(String(10), nullable=False, default="ja")
    confidence_score: Mapped[float | None] = mapped_column(nullable=True)

    # Processing details
    stt_service: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # Which STT service used
    processing_duration_seconds: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )
    word_count: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Speaker identification
    speaker_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    speakers_identified: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )

    # Status
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="processing"
    )
    processing_error: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Metadata
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    meeting = relationship("Meeting", back_populates="transcripts")
    recording = relationship("MeetingRecording")

    # Indexes
    __table_args__ = (
        Index("idx_meeting_transcripts_meeting", "meeting_id"),
        Index("idx_meeting_transcripts_recording", "recording_id"),
        Index("idx_meeting_transcripts_status", "status"),
    )


class MeetingSummary(Base):
    __tablename__ = "meeting_summaries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    meeting_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False
    )
    transcript_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("meeting_transcripts.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Summary content
    summary_text: Mapped[str] = mapped_column(Text, nullable=False)
    key_points: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )  # JSON array of key points
    action_items: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )  # JSON array of action items
    sentiment_analysis: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )  # JSON sentiment data

    # Generation details
    ai_model: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # Which AI model used
    prompt_version: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # For tracking prompt changes
    generation_duration_seconds: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )

    # Quality metrics
    confidence_score: Mapped[float | None] = mapped_column(nullable=True)
    summary_length_words: Mapped[int | None] = mapped_column(Integer, nullable=True)
    compression_ratio: Mapped[float | None] = mapped_column(
        nullable=True
    )  # summary_length / transcript_length

    # Status
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="processing"
    )
    processing_error: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Access control
    is_final: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True
    )  # vs draft
    reviewed_by: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Metadata
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    meeting = relationship("Meeting", back_populates="summaries")
    transcript = relationship("MeetingTranscript")
    reviewer = relationship("User", foreign_keys=[reviewed_by])

    # Indexes
    __table_args__ = (
        Index("idx_meeting_summaries_meeting", "meeting_id"),
        Index("idx_meeting_summaries_transcript", "transcript_id"),
        Index("idx_meeting_summaries_status", "status"),
        Index("idx_meeting_summaries_final", "is_final"),
    )
