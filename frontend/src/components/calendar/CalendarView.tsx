'use client';

import { useCallback, useEffect, useMemo, useRef } from 'react';
import dynamic from 'next/dynamic';
import dayGridPlugin from '@fullcalendar/daygrid';
import timeGridPlugin from '@fullcalendar/timegrid';
import interactionPlugin from '@fullcalendar/interaction';
import listPlugin from '@fullcalendar/list';
import type { CalendarApi, DateSelectArg, EventClickArg, DatesSetArg } from '@fullcalendar/core';
import type { CalendarEvent } from '@/types/interview';
import type { CalendarViewProps, CalendarViewMode } from '@/types/components';

const FullCalendar = dynamic(
  () => import('@fullcalendar/react').then((mod) => ({ default: mod.default })),
  {
    ssr: false,
    loading: () => (
      <div className="flex items-center justify-center h-96">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-500 border-t-transparent" />
      </div>
    ),
  }
);

const viewToFullCalendar: Record<CalendarViewMode, string> = {
  month: 'dayGridMonth',
  week: 'timeGridWeek',
  day: 'timeGridDay',
  list: 'listWeek',
};

const fullCalendarToView: Partial<Record<string, CalendarViewMode>> = {
  dayGridMonth: 'month',
  timeGridWeek: 'week',
  timeGridDay: 'day',
  listWeek: 'list',
};

const getEventPalette = (event: CalendarEvent | undefined) => {
  if (!event) {
    return {
      backgroundColor: '#2563eb',
      borderColor: '#1d4ed8',
      textColor: '#ffffff',
    };
  }

  if (event.id?.startsWith('holiday-')) {
    return {
      backgroundColor: '#dc2626',
      borderColor: '#b91c1c',
      textColor: '#ffffff',
    };
  }

  if (event.id?.startsWith('interview-')) {
    return {
      backgroundColor: '#7c3aed',
      borderColor: '#6d28d9',
      textColor: '#ffffff',
    };
  }

  if (event.id?.startsWith('todo-')) {
    return {
      backgroundColor: '#0ea5e9',
      borderColor: '#0284c7',
      textColor: '#ffffff',
    };
  }

  return {
    backgroundColor: '#2563eb',
    borderColor: '#1d4ed8',
    textColor: '#ffffff',
  };
};

