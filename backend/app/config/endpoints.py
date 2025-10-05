"""
Centralized API endpoint path configuration.

This module defines all API endpoint paths in a single location for consistency
and easy maintenance. Use these constants when defining routes in endpoint files.

Example usage:
    from app.config.endpoints import API_ROUTES

    router = APIRouter()

    @router.post(API_ROUTES.AUTH.LOGIN)
    async def login(...):
        pass
"""

from collections.abc import Callable


class EndpointPath:
    """Helper class for creating parameterized endpoint paths."""

    @staticmethod
    def with_id(base: str, param: str = "id") -> Callable[[str | int], str]:
        """Create a function that generates paths with ID parameter.

        Args:
            base: Base path (e.g., "/api/users")
            param: Parameter name (default: "id")

        Returns:
            Function that takes an ID and returns the full path
        """
        return lambda id_val: f"{base}/{{{param}}}"

    @staticmethod
    def format(template: str) -> str:
        """Return the template as-is for use in FastAPI route decorators."""
        return template


class AuthRoutes:
    """Authentication and authorization endpoints."""

    LOGIN = "/login"
    REGISTER = "/register"
    LOGOUT = "/logout"
    REFRESH = "/refresh"
    ME = "/me"
    CHANGE_PASSWORD = "/change-password"

    # 2FA endpoints
    TWO_FA_VERIFY = "/2fa/verify"

    # Password reset endpoints
    PASSWORD_RESET_REQUEST = "/password-reset/request"
    PASSWORD_RESET_APPROVE = "/password-reset/approve"
    PASSWORD_RESET_REQUESTS = "/password-reset/requests"

    # Account activation
    ACTIVATE_ACCOUNT = "/activate"


class UserRoutes:
    """User management endpoints."""

    BASE = "/users"
    BY_ID = "/users/{user_id}"
    PROFILE = "/user/profile"
    SETTINGS = "/user/settings"

    # Admin user endpoints (used with /api/admin prefix)
    ADMIN_USERS = "/users"
    ADMIN_USER_BY_ID = "/users/{user_id}"
    ADMIN_USER_RESET_PASSWORD = "/users/{user_id}/reset-password"
    ADMIN_USER_RESEND_ACTIVATION = "/users/{user_id}/resend-activation"
    ADMIN_USER_SUSPEND = "/users/{user_id}/suspend"
    ADMIN_USER_UNSUSPEND = "/users/{user_id}/unsuspend"


class CompanyRoutes:
    """Company management endpoints."""

    BASE = "/companies"
    BY_ID = "/companies/{company_id}"
    CREATE = "/companies"
    UPDATE = "/companies/{company_id}"
    DELETE = "/companies/{company_id}"
    ADMIN_STATUS = "/companies/{company_id}/admin-status"


class PositionRoutes:
    """Job position endpoints."""

    BASE = ""
    BASE_SLASH = "/"
    BY_ID = "/{position_id}"
    BY_SLUG = "/slug/{slug}"
    PUBLIC = "/public/positions"
    POPULAR = "/popular"
    RECENT = "/recent"
    COMPANY = "/company/{company_id}"
    EXPIRING = "/expiring"
    STATISTICS = "/statistics"
    STATUS = "/{position_id}/status"
    BULK_STATUS = "/bulk/status"


class InterviewRoutes:
    """Interview management endpoints."""

    BASE = ""
    BASE_SLASH = "/"
    BY_ID = "/{interview_id}"
    STATUS = "/{interview_id}/status"
    SCHEDULE = "/{interview_id}/schedule"
    PROPOSALS = "/{interview_id}/proposals"
    PROPOSAL_RESPOND = "/{interview_id}/proposals/{proposal_id}/respond"
    CANCEL = "/{interview_id}/cancel"
    RESCHEDULE = "/{interview_id}/reschedule"
    STATS_SUMMARY = "/stats/summary"
    CALENDAR_EVENTS = "/calendar/events"
    CALENDAR_INTEGRATION_STATUS = "/calendar/integration-status"
    NOTES = "/{interview_id}/notes"
    VIDEO_CALL = "/{interview_id}/video-call"


