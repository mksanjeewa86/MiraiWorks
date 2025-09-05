import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { 
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

// Helper function for handling API responses
const handleResponse = <T>(response: AxiosResponse<ApiResponse<T>>): ApiResponse<T> => {
  return response.data;
};

// Authentication API
export const authApi = {
  login: (credentials: LoginCredentials): Promise<ApiResponse<AuthResponse>> =>
    api.post('/api/auth/login', credentials).then(handleResponse),

  register: (data: RegisterData): Promise<ApiResponse<AuthResponse>> =>
    api.post('/api/auth/register', data).then(handleResponse),

  verifyTwoFactor: (data: TwoFactorRequest): Promise<ApiResponse<AuthResponse>> =>
    api.post('/api/auth/verify-2fa', data).then(handleResponse),

  refreshToken: (refreshToken: string): Promise<ApiResponse<AuthResponse>> =>
    api.post('/api/auth/refresh', { refresh_token: refreshToken }).then(handleResponse),

  logout: (): Promise<void> =>
    api.post('/api/auth/logout').then(() => {}),

  getCurrentUser: (): Promise<ApiResponse<User>> =>
    api.get('/api/auth/me').then(handleResponse),

  requestPasswordReset: (email: string): Promise<ApiResponse<void>> =>
    api.post('/api/auth/request-password-reset', { email }).then(handleResponse),

  resetPassword: (token: string, newPassword: string): Promise<ApiResponse<void>> =>
    api.post('/api/auth/reset-password', { token, new_password: newPassword }).then(handleResponse),
};

// Users API
export const usersApi = {
  getUsers: (params?: { page?: number; limit?: number; search?: string }): Promise<ApiResponse<PaginatedResponse<User>>> =>
    api.get('/api/users', { params }).then(handleResponse),

  getUser: (id: number): Promise<ApiResponse<User>> =>
    api.get(`/api/users/${id}`).then(handleResponse),

  updateUser: (id: number, data: Partial<User>): Promise<ApiResponse<User>> =>
    api.put(`/api/users/${id}`, data).then(handleResponse),

  deleteUser: (id: number): Promise<ApiResponse<void>> =>
    api.delete(`/api/users/${id}`).then(handleResponse),

  bulkImportUsers: (file: File): Promise<ApiResponse<{ imported: number; errors: string[] }>> => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/api/users/bulk-import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }).then(handleResponse);
  },
};

// Messages API
export const messagesApi = {
  getConversations: (): Promise<ApiResponse<Conversation[]>> =>
    api.get('/api/messaging/conversations').then(handleResponse),

  getConversation: (id: number): Promise<ApiResponse<Conversation>> =>
    api.get(`/api/messaging/conversations/${id}`).then(handleResponse),

  createConversation: (participantIds: number[], title?: string): Promise<ApiResponse<Conversation>> =>
    api.post('/api/messaging/conversations', { participant_ids: participantIds, title }).then(handleResponse),

  getMessages: (conversationId: number, params?: { page?: number; limit?: number }): Promise<ApiResponse<PaginatedResponse<Message>>> =>
    api.get(`/api/messaging/conversations/${conversationId}/messages`, { params }).then(handleResponse),

  sendMessage: (conversationId: number, content: string, attachmentId?: number): Promise<ApiResponse<Message>> =>
    api.post(`/api/messaging/conversations/${conversationId}/messages`, {
      content,
      attachment_id: attachmentId,
    }).then(handleResponse),

  uploadAttachment: (file: File): Promise<ApiResponse<{ attachment_id: number; filename: string }>> => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/api/messaging/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }).then(handleResponse);
  },

  markAsRead: (conversationId: number): Promise<ApiResponse<void>> =>
    api.post(`/api/messaging/conversations/${conversationId}/read`).then(handleResponse),
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
    api.get('/api/interviews', { params }).then(handleResponse),

  getInterview: (id: number): Promise<ApiResponse<Interview>> =>
    api.get(`/api/interviews/${id}`).then(handleResponse),

  createInterview: (data: {
    candidate_id: number;
    recruiter_id: number;
    employer_company_id: number;
    title: string;
    description?: string;
    position_title?: string;
    interview_type: string;
  }): Promise<ApiResponse<Interview>> =>
    api.post('/api/interviews', data).then(handleResponse),

  updateInterview: (id: number, data: Partial<Interview>): Promise<ApiResponse<Interview>> =>
    api.put(`/api/interviews/${id}`, data).then(handleResponse),

  cancelInterview: (id: number, reason?: string): Promise<ApiResponse<Interview>> =>
    api.patch(`/api/interviews/${id}/cancel`, { reason }).then(handleResponse),

  createProposal: (interviewId: number, data: {
    start_datetime: string;
    end_datetime: string;
    timezone: string;
    location?: string;
    notes?: string;
  }): Promise<ApiResponse<any>> =>
    api.post(`/api/interviews/${interviewId}/proposals`, data).then(handleResponse),

  respondToProposal: (proposalId: number, data: {
    response: 'accepted' | 'declined';
    notes?: string;
  }): Promise<ApiResponse<any>> =>
    api.post(`/api/interviews/proposals/${proposalId}/respond`, data).then(handleResponse),

  getStats: (): Promise<ApiResponse<{
    total_interviews: number;
    by_status: Record<string, number>;
    by_type: Record<string, number>;
    upcoming_count: number;
    completed_count: number;
  }>> =>
    api.get('/api/interviews/stats').then(handleResponse),
};

