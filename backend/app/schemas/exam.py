from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field

# Import enums from models
from app.models.exam import ExamStatus, ExamType, QuestionType, SessionStatus

# Import TemplateQuestionSelection from question_bank schemas
from app.schemas.question_bank import TemplateQuestionSelection


class ExamBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    exam_type: ExamType = ExamType.CUSTOM
    time_limit_minutes: Optional[int] = Field(None, ge=1, le=480)  # Max 8 hours
    max_attempts: int = Field(1, ge=1, le=10)
    passing_score: Optional[float] = Field(None, ge=0, le=100)
    is_randomized: bool = False
    is_public: bool = False  # Public exams available to all companies
    allow_web_usage: bool = True
    monitor_web_usage: bool = False
    require_face_verification: bool = False
    face_check_interval_minutes: int = Field(5, ge=1, le=60)
    show_results_immediately: bool = True
    show_correct_answers: bool = False
    show_score: bool = True
    instructions: Optional[str] = None


class ExamCreate(ExamBase):
    company_id: Optional[int] = None  # NULL = global exam (system admin only)


class ExamUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[ExamStatus] = None
    time_limit_minutes: Optional[int] = Field(None, ge=1, le=480)
    max_attempts: Optional[int] = Field(None, ge=1, le=10)
    passing_score: Optional[float] = Field(None, ge=0, le=100)
    is_randomized: Optional[bool] = None
    is_public: Optional[bool] = None
    allow_web_usage: Optional[bool] = None
    monitor_web_usage: Optional[bool] = None
    require_face_verification: Optional[bool] = None
    face_check_interval_minutes: Optional[int] = Field(None, ge=1, le=60)
    show_results_immediately: Optional[bool] = None
    show_correct_answers: Optional[bool] = None
    show_score: Optional[bool] = None
    instructions: Optional[str] = None


class ExamInfo(ExamBase):
    id: int
    company_id: Optional[int]  # NULL for global exams
    created_by: Optional[int]
    status: ExamStatus
    created_at: datetime
    updated_at: datetime

    # Additional computed fields
    total_questions: Optional[int] = None
    total_sessions: Optional[int] = None
    completed_sessions: Optional[int] = None
    average_score: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


class ExamQuestionBase(BaseModel):
    question_text: str = Field(..., min_length=1)
    question_type: QuestionType
    order_index: int = Field(0, ge=0)
    points: float = Field(1.0, ge=0)
    time_limit_seconds: Optional[int] = Field(None, ge=1)
    is_required: bool = True
    options: dict[str, str] | None = None  # {"A": "Option 1", "B": "Option 2"}
    correct_answers: list[str] | None = None  # ["A"] or ["A", "B"]
    max_length: Optional[int] = Field(None, ge=1, le=10000)
    min_length: Optional[int] = Field(None, ge=0)
    rating_scale: Optional[int] = Field(None, ge=2, le=10)
    explanation: Optional[str] = None
    tags: list[str] | None = None


class ExamQuestionCreate(ExamQuestionBase):
    exam_id: int


class ExamQuestionUpdate(BaseModel):
    question_text: Optional[str] = Field(None, min_length=1)
    question_type: Optional[QuestionType] = None
    order_index: Optional[int] = Field(None, ge=0)
    points: Optional[float] = Field(None, ge=0)
    time_limit_seconds: Optional[int] = Field(None, ge=1)
    is_required: Optional[bool] = None
    options: dict[str, str] | None = None
    correct_answers: list[str] | None = None
    max_length: Optional[int] = Field(None, ge=1, le=10000)
    min_length: Optional[int] = Field(None, ge=0)
    rating_scale: Optional[int] = Field(None, ge=2, le=10)
    explanation: Optional[str] = None
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
    time_limit_seconds: Optional[int]
    is_required: bool
    options: dict[str, str] | None  # No correct answers exposed
    max_length: Optional[int]
    min_length: Optional[int]
    rating_scale: Optional[int]

    model_config = ConfigDict(from_attributes=True)


class ExamSessionCreate(BaseModel):
    exam_id: int
    assignment_id: Optional[int] = None


class ExamSessionUpdate(BaseModel):
    status: Optional[SessionStatus] = None
    current_question_index: Optional[int] = Field(None, ge=0)
    time_remaining_seconds: Optional[int] = Field(None, ge=0)
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    screen_resolution: Optional[str] = None


