import React, { useState, useEffect } from 'react';
import { Dialog, Transition } from '@headlessui/react';
import { Fragment } from 'react';
import { XMarkIcon, ClockIcon, CalendarIcon } from '@heroicons/react/24/outline';
import { format, addDays, parseISO } from 'date-fns';
import DateTimePicker from '@/components/ui/date-time-picker';
import { todoExtensionsApi } from '@/api/todo-extensions';
import type { ExtensionRequestModalProps, TodoExtensionValidation } from '@/types/todo';

const ExtensionRequestModal: React.FC<ExtensionRequestModalProps> = ({
  isOpen,
  onClose,
  todo,
  onSuccess,
}) => {
  const [requestedDate, setRequestedDate] = useState('');
  const [reason, setReason] = useState('');
  const [validation, setValidation] = useState<TodoExtensionValidation | null>(null);
  const [isValidating, setIsValidating] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Initialize with tomorrow's date
  useEffect(() => {
    if (isOpen && todo.due_date) {
      const tomorrow = addDays(parseISO(todo.due_date), 1);
      setRequestedDate(format(tomorrow, "yyyy-MM-dd'T'HH:mm"));
    }
  }, [isOpen, todo.due_date]);

  // Validate when requested date changes
  useEffect(() => {
    if (requestedDate && todo.due_date) {
      validateExtension();
    }
  }, [requestedDate, todo.due_date]);

  const validateExtension = async () => {
    if (!requestedDate) return;

    setIsValidating(true);
    setError(null);

    try {
      const result = await todoExtensionsApi.validateExtensionRequest(
        todo.id,
        new Date(requestedDate).toISOString()
      );
      setValidation(result);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to validate extension request');
      setValidation(null);
    } finally {
      setIsValidating(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validation?.can_request_extension) {
      setError('Extension request is not valid');
      return;
    }

    if (!reason.trim()) {
      setError('Please provide a reason for the extension');
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      await todoExtensionsApi.createExtensionRequest(todo.id, {
        requested_due_date: new Date(requestedDate).toISOString(),
        reason: reason.trim(),
      });

      onSuccess();
      onClose();

      // Reset form
      setRequestedDate('');
      setReason('');
      setValidation(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create extension request');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = () => {
    setRequestedDate('');
    setReason('');
    setValidation(null);
    setError(null);
    onClose();
  };

  if (!todo.due_date) {
    return null;
  }

  const currentDueDate = parseISO(todo.due_date);
  const maxAllowedDate = validation?.max_allowed_due_date
    ? parseISO(validation.max_allowed_due_date)
    : addDays(currentDueDate, 3);

  return (
    <Transition appear show={isOpen} as={Fragment}>
      <Dialog as="div" className="relative z-50" onClose={handleClose}>
        <Transition.Child
          as={Fragment}
          enter="ease-out duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-200"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-black bg-opacity-25" />
        </Transition.Child>

        <div className="fixed inset-0 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4 text-center">
            <Transition.Child
              as={Fragment}
              enter="ease-out duration-300"
              enterFrom="opacity-0 scale-95"
              enterTo="opacity-100 scale-100"
              leave="ease-in duration-200"
              leaveFrom="opacity-100 scale-100"
              leaveTo="opacity-0 scale-95"
            >
              <Dialog.Panel className="w-full max-w-md transform overflow-hidden rounded-2xl bg-white p-6 text-left align-middle shadow-xl transition-all">
                <div className="flex items-center justify-between mb-4">
                  <Dialog.Title as="h3" className="text-lg font-medium leading-6 text-gray-900">
                    Request Extension
                  </Dialog.Title>
                  <button onClick={handleClose} className="text-gray-400 hover:text-gray-600">
                    <XMarkIcon className="h-5 w-5" />
                  </button>
                </div>

                <div className="mb-4 p-3 bg-gray-50 rounded-lg">
                  <h4 className="font-medium text-gray-900 mb-1">{todo.title}</h4>
                  <div className="flex items-center text-sm text-gray-600">
                    <CalendarIcon className="h-4 w-4 mr-1" />
                    Current due: {format(currentDueDate, "MMM dd, yyyy 'at' h:mm a")}
                  </div>
                </div>

                <form onSubmit={handleSubmit} className="space-y-4">
                  {/* Requested Date */}
                  <DateTimePicker
                    label="New Due Date"
                    value={requestedDate || null}
                    onChange={(nextValue) => setRequestedDate(nextValue ?? '')}
                    min={format(addDays(currentDueDate, 1), "yyyy-MM-dd'T'HH:mm")}
                    max={format(maxAllowedDate, "yyyy-MM-dd'T'HH:mm")}
                    placeholder="Select new due date"
                    helperText={`Maximum extension: ${format(maxAllowedDate, 'MMM dd, yyyy')} (3 days)`}
                    required
                  />

                  {/* Validation Feedback */}
                  {isValidating && (
                    <div className="flex items-center text-sm text-blue-600">
                      <ClockIcon className="h-4 w-4 mr-1 animate-spin" />
                      Validating...
                    </div>
                  )}

                  {validation && !validation.can_request_extension && (
                    <div className="p-3 bg-red-50 border border-red-200 rounded-md">
                      <p className="text-sm text-red-600">{validation.reason}</p>
                    </div>
                  )}

                  {validation && validation.can_request_extension && (
                    <div className="p-3 bg-green-50 border border-green-200 rounded-md">
                      <p className="text-sm text-green-600">笨・Extension request is valid</p>
                    </div>
                  )}

                  {/* Reason */}
                  <div>
                    <label
                      htmlFor="reason"
                      className="block text-sm font-medium text-gray-700 mb-1"
                    >
                      Reason for Extension <span className="text-red-500">*</span>
                    </label>
                    <textarea
                      id="reason"
                      value={reason}
                      onChange={(e) => setReason(e.target.value)}
                      rows={4}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="Please explain why you need this extension..."
                      required
                      minLength={10}
                      maxLength={1000}
                    />
                    <p className="mt-1 text-xs text-gray-500">
                      {reason.length}/1000 characters (minimum 10)
                    </p>
                  </div>

                  {/* Error Message */}
                  {error && (
                    <div className="p-3 bg-red-50 border border-red-200 rounded-md">
                      <p className="text-sm text-red-600">{error}</p>
                    </div>
                  )}

                  {/* Actions */}
                  <div className="flex justify-end space-x-3 pt-4">
                    <button
                      type="button"
                      onClick={handleClose}
                      className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      disabled={
                        isSubmitting ||
                        isValidating ||
                        !validation?.can_request_extension ||
                        reason.trim().length < 10
                      }
                      className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {isSubmitting ? 'Submitting...' : 'Request Extension'}
                    </button>
                  </div>
                </form>
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition>
  );
};

export default ExtensionRequestModal;



