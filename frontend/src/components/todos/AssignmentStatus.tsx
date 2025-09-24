import React from 'react';
import { UserIcon, EyeIcon, PencilSquareIcon, LockClosedIcon } from '@heroicons/react/24/outline';
import type { AssignmentStatusProps } from '@/types/todo';

const AssignmentStatus: React.FC<AssignmentStatusProps> = ({ todo, permissions }) => {
  const assignedUser = 'assigned_user' in todo ? todo.assigned_user : null;

  if (!assignedUser) {
    return (
      <div className="flex items-center space-x-2 text-gray-500 text-sm">
        <LockClosedIcon className="h-4 w-4" />
        <span>Private</span>
      </div>
    );
  }

  const getVisibilityIcon = () => {
    switch (todo.visibility) {
      case 'public':
        return <PencilSquareIcon className="h-4 w-4 text-green-600" />;
      case 'viewer':
        return <EyeIcon className="h-4 w-4 text-blue-600" />;
      default:
        return <LockClosedIcon className="h-4 w-4 text-gray-500" />;
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

  const getVisibilityColor = () => {
    switch (todo.visibility) {
      case 'public':
        return 'text-green-700 bg-green-50 border-green-200';
      case 'viewer':
        return 'text-blue-700 bg-blue-50 border-blue-200';
      default:
        return 'text-gray-700 bg-gray-50 border-gray-200';
    }
  };

  return (
    <div className="space-y-2">
      {/* Assigned User Info */}
      <div className="flex items-center space-x-2">
        <UserIcon className="h-4 w-4 text-gray-600" />
        <div className="flex flex-col">
          <span className="text-sm font-medium text-gray-900">
            {assignedUser.first_name} {assignedUser.last_name}
          </span>
          <span className="text-xs text-gray-500">{assignedUser.email}</span>
        </div>
      </div>

      {/* Visibility Status */}
      <div
        className={`inline-flex items-center space-x-1 px-2 py-1 rounded-lg border text-xs font-medium ${getVisibilityColor()}`}
      >
        {getVisibilityIcon()}
        <span>{getVisibilityLabel()}</span>
      </div>

      {/* Permission Indicators (for debugging/admin view) */}
      {process.env.NODE_ENV === 'development' && (
        <div className="text-xs text-gray-400 border-t pt-2">
          <div className="grid grid-cols-2 gap-1">
            <span className={permissions.canView ? 'text-green-600' : 'text-red-600'}>
              View: {permissions.canView ? '✓' : '✗'}
            </span>
            <span className={permissions.canEdit ? 'text-green-600' : 'text-red-600'}>
              Edit: {permissions.canEdit ? '✓' : '✗'}
            </span>
            <span className={permissions.canDelete ? 'text-green-600' : 'text-red-600'}>
              Delete: {permissions.canDelete ? '✓' : '✗'}
            </span>
            <span className={permissions.canAssign ? 'text-green-600' : 'text-red-600'}>
              Assign: {permissions.canAssign ? '✓' : '✗'}
            </span>
          </div>
        </div>
      )}
    </div>
  );
};

export default AssignmentStatus;
