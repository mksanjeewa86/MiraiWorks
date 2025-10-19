// Centralized API configuration
export const API_CONFIG = {
  BASE_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  TIMEOUT: 30000, // 30 seconds
  RETRY_ATTEMPTS: 3,
} as const;

// Helper function to build API URLs
export const buildApiUrl = (endpoint: string): string => {
  // Ensure endpoint starts with /
  const normalizedEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  return `${API_CONFIG.BASE_URL}${normalizedEndpoint}`;
};

/**
 * Common API endpoints
 *
 * IMPORTANT ORDERING RULES:
 * - All top-level keys are ordered alphabetically (A-Z)
 * - All nested keys within each object are also ordered alphabetically
 * - This ordering makes it easier to:
 *   1. Find endpoints quickly
 *   2. Avoid duplicate endpoint definitions
 *   3. Maintain consistency across the codebase
 *   4. Review changes in pull requests
 *
 * WHEN ADDING NEW ENDPOINTS:
 * - Add the new key in alphabetical order relative to existing keys
 * - If adding to a nested object, maintain alphabetical order within that object
 * - Keep the comment above each section for clarity
 *
 * Example:
 * If adding a new endpoint starting with 'D', it should go between COMPANIES and EXAMS
 * If adding a new key to AUTH, ensure it's alphabetically ordered with LOGIN, LOGOUT, etc.
 */
