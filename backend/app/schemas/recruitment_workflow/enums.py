from enum import Enum


class ProcessStatus(str, Enum):
    """Status values for recruitment processes"""
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"
    INACTIVE = "inactive"


class NodeType(str, Enum):
    """Types of nodes in a recruitment process"""
    INTERVIEW = "interview"
    TODO = "todo"
    ASSESSMENT = "assessment"
    DECISION = "decision"


class NodeStatus(str, Enum):
    """Status values for process nodes"""
    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"


class CandidateProcessStatus(str, Enum):
    """Status values for candidate processes"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    WITHDRAWN = "withdrawn"
    ON_HOLD = "on_hold"


class ExecutionStatus(str, Enum):
    """Status values for node executions"""
    PENDING = "pending"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    AWAITING_INPUT = "awaiting_input"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class ExecutionResult(str, Enum):
    """Result values for node executions"""
    PASS = "pass"
    FAIL = "fail"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    SKIPPED = "skipped"


class ConnectionConditionType(str, Enum):
    """Condition types for node connections"""
    SUCCESS = "success"
    FAILURE = "failure"
    CONDITIONAL = "conditional"
    ALWAYS = "always"


class ViewerRole(str, Enum):
    """Roles for process viewers"""
    RECRUITER = "recruiter"
    OBSERVER = "observer"
    ADMIN = "admin"
    ASSISTANT = "assistant"


class InterviewNodeType(str, Enum):
    """Types of interviews in interview nodes"""
    VIDEO = "video"
    PHONE = "phone"
    IN_PERSON = "in_person"


class TodoNodeType(str, Enum):
    """Types of todos in todo nodes"""
    ASSIGNMENT = "assignment"
    ASSESSMENT = "assessment"
    DOCUMENT_UPLOAD = "document_upload"
    CODING_TEST = "coding_test"
    APTITUDE_TEST = "aptitude_test"


class SubmissionType(str, Enum):
    """Types of submissions for todo nodes"""
    FILE = "file"
    TEXT = "text"
    CODE = "code"
    LINK = "link"
    MULTIPLE_CHOICE = "multiple_choice"


class FinalResult(str, Enum):
    """Final results for candidate processes"""
    HIRED = "hired"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"
    FAILED = "failed"
    ON_HOLD = "on_hold"


class Priority(str, Enum):
    """Priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"