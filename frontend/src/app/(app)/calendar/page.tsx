'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';
import clsx from 'clsx';
import { addDays, addMonths, addWeeks, endOfWeek, format, startOfWeek } from 'date-fns';
import {
  Calendar as CalendarIcon,
  ChevronLeft,
  ChevronRight,
  Clock,
  Grid,
  List,
  Menu,
  Plus,
  RotateCw,
} from 'lucide-react';
import AppLayout from '@/components/layout/AppLayout';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import CalendarView from '@/components/calendar/CalendarView';
import CalendarSidebar from '@/components/calendar/CalendarSidebar';
import EventModal from '@/components/calendar/EventModal';
import { calendarApi } from '@/api/calendar';
import { interviewsApi } from '@/api/interviews';
import { useAuth } from '@/contexts/AuthContext';
import type { CalendarEvent, Interview } from '@/types/interview';
import type { CalendarConnection, CalendarProvider } from '@/types/calendar';
import type { SelectionRange } from '@/types/calendar';
import type { CalendarFilters, CalendarViewMode } from '@/types/components';
import { toast } from 'sonner';

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
  } else if (view === 'list') {
    start.setHours(0, 0, 0, 0);
    const listEnd = addDays(start, 14);
    end.setTime(listEnd.getTime());
    end.setHours(23, 59, 59, 999);
  } else {
    start.setHours(0, 0, 0, 0);
    end.setHours(23, 59, 59, 999);
  }

  return { start, end };
};

