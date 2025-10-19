import React from 'react';
import { X } from 'lucide-react';
import { clsx } from 'clsx';
import type { ConfirmationModalPropsExtended } from '@/types/components';

const ConfirmationModal: React.FC<ConfirmationModalPropsExtended> = ({
  isOpen,
  onClose,
  onConfirm,
  title,
  message,
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  confirmButtonClass,
  icon,
  dangerous = false,
}) => {
  if (!isOpen) return null;

  const handleConfirm = () => {
    onConfirm();
    onClose();
  };

  const defaultConfirmClass = dangerous
    ? 'bg-red-600 hover:bg-red-700 text-white'
    : 'bg-blue-600 hover:bg-blue-700 text-white';

  return (
    <div className="fixed inset-0 z-[100] overflow-y-auto">
      {/* Backdrop - transparent */}
      <div className="fixed inset-0 bg-transparent transition-opacity" onClick={onClose} />

      {/* Modal */}
      <div className="flex min-h-full items-center justify-center p-4">
        <div
          className="relative w-full max-w-md transform rounded-lg bg-white p-6 shadow-xl transition-all dark:bg-gray-800"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Close button */}
          <button
            onClick={onClose}
            className="absolute right-4 top-4 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
          >
            <X className="h-5 w-5" />
          </button>

          {/* Header */}
          <div className="flex items-center space-x-3 mb-4">
            {icon && <div className="flex-shrink-0">{icon}</div>}
            <h3 className="text-lg font-medium text-gray-900 dark:text-white">{title}</h3>
          </div>

          {/* Message */}
          <div className="mb-6 text-sm text-gray-600 dark:text-gray-300">
            {typeof message === 'string' ? <p>{message}</p> : message}
          </div>

          {/* Actions */}
          <div className="flex flex-col-reverse space-y-2 space-y-reverse sm:flex-row sm:justify-end sm:space-y-0 sm:space-x-2">
            <button
              onClick={onClose}
              className="inline-flex w-full justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-base font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600 sm:mt-0 sm:w-auto sm:text-sm"
            >
              {cancelText}
            </button>
            <button
              onClick={handleConfirm}
              className={clsx(
                'inline-flex w-full justify-center rounded-md px-4 py-2 text-base font-medium shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2 sm:w-auto sm:text-sm',
                confirmButtonClass || defaultConfirmClass
              )}
            >
              {confirmText}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ConfirmationModal;
