from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base
from app.models.base import BaseModel
from app.schemas.exam import ExamStatus, ExamType, QuestionType, SessionStatus


class Exam(BaseModel):
    """Recruitment exam model."""

    __tablename__ = "exams"
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    exam_type: Mapped[ExamType] = mapped_column(
        SQLAlchemyEnum(ExamType), nullable=False, default=ExamType.CUSTOM
    )
    status: Mapped[ExamStatus] = mapped_column(
        SQLAlchemyEnum(ExamStatus), nullable=False, default=ExamStatus.DRAFT
    )

    # Organization settings
    company_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=True,  # NULL = global exam created by system admin
        index=True,
    )
    is_public: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, index=True
    )  # True = available to all companies
    created_by: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    # Exam settings
    time_limit_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_attempts: Mapped[int | None] = mapped_column(Integer, default=1)
    passing_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    is_randomized: Mapped[bool | None] = mapped_column(Boolean, default=False)

    # Web monitoring settings
    allow_web_usage: Mapped[bool | None] = mapped_column(Boolean, default=True)
    monitor_web_usage: Mapped[bool | None] = mapped_column(Boolean, default=False)

    # Face recognition settings
    require_face_verification: Mapped[bool | None] = mapped_column(Boolean, default=False)
    face_check_interval_minutes: Mapped[int | None] = mapped_column(Integer, default=5)

    # Result settings
    show_results_immediately: Mapped[bool | None] = mapped_column(Boolean, default=True)
    show_correct_answers: Mapped[bool | None] = mapped_column(Boolean, default=False)
    show_score: Mapped[bool | None] = mapped_column(Boolean, default=True)

    # Metadata
    instructions: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Hybrid exam configuration
    question_selection_rules: Mapped[dict | None] = mapped_column(
        JSON, nullable=True
    )  # Stores how exam was created (for audit/recreation)
    # Example: {"custom_count": 10, "template_selections": [{"bank_id": 5, "count": 20, "category": "verbal"}]}

    # Relationships
    company = relationship("Company", back_populates="exams")
    creator = relationship("User", foreign_keys=[created_by])
    questions = relationship(
        "ExamQuestion", back_populates="exam", cascade="all, delete-orphan"
    )
    sessions = relationship(
        "ExamSession", back_populates="exam", cascade="all, delete-orphan"
    )
    assignments = relationship(
        "ExamAssignment", back_populates="exam", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return (
            f"<Exam(id={self.id}, title='{self.title}', company_id={self.company_id})>"
        )


class ExamQuestion(BaseModel):
    """Question within an exam."""

    __tablename__ = "exam_questions"
    exam_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("exams.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Question content
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    question_type: Mapped[QuestionType] = mapped_column(SQLAlchemyEnum(QuestionType), nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Question settings
    points: Mapped[float | None] = mapped_column(Float, default=1.0)
    time_limit_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_required: Mapped[bool | None] = mapped_column(Boolean, default=True)

    # Multiple choice / Single choice options
    options: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    correct_answers: Mapped[dict | None] = mapped_column(
        JSON, nullable=True
    )  # ["A", "B"] for multiple choice, ["A"] for single

    # Text input / Essay settings
    max_length: Mapped[int | None] = mapped_column(Integer, nullable=True)
    min_length: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Rating settings
    rating_scale: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Additional metadata
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    tags: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Source tracking (for hybrid exams)
    source_type: Mapped[str] = mapped_column(
        String(20), nullable=False, default="custom", index=True
    )  # "custom", "template", "question_bank"
    source_bank_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("question_banks.id", ondelete="SET NULL"), nullable=True
    )  # If from question bank
    source_question_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("question_bank_items.id", ondelete="SET NULL"),
        nullable=True,
    )  # Original question

    # Relationships
    exam = relationship("Exam", back_populates="questions")
    answers = relationship(
        "ExamAnswer", back_populates="question", cascade="all, delete-orphan"
    )
    source_bank = relationship("QuestionBank", foreign_keys=[source_bank_id])
    source_question = relationship(
        "QuestionBankItem",
        foreign_keys=[source_question_id],
        back_populates="used_in_exams",
    )

    def __repr__(self):
        return f"<ExamQuestion(id={self.id}, exam_id={self.exam_id}, type='{self.question_type}')>"


class ExamSession(BaseModel):
    """Individual exam session for a candidate."""

    __tablename__ = "exam_sessions"
    exam_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("exams.id", ondelete="CASCADE"), nullable=False, index=True
    )
    candidate_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    assignment_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("exam_assignments.id", ondelete="SET NULL"), nullable=True
    )

    # Session info
    status: Mapped[SessionStatus] = mapped_column(
        SQLAlchemyEnum(SessionStatus), nullable=False, default=SessionStatus.NOT_STARTED
    )
    attempt_number: Mapped[int | None] = mapped_column(Integer, default=1)

    # Timing
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    time_remaining_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Progress
    current_question_index: Mapped[int | None] = mapped_column(Integer, default=0)
    total_questions: Mapped[int] = mapped_column(Integer, nullable=False)
    questions_answered: Mapped[int | None] = mapped_column(Integer, default=0)

    # Results
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    max_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    percentage: Mapped[float | None] = mapped_column(Float, nullable=True)
    passed: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    # Monitoring data
    web_usage_detected: Mapped[bool | None] = mapped_column(Boolean, default=False)
    web_usage_count: Mapped[int | None] = mapped_column(Integer, default=0)
    face_verification_failed: Mapped[bool | None] = mapped_column(Boolean, default=False)
    face_check_count: Mapped[int | None] = mapped_column(Integer, default=0)
    face_verification_data: Mapped[dict | None] = mapped_column(
        JSON, nullable=True
    )  # Face check timestamps and results

    # Browser/Environment info
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    screen_resolution: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # Relationships
    exam = relationship("Exam", back_populates="sessions")
    candidate = relationship("User", foreign_keys=[candidate_id])
    assignment = relationship("ExamAssignment", back_populates="sessions")
    answers = relationship(
        "ExamAnswer", back_populates="session", cascade="all, delete-orphan"
    )
    monitoring_events = relationship(
        "ExamMonitoringEvent", back_populates="session", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<ExamSession(id={self.id}, exam_id={self.exam_id}, candidate_id={self.candidate_id})>"


class ExamAnswer(Base):
    """Candidate's answer to a specific question."""

    __tablename__ = "exam_answers"

    id: Mapped[int | None] = mapped_column(Integer, primary_key=True, index=True)
    session_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("exam_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    question_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("exam_questions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Answer data
    answer_data: Mapped[dict | None] = mapped_column(
        JSON, nullable=True
    )  # Flexible storage for different answer types
    answer_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    selected_options: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Scoring
    is_correct: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    points_earned: Mapped[float | None] = mapped_column(Float, default=0.0)
    points_possible: Mapped[float] = mapped_column(Float, nullable=False)

    # Timing
    time_spent_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    answered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    session = relationship("ExamSession", back_populates="answers")
    question = relationship("ExamQuestion", back_populates="answers")

    def __repr__(self):
        return f"<ExamAnswer(id={self.id}, session_id={self.session_id}, question_id={self.question_id})>"


class ExamAssignment(BaseModel):
    """Assignment of exam to specific candidates."""

    __tablename__ = "exam_assignments"
    exam_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("exams.id", ondelete="CASCADE"), nullable=False, index=True
    )
    candidate_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    assigned_by: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    # Assignment settings (override exam defaults)
    due_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    custom_time_limit_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    custom_max_attempts: Mapped[int | None] = mapped_column(Integer, nullable=True)
    custom_is_randomized: Mapped[bool | None] = mapped_column(
        Boolean, nullable=True
    )  # Override exam default randomization

    # Status
    is_active: Mapped[bool | None] = mapped_column(Boolean, default=True)
    completed: Mapped[bool | None] = mapped_column(Boolean, default=False)

    # Notifications
    notification_sent: Mapped[bool | None] = mapped_column(Boolean, default=False)
    reminder_sent: Mapped[bool | None] = mapped_column(Boolean, default=False)

    # Workflow integration (for exam TODOs)
    todo_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("todos.id", ondelete="SET NULL"), nullable=True, index=True
    )
    workflow_node_execution_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("workflow_node_executions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Relationships
    exam = relationship("Exam", back_populates="assignments")
    candidate = relationship("User", foreign_keys=[candidate_id])
    assigner = relationship("User", foreign_keys=[assigned_by])
    sessions = relationship("ExamSession", back_populates="assignment")
    todo = relationship(
        "Todo", foreign_keys=[todo_id], backref="exam_assignment", uselist=False
    )
    workflow_node_execution = relationship(
        "WorkflowNodeExecution", foreign_keys=[workflow_node_execution_id]
    )

    def __repr__(self):
        return f"<ExamAssignment(id={self.id}, exam_id={self.exam_id}, candidate_id={self.candidate_id})>"


class ExamMonitoringEvent(Base):
    """Monitoring events during exam sessions."""

    __tablename__ = "exam_monitoring_events"

    id: Mapped[int | None] = mapped_column(Integer, primary_key=True, index=True)
    session_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("exam_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    event_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # "web_usage", "face_check", "tab_switch", etc.
    event_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    severity: Mapped[str | None] = mapped_column(String(20), default="info")

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    session = relationship("ExamSession", back_populates="monitoring_events")

    def __repr__(self):
        return f"<ExamMonitoringEvent(id={self.id}, session_id={self.session_id}, type='{self.event_type}')>"
