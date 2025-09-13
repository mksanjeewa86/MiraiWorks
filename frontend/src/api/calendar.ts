import type { ApiResponse, CalendarEvent } from '@/types';
import { API_CONFIG } from '@/config/api';

// Calendar API
export const calendarApi = {
  getEvents: async (filters?: {
    startDate?: string;
    endDate?: string;
    type?: string;
  }): Promise<ApiResponse<CalendarEvent[]>> => {
    const token = localStorage.getItem('accessToken');
    const url = new URL(`${API_CONFIG.BASE_URL}/api/calendar/events`);
    
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value) {
          url.searchParams.set(key, value);
        }
      });
    }
    
    const response = await fetch(url.toString(), {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return { data, success: true };
  },

  getEvent: async (id: number): Promise<ApiResponse<CalendarEvent>> => {
    const token = localStorage.getItem('accessToken');
    const response = await fetch(`${API_CONFIG.BASE_URL}/api/calendar/events/${id}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return { data, success: true };
  },

  createEvent: async (eventData: Partial<CalendarEvent>): Promise<ApiResponse<CalendarEvent>> => {
    const token = localStorage.getItem('accessToken');
    const response = await fetch(`${API_CONFIG.BASE_URL}/api/calendar/events`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(eventData),
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return { data, success: true };
  },

  updateEvent: async (id: number, eventData: Partial<CalendarEvent>): Promise<ApiResponse<CalendarEvent>> => {
    const token = localStorage.getItem('accessToken');
    const response = await fetch(`${API_CONFIG.BASE_URL}/api/calendar/events/${id}`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(eventData),
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return { data, success: true };
  },

  deleteEvent: async (id: number): Promise<ApiResponse<void>> => {
    const token = localStorage.getItem('accessToken');
    const response = await fetch(`${API_CONFIG.BASE_URL}/api/calendar/events/${id}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }
    
    return { data: undefined, success: true };
  },

  getAvailability: async (userId: number, date: string): Promise<ApiResponse<{
    date: string;
    availableSlots: Array<{
      startTime: string;
      endTime: string;
    }>;
  }>> => {
    const token = localStorage.getItem('accessToken');
    const response = await fetch(`${API_CONFIG.BASE_URL}/api/calendar/availability/${userId}?date=${date}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return { data, success: true };
  },
};