class ExamRoutes:
    """Exam system endpoints."""

    # Exam management
    BASE = "/exams"
    BY_ID = "/exams/{exam_id}"
    TAKE = "/exams/take"
    MY_ASSIGNMENTS = "/my-assignments"
    HYBRID = "/exams/hybrid"  # NEW: Create hybrid exam
    CLONE = "/exams/{exam_id}/clone"  # NEW: Clone exam to company

    # Exam operations
    STATISTICS = "/exams/{exam_id}/statistics"
    EXPORT_PDF = "/exams/{exam_id}/export/pdf"
    EXPORT_EXCEL = "/exams/{exam_id}/export/excel"

    # Questions
    QUESTIONS = "/exams/{exam_id}/questions"
    QUESTION_BY_ID = "/questions/{question_id}"

    # Assignments
    ASSIGNMENTS = "/exams/{exam_id}/assignments"
    ASSIGNMENT_BY_ID = "/assignments/{assignment_id}"

    # Sessions
    SESSIONS = "/exams/{exam_id}/sessions"
    SESSION_BY_ID = "/sessions/{session_id}"
    SESSION_ANSWERS = "/sessions/{session_id}/answers"
    SESSION_COMPLETE = "/sessions/{session_id}/complete"
    SESSION_RESULTS = "/sessions/{session_id}/results"
    SESSION_DETAILS = "/sessions/{session_id}/details"
    SESSION_SUSPEND = "/sessions/{session_id}/suspend"
    SESSION_RESET = "/sessions/{session_id}/reset"
    SESSION_MONITORING = "/sessions/{session_id}/monitoring"
    SESSION_FACE_VERIFICATION = "/sessions/{session_id}/face-verification"

    # Templates
    TEMPLATES = "/templates"
    TEMPLATE_BY_ID = "/templates/{template_id}"
    TEMPLATE_FROM_EXAM = "/templates/from-exam/{exam_id}"


class QuestionBankRoutes:
    """Question bank endpoints."""

    # Question banks
    BASE = "/question-banks"
    BY_ID = "/question-banks/{bank_id}"

    # Bank questions
    QUESTIONS = "/question-banks/{bank_id}/questions"
    QUESTION_BY_ID = "/questions/{question_id}"

    # Statistics
    STATS = "/question-banks/{bank_id}/stats"


class VideoCallRoutes:
    """Video call endpoints."""

    BASE = "/"
    SCHEDULE = "/schedule"
    BY_ID = "/{call_id}"
    BY_ROOM = "/room/{room_id}"
    JOIN = "/{call_id}/join"
    JOIN_ROOM = "/room/{room_id}/join"
    LEAVE = "/{call_id}/leave"
    LEAVE_ROOM = "/room/{room_id}/leave"
    END = "/{call_id}/end"
    CONSENT = "/{call_id}/consent"
    CONSENT_ROOM = "/room/{room_id}/consent"
    TOKEN = "/{call_id}/token"

    # Transcription
    TRANSCRIPT = "/{call_id}/transcript"
    TRANSCRIPT_SEGMENTS = "/{call_id}/transcript/segments"
    TRANSCRIPT_DOWNLOAD = "/{call_id}/transcript/download"


class CalendarRoutes:
    """Calendar and event endpoints."""

    # OAuth
    GOOGLE_OAUTH_START = "/oauth/google/start"
    GOOGLE_OAUTH_CALLBACK = "/oauth/google/callback"
    MICROSOFT_OAUTH_START = "/oauth/microsoft/start"
    MICROSOFT_OAUTH_CALLBACK = "/oauth/microsoft/callback"

    # Calendar accounts
    ACCOUNTS = "/accounts"
    ACCOUNT_BY_ID = "/accounts/{account_id}"
    ACCOUNT_SYNC = "/accounts/{account_id}/sync"

    # Calendars list
    CALENDARS = "/calendars"

    # Events (main)
    EVENTS = "/events"
    EVENT_BY_ID = "/events/{event_id}"

    # Events filtering/search
    EVENTS_RANGE = "/events/range"
    EVENTS_UPCOMING = "/events/upcoming"
    EVENTS_SEARCH = "/events/search"
    EVENTS_BULK = "/events/bulk"

    # Webhooks
    WEBHOOKS_GOOGLE = "/webhooks/google"
    WEBHOOKS_MICROSOFT = "/webhooks/microsoft"


