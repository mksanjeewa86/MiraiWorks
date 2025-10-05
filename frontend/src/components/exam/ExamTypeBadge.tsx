import React from 'react';
import type { Exam } from '@/types/exam';

interface ExamTypeBadgeProps {
  exam: Exam;
  currentCompanyId?: number | null;
}

export function ExamTypeBadge({ exam, currentCompanyId }: ExamTypeBadgeProps) {
  // Global exam: company_id = null, is_public = true
  if (exam.company_id === null && exam.is_public) {
    return (
      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200">
        🌍 Global
      </span>
    );
  }

  // Public exam from another company
  if (exam.is_public && exam.company_id !== currentCompanyId) {
    return (
      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
        🔓 Public
      </span>
    );
  }

  // Own company's public exam
  if (exam.is_public && exam.company_id === currentCompanyId) {
    return (
      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
        ✓ Public (Yours)
      </span>
    );
  }

  // Private exam
  return (
    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200">
      🔒 Private
    </span>
  );
}
