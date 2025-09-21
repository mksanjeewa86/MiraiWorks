'use client';

import React, { useState, useEffect, useCallback } from 'react';
import AppLayout from '@/components/layout/AppLayout';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import CalendarView from '@/components/calendar/CalendarView';
import CalendarSidebar from '@/components/calendar/CalendarSidebar';
import EventModal from '@/components/calendar/EventModal';
import { Grid, List, Clock, Menu, Plus } from 'lucide-react';
import { calendarApi } from '@/api/calendar';
import { interviewsApi } from '@/api/interviews';
import { useAuth } from '@/contexts/AuthContext';
import type { CalendarEvent, Interview } from '@/types/interview';

function CalendarPageContent() {
  const { user } = useAuth();
  const [currentDate, setCurrentDate] = useState(new Date());
  const [viewType, setViewType] = useState<'month' | 'week' | 'day'>('month');
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [selectedEvent, setSelectedEvent] = useState<CalendarEvent | null>(null);
  const [selectedDate, setSelectedDate] = useState<Date | null>(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [isCreateMode, setIsCreateMode] = useState(false);
  const [filters, setFilters] = useState({
    eventType: 'all',
    status: 'all',
    search: ''
  });

  // Load events
  const loadEvents = useCallback(async () => {
    try {
      setLoading(true);

      // Get date range based on current view
      const startDate = new Date(currentDate);
      const endDate = new Date(currentDate);

      if (viewType === 'month') {
        startDate.setDate(1);
        endDate.setMonth(endDate.getMonth() + 1, 0);
      } else if (viewType === 'week') {
        const startOfWeek = currentDate.getDate() - currentDate.getDay();
        startDate.setDate(startOfWeek);
        endDate.setDate(startOfWeek + 6);
      } else {
        endDate.setDate(endDate.getDate());
      }

      let allEvents: CalendarEvent[] = [];

      try {
        // Load calendar events
        const calendarResponse = await calendarApi.getEvents({
          startDate: startDate.toISOString(),
          endDate: endDate.toISOString()
        });

        // Robust response format handling
        if (calendarResponse?.data) {
          if (Array.isArray(calendarResponse.data)) {
            allEvents = [...calendarResponse.data];
          } else if (calendarResponse.data && typeof calendarResponse.data === 'object') {
            // Handle object response with nested data
            const dataObj = calendarResponse.data as unknown as Record<string, unknown>;
            if (Array.isArray(dataObj.items)) {
              allEvents = [...dataObj.items];
            } else if (Array.isArray(dataObj.events)) {
              allEvents = [...dataObj.events];
            } else if (Array.isArray(dataObj.data)) {
              allEvents = [...dataObj.data];
            } else {
              console.warn('Calendar API returned unexpected format:', calendarResponse);
              allEvents = [];
            }
          } else {
            console.warn('Calendar API data is not in expected format:', calendarResponse);
            allEvents = [];
          }
        } else {
          console.warn('Calendar API returned no data:', calendarResponse);
          allEvents = [];
        }
      } catch (error) {
        console.warn('Failed to load calendar events:', error);
        allEvents = [];
      }

      try {
        // Load interview events as well (only if user is available and has company_id)
        if (!user || !user.company_id) {
          // Skip interviews if user data is not available
          console.warn('User data not available for loading interviews');
        } else {
          const interviewResponse = await interviewsApi.getAll({
            recruiter_id: user.id,
            employer_company_id: user.company_id
          });
          let interviews: Interview[] = [];

          // Robust response format handling for interviews
          if (interviewResponse?.data) {
            if (Array.isArray(interviewResponse.data)) {
              interviews = interviewResponse.data;
            } else if (interviewResponse.data && typeof interviewResponse.data === 'object') {
              // Handle object response with nested data
              const dataObj = interviewResponse.data as unknown as Record<string, unknown>;
              if (Array.isArray(dataObj.items)) {
                interviews = dataObj.items;
              } else if (Array.isArray(dataObj.interviews)) {
                interviews = dataObj.interviews;
              } else if (Array.isArray(dataObj.data)) {
                interviews = dataObj.data;
              } else {
                console.warn('Interviews API returned unexpected format:', interviewResponse);
                interviews = [];
              }
            } else {
              console.warn('Interviews API data is not in expected format:', interviewResponse);
              interviews = [];
            }
          } else {
            console.warn('Interviews API returned no data:', interviewResponse);
            interviews = [];
          }

          // Safely process interviews array
          if (Array.isArray(interviews) && interviews.length > 0) {
            const interviewEvents: CalendarEvent[] = interviews
              .filter(interview => interview && interview.scheduled_start)
              .map(interview => ({
                id: `interview-${interview.id}`,
                title: `Interview: ${interview.position_title || interview.title || 'Untitled Interview'}`,
                description: interview.description || '',
                location: interview.location || interview.meeting_url || '',
                startDatetime: interview.scheduled_start!,
                endDatetime: interview.scheduled_end || new Date(new Date(interview.scheduled_start!).getTime() + (interview.duration_minutes || 60) * 60000).toISOString(),
                timezone: interview.timezone || 'UTC',
                isAllDay: false,
                isRecurring: false,
                organizerEmail: interview.recruiter?.email || '',
                attendees: [interview.candidate?.email, interview.recruiter?.email].filter(Boolean) as string[],
                status: interview.status || 'tentative',
                createdAt: interview.created_at || new Date().toISOString(),
                updatedAt: interview.updated_at || new Date().toISOString()
              }));
            allEvents = [...allEvents, ...interviewEvents];
          }
        }
      } catch (error) {
        console.warn('Failed to load interview events:', error);
      }

      // Ensure allEvents is always an array
      if (!Array.isArray(allEvents)) {
        console.warn('allEvents is not an array, resetting to empty array');
        allEvents = [];
      }

      setEvents(allEvents);
    } catch (error) {
      console.error('Failed to load calendar events:', error);
      setEvents([]);
    } finally {
      setLoading(false);
    }
  }, [currentDate, viewType]);

  useEffect(() => {
    loadEvents();
  }, [currentDate, viewType, loadEvents]);

  // Filter events based on current filters
  const filteredEvents = Array.isArray(events) ? events.filter(event => {
    // Ensure event has required properties
    if (!event || !event.title || !event.id) {
      return false;
    }

    // Search filter
    if (filters.search) {
      const searchLower = filters.search.toLowerCase();
      const titleMatch = event.title.toLowerCase().includes(searchLower);
      const descriptionMatch = event.description?.toLowerCase().includes(searchLower) || false;
      if (!titleMatch && !descriptionMatch) {
        return false;
      }
    }

    // Event type filter
    if (filters.eventType !== 'all') {
      const eventId = event.id ? event.id.toString() : '';
      const eventTitle = event.title ? event.title.toLowerCase() : '';

      const eventType = eventId.startsWith('interview-') ? 'interview' :
                        eventTitle.includes('meeting') ? 'meeting' :
                        eventTitle.includes('call') ? 'call' : 'other';

      if (eventType !== filters.eventType && filters.eventType !== 'other') {
        return false;
      }
    }

    // Status filter
    if (filters.status !== 'all' && event.status !== filters.status) {
      return false;
    }

    return true;
  }) : [];

  const handleEventClick = (event: CalendarEvent) => {
    setSelectedEvent(event);
    setSelectedDate(null);
    setIsCreateMode(false);
    setModalOpen(true);
  };

  const handleDateSelect = (date: Date) => {
    setSelectedDate(date);
    setSelectedEvent(null);
    setIsCreateMode(true);
    setModalOpen(true);
  };

  const handleSaveEvent = async (eventData: Partial<CalendarEvent>) => {
    try {
      if (isCreateMode) {
        // Create new event
        await calendarApi.createEvent(eventData);
      } else if (selectedEvent && selectedEvent.id && /^\d+$/.test(selectedEvent.id.toString())) {
        // Update existing calendar event (only for numeric IDs - real calendar events)
        await calendarApi.updateEvent(Number(selectedEvent.id), eventData);
      }

      // Reload events to show the changes
      await loadEvents();
      setModalOpen(false);
    } catch (error) {
      console.error('Error saving event:', error);
      throw error; // Let the modal handle the error display
    }
  };

  const handleDeleteEvent = async (event: CalendarEvent) => {
    try {
      if (event.id && /^\d+$/.test(event.id.toString())) {
        // Delete calendar event (only for numeric IDs - real calendar events)
        await calendarApi.deleteEvent(Number(event.id));

        // Reload events to show the changes
        await loadEvents();
        setModalOpen(false);
      } else {
        throw new Error('This event cannot be deleted from the calendar view');
      }
    } catch (error) {
      console.error('Error deleting event:', error);
      throw error; // Let the modal handle the error display
    }
  };

  const getUserRole = () => {
    const userRole = localStorage.getItem('userRole');
    return userRole || 'candidate';
  };

  return (
    <AppLayout>
      <div className="flex flex-col h-full bg-white">
        {/* Header */}
        <div className="bg-white border-b border-gray-100">
          <div className="px-6 py-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-6">
                <div className="flex items-center space-x-3">
                  <h1 className="text-3xl font-semibold text-gray-900">Calendar</h1>
                  <button
                    onClick={() => setSidebarOpen(true)}
                    className="lg:hidden p-2 rounded-xl text-gray-500 hover:bg-gray-100 hover:text-gray-700 transition-colors"
                  >
                    <Menu className="h-5 w-5" />
                  </button>
                </div>

                {/* Current Date Display */}
                <div className="text-sm text-gray-500 bg-gray-50 px-3 py-1 rounded-full">
                  {new Date().toLocaleDateString('en-US', {
                    weekday: 'long',
                    month: 'long',
                    day: 'numeric',
                    year: 'numeric'
                  })}
                </div>
              </div>

              <div className="flex items-center space-x-3">
                {/* View Type Selector */}
                <div className="flex bg-gray-50 rounded-xl p-1 border border-gray-200">
                  <button
                    onClick={() => setViewType('month')}
                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                      viewType === 'month'
                        ? 'bg-white text-gray-900 shadow-sm border border-gray-200'
                        : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                    }`}
                  >
                    <Grid className="h-4 w-4 mr-2 inline" />
                    Month
                  </button>
                  <button
                    onClick={() => setViewType('week')}
                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                      viewType === 'week'
                        ? 'bg-white text-gray-900 shadow-sm border border-gray-200'
                        : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                    }`}
                  >
                    <List className="h-4 w-4 mr-2 inline" />
                    Week
                  </button>
                  <button
                    onClick={() => setViewType('day')}
                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                      viewType === 'day'
                        ? 'bg-white text-gray-900 shadow-sm border border-gray-200'
                        : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                    }`}
                  >
                    <Clock className="h-4 w-4 mr-2 inline" />
                    Day
                  </button>
                </div>

                {/* Create Event Button */}
                <button
                  onClick={() => handleDateSelect(new Date())}
                  className="inline-flex items-center px-5 py-2.5 bg-gradient-to-r from-blue-600 to-blue-700 text-white text-sm font-medium rounded-xl hover:from-blue-700 hover:to-blue-800 transition-all duration-200 shadow-sm hover:shadow-md"
                >
                  <Plus className="h-4 w-4 mr-2" />
                  New Event
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="flex flex-1 overflow-hidden bg-white relative">
          {/* Left Sidebar - Hidden on mobile */}
          <div className="hidden lg:flex lg:w-80 lg:flex-shrink-0 bg-gray-50 border-r border-gray-200">
            <CalendarSidebar
              isOpen={true}
              onClose={() => {}}
              events={filteredEvents}
              onEventClick={handleEventClick}
              filters={filters}
              onFiltersChange={setFilters}
              userRole={getUserRole()}
            />
          </div>

          {/* Calendar View */}
          <div className="flex-1 flex flex-col bg-white min-w-0">
            <CalendarView
              currentDate={currentDate}
              onDateChange={setCurrentDate}
              viewType={viewType}
              events={filteredEvents}
              onDateSelect={handleDateSelect}
              onEventClick={handleEventClick}
              loading={loading}
              canCreateEvents={true}
            />
          </div>

          {/* Mobile Sidebar Overlay - Only show on mobile when open */}
          {sidebarOpen && (
            <div className="lg:hidden">
              <CalendarSidebar
                isOpen={sidebarOpen}
                onClose={() => setSidebarOpen(false)}
                events={filteredEvents}
                onEventClick={handleEventClick}
                filters={filters}
                onFiltersChange={setFilters}
                userRole={getUserRole()}
              />
            </div>
          )}
        </div>

        {/* Event Modal */}
        <EventModal
          isOpen={modalOpen}
          onClose={() => setModalOpen(false)}
          event={selectedEvent}
          selectedDate={selectedDate}
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
