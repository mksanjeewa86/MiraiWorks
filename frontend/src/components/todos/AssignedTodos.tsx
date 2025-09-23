import React, { useState, useEffect } from 'react';
import { UserIcon, InboxIcon, CheckCircleIcon } from '@heroicons/react/24/outline';
import { useToast } from '@/contexts/ToastContext';
import { todosApi } from '@/api/todos';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import { TodoItem } from './TodoItem';
import useTodoPermissions from '@/hooks/useTodoPermissions';
import type { Todo, TodoListResponse, TodoWithAssignedUser, AssignedTodosProps } from '@/types/todo';

const AssignedTodos: React.FC<AssignedTodosProps> = ({
  onEditTodo,
  onViewAttachments
}) => {
  const { showToast } = useToast();
  const [assignedTodos, setAssignedTodos] = useState<Todo[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState<number | null>(null);
  const [includeCompleted, setIncludeCompleted] = useState(false);

  // Load assigned todos
  const loadAssignedTodos = async () => {
    try {
      setLoading(true);
      const response: TodoListResponse = await todosApi.listAssignedTodos({
        includeCompleted,
        limit: 50
      });
      setAssignedTodos(response.items);
    } catch (error) {
      console.error('Failed to load assigned todos:', error);
      showToast({
        type: 'error',
        title: 'Failed to load assigned todos'
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAssignedTodos();
  }, [includeCompleted]);

  const handleToggleComplete = async (todo: Todo) => {
    const permissions = useTodoPermissions(todo);
    if (!permissions.canChangeStatus) {
      showToast({
        type: 'error',
        title: 'You don\'t have permission to change this todo\'s status'
      });
      return;
    }

    setActionLoading(todo.id);
    try {
      if (todo.status === 'completed') {
        await todosApi.reopen(todo.id);
        showToast({ type: 'success', title: 'Todo reopened' });
      } else {
        await todosApi.complete(todo.id);
        showToast({ type: 'success', title: 'Todo completed' });
      }
      await loadAssignedTodos();
    } catch (error) {
      showToast({
        type: 'error',
        title: error instanceof Error ? error.message : 'Failed to update todo'
      });
    } finally {
      setActionLoading(null);
    }
  };

  const handleEdit = (todo: Todo) => {
    const permissions = useTodoPermissions(todo);
    if (!permissions.canEdit) {
      showToast({
        type: 'error',
        title: 'You don\'t have permission to edit this todo'
      });
      return;
    }
    onEditTodo?.(todo);
  };

  const handleDelete = async (todo: Todo) => {
    const permissions = useTodoPermissions(todo);
    if (!permissions.canDelete) {
      showToast({
        type: 'error',
        title: 'You don\'t have permission to delete this todo'
      });
      return;
    }

    if (!confirm('Are you sure you want to delete this todo?')) {
      return;
    }

    setActionLoading(todo.id);
    try {
      await todosApi.remove(todo.id);
      showToast({ type: 'success', title: 'Todo deleted' });
      await loadAssignedTodos();
    } catch (error) {
      showToast({
        type: 'error',
        title: error instanceof Error ? error.message : 'Failed to delete todo'
      });
    } finally {
      setActionLoading(null);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <UserIcon className="h-6 w-6 text-blue-600" />
          <div>
            <h2 className="text-xl font-semibold text-gray-900">Assigned to Me</h2>
            <p className="text-sm text-gray-500">
              Tasks that have been assigned to you by others
            </p>
          </div>
        </div>
        
        {/* Filter Toggle */}
        <div className="flex items-center space-x-2">
          <label className="flex items-center space-x-2 text-sm">
            <input
              type="checkbox"
              checked={includeCompleted}
              onChange={(e) => setIncludeCompleted(e.target.checked)}
              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span>Show completed</span>
          </label>
        </div>
      </div>

      {/* Todo List */}
      {assignedTodos.length === 0 ? (
        <div className="text-center py-12">
          <InboxIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-4 text-lg font-medium text-gray-900">
            No assigned todos
          </h3>
          <p className="mt-2 text-sm text-gray-500">
            {includeCompleted 
              ? "You don't have any assigned todos." 
              : "You don't have any pending assigned todos."
            }
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {assignedTodos.map((todo) => (
            <div key={todo.id} className="relative">
              {actionLoading === todo.id && (
                <div className="absolute inset-0 bg-white bg-opacity-50 flex items-center justify-center z-10 rounded-lg">
                  <LoadingSpinner size="sm" />
                </div>
              )}
              <TodoItem
                todo={todo}
                onToggleComplete={handleToggleComplete}
                onEdit={handleEdit}
                onDelete={handleDelete}
                onViewAttachments={onViewAttachments}
                attachmentCount={0} // TODO: Add attachment counts
                totalAttachmentSize={0}
              />
            </div>
          ))}
        </div>
      )}

      {/* Stats */}
      {assignedTodos.length > 0 && (
        <div className="mt-6 text-center text-sm text-gray-500">
          {assignedTodos.filter(t => t.status === 'completed').length} of {assignedTodos.length} completed
        </div>
      )}
    </div>
  );
};

export default AssignedTodos;