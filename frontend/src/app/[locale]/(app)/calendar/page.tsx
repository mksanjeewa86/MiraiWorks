'use client';

import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useRouter } from 'next/navigation';
import clsx from 'clsx';
import { addDays, addMonths, addWeeks, endOfWeek, format, startOfWeek } from 'date-fns';
import {
  ChevronLeft,
  ChevronRight,
  Clock,
  CloudOff,
  Grid,
  Link2,
  List,
  Loader2,
  Plus,
  RefreshCcw,
  RotateCw,
} from 'lucide-react';
import AppLayout from '@/components/layout/AppLayout';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import CalendarView from '@/components/calendar/CalendarView';
import EventModal from '@/components/calendar/EventModal';
import ConfirmDialog from '@/components/ui/ConfirmDialog';
import { calendarApi } from '@/api/calendar';
import { interviewsApi } from '@/api/interviews';
import { todosApi } from '@/api/todos';
import { useAuth } from '@/contexts/AuthContext';
import type { CalendarEvent, Interview } from '@/types/interview';
import type { CalendarConnection, CalendarProvider } from '@/types/calendar';
import type { SelectionRange } from '@/types/calendar';
import type { CalendarFilters, CalendarViewMode } from '@/types/components';
import type { Todo } from '@/types/todo';
import { toast } from 'sonner';
import { useTranslations } from 'next-intl';

const defaultFilters: CalendarFilters = {
  search: '',
};

const interviewStatusMap: Record<Interview['status'], CalendarEvent['status']> = {
  pending_schedule: 'tentative',
  scheduled: 'confirmed',
  confirmed: 'confirmed',
  in_progress: 'confirmed',
  completed: 'confirmed',
  cancelled: 'cancelled',
};

const toDateOrNull = (value: unknown): Date | null => {
  if (!value) return null;
  const parsed = new Date(value as string);
  return Number.isNaN(parsed.getTime()) ? null : parsed;
};

const toStringArray = (value: unknown): string[] => {
  if (!Array.isArray(value)) {
    return [];
  }

  return value
    .map((item) => {
      if (typeof item === 'string') {
        return item;
      }
      if (item && typeof item === 'object') {
        const record = item as Record<string, unknown>;
        const candidate = record.email ?? record.address ?? record.value ?? record.name ?? null;
        return typeof candidate === 'string' ? candidate : null;
      }
      return null;
    })
    .filter((entry): entry is string => Boolean(entry));
};

const normalizeCalendarEvent = (raw: Record<string, unknown>): CalendarEvent | null => {
  const start =
    raw?.startDatetime ??
    raw?.start_datetime ??
    raw?.start ??
    raw?.start_at ??
    raw?.startTime ??
    raw?.start_time;
  const end =
    raw?.endDatetime ??
    raw?.end_datetime ??
    raw?.end ??
    raw?.end_at ??
    raw?.endTime ??
    raw?.end_time;

  const startDate = toDateOrNull(start);
  if (!startDate) {
    return null;
  }

  const endDate = toDateOrNull(end) ?? new Date(startDate.getTime() + 60 * 60 * 1000);
  const attendeesRaw = raw?.attendees ?? raw?.guest_list ?? [];
  const idSource = raw?.id ?? raw?.event_id ?? raw?.uid ?? raw?.external_id;
  const id = idSource ? String(idSource) : `event-${startDate.getTime()}`;

  return {
    id,
    title: String(raw?.title ?? raw?.summary ?? raw?.name ?? 'Untitled event'),
    description: typeof raw?.description === 'string' ? (raw.description as string) : '',
    location: typeof raw?.location === 'string' ? (raw.location as string) : '',
    startDatetime: startDate.toISOString(),
    endDatetime: endDate.toISOString(),
    timezone:
      typeof raw?.timezone === 'string'
        ? (raw.timezone as string)
        : typeof raw?.time_zone === 'string'
          ? (raw.time_zone as string)
          : undefined,
    isAllDay: Boolean(raw?.isAllDay ?? raw?.all_day ?? raw?.is_all_day ?? false),
    isRecurring: Boolean(raw?.isRecurring ?? raw?.recurring ?? raw?.is_recurring ?? false),
    organizerEmail:
      typeof raw?.organizerEmail === 'string'
        ? (raw.organizerEmail as string)
        : typeof raw?.organizer_email === 'string'
          ? (raw.organizer_email as string)
          : ((raw?.organizer as { email?: string } | undefined)?.email ?? ''),
    organizerName:
      typeof raw?.organizerName === 'string'
        ? (raw.organizerName as string)
        : typeof raw?.organizer_name === 'string'
          ? (raw.organizer_name as string)
          : ((raw?.organizer as { name?: string } | undefined)?.name ?? ''),
    meetingUrl:
      typeof raw?.meetingUrl === 'string'
        ? (raw.meetingUrl as string)
        : typeof raw?.meeting_url === 'string'
          ? (raw.meeting_url as string)
          : '',
    attendees: toStringArray(attendeesRaw),
    status: typeof raw?.status === 'string' ? (raw.status as string) : 'tentative',
    type: 'calendar',
    createdAt:
      typeof raw?.createdAt === 'string'
        ? (raw.createdAt as string)
        : typeof raw?.created_at === 'string'
          ? (raw.created_at as string)
          : new Date().toISOString(),
    updatedAt:
      typeof raw?.updatedAt === 'string'
        ? (raw.updatedAt as string)
        : typeof raw?.updated_at === 'string'
          ? (raw.updated_at as string)
          : new Date().toISOString(),
  };
};

