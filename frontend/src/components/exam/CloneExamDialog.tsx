'use client';

import React, { useState } from 'react';
import { examApi } from '@/api/exam';
import { useLocaleRouter } from '@/hooks/useLocaleRouter';
import { ROUTES } from '@/routes/config';
import type { Exam } from '@/types/exam';

interface CloneExamDialogProps {
  exam: Exam;
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: (clonedExamId: number) => void;
}

export function CloneExamDialog({
  exam,
  isOpen,
  onClose,
  onSuccess
}: CloneExamDialogProps) {
  const router = useLocaleRouter();
  const [isCloning, setIsCloning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleClone = async () => {
    setIsCloning(true);
    setError(null);

    const response = await examApi.cloneExam(exam.id);

    if (response.success && response.data) {
      // Success - redirect to edit the cloned exam
      onClose();
      if (onSuccess) {
        onSuccess(response.data.id);
      } else {
        router.push(ROUTES.ADMIN.EXAMS.EDIT(response.data.id));
      }
    } else {
      setError(response.message || response.errors?.[0] || 'Failed to clone exam');
      setIsCloning(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen px-4">
        {/* Overlay */}
        <div
          className="fixed inset-0 bg-black bg-opacity-30 transition-opacity"
          onClick={onClose}
        />

        {/* Dialog */}
        <div className="relative bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full p-6">
          <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">
            Clone Exam
          </h3>

          <p className="text-gray-600 dark:text-gray-300 mb-4">
            Clone "<strong>{exam.title}</strong>" to your company's exam library?
          </p>

          <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded p-3 mb-4">
            <p className="text-sm text-blue-800 dark:text-blue-200 font-medium">
              What will be cloned:
            </p>
            <ul className="text-sm text-blue-700 dark:text-blue-300 mt-2 space-y-1 list-disc list-inside">
              <li>All exam settings (time limit, passing score, etc.)</li>
              <li>All {exam.total_questions || 0} questions with answers</li>
            </ul>
          </div>

          <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded p-3 mb-4">
            <p className="text-sm text-green-800 dark:text-green-200 font-medium">
              After cloning, you can:
            </p>
            <ul className="text-sm text-green-700 dark:text-green-300 mt-2 space-y-1 list-disc list-inside">
              <li>Edit all exam settings</li>
              <li>Add, edit, or delete questions</li>
              <li>Assign to your candidates</li>
            </ul>
          </div>

          {error && (
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded p-3 mb-4">
              <p className="text-sm text-red-800 dark:text-red-200">{error}</p>
            </div>
          )}

          <div className="flex justify-end space-x-3">
            <button
              onClick={onClose}
              disabled={isCloning}
              className="px-4 py-2 text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 rounded hover:bg-gray-200 dark:hover:bg-gray-600 disabled:opacity-50 transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleClone}
              disabled={isCloning}
              className="px-4 py-2 text-white bg-blue-600 rounded hover:bg-blue-700 disabled:opacity-50 flex items-center transition-colors"
            >
              {isCloning ? (
                <>
                  <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  Cloning...
                </>
              ) : (
                'Clone Exam'
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
