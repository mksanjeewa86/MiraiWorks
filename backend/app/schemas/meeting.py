from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, validator


class MeetingType(str, Enum):
    CASUAL = "casual"  # Candidate ↔ Recruiter (1:1 interviews)
    MAIN = "main"  # Candidate ↔ Employer (recruiter as optional observer/organizer)


class MeetingStatus(str, Enum):
    SCHEDULED = "scheduled"
    STARTING = "starting"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


class ParticipantRole(str, Enum):
    HOST = "host"  # Meeting organizer
    PARTICIPANT = "participant"  # Regular participant
    OBSERVER = "observer"  # View-only (e.g., recruiter in main interviews)


class ParticipantStatus(str, Enum):
    INVITED = "invited"
    JOINED = "joined"
    LEFT = "left"
    DISCONNECTED = "disconnected"


class RecordingStatus(str, Enum):
    NOT_STARTED = "not_started"
    RECORDING = "recording"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


# Base schemas for meeting participants
class MeetingParticipantBase(BaseModel):
    user_id: int
    role: ParticipantRole = ParticipantRole.PARTICIPANT
    can_record: bool = False
    recording_consent: Optional[bool] = None


class MeetingParticipantCreate(MeetingParticipantBase):
    pass


class MeetingParticipantUpdate(BaseModel):
    role: Optional[ParticipantRole] = None
    can_record: Optional[bool] = None
    recording_consent: Optional[bool] = None
    status: Optional[ParticipantStatus] = None


class MeetingParticipantResponse(MeetingParticipantBase):
    id: int
    meeting_id: int
    status: ParticipantStatus
    joined_at: Optional[datetime] = None
    left_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    # User details (populated from relationship)
    user: Optional[dict] = None  # Will be populated with user data

    class Config:
        from_attributes = True


# Base meeting schemas
class MeetingBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    meeting_type: MeetingType
    scheduled_start: datetime
    scheduled_end: datetime
    recording_enabled: bool = False
    recording_consent_required: bool = True
    transcription_enabled: bool = False
    auto_summary: bool = False
    access_code: Optional[str] = Field(None, min_length=4, max_length=50)

    @validator("scheduled_end")
    def end_after_start(cls, v, values):
        if "scheduled_start" in values and v <= values["scheduled_start"]:
            raise ValueError("scheduled_end must be after scheduled_start")
        return v

    @validator("scheduled_start")
    def not_in_past(cls, v):
        if v <= datetime.utcnow():
            raise ValueError("scheduled_start must be in the future")
        return v


class MeetingCreate(MeetingBase):
    interview_id: Optional[int] = None
    participants: list[MeetingParticipantCreate] = Field(..., min_items=1)

    @validator("participants")
    def validate_participants_by_type(cls, v, values):
        if "meeting_type" not in values:
            return v

        meeting_type = values["meeting_type"]
        roles = [p.role for p in v]

        # Must have at least one host
        if ParticipantRole.HOST not in roles:
            raise ValueError("Meeting must have at least one host")

        # Type-specific validations
        if meeting_type == MeetingType.CASUAL:
            # Casual interviews: 2 participants (candidate + recruiter)
            if len(v) != 2:
                raise ValueError("Casual interviews must have exactly 2 participants")
        elif meeting_type == MeetingType.MAIN:
            # Main interviews: at least 2 participants (candidate + employer), optional recruiter observer
            if len(v) < 2:
                raise ValueError("Main interviews must have at least 2 participants")
            if len(v) > 5:
                raise ValueError("Main interviews can have maximum 5 participants")

        return v


class MeetingUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[MeetingStatus] = None
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    recording_enabled: Optional[bool] = None
    recording_consent_required: Optional[bool] = None
    transcription_enabled: Optional[bool] = None
    auto_summary: Optional[bool] = None
    access_code: Optional[str] = Field(None, min_length=4, max_length=50)

    @validator("scheduled_end")
    def end_after_start(cls, v, values):
        if (
            "scheduled_start" in values
            and v
            and values["scheduled_start"]
            and v <= values["scheduled_start"]
        ):
            raise ValueError("scheduled_end must be after scheduled_start")
        return v


class MeetingResponse(MeetingBase):
    id: int
    interview_id: Optional[int] = None
    status: MeetingStatus
    room_id: str
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None
    recording_status: RecordingStatus
    company_id: int
    created_by: int
    created_at: datetime
    updated_at: datetime

    # Computed properties
    duration_minutes: Optional[int] = None
    is_active: bool
    can_join: bool

    # Relationships
    participants: list[MeetingParticipantResponse] = []
    recordings: list["MeetingRecordingResponse"] = []
    transcripts: list["MeetingTranscriptResponse"] = []
    summaries: list["MeetingSummaryResponse"] = []

    class Config:
        from_attributes = True


