from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.mysql import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base
from app.models.base import BaseModel


class VideoCall(BaseModel):
    __tablename__ = "video_calls"

    # Related entities
    job_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("positions.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    interview_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("interviews.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    interviewer_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    candidate_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Call details
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="scheduled")
    room_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    recording_url: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Transcription settings
    transcription_enabled: Mapped[bool | None] = mapped_column(Boolean, default=True)
    transcription_language: Mapped[str | None] = mapped_column(String(10), default="ja")

    # Relationships
    job = relationship("Position", foreign_keys=[job_id], lazy="noload")
    interview = relationship("Interview", foreign_keys=[interview_id], lazy="noload")
    interviewer = relationship("User", foreign_keys=[interviewer_id], lazy="noload")
    candidate = relationship("User", foreign_keys=[candidate_id], lazy="noload")
    participants = relationship(
        "CallParticipant", back_populates="video_call", cascade="all, delete-orphan"
    )
    recording_consents = relationship(
        "RecordingConsent", back_populates="video_call", cascade="all, delete-orphan"
    )
    transcriptions = relationship(
        "CallTranscription", back_populates="video_call", cascade="all, delete-orphan"
    )
    transcription_segments = relationship(
        "TranscriptionSegment",
        back_populates="video_call",
        cascade="all, delete-orphan",
    )

    # Indexes
    __table_args__ = (
        Index("idx_video_calls_scheduled_at", "scheduled_at"),
        Index("idx_video_calls_status", "status"),
    )


class CallParticipant(BaseModel):
    __tablename__ = "call_participants"
    video_call_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("video_calls.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Participation details
    joined_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    left_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    connection_quality: Mapped[str | None] = mapped_column(String(20), nullable=True)
    device_info: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Relationships
    video_call = relationship("VideoCall", back_populates="participants")
    user = relationship("User", lazy="noload")

    # Indexes
    __table_args__ = (
        Index(
            "idx_call_participants_video_call_user",
            "video_call_id",
            "user_id",
            unique=True,
        ),
    )


class RecordingConsent(Base):
    __tablename__ = "recording_consents"

    id: Mapped[int | None] = mapped_column(Integer, primary_key=True, index=True)
    video_call_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("video_calls.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Consent details
    consented: Mapped[bool | None] = mapped_column(Boolean, default=False)
    consented_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    video_call = relationship("VideoCall", back_populates="recording_consents")
    user = relationship("User", lazy="noload")

    # Indexes
    __table_args__ = (
        Index(
            "idx_recording_consents_video_call_user",
            "video_call_id",
            "user_id",
            unique=True,
        ),
    )


class CallTranscription(Base):
    __tablename__ = "call_transcriptions"

    id: Mapped[int | None] = mapped_column(Integer, primary_key=True, index=True)
    video_call_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("video_calls.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    # Transcription data
    transcript_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    transcript_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    language: Mapped[str | None] = mapped_column(String(10), default="ja")
    processing_status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    word_count: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    video_call = relationship("VideoCall", back_populates="transcriptions")


class TranscriptionSegment(Base):
    __tablename__ = "transcription_segments"

    id: Mapped[int | None] = mapped_column(Integer, primary_key=True, index=True)
    video_call_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("video_calls.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    speaker_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Segment data
    segment_text: Mapped[str] = mapped_column(Text, nullable=False)
    start_time: Mapped[float] = mapped_column(Float, nullable=False)
    end_time: Mapped[float] = mapped_column(Float, nullable=False)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    video_call = relationship("VideoCall", back_populates="transcription_segments")
    speaker = relationship("User", lazy="noload")

    # Indexes
    __table_args__ = (
        Index(
            "idx_transcription_segments_video_call_time", "video_call_id", "start_time"
        ),
    )
