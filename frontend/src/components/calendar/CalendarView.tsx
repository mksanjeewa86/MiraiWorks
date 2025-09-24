'use client';

import React, { useState, useMemo } from 'react';
import { ChevronLeft, ChevronRight, Clock, MapPin, Users, Plus, Loader2 } from 'lucide-react';
import type { CalendarEvent } from '@/types/interview';
import type { CalendarViewProps } from '@/types/components';
import { getEventColorScheme } from '@/utils/calendarHelpers';

export default function CalendarView({
  currentDate,
  onDateChange,
  viewType,
  events,
  onDateSelect,
  onEventClick,
  loading,
  canCreateEvents,
}: CalendarViewProps) {
  const [hoveredDate, setHoveredDate] = useState<Date | null>(null);

  // Navigation handlers
  const navigatePrevious = () => {
    const newDate = new Date(currentDate);
    if (viewType === 'month') {
      newDate.setMonth(newDate.getMonth() - 1);
    } else if (viewType === 'week') {
      newDate.setDate(newDate.getDate() - 7);
    } else {
      newDate.setDate(newDate.getDate() - 1);
    }
    onDateChange(newDate);
  };

  const navigateNext = () => {
    const newDate = new Date(currentDate);
    if (viewType === 'month') {
      newDate.setMonth(newDate.getMonth() + 1);
    } else if (viewType === 'week') {
      newDate.setDate(newDate.getDate() + 7);
    } else {
      newDate.setDate(newDate.getDate() + 1);
    }
    onDateChange(newDate);
  };

  const goToToday = () => {
    onDateChange(new Date());
  };

  // Generate calendar data based on view type
  const calendarData = useMemo(() => {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();

    if (viewType === 'month') {
      // Generate month view
      const firstDay = new Date(year, month, 1);
      const startDate = new Date(firstDay);
      startDate.setDate(startDate.getDate() - firstDay.getDay());

      const days = [];
      const current = new Date(startDate);

      for (let i = 0; i < 42; i++) {
        // 6 weeks * 7 days
        days.push(new Date(current));
        current.setDate(current.getDate() + 1);
      }

      return { days, weeks: chunk(days, 7) };
    } else if (viewType === 'week') {
      // Generate week view
      const startOfWeek = new Date(currentDate);
      startOfWeek.setDate(currentDate.getDate() - currentDate.getDay());

      const days = [];
      for (let i = 0; i < 7; i++) {
        const day = new Date(startOfWeek);
        day.setDate(startOfWeek.getDate() + i);
        days.push(day);
      }

      return { days, weeks: [days] };
    } else {
      // Generate day view
      return { days: [currentDate], weeks: [[currentDate]] };
    }
  }, [currentDate, viewType]);

  // Helper function to chunk array
  function chunk<T>(array: T[], size: number): T[][] {
    const chunks = [];
    for (let i = 0; i < array.length; i += size) {
      chunks.push(array.slice(i, i + size));
    }
    return chunks;
  }

  // Get events for a specific date
  const getEventsForDate = (date: Date) => {
    return events.filter((event) => {
      const eventDate = new Date(event.startDatetime);
      return eventDate.toDateString() === date.toDateString();
    });
  };

  // Check if date is today
  const isToday = (date: Date) => {
    const today = new Date();
    return date.toDateString() === today.toDateString();
  };

  // Check if date is in current month
  const isCurrentMonth = (date: Date) => {
    return date.getMonth() === currentDate.getMonth();
  };

  // Get event color using helper function
  const getEventColor = (event: CalendarEvent) => {
    return getEventColorScheme(event);
  };

  // Render loading state
  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin text-blue-600 mx-auto mb-4" />
          <p className="text-gray-600">Loading calendar...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col bg-white">
      {/* Calendar Navigation */}
      <div className="flex items-center justify-between px-8 py-5 border-b border-gray-100 bg-gray-50/50">
        <div className="flex items-center space-x-6">
          <div className="flex items-center space-x-2">
            <button
              onClick={navigatePrevious}
              className="p-2.5 rounded-xl text-gray-500 hover:bg-white hover:text-gray-700 hover:shadow-sm transition-all"
            >
              <ChevronLeft className="h-5 w-5" />
            </button>

            <button
              onClick={navigateNext}
              className="p-2.5 rounded-xl text-gray-500 hover:bg-white hover:text-gray-700 hover:shadow-sm transition-all"
            >
              <ChevronRight className="h-5 w-5" />
            </button>
          </div>

          <h2 className="text-2xl font-semibold text-gray-900">
            {viewType === 'month' &&
              currentDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
            {viewType === 'week' &&
              `Week of ${calendarData.days[0].toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}`}
            {viewType === 'day' &&
              currentDate.toLocaleDateString('en-US', {
                weekday: 'long',
                month: 'long',
                day: 'numeric',
                year: 'numeric',
              })}
          </h2>
        </div>

        <button
          onClick={goToToday}
          className="px-4 py-2 text-sm font-medium text-blue-600 bg-blue-50 border border-blue-200 rounded-xl hover:bg-blue-100 hover:border-blue-300 transition-all"
        >
          Today
        </button>
      </div>

      {/* Calendar Grid */}
      <div className="flex-1 overflow-auto">
        {viewType === 'month' && (
          <div className="min-h-full bg-white">
            {/* Days of week header */}
            <div className="grid grid-cols-7 border-b border-gray-100 bg-gray-50/30">
              {['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'].map(
                (day) => (
                  <div
                    key={day}
                    className="p-4 text-xs font-semibold text-gray-600 text-center uppercase tracking-wider"
                  >
                    {day.slice(0, 3)}
                  </div>
                )
              )}
            </div>

            {/* Calendar weeks */}
            {calendarData.weeks.map((week, weekIndex) => (
              <div key={weekIndex} className="grid grid-cols-7 min-h-[140px]">
                {week.map((date, dayIndex) => {
                  const dayEvents = getEventsForDate(date);
                  const isCurrentMonthDate = isCurrentMonth(date);
                  const isTodayDate = isToday(date);

                  return (
                    <div
                      key={dayIndex}
                      className={`border-r border-b border-gray-100 p-3 cursor-pointer transition-all duration-200 ${
                        isCurrentMonthDate
                          ? 'bg-white hover:bg-gray-50/80'
                          : 'bg-gray-50/50 text-gray-400'
                      } ${isTodayDate ? 'bg-blue-50/70 ring-2 ring-blue-200 ring-inset' : ''}`}
                      onClick={() => canCreateEvents && onDateSelect(date)}
                      onMouseEnter={() => setHoveredDate(date)}
                      onMouseLeave={() => setHoveredDate(null)}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <span
                          className={`text-sm font-semibold transition-colors ${
                            isTodayDate
                              ? 'text-blue-600 bg-blue-100 w-7 h-7 rounded-full flex items-center justify-center'
                              : isCurrentMonthDate
                                ? 'text-gray-900'
                                : 'text-gray-400'
                          }`}
                        >
                          {date.getDate()}
                        </span>
                        {canCreateEvents && hoveredDate?.toDateString() === date.toDateString() && (
                          <Plus className="h-4 w-4 text-blue-500 opacity-60 hover:opacity-100 transition-opacity" />
                        )}
                      </div>

                      <div className="space-y-1.5">
                        {dayEvents.slice(0, 3).map((event, eventIndex) => (
                          <div
                            key={eventIndex}
                            className={`px-2.5 py-1.5 rounded-lg text-xs font-medium cursor-pointer transition-all hover:shadow-sm hover:scale-105 ${getEventColor(event)}`}
                            onClick={(e) => {
                              e.stopPropagation();
                              onEventClick(event);
                            }}
                          >
                            <div className="truncate font-semibold">{event.title}</div>
                            {event.location && (
                              <div className="flex items-center text-xs opacity-80 mt-1">
                                <MapPin className="h-3 w-3 mr-1" />
                                <span className="truncate">{event.location}</span>
                              </div>
                            )}
                          </div>
                        ))}
                        {dayEvents.length > 3 && (
                          <div className="text-xs text-gray-500 font-medium bg-gray-100 px-2 py-1 rounded-lg text-center">
                            +{dayEvents.length - 3} more
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            ))}
          </div>
        )}

        {viewType === 'week' && (
          <div className="flex flex-col h-full">
            {/* Days header */}
            <div className="grid grid-cols-8 border-b border-gray-200">
              <div className="p-4"></div>
              {calendarData.days.map((date, index) => (
                <div key={index} className="p-4 text-center border-l border-gray-200">
                  <div className="text-sm font-medium text-gray-700">
                    {date.toLocaleDateString('en-US', { weekday: 'short' })}
                  </div>
                  <div
                    className={`text-lg font-semibold mt-1 ${
                      isToday(date) ? 'text-blue-600' : 'text-gray-900'
                    }`}
                  >
                    {date.getDate()}
                  </div>
                </div>
              ))}
            </div>

            {/* Time slots */}
            <div className="flex-1 overflow-auto">
              {Array.from({ length: 24 }, (_, hour) => (
                <div key={hour} className="grid grid-cols-8 min-h-[60px] border-b border-gray-100">
                  <div className="p-2 text-sm text-gray-500 border-r border-gray-200">
                    {hour === 0
                      ? '12:00 AM'
                      : hour < 12
                        ? `${hour}:00 AM`
                        : hour === 12
                          ? '12:00 PM'
                          : `${hour - 12}:00 PM`}
                  </div>
                  {calendarData.days.map((date, dayIndex) => {
                    const dayEvents = getEventsForDate(date).filter((event) => {
                      const eventHour = new Date(event.startDatetime).getHours();
                      return eventHour === hour;
                    });

                    return (
                      <div
                        key={dayIndex}
                        className="border-l border-gray-200 p-1 cursor-pointer hover:bg-gray-50"
                        onClick={() =>
                          canCreateEvents && onDateSelect(new Date(date.setHours(hour)))
                        }
                      >
                        {dayEvents.map((event, eventIndex) => (
                          <div
                            key={eventIndex}
                            className={`px-2 py-1 rounded text-xs font-medium border cursor-pointer mb-1 ${getEventColor(event)}`}
                            onClick={(e) => {
                              e.stopPropagation();
                              onEventClick(event);
                            }}
                          >
                            <div className="truncate">{event.title}</div>
                            <div className="flex items-center text-xs opacity-75">
                              <Clock className="h-3 w-3 mr-1" />
                              {new Date(event.startDatetime).toLocaleTimeString('en-US', {
                                hour: 'numeric',
                                minute: '2-digit',
                              })}
                            </div>
                          </div>
                        ))}
                      </div>
                    );
                  })}
                </div>
              ))}
            </div>
          </div>
        )}

        {viewType === 'day' && (
          <div className="flex flex-col h-full">
            {/* Day header */}
            <div className="p-6 border-b border-gray-200 text-center">
              <h3 className="text-xl font-semibold text-gray-900">
                {currentDate.toLocaleDateString('en-US', {
                  weekday: 'long',
                  month: 'long',
                  day: 'numeric',
                })}
              </h3>
            </div>

            {/* Time slots */}
            <div className="flex-1 overflow-auto">
              {Array.from({ length: 24 }, (_, hour) => {
                const hourEvents = getEventsForDate(currentDate).filter((event) => {
                  const eventHour = new Date(event.startDatetime).getHours();
                  return eventHour === hour;
                });

                return (
                  <div key={hour} className="flex min-h-[80px] border-b border-gray-100">
                    <div className="w-20 p-4 text-sm text-gray-500 border-r border-gray-200">
                      {hour === 0
                        ? '12:00 AM'
                        : hour < 12
                          ? `${hour}:00 AM`
                          : hour === 12
                            ? '12:00 PM'
                            : `${hour - 12}:00 PM`}
                    </div>
                    <div
                      className="flex-1 p-2 cursor-pointer hover:bg-gray-50"
                      onClick={() =>
                        canCreateEvents && onDateSelect(new Date(currentDate.setHours(hour)))
                      }
                    >
                      {hourEvents.map((event, eventIndex) => (
                        <div
                          key={eventIndex}
                          className={`px-4 py-2 rounded-lg border cursor-pointer mb-2 ${getEventColor(event)}`}
                          onClick={(e) => {
                            e.stopPropagation();
                            onEventClick(event);
                          }}
                        >
                          <div className="font-medium">{event.title}</div>
                          <div className="flex items-center text-sm opacity-75 mt-1">
                            <Clock className="h-4 w-4 mr-2" />
                            {new Date(event.startDatetime).toLocaleTimeString('en-US', {
                              hour: 'numeric',
                              minute: '2-digit',
                            })}{' '}
                            -{' '}
                            {new Date(event.endDatetime).toLocaleTimeString('en-US', {
                              hour: 'numeric',
                              minute: '2-digit',
                            })}
                          </div>
                          {event.location && (
                            <div className="flex items-center text-sm opacity-75 mt-1">
                              <MapPin className="h-4 w-4 mr-2" />
                              {event.location}
                            </div>
                          )}
                          {event.attendees.length > 0 && (
                            <div className="flex items-center text-sm opacity-75 mt-1">
                              <Users className="h-4 w-4 mr-2" />
                              {event.attendees.length} attendees
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
