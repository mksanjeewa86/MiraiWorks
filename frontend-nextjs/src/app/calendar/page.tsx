'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import AppLayout from '@/components/layout/AppLayout';
import Card from '@/components/ui/Card';
import Badge from '@/components/ui/Badge';
import Button from '@/components/ui/Button';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import { ChevronLeft, ChevronRight, Plus, Calendar as CalendarIcon, Clock, MapPin, Users } from 'lucide-react';
import type { CalendarEvent } from '@/types';

interface CalendarState {
  currentDate: Date;
  events: CalendarEvent[];
  loading: boolean;
  selectedDate: Date | null;
  viewMode: 'month' | 'week' | 'day';
}

export default function CalendarPage() {
  const { user } = useAuth();
  
  const [state, setState] = useState<CalendarState>({
    currentDate: new Date(),
    events: [],
    loading: true,
    selectedDate: null,
    viewMode: 'month'
  });

  // Mock events data
  const mockEvents: CalendarEvent[] = [
    {
      id: '1',
      title: 'Interview with Sarah Johnson',
      description: 'Senior Frontend Developer Position',
      start_time: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(), // Tomorrow
      end_time: new Date(Date.now() + 24 * 60 * 60 * 1000 + 60 * 60 * 1000).toISOString(), // 1 hour
      event_type: 'interview',
      location: 'Conference Room A',
      attendees: [
        { id: '1', email: user?.email || '', full_name: user?.full_name || '', role: user?.role || 'candidate' },
        { id: '2', email: 'sarah.johnson@company.com', full_name: 'Sarah Johnson', role: 'candidate' }
      ],
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      created_by: user?.id || '1'
    },
    {
      id: '2',
      title: 'Team Standup',
      description: 'Weekly team sync meeting',
      start_time: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000).toISOString(), // Day after tomorrow
      end_time: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000 + 30 * 60 * 1000).toISOString(), // 30 min
      event_type: 'meeting',
      location: 'Zoom',
      attendees: [
        { id: '1', email: user?.email || '', full_name: user?.full_name || '', role: user?.role || 'candidate' }
      ],
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      created_by: user?.id || '1'
    },
    {
      id: '3',
      title: 'Client Presentation',
      description: 'Quarterly business review',
      start_time: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(), // Next week
      end_time: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000 + 2 * 60 * 60 * 1000).toISOString(), // 2 hours
      event_type: 'meeting',
      location: 'Client Office',
      attendees: [
        { id: '1', email: user?.email || '', full_name: user?.full_name || '', role: user?.role || 'candidate' }
      ],
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      created_by: user?.id || '1'
    }
  ];

  useEffect(() => {
    // Simulate loading events
    setTimeout(() => {
      setState(prev => ({
        ...prev,
        events: mockEvents,
        loading: false
      }));
    }, 1000);
  }, []);

  const getDaysInMonth = (date: Date) => {
    return new Date(date.getFullYear(), date.getMonth() + 1, 0).getDate();
  };

  const getFirstDayOfMonth = (date: Date) => {
    return new Date(date.getFullYear(), date.getMonth(), 1).getDay();
  };

  const formatTime = (dateString: string) => {
    return new Date(dateString).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric'
    });
  };

  const getEventsForDate = (date: Date) => {
    return state.events.filter(event => {
      const eventDate = new Date(event.start_time);
      return eventDate.toDateString() === date.toDateString();
    });
  };

  const getEventTypeColor = (eventType: string) => {
    switch (eventType) {
      case 'interview':
        return 'primary';
      case 'meeting':
        return 'success';
      default:
        return 'secondary';
    }
  };

  const navigateMonth = (direction: 'prev' | 'next') => {
    setState(prev => ({
      ...prev,
      currentDate: new Date(
        prev.currentDate.getFullYear(),
        prev.currentDate.getMonth() + (direction === 'next' ? 1 : -1),
        1
      )
    }));
  };

  const renderCalendarGrid = () => {
    const daysInMonth = getDaysInMonth(state.currentDate);
    const firstDayOfMonth = getFirstDayOfMonth(state.currentDate);
    const days = [];

    // Empty cells for days before the first day of the month
    for (let i = 0; i < firstDayOfMonth; i++) {
      days.push(
        <div key={`empty-${i}`} className="h-24 bg-gray-50 dark:bg-gray-900 opacity-50"></div>
      );
    }

    // Days of the month
    for (let day = 1; day <= daysInMonth; day++) {
      const date = new Date(state.currentDate.getFullYear(), state.currentDate.getMonth(), day);
      const dayEvents = getEventsForDate(date);
      const isToday = date.toDateString() === new Date().toDateString();
      const isSelected = state.selectedDate?.toDateString() === date.toDateString();

      days.push(
        <div
          key={day}
          onClick={() => setState(prev => ({ ...prev, selectedDate: date }))}
          className={`h-24 border border-gray-200 dark:border-gray-700 p-2 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors ${
            isSelected ? 'bg-blue-50 dark:bg-blue-900/20 border-brand-primary' : ''
          }`}
        >
          <div className={`text-sm font-medium mb-1 ${
            isToday ? 'text-brand-primary font-bold' : ''
          }`} style={{ color: isToday ? 'var(--brand-primary)' : 'var(--text-primary)' }}>
            {day}
            {isToday && <span className="ml-1 text-xs">Today</span>}
          </div>
          <div className="space-y-1">
            {dayEvents.slice(0, 2).map(event => (
              <div
                key={event.id}
                className="text-xs p-1 rounded truncate"
                style={{ backgroundColor: 'var(--brand-primary)', color: 'white' }}
                title={event.title}
              >
                {event.title}
              </div>
            ))}
            {dayEvents.length > 2 && (
              <div className="text-xs text-gray-500">+{dayEvents.length - 2} more</div>
            )}
          </div>
        </div>
      );
    }

    return days;
  };

  const selectedDateEvents = state.selectedDate ? getEventsForDate(state.selectedDate) : [];
  const upcomingEvents = state.events
    .filter(event => new Date(event.start_time) > new Date())
    .sort((a, b) => new Date(a.start_time).getTime() - new Date(b.start_time).getTime())
    .slice(0, 5);

  if (state.loading) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center h-64">
          <LoadingSpinner className="w-8 h-8" />
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout>
      <div className="p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold" style={{ color: 'var(--text-primary)' }}>Calendar</h1>
            <p className="mt-1" style={{ color: 'var(--text-secondary)' }}>
              Manage your schedule and upcoming events
            </p>
          </div>
          <Button className="flex items-center gap-2">
            <Plus className="h-4 w-4" />
            New Event
          </Button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Calendar */}
          <div className="lg:col-span-2">
            <Card className="p-6">
              {/* Calendar Header */}
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-4">
                  <h2 className="text-xl font-semibold" style={{ color: 'var(--text-primary)' }}>
                    {state.currentDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
                  </h2>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => navigateMonth('prev')}
                    >
                      <ChevronLeft className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => navigateMonth('next')}
                    >
                      <ChevronRight className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setState(prev => ({ ...prev, currentDate: new Date() }))}
                >
                  Today
                </Button>
              </div>

              {/* Days of Week Header */}
              <div className="grid grid-cols-7 gap-0 mb-2">
                {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
                  <div
                    key={day}
                    className="p-3 text-sm font-medium text-center border-b border-gray-200 dark:border-gray-700"
                    style={{ color: 'var(--text-secondary)' }}
                  >
                    {day}
                  </div>
                ))}
              </div>

              {/* Calendar Grid */}
              <div className="grid grid-cols-7 gap-0">
                {renderCalendarGrid()}
              </div>
            </Card>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Selected Date Events */}
            {state.selectedDate && (
              <Card className="p-6">
                <h3 className="text-lg font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>
                  {state.selectedDate.toLocaleDateString('en-US', { 
                    weekday: 'long', 
                    month: 'long', 
                    day: 'numeric' 
                  })}
                </h3>
                {selectedDateEvents.length > 0 ? (
                  <div className="space-y-3">
                    {selectedDateEvents.map(event => (
                      <div
                        key={event.id}
                        className="p-3 rounded-lg border border-gray-200 dark:border-gray-700"
                      >
                        <div className="flex items-start justify-between mb-2">
                          <h4 className="font-medium" style={{ color: 'var(--text-primary)' }}>
                            {event.title}
                          </h4>
                          <Badge variant={getEventTypeColor(event.event_type)}>
                            {event.event_type}
                          </Badge>
                        </div>
                        <div className="space-y-1 text-sm" style={{ color: 'var(--text-secondary)' }}>
                          <div className="flex items-center gap-2">
                            <Clock className="h-4 w-4" />
                            {formatTime(event.start_time)} - {formatTime(event.end_time)}
                          </div>
                          {event.location && (
                            <div className="flex items-center gap-2">
                              <MapPin className="h-4 w-4" />
                              {event.location}
                            </div>
                          )}
                          <div className="flex items-center gap-2">
                            <Users className="h-4 w-4" />
                            {event.attendees.length} attendees
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-center py-4" style={{ color: 'var(--text-muted)' }}>
                    No events scheduled for this date
                  </p>
                )}
              </Card>
            )}

            {/* Upcoming Events */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>
                Upcoming Events
              </h3>
              {upcomingEvents.length > 0 ? (
                <div className="space-y-3">
                  {upcomingEvents.map(event => (
                    <div
                      key={event.id}
                      className="p-3 rounded-lg border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
                    >
                      <div className="flex items-center justify-between mb-1">
                        <h4 className="font-medium text-sm" style={{ color: 'var(--text-primary)' }}>
                          {event.title}
                        </h4>
                        <Badge variant={getEventTypeColor(event.event_type)} size="sm">
                          {event.event_type}
                        </Badge>
                      </div>
                      <div className="text-xs space-y-1" style={{ color: 'var(--text-secondary)' }}>
                        <div className="flex items-center gap-1">
                          <CalendarIcon className="h-3 w-3" />
                          {formatDate(event.start_time)} at {formatTime(event.start_time)}
                        </div>
                        {event.location && (
                          <div className="flex items-center gap-1">
                            <MapPin className="h-3 w-3" />
                            {event.location}
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-center py-4" style={{ color: 'var(--text-muted)' }}>
                  No upcoming events
                </p>
              )}
            </Card>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}