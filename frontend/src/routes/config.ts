/**
 * Frontend Route Configuration
 *
 * IMPORTANT: All routes MUST be alphabetically ordered (A-Z)
 * - Top-level keys: alphabetically sorted
 * - Nested keys: alphabetically sorted within each section
 *
 * This file centralizes all frontend route definitions to:
 * - Provide type safety with TypeScript autocomplete
 * - Create a single source of truth for all routes
 * - Enable easy refactoring (change once, updates everywhere)
 * - Support internationalization with locale prefixing
 * - Prevent typos and route inconsistencies
 */

export const ROUTES = {
  // ===== ADMIN ROUTES =====
  ADMIN: {
    BASE: '/admin',
    EXAMS: {
      ANALYTICS: (id: string | number) => `/admin/exams/${id}/analytics`,
      ASSIGN: (id: string | number) => `/admin/exams/${id}/assign`,
      BASE: '/admin/exams',
      CREATE: '/admin/exams/create',
      EDIT: (id: string | number) => `/admin/exams/${id}/edit`,
      PREVIEW: (id: string | number) => `/admin/exams/${id}/preview`,
      SESSION: (sessionId: string | number) => `/admin/exams/sessions/${sessionId}`,
      STATISTICS: (id: string | number) => `/admin/exams/${id}/statistics`,
      TEMPLATES: {
        BASE: '/admin/exams/templates',
        CREATE: '/admin/exams/templates/create',
      },
    },
    PLAN_REQUESTS: '/admin/plan-requests',
    PLANS: '/admin/plans',
    QUESTION_BANKS: {
      BASE: '/admin/question-banks',
      BY_ID: (id: string | number) => `/admin/question-banks/${id}`,
      CREATE: '/admin/question-banks/create',
    },
    SETTINGS: '/admin/settings',
  },

  // ===== APP ROUTES =====
  APP: {
    APPLICATIONS: '/app/applications',
    CANDIDATES: '/app/candidates',
    EMPLOYEES: {
      BASE: '/app/employees',
      NEW: '/app/employees/new',
    },
    INTERVIEWS: '/app/interviews',
    JOBS: {
      BASE: '/app/jobs',
      NEW: '/app/jobs/new',
    },
    POSITIONS: '/app/positions',
    REPORTS: '/app/reports',
    SETTINGS: '/app/settings',
  },

  // ===== AUTHENTICATION ROUTES =====
  AUTH: {
    ACTIVATE: (userId: string | number) => `/activate/${userId}`,
    FORGOT_PASSWORD: '/auth/forgot-password',
    LOGIN: '/auth/login',
    LOGIN_EXPIRED: '/auth/login?expired=true',
    LOGIN_PASSWORD_RESET_SUCCESS: '/auth/login?message=password-reset-success',
    REGISTER: '/auth/register',
    REGISTER_CANDIDATE: '/auth/register?role=candidate',
    REGISTER_EMPLOYER: '/auth/register?role=employer',
    REGISTER_RECRUITER: '/auth/register?role=recruiter',
    RESET_PASSWORD: '/auth/reset-password',
    TWO_FACTOR: '/auth/two-factor',
    TWO_FACTOR_WITH_EMAIL: (email: string) => `/auth/two-factor?email=${encodeURIComponent(email)}`,
  },

  // ===== CALENDAR ROUTES =====
  CALENDAR: {
    BASE: '/calendar',
  },

  // ===== CANDIDATE ROUTES =====
  CANDIDATES: {
    BASE: '/candidates',
    NEW: '/candidates/new',
  },

  // ===== COMPANIES ROUTES =====
  COMPANIES: {
    ADD: '/companies/add',
    BASE: '/companies',
    EDIT: (id: string | number) => `/companies/${id}/edit`,
  },

  // ===== DASHBOARD ROUTES =====
  DASHBOARD: '/dashboard',

  // ===== EXAMS ROUTES =====
  EXAMS: {
    BASE: '/exams',
    DEMO: {
      BASE: '/exams/demo',
      BY_ID: (examId: string | number) => `/exams/demo/${examId}`,
    },
    RESULTS: (sessionId: string | number) => `/exams/results/${sessionId}`,
    TAKE: (examId: string | number) => `/exams/take/${examId}`,
  },

  // ===== HOME/ROOT ROUTES =====
  HOME: '/',

  // ===== INTERVIEWS ROUTES =====
  INTERVIEWS: {
    BASE: '/interviews',
    BY_ID: (id: string | number) => `/interviews/${id}`,
    EDIT: (id: string | number) => `/interviews/${id}/edit`,
    NEW: '/interviews/new',
  },

  // ===== JOBS ROUTES =====
  JOBS: {
    BASE: '/jobs',
  },

  // ===== LANDING PAGES ROUTES =====
  LANDING: {
    CANDIDATE: '/candidate',
    EMPLOYER: {
      ABOUT: '/employer/about',
      BASE: '/employer',
      CONTACT: '/employer/contact',
      PRICING: '/employer/pricing',
      SERVICES: '/employer/services',
    },
    RECRUITER: {
      ABOUT: '/recruiter/about',
      BASE: '/recruiter',
      CONTACT: '/recruiter/contact',
      PRICING: '/recruiter/pricing',
      SERVICES: '/recruiter/services',
    },
  },

  // ===== MESSAGES ROUTES =====
  MESSAGES: {
    BASE: '/messages',
  },

  // ===== NOTIFICATIONS ROUTES =====
  NOTIFICATIONS: {
    BASE: '/notifications',
  },

  // ===== POSITIONS ROUTES =====
  POSITIONS: {
    BASE: '/positions',
  },

  // ===== PROFILE ROUTES =====
  PROFILE: '/profile',

  // ===== PUBLIC ROUTES =====
  PUBLIC: {
    RESUME: (slug: string) => `/public/resume/${slug}`,
  },

  // ===== RESOURCES ROUTES =====
  RESOURCES: {
    CAREER_ADVICE: '/career-advice',
    INTERVIEW_PREP: '/interview-prep',
    POST_JOB: '/post-job',
    RECRUITMENT_SERVICES: '/recruitment-services',
    RESUME_TIPS: '/resume-tips',
    TALENT_SEARCH: '/talent-search',
  },

  // ===== RESUMES ROUTES =====
  RESUMES: {
    BASE: '/resumes',
    BUILDER: '/resumes/builder',
    CREATE: '/resumes/create',
    EDIT: (id: string | number) => `/resumes/${id}/edit`,
    PREVIEW: {
      BASE: '/resumes/preview',
      BY_ID: (id: string | number) => `/resumes/${id}/preview`,
    },
  },

  // ===== ROOM ROUTES =====
  ROOM: {
    BY_CODE: (roomCode: string) => `/room/${roomCode}`,
  },

  // ===== SETTINGS ROUTES =====
  SETTINGS: '/settings',

  // ===== SUBSCRIPTION ROUTES =====
  SUBSCRIPTION: {
    BASE: '/subscription',
  },

  // ===== TODOS ROUTES =====
  TODOS: {
    BASE: '/todos',
  },

  // ===== USERS ROUTES =====
  USERS: {
    ADD: '/users/add',
    BASE: '/users',
    EDIT: (id: string | number) => `/users/${id}/edit`,
  },

  // ===== VIDEO CALL ROUTES =====
  VIDEO_CALL: {
    BY_ID: (id: string | number) => `/video-call/${id}`,
  },

  // ===== WORKFLOWS ROUTES =====
  WORKFLOWS: {
    BASE: '/workflows',
  },
} as const;

/**
 * Helper function to add locale prefix to routes
 *
 * @param locale - The locale code (e.g., 'en', 'ja')
 * @param route - The route path
 * @returns The route with locale prefix
 *
 * @example
 * withLocale('en', ROUTES.DASHBOARD) // returns '/en/dashboard'
 * withLocale('ja', ROUTES.AUTH.LOGIN) // returns '/ja/auth/login'
 */
export function withLocale(locale: string, route: string): string {
  return `/${locale}${route}`;
}

/**
 * Type-safe route builder for routes with query parameters
 *
 * @param route - The base route
 * @param params - Query parameters as an object
 * @returns The route with query parameters
 *
 * @example
 * withQueryParams(ROUTES.AUTH.LOGIN, { expired: 'true' })
 * // returns '/auth/login?expired=true'
 */
export function withQueryParams(route: string, params: Record<string, string>): string {
  const queryString = new URLSearchParams(params).toString();
  return queryString ? `${route}?${queryString}` : route;
}

// Type exported from @/types/routes for centralized type management
export type { Routes } from '@/types/routes';
