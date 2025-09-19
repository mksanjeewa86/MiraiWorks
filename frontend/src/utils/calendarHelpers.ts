import type { Interview, CalendarEvent } from '@/types/interview';
import type { Todo } from '@/types/todo';

/**
 * Safely parses a date string and returns a valid Date or null
 */
const safeParseDate = (dateString: string | null | undefined): Date | null => {
  if (!dateString) return null;
  const date = new Date(dateString);
  return isNaN(date.getTime()) ? null : date;
};

/**
 * Formats a date to ISO string safely
 */
const safeDateToISOString = (date: Date | null): string => {
  return date ? date.toISOString() : '';
};

/**
 * Converts an interview to a calendar event
 */
export const interviewToCalendarEvent = (interview: Interview): CalendarEvent => {
  const getEventTitle = () => {
    switch (interview.status) {
      case 'scheduled':
        return `Interview: ${interview.position_title || interview.title}`;
      case 'confirmed':
        return `✓ Interview: ${interview.position_title || interview.title}`;
      case 'cancelled':
        return `✗ Cancelled: ${interview.position_title || interview.title}`;
      default:
        return `Interview: ${interview.position_title || interview.title}`;
    }
  };

  const getEventStatus = () => {
    switch (interview.status) {
      case 'confirmed':
        return 'confirmed';
      case 'cancelled':
        return 'cancelled';
      default:
        return 'tentative';
    }
  };

  const getEventDescription = () => {
    const parts = [];

    if (interview.description) {
      parts.push(interview.description);
    }

    if (interview.candidate_name) {
      parts.push(`Candidate: ${interview.candidate_name}`);
    }

    if (interview.company_name) {
      parts.push(`Company: ${interview.company_name}`);
    }

    if (interview.interview_type) {
      parts.push(`Type: ${interview.interview_type}`);
    }

    if (interview.preparation_notes) {
      parts.push(`Preparation: ${interview.preparation_notes}`);
    }

    return parts.join('\n');
  };

  const getAttendees = () => {
    const attendees = [];

    if (interview.candidate?.email) {
      attendees.push(interview.candidate.email);
    }

    if (interview.recruiter?.email) {
      attendees.push(interview.recruiter.email);
    }

    return attendees;
  };

  const startDate = safeParseDate(interview.scheduled_start || interview.scheduled_at);
  const endDate = safeParseDate(interview.scheduled_end);

  // Calculate end date if not provided
  const calculatedEndDate = !endDate && startDate
    ? new Date(startDate.getTime() + (interview.duration_minutes || 60) * 60000)
    : endDate;

  return {
    id: `interview-${interview.id}`,
    title: getEventTitle(),
    description: getEventDescription(),
    location: interview.location || interview.meeting_url || '',
    startDatetime: safeDateToISOString(startDate),
    endDatetime: safeDateToISOString(calculatedEndDate),
    timezone: interview.timezone || 'UTC',
    isAllDay: false,
    isRecurring: false,
    organizerEmail: interview.recruiter?.email,
    attendees: getAttendees(),
    status: getEventStatus(),
    createdAt: interview.created_at,
    updatedAt: interview.updated_at,
  };
};

/**
 * Converts a todo to a calendar event
 */
