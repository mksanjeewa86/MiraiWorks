from enum import Enum

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class ExamType(str, Enum):
    # General Categories
    APTITUDE = "aptitude"  # 適性検査
    SKILL = "skill"
    KNOWLEDGE = "knowledge"
    PERSONALITY = "personality"
    CUSTOM = "custom"

    # Japanese Aptitude Tests (適性検査)
    SPI = "spi"  # SPI（総合適性検査）
    TAMATEBAKO = "tamatebako"  # 玉手箱
    CAB = "cab"  # CAB（IT適性検査）
    GAB = "gab"  # GAB（総合適性検査）
    TG_WEB = "tg_web"  # TG-WEB
    CUBIC = "cubic"  # CUBIC
    NTT = "ntt_aptitude"  # NTT適性検査
    KRAEPELIN = "kraepelin"  # クレペリン検査
    SJT = "sjt"  # 状況判断テスト

    # Technical/Industry-Specific
    PROGRAMMING_APTITUDE = "programming_aptitude"  # プログラミング適性検査
    NUMERICAL_ABILITY = "numerical_ability"  # 数理能力検査
    VERBAL_ABILITY = "verbal_ability"  # 言語能力検査
    LOGICAL_THINKING = "logical_thinking"  # 論理思考テスト


class ExamStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"


