"""
Centralized API endpoint path configuration.

This module defines all API endpoint paths in a single location for consistency
and easy maintenance. Use these constants when defining routes in endpoint files.

IMPORTANT ARCHITECTURAL RULES:
1. ALL endpoint paths MUST be defined here - NO hardcoded strings in @router decorators
2. ALL definitions MUST be in strict alphabetical order (A-Z) at three levels:
   - Route class definitions (AdminRoutes → WorkflowRoutes)
   - API_ROUTES properties (ADMIN → WORKFLOWS)
   - __all__ exports (all exports A-Z)

Example usage:
    from app.config.endpoints import API_ROUTES

    router = APIRouter()

    # ✅ CORRECT - Use centralized route constants
    @router.post(API_ROUTES.AUTH.LOGIN)
    async def login(...):
        pass

    # ❌ WRONG - Never hardcode endpoint paths
    @router.post("/login")  # DON'T DO THIS!
    async def login(...):
        pass

Benefits:
- Single source of truth for all endpoints
- Easy refactoring - change route in one place
- Prevents duplicate endpoint definitions
- Alphabetical ordering makes routes easy to find
- Better git diffs due to consistent ordering
"""

from collections.abc import Callable


class EndpointPath:
    """
    Helper class for creating parameterized endpoint paths.

    This class provides utility methods for generating dynamic endpoint paths
    that include parameters like IDs. Currently not actively used but available
    for future endpoint path generation needs.
    """

    @staticmethod
    def with_id(base: str, param: str = "id") -> Callable[[str | int], str]:
        """
        Create a function that generates paths with ID parameter.

        Args:
            base: Base path (e.g., "/api/users")
            param: Parameter name (default: "id")

        Returns:
            Function that takes an ID and returns the full path

        Example:
            >>> get_user_path = EndpointPath.with_id("/api/users")
            >>> get_user_path(123)
            "/api/users/{id}"
        """
        return lambda id_val: f"{base}/{{{param}}}"

    @staticmethod
    def format(template: str) -> str:
        """
        Return the template as-is for use in FastAPI route decorators.

        Args:
            template: Endpoint path template

        Returns:
            The same template string
        """
        return template


# =============================================================================
# ROUTE CLASS DEFINITIONS (Alphabetically Ordered A-Z)
# =============================================================================
# Each class below defines endpoint paths for a specific domain/feature.
# All route classes MUST be in alphabetical order for easy navigation.
# Within each class, endpoint constants should also be alphabetically ordered.
# =============================================================================

class AdminRoutes:
    """
    Administrative endpoints for system management.

    These endpoints are restricted to admin users and provide access to:
    - Security and antivirus management
    - Audit logging and monitoring
    - Bulk operations on entities
    - System health and performance monitoring
    - User management (suspend, activation, password reset)

    All admin endpoints are prefixed with /admin and require admin role.
    """

    # Antivirus - File security scanning
    ANTIVIRUS_BULK_SCAN = "/admin/security/antivirus/bulk-scan"
    ANTIVIRUS_STATUS = "/admin/security/antivirus/status"

    # Audit logs - System activity tracking
    AUDIT_ACTIVITY = "/admin/audit-logs/activity"
    AUDIT_EXPORT = "/admin/audit-logs/export"
    AUDIT_FILTER_OPTIONS = "/admin/audit-logs/filter-options"
    AUDIT_LOGS = "/admin/audit-logs"
    AUDIT_STATS = "/admin/audit-logs/stats"

    # Bulk operations - Mass entity management
    BULK_DELETE = "/admin/bulk/delete"
    BULK_ENTITY_COUNTS = "/admin/bulk/entity-counts"
    BULK_EXPORT = "/admin/bulk/export"
    BULK_IMPORT = "/admin/bulk/import"
    BULK_PREVIEW_DELETE = "/admin/bulk/preview-delete"
    BULK_PREVIEW_UPDATE = "/admin/bulk/preview-update"
    BULK_QUOTA = "/admin/bulk/quota"
    BULK_UPDATE = "/admin/bulk/update"
    BULK_VALIDATE_IDS = "/admin/bulk/validate-ids"
    BULK_VALIDATE_IMPORT = "/admin/bulk/validate-import"

    # Cache - Application cache management
    CACHE_CLEAR = "/admin/system/cache/clear"
    CACHE_STATS = "/admin/system/cache/stats"

    # Data migration - Database migration tools
    DATA_MIGRATION_JOBS = "/admin/data-migration/jobs"
    DATA_MIGRATION_START = "/admin/data-migration/start"

    # Database - Database statistics and health
    DATABASE_STATS = "/admin/system/database/stats"

    # Maintenance - System maintenance scheduling
    MAINTENANCE_SCHEDULE = "/admin/system/maintenance/schedule"

    # Security - File security and threat management
    SECURITY_BULK_ACTION = "/admin/security/bulk-action"
    SECURITY_FILE_BY_ID = "/admin/security/files/{file_id}"
    SECURITY_FILES = "/admin/security/files"
    SECURITY_LOGS = "/admin/security/logs"
    SECURITY_QUARANTINE = "/admin/security/files/{file_id}/quarantine"
    SECURITY_RESTORE = "/admin/security/files/{file_id}/restore"
    SECURITY_SCAN_FILE = "/admin/security/files/{file_id}/scan"
    SECURITY_STATS = "/admin/security/stats"

    # System monitoring - Health, performance, and resource tracking
    SYSTEM_ALERTS = "/admin/system/alerts"
    SYSTEM_BACKUP = "/admin/system/backup"
    SYSTEM_CONFIG = "/admin/system/configuration"
    SYSTEM_FEATURES = "/admin/system/features"
    SYSTEM_HEALTH = "/admin/system/health"
    SYSTEM_HEALTH_CHECK = "/admin/system/health-check"
    SYSTEM_PERFORMANCE = "/admin/system/performance"
    SYSTEM_RESOURCES = "/admin/system/resources"
    SYSTEM_SERVICES = "/admin/system/services/{service_name}"

    # User bulk operations - Mass user management actions
    USERS_BULK_DELETE = "/admin/users/bulk/delete"
    USERS_BULK_RESEND_ACTIVATION = "/admin/users/bulk/resend-activation"
    USERS_BULK_RESET_PASSWORD = "/admin/users/bulk/reset-password"
    USERS_BULK_SUSPEND = "/admin/users/bulk/suspend"
    USERS_BULK_UNSUSPEND = "/admin/users/bulk/unsuspend"


