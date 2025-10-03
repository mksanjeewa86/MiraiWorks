from enum import Enum


class UserRole(str, Enum):
    SYSTEM_ADMIN = "system_admin"  # System-level administrator
    ADMIN = "admin"  # Company administrator (context: company_type)
    MEMBER = "member"  # Company member (context: company_type)
    CANDIDATE = "candidate"  # Job candidate (no company affiliation)


class CompanyType(str, Enum):
    RECRUITER = "recruiter"
    EMPLOYER = "employer"


class MessageType(str, Enum):
    TEXT = "text"
    FILE = "file"
    SYSTEM = "system"


class InterviewStatus(str, Enum):
    PENDING_SCHEDULE = "pending_schedule"
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ProposalStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    EXPIRED = "expired"


class ResumeStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class ResumeVisibility(str, Enum):
    PRIVATE = "private"
    PUBLIC = "public"
    UNLISTED = "unlisted"  # Public but not searchable


class SectionType(str, Enum):
    SUMMARY = "summary"
    EXPERIENCE = "experience"
    EDUCATION = "education"
    SKILLS = "skills"
    PROJECTS = "projects"
    CERTIFICATIONS = "certifications"
    LANGUAGES = "languages"
    REFERENCES = "references"
    CUSTOM = "custom"


class ResumeFormat(str, Enum):
    RIREKISHO = "rirekisho"  # 履歴書 - Traditional Japanese resume
    SHOKUMU_KEIREKISHO = "shokumu_keirekisho"  # 職務経歴書 - Career history
    INTERNATIONAL = "international"  # Standard international resume
    MODERN = "modern"  # Modern format
    CREATIVE = "creative"  # Creative format


class ResumeLanguage(str, Enum):
    JAPANESE = "ja"
    ENGLISH = "en"
    BILINGUAL = "bilingual"


class NotificationType(str, Enum):
    PASSWORD_RESET_REQUEST = "password_reset_request"
    INTERVIEW_PROPOSAL = "interview_proposal"
    INTERVIEW_ACCEPTED = "interview_accepted"
    INTERVIEW_CANCELLED = "interview_cancelled"
    MESSAGE_RECEIVED = "message_received"
    SYSTEM_NOTIFICATION = "system_notification"
    TODO_EXTENSION_REQUEST = "todo_extension_request"
    TODO_EXTENSION_APPROVED = "todo_extension_approved"
    TODO_EXTENSION_REJECTED = "todo_extension_rejected"


class TodoStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    EXPIRED = "expired"


class TodoVisibility(str, Enum):
    PRIVATE = "private"  # Only owner can see
    PUBLIC = "public"    # Assigned user can see and interact
    VIEWER = "viewer"    # Assigned user can see but not interact


class TodoType(str, Enum):
    REGULAR = "regular"
    ASSIGNMENT = "assignment"  # For any kind of task assignment (coding test, document review, etc.)


class TodoPublishStatus(str, Enum):
    DRAFT = "draft"      # Not visible to assignee/viewers
    PUBLISHED = "published"  # Visible to assignee/viewers


class AssignmentStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"


class ExtensionRequestStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class VirusStatus(str, Enum):
    PENDING = "pending"
    CLEAN = "clean"
    INFECTED = "infected"
    ERROR = "error"


class AuditAction(str, Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    PASSWORD_RESET = "password_reset"
    BULK_IMPORT = "bulk_import"


class MBTIType(str, Enum):
    # Analysts (NT)
    INTJ = "INTJ"  # Architect
    INTP = "INTP"  # Thinker
    ENTJ = "ENTJ"  # Commander
    ENTP = "ENTP"  # Debater

    # Diplomats (NF)
    INFJ = "INFJ"  # Advocate
    INFP = "INFP"  # Mediator
    ENFJ = "ENFJ"  # Protagonist
    ENFP = "ENFP"  # Campaigner

    # Sentinels (SJ)
    ISTJ = "ISTJ"  # Logistician
    ISFJ = "ISFJ"  # Protector
    ESTJ = "ESTJ"  # Executive
    ESFJ = "ESFJ"  # Consul

    # Explorers (SP)
    ISTP = "ISTP"  # Virtuoso
    ISFP = "ISFP"  # Adventurer
    ESTP = "ESTP"  # Entrepreneur
    ESFP = "ESFP"  # Entertainer


class MBTIDimension(str, Enum):
    EXTRAVERSION_INTROVERSION = "E_I"  # E vs I
    SENSING_INTUITION = "S_N"          # S vs N
    THINKING_FEELING = "T_F"           # T vs F
    JUDGING_PERCEIVING = "J_P"         # J vs P


class MBTITestStatus(str, Enum):
    NOT_TAKEN = "not_taken"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

