/**
 * Tests for calendar API functions.
 */

import { jest } from '@jest/globals';
import { createCalendarEvent, getCalendarEvents, updateCalendarEvent, deleteCalendarEvent } from '../../api/calendar';
import type { CalendarEvent, CalendarEventInput } from '../../types';

// Mock fetch globally
global.fetch = jest.fn();
const mockFetch = fetch as jest.MockedFunction<typeof fetch>;

// Mock API_CONFIG
jest.mock('../../config/api', () => ({
  API_CONFIG: {
    BASE_URL: 'http://localhost:8000',
    TIMEOUT: 30000,
    RETRY_ATTEMPTS: 3,
  },
  buildApiUrl: (endpoint: string) => `http://localhost:8000${endpoint}`,
  API_ENDPOINTS: {
    CALENDAR: {
      BASE: '/api/calendar',
      EVENTS: '/api/calendar/events',
    },
  },
}));

describe('Calendar API', () => {
  const mockEvent: CalendarEvent = {
    id: 'test-event-id',
    title: 'Test Meeting',
    description: 'A test meeting',
    location: 'Conference Room A',
    startDatetime: '2025-01-15T09:00:00Z',
    endDatetime: '2025-01-15T10:00:00Z',
    timezone: 'UTC',
    isAllDay: false,
    isRecurring: false,
    organizerEmail: 'test@example.com',
    attendees: ['attendee@example.com'],
    status: 'confirmed',
    createdAt: '2025-01-15T08:00:00Z',
    updatedAt: '2025-01-15T08:00:00Z',
  };

  const mockEventInput: CalendarEventInput = {
    title: 'Test Meeting',
    description: 'A test meeting',
    location: 'Conference Room A',
    startDatetime: '2025-01-15T09:00:00Z',
    endDatetime: '2025-01-15T10:00:00Z',
    timezone: 'UTC',
    isAllDay: false,
    attendees: ['attendee@example.com'],
    status: 'confirmed',
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('createCalendarEvent', () => {
    it('should create event successfully', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 201,
        json: async () => mockEvent,
      } as Response);

      const result = await createCalendarEvent(mockEventInput);

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/calendar/events',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(mockEventInput),
        }
      );

      expect(result.data).toEqual(mockEvent);
    });

    it('should handle creation with minimal data', async () => {
      const minimalInput: CalendarEventInput = {
        title: 'Minimal Event',
        startDatetime: '2025-01-15T14:00:00Z',
        endDatetime: '2025-01-15T15:00:00Z',
      };

      const minimalEvent = {
        ...mockEvent,
        title: 'Minimal Event',
        description: null,
        location: null,
        attendees: [],
        startDatetime: '2025-01-15T14:00:00Z',
        endDatetime: '2025-01-15T15:00:00Z',
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 201,
        json: async () => minimalEvent,
      } as Response);

      const result = await createCalendarEvent(minimalInput);

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/calendar/events',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(minimalInput),
        }
      );

      expect(result.data).toEqual(minimalEvent);
    });

    it('should handle validation errors', async () => {
      const errorResponse = {
        detail: [
          {
            loc: ['title'],
            msg: 'field required',
            type: 'value_error.missing'
          }
        ]
      };

      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 422,
        json: async () => errorResponse,
      } as Response);

      await expect(createCalendarEvent({ ...mockEventInput, title: '' }))
        .rejects
        .toThrow();

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/calendar/events',
        expect.objectContaining({
          method: 'POST',
        })
      );
    });

    it('should handle network errors', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Network error'));

      await expect(createCalendarEvent(mockEventInput))
        .rejects
        .toThrow('Network error');
    });

    it('should handle server errors', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: async () => ({ error: 'Internal server error' }),
      } as Response);

      await expect(createCalendarEvent(mockEventInput))
        .rejects
        .toThrow();
    });

    it('should handle all-day events', async () => {
      const allDayInput: CalendarEventInput = {
        ...mockEventInput,
        isAllDay: true,
        startDatetime: '2025-01-15T00:00:00Z',
        endDatetime: '2025-01-15T23:59:59Z',
      };

      const allDayEvent = {
        ...mockEvent,
        isAllDay: true,
        startDatetime: '2025-01-15T00:00:00Z',
        endDatetime: '2025-01-15T23:59:59Z',
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 201,
        json: async () => allDayEvent,
      } as Response);

      const result = await createCalendarEvent(allDayInput);

      expect(result.data.isAllDay).toBe(true);
      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/calendar/events',
        expect.objectContaining({
          body: JSON.stringify(allDayInput),
        })
      );
    });

    it('should handle events with multiple attendees', async () => {
      const multiAttendeeInput: CalendarEventInput = {
        ...mockEventInput,
        attendees: ['alice@example.com', 'bob@example.com', 'charlie@example.com'],
      };

      const multiAttendeeEvent = {
        ...mockEvent,
        attendees: ['alice@example.com', 'bob@example.com', 'charlie@example.com'],
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 201,
        json: async () => multiAttendeeEvent,
      } as Response);

      const result = await createCalendarEvent(multiAttendeeInput);

      expect(result.data.attendees).toHaveLength(3);
      expect(result.data.attendees).toContain('alice@example.com');
    });
  });

  describe('getCalendarEvents', () => {
    it('should fetch events successfully', async () => {
      const eventsResponse = {
        events: [mockEvent],
        has_more: false,
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => eventsResponse,
      } as Response);

      const result = await getCalendarEvents();

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/calendar/events',
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );

      expect(result.data).toEqual(eventsResponse);
    });

    it('should fetch events with date range', async () => {
      const startDate = '2025-01-01';
      const endDate = '2025-01-31';
      const eventsResponse = {
        events: [mockEvent],
        has_more: false,
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => eventsResponse,
      } as Response);

      const result = await getCalendarEvents(startDate, endDate);

      expect(mockFetch).toHaveBeenCalledWith(
        `http://localhost:8000/api/calendar/events?startDate=${startDate}&endDate=${endDate}`,
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );

      expect(result.data).toEqual(eventsResponse);
    });

    it('should handle empty events response', async () => {
      const eventsResponse = {
        events: [],
        has_more: false,
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => eventsResponse,
      } as Response);

      const result = await getCalendarEvents();

      expect(result.data.events).toHaveLength(0);
      expect(result.data.has_more).toBe(false);
    });

    it('should handle fetch errors', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Network error'));

      await expect(getCalendarEvents())
        .rejects
        .toThrow('Network error');
    });
  });

  describe('updateCalendarEvent', () => {
    it('should update event successfully', async () => {
      const updatedEvent = {
        ...mockEvent,
        title: 'Updated Meeting',
        description: 'Updated description',
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => updatedEvent,
      } as Response);

      const updateInput = {
        ...mockEventInput,
        title: 'Updated Meeting',
        description: 'Updated description',
      };

      const result = await updateCalendarEvent(mockEvent.id, updateInput);

      expect(mockFetch).toHaveBeenCalledWith(
        `http://localhost:8000/api/calendar/events/${mockEvent.id}`,
        {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(updateInput),
        }
      );

      expect(result.data.title).toBe('Updated Meeting');
    });

    it('should handle update errors', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        json: async () => ({ error: 'Event not found' }),
      } as Response);

      await expect(updateCalendarEvent('non-existent-id', mockEventInput))
        .rejects
        .toThrow();
    });
  });

  describe('deleteCalendarEvent', () => {
    it('should delete event successfully', async () => {
      const deleteResponse = {
        message: 'Event deleted successfully',
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => deleteResponse,
      } as Response);

      const result = await deleteCalendarEvent(mockEvent.id);

      expect(mockFetch).toHaveBeenCalledWith(
        `http://localhost:8000/api/calendar/events/${mockEvent.id}`,
        {
          method: 'DELETE',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );

      expect(result.data.message).toBe('Event deleted successfully');
    });

    it('should handle delete errors', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        json: async () => ({ error: 'Event not found' }),
      } as Response);

      await expect(deleteCalendarEvent('non-existent-id'))
        .rejects
        .toThrow();
    });

    it('should handle network errors during delete', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Network error'));

      await expect(deleteCalendarEvent(mockEvent.id))
        .rejects
        .toThrow('Network error');
    });
  });

  describe('Error Response Handling', () => {
    it('should handle malformed JSON responses', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: async () => {
          throw new Error('Malformed JSON');
        },
      } as Response);

      await expect(createCalendarEvent(mockEventInput))
        .rejects
        .toThrow();
    });

    it('should handle timeout scenarios', async () => {
      // Simulate timeout
      mockFetch.mockImplementationOnce(() => {
        return new Promise((_, reject) => {
          setTimeout(() => reject(new Error('Request timeout')), 100);
        });
      });

      await expect(createCalendarEvent(mockEventInput))
        .rejects
        .toThrow('Request timeout');
    });

    it('should handle rate limiting', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 429,
        json: async () => ({ error: 'Rate limit exceeded' }),
      } as Response);

      await expect(createCalendarEvent(mockEventInput))
        .rejects
        .toThrow();
    });
  });

  describe('Data Validation', () => {
    it('should handle invalid date formats gracefully', async () => {
      const invalidDateInput: CalendarEventInput = {
        ...mockEventInput,
        startDatetime: 'invalid-date',
        endDatetime: 'invalid-date',
      };

      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 422,
        json: async () => ({
          detail: [
            {
              loc: ['startDatetime'],
              msg: 'invalid datetime format',
              type: 'value_error.datetime',
            },
          ],
        }),
      } as Response);

      await expect(createCalendarEvent(invalidDateInput))
        .rejects
        .toThrow();
    });

    it('should handle end time before start time', async () => {
      const invalidTimeInput: CalendarEventInput = {
        ...mockEventInput,
        startDatetime: '2025-01-15T10:00:00Z',
        endDatetime: '2025-01-15T09:00:00Z', // End before start
      };

      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 422,
        json: async () => ({
          detail: [
            {
              loc: ['endDatetime'],
              msg: 'end time must be after start time',
              type: 'value_error.datetime',
            },
          ],
        }),
      } as Response);

      await expect(createCalendarEvent(invalidTimeInput))
        .rejects
        .toThrow();
    });
  });
});