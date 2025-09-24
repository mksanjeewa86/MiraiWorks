'use client';

import { useState, useEffect } from 'react';
import { X, Plus, Save, ClipboardList } from 'lucide-react';
import Button from '@/components/ui/button';
import Input from '@/components/ui/input';
import Badge from '@/components/ui/badge';
import { useToast } from '@/contexts/ToastContext';
import { useAuth } from '@/contexts/AuthContext';
import { todosApi } from '@/api/todos';
import UserAssignment from './UserAssignment';
import { getTodoPermissions } from '@/utils/todoPermissions';
import type {
  Todo,
  TodoPayload,
  TaskFormState,
  TaskModalProps,
  AssignableUser,
  TodoAssignmentUpdate,
} from '@/types/todo';

const initialFormState: TaskFormState = {
  title: '',
  description: '',
  notes: '',
  dueDate: '',
  priority: '',
};

function formatDateForInput(input?: string | null): string {
  if (!input) return '';
  const date = new Date(input);
  if (Number.isNaN(date.getTime())) return '';
  const off = date.getTimezoneOffset();
  const local = new Date(date.getTime() - off * 60_000);
  return local.toISOString().slice(0, 16);
}

export default function TaskModal({ isOpen, onClose, onSuccess, editingTodo }: TaskModalProps) {
  const { showToast } = useToast();
  const { user } = useAuth();
  const [formState, setFormState] = useState<TaskFormState>(initialFormState);
  const [submitting, setSubmitting] = useState(false);
  const [assignableUsers, setAssignableUsers] = useState<AssignableUser[]>([]);
  const [loadingUsers, setLoadingUsers] = useState(false);
  const [assignment, setAssignment] = useState<TodoAssignmentUpdate>({});

  const isEditing = !!editingTodo;
  const permissions = editingTodo ? getTodoPermissions(editingTodo, user) : null;
  const canAssign = permissions?.canAssign || !isEditing; // Any user can assign when creating

  // Load assignable users when modal opens
  useEffect(() => {
    if (isOpen && canAssign) {
      const loadUsers = async () => {
        setLoadingUsers(true);
        try {
          const users = await todosApi.getAssignableUsers();
          setAssignableUsers(users);
        } catch (error) {
          console.error('Failed to load assignable users:', error);
          showToast({
            type: 'error',
            title: 'Failed to load users for assignment',
          });
        } finally {
          setLoadingUsers(false);
        }
      };
      loadUsers();
    }
  }, [isOpen, canAssign, showToast]);

  // Reset form when modal opens/closes or when editing todo changes
  useEffect(() => {
    if (isOpen) {
      if (editingTodo) {
        setFormState({
          title: editingTodo.title,
          description: editingTodo.description ?? '',
          notes: editingTodo.notes ?? '',
          dueDate: formatDateForInput(editingTodo.due_date),
          priority: editingTodo.priority ?? '',
        });
        setAssignment({
          assigned_user_id: editingTodo.assigned_user_id,
          visibility: editingTodo.visibility,
        });
      } else {
        setFormState(initialFormState);
        setAssignment({});
      }
    }
  }, [isOpen, editingTodo]);

  const handleInputChange =
    (field: keyof TaskFormState) =>
    (event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
      setFormState((prev) => ({ ...prev, [field]: event.target.value }));
    };

  const handleAssignmentChange = (assignmentData: TodoAssignmentUpdate) => {
    setAssignment(assignmentData);
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const trimmedTitle = formState.title.trim();
    if (!trimmedTitle) {
      showToast({ type: 'error', title: 'Title is required' });
      return;
    }

    const payload: TodoPayload = {
      title: trimmedTitle,
      description: formState.description.trim() || undefined,
      notes: formState.notes.trim() || undefined,
      priority: formState.priority.trim() || undefined,
      due_date: formState.dueDate ? new Date(formState.dueDate).toISOString() : undefined,
      ...(canAssign && {
        assigned_user_id: assignment.assigned_user_id,
        visibility: assignment.visibility,
      }),
    };

    setSubmitting(true);
    try {
      if (isEditing && editingTodo) {
        await todosApi.update(editingTodo.id, payload);

        // Handle assignment separately if it changed and user can assign
        if (
          canAssign &&
          permissions?.canAssign &&
          (assignment.assigned_user_id !== editingTodo.assigned_user_id ||
            assignment.visibility !== editingTodo.visibility)
        ) {
          await todosApi.assignTodo(editingTodo.id, assignment);
        }

        showToast({ type: 'success', title: 'Task updated successfully' });
      } else {
        await todosApi.create(payload);
        showToast({ type: 'success', title: 'Task created successfully' });
      }
      onSuccess();
      onClose();
    } catch (err) {
      console.error(err);
      showToast({
        type: 'error',
        title:
          err instanceof Error ? err.message : `Failed to ${isEditing ? 'update' : 'create'} task`,
      });
    } finally {
      setSubmitting(false);
    }
  };

  const handleClose = () => {
    if (!submitting) {
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen p-4">
        {/* Backdrop */}
        <div
          className="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
          onClick={handleClose}
        />

        {/* Modal */}
        <div className="relative bg-white dark:bg-gray-800 rounded-2xl shadow-xl max-w-lg w-full max-h-[90vh] overflow-y-auto border border-gray-200 dark:border-gray-700">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-500/20 text-blue-600 dark:bg-blue-500/25 dark:text-blue-200">
                <ClipboardList className="h-5 w-5" />
              </div>
              <div>
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                  {isEditing ? 'Update Task' : 'Create New Task'}
                </h2>
                {isEditing && (
                  <Badge variant="secondary" size="sm" className="mt-1">
                    Editing
                  </Badge>
                )}
              </div>
            </div>
            <button
              onClick={handleClose}
              disabled={submitting}
              className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors disabled:opacity-50"
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="p-6 space-y-6">
            <div>
              <Input
                label="Title"
                placeholder="What needs to get done?"
                value={formState.title}
                onChange={handleInputChange('title')}
                required
                autoFocus
              />
            </div>

            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Due Date
                </label>
                <input
                  type="datetime-local"
                  value={formState.dueDate}
                  onChange={handleInputChange('dueDate')}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                />
              </div>
              <div>
                <Input
                  label="Priority"
                  placeholder="e.g., High, Medium, Low"
                  value={formState.priority}
                  onChange={handleInputChange('priority')}
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Description
              </label>
              <textarea
                value={formState.description}
                onChange={handleInputChange('description')}
                placeholder="Add more context and details..."
                rows={4}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white resize-none"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Notes
              </label>
              <textarea
                value={formState.notes}
                onChange={handleInputChange('notes')}
                placeholder="Quick reminders or additional notes..."
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white resize-none"
              />
            </div>

            {/* Assignment Section */}
            {canAssign && (
              <div className="border-t border-gray-200 dark:border-gray-700 pt-6">
                <UserAssignment
                  todo={
                    {
                      ...formState,
                      assigned_user_id: assignment.assigned_user_id,
                      visibility: assignment.visibility || 'private',
                    } as any
                  }
                  assignableUsers={assignableUsers}
                  onAssign={handleAssignmentChange}
                  isLoading={loadingUsers || submitting}
                />
              </div>
            )}

            {/* Footer */}
            <div className="flex items-center justify-end gap-3 pt-4 border-t border-gray-200 dark:border-gray-700">
              <Button type="button" variant="ghost" onClick={handleClose} disabled={submitting}>
                Cancel
              </Button>
              <Button
                type="submit"
                loading={submitting}
                leftIcon={isEditing ? <Save className="h-4 w-4" /> : <Plus className="h-4 w-4" />}
              >
                {isEditing ? 'Save Changes' : 'Create Task'}
              </Button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
