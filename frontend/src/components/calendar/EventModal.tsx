'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  CalendarClock,
  CalendarRange,
  MapPin,
  Users,
  Video,
  Phone,
  Trash2,
  Save,
  X,
  UserPlus,
} from 'lucide-react';
import type { CalendarEvent, AttendeeInfo } from '@/types/interview';
import type { EventModalProps, EventFormData } from '@/types/components';
import type { ConnectedUser } from '@/types/user';
import { calendarApi } from '@/api/calendar';
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  ConfirmDialog,
} from '@/components/ui';
import { Button } from '@/components/ui';
import { Input } from '@/components/ui';
import { Textarea } from '@/components/ui';
import { Checkbox } from '@/components/ui';
import { userConnectionsApi } from '@/api/userConnections';

export default function EventModal({
  isOpen,
  onClose,
  event,
  selectedDate,
  selectedRange,
  isCreateMode,
  onSave,
  onDelete,
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
    timezone: 'UTC',
  });

  const [attendeeInput, setAttendeeInput] = useState('');
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [connectedUsers, setConnectedUsers] = useState<ConnectedUser[]>([]);
  const [showAddAttendee, setShowAddAttendee] = useState(false);
  const [selectedUserId, setSelectedUserId] = useState<number | null>(null);
  const [attendeeInfoMap, setAttendeeInfoMap] = useState<Map<string, AttendeeInfo>>(new Map());
  const [removeAttendeeConfirm, setRemoveAttendeeConfirm] = useState<{
    isOpen: boolean;
    email: string;
    name: string;
  }>({ isOpen: false, email: '', name: '' });
  const [removingAttendee, setRemovingAttendee] = useState(false);

  const eventId = event?.id ? String(event.id) : '';
  const isTodoEvent = eventId.startsWith('todo-');
  const isInterviewEvent = eventId.startsWith('interview-');
  // Calendar events can be pure numeric IDs like "12" or prefixed like "event-12"
  const isCalendarEvent = /^\d+$/.test(eventId) || /^event-\d+$/.test(eventId);
  const canDeleteEvent = !isCreateMode && !!event && (isCalendarEvent || isTodoEvent);

  const handleClose = () => {
    if (!loading) {
      onClose();
    }
  };

  const safeParseDate = (dateString: string | null | undefined): Date | null => {
    if (!dateString) return null;
    const date = new Date(dateString);
    return Number.isNaN(date.getTime()) ? null : date;
  };

  // Convert a Date object to local datetime string format for datetime-local input
  const toLocalDatetimeString = (date: Date): string => {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    return `${year}-${month}-${day}T${hours}:${minutes}`;
  };

  // Fetch connected users on mount
  useEffect(() => {
    const fetchConnectedUsers = async () => {
      const result = await userConnectionsApi.getMyConnections();
      if (result.success && result.data) {
        setConnectedUsers(result.data);
      }
    };
    if (isOpen) {
      fetchConnectedUsers();
    }
  }, [isOpen]);

  // Convert a Date object to local date string format for date input
  const toLocalDateString = (date: Date): string => {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  };

  const safeDateToLocalString = useCallback(
    (dateString: string | null | undefined, fallback: Date = new Date()): string => {
      const date = safeParseDate(dateString);
      return toLocalDatetimeString(date || fallback);
    },
    []
  );

  useEffect(() => {
    if (!isOpen) {
      return;
    }

    if (isCreateMode) {
      // Use selectedRange.start or selectedDate if available, otherwise current time
      let startTime: Date;

      if (selectedRange?.start) {
        startTime = new Date(selectedRange.start);
      } else if (selectedDate) {
        startTime = new Date(selectedDate);
      } else {
        startTime = new Date();
      }

      const endTime = selectedRange?.end
        ? new Date(selectedRange.end)
        : new Date(startTime.getTime() + 60 * 60 * 1000);

      setFormData({
        title: '',
        description: '',
        location: '',
        startDatetime: toLocalDatetimeString(startTime),
        endDatetime: toLocalDatetimeString(endTime),
        isAllDay: selectedRange?.allDay || false,
        attendees: [],
        status: 'tentative',
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC',
      });
    } else if (event) {
      const currentTime = new Date();
      const oneHourLater = new Date(currentTime.getTime() + 60 * 60 * 1000);

      // Normalize attendees - convert AttendeeInfo[] to string[] for form
      let normalizedAttendees: string[] = [];
      const infoMap = new Map<string, AttendeeInfo>();

      if (event.attendees && event.attendees.length > 0) {
        if (typeof event.attendees[0] === 'string') {
          normalizedAttendees = event.attendees as string[];
        } else {
          const attendeeInfoList = event.attendees as AttendeeInfo[];
          normalizedAttendees = attendeeInfoList.map((a) => a.email);
          attendeeInfoList.forEach((a) => {
            infoMap.set(a.email, a);
          });
        }
      }

      setAttendeeInfoMap(infoMap);
      setFormData({
        title: event.title,
        description: event.description || '',
        location: event.location || '',
        startDatetime: safeDateToLocalString(event.startDatetime, currentTime),
        endDatetime: safeDateToLocalString(event.endDatetime, oneHourLater),
        isAllDay: event.isAllDay ?? false,
        attendees: normalizedAttendees,
        status: event.status || 'tentative',
        timezone: event.timezone || 'UTC',
      });
    }

    setErrors({});
    setAttendeeInput('');
  }, [isOpen, isCreateMode, event, selectedDate, selectedRange, safeDateToLocalString]);

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.title.trim()) {
      newErrors.title = 'Title is required';
    }

    if (!formData.startDatetime) {
      newErrors.startDatetime = formData.isAllDay ? 'Start date is required' : 'Start time is required';
    }

    // End datetime is optional for all-day events
    if (!formData.isAllDay && !formData.endDatetime) {
      newErrors.endDatetime = 'End time is required';
    }

    if (formData.startDatetime && formData.endDatetime) {
      const start = safeParseDate(formData.startDatetime);
      const end = safeParseDate(formData.endDatetime);
      if (start && end && end <= start) {
        newErrors.endDatetime = formData.isAllDay ? 'End date must be after start date' : 'End time must be after start time';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();

    if (!validateForm()) {
      return;
    }

    setLoading(true);
    try {
      const startDate = new Date(formData.startDatetime);
      // For all-day events without end date, use start date as end date
      const endDate = formData.endDatetime
        ? new Date(formData.endDatetime)
        : new Date(startDate);

      const eventData: Partial<CalendarEvent> = {
        title: formData.title.trim(),
        description: formData.description.trim() || undefined,
        location: formData.location.trim() || undefined,
        startDatetime: startDate.toISOString(),
        endDatetime: endDate.toISOString(),
        isAllDay: formData.isAllDay,
        attendees: formData.attendees,
        status: formData.status,
        timezone: formData.timezone,
        organizerEmail: undefined,
        isRecurring: false,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };

      await onSave(eventData);
      setLoading(false);
    } catch (error) {
      console.error('Error saving event:', error);
      setLoading(false);
    }
  };

  const handleDelete = () => {
    setShowDeleteConfirm(true);
  };

  const confirmDelete = async () => {
    if (!event) return;

    setDeleting(true);
    try {
      await onDelete(event);
      setShowDeleteConfirm(false);
    } catch (error) {
      console.error('Error deleting event:', error);
    } finally {
      setDeleting(false);
    }
  };

  const addAttendee = () => {
    const email = attendeeInput.trim();
    if (email && !formData.attendees.includes(email)) {
      setFormData((prev) => ({
        ...prev,
        attendees: [...prev.attendees, email],
      }));
      setAttendeeInput('');
    }
  };

  const handleRemoveAttendeeClick = (email: string, name: string) => {
    setRemoveAttendeeConfirm({ isOpen: true, email, name });
  };

  const confirmRemoveAttendee = async () => {
    if (!removeAttendeeConfirm.email) return;

    const updatedAttendees = formData.attendees.filter(
      (attendee) => attendee !== removeAttendeeConfirm.email
    );

    console.log('[EventModal] Removing attendee:', removeAttendeeConfirm.email);
    console.log('[EventModal] Updated attendees list:', updatedAttendees);

    // Update local state immediately for better UX
    setFormData((prev) => ({
      ...prev,
      attendees: updatedAttendees,
    }));

    // If editing an existing event, immediately update the database WITHOUT closing the modal
    if (!isCreateMode && event) {
      setRemovingAttendee(true);
      try {
        const eventIdStr = String(event.id);
        const numericId = eventIdStr.replace(/^event-/, '');

        // Directly call the API to update just the attendees
        const eventDataToSave = {
          ...formData,
          attendees: updatedAttendees,
        };

        console.log('[EventModal] Updating event attendees via API, ID:', numericId);
        await calendarApi.updateEvent(Number(numericId), eventDataToSave);
        console.log('[EventModal] Attendee removed successfully');

        // Also remove from attendeeInfoMap if it exists
        const newInfoMap = new Map(attendeeInfoMap);
        newInfoMap.delete(removeAttendeeConfirm.email);
        setAttendeeInfoMap(newInfoMap);

      } catch (error) {
        console.error('[EventModal] Failed to remove attendee', error);
        // Revert the change on error
        setFormData((prev) => ({
          ...prev,
          attendees: formData.attendees,
        }));
      } finally {
        setRemovingAttendee(false);
      }
    }

    setRemoveAttendeeConfirm({ isOpen: false, email: '', name: '' });
  };

  const addAttendeeFromUser = () => {
    if (selectedUserId) {
      const user = connectedUsers.find(u => u.id === selectedUserId);
      if (user && !formData.attendees.includes(user.email)) {
        setFormData((prev) => ({
          ...prev,
          attendees: [...prev.attendees, user.email],
        }));
        setSelectedUserId(null);
        setShowAddAttendee(false);
      }
    }
  };

  const eventTemplates = [
    { name: 'Interview', icon: Video, duration: 60, location: 'Video Call' },
    { name: 'Phone Screening', icon: Phone, duration: 30, location: 'Phone' },
    { name: 'Team Meeting', icon: Users, duration: 60, location: 'Conference Room' },
    { name: 'One-on-One', icon: Users, duration: 30, location: 'Office' },
  ] as const;

  const applyTemplate = (template: (typeof eventTemplates)[number]) => {
    const startSource =
      formData.startDatetime || (selectedDate ? selectedDate.toISOString() : null);
    const start = safeParseDate(startSource) || new Date();
    const end = new Date(start);
    end.setMinutes(start.getMinutes() + template.duration);

    setFormData((prev) => ({
      ...prev,
      title: template.name,
      location: template.location,
      endDatetime: toLocalDatetimeString(end),
    }));
  };

  return (
    <Dialog open={isOpen} onOpenChange={(open) => (!open ? handleClose() : undefined)}>
      <DialogContent
        closeButton={false}
        className="flex flex-col h-[90vh] max-h-[90vh] w-full max-w-4xl md:max-w-3xl overflow-hidden rounded-3xl border border-slate-200 bg-white text-slate-900 shadow-[0_30px_80px_-20px_rgba(15,23,42,0.2)]"
      >
        <DialogHeader className="flex-shrink-0 px-6 pt-6">
          <div className="flex items-start justify-between gap-4">
            <div className="space-y-3">
              <div className="flex items-center gap-3">
                <span className="inline-flex h-10 w-10 items-center justify-center rounded-full bg-blue-100 text-blue-600">
                  <CalendarClock className="h-5 w-5" />
                </span>
                <div>
                  <DialogTitle className="text-xl font-semibold text-slate-900">
                    {isCreateMode ? 'Create calendar event' : 'Edit calendar event'}
                  </DialogTitle>
                  <DialogDescription className="text-sm text-slate-500">
                    {isCreateMode
                      ? 'Schedule time on your calendar and tailor the invite before sending.'
                      : 'Update the timing, details, or attendees for this event.'}
                  </DialogDescription>
                </div>
              </div>
            </div>
            <DialogClose className="rounded-full border border-slate-200 p-2 text-slate-500 transition hover:bg-slate-100 hover:text-slate-700">
              <X className="h-4 w-4" />
            </DialogClose>
          </div>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="flex flex-1 flex-col min-h-0">
          <div className="flex-1 overflow-y-auto px-6 py-6 min-h-0">
            <div className="space-y-8">
              {isCreateMode && (
                <div className="rounded-xl border border-slate-200 bg-gradient-to-br from-slate-50 to-white p-3">
                  <div className="mb-2 flex items-center gap-2">
                    <div className="flex h-5 w-5 items-center justify-center rounded-md bg-blue-100">
                      <CalendarClock className="h-3 w-3 text-blue-600" />
                    </div>
                    <p className="text-xs font-semibold text-slate-900">Quick Templates</p>
                  </div>
                  <div className="grid gap-1.5 grid-cols-2 sm:grid-cols-4">
                    {eventTemplates.map((template) => (
                      <button
                        key={template.name}
                        type="button"
                        onClick={() => applyTemplate(template)}
                        className="group flex flex-col items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-2.5 py-2.5 text-center transition-all hover:border-blue-400 hover:bg-blue-50 hover:shadow-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      >
                        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-br from-blue-500 to-blue-600 text-white shadow-sm group-hover:scale-105 transition-transform">
                          <template.icon className="h-4 w-4" />
                        </div>
                        <div className="space-y-0">
                          <p className="text-[11px] font-semibold text-slate-900 leading-tight">{template.name}</p>
                          <p className="text-[10px] text-slate-500">{template.duration} min</p>
                        </div>
                      </button>
                    ))}
                  </div>
                </div>
              )}

              <div className="grid gap-6 rounded-2xl border border-slate-200 bg-slate-50 p-6">
                <Input
                  label="Event title"
                  placeholder="Give this event a clear name"
                  value={formData.title}
                  onChange={(event) =>
                    setFormData((prev) => ({ ...prev, title: event.target.value }))
                  }
                  required
                  error={errors.title}
                />

                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <label className="text-sm font-semibold text-slate-900">Date & Time</label>
                    <div className="flex items-center gap-2">
                      <Checkbox
                        id="all-day-event"
                        checked={formData.isAllDay ?? false}
                        onCheckedChange={(checked) => {
                          if (checked) {
                            // When checking "All day", set times to 00:00 and 23:59
                            const dateOnly = formData.startDatetime ? formData.startDatetime.split('T')[0] : '';
                            setFormData((prev) => ({
                              ...prev,
                              isAllDay: true,
                              startDatetime: dateOnly ? `${dateOnly}T00:00` : prev.startDatetime,
                              endDatetime: dateOnly ? `${dateOnly}T23:59` : prev.endDatetime,
                            }));
                          } else {
                            // When unchecking, set end time to 1 hour after start time
                            setFormData((prev) => {
                              // Parse the datetime-local string (YYYY-MM-DDTHH:mm)
                              const [datePart, timePart] = prev.startDatetime.split('T');
                              const [hours, minutes] = timePart.split(':').map(Number);

                              // Add 1 hour
                              let newHours = hours + 1;
                              let newDate = datePart;

                              // Handle day overflow
                              if (newHours >= 24) {
                                newHours = newHours % 24;
                                const date = new Date(datePart);
                                date.setDate(date.getDate() + 1);
                                newDate = date.toISOString().split('T')[0];
                              }

                              const endDatetimeString = `${newDate}T${String(newHours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}`;

                              return {
                                ...prev,
                                isAllDay: false,
                                endDatetime: endDatetimeString,
                              };
                            });
                          }
                        }}
                        disabled={loading}
                      />
                      <label htmlFor="all-day-event" className="text-xs font-medium text-slate-600 cursor-pointer">
                        All day
                      </label>
                    </div>
                  </div>

                  {formData.isAllDay ? (
                    <div className="grid gap-2 sm:grid-cols-2">
                      <div className="rounded-lg border border-slate-200 bg-white p-3">
                        <div className="flex items-center gap-3">
                          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-green-50">
                            <CalendarClock className="h-4 w-4 text-green-600" />
                          </div>
                          <div className="flex-1 min-w-0">
                            <p className="text-xs text-slate-500 mb-1">Starts</p>
                            <input
                              type="datetime-local"
                              value={formData.startDatetime}
                              onChange={(event) =>
                                setFormData((prev) => ({
                                  ...prev,
                                  startDatetime: event.target.value,
                                  endDatetime: event.target.value.split('T')[0] + 'T23:59',
                                }))
                              }
                              className="w-full border-none bg-transparent text-sm font-medium text-slate-900 focus:outline-none focus:ring-0 p-0"
                              required
                            />
                            {errors.startDatetime && (
                              <p className="text-xs text-red-500 mt-1">{errors.startDatetime}</p>
                            )}
                          </div>
                        </div>
                      </div>
                      <div className="rounded-lg border border-slate-200 bg-white p-3">
                        <div className="flex items-center gap-3">
                          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-red-50">
                            <CalendarRange className="h-4 w-4 text-red-600" />
                          </div>
                          <div className="flex-1 min-w-0">
                            <p className="text-xs text-slate-500 mb-1">Ends</p>
                            <input
                              type="datetime-local"
                              value={formData.endDatetime}
                              onChange={(event) =>
                                setFormData((prev) => ({ ...prev, endDatetime: event.target.value }))
                              }
                              className="w-full border-none bg-transparent text-sm font-medium text-slate-900 focus:outline-none focus:ring-0 p-0"
                              required
                            />
                            {errors.endDatetime && (
                              <p className="text-xs text-red-500 mt-1">{errors.endDatetime}</p>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="grid gap-2 sm:grid-cols-2">
                      <div className="rounded-lg border border-slate-200 bg-white p-3">
                        <div className="flex items-center gap-3">
                          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-green-50">
                            <CalendarClock className="h-4 w-4 text-green-600" />
                          </div>
                          <div className="flex-1 min-w-0">
                            <p className="text-xs text-slate-500 mb-1">Starts</p>
                            <input
                              type="datetime-local"
                              value={formData.startDatetime}
                              onChange={(event) =>
                                setFormData((prev) => ({ ...prev, startDatetime: event.target.value }))
                              }
                              className="w-full border-none bg-transparent text-sm font-medium text-slate-900 focus:outline-none focus:ring-0 p-0"
                              required
                            />
                            {errors.startDatetime && (
                              <p className="text-xs text-red-500 mt-1">{errors.startDatetime}</p>
                            )}
                          </div>
                        </div>
                      </div>
                      <div className="rounded-lg border border-slate-200 bg-white p-3">
                        <div className="flex items-center gap-3">
                          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-red-50">
                            <CalendarRange className="h-4 w-4 text-red-600" />
                          </div>
                          <div className="flex-1 min-w-0">
                            <p className="text-xs text-slate-500 mb-1">Ends</p>
                            <input
                              type="datetime-local"
                              value={formData.endDatetime}
                              onChange={(event) =>
                                setFormData((prev) => ({ ...prev, endDatetime: event.target.value }))
                              }
                              className="w-full border-none bg-transparent text-sm font-medium text-slate-900 focus:outline-none focus:ring-0 p-0"
                              required
                            />
                            {errors.endDatetime && (
                              <p className="text-xs text-red-500 mt-1">{errors.endDatetime}</p>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>

                <Input
                  label="Location"
                  placeholder="Add a meeting room, video link, or phone number"
                  value={formData.location}
                  onChange={(event) =>
                    setFormData((prev) => ({ ...prev, location: event.target.value }))
                  }
                  leftIcon={<MapPin className="h-4 w-4" />}
                />

                <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-700">Description</label>
                  <Textarea
                    rows={4}
                    placeholder="Share an agenda, preparation notes, or relevant links."
                    value={formData.description}
                    onChange={(event) =>
                      setFormData((prev) => ({ ...prev, description: event.target.value }))
                    }
                    className="border border-slate-300 bg-white text-slate-900 focus-visible:ring-blue-500"
                  />
                </div>

              </div>

              <div className="rounded-2xl border border-slate-200 bg-gradient-to-br from-slate-50 to-slate-100/50 p-6 shadow-sm">
                {/* Header */}
                <div className="flex items-center justify-between mb-6">
                  <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-blue-500 to-blue-600 shadow-lg shadow-blue-500/30">
                      <Users className="h-5 w-5 text-white" />
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold text-slate-900">Attendees</h3>
                      <p className="text-xs text-slate-500">{formData.attendees.length} {formData.attendees.length === 1 ? 'attendee' : 'attendees'}</p>
                    </div>
                  </div>
                  {!showAddAttendee && connectedUsers.length > 0 && (
                    <button
                      type="button"
                      onClick={() => setShowAddAttendee(true)}
                      className="group flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg hover:from-blue-600 hover:to-blue-700 shadow-md shadow-blue-500/30 transition-all duration-200 hover:shadow-lg hover:scale-105"
                    >
                      <UserPlus className="h-4 w-4" />
                      Add Attendee
                    </button>
                  )}
                </div>

                {/* Add attendee form */}
                {showAddAttendee && (
                  <div className="mb-4 rounded-xl border border-blue-200 bg-gradient-to-br from-blue-50 to-blue-50/50 p-4 shadow-sm">
                    <div className="flex items-center gap-2 mb-3">
                      <Users className="h-4 w-4 text-blue-600" />
                      <h4 className="text-sm font-semibold text-slate-900">Add Attendee</h4>
                    </div>
                    <div className="flex gap-2">
                      <select
                        value={selectedUserId || ''}
                        onChange={(e) => setSelectedUserId(Number(e.target.value))}
                        className="flex-1 px-3 py-2 text-sm border border-slate-300 rounded-lg bg-white text-slate-900 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                      >
                        <option value="">Select a user...</option>
                        {connectedUsers.filter(user => !formData.attendees.includes(user.email)).map((user) => (
                          <option key={user.id} value={user.id}>
                            {user.full_name || user.email}
                          </option>
                        ))}
                      </select>
                      <button
                        type="button"
                        onClick={addAttendeeFromUser}
                        disabled={!selectedUserId}
                        className="px-4 py-2 text-sm font-medium text-white bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg hover:from-blue-600 hover:to-blue-700 disabled:from-slate-400 disabled:to-slate-400 disabled:cursor-not-allowed shadow-sm transition-all duration-200"
                      >
                        Add
                      </button>
                      <button
                        type="button"
                        onClick={() => {
                          setShowAddAttendee(false);
                          setSelectedUserId(null);
                        }}
                        className="p-2 text-slate-600 hover:text-slate-900 hover:bg-slate-200 rounded-lg transition-colors"
                      >
                        <X className="h-5 w-5" />
                      </button>
                    </div>
                  </div>
                )}

                {/* Attendees list */}
                {formData.attendees.length === 0 ? (
                  <div className="flex flex-col items-center justify-center py-8 text-center">
                    <div className="flex h-16 w-16 items-center justify-center rounded-full bg-slate-200 mb-3">
                      <Users className="h-8 w-8 text-slate-400" />
                    </div>
                    <p className="text-sm font-medium text-slate-700 mb-1">No attendees yet</p>
                    <p className="text-xs text-slate-500">Add attendees to share this event on their calendars</p>
                  </div>
                ) : (
                  <div className="space-y-2">
                    {formData.attendees.map((email) => {
                      const user = connectedUsers.find(u => u.email === email);
                      const attendeeInfo = attendeeInfoMap.get(email);
                      const status = attendeeInfo?.response_status || 'pending';

                      // Determine status badge styling
                      const getStatusBadge = () => {
                        switch (status) {
                          case 'accepted':
                            return (
                              <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-700">
                                Accepted
                              </span>
                            );
                          case 'declined':
                            return (
                              <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-700">
                                Declined
                              </span>
                            );
                          case 'pending':
                          default:
                            return (
                              <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-orange-100 text-orange-700">
                                Pending
                              </span>
                            );
                        }
                      };

                      return (
                        <div
                          key={email}
                          className="group flex items-center justify-between p-3 rounded-xl bg-white border border-slate-200 hover:border-blue-300 hover:shadow-md transition-all duration-200"
                        >
                          <div className="flex items-center gap-3 flex-1 min-w-0">
                            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-slate-200 to-slate-300 flex-shrink-0">
                              <span className="text-sm font-semibold text-slate-700">
                                {(user?.full_name || email).charAt(0).toUpperCase()}
                              </span>
                            </div>
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-2">
                                <p className="text-sm font-semibold text-slate-900 truncate">
                                  {user?.full_name || email}
                                </p>
                                {attendeeInfo && getStatusBadge()}
                              </div>
                              <p className="text-xs text-slate-500 truncate">{email}</p>
                            </div>
                          </div>
                          <button
                            type="button"
                            onClick={() => handleRemoveAttendeeClick(email, user?.full_name || email)}
                            className="flex items-center gap-1 px-3 py-1.5 text-xs font-medium text-red-600 hover:text-red-700 hover:bg-red-50 rounded-lg transition-all duration-200 opacity-0 group-hover:opacity-100"
                          >
                            <Trash2 className="h-3 w-3" />
                            Remove
                          </button>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            </div>
          </div>

          <DialogFooter className="flex-shrink-0 border-t border-slate-200 bg-white px-6 py-4">
            <div className="flex w-full flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
              <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:gap-3">
                {!isCreateMode && event && canDeleteEvent && (
                  <Button
                    type="button"
                    variant="danger"
                    onClick={handleDelete}
                    disabled={loading}
                    leftIcon={<Trash2 className="h-4 w-4" />}
                  >
                    Delete event
                  </Button>
                )}
              </div>
              <div className="flex items-center gap-3">
                <Button
                  type="button"
                  variant="ghost"
                  onClick={handleClose}
                  disabled={loading}
                  className="border border-slate-300 bg-white text-slate-600 hover:bg-slate-100"
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  loading={loading}
                  leftIcon={<Save className="h-4 w-4" />}
                  className="min-w-[150px] bg-blue-600 text-white shadow-lg shadow-blue-500/30 hover:bg-blue-600/90"
                >
                  {isCreateMode ? 'Create event' : 'Save changes'}
                </Button>
              </div>
            </div>
          </DialogFooter>
        </form>
      </DialogContent>

      <ConfirmDialog
        isOpen={showDeleteConfirm}
        onClose={() => setShowDeleteConfirm(false)}
        onConfirm={confirmDelete}
        title="Delete Event"
        description="Are you sure you want to delete this event? This action cannot be undone."
        confirmText="Delete"
        cancelText="Cancel"
        variant="danger"
        loading={deleting}
      />

      <ConfirmDialog
        isOpen={removeAttendeeConfirm.isOpen}
        onClose={() => !removingAttendee && setRemoveAttendeeConfirm({ isOpen: false, email: '', name: '' })}
        onConfirm={confirmRemoveAttendee}
        title="Remove Attendee?"
        description={`Are you sure you want to remove ${removeAttendeeConfirm.name} from this event?${!isCreateMode ? ' This will immediately remove them from the event and delete their invitation.' : ''}`}
        confirmText="Remove"
        cancelText="Cancel"
        variant="warning"
        loading={removingAttendee}
      />
    </Dialog>
  );
}