function CalendarPageContent() {
  const { user } = useAuth();
  const userId = user?.id ?? null;
  const userCompanyId = user?.company_id ?? null;
  const [currentDate, setCurrentDate] = useState(new Date());
  const [viewType, setViewType] = useState<CalendarViewMode>('month');
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [filters, setFilters] = useState<CalendarFilters>(defaultFilters);
  const [selectedEvent, setSelectedEvent] = useState<CalendarEvent | null>(null);
  const [selectedDate, setSelectedDate] = useState<Date | null>(null);
  const [selectedRange, setSelectedRange] = useState<SelectionRange | undefined>();
  const [modalOpen, setModalOpen] = useState(false);
  const [isCreateMode, setIsCreateMode] = useState(false);
  const [connections, setConnections] = useState<CalendarConnection[]>([]);
  const [connectionsLoading, setConnectionsLoading] = useState(false);
  const [syncingConnectionId, setSyncingConnectionId] = useState<number | null>(null);

  const goToToday = useCallback(() => {
    setCurrentDate(new Date());
  }, []);

  const navigateNext = useCallback(() => {
    setCurrentDate((prevDate) => {
      if (viewType === 'month') {
        return addMonths(prevDate, 1); // Move to next month
      } else if (viewType === 'week') {
        return addWeeks(prevDate, 1); // Move to next week
      } else if (viewType === 'day') {
        return addDays(prevDate, 1); // Move to next day
      } else if (viewType === 'list') {
        return addWeeks(prevDate, 2); // Move 2 weeks forward for list view
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
      } else if (viewType === 'list') {
        return addWeeks(prevDate, -2); // Move 2 weeks back for list view
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
      toast.error('Unable to load calendar connections.');
    } finally {
      setConnectionsLoading(false);
    }
  }, []);

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

      combined.sort(
        (a, b) => new Date(a.startDatetime).getTime() - new Date(b.startDatetime).getTime()
      );
      setEvents(combined);
    } catch (error) {
      console.error('Unexpected error while loading events', error);
      toast.error('Unable to load calendar events.');
    } finally {
      setLoading(false);
    }
  }, [currentDate, viewType, userCompanyId, userId]);

  useEffect(() => {
    void loadEvents();
  }, [loadEvents]);

  useEffect(() => {
    void loadConnections();
  }, [loadConnections]);

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
    const start = range?.start ?? new Date();
    const end = range?.end ?? new Date(start.getTime() + 60 * 60 * 1000);
    setIsCreateMode(true);
    setSelectedEvent(null);
    setSelectedDate(start);
    setSelectedRange(range ?? { start, end, allDay: false });
    setModalOpen(true);
    setSidebarOpen(false);
  }, []);

  const handleRangeSelect = useCallback(
    (range: SelectionRange) => {
      openCreateModal(range);
    },
    [openCreateModal]
  );

  const handleEventClick = useCallback((event: CalendarEvent) => {
    setIsCreateMode(false);
    setSelectedEvent(event);
    setSelectedDate(toDateOrNull(event.startDatetime));
    setSelectedRange(undefined);
    setModalOpen(true);
    setSidebarOpen(false);
  }, []);

  const handleSaveEvent = async (eventData: Partial<CalendarEvent>) => {
    try {
      if (isCreateMode) {
        await calendarApi.createEvent(eventData);
        toast.success('Event created.');
      } else if (selectedEvent && /^\d+$/.test(selectedEvent.id)) {
        await calendarApi.updateEvent(Number(selectedEvent.id), eventData);
        toast.success('Event updated.');
      } else {
        toast.error('This event can only be edited from its source.');
        return;
      }

      await loadEvents();
      closeModal();
    } catch (error) {
      console.error('Failed to save event', error);
      toast.error('Unable to save event. Please try again.');
      throw error;
    }
  };

  const handleDeleteEvent = async (event: CalendarEvent) => {
    try {
      if (event.id && /^\d+$/.test(event.id)) {
        await calendarApi.deleteEvent(Number(event.id));
        toast.success('Event deleted.');
        await loadEvents();
        closeModal();
      } else {
        toast.error('This event must be managed from the interview workflow.');
      }
    } catch (error) {
      console.error('Failed to delete event', error);
      toast.error('Unable to delete event.');
      throw error;
    }
  };

  const handleConnectProvider = async (provider: CalendarProvider) => {
    try {
      const response =
        provider === 'google'
          ? await calendarApi.getGoogleAuthUrl()
          : await calendarApi.getOutlookAuthUrl();
      const authUrl = response?.data?.auth_url;
      if (authUrl) {
        window.open(authUrl, '_blank', 'noopener,noreferrer');
        toast.info('Complete the connection in the new tab, then return to sync.');
      } else {
        throw new Error('Missing auth URL');
      }
    } catch (error) {
      console.error('Failed to start calendar connection', error);
      toast.error('Unable to start the calendar connection flow.');
    }
  };

  const handleDisconnect = async (connectionId: number) => {
    try {
      await calendarApi.deleteConnection(connectionId);
      toast.success('Calendar disconnected.');
      await loadConnections();
    } catch (error) {
      console.error('Failed to disconnect calendar', error);
      toast.error('Unable to disconnect calendar.');
    }
  };

  const handleSync = async (connectionId: number) => {
    try {
      setSyncingConnectionId(connectionId);
      await calendarApi.syncCalendar(connectionId);
      toast.success('Sync started. It may take a moment to finish.');
      await Promise.all([loadConnections(), loadEvents()]);
    } catch (error) {
      console.error('Failed to sync calendar', error);
      toast.error('Unable to trigger sync.');
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
    if (viewType === 'list') {
      return `${format(currentDate, 'MMM d')} - ${format(addDays(currentDate, 14), 'MMM d, yyyy')}`;
    }
    return format(currentDate, 'MMMM yyyy');
  }, [currentDate, viewType]);

  return (
    <AppLayout
      pageTitle="Calendar"
      pageDescription="Manage interviews, internal events, and synced calendars."
    >
      <div className="flex h-screen flex-col bg-slate-100/80">
        <div className="border-b border-slate-200 bg-white/90 backdrop-blur">
          <div className="mx-auto flex w-full max-w-[1400px] items-center justify-between gap-4 px-4 py-4 lg:px-6">
            <div className="flex flex-1 items-center gap-3">
              <button
                type="button"
                onClick={() => setSidebarOpen(true)}
                className="inline-flex items-center justify-center rounded-full border border-slate-200 bg-white p-2 text-slate-500 transition hover:border-blue-300 hover:text-blue-600 lg:hidden"
                aria-label="Open calendar sidebar"
              >
                <Menu className="h-5 w-5" />
              </button>
              <div>
                <h1 className="text-xl font-semibold text-slate-900">Calendar</h1>
                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={navigatePrev}
                    className="inline-flex items-center justify-center rounded-full p-1 text-slate-400 transition hover:bg-slate-100 hover:text-slate-600"
                    aria-label="Previous"
                  >
                    <ChevronLeft className="h-4 w-4" />
                  </button>
                  <p className="text-xs text-slate-500 min-w-0 flex-1 text-center">{headerLabel}</p>
                  <button
                    type="button"
                    onClick={navigateNext}
                    className="inline-flex items-center justify-center rounded-full p-1 text-slate-400 transition hover:bg-slate-100 hover:text-slate-600"
                    aria-label="Next"
                  >
                    <ChevronRight className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={goToToday}
                className="hidden items-center gap-1 rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-600 shadow-sm transition hover:border-blue-300 hover:text-blue-600 lg:inline-flex"
              >
                <RotateCw className="h-4 w-4" />
                Today
              </button>
              <div className="hidden rounded-full border border-slate-200 bg-slate-50 p-1 text-xs font-semibold text-slate-500 lg:flex">
                {(
                  [
                    { key: 'month', label: 'Month', icon: Grid },
                    { key: 'week', label: 'Week', icon: List },
                    { key: 'day', label: 'Day', icon: Clock },
                    { key: 'list', label: 'Agenda', icon: CalendarIcon },
                  ] as { key: CalendarViewMode; label: string; icon: typeof Grid }[]
                ).map(({ key, label, icon: Icon }) => (
                  <button
                    key={key}
                    type="button"
                    onClick={() => setViewType(key)}
                    className={clsx(
                      'inline-flex items-center gap-1 rounded-full px-3 py-1.5 transition',
                      viewType === key
                        ? 'bg-white text-blue-600 shadow-sm'
                        : 'text-slate-500 hover:text-blue-600'
                    )}
                  >
                    <Icon className="h-3.5 w-3.5" />
                    {label}
                  </button>
                ))}
              </div>
              <button
                type="button"
                onClick={() => openCreateModal()}
                className="inline-flex items-center gap-2 rounded-full bg-blue-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-700"
              >
                <Plus className="h-4 w-4" />
                New event
              </button>
            </div>
          </div>
        </div>

        <div className="mx-auto flex w-full max-w-[1400px] flex-1 gap-6 overflow-hidden px-4 pb-6 pt-4 lg:px-6">
          <div className="hidden w-80 flex-shrink-0 lg:block">
            <div className="h-full overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
              <CalendarSidebar
                isOpen
                onClose={() => setSidebarOpen(false)}
                events={filteredEvents}
                onEventClick={handleEventClick}
                filters={filters}
                onFiltersChange={setFilters}
                onCreateEvent={() => openCreateModal()}
                connections={connections}
                onConnectProvider={handleConnectProvider}
                onDisconnect={handleDisconnect}
                onSync={handleSync}
                loadingConnections={connectionsLoading}
                syncingConnectionId={syncingConnectionId}
              />
            </div>
          </div>

          <div className="flex min-w-0 flex-1 flex-col overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
            <CalendarView
              currentDate={currentDate}
              onDateChange={setCurrentDate}
              viewType={viewType}
              onViewChange={setViewType}
              events={filteredEvents}
              onRangeSelect={handleRangeSelect}
              onEventClick={handleEventClick}
              loading={loading}
              canCreateEvents
            />
          </div>
        </div>

        {sidebarOpen && (
          <CalendarSidebar
            isOpen={sidebarOpen}
            onClose={() => setSidebarOpen(false)}
            events={filteredEvents}
            onEventClick={handleEventClick}
            filters={filters}
            onFiltersChange={setFilters}
            onCreateEvent={() => openCreateModal()}
            connections={connections}
            onConnectProvider={handleConnectProvider}
            onDisconnect={handleDisconnect}
            onSync={handleSync}
            loadingConnections={connectionsLoading}
            syncingConnectionId={syncingConnectionId}
          />
        )}

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
