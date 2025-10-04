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
} from 'lucide-react';
import type { CalendarEvent } from '@/types/interview';
import type { EventModalProps, EventFormData } from '@/types/components';
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui';
import { Button } from '@/components/ui';
import { Input } from '@/components/ui';
import { Textarea } from '@/components/ui';
import { Checkbox } from '@/components/ui';

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

  const eventId = event?.id ?? '';
  const isTodoEvent = eventId.startsWith('todo-');
  const isInterviewEvent = eventId.startsWith('interview-');
  const isCalendarEvent = /^\d+$/.test(eventId);
  const canDeleteEvent = !isCreateMode && !!event && (isCalendarEvent || isTodoEvent);
  const deleteHelperMessage =
    !isCreateMode && event && !canDeleteEvent
      ? isInterviewEvent
        ? 'Interviews must be cancelled from the interview workflow.'
        : 'This event cannot be deleted from this view.'
      : null;

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

  const safeDateToLocalString = useCallback(
    (dateString: string | null | undefined, fallback: Date = new Date()): string => {
      const date = safeParseDate(dateString);
      return (date || fallback).toISOString().slice(0, 16);
    },
    []
  );

  useEffect(() => {
    if (!isOpen) {
      return;
    }

    if (isCreateMode) {
      const now = new Date();
      const baseStart = selectedRange
        ? new Date(selectedRange.start)
        : selectedDate
          ? new Date(selectedDate)
          : now;
      const safeStart = Number.isNaN(baseStart.getTime()) ? now : baseStart;

      const computedEnd = (() => {
        if (selectedRange) {
          const maybeEnd = new Date(selectedRange.end);
          if (!Number.isNaN(maybeEnd.getTime())) {
            return maybeEnd;
          }
        }
        const fallback = new Date(safeStart);
        fallback.setHours(fallback.getHours() + 1);
        return fallback;
      })();

      setFormData({
        title: '',
        description: '',
        location: '',
        startDatetime: safeStart.toISOString().slice(0, 16),
        endDatetime: computedEnd.toISOString().slice(0, 16),
        isAllDay: Boolean(selectedRange?.allDay),
        attendees: [],
        status: 'tentative',
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC',
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

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();

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
        organizerEmail: undefined,
        isRecurring: false,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };

      await onSave(eventData);
    } catch (error) {
      console.error('Error saving event:', error);
    } finally {
      setLoading(false);
    }
  };

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

  const removeAttendee = (email: string) => {
    setFormData((prev) => ({
      ...prev,
      attendees: prev.attendees.filter((attendee) => attendee !== email),
    }));
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
      endDatetime: end.toISOString().slice(0, 16),
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
                <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-[0_20px_40px_-28px_rgba(37,99,235,0.45)]">
                  <div className="mb-4 flex items-center justify-between gap-3">
                    <div>
                      <p className="text-sm font-semibold text-slate-800">Quick templates</p>
                      <p className="text-xs text-slate-500">
                        Prefill common event details in one click.
                      </p>
                    </div>
                  </div>
                  <div className="grid gap-2 sm:grid-cols-2">
                    {eventTemplates.map((template) => (
                      <button
                        key={template.name}
                        type="button"
                        onClick={() => applyTemplate(template)}
                        className="flex items-center gap-3 rounded-xl border border-slate-200 bg-gradient-to-r from-white to-blue-50/60 px-4 py-3 text-left transition-all hover:border-blue-300 hover:shadow-md focus:outline-none focus:ring-2 focus:ring-blue-400"
                      >
                        <span className="inline-flex h-9 w-9 items-center justify-center rounded-full bg-blue-100 text-blue-600">
                          <template.icon className="h-4 w-4" />
                        </span>
                        <span className="text-sm font-medium text-slate-700">{template.name}</span>
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

                <div className="grid gap-4 md:grid-cols-2">
                  <Input
                    type="datetime-local"
                    label="Starts"
                    value={formData.startDatetime}
                    onChange={(event) =>
                      setFormData((prev) => ({ ...prev, startDatetime: event.target.value }))
                    }
                    leftIcon={<CalendarClock className="h-4 w-4" />}
                    error={errors.startDatetime}
                    required
                  />
                  <Input
                    type="datetime-local"
                    label="Ends"
                    value={formData.endDatetime}
                    onChange={(event) =>
                      setFormData((prev) => ({ ...prev, endDatetime: event.target.value }))
                    }
                    leftIcon={<CalendarRange className="h-4 w-4" />}
                    error={errors.endDatetime}
                    required
                  />
                </div>

                <div className="flex flex-col gap-2 rounded-xl border border-slate-200 bg-white px-4 py-3 sm:flex-row sm:items-center sm:justify-between">
                  <div className="flex items-center gap-3">
                    <Checkbox
                      id="all-day-event"
                      checked={formData.isAllDay}
                      onCheckedChange={(checked) =>
                        setFormData((prev) => ({ ...prev, isAllDay: checked }))
                      }
                      disabled={loading}
                    />
                    <label htmlFor="all-day-event" className="text-sm font-medium text-slate-700">
                      All-day event
                    </label>
                  </div>
                  <p className="text-xs text-slate-500">
                    {formData.isAllDay
                      ? 'Blocks the entire day on your calendar.'
                      : 'Uses start and end times in your local timezone.'}
                  </p>
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

                <div className="grid gap-4 md:grid-cols-2">
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-slate-700">Status</label>
                    <select
                      value={formData.status}
                      onChange={(event) =>
                        setFormData((prev) => ({ ...prev, status: event.target.value }))
                      }
                      className="h-11 w-full rounded-lg border border-slate-300 bg-white px-3 text-sm text-slate-700 shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                    >
                      <option value="tentative">Tentative</option>
                      <option value="confirmed">Confirmed</option>
                      <option value="cancelled">Cancelled</option>
                    </select>
                  </div>
                  <div className="rounded-lg border border-dashed border-blue-200 bg-blue-50 px-4 py-3 text-xs font-medium text-blue-700">
                    Invites default to <span className="font-semibold">{formData.timezone}</span>{' '}
                    timezone.
                  </div>
                </div>
              </div>

              <div className="rounded-2xl border border-slate-200 bg-white p-6">
                <div className="mb-4 flex items-center justify-between gap-3">
                  <div>
                    <h3 className="flex items-center gap-2 text-sm font-semibold text-slate-800">
                      <Users className="h-4 w-4 text-blue-600" />
                      Attendees
                    </h3>
                    <p className="text-xs text-slate-500">
                      Invite teammates or clients to sync this event to their calendar.
                    </p>
                  </div>
                </div>
                <div className="flex flex-col gap-3 sm:flex-row">
                  <Input
                    type="email"
                    label="Email"
                    placeholder="name@example.com"
                    value={attendeeInput}
                    onChange={(event) => setAttendeeInput(event.target.value)}
                    onKeyDown={(event) => {
                      if (event.key === 'Enter') {
                        event.preventDefault();
                        addAttendee();
                      }
                    }}
                  />
                  <Button
                    type="button"
                    onClick={addAttendee}
                    disabled={loading || !attendeeInput.trim()}
                    className="sm:self-end sm:px-5"
                  >
                    Add attendee
                  </Button>
                </div>
                {formData.attendees.length > 0 && (
                  <div className="mt-4 space-y-2">
                    {formData.attendees.map((email) => (
                      <div
                        key={email}
                        className="flex items-center justify-between rounded-xl border border-slate-200 bg-slate-50 px-4 py-2"
                      >
                        <span className="text-sm text-slate-700">{email}</span>
                        <button
                          type="button"
                          onClick={() => removeAttendee(email)}
                          className="text-slate-400 transition hover:text-red-500"
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
                {!isCreateMode && event && deleteHelperMessage && (
                  <p className="text-xs text-slate-500">{deleteHelperMessage}</p>
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
    </Dialog>
  );
}
