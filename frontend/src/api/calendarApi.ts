import {
  CalendarConnection,
  CalendarConnectionUpdate,
  CalendarConnectionResponse,
  CalendarListResponse,
  CalendarAuthResponse,
} from '@/types/calendar';
import { API_CONFIG } from '@/config/api';

// Helper function to get auth token from localStorage
const getAuthToken = (): string | null => {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('accessToken');
  }
  return null;
};

// Helper function to make authenticated requests
const makeAuthenticatedRequest = async <T>(
  url: string,
  options: RequestInit = {}
): Promise<{ data: T }> => {
  const token = getAuthToken();
  
  const response = await fetch(`${API_CONFIG.BASE_URL}${url}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
      ...options.headers,
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(errorData.detail || `API request failed: ${response.status} ${response.statusText}`);
  }

  const data = await response.json();
  return { data };
};

export const calendarApi = {
  // Get all calendar connections
  getConnections: () =>
    makeAuthenticatedRequest<CalendarConnection[]>('/api/calendar/accounts'),

  // Get specific calendar connection
  getConnection: (connectionId: number) =>
    makeAuthenticatedRequest<CalendarConnection>(`/api/calendar/accounts/${connectionId}`),

  // Update calendar connection settings
  updateConnection: (connectionId: number, updates: CalendarConnectionUpdate) =>
    makeAuthenticatedRequest<CalendarConnectionResponse>(`/api/calendar/accounts/${connectionId}`, {
      method: 'PUT',
      body: JSON.stringify(updates),
    }),

  // Delete calendar connection
  deleteConnection: (connectionId: number) =>
    makeAuthenticatedRequest<{ message: string }>(`/api/calendar/accounts/${connectionId}`, {
      method: 'DELETE',
    }),

  // Get Google Calendar OAuth URL
  getGoogleAuthUrl: () =>
    makeAuthenticatedRequest<CalendarAuthResponse>('/api/calendar/oauth/google/start'),

  // Handle Google Calendar OAuth callback
  handleGoogleCallback: (code: string, state?: string) =>
    makeAuthenticatedRequest<CalendarConnectionResponse>(`/api/calendar/oauth/google/callback?code=${code}&state=${state || ''}`),

  // Get Outlook Calendar OAuth URL
  getOutlookAuthUrl: () =>
    makeAuthenticatedRequest<CalendarAuthResponse>('/api/calendar/oauth/microsoft/start'),

  // Handle Outlook Calendar OAuth callback
  handleOutlookCallback: (code: string, state?: string) =>
    makeAuthenticatedRequest<CalendarConnectionResponse>(`/api/calendar/oauth/microsoft/callback?code=${code}&state=${state || ''}`),

  // Manually sync calendar
  syncCalendar: (connectionId: number) =>
    makeAuthenticatedRequest<{ message: string; result: any }>(`/api/calendar/accounts/${connectionId}/sync`, {
      method: 'POST',
    }),
};