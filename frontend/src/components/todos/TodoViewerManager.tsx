'use client';

import { useState } from 'react';
import { Eye, UserPlus, X, Trash2, Users, AlertCircle } from 'lucide-react';
import { useTodoViewers } from '@/hooks/useTodoViewers';
import type { ConnectedUser } from '@/types/user';
import type { TodoViewerWithUser } from '@/types/todo-viewer';

interface TodoViewerManagerProps {
  todoId: number;
  isCreator: boolean;
  availableUsers: ConnectedUser[];
  assigneeId?: number | null;
  onRemoveViewer: (viewerUserId: number, viewerName: string, refetchFn: () => Promise<void>) => void;
}

/**
 * Component for managing todo viewers (creator only)
 *
 * Features:
 * - Display list of viewers (creator only)
 * - Add viewers from available users
 * - Remove viewers
 */
export const TodoViewerManager: React.FC<TodoViewerManagerProps> = ({
  todoId,
  isCreator,
  availableUsers,
  assigneeId,
  onRemoveViewer,
}) => {
  const {
    viewers,
    total,
    isLoading,
    addViewer,
    isAddingViewer,
    addViewerError,
    refetch,
  } = useTodoViewers(todoId);

  const [selectedUserId, setSelectedUserId] = useState<number | null>(null);
  const [showAddForm, setShowAddForm] = useState(false);

  // Only creator can manage viewers
  if (!isCreator) {
    return null;
  }

  const handleAddViewer = () => {
    if (selectedUserId) {
      addViewer(
        { user_id: selectedUserId },
        {
          onSuccess: () => {
            setSelectedUserId(null);
            setShowAddForm(false);
          },
        }
      );
    }
  };

  const handleRemoveViewer = (viewer: TodoViewerWithUser) => {
    onRemoveViewer(viewer.user_id, viewer.user.full_name || viewer.user.email, refetch);
  };

  // Filter out users who are already viewers or the assignee
  const viewerUserIds = new Set(viewers.map((v: { user_id: number }) => v.user_id));
  const availableToAdd = availableUsers.filter((user) => {
    // Exclude if already a viewer
    if (viewerUserIds.has(user.id)) return false;
    // Exclude if user is the assignee
    if (assigneeId && user.id === assigneeId) return false;
    return true;
  });

  return (
    <div className="rounded-2xl border border-slate-200 bg-gradient-to-br from-slate-50 to-slate-100/50 p-6 shadow-sm">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-teal-500 to-cyan-600 shadow-lg shadow-teal-500/30">
            <Eye className="h-5 w-5 text-white" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-slate-900">Shared With</h3>
            <p className="text-xs text-slate-500">{total} {total === 1 ? 'viewer' : 'viewers'}</p>
          </div>
        </div>
        {!showAddForm && availableToAdd.length > 0 && (
          <button
            type="button"
            onClick={() => setShowAddForm(true)}
            className="group flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-gradient-to-r from-teal-500 to-cyan-600 rounded-lg hover:from-teal-600 hover:to-cyan-700 shadow-md shadow-teal-500/30 transition-all duration-200 hover:shadow-lg hover:scale-105"
          >
            <UserPlus className="h-4 w-4" />
            Add Viewer
          </button>
        )}
      </div>

      {/* Add viewer form */}
      {showAddForm && (
        <div className="mb-4 rounded-xl border border-teal-200 bg-gradient-to-br from-teal-50 to-cyan-50 p-4 shadow-sm">
          <div className="flex items-center gap-2 mb-3">
            <Users className="h-4 w-4 text-teal-600" />
            <h4 className="text-sm font-semibold text-slate-900">Add New Viewer</h4>
          </div>
          <div className="flex gap-2">
            <select
              value={selectedUserId || ''}
              onChange={(e) => setSelectedUserId(Number(e.target.value))}
              className="flex-1 px-3 py-2 text-sm border border-slate-300 rounded-lg bg-white text-slate-900 focus:border-teal-500 focus:outline-none focus:ring-2 focus:ring-teal-500/20 disabled:bg-slate-100 disabled:cursor-not-allowed"
              disabled={isAddingViewer}
            >
              <option value="">Select a user...</option>
              {availableToAdd.map((user) => (
                <option key={user.id} value={user.id}>
                  {user.full_name || user.email}
                </option>
              ))}
            </select>
            <button
              type="button"
              onClick={handleAddViewer}
              disabled={!selectedUserId || isAddingViewer}
              className="px-4 py-2 text-sm font-medium text-white bg-gradient-to-r from-teal-500 to-cyan-600 rounded-lg hover:from-teal-600 hover:to-cyan-700 disabled:from-slate-400 disabled:to-slate-400 disabled:cursor-not-allowed shadow-sm transition-all duration-200"
            >
              {isAddingViewer ? 'Adding...' : 'Add'}
            </button>
            <button
              type="button"
              onClick={() => {
                setShowAddForm(false);
                setSelectedUserId(null);
              }}
              disabled={isAddingViewer}
              className="p-2 text-slate-600 hover:text-slate-900 hover:bg-slate-200 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
          {addViewerError && (
            <div className="mt-3 flex items-start gap-2 text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg p-2">
              <span>⚠️</span>
              <span>Error: {addViewerError instanceof Error ? addViewerError.message : 'Failed to add viewer'}</span>
            </div>
          )}
        </div>
      )}

      {/* Viewers list */}
      {isLoading ? (
        <div className="flex items-center justify-center py-8">
          <div className="flex items-center gap-2 text-sm text-slate-500">
            <div className="h-4 w-4 border-2 border-teal-500 border-t-transparent rounded-full animate-spin"></div>
            Loading viewers...
          </div>
        </div>
      ) : viewers.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-8 text-center">
          <div className="flex h-16 w-16 items-center justify-center rounded-full bg-slate-200 mb-3">
            <Users className="h-8 w-8 text-slate-400" />
          </div>
          <p className="text-sm font-medium text-slate-700 mb-1">No viewers yet</p>
          <p className="text-xs text-slate-500">Add viewers to share this todo with view-only access</p>
        </div>
      ) : (
        <div className="space-y-2">
          {viewers.map((viewer: TodoViewerWithUser) => (
            <div
              key={viewer.id}
              className="group flex items-center justify-between p-3 rounded-xl bg-white border border-slate-200 hover:border-teal-300 hover:shadow-md transition-all duration-200"
            >
              <div className="flex items-center gap-3 flex-1 min-w-0">
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-slate-200 to-slate-300 flex-shrink-0">
                  <span className="text-sm font-semibold text-slate-700">
                    {(viewer.user.full_name || viewer.user.email).charAt(0).toUpperCase()}
                  </span>
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-semibold text-slate-900 truncate">
                    {viewer.user.full_name || viewer.user.email}
                  </p>
                  <p className="text-xs text-slate-500 truncate">{viewer.user.email}</p>
                  <div className="flex items-center gap-1 mt-1">
                    <Eye className="h-3 w-3 text-teal-500" />
                    <p className="text-xs text-slate-400">
                      Added {new Date(viewer.created_at).toLocaleDateString()}
                    </p>
                  </div>
                </div>
              </div>
              <button
                type="button"
                onClick={() => handleRemoveViewer(viewer)}
                className="flex items-center gap-1 px-3 py-1.5 text-xs font-medium text-red-600 hover:text-red-700 hover:bg-red-50 rounded-lg transition-all duration-200 opacity-0 group-hover:opacity-100"
              >
                <Trash2 className="h-3 w-3" />
                Remove
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default TodoViewerManager;