class AssignmentRoutes:
    """Assignment workflow endpoints."""

    BASE = ""
    BY_ID = "/{assignment_id}"
    MAKE_DRAFT = "/{todo_id}/make-draft"
    PENDING_REVIEW = "/pending-review"
    PUBLISH = "/{todo_id}/publish"
    REVIEW = "/{todo_id}/review"
    SUBMIT = "/{todo_id}/submit"


class AuthRoutes:
    """Authentication and authorization endpoints."""

    # Account activation
    ACTIVATE_ACCOUNT = "/activate"

    CHANGE_PASSWORD = "/change-password"
    LOGIN = "/login"
    LOGOUT = "/logout"
    ME = "/me"

    # Password reset endpoints
    PASSWORD_RESET_APPROVE = "/password-reset/approve"
    PASSWORD_RESET_REQUEST = "/password-reset/request"
    PASSWORD_RESET_REQUESTS = "/password-reset/requests"

    REFRESH = "/refresh"
    REGISTER = "/register"

    # 2FA endpoints
    TWO_FA_RESEND = "/2fa/resend"
    TWO_FA_VERIFY = "/2fa/verify"


class BlockedCompanyRoutes:
    """
    Blocked company management endpoints.

    Allows candidates to block companies from:
    - Viewing their profile
    - Receiving recommendations for these companies
    - Being contacted by recruiters from these companies
    """

    BASE = "/blocked-companies"
    BY_ID = "/blocked-companies/{blocked_company_id}"
    SEARCH = "/blocked-companies/search"


class CalendarConnectionRoutes:
    """Calendar connection endpoints."""

    AUTH_GOOGLE_CALLBACK = "/calendar-connections/auth/google/callback"
    AUTH_GOOGLE_URL = "/calendar-connections/auth/google/url"
    AUTH_OUTLOOK_CALLBACK = "/calendar-connections/auth/outlook/callback"
    AUTH_OUTLOOK_URL = "/calendar-connections/auth/outlook/url"
    BASE = "/calendar-connections"
    BY_ID = "/calendar-connections/{connection_id}"
    DELETE = "/calendar-connections/{connection_id}"
    SYNC = "/calendar-connections/{connection_id}/sync"


class CalendarRoutes:
    """
    Calendar and event management endpoints.

    Supports integration with external calendar providers:
    - Google Calendar (OAuth, webhooks, sync)
    - Microsoft Outlook Calendar (OAuth, webhooks, sync)

    Features:
    - Calendar account management (connect, disconnect, sync)
    - Event CRUD operations
    - Event search and filtering (by date range, upcoming)
    - Bulk event operations
    - OAuth authentication flows
    - Webhook subscriptions for real-time updates
    """

    # Calendar accounts - External calendar account management
    ACCOUNT_BY_ID = "/accounts/{account_id}"
    ACCOUNT_SYNC = "/accounts/{account_id}/sync"
    ACCOUNTS = "/accounts"

    # Calendars list - Available calendars
    CALENDARS = "/calendars"

    # Events (main) - Core event CRUD operations
    EVENT_BY_ID = "/events/{event_id}"
    EVENTS = "/events"

    # Events filtering/search - Event query operations
    EVENTS_BULK = "/events/bulk"
    EVENTS_RANGE = "/events/range"
    EVENTS_SEARCH = "/events/search"
    EVENTS_UPCOMING = "/events/upcoming"

    # Event invitations - Attendee invitation management
    INVITATIONS_ACCEPT = "/invitations/{invitation_id}/accept"
    INVITATIONS_PENDING = "/invitations/pending"
    INVITATIONS_REJECT = "/invitations/{invitation_id}/reject"

    # OAuth - Authentication flows for calendar providers
    GOOGLE_OAUTH_CALLBACK = "/oauth/google/callback"
    GOOGLE_OAUTH_START = "/oauth/google/start"
    MICROSOFT_OAUTH_CALLBACK = "/oauth/microsoft/callback"
    MICROSOFT_OAUTH_START = "/oauth/microsoft/start"

    # Webhooks - Real-time calendar event notifications
    WEBHOOKS_GOOGLE = "/webhooks/google"
    WEBHOOKS_MICROSOFT = "/webhooks/microsoft"


