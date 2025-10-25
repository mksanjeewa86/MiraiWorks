from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, field_validator

from app.utils.constants import InterviewStatus


class InterviewCreate(BaseModel):
    candidate_id: int
    recruiter_id: int
    employer_company_id: int
    title: str
    description: str | None = None
    position_title: str | None = None
    interview_type: str = "video"
    status: str | None = None
    scheduled_start: datetime | None = None
    scheduled_end: datetime | None = None
    timezone: str | None = "UTC"
    location: str | None = None
    meeting_url: str | None = None
    video_call_type: str | None = None
    notes: str | None = None
    workflow_id: int | None = None


class InterviewUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    position_title: str | None = None
    interview_type: str | None = None
    location: str | None = None
    meeting_url: str | None = None
    video_call_type: str | None = None
    notes: str | None = None
    status: str | None = None
    scheduled_start: datetime | None = None
    scheduled_end: datetime | None = None
    timezone: str | None = None
    workflow_id: int | None = None


class ProposalCreate(BaseModel):
    start_datetime: datetime
    end_datetime: datetime
    timezone: str = "UTC"
    location: str | None = None
    notes: str | None = None

    @field_validator("end_datetime")
    @classmethod
    def validate_end_after_start(cls, v, info):
        if info.data.get("start_datetime") and v <= info.data.get("start_datetime"):
            raise ValueError("End datetime must be after start datetime")
        return v

    @field_validator("timezone")
    @classmethod
    def validate_timezone(cls, v):
        # Basic timezone validation - could be enhanced with pytz
        if not v:
            return "UTC"
        return v


class ProposalResponse(BaseModel):
    response: str  # "accepted" or "declined"
    notes: str | None = None

    @field_validator("response")
    @classmethod
    def validate_response(cls, v):
        if v not in ["accepted", "declined"]:
            raise ValueError('Response must be "accepted" or "declined"')
        return v


class ProposalInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    interview_id: int
    proposed_by: int
    proposer_name: str
    proposer_role: str
    start_datetime: datetime
    end_datetime: datetime
    timezone: str
    location: str | None = None
    notes: str | None = None
    status: str
    responded_by: int | None
    responder_name: str | None
    responded_at: datetime | None
    response_notes: str | None = None
    expires_at: datetime | None
    created_at: datetime


class ParticipantInfo(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    company_name: str | None = None


class InterviewInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None = None
    position_title: str | None = None
    status: str
    interview_type: str

    candidate: ParticipantInfo
    recruiter: ParticipantInfo
    employer_company_name: str | None = None

    scheduled_start: datetime | None = None
    scheduled_end: datetime | None = None
    timezone: str | None = None
    location: str | None = None
    meeting_url: str | None = None
    video_call_type: str | None = None
    duration_minutes: int | None = None

    notes: str | None = None
    preparation_notes: str | None = None
    workflow_id: int | None = None
    created_by: int | None = None
    confirmed_by: int | None = None
    confirmed_at: datetime | None = None
    cancelled_by: int | None = None
    cancelled_at: datetime | None = None
    cancellation_reason: str | None = None

    proposals: list[ProposalInfo] = []
    active_proposal_count: int = 0

    created_at: datetime
    updated_at: datetime


class InterviewCancel(BaseModel):
    reason: str | None = None

    @field_validator("reason")
    @classmethod
    def validate_reason(cls, v):
        if v and len(v) > 1000:
            raise ValueError("Cancellation reason cannot exceed 1000 characters")
        return v


class InterviewReschedule(BaseModel):
    new_start: datetime
    new_end: datetime
    reason: str | None = None

    @field_validator("new_end")
    @classmethod
    def validate_end_after_start(cls, v, info):
        if info.data.get("new_start") and v <= info.data.get("new_start"):
            raise ValueError("End datetime must be after start datetime")
        return v


class InterviewsListRequest(BaseModel):
    status: str | None = None
    candidate_id: int | None = None
    recruiter_id: int | None = None
    employer_company_id: int | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    limit: int = 50
    offset: int = 0

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        if v and v not in [status.value for status in InterviewStatus]:
            raise ValueError(
                f"Invalid status. Must be one of: {', '.join([s.value for s in InterviewStatus])}"
            )
        return v

    @field_validator("limit")
    @classmethod
    def validate_limit(cls, v):
        if v > 100:
            raise ValueError("Limit cannot exceed 100")
        return v


class InterviewsListResponse(BaseModel):
    interviews: list[InterviewInfo]
    total: int
    has_more: bool


class InterviewStats(BaseModel):
    total_interviews: int
    by_status: dict[str, int]
    by_type: dict[str, int]
    upcoming_count: int
    completed_count: int
    average_duration_minutes: float | None


class InterviewCalendarEvent(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    interview_id: int
    title: str
    start: datetime
    end: datetime
    status: str
    participants: list[str]  # Email addresses
    location: str | None = None
    meeting_url: str | None = None


class CalendarIntegrationStatus(BaseModel):
    has_google_calendar: bool
    has_microsoft_calendar: bool
    google_calendar_email: str | None
    microsoft_calendar_email: str | None
    last_sync_at: datetime | None
    sync_enabled: bool


class InterviewAvailabilityRequest(BaseModel):
    participant_emails: list[str]
    duration_minutes: int = 60
    preferred_times: list[dict[str, Any]] = []  # Flexible time preferences
    timezone: str = "UTC"

    @field_validator("participant_emails")
    @classmethod
    def validate_emails(cls, v):
        if not v:
            raise ValueError("At least one participant email is required")
        return v


class InterviewTimeSlot(BaseModel):
    start_datetime: datetime
    end_datetime: datetime
    available_participants: list[str]
    conflicting_participants: list[str]
    confidence_score: float  # 0-1, based on availability and preferences


class InterviewSuggestion(BaseModel):
    suggested_slots: list[InterviewTimeSlot]
    total_participants: int
    timezone: str
    duration_minutes: int
