'use client';

import { useEffect, useMemo, useState } from 'react';
import { AlertCircle, ArrowDown, Calendar, CalendarRange, Clock, X } from 'lucide-react';
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
import { addDays, format, parseISO } from 'date-fns';
import { todoExtensionsApi } from '@/api/todo-extensions';
import type { ExtensionRequestModalProps } from '@/types/todo';

const formatDateForInput = (value: Date | string) => {
  const date = value instanceof Date ? value : new Date(value);
  if (Number.isNaN(date.getTime())) return '';
  const offset = date.getTimezoneOffset();
  const local = new Date(date.getTime() - offset * 60_000);
  return local.toISOString().slice(0, 10); // Date only (YYYY-MM-DD)
};

const formatTimeForInput = (value: Date | string) => {
  const date = value instanceof Date ? value : new Date(value);
  if (Number.isNaN(date.getTime())) return '';
  const offset = date.getTimezoneOffset();
  const local = new Date(date.getTime() - offset * 60_000);
  return local.toISOString().slice(11, 16); // Time only (HH:mm)
};

const combineDateTime = (dateStr: string, timeStr: string): string => {
  if (!dateStr) return '';
  const time = timeStr || '23:59'; // Default to end of day if no time
  return new Date(`${dateStr}T${time}:00`).toISOString();
};