export default function CalendarView({
  currentDate,
  onDateChange,
  viewType,
  onViewChange,
  events,
  onRangeSelect,
  onEventClick,
  loading,
  canCreateEvents,
}: CalendarViewProps) {
  const calendarApiRef = useRef<CalendarApi | null>(null);

  const calendarEvents = useMemo(
    () =>
      events.map((event) => {
        const palette = getEventPalette(event);
        const isHoliday = event.id?.startsWith('holiday-');
        return {
          id: event.id,
          title: event.title,
          start: event.startDatetime,
          end: event.endDatetime,
          allDay: event.isAllDay,
          extendedProps: { raw: event },
          backgroundColor: palette.backgroundColor,
          borderColor: palette.borderColor,
          textColor: palette.textColor,
          classNames: isHoliday ? ['holiday-event'] : [],
        };
      }),
    [events]
  );

  useEffect(() => {
    const api = calendarApiRef.current;
    if (api) {
      const targetView = viewToFullCalendar[viewType];
      if (api.view.type !== targetView) {
        api.changeView(targetView);
      }
    }
  }, [viewType]);

  useEffect(() => {
    const api = calendarApiRef.current;
    if (api) {
      api.gotoDate(currentDate);
    }
  }, [currentDate]);

  // Apply holiday styling when events change
  useEffect(() => {
    const applyHolidayStyling = () => {
      // Clear previous holiday classes
      document.querySelectorAll('.holiday-day').forEach((cell) => {
        cell.classList.remove('holiday-day');
      });

      // Apply holiday styling
      const holidayEvents = events.filter((event) => event.id?.startsWith('holiday-'));
      holidayEvents.forEach((holiday) => {
        const holidayDate = new Date(holiday.startDatetime);

        // Format date correctly to avoid timezone issues
        const year = holidayDate.getFullYear();
        const month = String(holidayDate.getMonth() + 1).padStart(2, '0');
        const day = String(holidayDate.getDate()).padStart(2, '0');
        const dateStr = `${year}-${month}-${day}`;

        // Find all date cells for this holiday
        const dateCells = document.querySelectorAll(`[data-date="${dateStr}"]`);
        dateCells.forEach((cell) => {
          cell.classList.add('holiday-day');
        });
      });
    };

    // Apply with a small delay to ensure DOM is ready
    const timeoutId = setTimeout(applyHolidayStyling, 100);
    return () => clearTimeout(timeoutId);
  }, [events]);

  const handleSelect = useCallback(
    (selection: DateSelectArg) => {
      if (onRangeSelect) {
        onRangeSelect({
          start: selection.start,
          end: selection.end,
          allDay: selection.allDay,
        });
      }
    },
    [onRangeSelect]
  );

  const handleEventClick = useCallback(
    (eventClickArg: EventClickArg) => {
      const rawEvent =
        (eventClickArg.event.extendedProps?.raw as CalendarEvent | undefined) ?? undefined;
      if (rawEvent) {
        onEventClick(rawEvent);
        return;
      }

      const now = new Date().toISOString();
      onEventClick({
        id: eventClickArg.event.id,
        title: eventClickArg.event.title,
        startDatetime: eventClickArg.event.startStr,
        endDatetime: eventClickArg.event.endStr || eventClickArg.event.startStr,
        isAllDay: eventClickArg.event.allDay,
        isRecurring: false,
        attendees: [],
        createdAt: now,
        updatedAt: now,
      } as CalendarEvent);
    },
    [onEventClick]
  );

  const handleDatesSet = useCallback(
    (datesSetArg: DatesSetArg) => {
      calendarApiRef.current = datesSetArg.view.calendar;

      const nextView = fullCalendarToView[datesSetArg.view.type];
      if (nextView && nextView !== viewType) {
        onViewChange(nextView);
      }

      // Only update date if it's actually different to prevent circular updates
      const newDate = datesSetArg.view.currentStart;
      if (newDate.getTime() !== currentDate.getTime()) {
        onDateChange(newDate);
      }

      // Add holiday styling to date cells
      setTimeout(() => {
        const holidayEvents = events.filter((event) => event.id?.startsWith('holiday-'));
        holidayEvents.forEach((holiday) => {
          const holidayDate = new Date(holiday.startDatetime);

          // Format date correctly to avoid timezone issues
          const year = holidayDate.getFullYear();
          const month = String(holidayDate.getMonth() + 1).padStart(2, '0');
          const day = String(holidayDate.getDate()).padStart(2, '0');
          const dateStr = `${year}-${month}-${day}`;

          // Find all date cells for this holiday
          const dateCells = document.querySelectorAll(`[data-date="${dateStr}"]`);
          dateCells.forEach((cell) => {
            cell.classList.add('holiday-day');
          });
        });
      }, 100);
    },
    [viewType, currentDate, onViewChange, onDateChange, events]
  );

  return (
    <div className="relative flex-1 overflow-hidden">
      {loading && (
        <div className="absolute inset-0 z-20 flex items-center justify-center bg-white/60 backdrop-blur-sm">
          <div className="h-10 w-10 animate-spin rounded-full border-4 border-blue-500 border-t-transparent" />
        </div>
      )}
      <div className="h-full w-full">
        <FullCalendar
          plugins={[dayGridPlugin, timeGridPlugin, interactionPlugin, listPlugin]}
          initialView={viewToFullCalendar[viewType]}
          initialDate={currentDate}
          events={calendarEvents}
          headerToolbar={false}
          height="100%"
          buttonText={{
            today: 'Today',
            month: 'Month',
            week: 'Week',
            day: 'Day',
            list: 'Agenda',
          }}
          selectable={canCreateEvents}
          selectMirror
          select={handleSelect}
          selectLongPressDelay={200}
          eventClick={handleEventClick}
          datesSet={handleDatesSet}
          eventOverlap
          dayMaxEventRows={3}
          moreLinkClick="popover"
          moreLinkClassNames="text-xs text-blue-600 hover:text-blue-700 font-medium cursor-pointer bg-blue-50 hover:bg-blue-100 rounded px-1 py-0.5 transition-colors"
          moreLinkContent={(args) => `+${args.num} more`}
          weekends
          nowIndicator
          slotLabelFormat={{
            hour: '2-digit',
            minute: '2-digit',
            hour12: false,
          }}
          eventTimeFormat={{
            hour: '2-digit',
            minute: '2-digit',
            hour12: false,
          }}
          stickyHeaderDates
          displayEventEnd
          eventDisplay="block"
          progressiveEventRendering
        />
      </div>
    </div>
  );
}
