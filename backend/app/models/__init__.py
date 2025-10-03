# Import all models to ensure they are registered with SQLAlchemy
from app.models.attachment import Attachment
from app.models.audit import AuditLog
from app.models.auth import OauthAccount, PasswordResetRequest, RefreshToken
from app.models.calendar_connection import CalendarConnection
from app.models.calendar_event import CalendarEvent
from app.models.calendar_integration import ExternalCalendarAccount, SyncedEvent
from app.models.company import Company
from app.models.connection_invitation import ConnectionInvitation
from app.models.exam import (
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
from app.models.holiday import Holiday
from app.models.interview import Interview, InterviewProposal
from app.models.interview_note import InterviewNote
from app.models.mbti_model import MBTIQuestion, MBTITest
from app.models.meeting import (
    Meeting,
    MeetingRecording,
    MeetingSummary,
    MeetingTranscript,
    meeting_participants,
)
from app.models.message import Message
from app.models.notification import Notification
from app.models.position import CompanyProfile, Position, PositionApplication
from app.models.candidate_process import CandidateProcess
from app.models.node_connection import NodeConnection
from app.models.node_execution import NodeExecution
from app.models.process_node import ProcessNode
from app.models.process_viewer import ProcessViewer
from app.models.recruitment_process import RecruitmentProcess
from app.models.resume import (
    Certification,
    Education,
    Language,
    Project,
    Reference,
    Resume,
    Skill,
    WorkExperience,
)
from app.models.role import Role, UserRole
from app.models.todo import Todo
from app.models.todo_attachment import TodoAttachment
from app.models.todo_extension_request import TodoExtensionRequest
from app.models.todo_viewer import TodoViewer
from app.models.user import User
from app.models.user_connection import UserConnection
from app.models.company_follow import CompanyFollow
from app.models.company_connection import CompanyConnection
from app.models.user_settings import UserSettings
from app.models.video_call import (
    CallParticipant,
    CallTranscription,
    RecordingConsent,
    TranscriptionSegment,
    VideoCall,
)

__all__ = [
    "Company",
    "User",
    "UserConnection",
    "CompanyFollow",
    "CompanyConnection",
    "ConnectionInvitation",
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
    "CandidateProcess",
    "NodeConnection",
    "NodeExecution",
    "ProcessNode",
    "ProcessViewer",
    "RecruitmentProcess",
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
    "CalendarEvent",
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
    "Holiday",
]
