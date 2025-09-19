/**
 * Comprehensive tests for calendar event creation functionality.
 */

import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { jest } from '@jest/globals';
import '@testing-library/jest-dom';

import CalendarPage from '../../app/calendar/page';
import { createCalendarEvent, getCalendarEvents } from '../../api/calendar';

// Mock the API functions
jest.mock('../../api/calendar', () => ({
  createCalendarEvent: jest.fn(),
  getCalendarEvents: jest.fn(),
}));

const mockCreateCalendarEvent = createCalendarEvent as jest.MockedFunction<typeof createCalendarEvent>;
const mockGetCalendarEvents = getCalendarEvents as jest.MockedFunction<typeof getCalendarEvents>;

// Mock the next/navigation module
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
    replace: jest.fn(),
    back: jest.fn(),
  }),
  useSearchParams: () => ({
    get: jest.fn(),
  }),
}));

// Mock date to ensure consistent testing
const mockDate = new Date('2025-01-15T10:00:00Z');
jest.useFakeTimers();
jest.setSystemTime(mockDate);

describe('Calendar Event Creation', () => {
  const mockEvent = {
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

  beforeEach(() => {
    jest.clearAllMocks();
    mockGetCalendarEvents.mockResolvedValue({
      data: { events: [], has_more: false }
    });
  });

  afterEach(() => {
    jest.runOnlyPendingTimers();
    jest.useRealTimers();
  });

  describe('Event Creation Modal', () => {
    it('should open event creation modal when clicking on a date', async () => {
      const user = userEvent.setup({ advanceTimers: jest.advanceTimersByTime });

      render(<CalendarPage />);

      await waitFor(() => {
        expect(screen.queryByText('Loading calendar...')).not.toBeInTheDocument();
      });

      // Find and click a date cell to create an event
      const dateCell = screen.getByText('15');
      await user.click(dateCell);

      // Modal should open
      await waitFor(() => {
        expect(screen.getByText('Create Event')).toBeInTheDocument();
      });
    });

    it('should close modal when clicking cancel', async () => {
      const user = userEvent.setup({ advanceTimers: jest.advanceTimersByTime });

      render(<CalendarPage />);

      await waitFor(() => {
        expect(screen.queryByText('Loading calendar...')).not.toBeInTheDocument();
      });

      // Open modal
      const dateCell = screen.getByText('15');
      await user.click(dateCell);

      await waitFor(() => {
        expect(screen.getByText('Create Event')).toBeInTheDocument();
      });

      // Click cancel
      const cancelButton = screen.getByRole('button', { name: /cancel/i });
      await user.click(cancelButton);

      // Modal should close
      await waitFor(() => {
        expect(screen.queryByText('Create Event')).not.toBeInTheDocument();
      });
    });
  });

  describe('Event Creation Form Validation', () => {
    it('should show validation error for empty title', async () => {
      const user = userEvent.setup({ advanceTimers: jest.advanceTimersByTime });

      render(<CalendarPage />);

      await waitFor(() => {
        expect(screen.queryByText('Loading calendar...')).not.toBeInTheDocument();
      });

      // Open modal
      const dateCell = screen.getByText('15');
      await user.click(dateCell);

      await waitFor(() => {
        expect(screen.getByText('Create Event')).toBeInTheDocument();
      });

      // Try to save without title
      const saveButton = screen.getByRole('button', { name: /save/i });
      await user.click(saveButton);

      // Should show validation error
      await waitFor(() => {
        expect(screen.getByText(/title is required/i)).toBeInTheDocument();
      });
    });

    it('should show validation error for invalid end time', async () => {
      const user = userEvent.setup({ advanceTimers: jest.advanceTimersByTime });

      render(<CalendarPage />);

      await waitFor(() => {
        expect(screen.queryByText('Loading calendar...')).not.toBeInTheDocument();
      });

      // Open modal
      const dateCell = screen.getByText('15');
      await user.click(dateCell);

      await waitFor(() => {
        expect(screen.getByText('Create Event')).toBeInTheDocument();
      });

      // Fill title
      const titleInput = screen.getByLabelText(/title/i);
      await user.type(titleInput, 'Test Event');

      // Set end time before start time
      const startTimeInput = screen.getByLabelText(/start time/i);
      const endTimeInput = screen.getByLabelText(/end time/i);

      await user.clear(startTimeInput);
      await user.type(startTimeInput, '10:00');

      await user.clear(endTimeInput);
      await user.type(endTimeInput, '09:00');

      // Try to save
      const saveButton = screen.getByRole('button', { name: /save/i });
      await user.click(saveButton);

      // Should show validation error
      await waitFor(() => {
        expect(screen.getByText(/end time must be after start time/i)).toBeInTheDocument();
      });
    });
  });

  describe('Successful Event Creation', () => {
    it('should create event successfully with valid data', async () => {
      const user = userEvent.setup({ advanceTimers: jest.advanceTimersByTime });

      mockCreateCalendarEvent.mockResolvedValue({
        data: mockEvent
      });

      render(<CalendarPage />);

      await waitFor(() => {
        expect(screen.queryByText('Loading calendar...')).not.toBeInTheDocument();
      });

      // Open modal
      const dateCell = screen.getByText('15');
      await user.click(dateCell);

      await waitFor(() => {
        expect(screen.getByText('Create Event')).toBeInTheDocument();
      });

      // Fill form
      const titleInput = screen.getByLabelText(/title/i);
      await user.type(titleInput, 'Test Meeting');

      const descriptionInput = screen.getByLabelText(/description/i);
      await user.type(descriptionInput, 'A test meeting');

      const locationInput = screen.getByLabelText(/location/i);
      await user.type(locationInput, 'Conference Room A');

      // Save event
      const saveButton = screen.getByRole('button', { name: /save/i });
      await user.click(saveButton);

      // Should call API
      await waitFor(() => {
        expect(mockCreateCalendarEvent).toHaveBeenCalledWith(
          expect.objectContaining({
            title: 'Test Meeting',
            description: 'A test meeting',
            location: 'Conference Room A',
          })
        );
      });

      // Modal should close
      await waitFor(() => {
        expect(screen.queryByText('Create Event')).not.toBeInTheDocument();
      });
    });

    it('should create all-day event when all-day toggle is enabled', async () => {
      const user = userEvent.setup({ advanceTimers: jest.advanceTimersByTime });

      mockCreateCalendarEvent.mockResolvedValue({
        data: { ...mockEvent, isAllDay: true }
      });

      render(<CalendarPage />);

      await waitFor(() => {
        expect(screen.queryByText('Loading calendar...')).not.toBeInTheDocument();
      });

      // Open modal
      const dateCell = screen.getByText('15');
      await user.click(dateCell);

      await waitFor(() => {
        expect(screen.getByText('Create Event')).toBeInTheDocument();
      });

      // Fill title
      const titleInput = screen.getByLabelText(/title/i);
      await user.type(titleInput, 'All Day Event');

      // Enable all-day
      const allDayToggle = screen.getByLabelText(/all day/i);
      await user.click(allDayToggle);

      // Save event
      const saveButton = screen.getByRole('button', { name: /save/i });
      await user.click(saveButton);

      // Should call API with isAllDay: true
      await waitFor(() => {
        expect(mockCreateCalendarEvent).toHaveBeenCalledWith(
          expect.objectContaining({
            title: 'All Day Event',
            isAllDay: true,
          })
        );
      });
    });

    it('should handle event creation with attendees', async () => {
      const user = userEvent.setup({ advanceTimers: jest.advanceTimersByTime });

      mockCreateCalendarEvent.mockResolvedValue({
        data: mockEvent
      });

      render(<CalendarPage />);

      await waitFor(() => {
        expect(screen.queryByText('Loading calendar...')).not.toBeInTheDocument();
      });

      // Open modal
      const dateCell = screen.getByText('15');
      await user.click(dateCell);

      await waitFor(() => {
        expect(screen.getByText('Create Event')).toBeInTheDocument();
      });

      // Fill title
      const titleInput = screen.getByLabelText(/title/i);
      await user.type(titleInput, 'Team Meeting');

      // Add attendees
      const attendeesInput = screen.getByLabelText(/attendees/i);
      await user.type(attendeesInput, 'alice@example.com, bob@example.com');

      // Save event
      const saveButton = screen.getByRole('button', { name: /save/i });
      await user.click(saveButton);

      // Should call API with attendees
      await waitFor(() => {
        expect(mockCreateCalendarEvent).toHaveBeenCalledWith(
          expect.objectContaining({
            title: 'Team Meeting',
            attendees: expect.arrayContaining(['alice@example.com', 'bob@example.com']),
          })
        );
      });
    });
  });

  describe('Error Handling', () => {
    it('should show error message when API call fails', async () => {
      const user = userEvent.setup({ advanceTimers: jest.advanceTimersByTime });

      mockCreateCalendarEvent.mockRejectedValue(new Error('API Error'));

      render(<CalendarPage />);

      await waitFor(() => {
        expect(screen.queryByText('Loading calendar...')).not.toBeInTheDocument();
      });

      // Open modal
      const dateCell = screen.getByText('15');
      await user.click(dateCell);

      await waitFor(() => {
        expect(screen.getByText('Create Event')).toBeInTheDocument();
      });

      // Fill title
      const titleInput = screen.getByLabelText(/title/i);
      await user.type(titleInput, 'Test Event');

      // Save event
      const saveButton = screen.getByRole('button', { name: /save/i });
      await user.click(saveButton);

      // Should show error message
      await waitFor(() => {
        expect(screen.getByText(/failed to create event/i)).toBeInTheDocument();
      });

      // Modal should remain open
      expect(screen.getByText('Create Event')).toBeInTheDocument();
    });

    it('should handle network timeout errors', async () => {
      const user = userEvent.setup({ advanceTimers: jest.advanceTimersByTime });

      mockCreateCalendarEvent.mockRejectedValue(new Error('Network timeout'));

      render(<CalendarPage />);

      await waitFor(() => {
        expect(screen.queryByText('Loading calendar...')).not.toBeInTheDocument();
      });

      // Open modal
      const dateCell = screen.getByText('15');
      await user.click(dateCell);

      await waitFor(() => {
        expect(screen.getByText('Create Event')).toBeInTheDocument();
      });

      // Fill title
      const titleInput = screen.getByLabelText(/title/i);
      await user.type(titleInput, 'Test Event');

      // Save event
      const saveButton = screen.getByRole('button', { name: /save/i });
      await user.click(saveButton);

      // Should show network error
      await waitFor(() => {
        expect(screen.getByText(/network error/i)).toBeInTheDocument();
      });
    });

    it('should handle validation errors from server', async () => {
      const user = userEvent.setup({ advanceTimers: jest.advanceTimersByTime });

      mockCreateCalendarEvent.mockRejectedValue({
        response: {
          status: 422,
          data: {
            detail: [
              { loc: ['title'], msg: 'Title is required', type: 'value_error' }
            ]
          }
        }
      });

      render(<CalendarPage />);

      await waitFor(() => {
        expect(screen.queryByText('Loading calendar...')).not.toBeInTheDocument();
      });

      // Open modal
      const dateCell = screen.getByText('15');
      await user.click(dateCell);

      await waitFor(() => {
        expect(screen.getByText('Create Event')).toBeInTheDocument();
      });

      // Try to save without title
      const saveButton = screen.getByRole('button', { name: /save/i });
      await user.click(saveButton);

      // Should show server validation error
      await waitFor(() => {
        expect(screen.getByText(/title is required/i)).toBeInTheDocument();
      });
    });
  });

  describe('Event Loading and Display', () => {
    it('should load and display existing events', async () => {
      mockGetCalendarEvents.mockResolvedValue({
        data: {
          events: [mockEvent],
          has_more: false
        }
      });

      render(<CalendarPage />);

      // Should load events
      await waitFor(() => {
        expect(mockGetCalendarEvents).toHaveBeenCalled();
      });

      // Should display event
      await waitFor(() => {
        expect(screen.getByText('Test Meeting')).toBeInTheDocument();
      });
    });

    it('should refresh events after creating new event', async () => {
      const user = userEvent.setup({ advanceTimers: jest.advanceTimersByTime });

      // Initial load returns no events
      mockGetCalendarEvents
        .mockResolvedValueOnce({
          data: { events: [], has_more: false }
        })
        // After creating event, return the new event
        .mockResolvedValueOnce({
          data: { events: [mockEvent], has_more: false }
        });

      mockCreateCalendarEvent.mockResolvedValue({
        data: mockEvent
      });

      render(<CalendarPage />);

      await waitFor(() => {
        expect(screen.queryByText('Loading calendar...')).not.toBeInTheDocument();
      });

      // Open modal and create event
      const dateCell = screen.getByText('15');
      await user.click(dateCell);

      await waitFor(() => {
        expect(screen.getByText('Create Event')).toBeInTheDocument();
      });

      const titleInput = screen.getByLabelText(/title/i);
      await user.type(titleInput, 'Test Meeting');

      const saveButton = screen.getByRole('button', { name: /save/i });
      await user.click(saveButton);

      // Should refresh events
      await waitFor(() => {
        expect(mockGetCalendarEvents).toHaveBeenCalledTimes(2);
      });

      // Should display new event
      await waitFor(() => {
        expect(screen.getByText('Test Meeting')).toBeInTheDocument();
      });
    });
  });

  describe('Date and Time Handling', () => {
    it('should handle different timezones correctly', async () => {
      const user = userEvent.setup({ advanceTimers: jest.advanceTimersByTime });

      mockCreateCalendarEvent.mockResolvedValue({
        data: { ...mockEvent, timezone: 'America/New_York' }
      });

      render(<CalendarPage />);

      await waitFor(() => {
        expect(screen.queryByText('Loading calendar...')).not.toBeInTheDocument();
      });

      // Open modal
      const dateCell = screen.getByText('15');
      await user.click(dateCell);

      await waitFor(() => {
        expect(screen.getByText('Create Event')).toBeInTheDocument();
      });

      // Fill title
      const titleInput = screen.getByLabelText(/title/i);
      await user.type(titleInput, 'Timezone Event');

      // Change timezone if timezone selector exists
      const timezoneSelect = screen.queryByLabelText(/timezone/i);
      if (timezoneSelect) {
        await user.selectOptions(timezoneSelect, 'America/New_York');
      }

      // Save event
      const saveButton = screen.getByRole('button', { name: /save/i });
      await user.click(saveButton);

      // Should handle timezone correctly
      await waitFor(() => {
        expect(mockCreateCalendarEvent).toHaveBeenCalledWith(
          expect.objectContaining({
            title: 'Timezone Event',
            timezone: expect.any(String),
          })
        );
      });
    });

    it('should handle recurring events if supported', async () => {
      const user = userEvent.setup({ advanceTimers: jest.advanceTimersByTime });

      mockCreateCalendarEvent.mockResolvedValue({
        data: { ...mockEvent, isRecurring: true }
      });

      render(<CalendarPage />);

      await waitFor(() => {
        expect(screen.queryByText('Loading calendar...')).not.toBeInTheDocument();
      });

      // Open modal
      const dateCell = screen.getByText('15');
      await user.click(dateCell);

      await waitFor(() => {
        expect(screen.getByText('Create Event')).toBeInTheDocument();
      });

      // Fill title
      const titleInput = screen.getByLabelText(/title/i);
      await user.type(titleInput, 'Recurring Event');

      // Enable recurring if option exists
      const recurringToggle = screen.queryByLabelText(/recurring/i);
      if (recurringToggle) {
        await user.click(recurringToggle);
      }

      // Save event
      const saveButton = screen.getByRole('button', { name: /save/i });
      await user.click(saveButton);

      await waitFor(() => {
        expect(mockCreateCalendarEvent).toHaveBeenCalled();
      });
    });
  });
});