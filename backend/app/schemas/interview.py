from datetime import datetime
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from pydantic import BaseModel
from pydantic import validator

from app.utils.constants import InterviewStatus


class InterviewCreate(BaseModel):
    candidate_id: int
    recruiter_id: int
    employer_company_id: int
    title: str
    description: Optional[str] = None
    position_title: Optional[str] = None
    interview_type: str = "video"  # video, phone, in_person
    
    @validator('title')
    def validate_title(cls, v):
        if not v or not v.strip():
            raise ValueError('Title is required')
        return v.strip()
    
    @validator('interview_type')
    def validate_interview_type(cls, v):
        allowed_types = ['video', 'phone', 'in_person']
        if v not in allowed_types:
            raise ValueError(f'Interview type must be one of: {", ".join(allowed_types)}')
        return v


class InterviewUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    position_title: Optional[str] = None
    interview_type: Optional[str] = None
    location: Optional[str] = None
    meeting_url: Optional[str] = None
    notes: Optional[str] = None
    
    @validator('title')
    def validate_title(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError('Title cannot be empty')
        return v.strip() if v else v


class ProposalCreate(BaseModel):
    start_datetime: datetime
    end_datetime: datetime
    timezone: str = "UTC"
    location: Optional[str] = None
    notes: Optional[str] = None
    
    @validator('end_datetime')
    def validate_end_after_start(cls, v, values):
        if 'start_datetime' in values and v <= values['start_datetime']:
            raise ValueError('End datetime must be after start datetime')
        return v
    
    @validator('timezone')
    def validate_timezone(cls, v):
        # Basic timezone validation - could be enhanced with pytz
        if not v:
            return "UTC"
        return v


class ProposalResponse(BaseModel):
    response: str  # "accepted" or "declined"
    notes: Optional[str] = None
    
    @validator('response')
    def validate_response(cls, v):
        if v not in ['accepted', 'declined']:
            raise ValueError('Response must be "accepted" or "declined"')
        return v


class ProposalInfo(BaseModel):
    id: int
    interview_id: int
    proposed_by: int
    proposer_name: str
    proposer_role: str
    start_datetime: datetime
    end_datetime: datetime
    timezone: str
    location: Optional[str]
    notes: Optional[str]
    status: str
    responded_by: Optional[int]
    responder_name: Optional[str]
    responded_at: Optional[datetime]
    response_notes: Optional[str]
    expires_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ParticipantInfo(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    company_name: Optional[str]


class InterviewInfo(BaseModel):
    id: int
    title: str
    description: Optional[str]
    position_title: Optional[str]
    status: str
    interview_type: str
    
    # Participants
    candidate: ParticipantInfo
    recruiter: ParticipantInfo
    employer_company_name: str
    
    # Scheduling
    scheduled_start: Optional[datetime]
    scheduled_end: Optional[datetime]
    timezone: Optional[str]
    location: Optional[str]
    meeting_url: Optional[str]
    duration_minutes: Optional[int]
    
    # Metadata
    notes: Optional[str]
    preparation_notes: Optional[str]
    created_by: Optional[int]
    confirmed_by: Optional[int]
    confirmed_at: Optional[datetime]
    cancelled_by: Optional[int]
    cancelled_at: Optional[datetime]
    cancellation_reason: Optional[str]
    
    # Related data
    proposals: List[ProposalInfo] = []
    active_proposal_count: int = 0
    
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class InterviewCancel(BaseModel):
    reason: Optional[str] = None
    
    @validator('reason')
    def validate_reason(cls, v):
        if v and len(v) > 1000:
            raise ValueError('Cancellation reason cannot exceed 1000 characters')
        return v


class InterviewReschedule(BaseModel):
    new_start: datetime
    new_end: datetime
    reason: Optional[str] = None
    
    @validator('new_end')
    def validate_end_after_start(cls, v, values):
        if 'new_start' in values and v <= values['new_start']:
            raise ValueError('End datetime must be after start datetime')
        return v


class InterviewsListRequest(BaseModel):
    status: Optional[str] = None
    candidate_id: Optional[int] = None
    recruiter_id: Optional[int] = None
    employer_company_id: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = 50
    offset: int = 0
    
    @validator('status')
    def validate_status(cls, v):
        if v and v not in [status.value for status in InterviewStatus]:
            raise ValueError(f'Invalid status. Must be one of: {", ".join([s.value for s in InterviewStatus])}')
        return v
    
    @validator('limit')
    def validate_limit(cls, v):
        if v > 100:
            raise ValueError('Limit cannot exceed 100')
        return v


class InterviewsListResponse(BaseModel):
    interviews: List[InterviewInfo]
    total: int
    has_more: bool


class InterviewStats(BaseModel):
    total_interviews: int
    by_status: Dict[str, int]
    by_type: Dict[str, int]
    upcoming_count: int
    completed_count: int
    average_duration_minutes: Optional[float]


class InterviewCalendarEvent(BaseModel):
    interview_id: int
    title: str
    start: datetime
    end: datetime
    status: str
    participants: List[str]  # Email addresses
    location: Optional[str]
    meeting_url: Optional[str]
    
    class Config:
        from_attributes = True


class CalendarIntegrationStatus(BaseModel):
    has_google_calendar: bool
    has_microsoft_calendar: bool
    google_calendar_email: Optional[str]
    microsoft_calendar_email: Optional[str]
    last_sync_at: Optional[datetime]
    sync_enabled: bool


class InterviewAvailabilityRequest(BaseModel):
    participant_emails: List[str]
    duration_minutes: int = 60
    preferred_times: List[Dict[str, Any]] = []  # Flexible time preferences
    timezone: str = "UTC"
    
    @validator('participant_emails')
    def validate_emails(cls, v):
        if not v:
            raise ValueError('At least one participant email is required')
        return v


class InterviewTimeSlot(BaseModel):
    start_datetime: datetime
    end_datetime: datetime
    available_participants: List[str]
    conflicting_participants: List[str]
    confidence_score: float  # 0-1, based on availability and preferences


class InterviewSuggestion(BaseModel):
    suggested_slots: List[InterviewTimeSlot]
    total_participants: int
    timezone: str
    duration_minutes: int