class CompanyConnectionRoutes:
    """Company connection endpoints."""

    ACTIVATE = "/{connection_id}/activate"
    BY_ID = "/{connection_id}"
    COMPANY_TO_COMPANY = "/company-to-company"
    DEACTIVATE = "/{connection_id}/deactivate"
    MY_CONNECTIONS = "/my-connections"
    USER_TO_COMPANY = "/user-to-company"


class CompanyRoutes:
    """Company management endpoints."""

    ADMIN_STATUS = "/companies/{company_id}/admin-status"
    BASE = "/companies"
    BY_ID = "/companies/{company_id}"
    CREATE = "/companies"
    DELETE = "/companies/{company_id}"
    MY_COMPANY = "/my-company"
    UPDATE = "/companies/{company_id}"
    UPDATE_MY_COMPANY = "/my-company"


class ConnectionInvitationRoutes:
    """Connection invitation endpoints."""

    CANCEL = "/cancel/{invitation_id}"
    PENDING = "/pending"
    RECEIVED = "/received"
    RESPOND = "/respond/{invitation_id}"
    SEND = "/send/{user_id}"
    SENT = "/sent"


class DashboardRoutes:
    """Dashboard and statistics endpoints."""

    ACTIVITY = "/activity"
    BASE = ""
    STATS = "/stats"


class EmailPreviewRoutes:
    """Email template preview endpoints."""

    ALL = "/all"
    BASE = "/"
    TEMPLATE = "/template"
    TEMPLATES = "/templates"


class ExamRoutes:
    """
    Exam system endpoints for assessment management.

    This comprehensive exam system supports:
    - Exam creation and management (CRUD operations)
    - Question bank integration
    - Exam assignments to candidates
    - Live exam sessions with monitoring
    - Face verification during exams
    - Answer submission and grading
    - Results and statistics
    - Template management for reusable exam structures
    - Export capabilities (PDF, Excel)
    """

    # Assignments - Exam assignment management
    ASSIGNMENT_BY_ID = "/assignments/{assignment_id}"
    ASSIGNMENTS = "/exams/{exam_id}/assignments"

    # Exam management - Core CRUD operations
    BASE = "/exams"
    BY_ID = "/exams/{exam_id}"
    CLONE = "/exams/{exam_id}/clone"

    # Exam operations - Export and data operations
    EXPORT_EXCEL = "/exams/{exam_id}/export/excel"
    EXPORT_PDF = "/exams/{exam_id}/export/pdf"

    HYBRID = "/exams/hybrid"
    MY_ASSIGNMENTS = "/my-assignments"

    # Questions - Exam question management
    QUESTION_BY_ID = "/questions/{question_id}"
    QUESTIONS = "/exams/{exam_id}/questions"

    # Sessions - Live exam session management and monitoring
    SESSION_ANSWERS = "/sessions/{session_id}/answers"
    SESSION_BY_ID = "/sessions/{session_id}"
    SESSION_COMPLETE = "/sessions/{session_id}/complete"
    SESSION_DETAILS = "/sessions/{session_id}/details"
    SESSION_FACE_VERIFICATION = "/sessions/{session_id}/face-verification"
    SESSION_MONITORING = "/sessions/{session_id}/monitoring"
    SESSION_RESET = "/sessions/{session_id}/reset"
    SESSION_RESULTS = "/sessions/{session_id}/results"
    SESSION_SUSPEND = "/sessions/{session_id}/suspend"
    SESSIONS = "/exams/{exam_id}/sessions"

    STATISTICS = "/exams/{exam_id}/statistics"
    TAKE = "/exams/take"

    # Templates - Exam template management for reusability
    TEMPLATE_BY_ID = "/templates/{template_id}"
    TEMPLATE_FROM_EXAM = "/templates/from-exam/{exam_id}"
    TEMPLATES = "/templates"


class FeatureRoutes:
    """Feature catalog and plan-feature management endpoints."""

    # Plan-feature management
    ADD_FEATURE_TO_PLAN = "/plan/{plan_id}/features"

    # Feature catalog
    BASE = "/"
    BY_ID = "/{feature_id}"
    FLAT = "/flat"
    HIERARCHICAL = "/"
    PLAN_FEATURES = "/plan/{plan_id}/features"
    REMOVE_FEATURE_FROM_PLAN = "/plan/{plan_id}/features/{feature_id}"
    SEARCH = "/search/{search_term}"


class FileRoutes:
    """File upload/download endpoints."""

    DELETE = "/{s3_key:path}"
    DOWNLOAD = "/download/{s3_key:path}"
    MESSAGE_FILE = "/message/{user_id}/{filename}"
    TEST = "/test"
    UPLOAD = "/upload"


class HolidayRoutes:
    """Holiday management endpoints."""

    BASE = "/"
    BULK = "/bulk"
    BY_ID = "/{holiday_id}"
    CHECK = "/check/{holiday_date}"
    UPCOMING = "/upcoming"