class MessageRoutes:
    """Messaging system endpoints."""

    BASE = "/messages"
    BY_ID = "/messages/{message_id}"
    CONVERSATIONS = "/conversations"
    WITH_USER = "/with/{other_user_id}"
    SEND = "/send"
    MARK_READ_SINGLE = "/mark-read"
    MARK_READ_CONVERSATION = "/mark-conversation-read/{other_user_id}"
    SEARCH = "/search"
    PARTICIPANTS = "/participants"

    # File uploads
    UPLOAD = "/upload"
    UPLOAD_CHUNK = "/upload/chunk"
    UPLOAD_COMPLETE = "/upload/complete"
    RESTRICTED_USERS = "/restricted-users"


class NotificationRoutes:
    """Notification endpoints."""

    BASE = "/"
    BY_ID = "/{notification_id}"
    UNREAD_COUNT = "/unread-count"
    MARK_READ = "/mark-read"
    MARK_ALL_READ = "/mark-all-read"


class TodoRoutes:
    """Todo/task management endpoints."""

    BASE = ""
    BY_ID = "/{todo_id}"
    RECENT = "/recent"
    ASSIGNABLE_USERS = "/assignable-users"
    ASSIGNED = "/assigned"
    DETAILS = "/{todo_id}/details"
    ASSIGN = "/{todo_id}/assign"
    VIEWERS = "/{todo_id}/viewers"
    COMPLETE = "/{todo_id}/complete"
    REOPEN = "/{todo_id}/reopen"
    RESTORE = "/{todo_id}/restore"

    # Attachments
    ATTACHMENTS = "/{todo_id}/attachments"
    ATTACHMENT_UPLOAD = "/{todo_id}/attachments/upload"
    ATTACHMENT_BY_ID = "/{todo_id}/attachments/{attachment_id}"
    ATTACHMENT_DOWNLOAD = "/{todo_id}/attachments/{attachment_id}/download"
    ATTACHMENT_PREVIEW = "/{todo_id}/attachments/{attachment_id}/preview"
    ATTACHMENT_BULK_DELETE = "/{todo_id}/attachments/bulk-delete"
    ATTACHMENT_STATS = "/{todo_id}/attachments/stats"
    MY_UPLOADS = "/attachments/my-uploads"

    # Extension requests
    EXTENSION_CREATE = "/{todo_id}/extension-requests"
    EXTENSION_VALIDATE = "/extension-requests/validate/{todo_id}"
    EXTENSION_RESPOND = "/extension-requests/{request_id}/respond"
    EXTENSION_MY_REQUESTS = "/extension-requests/my-requests"
    EXTENSION_TO_REVIEW = "/extension-requests/to-review"
    EXTENSION_BY_ID = "/extension-requests/{request_id}"


class TodoAttachmentRoutes:
    """Todo attachment endpoints."""

    UPLOAD = "/todos/{todo_id}/attachments/upload"
    LIST = "/todos/{todo_id}/attachments"
    BY_ID = "/todos/{todo_id}/attachments/{attachment_id}"
    DOWNLOAD = "/todos/{todo_id}/attachments/{attachment_id}/download"
    PREVIEW = "/todos/{todo_id}/attachments/{attachment_id}/preview"
    DELETE = "/todos/{todo_id}/attachments/{attachment_id}"
    UPDATE = "/todos/{todo_id}/attachments/{attachment_id}"
    BULK_DELETE = "/todos/{todo_id}/attachments/bulk-delete"
    STATS = "/todos/{todo_id}/attachments/stats"
    MY_UPLOADS = "/attachments/my-uploads"
    ADMIN_CLEANUP = "/admin/attachments/cleanup"


