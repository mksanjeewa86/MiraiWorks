# Import all models to ensure they are registered with SQLAlchemy
from .attachment import Attachment
from .audit import AuditLog
from .auth import OauthAccount, PasswordResetRequest, RefreshToken
from .company import Company
from .message import Message
from .interview import Interview, InterviewProposal
from .interview_note import InterviewNote
from .position import CompanyProfile, Position, PositionApplication
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
from .todo_attachment import TodoAttachment
from .todo_extension_request import TodoExtensionRequest
from .todo_viewer import TodoViewer
from .user_settings import UserSettings
from .video_call import (
    VideoCall,
    CallParticipant,
    RecordingConsent,
    CallTranscription,
    TranscriptionSegment,
)

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
    "Message",
    "Attachment",
    "Interview",
    "InterviewProposal",
    "InterviewNote",
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
    "CompanyProfile",
    "Position",
    "PositionApplication",
    "UserSettings",
    "Todo",
    "TodoAttachment",
    "TodoExtensionRequest",
    "TodoViewer",
    "VideoCall",
    "CallParticipant",
    "RecordingConsent",
    "CallTranscription",
    "TranscriptionSegment",
]