class InfrastructureRoutes:
    """Infrastructure and system endpoints."""

    HEALTH = "/health"
    ROOT = "/"


class InterviewRoutes:
    """Interview management endpoints."""

    BASE = ""
    BASE_SLASH = "/"
    BY_ID = "/{interview_id}"
    CALENDAR_EVENTS = "/calendar/events"
    CALENDAR_INTEGRATION_STATUS = "/calendar/integration-status"
    CANCEL = "/{interview_id}/cancel"
    NOTES = "/{interview_id}/notes"
    PROPOSAL_RESPOND = "/{interview_id}/proposals/{proposal_id}/respond"
    PROPOSALS = "/{interview_id}/proposals"
    RESCHEDULE = "/{interview_id}/reschedule"
    SCHEDULE = "/{interview_id}/schedule"
    STATS_SUMMARY = "/stats/summary"
    STATUS = "/{interview_id}/status"
    VIDEO_CALL = "/{interview_id}/video-call"


class MBTIRoutes:
    """MBTI personality test endpoints."""

    ADMIN_QUESTIONS_BULK = "/admin/questions/bulk"
    ANSWER = "/answer"
    PROGRESS = "/progress"
    QUESTIONS = "/questions"
    RESULT = "/result"
    START = "/start"
    SUBMIT = "/submit"
    SUMMARY = "/summary"
    TYPE_DETAILS = "/types/{mbti_type}"
    TYPES = "/types"


class MeetingRoutes:
    """Meeting endpoints."""

    BASE = "/"
    BY_ID = "/{meeting_id}"
    BY_ROOM = "/room/{room_id}"
    JOIN = "/join/{room_id}"
    LEAVE = "/leave/{room_id}"
    RECORDINGS = "/{meeting_id}/recordings"
    SUMMARIES = "/{meeting_id}/summaries"
    SUMMARY_BY_ID = "/{meeting_id}/summaries/{summary_id}"
    TRANSCRIPT_BY_ID = "/{meeting_id}/transcripts/{transcript_id}"
    TRANSCRIPTS = "/{meeting_id}/transcripts"


class MessageRoutes:
    """Messaging system endpoints."""

    BASE = "/messages"
    BY_ID = "/messages/{message_id}"
    CONVERSATIONS = "/conversations"
    MARK_READ_CONVERSATION = "/mark-conversation-read/{other_user_id}"
    MARK_READ_SINGLE = "/mark-read"
    PARTICIPANTS = "/participants"

    # File uploads
    RESTRICTED_USERS = "/restricted-users"
    SEARCH = "/search"
    SEND = "/send"
    UPLOAD = "/upload"
    UPLOAD_CHUNK = "/upload/chunk"
    UPLOAD_COMPLETE = "/upload/complete"

    WITH_USER = "/with/{other_user_id}"


class NotificationRoutes:
    """Notification endpoints."""

    BASE = "/"
    BY_ID = "/{notification_id}"
    MARK_ALL_READ = "/mark-all-read"
    MARK_READ = "/mark-read"
    UNREAD_COUNT = "/unread-count"


class PositionRoutes:
    """Job position endpoints."""

    BASE = ""
    BASE_SLASH = "/"
    BULK_STATUS = "/bulk/status"
    BY_ID = "/{position_id}"
    BY_SLUG = "/slug/{slug}"
    COMPANY = "/company/{company_id}"
    EXPIRING = "/expiring"
    POPULAR = "/popular"
    PUBLIC = "/public/positions"
    RECENT = "/recent"
    STATISTICS = "/statistics"
    STATUS = "/{position_id}/status"


class PrivacySettingsRoutes:
    """
    Privacy settings endpoints for section-specific profile visibility controls.

    These endpoints support the privacy toggles on profile sections
    (work experience, education, skills, etc.) allowing users to control
    what information is visible to others.
    """

    ME = "/me"


class ProfileRoutes:
    """User profile information endpoints."""

    # Certifications
    CERTIFICATIONS = "/certifications"
    CERTIFICATIONS_BY_ID = "/certifications/{certification_id}"

    # Profile Completeness
    COMPLETENESS = "/completeness"

    # Education
    EDUCATION = "/education"
    EDUCATION_BY_ID = "/education/{education_id}"

    # Job Preferences
    JOB_PREFERENCES = "/job-preferences"

    # Projects
    PROJECTS = "/projects"
    PROJECTS_BY_ID = "/projects/{project_id}"

    # Skills
    SKILLS = "/skills"
    SKILLS_BY_ID = "/skills/{skill_id}"

    # Work Experience
    WORK_EXPERIENCE = "/work-experience"
    WORK_EXPERIENCE_BY_ID = "/work-experience/{experience_id}"


class ProfileViewRoutes:
    """Profile view tracking endpoints."""

    BASE = "/"
    COUNT = "/count"
    MY_VIEWS = "/my-views"
    RECENT_VIEWERS = "/recent-viewers"
    STATS = "/stats"


