'use client';

import { useMemo } from 'react';
import clsx from 'clsx';
import {
  CalendarDays,
  CircleCheck,
  CloudOff,
  Link2,
  Loader2,
  PlugZap,
  RefreshCcw,
  Search,
  X,
} from 'lucide-react';
import { format } from 'date-fns';
import type { CalendarEvent } from '@/types/interview';
import type { CalendarConnection } from '@/types/calendar';
import type { CalendarSidebarProps, CalendarFilters } from '@/types/components';

const providerMeta = {
  google: {
    label: 'Google Calendar',
    accentClass: 'bg-emerald-100 text-emerald-700',
  },
  outlook: {
    label: 'Microsoft Outlook',
    accentClass: 'bg-blue-100 text-blue-700',
  },
};

type ProviderKey = keyof typeof providerMeta;

const STATUS_BADGES: Record<CalendarConnection['status'], string> = {
  connected: 'bg-emerald-100 text-emerald-700',
  error: 'bg-red-100 text-red-700',
  expired: 'bg-amber-100 text-amber-700',
  disabled: 'bg-slate-100 text-slate-600',
};

const getEventPalette = (event: CalendarEvent) => {
  if (event.id.startsWith('holiday-')) {
    return {
      backgroundColor: '#dc2626',
      textColor: '#ffffff',
      badgeLabel: 'Holiday',
    };
  }

  if (event.id.startsWith('interview-') || event.type === 'interview') {
    return {
      backgroundColor: '#7c3aed',
      textColor: '#ffffff',
      badgeLabel: 'Interview',
    };
  }

  if (event.id.startsWith('todo-')) {
    return {
      backgroundColor: '#0ea5e9',
      textColor: '#ffffff',
      badgeLabel: 'Task',
    };
  }

  return {
    backgroundColor: '#2563eb',
    textColor: '#ffffff',
    badgeLabel: 'Event',
  };
};

const formatTimeRange = (startIso: string, endIso: string) => {
  const start = new Date(startIso);
  const end = new Date(endIso || startIso);

  if (Number.isNaN(start.valueOf()) || Number.isNaN(end.valueOf())) {
    return '';
  }

  const sameDay = start.toDateString() === end.toDateString();
  if (sameDay) {
    return `${format(start, 'MMM d, h:mm a')} - ${format(end, 'h:mm a')}`;
  }

  return `${format(start, 'MMM d, h:mm a')} - ${format(end, 'MMM d, h:mm a')}`;
};

const EmptyUpcomingState = () => (
  <div className="flex flex-1 flex-col items-center justify-center rounded-xl border border-dashed border-slate-200 bg-slate-50/60 p-6 text-center">
    <CalendarDays className="mb-3 h-8 w-8 text-slate-400" />
    <p className="text-sm font-semibold text-slate-600">No upcoming events</p>
    <p className="mt-1 text-xs text-slate-500">Create an event or connect a calendar to get started.</p>
  </div>
);

const FiltersSection = ({
  filters,
  onFiltersChange,
}: {
  filters: CalendarFilters;
  onFiltersChange: (filters: CalendarFilters) => void;
}) => (
  <div className="space-y-4">
    <div className="relative">
      <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
      <input
        type="search"
        placeholder="Search events"
        value={filters.search}
        onChange={(event) => onFiltersChange({ ...filters, search: event.target.value })}
        className="w-full rounded-lg border border-slate-200 bg-white py-2 pl-9 pr-3 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200"
      />
    </div>
    <div>
      <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">Event type</p>
      <div className="mt-2 flex flex-wrap gap-2">
        {[
          { key: 'all', label: 'All' },
          { key: 'calendar', label: 'Internal' },
          { key: 'interview', label: 'Interviews' },
        ].map(({ key, label }) => {
          const active = filters.eventType === key;
          return (
            <button
              key={key}
              type="button"
              onClick={() => onFiltersChange({ ...filters, eventType: key as CalendarFilters['eventType'] })}
              className={clsx(
                'rounded-full border px-3 py-1 text-xs font-medium transition focus:outline-none focus:ring-2 focus:ring-blue-200',
                active
                  ? 'border-transparent bg-blue-600 text-white shadow-sm'
                  : 'border-slate-200 bg-white text-slate-600 hover:border-blue-300 hover:text-blue-600'
              )}
            >
              {label}
            </button>
          );
        })}
      </div>
    </div>
    <div>
      <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">Status</p>
      <div className="mt-2 grid grid-cols-2 gap-2">
        {[
          { key: 'all', label: 'All' },
          { key: 'tentative', label: 'Tentative' },
          { key: 'confirmed', label: 'Confirmed' },
          { key: 'cancelled', label: 'Cancelled' },
        ].map(({ key, label }) => {
          const active = filters.status === key;
          return (
            <button
              key={key}
              type="button"
              onClick={() => onFiltersChange({ ...filters, status: key as CalendarFilters['status'] })}
              className={clsx(
                'rounded-lg border px-3 py-1.5 text-xs font-medium transition focus:outline-none focus:ring-2 focus:ring-blue-200',
                active
                  ? 'border-transparent bg-blue-100 text-blue-700'
                  : 'border-slate-200 bg-white text-slate-600 hover:border-blue-300 hover:text-blue-600'
              )}
            >
              {label}
            </button>
          );
        })}
      </div>
    </div>
  </div>
);

