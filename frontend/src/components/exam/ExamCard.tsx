'use client';

import React, { useState } from 'react';
import { ExamTypeBadge } from './ExamTypeBadge';
import { CloneExamDialog } from './CloneExamDialog';
import type { Exam } from '@/types/exam';

interface ExamCardProps {
  exam: Exam;
  currentCompanyId?: number | null;
  onEdit?: (examId: number) => void;
  onDelete?: (examId: number) => void;
  onAssign?: (examId: number) => void;
  onCloneSuccess?: (clonedExamId: number) => void;
}

export function ExamCard({
  exam,
  currentCompanyId,
  onEdit,
  onDelete,
  onAssign,
  onCloneSuccess
}: ExamCardProps) {
  const [showCloneDialog, setShowCloneDialog] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  // Check if user can clone this exam
  const canClone = () => {
    // Can clone if:
    // 1. It's a global/public exam
    // 2. It's not our own exam
    return exam.is_public && exam.company_id !== currentCompanyId;
  };

  // Check if user can edit this exam
  const canEdit = () => {
    // Can edit if it's our company's exam
    return exam.company_id === currentCompanyId;
  };

  const handleDelete = async () => {
    if (!confirm(`Are you sure you want to delete "${exam.title}"?`)) {
      return;
    }
    setIsDeleting(true);
    if (onDelete) {
      onDelete(exam.id);
    }
    setIsDeleting(false);
  };

  return (
    <>
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow hover:shadow-md transition-shadow p-6 border border-gray-200 dark:border-gray-700">
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
              {exam.title}
            </h3>
            <div className="flex items-center space-x-2 flex-wrap gap-1">
              <ExamTypeBadge exam={exam} currentCompanyId={currentCompanyId} />
              <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200 capitalize">
                {exam.exam_type}
              </span>
              <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
                exam.status === 'active'
                  ? 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200'
                  : exam.status === 'draft'
                  ? 'bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200'
              } capitalize`}>
                {exam.status}
              </span>
            </div>
          </div>
        </div>

        {/* Description */}
        {exam.description && (
          <p className="text-gray-600 dark:text-gray-300 text-sm mb-4 line-clamp-2">
            {exam.description}
          </p>
        )}

        {/* Stats */}
        <div className="grid grid-cols-2 gap-4 mb-4 text-sm">
          <div>
            <span className="text-gray-500 dark:text-gray-400">Questions:</span>
            <span className="ml-2 font-medium text-gray-900 dark:text-white">
              {exam.total_questions || 0}
            </span>
          </div>
          <div>
            <span className="text-gray-500 dark:text-gray-400">Time Limit:</span>
            <span className="ml-2 font-medium text-gray-900 dark:text-white">
              {exam.time_limit_minutes ? `${exam.time_limit_minutes} min` : 'No limit'}
            </span>
          </div>
          <div>
            <span className="text-gray-500 dark:text-gray-400">Passing Score:</span>
            <span className="ml-2 font-medium text-gray-900 dark:text-white">
              {exam.passing_score ? `${exam.passing_score}%` : 'N/A'}
            </span>
          </div>
          <div>
            <span className="text-gray-500 dark:text-gray-400">Max Attempts:</span>
            <span className="ml-2 font-medium text-gray-900 dark:text-white">
              {exam.max_attempts}
            </span>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center space-x-2">
          {canClone() && (
            <button
              onClick={() => setShowCloneDialog(true)}
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm font-medium transition-colors"
              title="Clone this exam to your company"
            >
              📋 Clone
            </button>
          )}

          {canEdit() && (
            <button
              onClick={() => onEdit?.(exam.id)}
              className="flex-1 px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 text-sm font-medium transition-colors"
              title="Edit exam"
            >
              ✏️ Edit
            </button>
          )}

          <button
            onClick={() => onAssign?.(exam.id)}
            className="flex-1 px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 text-sm font-medium transition-colors"
            title="Assign to candidates"
          >
            👥 Assign
          </button>

          {canEdit() && (
            <button
              onClick={handleDelete}
              disabled={isDeleting}
              className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 text-sm font-medium transition-colors disabled:opacity-50"
              title="Delete exam"
            >
              🗑️ Delete
            </button>
          )}
        </div>
      </div>

      {/* Clone Dialog */}
      <CloneExamDialog
        exam={exam}
        isOpen={showCloneDialog}
        onClose={() => setShowCloneDialog(false)}
        onSuccess={onCloneSuccess}
      />
    </>
  );
}