class PublicRoutes:
    """Public endpoints (no authentication)."""

    COMPANIES = "/companies"
    COMPANIES_SEARCH = "/companies/search"
    POSITIONS = "/positions"
    POSITIONS_SEARCH = "/positions/search"
    RESUME = "/resume/{slug}"
    RESUME_DOWNLOAD = "/resume/{slug}/download-pdf"
    RESUME_VIEW = "/resume/{slug}/view"
    ROBOTS = "/robots.txt"
    RSS_POSITIONS = "/rss/positions.xml"
    SITEMAP = "/sitemap.xml"
    STATS = "/stats"


class QuestionBankRoutes:
    """Question bank endpoints."""

    # Question banks
    BASE = "/question-banks"
    BY_ID = "/question-banks/{bank_id}"

    # Bank questions
    QUESTION_BY_ID = "/questions/{question_id}"
    QUESTIONS = "/question-banks/{bank_id}/questions"

    # Statistics
    STATS = "/question-banks/{bank_id}/stats"


class RecruiterProfileRoutes:
    """Recruiter profile endpoints."""

    BY_USER_ID = "/{user_id}"
    ME = "/me"


class ResumeRoutes:
    """
    Resume/CV management endpoints.

    Comprehensive resume builder with support for:
    - Multiple resume formats (standard, Japanese 履歴書, 職務経歴書)
    - Resume sections: education, experience, skills, certifications, projects, languages
    - Template system for different resume styles
    - Public/private resume sharing with custom slugs
    - PDF generation and export
    - Message integration (attach resume to messages)
    - Bulk operations on resumes
    - Analytics and statistics
    - Photo/avatar management
    - Search and filtering

    Japanese Resume Support:
    - 履歴書 (Rirekisho) - Personal history/background
    - 職務経歴書 (Shokumu Keirekisho) - Professional experience record
    """

    # Analytics - Resume view and usage statistics
    ANALYTICS = "/{resume_id}/analytics"

    # Sharing and Public - Template application
    APPLY_TEMPLATE = "/{resume_id}/template/{template_id}"

    # Message integration - Resume attachment to messages
    ATTACH_TO_MESSAGE = "/{resume_id}/attach-to-message"
    AUTO_ATTACH_SETTINGS = "/{resume_id}/auto-attach-settings"

    BASE = "/"

    # Bulk operations - Mass resume management
    BULK_ACTION = "/bulk-action"
    BULK_DELETE = "/bulk/delete"
    BULK_UPDATE = "/bulk/update"

    BY_ID = "/{resume_id}"
    BY_SLUG = "/public/resume/{slug}"

    # Resume sections - Certifications management
    CERTIFICATION_BY_ID = "/certifications/{cert_id}"
    CERTIFICATIONS = "/{resume_id}/certifications"

    # Japanese resume conversions - Localized resume formats
    CONVERT_RIREKISHO = "/{resume_id}/convert-to-rirekisho"
    CONVERT_SHOKUMU = "/{resume_id}/convert-to-shokumu"

    DUPLICATE = "/{resume_id}/duplicate"

    # Resume sections - Education management
    EDUCATION = "/{resume_id}/education"
    EDUCATION_BY_ID = "/education/{edu_id}"

    # Resume sections - Work experience management
    EXPERIENCE_BY_ID = "/experiences/{exp_id}"
    EXPERIENCES = "/{resume_id}/experiences"

    GENERATE_PDF = "/{resume_id}/generate-pdf"

    # Resume sections - Language proficiency
    LANGUAGE_BY_ID = "/languages/{lang_id}"
    LANGUAGES = "/{resume_id}/languages"

    PREVIEW = "/{resume_id}/preview"

    # Resume sections - Projects portfolio
    PROJECT_BY_ID = "/projects/{project_id}"
    PROJECTS = "/{resume_id}/projects"

    PROTECTION = "/{resume_id}/protection"
    PUBLIC = "/public/{slug}"

    # Public endpoints - Publicly accessible resume views
    PUBLIC_DOWNLOAD = "/public/resume/{slug}/download-pdf"
    PUBLIC_DOWNLOAD_SLUG = "/public/{slug}/download"
    PUBLIC_INFO = "/public/{slug}"
    PUBLIC_SETTINGS = "/{resume_id}/public-settings"
    PUBLIC_VIEW = "/public/resume/{slug}/view"

    REMOVE_PHOTO = "/{resume_id}/remove-photo"
    SEARCH = "/search"
    SEND_EMAIL = "/{resume_id}/send-email"
    SHARE = "/{resume_id}/share"
    SHARED = "/shared/{share_token}"

    # Resume sections - Skills management
    SKILL_BY_ID = "/skills/{skill_id}"
    SKILLS = "/{resume_id}/skills"

    STATS = "/stats"

    # Templates - Resume template library
    TEMPLATES_AVAILABLE = "/templates/available"
    TEMPLATES_JAPANESE = "/templates/japanese"

    TOGGLE_PUBLIC = "/{resume_id}/toggle-public"
    UPLOAD_PHOTO = "/{resume_id}/upload-photo"


