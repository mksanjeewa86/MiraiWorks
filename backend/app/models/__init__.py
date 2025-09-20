# Import all models to ensure they are registered with SQLAlchemy
from .attachment import Attachment
from .audit import AuditLog
from .auth import OauthAccount, PasswordResetRequest, RefreshToken
from .company import Company
from .direct_message import DirectMessage
from .interview import Interview, InterviewProposal
from .job import CompanyProfile, Job, JobApplication
from .meeting import (
    Meeting,
    MeetingRecording,
    MeetingSummary,
    MeetingTranscript,
    meeting_participants,
)
from .notification import Notification
from .resume import (
    Certification,
    Education,
    Language,
    Project,
    Reference,
    Resume,
    Skill,
    WorkExperience,
)
from .role import Role, UserRole
from .user import User
from .todo import Todo
from .user_settings import UserSettings

__all__ = [
    "Company",
    "User",
    "Role",
    "UserRole",
    "RefreshToken",
    "PasswordResetRequest",
    "OauthAccount",
    "AuditLog",
    "Notification",
    "DirectMessage",
    "Attachment",
    "Interview",
    "InterviewProposal",
    "Resume",
    "WorkExperience",
    "Education",
    "Skill",
    "Project",
    "Certification",
    "Language",
    "Reference",
    "Meeting",
    "MeetingRecording",
    "MeetingTranscript",
    "MeetingSummary",
    "meeting_participants",
    "Job",
    "JobApplication",
    "CompanyProfile",
    "UserSettings",
    "Todo",
]
