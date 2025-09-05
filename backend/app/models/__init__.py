# Import all models to ensure they are registered with SQLAlchemy
from .company import Company
from .user import User
from .role import Role, UserRole
from .auth import RefreshToken, PasswordResetRequest, OauthAccount
from .audit import AuditLog
from .notification import Notification
from .message import Conversation, Message, MessageRead, conversation_participants
from .attachment import Attachment
from .interview import Interview, InterviewProposal
from .resume import Resume, WorkExperience, Education, Skill, Project, Certification, Language, Reference
from .meeting import Meeting, MeetingRecording, MeetingTranscript, MeetingSummary, meeting_participants
from .job import Job, JobApplication, CompanyProfile

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
    "Conversation",
    "Message",
    "MessageRead",
    "conversation_participants",
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
]