export const todoToCalendarEvent = (todo: Todo): CalendarEvent => {
  const getEventTitle = () => {
    const statusIcon = {
      pending: '📋',
      in_progress: '🔄',
      completed: '✅',
      expired: '⏰'
    }[todo.status] || '📋';

    const priorityText = todo.priority ? ` [${todo.priority}]` : '';
    return `${statusIcon} ${todo.title}${priorityText}`;
  };

  const getEventStatus = (): 'confirmed' | 'tentative' | 'cancelled' => {
    switch (todo.status) {
      case 'completed':
        return 'confirmed';
      case 'expired':
        return 'cancelled';
      case 'in_progress':
      case 'pending':
      default:
        return 'tentative';
    }
  };

  const getEventType = () => {
    if (todo.status === 'expired') return 'expired-todo';
    if (todo.status === 'completed') return 'completed-todo';
    return 'todo';
  };

  // For todos, we'll create an all-day event on the due date
  const dueDate = safeParseDate(todo.due_date);
  if (!dueDate) {
    // If due date is invalid, return a placeholder event
    return {
      id: `todo-${todo.id}`,
      title: `❌ Invalid date: ${getEventTitle()}`,
      description: todo.description || undefined,
      startDatetime: '',
      endDatetime: '',
      isAllDay: true,
      isRecurring: false,
      location: undefined,
      meetingUrl: undefined,
      type: 'invalid-todo',
      organizerName: undefined,
      organizerEmail: undefined,
      attendees: [],
      status: 'cancelled' as const,
      createdAt: todo.created_at,
      updatedAt: todo.updated_at,
    };
  }

  const startDateTime = new Date(dueDate.getFullYear(), dueDate.getMonth(), dueDate.getDate());
  const endDateTime = new Date(startDateTime.getTime() + 24 * 60 * 60 * 1000); // Next day

  return {
    id: `todo-${todo.id}`,
    title: getEventTitle(),
    description: todo.description || undefined,
    startDatetime: startDateTime.toISOString(),
    endDatetime: endDateTime.toISOString(),
    isAllDay: true,
    isRecurring: false,
    location: undefined,
    meetingUrl: undefined,
    type: getEventType(),
    organizerName: undefined,
    organizerEmail: undefined,
    attendees: [],
    status: getEventStatus(),
    createdAt: todo.created_at,
    updatedAt: todo.updated_at,
  };
};

/**
 * Merges calendar events, interviews, and todos into a single event list
 */
export const mergeCalendarAndInterviews = (
  calendarEvents: CalendarEvent[],
  interviews: Interview[],
  todos?: Todo[]
): CalendarEvent[] => {
  // Ensure inputs are arrays
  const safeCalendarEvents = Array.isArray(calendarEvents) ? calendarEvents : [];
  const safeInterviews = Array.isArray(interviews) ? interviews : [];
  const safeTodos = Array.isArray(todos) ? todos : [];

  const interviewEvents = safeInterviews
    .filter(interview => interview.scheduled_start || interview.scheduled_at)
    .map(interviewToCalendarEvent);

  const todoEvents = safeTodos
    .filter(todo => todo.due_date) // Only show todos with due dates
    .map(todoToCalendarEvent);

  return [...safeCalendarEvents, ...interviewEvents, ...todoEvents];
};

/**
 * Filters events based on search criteria and filters
 */
export const filterEvents = (
  events: CalendarEvent[],
  filters: {
    eventType: string;
    status: string;
    search: string;
  }
): CalendarEvent[] => {
  return events.filter(event => {
    // Search filter
    const matchesSearch = filters.search === '' ||
      event.title.toLowerCase().includes(filters.search.toLowerCase()) ||
      event.description?.toLowerCase().includes(filters.search.toLowerCase()) ||
      event.location?.toLowerCase().includes(filters.search.toLowerCase());

    // Status filter
    const matchesStatus = filters.status === 'all' || event.status === filters.status;

    // Event type filter
    let matchesType = true;
    if (filters.eventType !== 'all') {
      switch (filters.eventType) {
        case 'interview':
          matchesType = event.id.toString().startsWith('interview-') ||
                       event.title.toLowerCase().includes('interview');
          break;
        case 'meeting':
          matchesType = event.title.toLowerCase().includes('meeting');
          break;
        case 'call':
          matchesType = event.title.toLowerCase().includes('call') ||
                       event.title.toLowerCase().includes('phone');
          break;
        case 'personal':
          matchesType = !event.id.toString().startsWith('interview-') &&
                       !event.title.toLowerCase().includes('interview') &&
                       !event.title.toLowerCase().includes('meeting');
          break;
        case 'screening':
          matchesType = event.title.toLowerCase().includes('screening');
          break;
        case 'onboarding':
          matchesType = event.title.toLowerCase().includes('onboarding');
          break;
      }
    }

    return matchesSearch && matchesStatus && matchesType;
  });
};