class ResumeRoutes:
    """Resume/CV management endpoints."""

    BASE = "/"
    BY_ID = "/{resume_id}"
    STATS = "/stats"
    SEARCH = "/search"
    DUPLICATE = "/{resume_id}/duplicate"
    BY_SLUG = "/public/resume/{slug}"
    PREVIEW = "/{resume_id}/preview"
    GENERATE_PDF = "/{resume_id}/generate-pdf"
    UPLOAD_PHOTO = "/{resume_id}/upload-photo"
    REMOVE_PHOTO = "/{resume_id}/remove-photo"
    TOGGLE_PUBLIC = "/{resume_id}/toggle-public"
    CONVERT_RIREKISHO = "/{resume_id}/convert-to-rirekisho"
    CONVERT_SHOKUMU = "/{resume_id}/convert-to-shokumu"
    SEND_EMAIL = "/{resume_id}/send-email"

    # Public endpoints
    PUBLIC_VIEW = "/public/resume/{slug}/view"
    PUBLIC_DOWNLOAD = "/public/resume/{slug}/download-pdf"

    # Resume sections
    EXPERIENCES = "/{resume_id}/experiences"
    EXPERIENCE_BY_ID = "/experiences/{exp_id}"
    EDUCATION = "/{resume_id}/education"
    EDUCATION_BY_ID = "/education/{edu_id}"
    SKILLS = "/{resume_id}/skills"
    SKILL_BY_ID = "/skills/{skill_id}"
    PROJECTS = "/{resume_id}/projects"
    PROJECT_BY_ID = "/projects/{project_id}"
    CERTIFICATIONS = "/{resume_id}/certifications"
    CERTIFICATION_BY_ID = "/certifications/{cert_id}"
    LANGUAGES = "/{resume_id}/languages"
    LANGUAGE_BY_ID = "/languages/{lang_id}"

    # Templates
    TEMPLATES_AVAILABLE = "/templates/available"
    TEMPLATES_JAPANESE = "/templates/japanese"
    APPLY_TEMPLATE = "/{resume_id}/template/{template_id}"

    # Sharing and Public
    PREVIEW = "/{resume_id}/preview"
    SHARE = "/{resume_id}/share"
    SHARED = "/shared/{share_token}"
    PUBLIC = "/public/{slug}"
    PUBLIC_SETTINGS = "/{resume_id}/public-settings"
    PUBLIC_INFO = "/public/{slug}"
    PUBLIC_DOWNLOAD_SLUG = "/public/{slug}/download"

    # Analytics
    ANALYTICS = "/{resume_id}/analytics"

    # Japanese resume conversions
    CONVERT_RIREKISHO = "/{resume_id}/convert-to-rirekisho"
    CONVERT_SHOKUMU = "/{resume_id}/convert-to-shokumu"

    # Message integration
    ATTACH_TO_MESSAGE = "/{resume_id}/attach-to-message"
    AUTO_ATTACH_SETTINGS = "/{resume_id}/auto-attach-settings"
    PROTECTION = "/{resume_id}/protection"

    # Bulk operations
    BULK_ACTION = "/bulk-action"
    BULK_UPDATE = "/bulk/update"
    BULK_DELETE = "/bulk/delete"


class DashboardRoutes:
    """Dashboard and statistics endpoints."""

    BASE = "/dashboard"
    STATS = "/dashboard/stats"
    ACTIVITY = "/dashboard/activity"


class FileRoutes:
    """File upload/download endpoints."""

    TEST = "/test"
    UPLOAD = "/upload"
    DOWNLOAD = "/download/{s3_key:path}"
    DELETE = "/{s3_key:path}"
    MESSAGE_FILE = "/message/{user_id}/{filename}"


class WorkflowRoutes:
    """Recruitment workflow/process endpoints."""

    # Workflow routes
    BASE = "/"
    BY_ID = "/{workflow_id}"
    ACTIVATE = "/{workflow_id}/activate"
    ARCHIVE = "/{workflow_id}/archive"
    CLONE = "/{workflow_id}/clone"
    VALIDATE = "/{workflow_id}/validate"
    ANALYTICS = "/{workflow_id}/analytics"
    COMPANY_STATS = "/company/{company_id}/statistics"
    TEMPLATES = "/templates/"
    APPLY_TEMPLATE = "/templates/{template_id}/apply"

    # Node routes
    NODES = "/{workflow_id}/nodes"
    NODE_WITH_INTEGRATION = "/{workflow_id}/nodes/create-with-integration"
    NODE_BY_ID = "/{workflow_id}/nodes/{node_id}"

    # Candidate routes
    CANDIDATES = "/{workflow_id}/candidates"
    CANDIDATES_BULK = "/{workflow_id}/candidates/bulk"
    CANDIDATE_PROCESS_BY_ID = "/candidate-workflows/{candidate_workflow_id}"
    CANDIDATE_START = "/candidate-workflows/{candidate_workflow_id}/start"
    CANDIDATE_STATUS = "/candidate-workflows/{candidate_workflow_id}/status"
    CANDIDATE_TIMELINE = "/candidate-workflows/{candidate_workflow_id}/timeline"
    MY_PROCESSES = "/my-workflows"
    RECRUITER_WORKLOAD = "/recruiters/{recruiter_id}/workload"


