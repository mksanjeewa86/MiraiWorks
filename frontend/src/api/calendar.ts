import { API_ENDPOINTS } from './config';
import { apiClient, publicApiClient } from './apiClient';
import type {
  ApiResponse,
  CalendarEventInput,
  CalendarConnection,
  CalendarEventCreate,
  CalendarEventUpdate,
  CalendarEventInfo,
  CalendarEventListResponse,
  CalendarEventQueryParams,
  CalendarEventBulkCreate,
  CalendarEventBulkResponse,
  ConsolidatedCalendarData,
} from '@/types';
import type { CalendarEvent } from '@/types/interview';

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
    // Transform the data from old format to new format
    const transformedData: CalendarEventCreate = {
      title: eventData.title || '',
      description: eventData.description || undefined,
      start_datetime: eventData.startDatetime || '',
      end_datetime: eventData.endDatetime || undefined,
      is_all_day: eventData.isAllDay || false,
      location: eventData.location || undefined,
      timezone: eventData.timezone || 'UTC',
    };

    const response = await apiClient.post<CalendarEventInfo>(
      API_ENDPOINTS.CALENDAR.EVENTS,
      transformedData
    );

    // Transform the response back to the old format for compatibility
    const transformedResponse: CalendarEvent = {
      id: response.data.id.toString(),
      title: response.data.title,
      description: response.data.description || '',
      location: response.data.location || '',
      startDatetime: response.data.start_datetime,
      endDatetime: response.data.end_datetime || '',
      timezone: response.data.timezone || 'UTC',
      isAllDay: response.data.is_all_day || false,
      isRecurring: response.data.is_recurring || false,
      organizerEmail: response.data.creator_id?.toString(),
      attendees: [],
      status: response.data.status || 'confirmed',
      createdAt: response.data.created_at,
      updatedAt: response.data.updated_at,
    };

    return { data: transformedResponse, success: true };
  },

  async updateEvent(
    id: number,
    eventData: Partial<CalendarEvent>
  ): Promise<ApiResponse<CalendarEvent>> {
    // Transform the data from old format to new format
    const transformedData: CalendarEventUpdate = {
      title: eventData.title,
      description: eventData.description,
      start_datetime: eventData.startDatetime,
      end_datetime: eventData.endDatetime,
      is_all_day: eventData.isAllDay,
      location: eventData.location,
      timezone: eventData.timezone,
    };

    const response = await apiClient.put<CalendarEventInfo>(
      API_ENDPOINTS.CALENDAR.EVENT_BY_ID(id),
      transformedData
    );

    // Transform the response back to the old format for compatibility
    const transformedResponse: CalendarEvent = {
      id: response.data.id.toString(),
      title: response.data.title,
      description: response.data.description || '',
      location: response.data.location || '',
      startDatetime: response.data.start_datetime,
      endDatetime: response.data.end_datetime || '',
      timezone: response.data.timezone || 'UTC',
      isAllDay: response.data.is_all_day || false,
      isRecurring: response.data.is_recurring || false,
      organizerEmail: response.data.creator_id?.toString(),
      attendees: [],
      status: response.data.status || 'confirmed',
      createdAt: response.data.created_at,
      updatedAt: response.data.updated_at,
    };

    return { data: transformedResponse, success: true };
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
    const response = await apiClient.get<CalendarConnection[]>(
      API_ENDPOINTS.CALENDAR.ACCOUNTS.BASE
    );
    return { data: response.data, success: true };
  },

  async getGoogleAuthUrl(): Promise<ApiResponse<{ auth_url: string }>> {
    const response = await apiClient.get<{ auth_url: string }>(
      API_ENDPOINTS.CALENDAR_OAUTH.GOOGLE_START
    );
    return { data: response.data, success: true };
  },

  async getOutlookAuthUrl(): Promise<ApiResponse<{ auth_url: string }>> {
    const response = await apiClient.get<{ auth_url: string }>(
      API_ENDPOINTS.CALENDAR_OAUTH.MICROSOFT_START
    );
    return { data: response.data, success: true };
  },

  async deleteConnection(connectionId: number): Promise<ApiResponse<{ message: string }>> {
    const response = await apiClient.delete<{ message: string }>(
      API_ENDPOINTS.CALENDAR.ACCOUNTS.BY_ID(connectionId)
    );
    return { data: response.data, success: true };
  },

  async syncCalendar(connectionId: number): Promise<ApiResponse<{ message: string }>> {
    const response = await apiClient.post<{ message: string }>(
      API_ENDPOINTS.CALENDAR.ACCOUNTS.SYNC(connectionId)
    );
    return { data: response.data, success: true };
  },

  async updateConnection(
    connectionId: number,
    updates: Record<string, unknown>
  ): Promise<ApiResponse<CalendarConnection>> {
    const response = await apiClient.put<CalendarConnection>(
      API_ENDPOINTS.CALENDAR.ACCOUNTS.BY_ID(connectionId),
      updates
    );
    return { data: response.data, success: true };
  },

  // ==================== INTERNAL CALENDAR EVENTS ====================

  async createInternalEvent(
    eventData: CalendarEventCreate
  ): Promise<ApiResponse<CalendarEventInfo>> {
    const response = await apiClient.post<CalendarEventInfo>(
      API_ENDPOINTS.CALENDAR.EVENTS,
      eventData
    );
    return { data: response.data, success: true };
  },

  async getInternalEvent(eventId: number): Promise<ApiResponse<CalendarEventInfo>> {
    const response = await apiClient.get<CalendarEventInfo>(
      API_ENDPOINTS.CALENDAR.EVENT_BY_ID(eventId)
    );
    return { data: response.data, success: true };
  },

  async updateInternalEvent(
    eventId: number,
    eventData: CalendarEventUpdate
  ): Promise<ApiResponse<CalendarEventInfo>> {
    const response = await apiClient.put<CalendarEventInfo>(
      API_ENDPOINTS.CALENDAR.EVENT_BY_ID(eventId),
      eventData
    );
    return { data: response.data, success: true };
  },

  async deleteInternalEvent(eventId: number): Promise<ApiResponse<{ message: string }>> {
    const response = await apiClient.delete<{ message: string }>(
      API_ENDPOINTS.CALENDAR.EVENT_BY_ID(eventId)
    );
    return { data: response.data, success: true };
  },

  async getEventsInRange(
    params: CalendarEventQueryParams
  ): Promise<ApiResponse<CalendarEventListResponse>> {
    const queryParams = new URLSearchParams();

    if (params.start_date) queryParams.set('start_date', params.start_date);
    if (params.end_date) queryParams.set('end_date', params.end_date);
    if (params.event_type) queryParams.set('event_type', params.event_type);
    if (params.status) queryParams.set('status', params.status);

    const response = await apiClient.get<CalendarEventListResponse>(
      `${API_ENDPOINTS.CALENDAR.RANGE}?${queryParams.toString()}`
    );
    return { data: response.data, success: true };
  },

  async getUpcomingEvents(limit: number = 10): Promise<ApiResponse<CalendarEventInfo[]>> {
    const response = await apiClient.get<CalendarEventInfo[]>(
      `${API_ENDPOINTS.CALENDAR.UPCOMING}?limit=${limit}`
    );
    return { data: response.data, success: true };
  },

  async bulkCreateEvents(
    bulkData: CalendarEventBulkCreate
  ): Promise<ApiResponse<CalendarEventBulkResponse>> {
    const response = await apiClient.post<CalendarEventBulkResponse>(
      API_ENDPOINTS.CALENDAR_EVENTS_BULK,
      bulkData
    );
    return { data: response.data, success: true };
  },

  async searchEvents(
    query: string,
    skip: number = 0,
    limit: number = 50
  ): Promise<ApiResponse<{ events: CalendarEventInfo[]; total: number }>> {
    const params = new URLSearchParams({
      q: query,
      skip: skip.toString(),
      limit: limit.toString(),
    });

    const response = await apiClient.get<{ events: CalendarEventInfo[]; total: number }>(
      `${API_ENDPOINTS.CALENDAR.SEARCH}?${params.toString()}`
    );
    return { data: response.data, success: true };
  },

  async getConsolidatedCalendar(
    startDate: string,
    endDate: string
  ): Promise<ApiResponse<ConsolidatedCalendarData>> {
    const params = new URLSearchParams({
      startDate,
      endDate,
    });

    const response = await apiClient.get<ConsolidatedCalendarData>(
      `${API_ENDPOINTS.CALENDAR.CONSOLIDATED}?${params.toString()}`
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