class ExamSessionInfo(BaseModel):
    id: int
    exam_id: int
    candidate_id: int
    assignment_id: Optional[int]
    status: SessionStatus
    attempt_number: int
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    expires_at: Optional[datetime]
    time_remaining_seconds: Optional[int]
    current_question_index: int
    total_questions: int
    questions_answered: int
    score: Optional[float]
    max_score: Optional[float]
    percentage: Optional[float]
    passed: Optional[bool]
    web_usage_detected: bool
    web_usage_count: int
    face_verification_failed: bool
    face_check_count: int
    created_at: datetime
    updated_at: datetime

    # Exam info for convenience
    exam_title: Optional[str] = None
    exam_type: Optional[ExamType] = None
    candidate_name: Optional[str] = None
    candidate_email: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ExamAnswerSubmit(BaseModel):
    question_id: int
    answer_data: dict[str, Any] | None = None
    answer_text: Optional[str] = None
    selected_options: list[str] | None = None
    time_spent_seconds: Optional[int] = Field(None, ge=0)


class ExamAnswerInfo(BaseModel):
    id: int
    session_id: int
    question_id: int
    answer_data: dict[str, Any] | None
    answer_text: Optional[str]
    selected_options: list[str] | None
    is_correct: Optional[bool]
    points_earned: float
    points_possible: float
    time_spent_seconds: Optional[int]
    answered_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ExamAssignmentCreate(BaseModel):
    exam_id: int
    candidate_ids: list[int]  # Can assign to multiple candidates
    due_date: Optional[datetime] = None
    custom_time_limit_minutes: Optional[int] = Field(None, ge=1)
    custom_max_attempts: Optional[int] = Field(None, ge=1, le=10)
    custom_is_randomized: Optional[bool] = None


class ExamAssignmentUpdate(BaseModel):
    due_date: Optional[datetime] = None
    custom_time_limit_minutes: Optional[int] = Field(None, ge=1)
    custom_max_attempts: Optional[int] = Field(None, ge=1, le=10)
    custom_is_randomized: Optional[bool] = None
    is_active: Optional[bool] = None


class ExamAssignmentInfo(BaseModel):
    id: int
    exam_id: int
    candidate_id: int
    assigned_by: Optional[int]
    due_date: Optional[datetime]
    custom_time_limit_minutes: Optional[int]
    custom_max_attempts: Optional[int]
    custom_is_randomized: Optional[bool]
    is_active: bool
    completed: bool
    notification_sent: bool
    reminder_sent: bool
    created_at: datetime
    updated_at: datetime

    # Related info for convenience
    exam_title: Optional[str] = None
    exam_type: Optional[ExamType] = None
    candidate_name: Optional[str] = None
    candidate_email: Optional[str] = None
    assigner_name: Optional[str] = None
    sessions_count: Optional[int] = None
    latest_session: Optional[ExamSessionInfo] = None

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
    questions: list[
        ExamQuestionInfo
    ] | None = None  # Include if showing correct answers
    monitoring_events: list[ExamMonitoringEventInfo] | None = None


class ExamStatistics(BaseModel):
    """Statistics for an exam"""

    exam_id: int
    total_assigned: int
    total_started: int
    total_completed: int
    completion_rate: float
    average_score: Optional[float]
    average_time_minutes: Optional[float]
    pass_rate: Optional[float]
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
    assignment_id: Optional[int] = None
    test_mode: bool = False
    user_agent: Optional[str] = None
    screen_resolution: Optional[str] = None


class ExamTakeResponse(BaseModel):
    """Response when starting exam"""

    session: ExamSessionInfo
    questions: list[ExamQuestionPublic]
    current_question: Optional[ExamQuestionPublic] = None
    time_remaining_seconds: Optional[int]
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


# Hybrid Exam Schemas


class HybridExamQuestionCreate(ExamQuestionBase):
    """Question for hybrid exam (without exam_id, will be set during creation)"""

    pass


class HybridExamCreate(BaseModel):
    """Schema for creating a hybrid exam with custom questions + template selections"""

    # Base exam data
    exam_data: ExamCreate

    # Custom questions created specifically for this exam
    custom_questions: list[HybridExamQuestionCreate] = Field(
        default_factory=list, description="Custom questions created for this exam"
    )

    # Template selections (randomly select from question banks)
    template_selections: list[TemplateQuestionSelection] = Field(
        default_factory=list,
        description="Question bank selections for random question picking",
    )

    # Validation
    def validate_has_questions(self) -> bool:
        """Ensure at least one question source is provided"""
        return len(self.custom_questions) > 0 or len(self.template_selections) > 0


class HybridExamResponse(BaseModel):
    """Response after creating a hybrid exam"""

    exam: ExamInfo
    total_questions: int
    custom_count: int
    template_count: int
    selection_rules: dict[str, Any]  # The question_selection_rules stored in exam