export const API_ENDPOINTS = {
  // Admin/Users endpoints (includes candidates)
  ADMIN: {
    USER_BY_ID: (id: string | number) => `/api/admin/users/${id}`,
    USERS: '/api/admin/users',
  },

  // Admin endpoints
  ADMIN_EXTENDED: {
    // Audit logs
    AUDIT_LOGS: {
      ACTIVITY: '/api/admin/audit-logs/activity',
      BASE: '/api/admin/audit-logs',
      EXPORT: '/api/admin/audit-logs/export',
      FILTER_OPTIONS: '/api/admin/audit-logs/filter-options',
      STATS: '/api/admin/audit-logs/stats',
    },
    // Bulk operations
    BULK: {
      DELETE: '/api/admin/bulk/delete',
      ENTITY_COUNTS: '/api/admin/bulk/entity-counts',
      EXPORT: '/api/admin/bulk/export',
      IMPORT: '/api/admin/bulk/import',
      PREVIEW_DELETE: '/api/admin/bulk/preview-delete',
      PREVIEW_UPDATE: '/api/admin/bulk/preview-update',
      QUOTA: '/api/admin/bulk/quota',
      UPDATE: '/api/admin/bulk/update',
      VALIDATE_IDS: '/api/admin/bulk/validate-ids',
      VALIDATE_IMPORT: '/api/admin/bulk/validate-import',
    },
    // Security
    SECURITY: {
      ANTIVIRUS: {
        BULK_SCAN: '/api/admin/security/antivirus/bulk-scan',
        STATUS: '/api/admin/security/antivirus/status',
      },
      BULK_ACTION: '/api/admin/security/bulk-action',
      FILE_BY_ID: (fileId: number | string) => `/api/admin/security/files/${fileId}`,
      FILES: '/api/admin/security/files',
      LOGS: '/api/admin/security/logs',
      QUARANTINE_FILE: (fileId: number | string) =>
        `/api/admin/security/files/${fileId}/quarantine`,
      RESTORE_FILE: (fileId: number | string) => `/api/admin/security/files/${fileId}/restore`,
      SCAN_FILE: (fileId: number | string) => `/api/admin/security/files/${fileId}/scan`,
      STATS: '/api/admin/security/stats',
    },
    // System monitoring
    SYSTEM: {
      ALERTS: '/api/admin/system/alerts',
      BACKUP: '/api/admin/system/backup',
      CACHE: {
        CLEAR: '/api/admin/system/cache/clear',
        STATS: '/api/admin/system/cache/stats',
      },
      CONFIGURATION: '/api/admin/system/configuration',
      DATABASE: {
        STATS: '/api/admin/system/database/stats',
      },
      FEATURES: '/api/admin/system/features',
      HEALTH: '/api/admin/system/health',
      HEALTH_CHECK: '/api/admin/system/health-check',
      MAINTENANCE: {
        SCHEDULE: '/api/admin/system/maintenance/schedule',
      },
      PERFORMANCE: '/api/admin/system/performance',
      RESOURCES: '/api/admin/system/resources',
      SERVICES: (serviceName: string) => `/api/admin/system/services/${serviceName}`,
    },
    // Data migration
    DATA_MIGRATION: {
      JOBS: '/api/admin/data-migration/jobs',
      START: '/api/admin/data-migration/start',
    },
    // User bulk operations
    USERS_BULK: {
      DELETE: '/api/admin/users/bulk/delete',
      RESEND_ACTIVATION: '/api/admin/users/bulk/resend-activation',
      RESET_PASSWORD: '/api/admin/users/bulk/reset-password',
      SUSPEND: '/api/admin/users/bulk/suspend',
      UNSUSPEND: '/api/admin/users/bulk/unsuspend',
    },
  },

  // Assignment endpoints
  ASSIGNMENTS: {
    BY_ID: (id: number | string) => `/api/assignments/${id}`,
    MAKE_DRAFT: (id: number | string) => `/api/assignments/${id}/make-draft`,
    PENDING_REVIEW: '/api/assignments/pending-review',
    PUBLISH: (id: number | string) => `/api/assignments/${id}/publish`,
    REVIEW: (id: number | string) => `/api/assignments/${id}/review`,
    SUBMIT: (id: number | string) => `/api/assignments/${id}/submit`,
  },

  // Auth endpoints
  AUTH: {
    ACTIVATE: '/api/auth/activate',
    FORGOT_PASSWORD: '/api/auth/forgot-password',
    LOGIN: '/api/auth/login',
    LOGOUT: '/api/auth/logout',
    ME: '/api/auth/me',
    REFRESH: '/api/auth/refresh',
    REGISTER: '/api/auth/register',
    RESEND_2FA: '/api/auth/2fa/resend',
    RESET_PASSWORD: '/api/auth/reset-password',
    VERIFY_2FA: '/api/auth/2fa/verify',
  },

  // Blocked Companies endpoints
  BLOCKED_COMPANIES: {
    BASE: '/api/blocked-companies',
    BY_ID: (id: number | string) => `/api/blocked-companies/${id}`,
    SEARCH: '/api/blocked-companies/search',
  },

  // Calendar endpoints
  CALENDAR: {
    ACCOUNTS: {
      BASE: '/api/calendar/accounts',
      BY_ID: (connectionId: string | number) => `/api/calendar/accounts/${connectionId}`,
      SYNC: (connectionId: string | number) => `/api/calendar/accounts/${connectionId}/sync`,
    },
    AVAILABILITY: (userId: string | number) => `/api/calendar/availability/${userId}`,
    BASE: '/api/calendar',
    CONSOLIDATED: '/api/calendar/consolidated',
    EVENT_BY_ID: (id: string | number) => `/api/calendar/events/${id}`,
    EVENTS: '/api/calendar/events',
    RANGE: '/api/calendar/events/range',
    SEARCH: '/api/calendar/events/search',
    UPCOMING: '/api/calendar/events/upcoming',
  },

  // Calendar accounts
  CALENDAR_ACCOUNTS: '/api/calendar/accounts',

  // Calendar events bulk
  CALENDAR_EVENTS_BULK: '/api/calendar/events/bulk',

  // Calendar OAuth endpoints
  CALENDAR_OAUTH: {
    GOOGLE_START: '/api/calendar/oauth/google/start',
    MICROSOFT_START: '/api/calendar/oauth/microsoft/start',
  },

  // Company endpoints
  COMPANIES: {
    BASE: '/api/admin/companies',
    BY_ID: (id: string) => `/api/admin/companies/${id}`,
    MY_COMPANY: '/api/companies/my-company',
  },

  // Company Connections endpoints (new company-based connection system)
  COMPANY_CONNECTIONS: {
    ACTIVATE: (id: number | string) => `/api/company-connections/${id}/activate`,
    BASE: '/api/company-connections',
    BY_ID: (id: number | string) => `/api/company-connections/${id}`,
    COMPANY_TO_COMPANY: '/api/company-connections/company-to-company',
    DEACTIVATE: (id: number | string) => `/api/company-connections/${id}/deactivate`,
    MY_CONNECTIONS: '/api/company-connections/my-connections',
    USER_TO_COMPANY: '/api/company-connections/user-to-company',
  },

  // Exam endpoints
  EXAMS: {
    ASSIGNMENTS: (examId: number | string) => `/api/exam/exams/${examId}/assignments`,
    BASE: '/api/exam/exams',
    BY_ID: (id: number | string) => `/api/exam/exams/${id}`,
    EXPORT_EXCEL: (id: number | string) => `/api/exam/exams/${id}/export/excel`,
    EXPORT_PDF: (id: number | string) => `/api/exam/exams/${id}/export/pdf`,
    MY_ASSIGNMENTS: '/api/exam/my-assignments',
    QUESTIONS: (examId: number | string) => `/api/exam/exams/${examId}/questions`,
    SESSIONS: (examId: number | string) => `/api/exam/exams/${examId}/sessions`,
    STATISTICS: (id: number | string) => `/api/exam/exams/${id}/statistics`,
    TAKE: '/api/exam/exams/take',
  },

  // Exam Assignment endpoints
  EXAM_ASSIGNMENTS: {
    BY_ID: (assignmentId: number | string) => `/api/exam/assignments/${assignmentId}`,
  },

  // Exam Question endpoints
  EXAM_QUESTIONS: {
    BY_ID: (questionId: number | string) => `/api/exam/questions/${questionId}`,
  },

  // Exam Session endpoints
  EXAM_SESSIONS: {
    ANSWERS: (sessionId: number | string) => `/api/exam/sessions/${sessionId}/answers`,
    BY_ID: (sessionId: number | string) => `/api/exam/sessions/${sessionId}`,
    COMPLETE: (sessionId: number | string) => `/api/exam/sessions/${sessionId}/complete`,
    DETAILS: (sessionId: number | string) => `/api/exam/sessions/${sessionId}/details`,
    FACE_VERIFICATION: (sessionId: number | string) =>
      `/api/exam/sessions/${sessionId}/face-verification`,
    MONITORING: (sessionId: number | string) => `/api/exam/sessions/${sessionId}/monitoring`,
    RESET: (sessionId: number | string) => `/api/exam/sessions/${sessionId}/reset`,
    RESULTS: (sessionId: number | string) => `/api/exam/sessions/${sessionId}/results`,
    SUSPEND: (sessionId: number | string) => `/api/exam/sessions/${sessionId}/suspend`,
  },

  // Exam Template endpoints
  EXAM_TEMPLATES: {
    BASE: '/api/exam/templates',
    BY_ID: (templateId: number | string) => `/api/exam/templates/${templateId}`,
    FROM_EXAM: (examId: number | string) => `/api/exam/templates/from-exam/${examId}`,
  },

  // Features endpoints
  FEATURES: {
    ADD_TO_PLAN: (planId: number | string) => `/api/plan-features/${planId}`,
    BASE: '/api/features',
    BY_ID: (featureId: number | string) => `/api/features/${featureId}`,
    FLAT: '/api/features/flat',
    HIERARCHICAL: '/api/features/hierarchical',
    PLAN_FEATURES: (planId: number | string) => `/api/plan-features/${planId}`,
    REMOVE_FROM_PLAN: (planId: number | string, featureId: number | string) =>
      `/api/plan-features/${planId}/features/${featureId}`,
    SEARCH: (term: string) => `/api/features/search/${term}`,
  },

  // File endpoints
  FILES: {
    UPLOAD: '/api/files/upload',
  },

  // Interview endpoints
  INTERVIEWS: {
    BASE: '/api/interviews',
    BY_ID: (id: string | number) => `/api/interviews/${id}`,
    NOTES: (id: string | number) => `/api/interviews/${id}/notes`,
    SCHEDULE: (id: string | number) => `/api/interviews/${id}/schedule`,
    STATUS: (id: string | number) => `/api/interviews/${id}/status`,
    VIDEO_CALL: (id: string | number) => `/api/interviews/${id}/video-call`,
  },

  // MBTI endpoints
  MBTI: {
    ANSWER: '/api/mbti/answer',
    PROGRESS: '/api/mbti/progress',
    QUESTIONS: '/api/mbti/questions',
    RESULT: '/api/mbti/result',
    START: '/api/mbti/start',
    SUBMIT: '/api/mbti/submit',
    SUMMARY: '/api/mbti/summary',
    TYPE_DETAILS: (type: string) => `/api/mbti/types/${type}`,
    TYPES: '/api/mbti/types',
  },

  // Message endpoints (New unified system)
  MESSAGES: {
    BASE: '/api/messages',
    BY_ID: (id: string | number) => `/api/messages/${id}`,
    CONVERSATIONS: '/api/messages/conversations',
    MARK_READ: (userId: string | number) => `/api/messages/mark-conversation-read/${userId}`,
    PARTICIPANTS: '/api/messages/participants',
    SEARCH: '/api/messages/search',
    SEND: '/api/messages/send',
    WITH_USER: (userId: string | number) => `/api/messages/with/${userId}`,
  },

  // Messages extended
  MESSAGES_EXTENDED: {
    RESTRICTED_USERS: '/api/messages/restricted-users',
    UPLOAD: '/api/messages/upload',
    UPLOAD_CHUNK: '/api/messages/upload/chunk',
    UPLOAD_COMPLETE: '/api/messages/upload/complete',
  },

  // Notification endpoints
  NOTIFICATIONS: {
    BASE: '/api/notifications',
    BY_ID: (id: string | number) => `/api/notifications/${id}`,
    MARK_ALL_READ: '/api/notifications/mark-all-read',
    MARK_READ: '/api/notifications/mark-read',
    UNREAD_COUNT: '/api/notifications/unread-count',
  },

  // Position endpoints (updated from JOBS)
  POSITIONS: {
    BASE: '/api/positions',
    BULK_STATUS: '/api/positions/bulk/status',
    BY_ID: (id: string | number) => `/api/positions/${id}`,
    BY_SLUG: (slug: string) => `/api/positions/slug/${slug}`,
    COMPANY: (companyId: string | number) => `/api/positions/company/${companyId}`,
    EXPIRING: '/api/positions/expiring',
    POPULAR: '/api/positions/popular',
    PUBLIC: '/api/public/positions',
    RECENT: '/api/positions/recent',
    STATISTICS: '/api/positions/statistics',
    STATUS: (id: string | number) => `/api/positions/${id}/status`,
  },

  // Privacy Settings endpoints
  PRIVACY: {
    ME: '/api/privacy-settings/me',
  },

  // Profile endpoints
  PROFILE: {
    // Certifications
    CERTIFICATIONS: '/api/profile/certifications',
    CERTIFICATIONS_BY_ID: (id: number | string) => `/api/profile/certifications/${id}`,
    // Completeness
    COMPLETENESS: '/api/profile/completeness',
    // Education
    EDUCATION: '/api/profile/education',
    EDUCATION_BY_ID: (id: number | string) => `/api/profile/education/${id}`,
    // Job Preferences
    JOB_PREFERENCES: '/api/profile/job-preferences',
    // Projects
    PROJECTS: '/api/profile/projects',
    PROJECTS_BY_ID: (id: number | string) => `/api/profile/projects/${id}`,
    // Skills
    SKILLS: '/api/profile/skills',
    SKILLS_BY_ID: (id: number | string) => `/api/profile/skills/${id}`,
    // Work Experience
    WORK_EXPERIENCE: '/api/profile/work-experience',
    WORK_EXPERIENCE_BY_ID: (id: number | string) => `/api/profile/work-experience/${id}`,
  },

  // Profile Views endpoints
  PROFILE_VIEWS: {
    COUNT: '/api/profile-views/count',
    MY_VIEWS: '/api/profile-views/my-views',
    RECENT_VIEWERS: '/api/profile-views/recent-viewers',
    RECORD: '/api/profile-views/',
    STATS: '/api/profile-views/stats',
  },

  // Question Bank endpoints
  QUESTION_BANKS: {
    BASE: '/api/question-banks',
    BY_ID: (bankId: number | string) => `/api/question-banks/${bankId}`,
    CLONE: (bankId: number | string) => `/api/question-banks/${bankId}/clone`,
    STATS: (bankId: number | string) => `/api/question-banks/${bankId}/stats`,
  },

  // Recruiter Profile endpoints
  RECRUITER_PROFILE: {
    BY_USER_ID: (userId: number | string) => `/api/recruiter-profile/${userId}`,
    ME: '/api/recruiter-profile/me',
  },

  // Resume endpoints
  RESUMES: {
    BASE: '/api/resumes',
    BY_ID: (id: string | number) => `/api/resumes/${id}`,
    BY_SLUG: (slug: string) => `/api/public/resume/${slug}`,
    CERTIFICATIONS: (resumeId: string | number) => `/api/resumes/${resumeId}/certifications`,
    CONVERT_RIREKISHO: (id: string | number) => `/api/resumes/${id}/convert-to-rirekisho`,
    CONVERT_SHOKUMU: (id: string | number) => `/api/resumes/${id}/convert-to-shokumu`,
    EDUCATION: (resumeId: string | number) => `/api/resumes/${resumeId}/education`,
    EXPERIENCE_BY_ID: (id: string | number) => `/api/experiences/${id}`,
    EXPERIENCES: (resumeId: string | number) => `/api/resumes/${resumeId}/experiences`,
    GENERATE_PDF: (id: string | number) => `/api/resumes/${id}/generate-pdf`,
    LANGUAGES: (resumeId: string | number) => `/api/resumes/${resumeId}/languages`,
    PREVIEW: (id: string | number) => `/api/resumes/${id}/preview`,
    PROJECTS: (resumeId: string | number) => `/api/resumes/${resumeId}/projects`,
    PUBLIC_DOWNLOAD: (slug: string) => `/api/public/resume/${slug}/download-pdf`,
    PUBLIC_VIEW: (slug: string) => `/api/public/resume/${slug}/view`,
    REMOVE_PHOTO: (id: string | number) => `/api/resumes/${id}/remove-photo`,
    SEND_EMAIL: (id: string | number) => `/api/resumes/${id}/send-email`,
    SKILLS: (resumeId: string | number) => `/api/resumes/${resumeId}/skills`,
    TOGGLE_PUBLIC: (id: string | number) => `/api/resumes/${id}/toggle-public`,
    UPLOAD_PHOTO: (id: string | number) => `/api/resumes/${id}/upload-photo`,
  },

  // Subscription endpoints
  SUBSCRIPTIONS: {
    ALL_PLAN_CHANGE_REQUESTS: '/api/subscriptions/plan-change-requests',
    BULK_FEATURE_ACCESS: '/api/subscriptions/bulk-check-features',
    CANCEL_PLAN_CHANGE: (requestId: number | string) =>
      `/api/subscriptions/plan-change-requests/${requestId}/cancel`,
    CANCEL_SUBSCRIPTION: '/api/subscriptions/cancel',
    CHECK_FEATURE_ACCESS: (featureName: string) => `/api/subscriptions/check-feature/${featureName}`,
    MY_PLAN_CHANGE_REQUESTS: '/api/subscriptions/my-plan-change-requests',
    MY_SUBSCRIPTION: '/api/subscriptions/my-subscription',
    REQUEST_PLAN_CHANGE: '/api/subscriptions/plan-change-request',
    REVIEW_PLAN_CHANGE: (requestId: number | string) =>
      `/api/subscriptions/plan-change-requests/${requestId}/review`,
    SUBSCRIBE: '/api/subscriptions/subscribe',
    UPDATE_SUBSCRIPTION: '/api/subscriptions/update',
  },

  // Subscription Plans endpoints
  SUBSCRIPTION_PLANS: {
    BASE: '/api/subscriptions/plans',
    BY_ID: (planId: number | string) => `/api/subscriptions/plans/${planId}`,
    PUBLIC: '/api/subscriptions/plans',
    WITH_FEATURES: (planId: number | string) => `/api/subscriptions/plans/${planId}`,
  },

  // System Update endpoints
  SYSTEM_UPDATES: {
    ACTIVATE: (id: number | string) => `/api/system-updates/${id}/activate`,
    BASE: '/api/system-updates',
    BY_ID: (id: number | string) => `/api/system-updates/${id}`,
  },

  // Todo endpoints
  TODOS: {
    ASSIGN: (id: number | string) => `/api/todos/${id}/assign`,
    ASSIGNABLE_USERS: '/api/todos/assignable-users',
    ASSIGNED: '/api/todos/assigned',
    ATTACHMENTS: {
      BASE: (todoId: number | string) => `/api/todos/${todoId}/attachments`,
      BULK_DELETE: (todoId: number | string) => `/api/todos/${todoId}/attachments/bulk-delete`,
      BY_ID: (todoId: number | string, attachmentId: number | string) =>
        `/api/todos/${todoId}/attachments/${attachmentId}`,
      DOWNLOAD: (todoId: number | string, attachmentId: number | string) =>
        `/api/todos/${todoId}/attachments/${attachmentId}/download`,
      MY_UPLOADS: '/api/attachments/my-uploads',
      PREVIEW: (todoId: number | string, attachmentId: number | string) =>
        `/api/todos/${todoId}/attachments/${attachmentId}/preview`,
      STATS: (todoId: number | string) => `/api/todos/${todoId}/attachments/stats`,
      UPLOAD: (todoId: number | string) => `/api/todos/${todoId}/attachments/upload`,
    },
    BASE: '/api/todos',
    BY_ID: (id: number | string) => `/api/todos/${id}`,
    COMPLETE: (id: number | string) => `/api/todos/${id}/complete`,
    DETAILS: (id: number | string) => `/api/todos/${id}/details`,
    EXTENSIONS: {
      BY_ID: (requestId: number | string) => `/api/todos/extension-requests/${requestId}`,
      CREATE: (todoId: number | string) => `/api/todos/${todoId}/extension-requests`,
      MY_REQUESTS: '/api/todos/extension-requests/my-requests',
      RESPOND: (requestId: number | string) => `/api/todos/extension-requests/${requestId}/respond`,
      TO_REVIEW: '/api/todos/extension-requests/to-review',
      VALIDATE: (todoId: number | string) => `/api/todos/extension-requests/validate/${todoId}`,
    },
    RECENT: '/api/todos/recent',
    REOPEN: (id: number | string) => `/api/todos/${id}/reopen`,
    RESTORE: (id: number | string) => `/api/todos/${id}/restore`,
    VIEWABLE: '/api/todos/viewable',
    VIEWERS: {
      ADD: (todoId: number | string) => `/api/todos/${todoId}/viewers`,
      LIST: (todoId: number | string) => `/api/todos/${todoId}/viewers`,
      REMOVE: (todoId: number | string, viewerUserId: number | string) =>
        `/api/todos/${todoId}/viewers/${viewerUserId}`,
    },
  },

  // User endpoints
  USER: {
    PROFILE: '/api/auth/me',
    SETTINGS: '/api/user/settings',
    UPDATE_PROFILE: '/api/user/profile',
  },

  // General Users endpoints (non-admin)
  USERS: {
    BASE: '/api/users',
  },

  // User Connections endpoints
  USER_CONNECTIONS: {
    ASSIGNABLE_USERS: '/api/user/connections/assignable-users',
    CONNECT: (userId: number | string) => `/api/user/connections/connect/${userId}`,
    DISCONNECT: (userId: number | string) => `/api/user/connections/disconnect/${userId}`,
    MY_CONNECTIONS: '/api/user/connections/my-connections',
  },

  // Video Call endpoints
  VIDEO_CALLS: {
    BY_ID: (id: string | number) => `/api/video-calls/${id}`,
    BY_ROOM: (roomCode: string) => `/api/video-calls/room/${roomCode}`,
    CONSENT: (id: string | number) => `/api/video-calls/${id}/consent`,
    CONSENT_ROOM: (roomCode: string) => `/api/video-calls/room/${roomCode}/consent`,
    JOIN: (id: string | number) => `/api/video-calls/${id}/join`,
    JOIN_ROOM: (roomCode: string) => `/api/video-calls/room/${roomCode}/join`,
    LEAVE: (id: string | number) => `/api/video-calls/${id}/leave`,
    LEAVE_ROOM: (roomCode: string) => `/api/video-calls/room/${roomCode}/leave`,
    TRANSCRIPT: (id: string | number) => `/api/video-calls/${id}/transcript`,
    TRANSCRIPT_DOWNLOAD: (id: string | number) => `/api/video-calls/${id}/transcript/download`,
    TRANSCRIPT_SEGMENTS: (id: string | number) => `/api/video-calls/${id}/transcript/segments`,
  },

  // Workflow/Recruitment Process endpoints
  WORKFLOWS: {
    BASE: '/api/recruitment-processes/',
  },
} as const;
