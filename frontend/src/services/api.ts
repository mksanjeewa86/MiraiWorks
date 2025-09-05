import axios, { type AxiosInstance } from 'axios';
import type { 
  AuthResponse, 
  LoginCredentials, 
  RegisterData, 
  TwoFactorRequest,
  User,
  ApiResponse,
  PaginatedResponse,
  Message,
  Conversation,
  Interview,
  Resume,
  CalendarIntegration,
  CalendarEvent,
  DashboardStats
} from '../types';

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('accessToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config;

    if (error.response?.status === 401 && !original._retry) {
      original._retry = true;

      try {
        const refreshToken = localStorage.getItem('refreshToken');
        if (refreshToken) {
          const response = await axios.post(
            `${api.defaults.baseURL}/api/auth/refresh`,
            { refresh_token: refreshToken }
          );

          const { accessToken } = response.data;
          localStorage.setItem('accessToken', accessToken);

          // Retry original request with new token
          original.headers.Authorization = `Bearer ${accessToken}`;
          return api(original);
        }
      } catch (refreshError) {
        // Refresh failed, redirect to login
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        window.location.href = '/login';
      }
    }

    return Promise.reject(error);
  }
);

// Helper functions for typed API calls
const apiGet = <T>(url: string, config?: any): Promise<ApiResponse<T>> =>
  api.get(url, config).then(response => response.data as ApiResponse<T>);

const apiPost = <T>(url: string, data?: any, config?: any): Promise<ApiResponse<T>> =>
  api.post(url, data, config).then(response => response.data as ApiResponse<T>);

const apiPut = <T>(url: string, data?: any, config?: any): Promise<ApiResponse<T>> =>
  api.put(url, data, config).then(response => response.data as ApiResponse<T>);

const apiPatch = <T>(url: string, data?: any, config?: any): Promise<ApiResponse<T>> =>
  api.patch(url, data, config).then(response => response.data as ApiResponse<T>);

const apiDelete = <T>(url: string, config?: any): Promise<ApiResponse<T>> =>
  api.delete(url, config).then(response => response.data as ApiResponse<T>);

// Authentication API
export const authApi = {
  login: (credentials: LoginCredentials): Promise<ApiResponse<AuthResponse>> =>
    apiPost<AuthResponse>('/api/auth/login', credentials),

  register: (data: RegisterData): Promise<ApiResponse<AuthResponse>> =>
    apiPost<AuthResponse>('/api/auth/register', data),

  verifyTwoFactor: (data: TwoFactorRequest): Promise<ApiResponse<AuthResponse>> =>
    apiPost<AuthResponse>('/api/auth/verify-2fa', data),

  refreshToken: (refreshToken: string): Promise<ApiResponse<AuthResponse>> =>
    apiPost<AuthResponse>('/api/auth/refresh', { refresh_token: refreshToken }),

  logout: (): Promise<void> =>
    api.post('/api/auth/logout').then(() => {}),

  getCurrentUser: (): Promise<ApiResponse<User>> =>
    apiGet<User>('/api/auth/me'),

  requestPasswordReset: (email: string): Promise<ApiResponse<void>> =>
    apiPost<void>('/api/auth/request-password-reset', { email }),

  resetPassword: (token: string, newPassword: string): Promise<ApiResponse<void>> =>
    apiPost<void>('/api/auth/reset-password', { token, new_password: newPassword }),
};

