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
    BY_SLUG: (slug: string) => `/api/public/resumes/${slug}`,
    EXPERIENCES: (resumeId: string | number) => `/api/resumes/${resumeId}/experiences`,
    EXPERIENCE_BY_ID: (id: string | number) => `/api/experiences/${id}`,
    EDUCATION: (resumeId: string | number) => `/api/resumes/${resumeId}/education`,
    SKILLS: (resumeId: string | number) => `/api/resumes/${resumeId}/skills`,
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
    SETTINGS: '/api/user/settings',
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
} as const;