class MBTIRoutes:
    """MBTI personality test endpoints."""

    START = "/start"
    QUESTIONS = "/questions"
    ANSWER = "/answer"
    SUBMIT = "/submit"
    RESULT = "/result"
    SUMMARY = "/summary"
    PROGRESS = "/progress"
    TYPES = "/types"
    TYPE_DETAILS = "/types/{mbti_type}"
    ADMIN_QUESTIONS_BULK = "/admin/questions/bulk"


class HolidayRoutes:
    """Holiday management endpoints."""

    BASE = "/"
    BY_ID = "/{holiday_id}"
    UPCOMING = "/upcoming"
    CHECK = "/check/{holiday_date}"
    BULK = "/bulk"


class AdminRoutes:
    """Administrative endpoints."""

    # Audit logs
    AUDIT_LOGS = "/admin/audit-logs"
    AUDIT_STATS = "/admin/audit-logs/stats"
    AUDIT_ACTIVITY = "/admin/audit-logs/activity"
    AUDIT_EXPORT = "/admin/audit-logs/export"
    AUDIT_FILTER_OPTIONS = "/admin/audit-logs/filter-options"

    # Bulk operations
    BULK_DELETE = "/admin/bulk/delete"
    BULK_UPDATE = "/admin/bulk/update"
    BULK_EXPORT = "/admin/bulk/export"
    BULK_IMPORT = "/admin/bulk/import"
    BULK_VALIDATE_IDS = "/admin/bulk/validate-ids"
    BULK_VALIDATE_IMPORT = "/admin/bulk/validate-import"
    BULK_PREVIEW_DELETE = "/admin/bulk/preview-delete"
    BULK_PREVIEW_UPDATE = "/admin/bulk/preview-update"
    BULK_ENTITY_COUNTS = "/admin/bulk/entity-counts"
    BULK_QUOTA = "/admin/bulk/quota"

    # Security
    SECURITY_STATS = "/admin/security/stats"
    SECURITY_FILES = "/admin/security/files"
    SECURITY_FILE_BY_ID = "/admin/security/files/{file_id}"
    SECURITY_SCAN_FILE = "/admin/security/files/{file_id}/scan"
    SECURITY_QUARANTINE = "/admin/security/files/{file_id}/quarantine"
    SECURITY_RESTORE = "/admin/security/files/{file_id}/restore"
    SECURITY_LOGS = "/admin/security/logs"
    SECURITY_BULK_ACTION = "/admin/security/bulk-action"

    # Antivirus
    ANTIVIRUS_STATUS = "/admin/security/antivirus/status"
    ANTIVIRUS_BULK_SCAN = "/admin/security/antivirus/bulk-scan"

    # System monitoring
    SYSTEM_HEALTH = "/admin/system/health"
    SYSTEM_HEALTH_CHECK = "/admin/system/health-check"
    SYSTEM_ALERTS = "/admin/system/alerts"
    SYSTEM_BACKUP = "/admin/system/backup"
    SYSTEM_CONFIG = "/admin/system/configuration"
    SYSTEM_FEATURES = "/admin/system/features"
    SYSTEM_SERVICES = "/admin/system/services/{service_name}"
    SYSTEM_PERFORMANCE = "/admin/system/performance"
    SYSTEM_RESOURCES = "/admin/system/resources"

    # Database
    DATABASE_STATS = "/admin/system/database/stats"

    # Cache
    CACHE_STATS = "/admin/system/cache/stats"
    CACHE_CLEAR = "/admin/system/cache/clear"

    # Maintenance
    MAINTENANCE_SCHEDULE = "/admin/system/maintenance/schedule"

    # Data migration
    DATA_MIGRATION_START = "/admin/data-migration/start"
    DATA_MIGRATION_JOBS = "/admin/data-migration/jobs"

    # User bulk operations
    USERS_BULK_DELETE = "/admin/users/bulk/delete"
    USERS_BULK_SUSPEND = "/admin/users/bulk/suspend"
    USERS_BULK_UNSUSPEND = "/admin/users/bulk/unsuspend"
    USERS_BULK_RESET_PASSWORD = "/admin/users/bulk/reset-password"
    USERS_BULK_RESEND_ACTIVATION = "/admin/users/bulk/resend-activation"


