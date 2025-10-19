import React, { useState } from 'react';
import {
  CheckCircleIcon,
  ClockIcon,
  PaperClipIcon,
  PencilIcon,
  TrashIcon,
  CalendarIcon,
  ExclamationTriangleIcon,
} from '@heroicons/react/24/outline';
import { CheckCircleIcon as CheckCircleIconSolid } from '@heroicons/react/24/solid';
import type { Todo, TodoItemProps } from '@/types/todo';
import { formatFileSize } from '@/types/todo-attachment';
import useTodoPermissions from '@/hooks/useTodoPermissions';

export const TodoItem: React.FC<TodoItemProps> = ({
  todo,
  onToggleComplete,
  onEdit,
  onDelete,
  onViewAttachments,
  attachmentCount = 0,
  totalAttachmentSize = 0,
}) => {
  const [isHovered, setIsHovered] = useState(false);
  const permissions = useTodoPermissions(todo);

  const isCompleted = todo.status === 'completed';

  // Check if task is overdue
  const isOverdue = React.useMemo(() => {
    if (!todo.due_datetime || isCompleted) return false;

    const now = new Date();
    const dueDateTime = new Date(todo.due_datetime);

    return dueDateTime < now;
  }, [todo.due_datetime, isCompleted]);

  const formatDueDate = (datetimeString: string) => {
    const date = new Date(datetimeString);
    const now = new Date();

    const diffTime = date.getTime() - now.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    const dateStr = date.toLocaleDateString();
    const timeStr = ` at ${date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;

    if (diffDays === 0) return `Due today${timeStr}`;
    if (diffDays === 1) return `Due tomorrow${timeStr}`;
    if (diffDays === -1) return `Due yesterday${timeStr}`;
    if (diffDays < 0) return `Overdue by ${Math.abs(diffDays)} days`;
    if (diffDays <= 7) return `Due in ${diffDays} days${timeStr}`;

    return `${dateStr}${timeStr}`;
  };

  const getPriorityColor = (priority?: string) => {
    if (!priority) return 'bg-gray-100 text-gray-600';

    switch (priority.toLowerCase()) {
      case 'high':
        return 'bg-red-100 text-red-700';
      case 'mid':
      case 'medium':
        return 'bg-yellow-100 text-yellow-700';
      case 'low':
        return 'bg-green-100 text-green-700';
      default:
        return 'bg-gray-100 text-gray-600';
    }
  };

  return (
    <div
      className={`
        group relative bg-white rounded-lg shadow-sm border border-gray-200 
        hover:shadow-md transition-all duration-200 p-4
        ${isCompleted ? 'opacity-60' : ''}
        ${isOverdue ? 'border-red-200 bg-red-50' : ''}
      `}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <div className="flex items-start space-x-3">
        {/* Completion Toggle */}
        {permissions.canChangeStatus ? (
          <button
            onClick={() => onToggleComplete?.(todo)}
            className={`
              flex-shrink-0 mt-1 p-1 rounded-full transition-colors
              ${
                isCompleted
                  ? 'text-green-600 hover:text-green-700'
                  : 'text-gray-400 hover:text-green-600'
              }
            `}
          >
            {isCompleted ? (
              <CheckCircleIconSolid className="h-5 w-5" />
            ) : (
              <CheckCircleIcon className="h-5 w-5" />
            )}
          </button>
        ) : (
          <div className="flex-shrink-0 mt-1 p-1">
            {isCompleted ? (
              <CheckCircleIconSolid className="h-5 w-5 text-green-600" />
            ) : (
              <CheckCircleIcon className="h-5 w-5 text-gray-300" />
            )}
          </div>
        )}

        {/* Content */}
        <div className="flex-1 min-w-0">
          {/* Title */}
          <h3
            className={`
            text-sm font-medium transition-all
            ${isCompleted ? 'line-through text-gray-500' : 'text-gray-900'}
          `}
          >
            {todo.title}
          </h3>

          {/* Description */}
          {todo.description && (
            <p className="mt-1 text-xs text-gray-600 line-clamp-2">{todo.description}</p>
          )}

          {/* Meta Information */}
          <div className="mt-2 flex flex-wrap items-center gap-2 text-xs">
            {/* Overdue Badge */}
            {isOverdue && (
              <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full bg-red-100 text-red-700 font-medium">
                <ExclamationTriangleIcon className="h-3 w-3" />
                Overdue
              </span>
            )}

            {/* Priority Badge */}
            {todo.priority && (
              <span
                className={`
                inline-flex items-center px-2 py-1 rounded-full text-xs font-medium
                ${getPriorityColor(todo.priority)}
              `}
              >
                {todo.priority}
              </span>
            )}

            {/* Due Date */}
            {todo.due_datetime && (
              <span
                className={`
                inline-flex items-center gap-1 px-2 py-1 rounded-full
                ${isOverdue ? 'bg-red-50 text-red-600' : 'bg-blue-50 text-blue-700'}
              `}
              >
                <CalendarIcon className="h-3 w-3" />
                {formatDueDate(todo.due_datetime)}
              </span>
            )}

            {/* Attachments */}
            {attachmentCount > 0 && (
              <button
                onClick={() => onViewAttachments?.(todo)}
                className="inline-flex items-center gap-1 px-2 py-1 rounded-full bg-gray-100 text-gray-700 hover:bg-gray-200 transition-colors"
              >
                <PaperClipIcon className="h-3 w-3" />
                <span>
                  {attachmentCount} file{attachmentCount !== 1 ? 's' : ''}
                </span>
              </button>
            )}

            {/* Created Date */}
            <span className="inline-flex items-center gap-1 text-gray-500">
              <ClockIcon className="h-3 w-3" />
              {new Date(todo.created_at).toLocaleDateString()}
            </span>
          </div>
        </div>

        {/* Actions */}
        <div
          className={`
          flex items-center space-x-1 transition-opacity
          ${isHovered ? 'opacity-100' : 'opacity-0'}
        `}
        >
          {permissions.canEdit && (
            <button
              onClick={() => onEdit(todo)}
              className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded transition-colors"
              title="Edit task"
            >
              <PencilIcon className="h-4 w-4" />
            </button>
          )}

          {attachmentCount > 0 && onViewAttachments && permissions.canView && (
            <button
              onClick={() => onViewAttachments(todo)}
              className="p-2 text-gray-400 hover:text-green-600 hover:bg-green-50 rounded transition-colors"
              title="View attachments"
            >
              <PaperClipIcon className="h-4 w-4" />
            </button>
          )}

          {permissions.canDelete && (
            <button
              onClick={() => onDelete(todo)}
              className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded transition-colors"
              title="Delete task"
            >
              <TrashIcon className="h-4 w-4" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
