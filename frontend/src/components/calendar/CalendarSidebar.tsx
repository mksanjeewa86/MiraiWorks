'use client';

import React from 'react';
import {
  X,
  Calendar,
  Clock,
  MapPin,
  Users,
  Search,
  CalendarCheck,
  CalendarClock,
  CalendarX,
  Video,
  Phone,
  MessageSquare
} from 'lucide-react';
import type { CalendarEvent } from '@/types/interview';

interface CalendarSidebarProps {
  isOpen: boolean;
  onClose: () => void;
  events: CalendarEvent[];
  onEventClick: (event: CalendarEvent) => void;
  filters: {
    eventType: string;
    status: string;
    search: string;
  };
  onFiltersChange: (filters: {
    eventType: string;
    status: string;
    search: string;
  }) => void;
  userRole: string;
}

export default function CalendarSidebar({
  isOpen,
  onClose,
  events,
  onEventClick,
  filters,
  onFiltersChange,
  userRole
}: CalendarSidebarProps) {
  // Group events by date
  const groupedEvents = events.reduce((groups, event) => {
    const date = new Date(event.startDatetime).toDateString();
    if (!groups[date]) {
      groups[date] = [];
    }
    groups[date].push(event);
    return groups;
  }, {} as Record<string, CalendarEvent[]>);

  // Sort dates
  const sortedDates = Object.keys(groupedEvents).sort((a, b) =>
    new Date(a).getTime() - new Date(b).getTime()
  );

  // Get event icon based on type
  const getEventIcon = (event: CalendarEvent) => {
    if (event.id.toString().startsWith('interview-') || event.title.toLowerCase().includes('interview')) {
      return <Video className="h-4 w-4 text-purple-600" />;
    }
    if (event.title.toLowerCase().includes('meeting')) {
      return <Users className="h-4 w-4 text-blue-600" />;
    }
    if (event.title.toLowerCase().includes('call') || event.title.toLowerCase().includes('phone')) {
      return <Phone className="h-4 w-4 text-green-600" />;
    }
    if (event.title.toLowerCase().includes('screening')) {
      return <MessageSquare className="h-4 w-4 text-orange-600" />;
    }
    return <Calendar className="h-4 w-4 text-gray-600" />;
  };

  // Get status icon
  const getStatusIcon = (status?: string) => {
    switch (status) {
      case 'confirmed':
        return <CalendarCheck className="h-4 w-4 text-green-600" />;
      case 'tentative':
        return <CalendarClock className="h-4 w-4 text-yellow-600" />;
      case 'cancelled':
        return <CalendarX className="h-4 w-4 text-red-600" />;
      default:
        return <Calendar className="h-4 w-4 text-gray-400" />;
    }
  };

  // Filter options based on user role
  const eventTypeOptions = [
    { value: 'all', label: 'All Events' },
    { value: 'interview', label: 'Interviews' },
    { value: 'meeting', label: 'Meetings' },
    { value: 'call', label: 'Calls' },
  ];

  if (userRole === 'candidate') {
    eventTypeOptions.push({ value: 'personal', label: 'Personal' });
  }

  if (['super_admin', 'company_admin', 'recruiter'].includes(userRole)) {
    eventTypeOptions.push(
      { value: 'screening', label: 'Screenings' },
      { value: 'onboarding', label: 'Onboarding' }
    );
  }

  return (
    <>
      {/* Mobile Overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-black bg-opacity-50 lg:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <div className={`
        fixed left-0 top-0 z-50 h-full w-80 bg-white shadow-lg transform transition-transform duration-300 ease-in-out
        lg:static lg:transform-none lg:shadow-none lg:z-auto lg:h-full lg:w-full
        ${isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
      `}>
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-gray-100">
            <h2 className="text-xl font-semibold text-gray-900">Upcoming Events</h2>
            <button
              onClick={onClose}
              className="lg:hidden p-2 rounded-xl text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors"
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          {/* Filters */}
          <div className="p-6 border-b border-gray-100 space-y-5">
            {/* Search */}
            <div className="relative">
              <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
              <input
                type="text"
                placeholder="Search events..."
                value={filters.search}
                onChange={(e) => onFiltersChange({ ...filters, search: e.target.value })}
                className="w-full pl-11 pr-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-300 text-sm bg-gray-50 focus:bg-white transition-colors"
              />
            </div>

            {/* Event Type Filter */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-3">
                Event Type
              </label>
              <select
                value={filters.eventType}
                onChange={(e) => onFiltersChange({ ...filters, eventType: e.target.value })}
                className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-300 text-sm bg-gray-50 focus:bg-white transition-colors"
              >
                {eventTypeOptions.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Status Filter */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-3">
                Status
              </label>
              <select
                value={filters.status}
                onChange={(e) => onFiltersChange({ ...filters, status: e.target.value })}
                className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-300 text-sm bg-gray-50 focus:bg-white transition-colors"
              >
                <option value="all">All Status</option>
                <option value="confirmed">Confirmed</option>
                <option value="tentative">Tentative</option>
                <option value="cancelled">Cancelled</option>
              </select>
            </div>
          </div>

          {/* Events List */}
          <div className="flex-1 overflow-auto">
            {sortedDates.length === 0 ? (
              <div className="p-8 text-center">
                <Calendar className="h-16 w-16 text-gray-300 mx-auto mb-6" />
                <p className="text-gray-600 font-semibold text-lg">No events found</p>
                <p className="text-gray-400 text-sm mt-2">
                  Try adjusting your filters or create a new event
                </p>
              </div>
            ) : (
              <div className="p-6 space-y-8">
                {sortedDates.map(date => {
                  const dateEvents = groupedEvents[date];
                  const dateObj = new Date(date);
                  const isToday = dateObj.toDateString() === new Date().toDateString();
                  const isTomorrow = dateObj.toDateString() === new Date(Date.now() + 86400000).toDateString();

                  return (
                    <div key={date}>
                      {/* Date Header */}
                      <div className="flex items-center space-x-3 mb-4">
                        <h3 className={`text-sm font-bold ${
                          isToday ? 'text-blue-600' : 'text-gray-900'
                        }`}>
                          {isToday ? 'Today' : isTomorrow ? 'Tomorrow' : dateObj.toLocaleDateString('en-US', {
                            weekday: 'short',
                            month: 'short',
                            day: 'numeric'
                          })}
                        </h3>
                        <div className="flex-1 h-px bg-gray-200"></div>
                        <span className="text-xs text-gray-500 bg-gray-100 px-3 py-1 rounded-full font-medium">
                          {dateEvents.length}
                        </span>
                      </div>

                      {/* Events */}
                      <div className="space-y-3">
                        {dateEvents.map(event => (
                          <div
                            key={event.id}
                            className="p-4 rounded-xl border border-gray-200 hover:border-gray-300 hover:shadow-lg transition-all cursor-pointer bg-white hover:bg-gray-50/80"
                            onClick={() => onEventClick(event)}
                          >
                            <div className="flex items-start space-x-3">
                              <div className="flex-shrink-0 mt-0.5">
                                {getEventIcon(event)}
                              </div>

                              <div className="flex-1 min-w-0">
                                <div className="flex items-center justify-between">
                                  <h4 className="text-sm font-medium text-gray-900 truncate">
                                    {event.title}
                                  </h4>
                                  <div className="flex-shrink-0 ml-2">
                                    {getStatusIcon(event.status)}
                                  </div>
                                </div>

                                <div className="mt-1 flex items-center text-xs text-gray-500">
                                  <Clock className="h-3 w-3 mr-1" />
                                  {new Date(event.startDatetime).toLocaleTimeString('en-US', {
                                    hour: 'numeric',
                                    minute: '2-digit'
                                  })}
                                  {!event.isAllDay && (
                                    <>
                                      {' - '}
                                      {new Date(event.endDatetime).toLocaleTimeString('en-US', {
                                        hour: 'numeric',
                                        minute: '2-digit'
                                      })}
                                    </>
                                  )}
                                </div>

                                {event.location && (
                                  <div className="mt-1 flex items-center text-xs text-gray-500">
                                    <MapPin className="h-3 w-3 mr-1" />
                                    <span className="truncate">{event.location}</span>
                                  </div>
                                )}

                                {event.attendees.length > 0 && (
                                  <div className="mt-1 flex items-center text-xs text-gray-500">
                                    <Users className="h-3 w-3 mr-1" />
                                    {event.attendees.length} attendee{event.attendees.length !== 1 ? 's' : ''}
                                  </div>
                                )}

                                {event.description && (
                                  <p className="mt-2 text-xs text-gray-600 line-clamp-2">
                                    {event.description}
                                  </p>
                                )}
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* Quick Stats */}
          <div className="p-6 border-t border-gray-100 bg-gradient-to-br from-gray-50 to-gray-100/50">
            <div className="grid grid-cols-3 gap-4 text-center">
              <div className="bg-white rounded-xl p-4 shadow-sm">
                <div className="text-2xl font-bold text-gray-900">
                  {events.length}
                </div>
                <div className="text-xs text-gray-500 font-medium uppercase tracking-wide">Total</div>
              </div>
              <div className="bg-white rounded-xl p-4 shadow-sm">
                <div className="text-2xl font-bold text-green-600">
                  {events.filter(e => e.status === 'confirmed').length}
                </div>
                <div className="text-xs text-gray-500 font-medium uppercase tracking-wide">Confirmed</div>
              </div>
              <div className="bg-white rounded-xl p-4 shadow-sm">
                <div className="text-2xl font-bold text-yellow-600">
                  {events.filter(e => e.status === 'tentative').length}
                </div>
                <div className="text-xs text-gray-500 font-medium uppercase tracking-wide">Pending</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}