// Users API
export const usersApi = {
  getUsers: (params?: { page?: number; limit?: number; search?: string }): Promise<ApiResponse<PaginatedResponse<User>>> =>
    apiGet<PaginatedResponse<User>>('/api/users', { params }),

  getUser: (id: number): Promise<ApiResponse<User>> =>
    apiGet<User>(`/api/users/${id}`),

  updateUser: (id: number, data: Partial<User>): Promise<ApiResponse<User>> =>
    apiPut<User>(`/api/users/${id}`, data),

  deleteUser: (id: number): Promise<ApiResponse<void>> =>
    apiDelete<void>(`/api/users/${id}`),

  bulkImportUsers: (file: File): Promise<ApiResponse<{ imported: number; errors: string[] }>> => {
    const formData = new FormData();
    formData.append('file', file);
    return apiPost<{ imported: number; errors: string[] }>('/api/users/bulk-import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
};

// Messages API
export const messagesApi = {
  getConversations: (): Promise<ApiResponse<Conversation[]>> =>
    apiGet<Conversation[]>('/api/messaging/conversations'),

  getConversation: (id: number): Promise<ApiResponse<Conversation>> =>
    apiGet<Conversation>(`/api/messaging/conversations/${id}`),

  createConversation: (participantIds: number[], title?: string): Promise<ApiResponse<Conversation>> =>
    apiPost<Conversation>('/api/messaging/conversations', { participant_ids: participantIds, title }),

  getMessages: (conversationId: number, params?: { page?: number; limit?: number }): Promise<ApiResponse<PaginatedResponse<Message>>> =>
    apiGet<PaginatedResponse<Message>>(`/api/messaging/conversations/${conversationId}/messages`, { params }),

  sendMessage: (conversationId: number, content: string, attachmentId?: number): Promise<ApiResponse<Message>> =>
    apiPost<Message>(`/api/messaging/conversations/${conversationId}/messages`, {
      content,
      attachment_id: attachmentId,
    }),

  uploadAttachment: (file: File): Promise<ApiResponse<{ attachment_id: number; filename: string }>> => {
    const formData = new FormData();
    formData.append('file', file);
    return apiPost<{ attachment_id: number; filename: string }>('/api/messaging/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },

  markAsRead: (conversationId: number): Promise<ApiResponse<void>> =>
    apiPost<void>(`/api/messaging/conversations/${conversationId}/read`),
};

// Interviews API
export const interviewsApi = {
  getInterviews: (params?: {
    status?: string;
    candidate_id?: number;
    recruiter_id?: number;
    limit?: number;
    offset?: number;
  }): Promise<ApiResponse<{ interviews: Interview[]; total: number; has_more: boolean }>> =>
    apiGet<{ interviews: Interview[]; total: number; has_more: boolean }>('/api/interviews', { params }),

  getInterview: (id: number): Promise<ApiResponse<Interview>> =>
    apiGet<Interview>(`/api/interviews/${id}`),

  createInterview: (data: {
    candidate_id: number;
    recruiter_id: number;
    employer_company_id: number;
    title: string;
    description?: string;
    position_title?: string;
    interview_type: string;
  }): Promise<ApiResponse<Interview>> =>
    apiPost<Interview>('/api/interviews', data),

  updateInterview: (id: number, data: Partial<Interview>): Promise<ApiResponse<Interview>> =>
    apiPut<Interview>(`/api/interviews/${id}`, data),

  cancelInterview: (id: number, reason?: string): Promise<ApiResponse<Interview>> =>
    apiPatch<Interview>(`/api/interviews/${id}/cancel`, { reason }),

  createProposal: (interviewId: number, data: {
    start_datetime: string;
    end_datetime: string;
    timezone: string;
    location?: string;
    notes?: string;
  }): Promise<ApiResponse<any>> =>
    apiPost<any>(`/api/interviews/${interviewId}/proposals`, data),

  respondToProposal: (proposalId: number, data: {
    response: 'accepted' | 'declined';
    notes?: string;
  }): Promise<ApiResponse<any>> =>
    apiPost<any>(`/api/interviews/proposals/${proposalId}/respond`, data),

  getStats: (): Promise<ApiResponse<{
    total_interviews: number;
    by_status: Record<string, number>;
    by_type: Record<string, number>;
    upcoming_count: number;
    completed_count: number;
  }>> =>
    apiGet<{
      total_interviews: number;
      by_status: Record<string, number>;
      by_type: Record<string, number>;
      upcoming_count: number;
      completed_count: number;
    }>('/api/interviews/stats'),
};

// Calendar API
export const calendarApi = {
  getAccounts: (): Promise<ApiResponse<{ accounts: CalendarIntegration[] }>> =>
    apiGet<{ accounts: CalendarIntegration[] }>('/api/calendar/accounts'),

  connectCalendar: (provider: 'google' | 'microsoft'): Promise<ApiResponse<{ auth_url: string; state: string }>> =>
    apiPost<{ auth_url: string; state: string }>('/api/calendar/connect', { provider }),

  disconnectCalendar: (accountId: number): Promise<ApiResponse<void>> =>
    apiDelete<void>(`/api/calendar/accounts/${accountId}`),

  getCalendars: (): Promise<ApiResponse<any[]>> =>
    apiGet<any[]>('/api/calendar/calendars'),

  getEvents: (params?: {
    start_date?: string;
    end_date?: string;
    calendar_id?: string;
  }): Promise<ApiResponse<{ events: CalendarEvent[] }>> =>
    apiGet<{ events: CalendarEvent[] }>('/api/calendar/events', { params }),

  syncCalendars: (): Promise<ApiResponse<{ success: boolean; synced_events: number }>> =>
    apiPost<{ success: boolean; synced_events: number }>('/api/calendar/sync'),

  checkAvailability: (data: {
    participant_emails: string[];
    duration_minutes: number;
    preferred_times?: any[];
    timezone: string;
  }): Promise<ApiResponse<any>> =>
    apiPost<any>('/api/calendar/availability', data),
};

// Resumes API
export const resumesApi = {
  getResumes: (params?: {
    status?: string;
    limit?: number;
    offset?: number;
  }): Promise<ApiResponse<{ resumes: Resume[]; total: number; has_more: boolean }>> =>
    apiGet<{ resumes: Resume[]; total: number; has_more: boolean }>('/api/resumes', { params }),

  getResume: (id: number): Promise<ApiResponse<Resume>> =>
    apiGet<Resume>(`/api/resumes/${id}`),

  createResume: (data: {
    title: string;
    description?: string;
    full_name?: string;
    email?: string;
    phone?: string;
    location?: string;
    website?: string;
    linkedin_url?: string;
    github_url?: string;
    professional_summary?: string;
    template_id?: string;
  }): Promise<ApiResponse<Resume>> =>
    apiPost<Resume>('/api/resumes', data),

  updateResume: (id: number, data: Partial<Resume>): Promise<ApiResponse<Resume>> =>
    apiPut<Resume>(`/api/resumes/${id}`, data),

  deleteResume: (id: number): Promise<ApiResponse<void>> =>
    apiDelete<void>(`/api/resumes/${id}`),

  duplicateResume: (id: number): Promise<ApiResponse<Resume>> =>
    apiPost<Resume>(`/api/resumes/${id}/duplicate`),

  getTemplates: (): Promise<ApiResponse<any[]>> =>
    apiGet<any[]>('/api/resumes/templates/available'),

  previewResume: (id: number, templateId?: string): Promise<string> =>
    api.get(`/api/resumes/${id}/preview`, {
      params: { template_id: templateId },
      responseType: 'text',
    }).then(response => response.data),

  generatePdf: (id: number, data?: {
    format?: string;
    include_contact_info?: boolean;
    watermark?: string;
  }): Promise<ApiResponse<{ pdf_url: string; expires_at: string; file_size: number }>> =>
    apiPost<{ pdf_url: string; expires_at: string; file_size: number }>(`/api/resumes/${id}/generate-pdf`, { resume_id: id, ...data }),

  createShareLink: (id: number, data: {
    recipient_email?: string;
    password?: string;
    expires_in_days?: number;
    max_views?: number;
    allow_download?: boolean;
    show_contact_info?: boolean;
  }): Promise<ApiResponse<{ share_token: string }>> =>
    apiPost<{ share_token: string }>(`/api/resumes/${id}/share`, data),

  addWorkExperience: (resumeId: number, data: any): Promise<ApiResponse<any>> =>
    apiPost<any>(`/api/resumes/${resumeId}/experiences`, data),

  addEducation: (resumeId: number, data: any): Promise<ApiResponse<any>> =>
    apiPost<any>(`/api/resumes/${resumeId}/education`, data),

  addSkill: (resumeId: number, data: any): Promise<ApiResponse<any>> =>
    apiPost<any>(`/api/resumes/${resumeId}/skills`, data),

  addProject: (resumeId: number, data: any): Promise<ApiResponse<any>> =>
    apiPost<any>(`/api/resumes/${resumeId}/projects`, data),
};

// Dashboard API
export const dashboardApi = {
  getStats: (): Promise<ApiResponse<DashboardStats>> =>
    apiGet<DashboardStats>('/api/dashboard/stats'),

  getRecentActivity: (limit?: number): Promise<ApiResponse<any[]>> =>
    apiGet<any[]>('/api/dashboard/activity', { params: { limit } }),
};

export default api;