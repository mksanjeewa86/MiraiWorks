'use client';

import { useState, useEffect } from 'react';
import { CalendarRange, Calendar, Clock } from 'lucide-react';
import { addDays, format } from 'date-fns';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui';
import { Button, Input, Textarea } from '@/components/ui';
import type { TodoExtensionRequest } from '@/types/todo';

interface ExtensionChangeDateDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (newDate: string, newTime: string, reason?: string) => void;
  request: TodoExtensionRequest | null;
  loading?: boolean;
}

const formatDateForInput = (value: Date | string) => {
  const date = value instanceof Date ? value : new Date(value);
  if (Number.isNaN(date.getTime())) return '';
  const offset = date.getTimezoneOffset();
  const local = new Date(date.getTime() - offset * 60_000);
  return local.toISOString().slice(0, 10);
};

const formatTimeForInput = (value: Date | string) => {
  const date = value instanceof Date ? new Date(value) : new Date(value);
  if (Number.isNaN(date.getTime())) return '';
  const offset = date.getTimezoneOffset();
  const local = new Date(date.getTime() - offset * 60_000);
  return local.toISOString().slice(11, 16);
};

export default function ExtensionChangeDateDialog({
  isOpen,
  onClose,
  onConfirm,
  request,
  loading = false,
}: ExtensionChangeDateDialogProps) {
  const [newDate, setNewDate] = useState('');
  const [newTime, setNewTime] = useState('');
  const [reason, setReason] = useState('');

  useEffect(() => {
    if (isOpen && request) {
      const requestedDate = new Date(request.requested_due_date);
      setNewDate(formatDateForInput(requestedDate));
      setNewTime(formatTimeForInput(requestedDate));
      setReason('');
    }
  }, [isOpen, request]);

  const handleClose = () => {
    if (!loading) {
      setNewDate('');
      setNewTime('');
      setReason('');
      onClose();
    }
  };

  const handleConfirm = () => {
    if (newDate && newTime) {
      onConfirm(newDate, newTime, reason.trim() || undefined);
      setNewDate('');
      setNewTime('');
      setReason('');
    }
  };

  if (!request) return null;

  // Get current due date from todo
  const getCurrentDate = () => {
    if (!request.todo.due_datetime) return new Date();
    return new Date(request.todo.due_datetime);
  };

  const currentDate = getCurrentDate();
  const maxDate = addDays(currentDate, 3);
  const isValid = newDate.length > 0 && newTime.length > 0;

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && handleClose()}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <div className="flex items-start gap-4">
            <div className="flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-full bg-blue-100 text-blue-600">
              <CalendarRange className="h-6 w-6" />
            </div>
            <div className="flex-1">
              <DialogTitle className="text-lg font-semibold text-slate-900">
                Change Extension Date
              </DialogTitle>
              <DialogDescription className="mt-2 text-sm text-slate-600">
                Set a different due date for this extension request.
              </DialogDescription>
            </div>
          </div>
        </DialogHeader>

        <div className="mt-4 space-y-4">
          {/* New Due Date & Time */}
          <div>
            <label className="text-sm font-medium text-slate-700 mb-2 block">
              New Due Date & Time
            </label>
            <div className="grid gap-3 grid-cols-2">
              <Input
                type="date"
                value={newDate}
                onChange={(e) => setNewDate(e.target.value)}
                min={formatDateForInput(addDays(currentDate, 1))}
                max={formatDateForInput(maxDate)}
                required
                leftIcon={<Calendar className="h-4 w-4" />}
              />
              <Input
                type="time"
                value={newTime}
                onChange={(e) => setNewTime(e.target.value)}
                required
                leftIcon={<Clock className="h-4 w-4" />}
              />
            </div>
            <p className="mt-1 text-xs text-slate-500">
              Maximum: {format(maxDate, 'MMM dd, yyyy')}
            </p>
          </div>

          {/* Optional Note */}
          <div>
            <label className="text-sm font-medium text-slate-700 mb-2 block">
              Note (optional)
            </label>
            <Textarea
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              placeholder="Add a note about the date change..."
              rows={3}
              maxLength={1000}
              className="border border-slate-300 bg-white text-slate-900"
            />
            <p className="mt-1 text-xs text-slate-500">{reason.length}/1000 characters</p>
          </div>
        </div>

        <DialogFooter className="mt-6 gap-3 sm:gap-3">
          <Button
            type="button"
            variant="ghost"
            onClick={handleClose}
            disabled={loading}
            className="flex-1 sm:flex-none"
          >
            Cancel
          </Button>
          <Button
            type="button"
            onClick={handleConfirm}
            loading={loading}
            disabled={!isValid || loading}
            className="flex-1 sm:flex-none bg-blue-600 hover:bg-blue-700"
          >
            Approve with New Date
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
