from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

# Import enums from models
from app.models.exam import ExamStatus, ExamType, QuestionType, SessionStatus


class ExamBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    exam_type: ExamType = ExamType.CUSTOM
    time_limit_minutes: int | None = Field(None, ge=1, le=480)  # Max 8 hours
    max_attempts: int = Field(1, ge=1, le=10)
    passing_score: float | None = Field(None, ge=0, le=100)
    is_randomized: bool = False
    allow_web_usage: bool = True
    monitor_web_usage: bool = False
    require_face_verification: bool = False
    face_check_interval_minutes: int = Field(5, ge=1, le=60)
    show_results_immediately: bool = True
    show_correct_answers: bool = False
    show_score: bool = True
    instructions: str | None = None


class ExamCreate(ExamBase):
    company_id: int


class ExamUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    status: ExamStatus | None = None
    time_limit_minutes: int | None = Field(None, ge=1, le=480)
    max_attempts: int | None = Field(None, ge=1, le=10)
    passing_score: float | None = Field(None, ge=0, le=100)
    is_randomized: bool | None = None
    allow_web_usage: bool | None = None
    monitor_web_usage: bool | None = None
    require_face_verification: bool | None = None
    face_check_interval_minutes: int | None = Field(None, ge=1, le=60)
    show_results_immediately: bool | None = None
    show_correct_answers: bool | None = None
    show_score: bool | None = None
    instructions: str | None = None


class ExamInfo(ExamBase):
    id: int
    company_id: int
    created_by: int | None
    status: ExamStatus
    created_at: datetime
    updated_at: datetime

    # Additional computed fields
    total_questions: int | None = None
    total_sessions: int | None = None
    completed_sessions: int | None = None
    average_score: float | None = None

    model_config = ConfigDict(from_attributes=True)


class ExamQuestionBase(BaseModel):
    question_text: str = Field(..., min_length=1)
    question_type: QuestionType
    order_index: int = Field(0, ge=0)
    points: float = Field(1.0, ge=0)
    time_limit_seconds: int | None = Field(None, ge=1)
    is_required: bool = True
    options: dict[str, str] | None = None  # {"A": "Option 1", "B": "Option 2"}
    correct_answers: list[str] | None = None  # ["A"] or ["A", "B"]
    max_length: int | None = Field(None, ge=1, le=10000)
    min_length: int | None = Field(None, ge=0)
    rating_scale: int | None = Field(None, ge=2, le=10)
    explanation: str | None = None
    tags: list[str] | None = None


class ExamQuestionCreate(ExamQuestionBase):
    exam_id: int


class ExamQuestionUpdate(BaseModel):
    question_text: str | None = Field(None, min_length=1)
    question_type: QuestionType | None = None
    order_index: int | None = Field(None, ge=0)
    points: float | None = Field(None, ge=0)
    time_limit_seconds: int | None = Field(None, ge=1)
    is_required: bool | None = None
    options: dict[str, str] | None = None
    correct_answers: list[str] | None = None
    max_length: int | None = Field(None, ge=1, le=10000)
    min_length: int | None = Field(None, ge=0)
    rating_scale: int | None = Field(None, ge=2, le=10)
    explanation: str | None = None
    tags: list[str] | None = None


class ExamQuestionInfo(ExamQuestionBase):
    id: int
    exam_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ExamQuestionPublic(BaseModel):
    """Public version of question (for candidates taking exam)"""
    id: int
    question_text: str
    question_type: QuestionType
    order_index: int
    points: float
    time_limit_seconds: int | None
    is_required: bool
    options: dict[str, str] | None  # No correct answers exposed
    max_length: int | None
    min_length: int | None
    rating_scale: int | None

    model_config = ConfigDict(from_attributes=True)


class ExamSessionCreate(BaseModel):
    exam_id: int
    assignment_id: int | None = None


class ExamSessionUpdate(BaseModel):
    status: SessionStatus | None = None
    current_question_index: int | None = Field(None, ge=0)
    time_remaining_seconds: int | None = Field(None, ge=0)
    user_agent: str | None = None
    ip_address: str | None = None
    screen_resolution: str | None = None