const ExtensionRequestModal = ({
  isOpen,
  onClose,
  todo,
  onSuccess,
}: ExtensionRequestModalProps) => {
  const [newDate, setNewDate] = useState('');
  const [newTime, setNewTime] = useState('');
  const [reason, setReason] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Memoize currentDueDate to prevent unnecessary re-renders
  const currentDueDate = useMemo(
    () => (todo.due_datetime ? parseISO(todo.due_datetime) : null),
    [todo.due_datetime]
  );

  const currentDateStr = useMemo(
    () => (currentDueDate ? formatDateForInput(currentDueDate) : ''),
    [currentDueDate]
  );

  const currentTimeStr = useMemo(
    () => (currentDueDate ? formatTimeForInput(currentDueDate) : ''),
    [currentDueDate]
  );

  // Initialize form when modal opens
  useEffect(() => {
    if (!isOpen || !currentDueDate) return;
    const tomorrow = addDays(currentDueDate, 1);
    setNewDate(formatDateForInput(tomorrow));
    setNewTime(formatTimeForInput(currentDueDate)); // Keep same time as current
    setReason('');
    setError(null);
  }, [isOpen, currentDueDate]);

  const handleClose = () => {
    if (isSubmitting) return;
    setError(null);
    setReason('');
    setNewDate('');
    setNewTime('');
    onClose();
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    // Validate that new date is after current date
    if (newDate && currentDateStr) {
      const newDateTime = new Date(`${newDate}T${newTime || '00:00'}:00`);
      const currentDateTime = new Date(`${currentDateStr}T${currentTimeStr}:00`);

      if (newDateTime <= currentDateTime) {
        setError('Extension date must be after the current due date');
        return;
      }

      // Check max 3 days extension
      const maxDate = addDays(currentDateTime, 3);
      if (newDateTime > maxDate) {
        setError(`Extension cannot exceed 3 days. Maximum: ${format(maxDate, 'MMM dd, yyyy')}`);
        return;
      }
    }

    if (reason.trim().length < 10) {
      setError('Please provide a reason (at least 10 characters)');
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      await todoExtensionsApi.createExtensionRequest(todo.id, {
        requested_due_date: combineDateTime(newDate, newTime),
        reason: reason.trim(),
      });
      onSuccess();
      handleClose();
    } catch (err: any) {
      const message = err?.response?.data?.detail || "We couldn't submit your request.";
      setError(message);
    } finally {
      setIsSubmitting(false);
    }
  };

  const maxAllowedDate = useMemo(() => {
    if (!currentDueDate) return null;
    return addDays(currentDueDate, 3);
  }, [currentDueDate]);

  // Check if form is valid for submission
  const isFormValid = useMemo(() => {
    return (
      newDate.length > 0 &&
      newTime.length > 0 &&
      reason.trim().length >= 10
    );
  }, [newDate, newTime, reason]);

  if (!currentDueDate) {
    return null;
  }

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && handleClose()}>
      <DialogContent
        closeButton={false}
        className="flex flex-col max-h-[90vh] w-full max-w-2xl overflow-hidden rounded-3xl border border-slate-200 bg-white text-slate-900 shadow-[0_30px_70px_-20px_rgba(15,23,42,0.2)]"
      >
        <DialogHeader className="flex-shrink-0 px-6 pt-6">
          <div className="flex items-start justify-between gap-4">
            <div className="space-y-2">
              <div className="flex items-center gap-3">
                <span className="inline-flex h-10 w-10 items-center justify-center rounded-full bg-cyan-100 text-cyan-600">
                  <CalendarRange className="h-5 w-5" />
                </span>
                <div>
                  <DialogTitle className="text-lg font-semibold text-slate-900">
                    Request Extension
                  </DialogTitle>
                  <DialogDescription className="text-sm text-slate-500">
                    Propose a new due date and explain why you need more time
                  </DialogDescription>
                </div>
              </div>
            </div>
            <DialogClose className="rounded-full border border-slate-200 p-2 text-slate-500 transition hover:bg-slate-100 hover:text-slate-700">
              <X className="h-4 w-4" />
            </DialogClose>
          </div>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="flex flex-1 flex-col overflow-hidden">
          <div className="flex-1 overflow-y-auto space-y-6 px-6 pb-6">
            <div className="space-y-4 rounded-2xl border border-slate-200 bg-slate-50 p-6">
              {/* Current Due Date (Read-only) */}
              <div className="space-y-3">
                <label className="text-sm font-medium text-slate-700">
                  Current Due Date & Time
                </label>
                <div className="grid gap-3 md:grid-cols-2">
                  <Input
                    type="date"
                    value={currentDateStr}
                    disabled
                    leftIcon={<Calendar className="h-4 w-4" />}
                    className="bg-slate-100"
                  />
                  <Input
                    type="time"
                    value={currentTimeStr}
                    disabled
                    leftIcon={<Clock className="h-4 w-4" />}
                    className="bg-slate-100"
                  />
                </div>
              </div>

              {/* Down Arrow */}
              <div className="flex justify-center">
                <div className="rounded-full bg-cyan-100 p-2">
                  <ArrowDown className="h-5 w-5 text-cyan-600" />
                </div>
              </div>

              {/* New Due Date */}
              <div className="space-y-3">
                <label className="text-sm font-medium text-slate-700">
                  New Due Date & Time <span className="text-red-500">*</span>
                </label>
                <div className="grid gap-3 md:grid-cols-2">
                  <Input
                    type="date"
                    value={newDate}
                    onChange={(e) => setNewDate(e.target.value)}
                    min={formatDateForInput(addDays(currentDueDate, 1))}
                    max={maxAllowedDate ? formatDateForInput(maxAllowedDate) : undefined}
                    required
                    leftIcon={<Calendar className="h-4 w-4" />}
                    helperText={
                      maxAllowedDate
                        ? `Max: ${format(maxAllowedDate, 'MMM dd, yyyy')}`
                        : undefined
                    }
                  />
                  <Input
                    type="time"
                    value={newTime}
                    onChange={(e) => setNewTime(e.target.value)}
                    required
                    leftIcon={<Clock className="h-4 w-4" />}
                  />
                </div>
              </div>

              {/* Reason */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-700">
                  Reason <span className="text-red-500">*</span>
                </label>
                <Textarea
                  value={reason}
                  onChange={(event) => setReason(event.target.value)}
                  rows={4}
                  minLength={10}
                  maxLength={1000}
                  required
                  placeholder="Explain why you need more time..."
                  className="border border-slate-300 bg-white text-slate-900 focus-visible:ring-cyan-500"
                />
                <p className="text-xs text-slate-500">
                  {reason.length}/1000 characters (minimum 10)
                </p>
              </div>

              {error && (
                <div className="flex items-start gap-2 rounded-xl border border-red-500/20 bg-red-50 p-4 text-sm text-red-600">
                  <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
                  <span>{error}</span>
                </div>
              )}
            </div>
          </div>

          <DialogFooter className="flex-shrink-0 gap-3 border-t border-slate-200 bg-white px-6 py-4">
            <Button
              type="button"
              variant="ghost"
              onClick={handleClose}
              disabled={isSubmitting}
              className="border border-slate-300 bg-white text-slate-600 hover:bg-slate-100"
            >
              Cancel
            </Button>
            <Button
              type="submit"
              loading={isSubmitting}
              disabled={isSubmitting || !isFormValid}
              leftIcon={<CalendarRange className="h-4 w-4" />}
              className="min-w-[170px] bg-cyan-600 text-white shadow-lg shadow-cyan-500/30 hover:bg-cyan-600/90 disabled:opacity-60"
            >
              Submit Request
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};

export default ExtensionRequestModal;
