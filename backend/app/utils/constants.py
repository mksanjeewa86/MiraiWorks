from enum import Enum


class UserRole(str, Enum):
    SUPER_ADMIN = "super_admin"
    COMPANY_ADMIN = "company_admin"
    RECRUITER = "recruiter"
    EMPLOYER = "employer"
    CANDIDATE = "candidate"


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


class NotificationType(str, Enum):
    PASSWORD_RESET_REQUEST = "password_reset_request"
    INTERVIEW_PROPOSAL = "interview_proposal"
    INTERVIEW_ACCEPTED = "interview_accepted"
    INTERVIEW_CANCELLED = "interview_cancelled"
    MESSAGE_RECEIVED = "message_received"
    SYSTEM_NOTIFICATION = "system_notification"

class TodoStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    EXPIRED = "expired"


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
