'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  X,
  MapPin,
  Users,
  Video,
  Phone,
  Trash2,
  Save,
  AlertCircle
} from 'lucide-react';
import type { CalendarEvent } from '@/types/interview';
import type { EventModalProps, EventFormData } from '@/types/components';

export default function EventModal({
  isOpen,
  onClose,
  event,
  selectedDate,
  isCreateMode,
  onSave,
  onDelete
}: EventModalProps) {
  const [formData, setFormData] = useState<EventFormData>({
    title: '',
    description: '',
    location: '',
    startDatetime: '',
    endDatetime: '',
    isAllDay: false,
    attendees: [],
    status: 'tentative',
    timezone: 'UTC'
  });

  const [attendeeInput, setAttendeeInput] = useState('');
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);

  const eventId = event?.id ?? '';
  const isTodoEvent = eventId.startsWith('todo-');
  const isInterviewEvent = eventId.startsWith('interview-');
  const isCalendarEvent = /^\d+$/.test(eventId);
  const canDeleteEvent = !isCreateMode && !!event && (isCalendarEvent || isTodoEvent);
  const deleteHelperMessage = !isCreateMode && event && !canDeleteEvent
    ? (isInterviewEvent
        ? 'Interviews must be cancelled from the interview workflow.'
        : 'This event cannot be deleted from this view.')
    : null;

  // Safe date parsing helper
  const safeParseDate = (dateString: string | null | undefined): Date | null => {
    if (!dateString) return null;
    const date = new Date(dateString);
    return isNaN(date.getTime()) ? null : date;
  };

  // Safe date to datetime-local format
  const safeDateToLocalString = useCallback((dateString: string | null | undefined, fallback: Date = new Date()): string => {
    const date = safeParseDate(dateString);
    return (date || fallback).toISOString().slice(0, 16);
  }, []);

  // Initialize form data
  useEffect(() => {
    if (isOpen) {
      if (isCreateMode && selectedDate) {
        const start = new Date(selectedDate);
        const end = new Date(selectedDate);
        end.setHours(start.getHours() + 1);

        setFormData({
          title: '',
          description: '',
          location: '',
          startDatetime: start.toISOString().slice(0, 16),
          endDatetime: end.toISOString().slice(0, 16),
          isAllDay: false,
          attendees: [],
          status: 'tentative',
          timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC'
        });
      } else if (event) {
        const currentTime = new Date();
        const oneHourLater = new Date(currentTime.getTime() + 60 * 60 * 1000);

        setFormData({
          title: event.title,
          description: event.description || '',
          location: event.location || '',
          startDatetime: safeDateToLocalString(event.startDatetime, currentTime),
          endDatetime: safeDateToLocalString(event.endDatetime, oneHourLater),
          isAllDay: event.isAllDay,
          attendees: event.attendees,
          status: event.status || 'tentative',
          timezone: event.timezone || 'UTC'
        });
      }
      setErrors({});
      setAttendeeInput('');
    }
  }, [isOpen, isCreateMode, event, selectedDate, safeDateToLocalString]);

  // Form validation
  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.title.trim()) {
      newErrors.title = 'Title is required';
    }

    if (!formData.startDatetime) {
      newErrors.startDatetime = 'Start time is required';
    }

    if (!formData.endDatetime) {
      newErrors.endDatetime = 'End time is required';
    }

    if (formData.startDatetime && formData.endDatetime) {
      const start = safeParseDate(formData.startDatetime);
      const end = safeParseDate(formData.endDatetime);
      if (start && end && end <= start) {
        newErrors.endDatetime = 'End time must be after start time';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setLoading(true);
    try {
      const eventData: Partial<CalendarEvent> = {
        title: formData.title.trim(),
        description: formData.description.trim() || undefined,
        location: formData.location.trim() || undefined,
        startDatetime: formData.startDatetime,
        endDatetime: formData.endDatetime,
        isAllDay: formData.isAllDay,
        attendees: formData.attendees,
        status: formData.status,
        timezone: formData.timezone,
        organizerEmail: undefined, // Will be set by backend
        isRecurring: false,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      };

      await onSave(eventData);
    } catch (error) {
      console.error('Error saving event:', error);
    } finally {
      setLoading(false);
    }
  };

  // Handle delete
  const handleDelete = async () => {
    if (event && window.confirm('Are you sure you want to delete this event?')) {
      setLoading(true);
      try {
        await onDelete(event);
      } catch (error) {
        console.error('Error deleting event:', error);
      } finally {
        setLoading(false);
      }
    }
  };

  // Add attendee
  const addAttendee = () => {
    const email = attendeeInput.trim();
    if (email && !formData.attendees.includes(email)) {
      setFormData(prev => ({
        ...prev,
        attendees: [...prev.attendees, email]
      }));
      setAttendeeInput('');
    }
  };

  // Remove attendee
  const removeAttendee = (email: string) => {
    setFormData(prev => ({
      ...prev,
      attendees: prev.attendees.filter(a => a !== email)
    }));
  };

  // Quick event templates
  const eventTemplates = [
    { name: 'Interview', icon: Video, duration: 60, location: 'Video Call' },
    { name: 'Phone Screening', icon: Phone, duration: 30, location: 'Phone' },
    { name: 'Team Meeting', icon: Users, duration: 60, location: 'Conference Room' },
    { name: 'One-on-One', icon: Users, duration: 30, location: 'Office' }
  ];

  // Apply template
  const applyTemplate = (template: typeof eventTemplates[0]) => {
    const startSource = formData.startDatetime || (selectedDate ? selectedDate.toISOString() : null);
    const start = safeParseDate(startSource) || new Date();
    const end = new Date(start);
    end.setMinutes(start.getMinutes() + template.duration);

    setFormData(prev => ({
      ...prev,
      title: template.name,
      location: template.location,
      endDatetime: end.toISOString().slice(0, 16)
    }));
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen p-4">
        <div className="fixed inset-0 bg-black bg-opacity-50" onClick={onClose} />

        <div className="relative bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900">
              {isCreateMode ? 'Create Event' : 'Edit Event'}
            </h2>
            <button
              onClick={onClose}
              className="p-2 rounded-lg text-gray-400 hover:text-gray-600"
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          <form onSubmit={handleSubmit}>
            <div className="p-6 space-y-6">
              {/* Quick Templates (Create mode only) */}
              {isCreateMode && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-3">
                    Quick Templates
                  </label>
                  <div className="grid grid-cols-2 gap-2">
                    {eventTemplates.map((template, index) => (
                      <button
                        key={index}
                        type="button"
                        onClick={() => applyTemplate(template)}
                        className="flex items-center space-x-2 p-3 border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-colors"
                      >
                        <template.icon className="h-4 w-4 text-gray-600" />
                        <span className="text-sm font-medium text-gray-700">{template.name}</span>
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Title */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Event Title *
                </label>
                <input
                  type="text"
                  value={formData.title}
                  onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
                  className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                    errors.title ? 'border-red-300' : 'border-gray-300'
                  }`}
                  placeholder="Enter event title"
                />
                {errors.title && (
                  <p className="mt-1 text-sm text-red-600 flex items-center">
                    <AlertCircle className="h-4 w-4 mr-1" />
                    {errors.title}
                  </p>
                )}
              </div>

              {/* Date and Time */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Start Time *
                  </label>
                  <input
                    type="datetime-local"
                    value={formData.startDatetime}
                    onChange={(e) => setFormData(prev => ({ ...prev, startDatetime: e.target.value }))}
                    className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                      errors.startDatetime ? 'border-red-300' : 'border-gray-300'
                    }`}
                  />
                  {errors.startDatetime && (
                    <p className="mt-1 text-sm text-red-600">{errors.startDatetime}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    End Time *
                  </label>
                  <input
                    type="datetime-local"
                    value={formData.endDatetime}
                    onChange={(e) => setFormData(prev => ({ ...prev, endDatetime: e.target.value }))}
                    className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                      errors.endDatetime ? 'border-red-300' : 'border-gray-300'
                    }`}
                  />
                  {errors.endDatetime && (
                    <p className="mt-1 text-sm text-red-600">{errors.endDatetime}</p>
                  )}
                </div>
              </div>

              {/* All Day Toggle */}
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="allDay"
                  checked={formData.isAllDay}
                  onChange={(e) => setFormData(prev => ({ ...prev, isAllDay: e.target.checked }))}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label htmlFor="allDay" className="ml-2 text-sm text-gray-700">
                  All day event
                </label>
              </div>

              {/* Location */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Location
                </label>
                <div className="relative">
                  <MapPin className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                  <input
                    type="text"
                    value={formData.location}
                    onChange={(e) => setFormData(prev => ({ ...prev, location: e.target.value }))}
                    className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Enter location or video link"
                  />
                </div>
              </div>

              {/* Description */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Description
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Enter event description"
                />
              </div>

              {/* Status */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Status
                </label>
                <select
                  value={formData.status}
                  onChange={(e) => setFormData(prev => ({ ...prev, status: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="tentative">Tentative</option>
                  <option value="confirmed">Confirmed</option>
                  <option value="cancelled">Cancelled</option>
                </select>
              </div>

              {/* Attendees */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Attendees
                </label>
                <div className="space-y-2">
                  <div className="flex space-x-2">
                    <input
                      type="email"
                      value={attendeeInput}
                      onChange={(e) => setAttendeeInput(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addAttendee())}
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="Enter email address"
                    />
                    <button
                      type="button"
                      onClick={addAttendee}
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                    >
                      Add
                    </button>
                  </div>
                  {formData.attendees.length > 0 && (
                    <div className="space-y-1">
                      {formData.attendees.map((email, index) => (
                        <div key={index} className="flex items-center justify-between bg-gray-50 px-3 py-2 rounded-lg">
                          <span className="text-sm text-gray-700">{email}</span>
                          <button
                            type="button"
                            onClick={() => removeAttendee(email)}
                            className="text-red-600 hover:text-red-800"
                          >
                            <X className="h-4 w-4" />
                          </button>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Footer */}
            <div className="flex items-center justify-between p-6 border-t border-gray-200 bg-gray-50">
              <div className="flex flex-col">
                {!isCreateMode && event && canDeleteEvent && (
                  <button
                    type="button"
                    onClick={handleDelete}
                    disabled={loading}
                    className="inline-flex items-center px-4 py-2 text-red-700 bg-red-100 border border-red-300 rounded-lg hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 disabled:opacity-50"
                  >
                    <Trash2 className="h-4 w-4 mr-2" />
                    Delete Event
                  </button>
                )}
                {!isCreateMode && event && deleteHelperMessage && (
                  <p className="mt-2 text-sm text-gray-500">{deleteHelperMessage}</p>
                )}
              </div>

              <div className="flex space-x-3">
                <button
                  type="button"
                  onClick={onClose}
                  className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50"
                >
                  {loading ? (
                    <div className="h-4 w-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                  ) : (
                    <Save className="h-4 w-4 mr-2" />
                  )}
                  {isCreateMode ? 'Create Event' : 'Save Changes'}
                </button>
              </div>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}