interface ConnectionListProps {
  connections: CalendarConnection[];
  onConnectProvider: CalendarSidebarProps['onConnectProvider'];
  onDisconnect: CalendarSidebarProps['onDisconnect'];
  onSync: CalendarSidebarProps['onSync'];
  loadingConnections: boolean;
  syncingConnectionId?: number | null;
}

const ConnectionsSection = ({
  connections,
  onConnectProvider,
  onDisconnect,
  onSync,
  loadingConnections,
  syncingConnectionId,
}: ConnectionListProps) => (
  <div className="space-y-4">
    <div className="flex items-center justify-between">
      <h3 className="text-sm font-semibold text-slate-700">Connected calendars</h3>
      {loadingConnections && <Loader2 className="h-4 w-4 animate-spin text-blue-500" />}
    </div>
    <div className="grid grid-cols-1 gap-2">
      {(Object.keys(providerMeta) as ProviderKey[]).map((provider) => (
        <button
          key={provider}
          type="button"
          onClick={() => onConnectProvider(provider)}
          className="flex items-center justify-between rounded-lg border border-dashed border-slate-300 bg-white px-3 py-2 text-left text-sm font-medium text-slate-600 shadow-sm transition hover:border-blue-400 hover:bg-blue-50/50"
        >
          <span>{providerMeta[provider].label}</span>
          <span className={clsx('rounded-full px-2 py-0.5 text-xs font-semibold', providerMeta[provider].accentClass)}>
            Connect
          </span>
        </button>
      ))}
    </div>

    {connections.length > 0 && (
      <div className="space-y-3">
        {connections.map((connection) => {
          const provider = providerMeta[connection.provider as ProviderKey];
          return (
            <div
              key={connection.id}
              className="rounded-xl border border-slate-200 bg-white p-3 shadow-sm"
            >
              <div className="flex items-start justify-between gap-2">
                <div>
                  <div className="flex items-center gap-2">
                    <span className={clsx('rounded-full px-2 py-0.5 text-[11px] font-semibold', provider.accentClass)}>
                      {provider.label}
                    </span>
                    <span
                      className={clsx(
                        'rounded-full px-2 py-0.5 text-[10px] font-semibold uppercase',
                        STATUS_BADGES[connection.status]
                      )}
                    >
                      {connection.status}
                    </span>
                  </div>
                  <p className="mt-2 text-sm font-semibold text-slate-700">
                    {connection.display_name ?? connection.provider_email}
                  </p>
                  <p className="text-xs text-slate-500">{connection.provider_email}</p>
                  {connection.last_sync_at && (
                    <p className="mt-1 text-xs text-slate-400">
                      Last sync: {format(new Date(connection.last_sync_at), 'MMM d, h:mm a')}
                    </p>
                  )}
                  {connection.sync_error && (
                    <p className="mt-1 flex items-center gap-1 text-xs text-red-600">
                      <CloudOff className="h-3.5 w-3.5" />
                      {connection.sync_error}
                    </p>
                  )}
                </div>
                <div className="flex flex-col gap-2">
                  <button
                    type="button"
                    onClick={() => onSync(connection.id)}
                    className="inline-flex items-center gap-1 rounded-lg border border-slate-200 bg-white px-3 py-1 text-xs font-medium text-slate-600 shadow-sm transition hover:border-blue-300 hover:text-blue-600"
                  >
                    {syncingConnectionId === connection.id ? (
                      <Loader2 className="h-3.5 w-3.5 animate-spin" />
                    ) : (
                      <RefreshCcw className="h-3.5 w-3.5" />
                    )}
                    Sync
                  </button>
                  <button
                    type="button"
                    onClick={() => onDisconnect(connection.id)}
                    className="inline-flex items-center gap-1 rounded-lg border border-transparent bg-slate-100 px-3 py-1 text-xs font-medium text-slate-500 transition hover:bg-red-100 hover:text-red-600"
                  >
                    <Link2 className="h-3.5 w-3.5 rotate-45" />
                    Disconnect
                  </button>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    )}
  </div>
);

export default function CalendarSidebar({
  isOpen,
  onClose,
  events,
  onEventClick,
  filters,
  onFiltersChange,
  onCreateEvent,
  connections,
  onConnectProvider,
  onDisconnect,
  onSync,
  loadingConnections,
  syncingConnectionId,
}: CalendarSidebarProps) {
  const upcomingEvents = useMemo(() => {
    const now = new Date();
    return [...events]
      .filter((event) => {
        const end = new Date(event.endDatetime || event.startDatetime);
        return !Number.isNaN(end.valueOf()) && end >= now;
      })
      .sort((a, b) => new Date(a.startDatetime).getTime() - new Date(b.startDatetime).getTime())
      .slice(0, 8);
  }, [events]);

  return (
    <div
      className={clsx(
        'fixed inset-0 z-40 flex bg-slate-900/40 transition-opacity duration-200 lg:relative lg:inset-auto lg:z-auto lg:bg-transparent',
        isOpen ? 'opacity-100' : 'pointer-events-none opacity-0 lg:pointer-events-auto lg:opacity-100'
      )}
    >
      <div className="flex-1 lg:hidden" onClick={onClose} role="presentation" />
      <aside
        className={clsx(
          'relative ml-auto flex h-full w-full max-w-sm transform flex-col overflow-hidden bg-gradient-to-b from-white to-slate-50 shadow-xl transition-transform duration-200 lg:ml-0 lg:w-80 lg:transform-none lg:shadow-none',
          isOpen ? 'translate-x-0' : 'translate-x-full lg:translate-x-0'
        )}
      >
        <div className="flex items-center justify-between border-b border-slate-200 px-5 py-4 lg:py-5">
          <div>
            <h2 className="text-base font-semibold text-slate-800">Planner</h2>
            <p className="text-xs text-slate-500">Keep track of interviews, tasks, and synced events.</p>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="rounded-full border border-slate-200 p-1 text-slate-500 transition hover:border-slate-300 hover:text-slate-700 lg:hidden"
            aria-label="Close sidebar"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="flex flex-1 flex-col gap-6 overflow-y-auto px-5 py-6">
          <FiltersSection filters={filters} onFiltersChange={onFiltersChange} />

          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-semibold text-slate-700">Upcoming</h3>
              <span className="rounded-full bg-slate-200 px-2 py-0.5 text-[11px] font-semibold text-slate-600">
                {upcomingEvents.length}
              </span>
            </div>
            {upcomingEvents.length === 0 ? (
              <EmptyUpcomingState />
            ) : (
              <div className="space-y-3">
                {upcomingEvents.map((event) => {
                  const palette = getEventPalette(event);
                  return (
                    <button
                      key={event.id}
                      type="button"
                      onClick={() => onEventClick(event)}
                      className="w-full rounded-xl border border-slate-200 bg-white p-3 text-left shadow-sm transition hover:border-blue-300 hover:shadow-md"
                    >
                      <div className="flex items-start justify-between gap-2">
                        <div>
                          <p className="text-sm font-semibold text-slate-800">{event.title}</p>
                          <p className="mt-1 text-xs text-slate-500">{formatTimeRange(event.startDatetime, event.endDatetime)}</p>
                          {event.location && (
                            <p className="mt-1 text-xs text-slate-400">{event.location}</p>
                          )}
                        </div>
                        {palette.badgeLabel && (
                          <span
                            className="rounded-full px-2 py-0.5 text-[10px] font-semibold uppercase"
                            style={{
                              backgroundColor: palette.backgroundColor,
                              color: palette.textColor,
                            }}
                          >
                            {palette.badgeLabel}
                          </span>
                        )}
                      </div>
                    </button>
                  );
                })}
              </div>
            )}
          </div>

          <ConnectionsSection
            connections={connections}
            onConnectProvider={onConnectProvider}
            onDisconnect={onDisconnect}
            onSync={onSync}
            loadingConnections={loadingConnections}
            syncingConnectionId={syncingConnectionId}
          />
        </div>

        <div className="border-t border-slate-200 bg-white px-5 py-4 text-xs text-slate-400">
          <div className="flex items-center gap-2">
            <CircleCheck className="h-4 w-4" />
            Calendar sync keeps interviews, tasks, and external events aligned.
          </div>
        </div>
      </aside>
    </div>
  );
}