class QuestionType(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    SINGLE_CHOICE = "single_choice"
    TEXT_INPUT = "text_input"
    ESSAY = "essay"
    TRUE_FALSE = "true_false"
    RATING = "rating"
    MATCHING = "matching"


class SessionStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    EXPIRED = "expired"
    SUSPENDED = "suspended"


class Exam(Base):
    """Recruitment exam model."""

    __tablename__ = "exams"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    exam_type = Column(
        SQLAlchemyEnum(ExamType), nullable=False, default=ExamType.CUSTOM
    )
    status = Column(
        SQLAlchemyEnum(ExamStatus), nullable=False, default=ExamStatus.DRAFT
    )

    # Organization settings
    company_id = Column(
        Integer,
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_by = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    # Exam settings
    time_limit_minutes = Column(Integer, nullable=True)  # null = no time limit
    max_attempts = Column(Integer, default=1)  # Number of times candidate can take exam
    passing_score = Column(Float, nullable=True)  # null = no passing score
    is_randomized = Column(Boolean, default=False)  # Random question order

    # Web monitoring settings
    allow_web_usage = Column(Boolean, default=True)
    monitor_web_usage = Column(Boolean, default=False)

    # Face recognition settings
    require_face_verification = Column(Boolean, default=False)
    face_check_interval_minutes = Column(Integer, default=5)  # How often to check face

    # Result settings
    show_results_immediately = Column(Boolean, default=True)
    show_correct_answers = Column(Boolean, default=False)
    show_score = Column(Boolean, default=True)

    # Metadata
    instructions = Column(Text, nullable=True)  # Instructions for candidates
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

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


class ExamQuestion(Base):
    """Question within an exam."""

    __tablename__ = "exam_questions"

    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(
        Integer, ForeignKey("exams.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Question content
    question_text = Column(Text, nullable=False)
    question_type = Column(SQLAlchemyEnum(QuestionType), nullable=False)
    order_index = Column(Integer, nullable=False, default=0)  # Order within exam

    # Question settings
    points = Column(Float, default=1.0)  # Points for correct answer
    time_limit_seconds = Column(Integer, nullable=True)  # Per-question time limit
    is_required = Column(Boolean, default=True)

    # Multiple choice / Single choice options
    options = Column(JSON, nullable=True)  # {"A": "Option 1", "B": "Option 2", ...}
    correct_answers = Column(
        JSON, nullable=True
    )  # ["A", "B"] for multiple choice, ["A"] for single

    # Text input / Essay settings
    max_length = Column(Integer, nullable=True)
    min_length = Column(Integer, nullable=True)

    # Rating settings
    rating_scale = Column(Integer, nullable=True)  # 1-5, 1-10, etc.

    # Additional metadata
    explanation = Column(Text, nullable=True)  # Explanation of correct answer
    tags = Column(JSON, nullable=True)  # ["skill", "logic", ...] for categorization

    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    exam = relationship("Exam", back_populates="questions")
    answers = relationship(
        "ExamAnswer", back_populates="question", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<ExamQuestion(id={self.id}, exam_id={self.exam_id}, type='{self.question_type}')>"


class ExamSession(Base):
    """Individual exam session for a candidate."""

    __tablename__ = "exam_sessions"

    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(
        Integer, ForeignKey("exams.id", ondelete="CASCADE"), nullable=False, index=True
    )
    candidate_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    assignment_id = Column(
        Integer, ForeignKey("exam_assignments.id", ondelete="SET NULL"), nullable=True
    )

    # Session info
    status = Column(
        SQLAlchemyEnum(SessionStatus), nullable=False, default=SessionStatus.NOT_STARTED
    )
    attempt_number = Column(Integer, default=1)

    # Timing
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    time_remaining_seconds = Column(Integer, nullable=True)

    # Progress
    current_question_index = Column(Integer, default=0)
    total_questions = Column(Integer, nullable=False)
    questions_answered = Column(Integer, default=0)

    # Results
    score = Column(Float, nullable=True)  # Final score
    max_score = Column(Float, nullable=True)  # Maximum possible score
    percentage = Column(Float, nullable=True)  # Score as percentage
    passed = Column(Boolean, nullable=True)  # Did candidate pass?

    # Monitoring data
    web_usage_detected = Column(Boolean, default=False)
    web_usage_count = Column(Integer, default=0)
    face_verification_failed = Column(Boolean, default=False)
    face_check_count = Column(Integer, default=0)
    face_verification_data = Column(
        JSON, nullable=True
    )  # Face check timestamps and results

    # Browser/Environment info
    user_agent = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    screen_resolution = Column(String(20), nullable=True)

    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

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

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(
        Integer,
        ForeignKey("exam_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    question_id = Column(
        Integer,
        ForeignKey("exam_questions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Answer data
    answer_data = Column(
        JSON, nullable=True
    )  # Flexible storage for different answer types
    answer_text = Column(Text, nullable=True)  # For text/essay questions
    selected_options = Column(JSON, nullable=True)  # For multiple choice: ["A", "B"]

    # Scoring
    is_correct = Column(Boolean, nullable=True)  # Null for manual grading needed
    points_earned = Column(Float, default=0.0)
    points_possible = Column(Float, nullable=False)

    # Timing
    time_spent_seconds = Column(Integer, nullable=True)
    answered_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    session = relationship("ExamSession", back_populates="answers")
    question = relationship("ExamQuestion", back_populates="answers")

    def __repr__(self):
        return f"<ExamAnswer(id={self.id}, session_id={self.session_id}, question_id={self.question_id})>"


class ExamAssignment(Base):
    """Assignment of exam to specific candidates."""

    __tablename__ = "exam_assignments"

    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(
        Integer, ForeignKey("exams.id", ondelete="CASCADE"), nullable=False, index=True
    )
    candidate_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    assigned_by = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    # Assignment settings
    due_date = Column(DateTime(timezone=True), nullable=True)
    custom_time_limit_minutes = Column(Integer, nullable=True)  # Override exam default
    custom_max_attempts = Column(Integer, nullable=True)  # Override exam default

    # Status
    is_active = Column(Boolean, default=True)
    completed = Column(Boolean, default=False)

    # Notifications
    notification_sent = Column(Boolean, default=False)
    reminder_sent = Column(Boolean, default=False)

    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    exam = relationship("Exam", back_populates="assignments")
    candidate = relationship("User", foreign_keys=[candidate_id])
    assigner = relationship("User", foreign_keys=[assigned_by])
    sessions = relationship("ExamSession", back_populates="assignment")

    def __repr__(self):
        return f"<ExamAssignment(id={self.id}, exam_id={self.exam_id}, candidate_id={self.candidate_id})>"


class ExamMonitoringEvent(Base):
    """Monitoring events during exam sessions."""

    __tablename__ = "exam_monitoring_events"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(
        Integer,
        ForeignKey("exam_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    event_type = Column(
        String(50), nullable=False
    )  # "web_usage", "face_check", "tab_switch", etc.
    event_data = Column(JSON, nullable=True)  # Flexible data storage
    severity = Column(String(20), default="info")  # "info", "warning", "critical"

    timestamp = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    session = relationship("ExamSession", back_populates="monitoring_events")

    def __repr__(self):
        return f"<ExamMonitoringEvent(id={self.id}, session_id={self.session_id}, type='{self.event_type}')>"
