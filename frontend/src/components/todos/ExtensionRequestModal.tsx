'use client';

import { useEffect, useMemo, useState } from 'react';
import {
  AlertCircle,
  CalendarClock,
  CalendarRange,
  CheckCircle2,
  Hourglass,
  X,
} from 'lucide-react';
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
import { Badge } from '@/components/ui';
import { addDays, format, parseISO } from 'date-fns';
import { todoExtensionsApi } from '@/api/todo-extensions';
import type { ExtensionRequestModalProps, TodoExtensionValidation } from '@/types/todo';

const formatDateForInput = (value: Date | string) => {
  const date = value instanceof Date ? value : new Date(value);
  if (Number.isNaN(date.getTime())) return '';
  const offset = date.getTimezoneOffset();
  const local = new Date(date.getTime() - offset * 60_000);
  return local.toISOString().slice(0, 16);
};

const toISO = (value: string) => (value ? new Date(value).toISOString() : '');

const ExtensionRequestModal = ({
  isOpen,
  onClose,
  todo,
  onSuccess,
}: ExtensionRequestModalProps) => {
  const [requestedDate, setRequestedDate] = useState('');
  const [reason, setReason] = useState('');
  const [validation, setValidation] = useState<TodoExtensionValidation | null>(null);
  const [isValidating, setIsValidating] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const currentDueDate = todo.due_date ? parseISO(todo.due_date) : null;

  useEffect(() => {
    if (!isOpen || !currentDueDate) return;
    const tomorrow = addDays(currentDueDate, 1);
    setRequestedDate(formatDateForInput(tomorrow));
    setReason('');
    setValidation(null);
    setError(null);
  }, [isOpen, currentDueDate]);

  useEffect(() => {
    if (!isOpen || !requestedDate || !currentDueDate) return;

    const runValidation = async () => {
      setIsValidating(true);
      setError(null);
      try {
        const payload = await todoExtensionsApi.validateExtensionRequest(
          todo.id,
          toISO(requestedDate)
        );
        setValidation(payload);
      } catch (err: any) {
        const message = err?.response?.data?.detail || 'Unable to validate this extension';
        setError(message);
        setValidation(null);
      } finally {
        setIsValidating(false);
      }
    };

    runValidation();
  }, [isOpen, requestedDate, currentDueDate, todo.id]);

  const handleClose = () => {
    if (isSubmitting) return;
    setError(null);
    setValidation(null);
    setReason('');
    setRequestedDate('');
    onClose();
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!validation?.can_request_extension) {
      setError(validation?.reason || 'Extension request is not valid');
      return;
    }
    if (reason.trim().length < 10) {
      setError('Please share a short explanation (at least 10 characters).');
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      await todoExtensionsApi.createExtensionRequest(todo.id, {
        requested_due_date: toISO(requestedDate),
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
    if (validation?.max_allowed_due_date) {
      return parseISO(validation.max_allowed_due_date);
    }
    return addDays(currentDueDate, 3);
  }, [currentDueDate, validation?.max_allowed_due_date]);

  if (!currentDueDate) {
    return null;
  }

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && handleClose()}>
      <DialogContent
        closeButton={false}
        className="flex flex-col max-h-[90vh] w-full max-w-3xl md:max-w-2xl overflow-hidden rounded-3xl border border-slate-200 bg-white text-slate-900 shadow-[0_30px_70px_-20px_rgba(15,23,42,0.2)]"
      >
        <DialogHeader className="flex-shrink-0 px-6 pt-6">
          <div className="flex items-start justify-between gap-4">
            <div className="space-y-3">
              <div className="flex items-center gap-3">
                <span className="inline-flex h-10 w-10 items-center justify-center rounded-full bg-cyan-100 text-cyan-600">
                  <CalendarRange className="h-5 w-5" />
                </span>
                <div>
                  <DialogTitle className="text-lg font-semibold text-slate-900">
                    Request an extension
                  </DialogTitle>
                  <DialogDescription className="text-sm text-slate-500">
                    Propose a new due date and let the task owner know why you need more time.
                  </DialogDescription>
                </div>
              </div>
              <Badge className="w-fit bg-cyan-100 text-cyan-700 ring-1 ring-inset ring-cyan-200">
                Current due {format(currentDueDate, "MMM dd, yyyy 'at' h:mm a")}
              </Badge>
            </div>
            <DialogClose className="rounded-full border border-slate-200 p-2 text-slate-500 transition hover:bg-slate-100 hover:text-slate-700">
              <X className="h-4 w-4" />
            </DialogClose>
          </div>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="flex flex-1 flex-col overflow-hidden">
          <div className="flex-1 overflow-y-auto space-y-6 px-6 pb-6">
            <div className="space-y-4 rounded-2xl border border-slate-200 bg-slate-50 p-6">
              <div className="grid gap-4 md:grid-cols-2">
                <Input
                  type="datetime-local"
                  label="New due date"
                  value={requestedDate}
                  onChange={(event) => setRequestedDate(event.target.value)}
                  min={formatDateForInput(addDays(currentDueDate, 1))}
                  max={maxAllowedDate ? formatDateForInput(maxAllowedDate) : undefined}
                  required
                  leftIcon={<CalendarClock className="h-4 w-4" />}
                  helperText={
                    maxAllowedDate
                      ? `Maximum extension: ${format(maxAllowedDate, 'MMM dd, yyyy')}`
                      : undefined
                  }
                />
                <div className="space-y-2">
                  <span className="flex items-center gap-2 text-sm font-medium text-slate-700">
                    <Hourglass className="h-4 w-4 text-slate-400" />
                    Validation status
                  </span>
                  <div className="rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm">
                    {isValidating && (
                      <div className="flex items-center gap-2 text-cyan-700">
                        <Hourglass className="h-4 w-4 animate-spin" />
                        Checking allowed extension window...
                      </div>
                    )}
                    {!isValidating && validation?.can_request_extension && (
                      <div className="flex items-center gap-2 text-emerald-600">
                        <CheckCircle2 className="h-4 w-4" />
                        Extension request looks good.
                      </div>
                    )}
                    {!isValidating && validation && !validation.can_request_extension && (
                      <div className="flex items-center gap-2 text-amber-600">
                        <AlertCircle className="h-4 w-4" />
                        {validation.reason}
                      </div>
                    )}
                    {!isValidating && !validation && (
                      <span className="text-slate-500">Select a new date to validate.</span>
                    )}
                  </div>
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-700">
                  Why do you need more time?
                </label>
                <Textarea
                  value={reason}
                  onChange={(event) => setReason(event.target.value)}
                  rows={4}
                  minLength={10}
                  maxLength={1000}
                  required
                  placeholder="Share context so reviewers understand the request..."
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
              disabled={
                isSubmitting ||
                isValidating ||
                !validation?.can_request_extension ||
                reason.trim().length < 10
              }
              leftIcon={<CalendarRange className="h-4 w-4" />}
              className="min-w-[170px] bg-cyan-600 text-white shadow-lg shadow-cyan-500/30 hover:bg-cyan-600/90 disabled:opacity-60"
            >
              Submit request
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};

export default ExtensionRequestModal;