// Calendar API
export const calendarApi = {
  getAccounts: (): Promise<ApiResponse<{ accounts: CalendarIntegration[] }>> =>
    api.get('/api/calendar/accounts').then(handleResponse),

  connectCalendar: (provider: 'google' | 'microsoft'): Promise<ApiResponse<{ auth_url: string; state: string }>> =>
    api.post('/api/calendar/connect', { provider }).then(handleResponse),

  disconnectCalendar: (accountId: number): Promise<ApiResponse<void>> =>
    api.delete(`/api/calendar/accounts/${accountId}`).then(handleResponse),

  getCalendars: (): Promise<ApiResponse<any[]>> =>
    api.get('/api/calendar/calendars').then(handleResponse),

  getEvents: (params?: {
    start_date?: string;
    end_date?: string;
    calendar_id?: string;
  }): Promise<ApiResponse<{ events: CalendarEvent[] }>> =>
    api.get('/api/calendar/events', { params }).then(handleResponse),

  syncCalendars: (): Promise<ApiResponse<{ success: boolean; synced_events: number }>> =>
    api.post('/api/calendar/sync').then(handleResponse),

  checkAvailability: (data: {
    participant_emails: string[];
    duration_minutes: number;
    preferred_times?: any[];
    timezone: string;
  }): Promise<ApiResponse<any>> =>
    api.post('/api/calendar/availability', data).then(handleResponse),
};

// Resumes API
export const resumesApi = {
  getResumes: (params?: {
    status?: string;
    limit?: number;
    offset?: number;
  }): Promise<ApiResponse<{ resumes: Resume[]; total: number; has_more: boolean }>> =>
    api.get('/api/resumes', { params }).then(handleResponse),

  getResume: (id: number): Promise<ApiResponse<Resume>> =>
    api.get(`/api/resumes/${id}`).then(handleResponse),

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
    api.post('/api/resumes', data).then(handleResponse),

  updateResume: (id: number, data: Partial<Resume>): Promise<ApiResponse<Resume>> =>
    api.put(`/api/resumes/${id}`, data).then(handleResponse),

  deleteResume: (id: number): Promise<ApiResponse<void>> =>
    api.delete(`/api/resumes/${id}`).then(handleResponse),

  duplicateResume: (id: number): Promise<ApiResponse<Resume>> =>
    api.post(`/api/resumes/${id}/duplicate`).then(handleResponse),

  getTemplates: (): Promise<ApiResponse<any[]>> =>
    api.get('/api/resumes/templates/available').then(handleResponse),

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
    api.post(`/api/resumes/${id}/generate-pdf`, { resume_id: id, ...data }).then(handleResponse),

  createShareLink: (id: number, data: {
    recipient_email?: string;
    password?: string;
    expires_in_days?: number;
    max_views?: number;
    allow_download?: boolean;
    show_contact_info?: boolean;
  }): Promise<ApiResponse<{ share_token: string }>> =>
    api.post(`/api/resumes/${id}/share`, data).then(handleResponse),

  addWorkExperience: (resumeId: number, data: any): Promise<ApiResponse<any>> =>
    api.post(`/api/resumes/${resumeId}/experiences`, data).then(handleResponse),

  addEducation: (resumeId: number, data: any): Promise<ApiResponse<any>> =>
    api.post(`/api/resumes/${resumeId}/education`, data).then(handleResponse),

  addSkill: (resumeId: number, data: any): Promise<ApiResponse<any>> =>
    api.post(`/api/resumes/${resumeId}/skills`, data).then(handleResponse),

  addProject: (resumeId: number, data: any): Promise<ApiResponse<any>> =>
    api.post(`/api/resumes/${resumeId}/projects`, data).then(handleResponse),
};

// Dashboard API
export const dashboardApi = {
  getStats: (): Promise<ApiResponse<DashboardStats>> =>
    api.get('/api/dashboard/stats').then(handleResponse),

  getRecentActivity: (limit?: number): Promise<ApiResponse<any[]>> =>
    api.get('/api/dashboard/activity', { params: { limit } }).then(handleResponse),
};

export default api;