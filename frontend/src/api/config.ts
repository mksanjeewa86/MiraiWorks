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

  // User endpoints
  USER: {
    PROFILE: '/api/auth/me',
    SETTINGS: '/api/user/settings',
  },

  // Company endpoints
  COMPANIES: {
    BASE: '/api/admin/companies',
    BY_ID: (id: string) => `/api/admin/companies/${id}`,
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

  // Interview endpoints
  INTERVIEWS: {
    BASE: '/api/interviews',
    BY_ID: (id: string | number) => `/api/interviews/${id}`,
    STATUS: (id: string | number) => `/api/interviews/${id}/status`,
    SCHEDULE: (id: string | number) => `/api/interviews/${id}/schedule`,
    NOTES: (id: string | number) => `/api/interviews/${id}/notes`,
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


  // File endpoints
  FILES: {
    UPLOAD: '/api/files/upload',
  },

  // Notification endpoints
  NOTIFICATIONS: {
    BASE: '/api/notifications',
    BY_ID: (id: string | number) => `/api/notifications/${id}`,
    UNREAD_COUNT: '/api/notifications/unread-count',
    MARK_READ: '/api/notifications/mark-read',
    MARK_ALL_READ: '/api/notifications/mark-all-read',
  },

  // Todo endpoints
  TODOS: {
    BASE: '/api/todos',
    BY_ID: (id: number | string) => `/api/todos/${id}`,
  },

  // Calendar endpoints
  CALENDAR: {
    BASE: '/api/calendar',
    EVENTS: '/api/calendar/events',
    EVENT_BY_ID: (id: string | number) => `/api/calendar/events/${id}`,
    AVAILABILITY: (userId: string | number) => `/api/calendar/availability/${userId}`,
  },

  // Dashboard endpoints
  DASHBOARD: {
    BASE: '/api/dashboard',
    STATS: '/api/dashboard/stats',
    ACTIVITY: '/api/dashboard/activity',
  },

  // Admin/Users endpoints (includes candidates)
  ADMIN: {
    USERS: '/api/admin/users',
    USER_BY_ID: (id: string | number) => `/api/admin/users/${id}`,
  },
} as const;