class AssignmentRoutes:
    """Assignment workflow endpoints."""

    BASE = ""
    PENDING_REVIEW = "/pending-review"
    BY_ID = "/{assignment_id}"
    PUBLISH = "/{todo_id}/publish"
    MAKE_DRAFT = "/{todo_id}/make-draft"
    SUBMIT = "/{todo_id}/submit"
    REVIEW = "/{todo_id}/review"


class InfrastructureRoutes:
    """Infrastructure and system endpoints."""

    ROOT = "/"
    HEALTH = "/health"


class WebhookRoutes:
    """Webhook endpoints for external integrations."""

    GOOGLE_CALENDAR = "/google/calendar"
    MICROSOFT_CALENDAR = "/microsoft/calendar"
    HEALTH = "/health"


class UserConnectionRoutes:
    """User connection endpoints."""

    CONNECT = "/connect/{user_id}"
    DISCONNECT = "/disconnect/{user_id}"
    MY_CONNECTIONS = "/my-connections"
    ASSIGNABLE_USERS = "/assignable-users"


class EmailPreviewRoutes:
    """Email template preview endpoints."""

    BASE = "/"
    TEMPLATE = "/template"
    ALL = "/all"
    TEMPLATES = "/templates"


class PublicRoutes:
    """Public endpoints (no authentication)."""

    RESUME = "/resume/{slug}"
    RESUME_VIEW = "/resume/{slug}/view"
    RESUME_DOWNLOAD = "/resume/{slug}/download-pdf"
    STATS = "/stats"
    POSITIONS = "/positions"
    POSITIONS_SEARCH = "/positions/search"
    COMPANIES = "/companies"
    COMPANIES_SEARCH = "/companies/search"
    SITEMAP = "/sitemap.xml"
    ROBOTS = "/robots.txt"
    RSS_POSITIONS = "/rss/positions.xml"


class ConnectionInvitationRoutes:
    """Connection invitation endpoints."""

    SEND = "/send/{user_id}"
    RESPOND = "/respond/{invitation_id}"
    CANCEL = "/cancel/{invitation_id}"
    SENT = "/sent"
    RECEIVED = "/received"
    PENDING = "/pending"


class WebsocketVideoRoutes:
    """WebSocket video endpoints."""

    WS_VIDEO = "/ws/video/{room_id}"


class CalendarConnectionRoutes:
    """Calendar connection endpoints."""

    BASE = "/calendar-connections"
    BY_ID = "/calendar-connections/{connection_id}"
    DELETE = "/calendar-connections/{connection_id}"
    AUTH_GOOGLE_URL = "/calendar-connections/auth/google/url"
    AUTH_GOOGLE_CALLBACK = "/calendar-connections/auth/google/callback"
    AUTH_OUTLOOK_URL = "/calendar-connections/auth/outlook/url"
    AUTH_OUTLOOK_CALLBACK = "/calendar-connections/auth/outlook/callback"
    SYNC = "/calendar-connections/{connection_id}/sync"


class MeetingRoutes:
    """Meeting endpoints."""

    BASE = "/"
    BY_ID = "/{meeting_id}"
    BY_ROOM = "/room/{room_id}"
    JOIN = "/join/{room_id}"
    LEAVE = "/leave/{room_id}"
    RECORDINGS = "/{meeting_id}/recordings"
    TRANSCRIPTS = "/{meeting_id}/transcripts"
    TRANSCRIPT_BY_ID = "/{meeting_id}/transcripts/{transcript_id}"
    SUMMARIES = "/{meeting_id}/summaries"
    SUMMARY_BY_ID = "/{meeting_id}/summaries/{summary_id}"


