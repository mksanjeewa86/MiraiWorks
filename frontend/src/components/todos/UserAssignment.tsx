import React, { useState, useMemo } from 'react';
import { ChevronDownIcon, UserIcon, XMarkIcon, EyeIcon, PlusIcon } from '@heroicons/react/24/outline';
import type { 
  AssignableUser, 
  TodoVisibility, 
  UserAssignmentProps,
  TodoWithAssignedUser
} from '@/types/todo';

const UserAssignment: React.FC<UserAssignmentProps> = ({
  todo,
  assignableUsers,
  onAssign,
  onUpdateViewers,
  isLoading = false
}) => {
  const [isAssignmentOpen, setIsAssignmentOpen] = useState(false);
  const [isViewersOpen, setIsViewersOpen] = useState(false);
  
  const selectedUser = useMemo(() => 
    assignableUsers.find(user => user.id === todo.assigned_user_id) || null,
    [assignableUsers, todo.assigned_user_id]
  );
  
  const selectedViewers = useMemo(() => {
    const todoWithViewers = todo as TodoWithAssignedUser;
    return todoWithViewers.viewers || [];
  }, [todo]);
  
  const [selectedVisibility, setSelectedVisibility] = useState<TodoVisibility>(todo.visibility);

  const handleAssign = (user: AssignableUser | null, visibility: TodoVisibility) => {
    setSelectedVisibility(visibility);
    onAssign({
      assigned_user_id: user?.id || null,
      visibility: visibility
    });
    setIsAssignmentOpen(false);
  };

  const handleUnassign = () => {
    handleAssign(null, 'private');
  };

  const handleAddViewer = (user: AssignableUser) => {
    if (!onUpdateViewers) return;
    
    const currentViewerIds = selectedViewers.map(v => v.user_id);
    if (!currentViewerIds.includes(user.id)) {
      onUpdateViewers({
        viewer_ids: [...currentViewerIds, user.id]
      });
    }
    setIsViewersOpen(false);
  };

  const handleRemoveViewer = (userId: number) => {
    if (!onUpdateViewers) return;
    
    const currentViewerIds = selectedViewers.map(v => v.user_id);
    onUpdateViewers({
      viewer_ids: currentViewerIds.filter(id => id !== userId)
    });
  };

  // Get available users for viewing (exclude assigned user and current viewers)
  const availableViewers = useMemo(() => {
    const assignedUserId = todo.assigned_user_id;
    const viewerUserIds = selectedViewers.map(v => v.user_id);
    
    return assignableUsers.filter(user => 
      user.id !== assignedUserId && !viewerUserIds.includes(user.id)
    );
  }, [assignableUsers, todo.assigned_user_id, selectedViewers]);

  const visibilityOptions: { value: TodoVisibility; label: string; description: string }[] = [
    {
      value: 'public',
      label: 'Full Access',
      description: 'Can view, edit, and interact with the todo'
    },
    {
      value: 'viewer',
      label: 'View Only',
      description: 'Can view the todo but cannot make changes'
    }
  ];

  return (
    <div className="relative space-y-4">
      {/* Assignment Section */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Assign To
        </label>
        
        {/* Current Assignment Display */}
        <div className="flex items-center space-x-2 mb-2">
          {selectedUser ? (
            <div className="flex items-center space-x-2 bg-blue-50 px-3 py-2 rounded-lg border border-blue-200">
              <UserIcon className="h-4 w-4 text-blue-600" />
              <span className="text-sm font-medium text-blue-900">
                {selectedUser.first_name} {selectedUser.last_name}
              </span>
              <span className="text-xs text-blue-600 bg-blue-100 px-2 py-1 rounded">
                {selectedVisibility === 'public' ? 'Full Access' : 'View Only'}
              </span>
              <button
                onClick={handleUnassign}
                disabled={isLoading}
                className="text-blue-600 hover:text-blue-800 disabled:opacity-50"
              >
                <XMarkIcon className="h-4 w-4" />
              </button>
            </div>
          ) : (
            <div className="text-sm text-gray-500 bg-gray-50 px-3 py-2 rounded-lg border border-gray-200">
              Not assigned
            </div>
          )}
        </div>

        {/* Assignment Dropdown */}
        <div className="relative">
          <button
            type="button"
            onClick={() => setIsAssignmentOpen(!isAssignmentOpen)}
            disabled={isLoading}
            className="relative w-full bg-white border border-gray-300 rounded-md pl-3 pr-10 py-2 text-left cursor-default focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500 sm:text-sm disabled:opacity-50"
          >
            <span className="block truncate">
              {selectedUser ? 'Change Assignment' : 'Assign to user'}
            </span>
            <span className="absolute inset-y-0 right-0 flex items-center pr-2 pointer-events-none">
              <ChevronDownIcon className="h-5 w-5 text-gray-400" aria-hidden="true" />
            </span>
          </button>

          {isAssignmentOpen && (
          <div className="absolute z-10 mt-1 w-full bg-white shadow-lg max-h-96 rounded-md py-1 text-base ring-1 ring-black ring-opacity-5 overflow-auto focus:outline-none sm:text-sm">
            {/* Unassign Option */}
            {selectedUser && (
              <>
                <button
                  onClick={handleUnassign}
                  className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 flex items-center space-x-2"
                >
                  <XMarkIcon className="h-4 w-4" />
                  <span>Unassign</span>
                </button>
                <div className="border-t border-gray-100 my-1"></div>
              </>
            )}

            {/* User List */}
            {assignableUsers.length === 0 ? (
              <div className="px-4 py-2 text-sm text-gray-500">
                No users available for assignment
              </div>
            ) : (
              assignableUsers.map((user) => (
                <div key={user.id} className="border-b border-gray-50 last:border-b-0">
                  <div className="px-4 py-2">
                    <div className="flex items-center space-x-2 mb-2">
                      <UserIcon className="h-4 w-4 text-gray-400" />
                      <div>
                        <div className="text-sm font-medium text-gray-900">
                          {user.first_name} {user.last_name}
                        </div>
                        <div className="text-xs text-gray-500">{user.email}</div>
                      </div>
                    </div>
                    
                    {/* Visibility Options for this user */}
                    <div className="ml-6 space-y-1">
                      {visibilityOptions.map((option) => (
                        <button
                          key={option.value}
                          onClick={() => handleAssign(user, option.value)}
                          className="w-full text-left px-2 py-1 text-xs rounded hover:bg-gray-50 flex flex-col"
                        >
                          <span className="font-medium text-gray-700">{option.label}</span>
                          <span className="text-gray-500">{option.description}</span>
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        )}
        
        {/* Click outside to close assignment dropdown */}
        {isAssignmentOpen && (
          <div
            className="fixed inset-0 z-0"
            onClick={() => setIsAssignmentOpen(false)}
          />
        )}
      </div>
      </div>

      {/* Viewers Section */}
      {onUpdateViewers && (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Additional Viewers (View Only)
          </label>
          
          {/* Current Viewers Display */}
          <div className="space-y-2 mb-2">
            {selectedViewers.length > 0 ? (
              selectedViewers.map((viewer) => (
                <div key={viewer.id} className="flex items-center space-x-2 bg-green-50 px-3 py-2 rounded-lg border border-green-200">
                  <EyeIcon className="h-4 w-4 text-green-600" />
                  <span className="text-sm font-medium text-green-900">
                    {viewer.user.first_name} {viewer.user.last_name}
                  </span>
                  <span className="text-xs text-green-600 bg-green-100 px-2 py-1 rounded">
                    Viewer
                  </span>
                  <button
                    onClick={() => handleRemoveViewer(viewer.user_id)}
                    disabled={isLoading}
                    className="text-green-600 hover:text-green-800 disabled:opacity-50"
                  >
                    <XMarkIcon className="h-4 w-4" />
                  </button>
                </div>
              ))
            ) : (
              <div className="text-sm text-gray-500 bg-gray-50 px-3 py-2 rounded-lg border border-gray-200">
                No additional viewers
              </div>
            )}
          </div>

          {/* Add Viewers Dropdown */}
          <div className="relative">
            <button
              type="button"
              onClick={() => setIsViewersOpen(!isViewersOpen)}
              disabled={isLoading || availableViewers.length === 0}
              className="relative w-full bg-white border border-gray-300 rounded-md pl-3 pr-10 py-2 text-left cursor-default focus:outline-none focus:ring-1 focus:ring-green-500 focus:border-green-500 sm:text-sm disabled:opacity-50"
            >
              <span className="flex items-center space-x-2">
                <PlusIcon className="h-4 w-4 text-gray-400" />
                <span className="block truncate">
                  {availableViewers.length === 0 ? 'No users available to add' : 'Add viewer'}
                </span>
              </span>
              <span className="absolute inset-y-0 right-0 flex items-center pr-2 pointer-events-none">
                <ChevronDownIcon className="h-5 w-5 text-gray-400" aria-hidden="true" />
              </span>
            </button>

            {isViewersOpen && availableViewers.length > 0 && (
              <div className="absolute z-10 mt-1 w-full bg-white shadow-lg max-h-60 rounded-md py-1 text-base ring-1 ring-black ring-opacity-5 overflow-auto focus:outline-none sm:text-sm">
                {availableViewers.map((user) => (
                  <button
                    key={user.id}
                    onClick={() => handleAddViewer(user)}
                    className="w-full text-left px-4 py-2 text-sm hover:bg-green-50 flex items-center space-x-2"
                  >
                    <EyeIcon className="h-4 w-4 text-gray-400" />
                    <div>
                      <div className="font-medium text-gray-900">
                        {user.first_name} {user.last_name}
                      </div>
                      <div className="text-xs text-gray-500">{user.email}</div>
                    </div>
                  </button>
                ))}
              </div>
            )}
            
            {/* Click outside to close viewers dropdown */}
            {isViewersOpen && (
              <div
                className="fixed inset-0 z-0"
                onClick={() => setIsViewersOpen(false)}
              />
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default UserAssignment;