class SubscriptionRoutes:
    """Subscription and plan management endpoints."""

    # Plan change requests
    ALL_PLAN_CHANGE_REQUESTS = "/plan-change-requests"
    CANCEL_PLAN_CHANGE = "/plan-change-requests/{request_id}/cancel"

    # Feature access check
    CHECK_FEATURE = "/check-feature/{feature_name}"

    MY_PLAN_CHANGE_REQUESTS = "/my-plan-change-requests"

    # Company subscription endpoints
    MY_SUBSCRIPTION = "/my-subscription"

    # Public plan endpoints
    PLAN_BY_ID = "/plans/{plan_id}"
    PLANS = "/plans"

    REQUEST_PLAN_CHANGE = "/plan-change-request"
    REVIEW_PLAN_CHANGE = "/plan-change-requests/{request_id}/review"
    SUBSCRIBE = "/subscribe"
    UPDATE_SUBSCRIPTION = "/my-subscription"


class SystemUpdateRoutes:
    """System update/announcement endpoints."""

    ACTIVATE = "/{update_id}/activate"
    BASE = ""
    BY_ID = "/{update_id}"


class TodoAttachmentRoutes:
    """Todo attachment endpoints."""

    ADMIN_CLEANUP = "/admin/attachments/cleanup"
    BULK_DELETE = "/todos/{todo_id}/attachments/bulk-delete"
    BY_ID = "/todos/{todo_id}/attachments/{attachment_id}"
    DELETE = "/todos/{todo_id}/attachments/{attachment_id}"
    DOWNLOAD = "/todos/{todo_id}/attachments/{attachment_id}/download"
    LIST = "/todos/{todo_id}/attachments"
    MY_UPLOADS = "/attachments/my-uploads"
    PREVIEW = "/todos/{todo_id}/attachments/{attachment_id}/preview"
    STATS = "/todos/{todo_id}/attachments/stats"
    UPDATE = "/todos/{todo_id}/attachments/{attachment_id}"
    UPLOAD = "/todos/{todo_id}/attachments/upload"


class TodoExtensionRoutes:
    """Todo extension request endpoints."""

    BY_ID = "/extension-requests/{request_id}"
    CREATE = "/{todo_id}/extension-requests"
    MY_REQUESTS = "/extension-requests/my-requests"
    RESPOND = "/extension-requests/{request_id}/respond"
    TO_REVIEW = "/extension-requests/to-review"
    VALIDATE = "/extension-requests/validate/{todo_id}"


class TodoRoutes:
    """Todo/task management endpoints."""

    ASSIGN = "/{todo_id}/assign"
    ASSIGNABLE_USERS = "/assignable-users"
    ASSIGNED = "/assigned"

    # Attachments
    ATTACHMENT_BULK_DELETE = "/{todo_id}/attachments/bulk-delete"
    ATTACHMENT_BY_ID = "/{todo_id}/attachments/{attachment_id}"
    ATTACHMENT_DOWNLOAD = "/{todo_id}/attachments/{attachment_id}/download"
    ATTACHMENT_PREVIEW = "/{todo_id}/attachments/{attachment_id}/preview"
    ATTACHMENT_STATS = "/{todo_id}/attachments/stats"
    ATTACHMENT_UPLOAD = "/{todo_id}/attachments/upload"
    ATTACHMENTS = "/{todo_id}/attachments"

    BASE = ""
    BY_ID = "/{todo_id}"
    COMPLETE = "/{todo_id}/complete"
    DETAILS = "/{todo_id}/details"

    # Extension requests
    EXTENSION_BY_ID = "/extension-requests/{request_id}"
    EXTENSION_CREATE = "/{todo_id}/extension-requests"
    EXTENSION_MY_REQUESTS = "/extension-requests/my-requests"
    EXTENSION_RESPOND = "/extension-requests/{request_id}/respond"
    EXTENSION_TO_REVIEW = "/extension-requests/to-review"
    EXTENSION_VALIDATE = "/extension-requests/validate/{todo_id}"

    MY_UPLOADS = "/attachments/my-uploads"
    RECENT = "/recent"
    REOPEN = "/{todo_id}/reopen"
    RESTORE = "/{todo_id}/restore"

    # Viewer management
    VIEWER_ADD = "/{todo_id}/viewers"
    VIEWER_LIST = "/{todo_id}/viewers"
    VIEWER_REMOVE = "/{todo_id}/viewers/{viewer_user_id}"
    VIEWABLE_TODOS = "/viewable"


class UserConnectionRoutes:
    """User connection endpoints."""

    ASSIGNABLE_USERS = "/assignable-users"
    CONNECT = "/connect/{user_id}"
    DISCONNECT = "/disconnect/{user_id}"
    MY_CONNECTIONS = "/my-connections"


class UserRoutes:
    """User management endpoints."""

    # Admin user endpoints (used with /api/admin prefix)
    ADMIN_USER_BY_ID = "/users/{user_id}"
    ADMIN_USER_RESEND_ACTIVATION = "/users/{user_id}/resend-activation"
    ADMIN_USER_RESET_PASSWORD = "/users/{user_id}/reset-password"
    ADMIN_USER_SUSPEND = "/users/{user_id}/suspend"
    ADMIN_USER_UNSUSPEND = "/users/{user_id}/unsuspend"
    ADMIN_USERS = "/users"

    BASE = "/users"
    BY_ID = "/users/{user_id}"
    PROFILE = "/profile"
    SETTINGS = "/settings"


