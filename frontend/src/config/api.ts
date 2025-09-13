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
    VERIFY_2FA: '/api/auth/verify-2fa',
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
    BASE: '/api/companies',
    BY_ID: (id: string) => `/api/companies/${id}`,
  },
  
  // Job endpoints
  JOBS: {
    BASE: '/api/jobs',
    BY_ID: (id: string) => `/api/jobs/${id}`,
  },
  
  // Interview endpoints
  INTERVIEWS: {
    BASE: '/api/interviews',
    BY_ID: (id: string) => `/api/interviews/${id}`,
  },
  
  // Resume endpoints
  RESUMES: {
    BASE: '/api/resumes',
    BY_ID: (id: string) => `/api/resumes/${id}`,
  },
  
  // Message endpoints
  MESSAGES: {
    BASE: '/api/messages',
    BY_ID: (id: string) => `/api/messages/${id}`,
  },
  
  // Notification endpoints
  NOTIFICATIONS: {
    BASE: '/api/notifications',
    BY_ID: (id: string) => `/api/notifications/${id}`,
  },
  
  // Calendar endpoints
  CALENDAR: {
    BASE: '/api/calendar',
    EVENTS: '/api/calendar/events',
  },
  
  // Dashboard endpoints
  DASHBOARD: {
    BASE: '/api/dashboard',
    STATS: '/api/dashboard/stats',
  },
} as const;