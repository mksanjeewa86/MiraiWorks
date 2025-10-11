# Import all models to ensure they are registered with SQLAlchemy
from app.models.attachment import Attachment
from app.models.audit import AuditLog
from app.models.auth import OauthAccount, PasswordResetRequest, RefreshToken
from app.models.calendar_connection import CalendarConnection
from app.models.calendar_event import CalendarEvent
from app.models.calendar_integration import ExternalCalendarAccount, SyncedEvent
from app.models.candidate_workflow import CandidateWorkflow
from app.models.company import Company
from app.models.company_subscription import CompanySubscription
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
from app.models.feature import Feature
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
from app.models.plan_change_request import PlanChangeRequest
from app.models.plan_feature import PlanFeature
from app.models.position import CompanyProfile, Position, PositionApplication
from app.models.question_bank import QuestionBank, QuestionBankItem
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
from app.models.subscription_plan import SubscriptionPlan
from app.models.system_update import SystemUpdate
from app.models.todo import Todo
from app.models.todo_attachment import TodoAttachment
from app.models.todo_extension_request import TodoExtensionRequest
from app.models.todo_viewer import TodoViewer
from app.models.user import User
from app.models.user_connection import UserConnection
from app.models.user_settings import UserSettings
from app.models.video_call import (
    CallParticipant,
    CallTranscription,
    RecordingConsent,
    TranscriptionSegment,
    VideoCall,
)
from app.models.workflow import Workflow
from app.models.workflow_node import WorkflowNode
from app.models.workflow_node_connection import WorkflowNodeConnection
from app.models.workflow_node_execution import WorkflowNodeExecution
from app.models.workflow_viewer import WorkflowViewer

__all__ = [
    "Company",
    "User",
    "UserConnection",
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
    "Workflow",
    "WorkflowNode",
    "WorkflowNodeConnection",
    "WorkflowNodeExecution",
    "WorkflowViewer",
    "CandidateWorkflow",
    "QuestionBank",
    "QuestionBankItem",
    "SubscriptionPlan",
    "Feature",
    "PlanFeature",
    "CompanySubscription",
    "PlanChangeRequest",
    "SystemUpdate",
]