class VideoCallRoutes:
    """Video call endpoints."""

    BASE = "/"
    BY_ID = "/{call_id}"
    BY_ROOM = "/room/{room_id}"
    CONSENT = "/{call_id}/consent"
    CONSENT_ROOM = "/room/{room_id}/consent"
    END = "/{call_id}/end"
    JOIN = "/{call_id}/join"
    JOIN_ROOM = "/room/{room_id}/join"
    LEAVE = "/{call_id}/leave"
    LEAVE_ROOM = "/room/{room_id}/leave"
    SCHEDULE = "/schedule"
    TOKEN = "/{call_id}/token"

    # Transcription
    TRANSCRIPT = "/{call_id}/transcript"
    TRANSCRIPT_DOWNLOAD = "/{call_id}/transcript/download"
    TRANSCRIPT_SEGMENTS = "/{call_id}/transcript/segments"


class WebhookRoutes:
    """Webhook endpoints for external integrations."""

    GOOGLE_CALENDAR = "/google/calendar"
    HEALTH = "/health"
    MICROSOFT_CALENDAR = "/microsoft/calendar"


class WebsocketVideoRoutes:
    """WebSocket video endpoints."""

    WS_VIDEO = "/ws/video/{room_id}"


class WorkflowRoutes:
    """
    Recruitment workflow/process management endpoints.

    Comprehensive workflow system for managing recruitment processes:
    - Visual workflow builder with nodes and connections
    - Template library for common recruitment processes
    - Candidate progress tracking through workflow stages
    - Analytics and reporting (completion rates, bottlenecks)
    - Integration with interviews, exams, and tasks
    - Recruiter workload management
    - Multi-company workflow support

    Workflow Structure:
    - Nodes: Individual stages in the recruitment process
    - Connections: Transitions between nodes
    - Candidate Workflows: Instances of candidates progressing through workflow
    - Templates: Reusable workflow structures
    """

    # Workflow routes - Core workflow management
    ACTIVATE = "/{workflow_id}/activate"
    ANALYTICS = "/{workflow_id}/analytics"
    APPLY_TEMPLATE = "/templates/{template_id}/apply"
    ARCHIVE = "/{workflow_id}/archive"
    BASE = "/"
    BY_ID = "/{workflow_id}"

    # Candidate routes - Candidate progression tracking
    CANDIDATE_PROCESS_BY_ID = "/candidate-workflows/{candidate_workflow_id}"
    CANDIDATE_START = "/candidate-workflows/{candidate_workflow_id}/start"
    CANDIDATE_STATUS = "/candidate-workflows/{candidate_workflow_id}/status"
    CANDIDATE_TIMELINE = "/candidate-workflows/{candidate_workflow_id}/timeline"
    CANDIDATES = "/{workflow_id}/candidates"
    CANDIDATES_BULK = "/{workflow_id}/candidates/bulk"

    CLONE = "/{workflow_id}/clone"
    COMPANY_STATS = "/company/{company_id}/statistics"
    MY_PROCESSES = "/my-workflows"

    # Node routes - Workflow node/stage management
    NODE_BY_ID = "/{workflow_id}/nodes/{node_id}"
    NODE_WITH_INTEGRATION = "/{workflow_id}/nodes/create-with-integration"
    NODES = "/{workflow_id}/nodes"

    RECRUITER_WORKLOAD = "/recruiters/{recruiter_id}/workload"
    TEMPLATES = "/templates/"
    VALIDATE = "/{workflow_id}/validate"


# =============================================================================
# CENTRALIZED API_ROUTES CLASS (Properties Alphabetically Ordered A-Z)
# =============================================================================
# This class aggregates all route class definitions into a single namespace.
# Import this class in endpoint files to access route constants.
#
# IMPORTANT: All properties MUST be in alphabetical order (A-Z)
#
# Usage pattern:
#   1. Import: from app.config.endpoints import API_ROUTES
#   2. Use in router decorator: @router.post(API_ROUTES.AUTH.LOGIN)
#   3. Never hardcode endpoint strings directly
# =============================================================================

