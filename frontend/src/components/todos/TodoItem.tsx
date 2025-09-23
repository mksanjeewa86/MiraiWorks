import React, { useState } from 'react';
import {
  CheckCircleIcon,
  ClockIcon,
  PaperClipIcon,
  PencilIcon,
  TrashIcon,
  CalendarIcon,
  ExclamationTriangleIcon,
  UserIcon,
  EyeIcon,
  PencilSquareIcon,
  LockClosedIcon,
} from '@heroicons/react/24/outline';
import { CheckCircleIcon as CheckCircleIconSolid } from '@heroicons/react/24/solid';
import type { Todo, TodoWithAssignedUser, TodoItemProps } from '@/types/todo';
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
  const isOverdue = todo.due_date && new Date(todo.due_date) < new Date() && !isCompleted;
  const assignedUser = 'assigned_user' in todo ? todo.assigned_user : null;
  
  const formatDueDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = date.getTime() - now.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) return 'Due today';
    if (diffDays === 1) return 'Due tomorrow';
    if (diffDays === -1) return 'Due yesterday';
    if (diffDays < 0) return `Overdue by ${Math.abs(diffDays)} days`;
    if (diffDays <= 7) return `Due in ${diffDays} days`;
    
    return date.toLocaleDateString();
  };

  const getPriorityColor = (priority?: string) => {
    if (!priority) return 'bg-gray-100 text-gray-600';
    
    switch (priority.toLowerCase()) {
      case 'high':
        return 'bg-red-100 text-red-700';
      case 'medium':
        return 'bg-yellow-100 text-yellow-700';
      case 'low':
        return 'bg-green-100 text-green-700';
      default:
        return 'bg-gray-100 text-gray-600';
    }
  };

  const getVisibilityIcon = () => {
    switch (todo.visibility) {
      case 'public':
        return <PencilSquareIcon className="h-3 w-3 text-green-600" />;
      case 'viewer':
        return <EyeIcon className="h-3 w-3 text-blue-600" />;
      default:
        return <LockClosedIcon className="h-3 w-3 text-gray-500" />;
    }
  };

  const getVisibilityLabel = () => {
    switch (todo.visibility) {
      case 'public':
        return 'Full Access';
      case 'viewer':
        return 'View Only';
      default:
        return 'Private';
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
            onClick={() => onToggleComplete(todo)}
            className={`
              flex-shrink-0 mt-1 p-1 rounded-full transition-colors
              ${isCompleted 
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
          <h3 className={`
            text-sm font-medium transition-all
            ${isCompleted 
              ? 'line-through text-gray-500' 
              : 'text-gray-900'
            }
          `}>
            {todo.title}
          </h3>

          {/* Description */}
          {todo.description && (
            <p className="mt-1 text-xs text-gray-600 line-clamp-2">
              {todo.description}
            </p>
          )}

          {/* Meta Information */}
          <div className="mt-2 flex items-center space-x-4 text-xs text-gray-500">
            {/* Assignment Status */}
            {assignedUser && (
              <div className="flex items-center space-x-1">
                <UserIcon className="h-3 w-3" />
                <span className="text-blue-600 font-medium">
                  {assignedUser.first_name} {assignedUser.last_name}
                </span>
                <div className="flex items-center space-x-1 ml-1">
                  {getVisibilityIcon()}
                  <span className="text-xs" title={getVisibilityLabel()}>
                    {todo.visibility === 'public' ? 'Full' : todo.visibility === 'viewer' ? 'View' : 'Private'}
                  </span>
                </div>
              </div>
            )}

            {/* Due Date */}
            {todo.due_date && (
              <div className={`
                flex items-center space-x-1
                ${isOverdue ? 'text-red-600' : ''}
              `}>
                {isOverdue ? (
                  <ExclamationTriangleIcon className="h-3 w-3" />
                ) : (
                  <CalendarIcon className="h-3 w-3" />
                )}
                <span>{formatDueDate(todo.due_date)}</span>
              </div>
            )}

            {/* Priority */}
            {todo.priority && (
              <span className={`
                px-2 py-1 rounded-full text-xs font-medium
                ${getPriorityColor(todo.priority)}
              `}>
                {todo.priority}
              </span>
            )}

            {/* Attachments */}
            {attachmentCount > 0 && (
              <button
                onClick={() => onViewAttachments?.(todo)}
                className="flex items-center space-x-1 hover:text-blue-600 transition-colors"
              >
                <PaperClipIcon className="h-3 w-3" />
                <span>
                  {attachmentCount} file{attachmentCount !== 1 ? 's' : ''}
                  {totalAttachmentSize > 0 && (
                    <span className="text-gray-400">
                      {' '}• {formatFileSize(totalAttachmentSize)}
                    </span>
                  )}
                </span>
              </button>
            )}

            {/* Created Date */}
            <div className="flex items-center space-x-1">
              <ClockIcon className="h-3 w-3" />
              <span>
                {new Date(todo.created_at).toLocaleDateString()}
              </span>
            </div>
          </div>

          {/* Notes Preview */}
          {todo.notes && (
            <div className="mt-2 p-2 bg-gray-50 rounded text-xs text-gray-600">
              <span className="font-medium">Note:</span> {todo.notes}
            </div>
          )}
        </div>

        {/* Actions */}
        <div className={`
          flex items-center space-x-1 transition-opacity
          ${isHovered ? 'opacity-100' : 'opacity-0'}
        `}>
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