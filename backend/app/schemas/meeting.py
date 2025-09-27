from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator


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
    recording_consent: bool | None = None


class MeetingParticipantCreate(MeetingParticipantBase):
    pass


class MeetingParticipantUpdate(BaseModel):
    role: ParticipantRole | None = None
    can_record: bool | None = None
    recording_consent: bool | None = None
    status: ParticipantStatus | None = None


class MeetingParticipantResponse(MeetingParticipantBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    meeting_id: int
    status: ParticipantStatus
    joined_at: datetime | None = None
    left_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    # User details (populated from relationship)
    user: dict | None = None  # Will be populated with user data


# Base meeting schemas
class MeetingBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    meeting_type: MeetingType
    scheduled_start: datetime
    scheduled_end: datetime
    recording_enabled: bool = False
    recording_consent_required: bool = True
    transcription_enabled: bool = False
    auto_summary: bool = False
    access_code: str | None = Field(None, min_length=4, max_length=50)

    @field_validator("scheduled_end")
    @classmethod
    def end_after_start(cls, v, info):
        if info.data.get("scheduled_start") and v <= info.data.get("scheduled_start"):
            raise ValueError("scheduled_end must be after scheduled_start")
        return v

    @field_validator("scheduled_start")
    @classmethod
    def not_in_past(cls, v):
        if v <= datetime.utcnow():
            raise ValueError("scheduled_start must be in the future")
        return v


class MeetingCreate(MeetingBase):
    interview_id: int | None = None
    participants: list[MeetingParticipantCreate] = Field(..., min_length=1)

    @field_validator("participants")
    @classmethod
    def validate_participants_by_type(cls, v, info):
        meeting_type = info.data.get("meeting_type")
        if not meeting_type:
            return v

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
    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    status: MeetingStatus | None = None
    scheduled_start: datetime | None = None
    scheduled_end: datetime | None = None
    recording_enabled: bool | None = None
    recording_consent_required: bool | None = None
    transcription_enabled: bool | None = None
    auto_summary: bool | None = None
    access_code: str | None = Field(None, min_length=4, max_length=50)

    @field_validator("scheduled_end")
    @classmethod
    def end_after_start(cls, v, info):
        scheduled_start = info.data.get("scheduled_start")
        if scheduled_start and v and v <= scheduled_start:
            raise ValueError("scheduled_end must be after scheduled_start")
        return v


class MeetingResponse(MeetingBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    interview_id: int | None = None
    status: MeetingStatus
    room_id: str
    actual_start: datetime | None = None
    actual_end: datetime | None = None
    recording_status: RecordingStatus
    company_id: int
    created_by: int
    created_at: datetime
    updated_at: datetime

    # Computed properties
    duration_minutes: int | None = None
    is_active: bool
    can_join: bool

    # Relationships
    participants: list[MeetingParticipantResponse] = []
    recordings: list["MeetingRecordingResponse"] = []
    transcripts: list["MeetingTranscriptResponse"] = []
    summaries: list["MeetingSummaryResponse"] = []


# Recording schemas
class MeetingRecordingBase(BaseModel):
    filename: str
    original_filename: str
    file_size: int
    duration_seconds: int | None = None
    mime_type: str
    is_public: bool = False
    access_expires_at: datetime | None = None


class MeetingRecordingCreate(MeetingRecordingBase):
    storage_path: str


class MeetingRecordingUpdate(BaseModel):
    status: RecordingStatus | None = None
    duration_seconds: int | None = None
    processing_error: str | None = None
    is_public: bool | None = None
    access_expires_at: datetime | None = None


class MeetingRecordingResponse(MeetingRecordingBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    meeting_id: int
    storage_path: str
    status: RecordingStatus
    processing_started_at: datetime | None = None
    processing_completed_at: datetime | None = None
    processing_error: str | None = None
    recorded_by: int
    created_at: datetime
    updated_at: datetime

    # Access URL (generated dynamically)
    download_url: str | None = None


# Transcript schemas
class MeetingTranscriptBase(BaseModel):
    transcript_text: str
    transcript_json: str | None = None
    language: str = "ja"
    confidence_score: float | None = Field(None, ge=0.0, le=1.0)
    stt_service: str
    processing_duration_seconds: int | None = None
    word_count: int | None = None
    speaker_count: int | None = None
    speakers_identified: bool = False


class MeetingTranscriptCreate(MeetingTranscriptBase):
    recording_id: int | None = None


class MeetingTranscriptUpdate(BaseModel):
    status: str | None = None
    transcript_text: str | None = None
    transcript_json: str | None = None
    confidence_score: float | None = Field(None, ge=0.0, le=1.0)
    processing_error: str | None = None
    processing_duration_seconds: int | None = None
    word_count: int | None = None
    speaker_count: int | None = None
    speakers_identified: bool | None = None


class MeetingTranscriptResponse(MeetingTranscriptBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    meeting_id: int
    recording_id: int | None = None
    status: str
    processing_error: str | None = None
    created_at: datetime
    updated_at: datetime


# Summary schemas
class MeetingSummaryBase(BaseModel):
    summary_text: str
    key_points: str | None = None  # JSON string
    action_items: str | None = None  # JSON string
    sentiment_analysis: str | None = None  # JSON string
    ai_model: str
    prompt_version: str
    generation_duration_seconds: int | None = None
    confidence_score: float | None = Field(None, ge=0.0, le=1.0)
    summary_length_words: int | None = None
    compression_ratio: float | None = Field(None, ge=0.0, le=1.0)
    is_final: bool = True


class MeetingSummaryCreate(MeetingSummaryBase):
    transcript_id: int | None = None


class MeetingSummaryUpdate(BaseModel):
    status: str | None = None
    summary_text: str | None = None
    key_points: str | None = None
    action_items: str | None = None
    sentiment_analysis: str | None = None
    processing_error: str | None = None
    confidence_score: float | None = Field(None, ge=0.0, le=1.0)
    is_final: bool | None = None
    reviewed_by: int | None = None
    reviewed_at: datetime | None = None


class MeetingSummaryResponse(MeetingSummaryBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    meeting_id: int
    transcript_id: int | None = None
    status: str
    processing_error: str | None = None
    reviewed_by: int | None = None
    reviewed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


# WebRTC signaling schemas
class WebRTCSignal(BaseModel):
    type: str  # offer, answer, ice-candidate, join, leave, etc.
    data: dict
    target_user_id: int | None = None  # For direct peer communication
    room_id: str


class MeetingJoinRequest(BaseModel):
    access_code: str | None = None


class MeetingJoinResponse(BaseModel):
    success: bool
    room_id: str
    participant_id: int
    meeting: MeetingResponse
    turn_servers: list[dict]
    error: str | None = None


# List and filter schemas
class MeetingListParams(BaseModel):
    status: MeetingStatus | None = None
    meeting_type: MeetingType | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    participant_id: int | None = None
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