class API_ROUTES:
    """
    Centralized API route definitions for the entire application.

    This class provides a single point of access to all API endpoint paths
    across the application. All endpoint files should import this class and
    use its properties instead of hardcoding endpoint strings.

    Architecture Benefits:
        - Single source of truth for all API routes
        - Easy to refactor endpoints (change in one place)
        - Prevents duplicate endpoint definitions
        - Type-safe route references (IDE autocomplete)
        - Alphabetical ordering for easy navigation

    Usage in endpoint files:
        from app.config.endpoints import API_ROUTES

        router = APIRouter()

        @router.post(API_ROUTES.AUTH.LOGIN)
        async def login(...):
            pass

        @router.get(API_ROUTES.USERS.BY_ID)
        async def get_user(user_id: int, ...):
            pass

    Note: All properties below are alphabetically ordered (A-Z).
    When adding new routes, maintain alphabetical order.
    """

    ADMIN = AdminRoutes
    ASSIGNMENTS = AssignmentRoutes
    AUTH = AuthRoutes
    BLOCKED_COMPANIES = BlockedCompanyRoutes
    CALENDAR = CalendarRoutes
    CALENDAR_CONNECTIONS = CalendarConnectionRoutes
    COMPANIES = CompanyRoutes
    COMPANY_CONNECTIONS = CompanyConnectionRoutes
    CONNECTION_INVITATIONS = ConnectionInvitationRoutes
    DASHBOARD = DashboardRoutes
    EMAIL_PREVIEW = EmailPreviewRoutes
    EXAMS = ExamRoutes
    FEATURES = FeatureRoutes
    FILES = FileRoutes
    HOLIDAYS = HolidayRoutes
    INFRASTRUCTURE = InfrastructureRoutes
    INTERVIEWS = InterviewRoutes
    MBTI = MBTIRoutes
    MEETINGS = MeetingRoutes
    MESSAGES = MessageRoutes
    NOTIFICATIONS = NotificationRoutes
    POSITIONS = PositionRoutes
    PRIVACY_SETTINGS = PrivacySettingsRoutes
    PROFILE = ProfileRoutes
    PROFILE_VIEWS = ProfileViewRoutes
    PUBLIC = PublicRoutes
    QUESTION_BANKS = QuestionBankRoutes
    RECRUITER_PROFILE = RecruiterProfileRoutes
    RESUMES = ResumeRoutes
    SUBSCRIPTIONS = SubscriptionRoutes
    SYSTEM_UPDATES = SystemUpdateRoutes
    TODO_ATTACHMENTS = TodoAttachmentRoutes
    TODO_EXTENSIONS = TodoExtensionRoutes
    TODOS = TodoRoutes
    USER_CONNECTIONS = UserConnectionRoutes
    USERS = UserRoutes
    VIDEO_CALLS = VideoCallRoutes
    WEBHOOKS = WebhookRoutes
    WEBSOCKET_VIDEO = WebsocketVideoRoutes
    WORKFLOWS = WorkflowRoutes


# =============================================================================
# MODULE EXPORTS (Alphabetically Ordered A-Z)
# =============================================================================
# The __all__ list explicitly defines what gets exported when someone does:
#   from app.config.endpoints import *
#
# Purpose:
#   1. Controls what's publicly available from this module
#   2. Helps IDEs provide better autocomplete
#   3. Makes the module's public API explicit and clear
#   4. Prevents accidental export of internal utilities
#
# IMPORTANT: All exports MUST be in alphabetical order (A-Z)
#
# When adding new route classes:
#   1. Define the route class above (in alphabetical position)
#   2. Add it to API_ROUTES class (in alphabetical position)
#   3. Add it to __all__ list below (in alphabetical position)
# =============================================================================

__all__ = [
    "API_ROUTES",  # Main entry point - always use this in endpoint files
    "AdminRoutes",
    "AssignmentRoutes",
    "AuthRoutes",
    "BlockedCompanyRoutes",
    "CalendarConnectionRoutes",
    "CalendarRoutes",
    "CompanyConnectionRoutes",
    "CompanyRoutes",
    "ConnectionInvitationRoutes",
    "DashboardRoutes",
    "EmailPreviewRoutes",
    "ExamRoutes",
    "FeatureRoutes",
    "FileRoutes",
    "HolidayRoutes",
    "InfrastructureRoutes",
    "InterviewRoutes",
    "MBTIRoutes",
    "MeetingRoutes",
    "MessageRoutes",
    "NotificationRoutes",
    "PositionRoutes",
    "PrivacySettingsRoutes",
    "ProfileRoutes",
    "ProfileViewRoutes",
    "PublicRoutes",
    "QuestionBankRoutes",
    "RecruiterProfileRoutes",
    "ResumeRoutes",
    "SubscriptionRoutes",
    "SystemUpdateRoutes",
    "TodoAttachmentRoutes",
    "TodoExtensionRoutes",
    "TodoRoutes",
    "UserConnectionRoutes",
    "UserRoutes",
    "VideoCallRoutes",
    "WebhookRoutes",
    "WebsocketVideoRoutes",
    "WorkflowRoutes",
]

# =============================================================================
# FILE MAINTENANCE GUIDELINES
# =============================================================================
# When modifying this file, ensure the following:
#
# 1. ALPHABETICAL ORDER (Critical):
#    - Route class definitions: A-Z
#    - API_ROUTES properties: A-Z
#    - __all__ exports: A-Z
#
# 2. NEVER HARDCODE ENDPOINTS:
#    - All endpoint paths must be defined here
#    - Endpoint files must import from API_ROUTES
#    - This ensures single source of truth
#
# 3. ADDING NEW ROUTES:
#    Step 1: Create route class in alphabetical position
#    Step 2: Add class property to API_ROUTES (alphabetical position)
#    Step 3: Add to __all__ exports (alphabetical position)
#    Step 4: Add docstring explaining the route's purpose
#    Step 5: Use section comments to group related endpoints
#
# 4. DOCUMENTATION:
#    - Keep class docstrings up-to-date
#    - Use inline comments to explain endpoint groups
#    - Document complex endpoint patterns
#
# 5. VALIDATION:
#    - Check alphabetical order before committing
#    - Ensure no hardcoded paths in endpoint files
#    - Verify all routes are exported in __all__
#
# For architectural guidance, see: CLAUDE.md
# =============================================================================
