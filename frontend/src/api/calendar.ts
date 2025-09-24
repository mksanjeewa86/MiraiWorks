import { API_ENDPOINTS } from './config';
import { apiClient, publicApiClient } from './apiClient';
import type { ApiResponse, CalendarEvent, CalendarEventInput, CalendarConnection } from '@/types';

// Helper to build query strings
const buildQueryString = (filters?: Record<string, string | undefined>): string => {
  if (!filters) return '';

  const params = new URLSearchParams();
  Object.entries(filters).forEach(([key, value]) => {
    if (value) {
      params.set(key, value);
    }
  });

  return params.toString();
};

export const calendarApi = {
  async getEvents(filters?: {
    startDate?: string;
    endDate?: string;
    type?: string;
  }): Promise<ApiResponse<CalendarEvent[]>> {
    const query = buildQueryString(filters);
    const url = query ? `${API_ENDPOINTS.CALENDAR.EVENTS}?${query}` : API_ENDPOINTS.CALENDAR.EVENTS;

    const response = await apiClient.get<CalendarEvent[]>(url);
    return { data: response.data, success: true };
  },

  async getEvent(id: number): Promise<ApiResponse<CalendarEvent>> {
    const response = await apiClient.get<CalendarEvent>(API_ENDPOINTS.CALENDAR.EVENT_BY_ID(id));
    return { data: response.data, success: true };
  },

  async createEvent(eventData: Partial<CalendarEvent>): Promise<ApiResponse<CalendarEvent>> {
    const response = await apiClient.post<CalendarEvent>(API_ENDPOINTS.CALENDAR.EVENTS, eventData);
    return { data: response.data, success: true };
  },

  async updateEvent(
    id: number,
    eventData: Partial<CalendarEvent>
  ): Promise<ApiResponse<CalendarEvent>> {
    const response = await apiClient.put<CalendarEvent>(
      API_ENDPOINTS.CALENDAR.EVENT_BY_ID(id),
      eventData
    );
    return { data: response.data, success: true };
  },

  async deleteEvent(id: number): Promise<ApiResponse<void>> {
    if (!Number.isFinite(id)) {
      throw new Error('Invalid calendar event identifier');
    }

    await apiClient.delete<void>(API_ENDPOINTS.CALENDAR.EVENT_BY_ID(id));
    return { data: undefined, success: true };
  },

  async getAvailability(
    userId: number,
    date: string
  ): Promise<
    ApiResponse<{
      date: string;
      availableSlots: Array<{
        startTime: string;
        endTime: string;
      }>;
    }>
  > {
    const query = `date=${date}`;
    const url = `${API_ENDPOINTS.CALENDAR.AVAILABILITY(userId)}?${query}`;

    const response = await apiClient.get<{
      date: string;
      availableSlots: Array<{
        startTime: string;
        endTime: string;
      }>;
    }>(url);
    return { data: response.data, success: true };
  },

  // Calendar connection methods for settings page
  async getConnections(): Promise<ApiResponse<CalendarConnection[]>> {
    const response = await apiClient.get<CalendarConnection[]>('/api/calendar/accounts');
    return { data: response.data, success: true };
  },

  async getGoogleAuthUrl(): Promise<ApiResponse<{ auth_url: string }>> {
    const response = await apiClient.get<{ auth_url: string }>('/api/calendar/oauth/google/start');
    return { data: response.data, success: true };
  },

  async getOutlookAuthUrl(): Promise<ApiResponse<{ auth_url: string }>> {
    const response = await apiClient.get<{ auth_url: string }>(
      '/api/calendar/oauth/microsoft/start'
    );
    return { data: response.data, success: true };
  },

  async deleteConnection(connectionId: number): Promise<ApiResponse<{ message: string }>> {
    const response = await apiClient.delete<{ message: string }>(
      `/api/calendar/accounts/${connectionId}`
    );
    return { data: response.data, success: true };
  },

  async syncCalendar(connectionId: number): Promise<ApiResponse<{ message: string }>> {
    const response = await apiClient.post<{ message: string }>(
      `/api/calendar/accounts/${connectionId}/sync`
    );
    return { data: response.data, success: true };
  },

  async updateConnection(
    connectionId: number,
    updates: Record<string, unknown>
  ): Promise<ApiResponse<CalendarConnection>> {
    const response = await apiClient.put<CalendarConnection>(
      `/api/calendar/accounts/${connectionId}`,
      updates
    );
    return { data: response.data, success: true };
  },
};

// Legacy function-based API for backward compatibility
export const createCalendarEvent = async (
  eventData: CalendarEventInput
): Promise<ApiResponse<CalendarEvent>> => {
  const response = await publicApiClient.post<CalendarEvent>(
    API_ENDPOINTS.CALENDAR.EVENTS,
    eventData
  );
  return { data: response.data, success: true };
};

export const getCalendarEvents = async (
  startDate?: string,
  endDate?: string
): Promise<ApiResponse<{ events: CalendarEvent[]; has_more: boolean }>> => {
  const filters = { startDate, endDate };
  const query = buildQueryString(filters);
  const url = query ? `${API_ENDPOINTS.CALENDAR.EVENTS}?${query}` : API_ENDPOINTS.CALENDAR.EVENTS;

  const response = await publicApiClient.get<{ events: CalendarEvent[]; has_more: boolean }>(url);
  return { data: response.data, success: true };
};

export const updateCalendarEvent = async (
  eventId: string,
  eventData: CalendarEventInput
): Promise<ApiResponse<CalendarEvent>> => {
  const response = await apiClient.put<CalendarEvent>(
    API_ENDPOINTS.CALENDAR.EVENT_BY_ID(eventId),
    eventData
  );
  return { data: response.data, success: true };
};

export const deleteCalendarEvent = async (
  eventId: string
): Promise<ApiResponse<{ message: string }>> => {
  const response = await apiClient.delete<{ message: string }>(
    API_ENDPOINTS.CALENDAR.EVENT_BY_ID(eventId)
  );
  return { data: response.data, success: true };
};