class TodoExtensionRoutes:
    """Todo extension request endpoints."""

    CREATE = "/{todo_id}/extension-requests"
    VALIDATE = "/extension-requests/validate/{todo_id}"
    RESPOND = "/extension-requests/{request_id}/respond"
    MY_REQUESTS = "/extension-requests/my-requests"
    TO_REVIEW = "/extension-requests/to-review"
    BY_ID = "/extension-requests/{request_id}"


class SubscriptionRoutes:
    """Subscription and plan management endpoints."""

    # Public plan endpoints
    PLANS = "/plans"
    PLAN_BY_ID = "/plans/{plan_id}"

    # Company subscription endpoints
    MY_SUBSCRIPTION = "/my-subscription"
    SUBSCRIBE = "/subscribe"
    UPDATE_SUBSCRIPTION = "/my-subscription"

    # Feature access check
    CHECK_FEATURE = "/check-feature/{feature_name}"

    # Plan change requests
    REQUEST_PLAN_CHANGE = "/plan-change-request"
    MY_PLAN_CHANGE_REQUESTS = "/my-plan-change-requests"
    ALL_PLAN_CHANGE_REQUESTS = "/plan-change-requests"
    REVIEW_PLAN_CHANGE = "/plan-change-requests/{request_id}/review"


class FeatureRoutes:
    """Feature catalog and plan-feature management endpoints."""

    # Feature catalog
    BASE = "/"
    HIERARCHICAL = "/"
    FLAT = "/flat"
    BY_ID = "/{feature_id}"
    SEARCH = "/search/{search_term}"

    # Plan-feature management
    PLAN_FEATURES = "/plan/{plan_id}/features"
    ADD_FEATURE_TO_PLAN = "/plan/{plan_id}/features"
    REMOVE_FEATURE_FROM_PLAN = "/plan/{plan_id}/features/{feature_id}"


class API_ROUTES:
    """
    Centralized API route definitions.

    Usage in endpoint files:
        from app.config.endpoints import API_ROUTES

        router = APIRouter()

        @router.post(API_ROUTES.AUTH.LOGIN)
        async def login(...):
            pass
    """

    AUTH = AuthRoutes
    USERS = UserRoutes
    COMPANIES = CompanyRoutes
    POSITIONS = PositionRoutes
    INTERVIEWS = InterviewRoutes
    EXAMS = ExamRoutes
    QUESTION_BANKS = QuestionBankRoutes
    VIDEO_CALLS = VideoCallRoutes
    CALENDAR = CalendarRoutes
    MESSAGES = MessageRoutes
    NOTIFICATIONS = NotificationRoutes
    TODOS = TodoRoutes
    TODO_ATTACHMENTS = TodoAttachmentRoutes
    RESUMES = ResumeRoutes
    DASHBOARD = DashboardRoutes
    FILES = FileRoutes
    WORKFLOWS = WorkflowRoutes
    MBTI = MBTIRoutes
    ADMIN = AdminRoutes
    ASSIGNMENTS = AssignmentRoutes
    HOLIDAYS = HolidayRoutes
    INFRASTRUCTURE = InfrastructureRoutes
    WEBHOOKS = WebhookRoutes
    USER_CONNECTIONS = UserConnectionRoutes
    EMAIL_PREVIEW = EmailPreviewRoutes
    PUBLIC = PublicRoutes
    CONNECTION_INVITATIONS = ConnectionInvitationRoutes
    WEBSOCKET_VIDEO = WebsocketVideoRoutes
    CALENDAR_CONNECTIONS = CalendarConnectionRoutes
    MEETINGS = MeetingRoutes
    TODO_EXTENSIONS = TodoExtensionRoutes
    SUBSCRIPTIONS = SubscriptionRoutes
    FEATURES = FeatureRoutes


# Convenience exports
__all__ = [
    "API_ROUTES",
    "AuthRoutes",
    "UserRoutes",
    "CompanyRoutes",
    "PositionRoutes",
    "InterviewRoutes",
    "ExamRoutes",
    "VideoCallRoutes",
    "CalendarRoutes",
    "MessageRoutes",
    "NotificationRoutes",
    "TodoRoutes",
    "ResumeRoutes",
    "DashboardRoutes",
    "FileRoutes",
    "WorkflowRoutes",
    "MBTIRoutes",
    "AdminRoutes",
    "AssignmentRoutes",
]