const mapInterviewToEvent = (interview: Interview): CalendarEvent | null => {
  const start = toDateOrNull(interview.scheduled_start);
  if (!start) {
    return null;
  }

  const end =
    toDateOrNull(interview.scheduled_end) ??
    new Date(start.getTime() + (interview.duration_minutes ?? 60) * 60 * 1000);

  return {
    id: `interview-${interview.id}`,
    title: `Interview: ${interview.position_title || interview.title || 'Untitled interview'}`,
    description: interview.description ?? '',
    location: interview.location ?? interview.meeting_url ?? '',
    startDatetime: start.toISOString(),
    endDatetime: end.toISOString(),
    timezone: interview.timezone ?? 'UTC',
    isAllDay: false,
    isRecurring: false,
    organizerEmail: interview.recruiter?.email ?? '',
    organizerName: interview.recruiter?.full_name ?? '',
    meetingUrl: interview.meeting_url ?? '',
    attendees: [interview.candidate?.email, interview.recruiter?.email].filter(Boolean) as string[],
    status: interviewStatusMap[interview.status] ?? 'tentative',
    type: 'interview',
    createdAt: interview.created_at ?? new Date().toISOString(),
    updatedAt: interview.updated_at ?? new Date().toISOString(),
  };
};

const mapTodoToEvent = (todo: Todo, currentUserId: number | null): CalendarEvent | null => {
  // Only show todos with due dates
  if (!todo.due_datetime) {
    return null;
  }

  // Filter logic: show todo only if:
  // 1. No assignee (private todo - show in creator's calendar), OR
  // 2. Current user is the assignee
  const hasAssignee = todo.assignee_id !== null && todo.assignee_id !== undefined;
  const isAssignedToMe = hasAssignee && todo.assignee_id === currentUserId;
  const isMyPrivateTodo = !hasAssignee && todo.owner_id === currentUserId;

  // Only show if it's my private todo or assigned to me
  if (!isMyPrivateTodo && !isAssignedToMe) {
    return null;
  }

  // Parse due_datetime (UTC ISO string from backend)
  const dueDatetime = toDateOrNull(todo.due_datetime);
  if (!dueDatetime) {
    return null;
  }

  let start: Date;
  let end: Date;
  let isAllDay: boolean;

  // Check if time is midnight (00:00:00) - treat as all-day event
  const hours = dueDatetime.getHours();
  const minutes = dueDatetime.getMinutes();
  const seconds = dueDatetime.getSeconds();

  if (hours === 0 && minutes === 0 && seconds === 0) {
    // All-day event (midnight time indicates no specific time)
    start = new Date(dueDatetime);
    start.setHours(0, 0, 0, 0);
    end = new Date(start);
    end.setDate(end.getDate() + 1);
    end.setHours(0, 0, 0, 0);
    isAllDay = true;
  } else {
    // Has specific time - create timed event
    // Browser automatically converts UTC to local time
    start = new Date(dueDatetime);

    // End time is 1 hour after start
    end = new Date(start.getTime() + 60 * 60 * 1000);
    isAllDay = false;
  }

  return {
    id: `todo-${todo.id}`,
    title: `📋 ${todo.title}`,
    description: todo.description ?? '',
    location: '',
    startDatetime: start.toISOString(),
    endDatetime: end.toISOString(),
    timezone: 'UTC',
    isAllDay,
    isRecurring: false,
    organizerEmail: '',
    organizerName: '',
    meetingUrl: '',
    attendees: [],
    status: todo.status === 'completed' ? 'confirmed' : 'tentative',
    type: 'todo',
    createdAt: todo.created_at ?? new Date().toISOString(),
    updatedAt: todo.updated_at ?? new Date().toISOString(),
  };
};