/**
 * Groups events by date for display
 */
export const groupEventsByDate = (events: CalendarEvent[]): Record<string, CalendarEvent[]> => {
  return events.reduce((groups, event) => {
    const eventDate = safeParseDate(event.startDatetime);
    if (!eventDate) return groups; // Skip events with invalid dates

    const dateString = eventDate.toDateString();
    if (!groups[dateString]) {
      groups[dateString] = [];
    }
    groups[dateString].push(event);
    return groups;
  }, {} as Record<string, CalendarEvent[]>);
};

/**
 * Gets available time slots for scheduling
 */
export const getAvailableTimeSlots = (
  events: CalendarEvent[],
  date: Date,
  duration: number = 60
): Array<{ startTime: string; endTime: string }> => {
  const dayEvents = events.filter(event => {
    const eventDate = safeParseDate(event.startDatetime);
    return eventDate && eventDate.toDateString() === date.toDateString() && !event.isAllDay;
  });

  // Sort events by start time (safely)
  dayEvents.sort((a, b) => {
    const dateA = safeParseDate(a.startDatetime);
    const dateB = safeParseDate(b.startDatetime);
    if (!dateA || !dateB) return 0;
    return dateA.getTime() - dateB.getTime();
  });

  const slots = [];
  const workingHours = {
    start: 9, // 9 AM
    end: 17    // 5 PM
  };

  // Generate potential slots
  for (let hour = workingHours.start; hour < workingHours.end; hour++) {
    for (let minute = 0; minute < 60; minute += 30) {
      const slotStart = new Date(date);
      slotStart.setHours(hour, minute, 0, 0);

      const slotEnd = new Date(slotStart.getTime() + duration * 60000);

      // Check if this slot conflicts with any existing events
      const hasConflict = dayEvents.some(event => {
        const eventStart = safeParseDate(event.startDatetime);
        const eventEnd = safeParseDate(event.endDatetime);

        if (!eventStart || !eventEnd) return false;
        return (slotStart < eventEnd && slotEnd > eventStart);
      });

      if (!hasConflict && slotEnd.getHours() <= workingHours.end) {
        slots.push({
          startTime: slotStart.toISOString(),
          endTime: slotEnd.toISOString()
        });
      }
    }
  }

  return slots;
};

/**
 * Formats time for display
 */
export const formatEventTime = (startTime: string, endTime: string, isAllDay: boolean): string => {
  if (isAllDay) {
    return 'All day';
  }

  const start = safeParseDate(startTime);
  const end = safeParseDate(endTime);

  if (!start || !end) {
    return 'Invalid time';
  }

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    });
  };

  return `${formatTime(start)} - ${formatTime(end)}`;
};

/**
 * Gets the color scheme for an event based on its type and status
 */
export const getEventColorScheme = (event: CalendarEvent): string => {
  // Interview events
  if (event.id.toString().startsWith('interview-') || event.title.toLowerCase().includes('interview')) {
    if (event.status === 'cancelled') return 'bg-red-100 text-red-700 border-red-200';
    if (event.status === 'confirmed') return 'bg-purple-100 text-purple-700 border-purple-200';
    return 'bg-purple-100 text-purple-700 border-purple-200';
  }

  // Status-based colors
  if (event.status === 'cancelled') return 'bg-red-100 text-red-700 border-red-200';
  if (event.status === 'confirmed') return 'bg-green-100 text-green-700 border-green-200';
  if (event.status === 'tentative') return 'bg-yellow-100 text-yellow-700 border-yellow-200';

  // Default
  return 'bg-blue-100 text-blue-700 border-blue-200';
};