from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class VideoCallStatus(str, Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ConnectionQuality(str, Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"


class TranscriptionStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class VideoCallCreate(BaseModel):
    job_id: int | None = None
    interview_id: int | None = None
    candidate_id: int
    scheduled_at: datetime
    transcription_enabled: bool = True
    transcription_language: str = "ja"


class VideoCallUpdate(BaseModel):
    scheduled_at: datetime | None = None
    status: VideoCallStatus | None = None
    recording_url: str | None = None
    transcription_enabled: bool | None = None
    transcription_language: str | None = None


class VideoCallInfo(BaseModel):
    id: int
    job_id: int | None = None
    interview_id: int | None = None
    interviewer_id: int
    candidate_id: int
    scheduled_at: datetime
    started_at: datetime | None = None
    ended_at: datetime | None = None
    status: VideoCallStatus
    room_id: str
    recording_url: str | None = None
    transcription_enabled: bool
    transcription_language: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class VideoCallToken(BaseModel):
    room_id: str
    token: str
    expires_at: datetime


class RecordingConsentRequest(BaseModel):
    consented: bool


class RecordingConsentInfo(BaseModel):
    id: int
    video_call_id: int
    user_id: int
    consented: bool
    consented_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class TranscriptionSegmentCreate(BaseModel):
    speaker_id: int
    segment_text: str
    start_time: float = Field(..., ge=0)
    end_time: float = Field(..., ge=0)
    confidence: float | None = Field(None, ge=0, le=1)

    @field_validator("end_time")
    @classmethod
    def validate_end_after_start(cls, v, info):
        if "start_time" in info.data and v <= info.data["start_time"]:
            raise ValueError("end_time must be greater than start_time")
        return v


class TranscriptionSegmentInfo(BaseModel):
    id: int
    video_call_id: int
    speaker_id: int
    segment_text: str
    start_time: float
    end_time: float
    confidence: float | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CallTranscriptionInfo(BaseModel):
    id: int
    video_call_id: int
    transcript_url: str | None = None
    transcript_text: str | None = None
    language: str
    processing_status: TranscriptionStatus
    word_count: int | None = None
    created_at: datetime
    processed_at: datetime | None = None
    segments: list[TranscriptionSegmentInfo] | None = []

    model_config = ConfigDict(from_attributes=True)


class CallParticipantInfo(BaseModel):
    id: int
    video_call_id: int
    user_id: int
    joined_at: datetime | None = None
    left_at: datetime | None = None
    connection_quality: ConnectionQuality | None = None
    device_info: dict | None = None

    model_config = ConfigDict(from_attributes=True)