class ExamSessionInfo(BaseModel):
    id: int
    exam_id: int
    candidate_id: int
    assignment_id: int | None
    status: SessionStatus
    attempt_number: int
    started_at: datetime | None
    completed_at: datetime | None
    expires_at: datetime | None
    time_remaining_seconds: int | None
    current_question_index: int
    total_questions: int
    questions_answered: int
    score: float | None
    max_score: float | None
    percentage: float | None
    passed: bool | None
    web_usage_detected: bool
    web_usage_count: int
    face_verification_failed: bool
    face_check_count: int
    created_at: datetime
    updated_at: datetime

    # Exam info for convenience
    exam_title: str | None = None
    exam_type: ExamType | None = None
    candidate_name: str | None = None
    candidate_email: str | None = None

    model_config = ConfigDict(from_attributes=True)


class ExamAnswerSubmit(BaseModel):
    question_id: int
    answer_data: dict[str, Any] | None = None
    answer_text: str | None = None
    selected_options: list[str] | None = None
    time_spent_seconds: int | None = Field(None, ge=0)


class ExamAnswerInfo(BaseModel):
    id: int
    session_id: int
    question_id: int
    answer_data: dict[str, Any] | None
    answer_text: str | None
    selected_options: list[str] | None
    is_correct: bool | None
    points_earned: float
    points_possible: float
    time_spent_seconds: int | None
    answered_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ExamAssignmentCreate(BaseModel):
    exam_id: int
    candidate_ids: list[int]  # Can assign to multiple candidates
    due_date: datetime | None = None
    custom_time_limit_minutes: int | None = Field(None, ge=1)
    custom_max_attempts: int | None = Field(None, ge=1, le=10)


class ExamAssignmentUpdate(BaseModel):
    due_date: datetime | None = None
    custom_time_limit_minutes: int | None = Field(None, ge=1)
    custom_max_attempts: int | None = Field(None, ge=1, le=10)
    is_active: bool | None = None


class ExamAssignmentInfo(BaseModel):
    id: int
    exam_id: int
    candidate_id: int
    assigned_by: int | None
    due_date: datetime | None
    custom_time_limit_minutes: int | None
    custom_max_attempts: int | None
    is_active: bool
    completed: bool
    notification_sent: bool
    reminder_sent: bool
    created_at: datetime
    updated_at: datetime

    # Related info for convenience
    exam_title: str | None = None
    exam_type: ExamType | None = None
    candidate_name: str | None = None
    candidate_email: str | None = None
    assigner_name: str | None = None
    sessions_count: int | None = None
    latest_session: ExamSessionInfo | None = None

    model_config = ConfigDict(from_attributes=True)


class ExamMonitoringEventCreate(BaseModel):
    session_id: int
    event_type: str
    event_data: dict[str, Any] | None = None
    severity: str = "info"


class ExamMonitoringEventInfo(BaseModel):
    id: int
    session_id: int
    event_type: str
    event_data: dict[str, Any] | None
    severity: str
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


class ExamResultSummary(BaseModel):
    """Summary of exam results for display"""
    session: ExamSessionInfo
    answers: list[ExamAnswerInfo]
    questions: list[ExamQuestionInfo] | None = None  # Include if showing correct answers
    monitoring_events: list[ExamMonitoringEventInfo] | None = None


class ExamStatistics(BaseModel):
    """Statistics for an exam"""
    exam_id: int
    total_assigned: int
    total_started: int
    total_completed: int
    completion_rate: float
    average_score: float | None
    average_time_minutes: float | None
    pass_rate: float | None
    question_statistics: list[dict[str, Any]]  # Per-question stats


class ExamListResponse(BaseModel):
    exams: list[ExamInfo]
    total: int
    page: int
    page_size: int
    has_more: bool


class ExamSessionListResponse(BaseModel):
    sessions: list[ExamSessionInfo]
    total: int
    page: int
    page_size: int
    has_more: bool


class ExamTakeRequest(BaseModel):
    """Request to start taking an exam"""
    exam_id: int
    assignment_id: int | None = None
    test_mode: bool = False
    user_agent: str | None = None
    screen_resolution: str | None = None


class ExamTakeResponse(BaseModel):
    """Response when starting exam"""
    session: ExamSessionInfo
    questions: list[ExamQuestionPublic]
    current_question: ExamQuestionPublic | None = None
    time_remaining_seconds: int | None
    can_navigate: bool = True


class FaceVerificationSubmit(BaseModel):
    """Face verification data submission"""
    session_id: int
    image_data: str  # Base64 encoded image
    timestamp: datetime
    verification_type: str = "periodic"  # "initial", "periodic", "suspicious"


class FaceVerificationResponse(BaseModel):
    """Face verification result"""
    verified: bool
    confidence_score: float
    message: str
    requires_human_review: bool = False
