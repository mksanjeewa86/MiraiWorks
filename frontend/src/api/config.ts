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

// Common API endpoints
export const API_ENDPOINTS = {
  // Admin/Users endpoints (includes candidates)
  ADMIN: {
    USERS: '/api/admin/users',
    USER_BY_ID: (id: string | number) => `/api/admin/users/${id}`,
  },

  // General Users endpoints (non-admin)
  USERS: {
    BASE: '/api/users',
  },

  // Auth endpoints
  AUTH: {
    LOGIN: '/api/auth/login',
    REGISTER: '/api/auth/register',
    LOGOUT: '/api/auth/logout',
    REFRESH: '/api/auth/refresh',
    ME: '/api/auth/me',
    VERIFY_2FA: '/api/auth/2fa/verify',
    ACTIVATE: '/api/auth/activate',
    FORGOT_PASSWORD: '/api/auth/forgot-password',
    RESET_PASSWORD: '/api/auth/reset-password',
  },

  // Calendar endpoints
  CALENDAR: {
    BASE: '/api/calendar',
    EVENTS: '/api/calendar/events',
    EVENT_BY_ID: (id: string | number) => `/api/calendar/events/${id}`,
    AVAILABILITY: (userId: string | number) => `/api/calendar/availability/${userId}`,
    RANGE: '/api/calendar/events/range',
    UPCOMING: '/api/calendar/events/upcoming',
    SEARCH: '/api/calendar/events/search',
    CONSOLIDATED: '/api/calendar/consolidated',
    ACCOUNTS: {
      BASE: '/api/calendar/accounts',
      BY_ID: (connectionId: string | number) => `/api/calendar/accounts/${connectionId}`,
      SYNC: (connectionId: string | number) => `/api/calendar/accounts/${connectionId}/sync`,
    },
  },

  // Company endpoints
  COMPANIES: {
    BASE: '/api/admin/companies',
    BY_ID: (id: string) => `/api/admin/companies/${id}`,
  },

  // Dashboard endpoints
  DASHBOARD: {
    BASE: '/api/dashboard',
    STATS: '/api/dashboard/stats',
    ACTIVITY: '/api/dashboard/activity',
  },

  // File endpoints
  FILES: {
    UPLOAD: '/api/files/upload',
  },

  // Interview endpoints
  INTERVIEWS: {
    BASE: '/api/interviews',
    BY_ID: (id: string | number) => `/api/interviews/${id}`,
    STATUS: (id: string | number) => `/api/interviews/${id}/status`,
    SCHEDULE: (id: string | number) => `/api/interviews/${id}/schedule`,
    NOTES: (id: string | number) => `/api/interviews/${id}/notes`,
    VIDEO_CALL: (id: string | number) => `/api/interviews/${id}/video-call`,
  },

  // Message endpoints (New unified system)
  MESSAGES: {
    BASE: '/api/messages',
    BY_ID: (id: string | number) => `/api/messages/${id}`,
    CONVERSATIONS: '/api/messages/conversations',
    WITH_USER: (userId: string | number) => `/api/messages/with/${userId}`,
    SEND: '/api/messages/send',
    MARK_READ: (userId: string | number) => `/api/messages/mark-conversation-read/${userId}`,
    SEARCH: '/api/messages/search',
    PARTICIPANTS: '/api/messages/participants',
  },

  // Notification endpoints
  NOTIFICATIONS: {
    BASE: '/api/notifications',
    BY_ID: (id: string | number) => `/api/notifications/${id}`,
    UNREAD_COUNT: '/api/notifications/unread-count',
    MARK_READ: '/api/notifications/mark-read',
    MARK_ALL_READ: '/api/notifications/mark-all-read',
  },

  // Position endpoints (updated from JOBS)
  POSITIONS: {
    BASE: '/api/positions',
    BY_ID: (id: string | number) => `/api/positions/${id}`,
    BY_SLUG: (slug: string) => `/api/positions/slug/${slug}`,
    PUBLIC: '/api/public/positions',
    POPULAR: '/api/positions/popular',
    RECENT: '/api/positions/recent',
    COMPANY: (companyId: string | number) => `/api/positions/company/${companyId}`,
    EXPIRING: '/api/positions/expiring',
    STATISTICS: '/api/positions/statistics',
    STATUS: (id: string | number) => `/api/positions/${id}/status`,
    BULK_STATUS: '/api/positions/bulk/status',
  },

  // Resume endpoints
  RESUMES: {
    BASE: '/api/resumes',
    BY_ID: (id: string | number) => `/api/resumes/${id}`,
    BY_SLUG: (slug: string) => `/api/public/resume/${slug}`,
    PREVIEW: (id: string | number) => `/api/resumes/${id}/preview`,
    GENERATE_PDF: (id: string | number) => `/api/resumes/${id}/generate-pdf`,
    UPLOAD_PHOTO: (id: string | number) => `/api/resumes/${id}/upload-photo`,
    REMOVE_PHOTO: (id: string | number) => `/api/resumes/${id}/remove-photo`,
    TOGGLE_PUBLIC: (id: string | number) => `/api/resumes/${id}/toggle-public`,
    CONVERT_RIREKISHO: (id: string | number) => `/api/resumes/${id}/convert-to-rirekisho`,
    CONVERT_SHOKUMU: (id: string | number) => `/api/resumes/${id}/convert-to-shokumu`,
    SEND_EMAIL: (id: string | number) => `/api/resumes/${id}/send-email`,
    PUBLIC_VIEW: (slug: string) => `/api/public/resume/${slug}/view`,
    PUBLIC_DOWNLOAD: (slug: string) => `/api/public/resume/${slug}/download-pdf`,
    EXPERIENCES: (resumeId: string | number) => `/api/resumes/${resumeId}/experiences`,
    EXPERIENCE_BY_ID: (id: string | number) => `/api/experiences/${id}`,
    EDUCATION: (resumeId: string | number) => `/api/resumes/${resumeId}/education`,
    SKILLS: (resumeId: string | number) => `/api/resumes/${resumeId}/skills`,
    PROJECTS: (resumeId: string | number) => `/api/resumes/${resumeId}/projects`,
    CERTIFICATIONS: (resumeId: string | number) => `/api/resumes/${resumeId}/certifications`,
    LANGUAGES: (resumeId: string | number) => `/api/resumes/${resumeId}/languages`,
  },

  // Todo endpoints
  TODOS: {
    BASE: '/api/todos',
    BY_ID: (id: number | string) => `/api/todos/${id}`,
    RECENT: '/api/todos/recent',
    ASSIGNABLE_USERS: '/api/todos/assignable-users',
    ASSIGNED: '/api/todos/assigned',
    DETAILS: (id: number | string) => `/api/todos/${id}/details`,
    ASSIGN: (id: number | string) => `/api/todos/${id}/assign`,
    VIEWERS: (id: number | string) => `/api/todos/${id}/viewers`,
    COMPLETE: (id: number | string) => `/api/todos/${id}/complete`,
    REOPEN: (id: number | string) => `/api/todos/${id}/reopen`,
    RESTORE: (id: number | string) => `/api/todos/${id}/restore`,
    ATTACHMENTS: {
      BASE: (todoId: number | string) => `/api/todos/${todoId}/attachments`,
      UPLOAD: (todoId: number | string) => `/api/todos/${todoId}/attachments/upload`,
      BY_ID: (todoId: number | string, attachmentId: number | string) =>
        `/api/todos/${todoId}/attachments/${attachmentId}`,
      DOWNLOAD: (todoId: number | string, attachmentId: number | string) =>
        `/api/todos/${todoId}/attachments/${attachmentId}/download`,
      PREVIEW: (todoId: number | string, attachmentId: number | string) =>
        `/api/todos/${todoId}/attachments/${attachmentId}/preview`,
      BULK_DELETE: (todoId: number | string) => `/api/todos/${todoId}/attachments/bulk-delete`,
      STATS: (todoId: number | string) => `/api/todos/${todoId}/attachments/stats`,
      MY_UPLOADS: '/api/attachments/my-uploads',
    },
    EXTENSIONS: {
      CREATE: (todoId: number | string) => `/api/todos/${todoId}/extension-requests`,
      VALIDATE: (todoId: number | string) => `/api/todos/extension-requests/validate/${todoId}`,
      RESPOND: (requestId: number | string) => `/api/todos/extension-requests/${requestId}/respond`,
      MY_REQUESTS: '/api/todos/extension-requests/my-requests',
      TO_REVIEW: '/api/todos/extension-requests/to-review',
      BY_ID: (requestId: number | string) => `/api/todos/extension-requests/${requestId}`,
    },
  },

  // User endpoints
  USER: {
    PROFILE: '/api/auth/me',
    UPDATE_PROFILE: '/api/user/profile',
    SETTINGS: '/api/user/settings',
  },

  // Video Call endpoints
  VIDEO_CALLS: {
    BY_ID: (id: string | number) => `/api/video-calls/${id}`,
    BY_ROOM: (roomCode: string) => `/api/video-calls/room/${roomCode}`,
    JOIN: (id: string | number) => `/api/video-calls/${id}/join`,
    JOIN_ROOM: (roomCode: string) => `/api/video-calls/room/${roomCode}/join`,
    LEAVE: (id: string | number) => `/api/video-calls/${id}/leave`,
    LEAVE_ROOM: (roomCode: string) => `/api/video-calls/room/${roomCode}/leave`,
    CONSENT: (id: string | number) => `/api/video-calls/${id}/consent`,
    CONSENT_ROOM: (roomCode: string) => `/api/video-calls/room/${roomCode}/consent`,
    TRANSCRIPT: (id: string | number) => `/api/video-calls/${id}/transcript`,
    TRANSCRIPT_SEGMENTS: (id: string | number) => `/api/video-calls/${id}/transcript/segments`,
    TRANSCRIPT_DOWNLOAD: (id: string | number) => `/api/video-calls/${id}/transcript/download`,
  },

  // MBTI endpoints
  MBTI: {
    START: '/api/mbti/start',
    QUESTIONS: '/api/mbti/questions',
    ANSWER: '/api/mbti/answer',
    SUBMIT: '/api/mbti/submit',
    RESULT: '/api/mbti/result',
    SUMMARY: '/api/mbti/summary',
    PROGRESS: '/api/mbti/progress',
    TYPES: '/api/mbti/types',
    TYPE_DETAILS: (type: string) => `/api/mbti/types/${type}`,
  },

  // Workflow/Recruitment Process endpoints
  WORKFLOWS: {
    BASE: '/api/recruitment-processes/',
  },

  // Exam endpoints
  EXAMS: {
    BASE: '/api/exam/exams',
    BY_ID: (id: number | string) => `/api/exam/exams/${id}`,
    TAKE: '/api/exam/exams/take',
    MY_ASSIGNMENTS: '/api/exam/my-assignments',
    STATISTICS: (id: number | string) => `/api/exam/exams/${id}/statistics`,
    EXPORT_PDF: (id: number | string) => `/api/exam/exams/${id}/export/pdf`,
    EXPORT_EXCEL: (id: number | string) => `/api/exam/exams/${id}/export/excel`,
    QUESTIONS: (examId: number | string) => `/api/exam/exams/${examId}/questions`,
    ASSIGNMENTS: (examId: number | string) => `/api/exam/exams/${examId}/assignments`,
    SESSIONS: (examId: number | string) => `/api/exam/exams/${examId}/sessions`,
  },

  // Exam Question endpoints
  EXAM_QUESTIONS: {
    BY_ID: (questionId: number | string) => `/api/exam/questions/${questionId}`,
  },

  // Exam Assignment endpoints
  EXAM_ASSIGNMENTS: {
    BY_ID: (assignmentId: number | string) => `/api/exam/assignments/${assignmentId}`,
  },

  // Exam Session endpoints
  EXAM_SESSIONS: {
    BY_ID: (sessionId: number | string) => `/api/exam/sessions/${sessionId}`,
    ANSWERS: (sessionId: number | string) => `/api/exam/sessions/${sessionId}/answers`,
    COMPLETE: (sessionId: number | string) => `/api/exam/sessions/${sessionId}/complete`,
    RESULTS: (sessionId: number | string) => `/api/exam/sessions/${sessionId}/results`,
    DETAILS: (sessionId: number | string) => `/api/exam/sessions/${sessionId}/details`,
    SUSPEND: (sessionId: number | string) => `/api/exam/sessions/${sessionId}/suspend`,
    RESET: (sessionId: number | string) => `/api/exam/sessions/${sessionId}/reset`,
    MONITORING: (sessionId: number | string) => `/api/exam/sessions/${sessionId}/monitoring`,
    FACE_VERIFICATION: (sessionId: number | string) =>
      `/api/exam/sessions/${sessionId}/face-verification`,
  },

  // Exam Template endpoints
  EXAM_TEMPLATES: {
    BASE: '/api/exam/templates',
    BY_ID: (templateId: number | string) => `/api/exam/templates/${templateId}`,
    FROM_EXAM: (examId: number | string) => `/api/exam/templates/from-exam/${examId}`,
  },

  // Question Bank endpoints
  QUESTION_BANKS: {
    BASE: '/api/question-banks',
    BY_ID: (bankId: number | string) => `/api/question-banks/${bankId}`,
    CLONE: (bankId: number | string) => `/api/question-banks/${bankId}/clone`,
    STATS: (bankId: number | string) => `/api/question-banks/${bankId}/stats`,
  },

  // Assignment endpoints
  ASSIGNMENTS: {
    PENDING_REVIEW: '/api/assignments/pending-review',
    BY_ID: (id: number | string) => `/api/assignments/${id}`,
    PUBLISH: (id: number | string) => `/api/assignments/${id}/publish`,
    MAKE_DRAFT: (id: number | string) => `/api/assignments/${id}/make-draft`,
    SUBMIT: (id: number | string) => `/api/assignments/${id}/submit`,
    REVIEW: (id: number | string) => `/api/assignments/${id}/review`,
  },

  // Admin endpoints
  ADMIN_EXTENDED: {
    // Audit logs
    AUDIT_LOGS: {
      BASE: '/api/admin/audit-logs',
      STATS: '/api/admin/audit-logs/stats',
      ACTIVITY: '/api/admin/audit-logs/activity',
      EXPORT: '/api/admin/audit-logs/export',
      FILTER_OPTIONS: '/api/admin/audit-logs/filter-options',
    },
    // Bulk operations
    BULK: {
      DELETE: '/api/admin/bulk/delete',
      UPDATE: '/api/admin/bulk/update',
      EXPORT: '/api/admin/bulk/export',
      IMPORT: '/api/admin/bulk/import',
      VALIDATE_IDS: '/api/admin/bulk/validate-ids',
      VALIDATE_IMPORT: '/api/admin/bulk/validate-import',
      PREVIEW_DELETE: '/api/admin/bulk/preview-delete',
      PREVIEW_UPDATE: '/api/admin/bulk/preview-update',
      ENTITY_COUNTS: '/api/admin/bulk/entity-counts',
      QUOTA: '/api/admin/bulk/quota',
    },
    // Security
    SECURITY: {
      STATS: '/api/admin/security/stats',
      FILES: '/api/admin/security/files',
      FILE_BY_ID: (fileId: number | string) => `/api/admin/security/files/${fileId}`,
      SCAN_FILE: (fileId: number | string) => `/api/admin/security/files/${fileId}/scan`,
      QUARANTINE_FILE: (fileId: number | string) =>
        `/api/admin/security/files/${fileId}/quarantine`,
      RESTORE_FILE: (fileId: number | string) => `/api/admin/security/files/${fileId}/restore`,
      LOGS: '/api/admin/security/logs',
      BULK_ACTION: '/api/admin/security/bulk-action',
      ANTIVIRUS: {
        STATUS: '/api/admin/security/antivirus/status',
        BULK_SCAN: '/api/admin/security/antivirus/bulk-scan',
      },
    },
    // System monitoring
    SYSTEM: {
      HEALTH: '/api/admin/system/health',
      HEALTH_CHECK: '/api/admin/system/health-check',
      ALERTS: '/api/admin/system/alerts',
      BACKUP: '/api/admin/system/backup',
      CONFIGURATION: '/api/admin/system/configuration',
      FEATURES: '/api/admin/system/features',
      SERVICES: (serviceName: string) => `/api/admin/system/services/${serviceName}`,
      PERFORMANCE: '/api/admin/system/performance',
      RESOURCES: '/api/admin/system/resources',
      DATABASE: {
        STATS: '/api/admin/system/database/stats',
      },
      CACHE: {
        STATS: '/api/admin/system/cache/stats',
        CLEAR: '/api/admin/system/cache/clear',
      },
      MAINTENANCE: {
        SCHEDULE: '/api/admin/system/maintenance/schedule',
      },
    },
    // Data migration
    DATA_MIGRATION: {
      START: '/api/admin/data-migration/start',
      JOBS: '/api/admin/data-migration/jobs',
    },
    // User bulk operations
    USERS_BULK: {
      DELETE: '/api/admin/users/bulk/delete',
      SUSPEND: '/api/admin/users/bulk/suspend',
      UNSUSPEND: '/api/admin/users/bulk/unsuspend',
      RESET_PASSWORD: '/api/admin/users/bulk/reset-password',
      RESEND_ACTIVATION: '/api/admin/users/bulk/resend-activation',
    },
  },

  // Calendar OAuth endpoints
  CALENDAR_OAUTH: {
    GOOGLE_START: '/api/calendar/oauth/google/start',
    MICROSOFT_START: '/api/calendar/oauth/microsoft/start',
  },

  // Calendar accounts
  CALENDAR_ACCOUNTS: '/api/calendar/accounts',

  // Calendar events bulk
  CALENDAR_EVENTS_BULK: '/api/calendar/events/bulk',

  // Messages extended
  MESSAGES_EXTENDED: {
    UPLOAD: '/api/messages/upload',
    UPLOAD_CHUNK: '/api/messages/upload/chunk',
    UPLOAD_COMPLETE: '/api/messages/upload/complete',
    RESTRICTED_USERS: '/api/messages/restricted-users',
  },

  // Subscription endpoints
  SUBSCRIPTIONS: {
    MY_SUBSCRIPTION: '/api/subscriptions/my-subscription',
    SUBSCRIBE: '/api/subscriptions/subscribe',
    UPDATE_SUBSCRIPTION: '/api/subscriptions/update',
    CANCEL_SUBSCRIPTION: '/api/subscriptions/cancel',
    CHECK_FEATURE_ACCESS: (featureName: string) => `/api/subscriptions/check-feature/${featureName}`,
    BULK_FEATURE_ACCESS: '/api/subscriptions/bulk-check-features',
    MY_PLAN_CHANGE_REQUESTS: '/api/subscriptions/my-plan-change-requests',
    ALL_PLAN_CHANGE_REQUESTS: '/api/subscriptions/plan-change-requests',
    REQUEST_PLAN_CHANGE: '/api/subscriptions/request-plan-change',
    REVIEW_PLAN_CHANGE: (requestId: number | string) =>
      `/api/subscriptions/plan-change-requests/${requestId}/review`,
  },

  // Subscription Plans endpoints
  SUBSCRIPTION_PLANS: {
    BASE: '/api/subscription-plans',
    BY_ID: (planId: number | string) => `/api/subscription-plans/${planId}`,
    PUBLIC: '/api/subscription-plans/public',
    WITH_FEATURES: (planId: number | string) => `/api/subscription-plans/${planId}/features`,
  },

  // Features endpoints
  FEATURES: {
    BASE: '/api/features',
    BY_ID: (featureId: number | string) => `/api/features/${featureId}`,
    HIERARCHICAL: '/api/features/hierarchical',
    FLAT: '/api/features/flat',
    SEARCH: (term: string) => `/api/features/search/${term}`,
    PLAN_FEATURES: (planId: number | string) => `/api/plan-features/${planId}`,
    ADD_TO_PLAN: (planId: number | string) => `/api/plan-features/${planId}`,
    REMOVE_FROM_PLAN: (planId: number | string, featureId: number | string) =>
      `/api/plan-features/${planId}/features/${featureId}`,
  },
} as const;