const computeRangeForView = (
  reference: Date,
  view: CalendarViewMode
): { start: Date; end: Date } => {
  const start = new Date(reference);
  const end = new Date(reference);

  if (view === 'month') {
    start.setDate(1);
    start.setHours(0, 0, 0, 0);
    end.setMonth(end.getMonth() + 1, 0);
    end.setHours(23, 59, 59, 999);
  } else if (view === 'week') {
    const weekStart = startOfWeek(reference, { weekStartsOn: 0 });
    const weekEnd = endOfWeek(reference, { weekStartsOn: 0 });
    start.setTime(weekStart.getTime());
    start.setHours(0, 0, 0, 0);
    end.setTime(weekEnd.getTime());
    end.setHours(23, 59, 59, 999);
  } else {
    start.setHours(0, 0, 0, 0);
    end.setHours(23, 59, 59, 999);
  }

  return { start, end };
};

function CalendarPageContent() {
  const { user } = useAuth();
  const router = useRouter();
  const t = useTranslations('calendar');
  const userId = user?.id ?? null;
  const userCompanyId = user?.company_id ?? null;
  const connectionsDropdownRef = useRef<HTMLDivElement>(null);
  const [currentDate, setCurrentDate] = useState(new Date());
  const [viewType, setViewType] = useState<CalendarViewMode>('month');
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState<CalendarFilters>(defaultFilters);
  const [selectedEvent, setSelectedEvent] = useState<CalendarEvent | null>(null);
  const [selectedDate, setSelectedDate] = useState<Date | null>(null);
  const [selectedRange, setSelectedRange] = useState<SelectionRange | undefined>();
  const [modalOpen, setModalOpen] = useState(false);
  const [isCreateMode, setIsCreateMode] = useState(false);
  const [connections, setConnections] = useState<CalendarConnection[]>([]);
  const [connectionsLoading, setConnectionsLoading] = useState(false);
  const [syncingConnectionId, setSyncingConnectionId] = useState<number | null>(null);
  const [showConnections, setShowConnections] = useState(false);
  const [todoConfirmDialog, setTodoConfirmDialog] = useState<{ isOpen: boolean; todoId: number | null }>({
    isOpen: false,
    todoId: null,
  });

  const goToToday = useCallback(() => {
    setCurrentDate(new Date());
  }, []);

  // Reset to today when view type changes
  useEffect(() => {
    setCurrentDate(new Date());
  }, [viewType]);

  const navigateNext = useCallback(() => {
    setCurrentDate((prevDate) => {
      if (viewType === 'month') {
        return addMonths(prevDate, 1); // Move to next month
      } else if (viewType === 'week') {
        return addWeeks(prevDate, 1); // Move to next week
      } else if (viewType === 'day') {
        return addDays(prevDate, 1); // Move to next day
      }
      return prevDate;
    });
  }, [viewType]);

  const navigatePrev = useCallback(() => {
    setCurrentDate((prevDate) => {
      if (viewType === 'month') {
        return addMonths(prevDate, -1); // Move to previous month
      } else if (viewType === 'week') {
        return addWeeks(prevDate, -1); // Move to previous week
      } else if (viewType === 'day') {
        return addDays(prevDate, -1); // Move to previous day
      }
      return prevDate;
    });
  }, [viewType]);

  const loadConnections = useCallback(async () => {
    try {
      setConnectionsLoading(true);
      const response = await calendarApi.getConnections();
      setConnections(Array.isArray(response.data) ? response.data : []);
    } catch (error) {
      console.error('Failed to load calendar connections', error);
      toast.error(t('errors.failedToLoadConnections'));
    } finally {
      setConnectionsLoading(false);
    }
  }, [t]);

  const loadEvents = useCallback(async () => {
    try {
      setLoading(true);
      const { start, end } = computeRangeForView(currentDate, viewType);

      const combined: CalendarEvent[] = [];

      try {
        const calendarResponse = await calendarApi.getEvents({
          startDate: start.toISOString(),
          endDate: end.toISOString(),
        });
        const payload = calendarResponse?.data;

        const extractCalendarItems = (value: unknown): unknown[] => {
          if (Array.isArray(value)) return value;
          if (value && typeof value === 'object') {
            for (const key of ['items', 'events', 'data']) {
              const candidate = (value as Record<string, unknown>)[key];
              if (Array.isArray(candidate)) {
                return candidate;
              }
            }
          }
          return [];
        };

        combined.push(
          ...extractCalendarItems(payload)
            .map((entry) =>
              entry && typeof entry === 'object'
                ? normalizeCalendarEvent(entry as Record<string, unknown>)
                : null
            )
            .filter((entry): entry is CalendarEvent => Boolean(entry))
        );
      } catch (error) {
        console.warn('Failed to load calendar events', error);
      }

      try {
        if (userId && userCompanyId) {
          const interviewResponse = await interviewsApi.getAll({
            recruiter_id: userId,
            employer_company_id: userCompanyId,
          });
          const payload = interviewResponse?.data;

          const extractInterviews = (value: unknown): Interview[] => {
            if (Array.isArray(value)) return value as Interview[];
            if (value && typeof value === 'object') {
              for (const key of ['items', 'interviews', 'data']) {
                const candidate = (value as Record<string, unknown>)[key];
                if (Array.isArray(candidate)) {
                  return candidate as Interview[];
                }
              }
            }
            return [];
          };

          combined.push(
            ...extractInterviews(payload)
              .map((interview) => mapInterviewToEvent(interview))
              .filter((entry): entry is CalendarEvent => Boolean(entry))
          );
        }
      } catch (error) {
        console.warn('Failed to load interview events', error);
      }

      // Load todos with due dates
      try {
        if (userId) {
          // Fetch both owned todos and assigned todos (excluding completed todos)
          const [ownedTodosResponse, assignedTodosResponse] = await Promise.all([
            todosApi.list({ includeCompleted: false }),
            todosApi.listAssignedTodos({ includeCompleted: false })
          ]);

          // Combine owned and assigned todos, removing duplicates by id
          const allTodos = [...(ownedTodosResponse?.items ?? []), ...(assignedTodosResponse?.items ?? [])];
          const uniqueTodos = Array.from(
            new Map(allTodos.map(todo => [todo.id, todo])).values()
          );

          const todos = uniqueTodos;

          // Filter todos that have due dates within the current view range
          const todosWithDueDates = todos.filter((todo) => {
            if (!todo.due_datetime) return false;
            const dueDatetime = toDateOrNull(todo.due_datetime);
            if (!dueDatetime) return false;

            // Normalize dates to start of day for comparison
            const dueDatetimeDay = new Date(dueDatetime);
            dueDatetimeDay.setHours(0, 0, 0, 0);

            const startDay = new Date(start);
            startDay.setHours(0, 0, 0, 0);

            const endDay = new Date(end);
            endDay.setHours(23, 59, 59, 999);

            // Include todos within the view range
            return dueDatetimeDay >= startDay && dueDatetimeDay <= endDay;
          });

          const todoEvents = todosWithDueDates
            .map((todo) => mapTodoToEvent(todo, userId))
            .filter((entry): entry is CalendarEvent => Boolean(entry));

          combined.push(...todoEvents);
        }
      } catch (error) {
        console.warn('Failed to load todo events', error);
      }

      combined.sort(
        (a, b) => new Date(a.startDatetime).getTime() - new Date(b.startDatetime).getTime()
      );
      setEvents(combined);
    } catch (error) {
      console.error('Unexpected error while loading events', error);
      toast.error(t('errors.failedToLoadEvents'));
    } finally {
      setLoading(false);
    }
  }, [currentDate, viewType, userCompanyId, userId, t]);

  useEffect(() => {
    void loadEvents();
  }, [loadEvents]);

  useEffect(() => {
    void loadConnections();
  }, [loadConnections]);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        connectionsDropdownRef.current &&
        !connectionsDropdownRef.current.contains(event.target as Node)
      ) {
        setShowConnections(false);
      }
    };

    if (showConnections) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [showConnections]);

  const filteredEvents = useMemo(() => {
    const searchTerm = filters.search.trim().toLowerCase();

    return events.filter((event) => {
      if (searchTerm) {
        const haystack = [event.title, event.description, event.location]
          .filter(Boolean)
          .join(' ')
          .toLowerCase();
        if (!haystack.includes(searchTerm)) {
          return false;
        }
      }
      return true;
    });
  }, [events, filters]);

  const closeModal = () => {
    setModalOpen(false);
    setSelectedEvent(null);
    setSelectedRange(undefined);
  };

  const openCreateModal = useCallback((range?: SelectionRange) => {
    let start: Date;
    let end: Date;
    const now = new Date();

    if (range?.start) {
      // If a date range is provided (user clicked on a date)
      const clickedDate = new Date(range.start);

      // Check if the clicked date is in the past (before today)
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      const clickedDay = new Date(clickedDate);
      clickedDay.setHours(0, 0, 0, 0);

      if (clickedDay < today) {
        // Prevent creating events in past days
        toast.error(t('errors.cannotCreateEventInPast') || 'Cannot create events in the past');
        return;
      }

      // Set the clicked date with current time
      start = new Date(
        clickedDate.getFullYear(),
        clickedDate.getMonth(),
        clickedDate.getDate(),
        now.getHours(),
        now.getMinutes()
      );

      // End time is ALWAYS 1 hour after start (ignore range.end)
      end = new Date(start.getTime() + 60 * 60 * 1000);
    } else {
      // No range provided (e.g., clicked "New Event" button)
      // Use current date and time
      start = new Date();
      end = new Date(start.getTime() + 60 * 60 * 1000);
    }

    setIsCreateMode(true);
    setSelectedEvent(null);
    setSelectedDate(start);
    setSelectedRange({ start, end, allDay: false });
    setModalOpen(true);
  }, [t]);

  const handleRangeSelect = useCallback(
    (range: SelectionRange) => {
      openCreateModal(range);
    },
    [openCreateModal]
  );

  const handleEventClick = useCallback((event: CalendarEvent) => {
    // Don't open modal for holiday events
    if (event.id?.startsWith('holiday-')) {
      return;
    }

    // Check if this is a todo event
    if (event.id?.startsWith('todo-')) {
      const todoId = parseInt(event.id.replace('todo-', ''), 10);
      if (!isNaN(todoId)) {
        setTodoConfirmDialog({ isOpen: true, todoId });
        return;
      }
    }

    setIsCreateMode(false);
    setSelectedEvent(event);
    setSelectedDate(toDateOrNull(event.startDatetime));
    setSelectedRange(undefined);
    setModalOpen(true);
  }, []);

  const handleSaveEvent = async (eventData: Partial<CalendarEvent>) => {
    try {
      if (isCreateMode) {
        await calendarApi.createEvent(eventData);
        toast.success(t('notifications.eventCreated'));
      } else if (selectedEvent) {
        // Check if the event is editable (numeric ID or starts with "event-" followed by number)
        const isInternalEvent = /^\d+$/.test(selectedEvent.id) || /^event-\d+$/.test(selectedEvent.id);

        if (isInternalEvent) {
          // Extract numeric ID from formats like "12" or "event-12"
          const numericId = selectedEvent.id.replace(/^event-/, '');
          await calendarApi.updateEvent(Number(numericId), eventData);
          toast.success(t('notifications.eventUpdated'));
        } else {
          // External event - cannot edit, silently close modal
          closeModal();
          return;
        }
      }

      await loadEvents();
      closeModal();
    } catch (error) {
      console.error('Failed to save event', error);
      toast.error(t('errors.failedToSaveEvent'));
      throw error;
    }
  };

  const handleDeleteEvent = async (event: CalendarEvent) => {
    try {
      if (event.id) {
        // Check if the event is deletable (numeric ID or starts with "event-" followed by number)
        const isInternalEvent = /^\d+$/.test(event.id) || /^event-\d+$/.test(event.id);

        if (isInternalEvent) {
          // Extract numeric ID from formats like "12" or "event-12"
          const numericId = event.id.replace(/^event-/, '');
          await calendarApi.deleteEvent(Number(numericId));
          toast.success(t('notifications.eventDeleted'));
          await loadEvents();
          closeModal();
        } else {
          // External event - cannot delete, silently close modal
          closeModal();
        }
      } else {
        // No ID - cannot delete, silently close modal
        closeModal();
      }
    } catch (error) {
      console.error('Failed to delete event', error);
      toast.error(t('errors.failedToDeleteEvent'));
      throw error;
    }
  };

  const handleEventDrop = useCallback(
    async (event: CalendarEvent, newStart: Date, newEnd: Date, allDay: boolean) => {
      try {
        // Check if the event is editable (numeric ID or starts with "event-" followed by number)
        const isInternalEvent = /^\d+$/.test(event.id) || /^event-\d+$/.test(event.id);

        if (!isInternalEvent) {
          // External event - cannot edit
          toast.error(t('errors.cannotEditExternalEvent'));
          return;
        }

        // Extract numeric ID from formats like "12" or "event-12"
        const numericId = event.id.replace(/^event-/, '');

        // Update the event with new times
        await calendarApi.updateEvent(Number(numericId), {
          startDatetime: newStart.toISOString(),
          endDatetime: newEnd.toISOString(),
          isAllDay: allDay,
        });

        toast.success(t('notifications.eventUpdated'));
        await loadEvents();
      } catch (error) {
        console.error('Failed to update event', error);
        toast.error(t('errors.failedToSaveEvent'));
        // Reload events to revert the visual change
        await loadEvents();
      }
    },
    [t, loadEvents]
  );

  const handleConnectProvider = async (provider: CalendarProvider) => {
    try {
      const response =
        provider === 'google'
          ? await calendarApi.getGoogleAuthUrl()
          : await calendarApi.getOutlookAuthUrl();
      const authUrl = response?.data?.auth_url;
      if (authUrl) {
        window.open(authUrl, '_blank', 'noopener,noreferrer');
        toast.info(t('notifications.completeConnectionInfo'));
      } else {
        throw new Error(t('errors.missingAuthUrl'));
      }
    } catch (error) {
      console.error('Failed to start calendar connection', error);
      toast.error(t('errors.failedToStartConnection'));
    }
  };

  const handleDisconnect = async (connectionId: number) => {
    try {
      await calendarApi.deleteConnection(connectionId);
      toast.success(t('notifications.calendarDisconnected'));
      await loadConnections();
    } catch (error) {
      console.error('Failed to disconnect calendar', error);
      toast.error(t('errors.failedToDisconnectCalendar'));
    }
  };

  const handleSync = async (connectionId: number) => {
    try {
      setSyncingConnectionId(connectionId);
      await calendarApi.syncCalendar(connectionId);
      toast.success(t('notifications.syncSuccess'));
      await Promise.all([loadConnections(), loadEvents()]);
    } catch (error) {
      console.error('Failed to sync calendar', error);
      toast.error(t('errors.failedToSyncCalendar'));
    } finally {
      setSyncingConnectionId(null);
    }
  };

  const headerLabel = useMemo(() => {
    if (viewType === 'week') {
      const start = startOfWeek(currentDate, { weekStartsOn: 0 });
      const end = endOfWeek(currentDate, { weekStartsOn: 0 });
      return `${format(start, 'MMM d')} - ${format(end, 'MMM d, yyyy')}`;
    }
    if (viewType === 'day') {
      return format(currentDate, 'EEEE, MMM d, yyyy');
    }
    return format(currentDate, 'MMMM yyyy');
  }, [currentDate, viewType]);

  return (
    <AppLayout
      pageTitle={t('page.title')}
      pageDescription={t('page.description')}
      noPadding={true}
    >
      <div className="flex h-full flex-col bg-slate-100/80 overflow-hidden">
        {/* Modern Top Bar */}
        <div className="flex-shrink-0 border-b border-slate-200 bg-white/95 backdrop-blur-sm shadow-sm overflow-visible relative z-10">
          <div className="mx-auto w-full max-w-[1400px] px-4 py-3 lg:px-6">
            {/* Top Row: Title and Action Buttons */}
            <div className="flex items-center justify-between gap-4 mb-3">
              {/* Left: Page Title */}
              <div>
                <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
                  {t('page.title')}
                </h1>
              </div>

              {/* Right: Action Buttons */}
              <div className="flex items-center gap-2">
                {/* Connections Dropdown */}
                <div className="relative" ref={connectionsDropdownRef}>
                  <button
                    type="button"
                    onClick={() => setShowConnections(!showConnections)}
                    className="inline-flex items-center gap-2 rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm font-medium text-slate-700 shadow-sm transition-all hover:border-blue-400 hover:bg-blue-50 hover:text-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-1"
                  >
                    <Link2 className="h-4 w-4" />
                    <span className="hidden sm:inline">Connections</span>
                    <span className="inline-flex items-center justify-center min-w-[20px] h-5 px-1.5 text-xs font-semibold rounded-full bg-slate-100 text-slate-700">
                      {connections.length}
                    </span>
                  </button>

                  {/* Connections Dropdown Panel */}
                  {showConnections && (
                    <div className="absolute right-0 top-full z-20 mt-2 w-80 rounded-xl border border-slate-200 bg-white shadow-2xl">
                      <div className="p-4">
                        <h3 className="mb-3 text-sm font-bold text-slate-900">
                          Calendar Connections
                        </h3>
                        {connectionsLoading ? (
                          <div className="flex items-center justify-center py-6">
                            <Loader2 className="h-6 w-6 animate-spin text-blue-500" />
                          </div>
                        ) : connections.length === 0 ? (
                          <div className="space-y-3 py-2">
                            <div className="flex items-center gap-2 rounded-lg bg-slate-50 p-3 text-sm text-slate-600">
                              <CloudOff className="h-4 w-4 text-slate-400" />
                              <span>No calendar connections</span>
                            </div>
                            <div className="space-y-2 pt-2">
                              <button
                                type="button"
                                onClick={() => handleConnectProvider('google')}
                                className="w-full rounded-lg bg-gradient-to-r from-blue-500 to-blue-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition-all hover:from-blue-600 hover:to-blue-700 hover:shadow-md"
                              >
                                Connect Google Calendar
                              </button>
                              <button
                                type="button"
                                onClick={() => handleConnectProvider('outlook')}
                                className="w-full rounded-lg bg-gradient-to-r from-indigo-500 to-indigo-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition-all hover:from-indigo-600 hover:to-indigo-700 hover:shadow-md"
                              >
                                Connect Outlook Calendar
                              </button>
                            </div>
                          </div>
                        ) : (
                          <div className="space-y-2">
                            {connections.map((connection) => (
                              <div
                                key={connection.id}
                                className="flex items-center justify-between rounded-lg border border-slate-200 bg-gradient-to-br from-slate-50 to-white p-3 transition-all hover:border-slate-300 hover:shadow-sm"
                              >
                                <div className="flex items-center gap-3">
                                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-100">
                                    <Link2 className="h-4 w-4 text-blue-600" />
                                  </div>
                                  <div>
                                    <p className="text-sm font-semibold text-slate-900">
                                      {connection.provider === 'google' ? 'Google Calendar' : 'Outlook Calendar'}
                                    </p>
                                    <p className="text-xs text-slate-500">{connection.provider_email}</p>
                                  </div>
                                </div>
                                <div className="flex items-center gap-1">
                                  <button
                                    type="button"
                                    onClick={() => handleSync(connection.id)}
                                    disabled={syncingConnectionId === connection.id}
                                    className="rounded-lg p-2 text-slate-400 transition-all hover:bg-blue-50 hover:text-blue-600 disabled:cursor-not-allowed disabled:opacity-50"
                                    title="Sync calendar"
                                  >
                                    {syncingConnectionId === connection.id ? (
                                      <Loader2 className="h-4 w-4 animate-spin" />
                                    ) : (
                                      <RefreshCcw className="h-4 w-4" />
                                    )}
                                  </button>
                                  <button
                                    type="button"
                                    onClick={() => handleDisconnect(connection.id)}
                                    className="rounded-lg p-2 text-slate-400 transition-all hover:bg-red-50 hover:text-red-600"
                                    title="Disconnect"
                                  >
                                    <CloudOff className="h-4 w-4" />
                                  </button>
                                </div>
                              </div>
                            ))}
                            <div className="mt-3 space-y-2 border-t border-slate-200 pt-3">
                              <button
                                type="button"
                                onClick={() => handleConnectProvider('google')}
                                className="w-full rounded-lg border border-blue-200 bg-blue-50 px-3 py-2 text-sm font-medium text-blue-700 transition-all hover:bg-blue-100 hover:border-blue-300"
                              >
                                + Connect Google Calendar
                              </button>
                              <button
                                type="button"
                                onClick={() => handleConnectProvider('outlook')}
                                className="w-full rounded-lg border border-indigo-200 bg-indigo-50 px-3 py-2 text-sm font-medium text-indigo-700 transition-all hover:bg-indigo-100 hover:border-indigo-300"
                              >
                                + Connect Outlook Calendar
                              </button>
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>

                {/* New Event Button */}
                <button
                  type="button"
                  onClick={() => openCreateModal()}
                  className="inline-flex items-center gap-2 rounded-lg bg-gradient-to-r from-blue-600 to-blue-700 px-4 py-2 text-sm font-semibold text-white shadow-md transition-all hover:from-blue-700 hover:to-blue-800 hover:shadow-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                >
                  <Plus className="h-4 w-4" />
                  <span className="hidden sm:inline">{t('form.newEvent')}</span>
                  <span className="sm:hidden">New</span>
                </button>
              </div>
            </div>

            {/* Bottom Row: Navigation and View Controls */}
            <div className="flex items-center justify-between gap-4 flex-wrap">
              {/* Left: Date Navigation */}
              <div className="flex items-center gap-3">
                {/* Today Button */}
                <button
                  type="button"
                  onClick={goToToday}
                  className="inline-flex items-center gap-1.5 rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-sm font-medium text-slate-700 shadow-sm transition-all hover:bg-slate-50 hover:border-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-1"
                >
                  <RotateCw className="h-3.5 w-3.5" />
                  <span className="hidden sm:inline">{t('navigation.today')}</span>
                </button>

                {/* Navigation Controls */}
                <div className="flex items-center gap-1 rounded-lg border border-slate-300 bg-white p-1 shadow-sm">
                  <button
                    type="button"
                    onClick={navigatePrev}
                    className="inline-flex items-center justify-center rounded-md p-1.5 text-slate-600 transition-all hover:bg-slate-100 hover:text-slate-900"
                    aria-label={t('navigation.previous')}
                  >
                    <ChevronLeft className="h-4 w-4" />
                  </button>
                  <div className="px-3 min-w-[200px] text-center">
                    <p className="text-sm font-semibold text-slate-900">{headerLabel}</p>
                  </div>
                  <button
                    type="button"
                    onClick={navigateNext}
                    className="inline-flex items-center justify-center rounded-md p-1.5 text-slate-600 transition-all hover:bg-slate-100 hover:text-slate-900"
                    aria-label={t('navigation.next')}
                  >
                    <ChevronRight className="h-4 w-4" />
                  </button>
                </div>
              </div>

              {/* Right: View Toggle */}
              <div className="flex items-center gap-1 rounded-lg border border-slate-300 bg-slate-50 p-1 shadow-sm">
                {(
                  [
                    { key: 'month', label: t('page.month'), icon: Grid },
                    { key: 'week', label: t('page.week'), icon: List },
                    { key: 'day', label: t('page.day'), icon: Clock },
                  ] as { key: CalendarViewMode; label: string; icon: typeof Grid }[]
                ).map(({ key, label, icon: Icon }) => (
                  <button
                    key={key}
                    type="button"
                    onClick={() => setViewType(key)}
                    className={clsx(
                      'inline-flex items-center gap-1.5 rounded-md px-3 py-1.5 text-sm font-medium transition-all',
                      viewType === key
                        ? 'bg-white text-blue-600 shadow-sm ring-1 ring-blue-100'
                        : 'text-slate-600 hover:bg-white/50 hover:text-slate-900'
                    )}
                  >
                    <Icon className="h-4 w-4" />
                    <span className="hidden sm:inline">{label}</span>
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>

        <div className="mx-auto flex w-full max-w-[1400px] flex-1 overflow-hidden px-4 pb-6 pt-4 lg:px-6">
          <div className="flex min-w-0 flex-1 flex-col overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
            <CalendarView
              currentDate={currentDate}
              onDateChange={setCurrentDate}
              viewType={viewType}
              onViewChange={setViewType}
              events={filteredEvents}
              onRangeSelect={handleRangeSelect}
              onEventClick={handleEventClick}
              onEventDrop={handleEventDrop}
              loading={loading}
              canCreateEvents
            />
          </div>
        </div>

        <EventModal
          isOpen={modalOpen}
          onClose={closeModal}
          event={selectedEvent}
          selectedDate={selectedDate}
          selectedRange={selectedRange}
          isCreateMode={isCreateMode}
          onSave={handleSaveEvent}
          onDelete={handleDeleteEvent}
        />

        <ConfirmDialog
          isOpen={todoConfirmDialog.isOpen}
          onClose={() => setTodoConfirmDialog({ isOpen: false, todoId: null })}
          onConfirm={() => {
            if (todoConfirmDialog.todoId) {
              router.push(`/todos?edit=${todoConfirmDialog.todoId}`);
            }
            setTodoConfirmDialog({ isOpen: false, todoId: null });
          }}
          title="Open Todo Details?"
          description="You can view or edit the complete details of this todo on the Todos page."
          confirmText="Open Todo"
          cancelText="Cancel"
          variant="info"
        />
      </div>
    </AppLayout>
  );
}

export default function CalendarPage() {
  return (
    <ProtectedRoute>
      <CalendarPageContent />
    </ProtectedRoute>
  );
}
