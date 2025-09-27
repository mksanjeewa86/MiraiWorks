# Import all models to ensure they are registered with SQLAlchemy
from .attachment import Attachment
from .audit import AuditLog
from .auth import OauthAccount, PasswordResetRequest, RefreshToken
from .calendar_connection import CalendarConnection
from .calendar_integration import ExternalCalendarAccount, SyncedEvent
from .company import Company
from .exam import (
    Exam,
    ExamAnswer,
    ExamAssignment,
    ExamMonitoringEvent,
    ExamQuestion,
    ExamSession,
    ExamStatus,
    ExamType,
    QuestionType,
    SessionStatus,
)
from .interview import Interview, InterviewProposal
from .interview_note import InterviewNote
from .mbti_model import MBTIQuestion, MBTITest
from .meeting import (
    Meeting,
    MeetingRecording,
    MeetingSummary,
    MeetingTranscript,
    meeting_participants,
)
from .message import Message
from .notification import Notification
from .position import CompanyProfile, Position, PositionApplication
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
from .todo import Todo
from .todo_attachment import TodoAttachment
from .todo_extension_request import TodoExtensionRequest
from .todo_viewer import TodoViewer
from .user import User
from .user_settings import UserSettings
from .video_call import (
    CallParticipant,
    CallTranscription,
    RecordingConsent,
    TranscriptionSegment,
    VideoCall,
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
    "MBTITest",
    "MBTIQuestion",
    "ExternalCalendarAccount",
    "SyncedEvent",
    "CalendarConnection",
    "Exam",
    "ExamQuestion",
    "ExamSession",
    "ExamAnswer",
    "ExamAssignment",
    "ExamMonitoringEvent",
    "ExamType",
    "ExamStatus",
    "QuestionType",
    "SessionStatus",
]