# Recording schemas
class MeetingRecordingBase(BaseModel):
    filename: str
    original_filename: str
    file_size: int
    duration_seconds: Optional[int] = None
    mime_type: str
    is_public: bool = False
    access_expires_at: Optional[datetime] = None


class MeetingRecordingCreate(MeetingRecordingBase):
    storage_path: str


class MeetingRecordingUpdate(BaseModel):
    status: Optional[RecordingStatus] = None
    duration_seconds: Optional[int] = None
    processing_error: Optional[str] = None
    is_public: Optional[bool] = None
    access_expires_at: Optional[datetime] = None


class MeetingRecordingResponse(MeetingRecordingBase):
    id: int
    meeting_id: int
    storage_path: str
    status: RecordingStatus
    processing_started_at: Optional[datetime] = None
    processing_completed_at: Optional[datetime] = None
    processing_error: Optional[str] = None
    recorded_by: int
    created_at: datetime
    updated_at: datetime

    # Access URL (generated dynamically)
    download_url: Optional[str] = None

    class Config:
        from_attributes = True


# Transcript schemas
class MeetingTranscriptBase(BaseModel):
    transcript_text: str
    transcript_json: Optional[str] = None
    language: str = "ja"
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    stt_service: str
    processing_duration_seconds: Optional[int] = None
    word_count: Optional[int] = None
    speaker_count: Optional[int] = None
    speakers_identified: bool = False


class MeetingTranscriptCreate(MeetingTranscriptBase):
    recording_id: Optional[int] = None


class MeetingTranscriptUpdate(BaseModel):
    status: Optional[str] = None
    transcript_text: Optional[str] = None
    transcript_json: Optional[str] = None
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    processing_error: Optional[str] = None
    processing_duration_seconds: Optional[int] = None
    word_count: Optional[int] = None
    speaker_count: Optional[int] = None
    speakers_identified: Optional[bool] = None


class MeetingTranscriptResponse(MeetingTranscriptBase):
    id: int
    meeting_id: int
    recording_id: Optional[int] = None
    status: str
    processing_error: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Summary schemas
class MeetingSummaryBase(BaseModel):
    summary_text: str
    key_points: Optional[str] = None  # JSON string
    action_items: Optional[str] = None  # JSON string
    sentiment_analysis: Optional[str] = None  # JSON string
    ai_model: str
    prompt_version: str
    generation_duration_seconds: Optional[int] = None
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    summary_length_words: Optional[int] = None
    compression_ratio: Optional[float] = Field(None, ge=0.0, le=1.0)
    is_final: bool = True


class MeetingSummaryCreate(MeetingSummaryBase):
    transcript_id: Optional[int] = None


class MeetingSummaryUpdate(BaseModel):
    status: Optional[str] = None
    summary_text: Optional[str] = None
    key_points: Optional[str] = None
    action_items: Optional[str] = None
    sentiment_analysis: Optional[str] = None
    processing_error: Optional[str] = None
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    is_final: Optional[bool] = None
    reviewed_by: Optional[int] = None
    reviewed_at: Optional[datetime] = None


class MeetingSummaryResponse(MeetingSummaryBase):
    id: int
    meeting_id: int
    transcript_id: Optional[int] = None
    status: str
    processing_error: Optional[str] = None
    reviewed_by: Optional[int] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# WebRTC signaling schemas
class WebRTCSignal(BaseModel):
    type: str  # offer, answer, ice-candidate, join, leave, etc.
    data: dict
    target_user_id: Optional[int] = None  # For direct peer communication
    room_id: str


class MeetingJoinRequest(BaseModel):
    access_code: Optional[str] = None


class MeetingJoinResponse(BaseModel):
    success: bool
    room_id: str
    participant_id: int
    meeting: MeetingResponse
    turn_servers: list[dict]
    error: Optional[str] = None


# List and filter schemas
class MeetingListParams(BaseModel):
    status: Optional[MeetingStatus] = None
    meeting_type: Optional[MeetingType] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    participant_id: Optional[int] = None
    page: int = Field(1, ge=1)
    limit: int = Field(50, ge=1, le=100)


class MeetingListResponse(BaseModel):
    meetings: list[MeetingResponse]
    total: int
    page: int
    limit: int
    total_pages: int


# Update model forward references
MeetingResponse.model_rebuild()
MeetingRecordingResponse.model_rebuild()
MeetingTranscriptResponse.model_rebuild()
MeetingSummaryResponse.model_rebuild()
