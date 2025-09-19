'use client';

import { useEffect, useMemo, useState } from 'react';
import { CheckCircle2, ClipboardList, Clock, ListCheck, Plus, RotateCcw, Trash2, AlertCircle, CalendarDays, StickyNote } from 'lucide-react';

import ProtectedRoute from '@/components/auth/ProtectedRoute';
import AppLayout from '@/components/layout/AppLayout';
import Card from '@/components/ui/Card';
import Badge from '@/components/ui/Badge';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import { useToast } from '@/contexts/ToastContext';
import { todosApi } from '@/api/todos';
import type { Todo, TodoStatus, TodoPayload } from '@/types/todo';

interface FormState {
  title: string;
  description: string;
  notes: string;
  dueDate: string;
  priority: string;
}

const initialFormState: FormState = {
  title: '',
  description: '',
  notes: '',
  dueDate: '',
  priority: '',
};

const statusVariants: Record<TodoStatus, 'primary' | 'secondary' | 'success' | 'warning' | 'error'> = {
  pending: 'warning',
  in_progress: 'primary',
  completed: 'success',
  expired: 'error',
};

const statusLabels: Record<TodoStatus, string> = {
  pending: 'Pending',
  in_progress: 'In progress',
  completed: 'Completed',
  expired: 'Expired',
};

function formatDateForInput(input?: string | null): string {
  if (!input) return '';
  const date = new Date(input);
  if (Number.isNaN(date.getTime())) return '';
  const off = date.getTimezoneOffset();
  const local = new Date(date.getTime() - off * 60_000);
  return local.toISOString().slice(0, 16);
}

function formatDisplayDate(input?: string | null): string {
  if (!input) return 'No due date';
  const date = new Date(input);
  if (Number.isNaN(date.getTime())) return 'No due date';
  return date.toLocaleString();
}

function formatRelativeTime(input?: string | null): string {
  if (!input) return '';
  const date = new Date(input);
  if (Number.isNaN(date.getTime())) return '';
  const diff = date.getTime() - Date.now();
  const days = Math.round(diff / (1000 * 60 * 60 * 24));
  if (days === 0) return 'Today';
  if (days > 0) return `${days} day${days === 1 ? '' : 's'} remaining`;
  const abs = Math.abs(days);
  return `${abs} day${abs === 1 ? '' : 's'} overdue`;
}

interface TodoItemProps {
  todo: Todo;
  onEdit: (todo: Todo) => void;
  onComplete: (todo: Todo) => Promise<void>;
  onReopen: (todo: Todo) => Promise<void>;
  onDelete: (todo: Todo) => Promise<void>;
  loadingId: number | null;
}

function TodoItem({ todo, onEdit, onComplete, onReopen, onDelete, loadingId }: TodoItemProps) {
  const isProcessing = loadingId === todo.id;
  const showExpired = todo.status === 'expired' || todo.is_expired;
  const showCompleteAction = todo.status !== 'completed';
  const showReopenAction = todo.status === 'completed' || showExpired;

  return (
    <div className={`border border-gray-200 dark:border-gray-700 rounded-xl p-4 space-y-3 transition-colors ${showExpired ? 'bg-red-50 dark:bg-red-900/10' : 'bg-white dark:bg-gray-900'}`}>
      <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-3">
        <div className="flex-1 space-y-2">
          <div className="flex items-center gap-2 flex-wrap">
            <h3 className="text-lg font-semibold" style={{ color: 'var(--text-primary)' }}>{todo.title}</h3>
            <Badge variant={statusVariants[todo.status]} size="sm">{statusLabels[todo.status]}</Badge>
            {showExpired && (
              <Badge variant="error" size="sm" className="flex items-center gap-1">
                <AlertCircle className="h-3 w-3" /> Overdue
              </Badge>
            )}
          </div>

          {todo.description && (
            <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>{todo.description}</p>
          )}

          <div className="flex flex-wrap items-center gap-3 text-sm" style={{ color: 'var(--text-secondary)' }}>
            <span className="flex items-center gap-1">
              <Clock className="h-4 w-4" />
              {formatDisplayDate(todo.due_date)}
            </span>
            {todo.priority && (
              <span className="flex items-center gap-1">
                <ListCheck className="h-4 w-4" /> Priority: {todo.priority}
              </span>
            )}
            {todo.due_date && (
              <span className="flex items-center gap-1">
                <CalendarDays className="h-4 w-4" />
                {formatRelativeTime(todo.due_date)}
              </span>
            )}
          </div>

          {todo.notes && (
            <div className="flex items-start gap-2 text-sm" style={{ color: 'var(--text-secondary)' }}>
              <StickyNote className="h-4 w-4 mt-0.5" />
              <span>{todo.notes}</span>
            </div>
          )}

          {todo.status === 'completed' && todo.completed_at && (
            <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
              Completed on {new Date(todo.completed_at).toLocaleString()}
            </p>
          )}
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {showCompleteAction && (
            <Button
              size="sm"
              variant="primary"
              loading={isProcessing}
              onClick={() => onComplete(todo)}
            >
              <CheckCircle2 className="h-4 w-4 mr-2" /> Complete
            </Button>
          )}
          {showReopenAction && (
            <Button
              size="sm"
              variant="outline"
              loading={isProcessing}
              onClick={() => onReopen(todo)}
            >
              <RotateCcw className="h-4 w-4 mr-2" /> Reopen
            </Button>
          )}
          <Button size="sm" variant="ghost" onClick={() => onEdit(todo)}>
            <ClipboardList className="h-4 w-4 mr-2" /> Edit
          </Button>
          <Button
            size="sm"
            variant="ghost"
            className="text-red-600 hover:text-red-700"
            loading={isProcessing}
            onClick={() => onDelete(todo)}
          >
            <Trash2 className="h-4 w-4 mr-2" /> Delete
          </Button>
        </div>
      </div>
    </div>
  );
}

function TodosPageContent() {
  const { showToast } = useToast();
  const [todos, setTodos] = useState<Todo[]>([]);
  const [recentTodos, setRecentTodos] = useState<Todo[]>([]);
  const [formState, setFormState] = useState<FormState>(initialFormState);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [actionLoadingId, setActionLoadingId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  const loadTodos = async () => {
    setLoading(true);
    try {
      const [listResponse, recent] = await Promise.all([
        todosApi.list({ includeCompleted: true, limit: 200 }),
        todosApi.listRecent(5),
      ]);
      setTodos(listResponse.items);
      setRecentTodos(recent);
      setError(null);
    } catch (err) {
      console.error(err);
      setError(err instanceof Error ? err.message : 'Failed to load todos');
      showToast({ type: 'error', title: 'Failed to load todos' });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadTodos();
  }, []);

  const stats = useMemo(() => {
    const pendingCount = todos.filter((todo) => !['completed', 'expired'].includes(todo.status)).length;
    const completedCount = todos.filter((todo) => todo.status === 'completed').length;
    const expiredCount = todos.filter((todo) => todo.status === 'expired' || todo.is_expired).length;
    return { pendingCount, completedCount, expiredCount, total: todos.length };
  }, [todos]);

  const handleInputChange = (field: keyof FormState) => (
    event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    setFormState((prev) => ({ ...prev, [field]: event.target.value }));
  };

  const resetForm = () => {
    setFormState(initialFormState);
    setEditingId(null);
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
    };

    setSubmitting(true);
    try {
      if (editingId) {
        await todosApi.update(editingId, payload);
        showToast({ type: 'success', title: 'Todo updated' });
      } else {
        await todosApi.create(payload);
        showToast({ type: 'success', title: 'Todo created' });
      }
      resetForm();
      await loadTodos();
    } catch (err) {
      console.error(err);
      showToast({ type: 'error', title: err instanceof Error ? err.message : 'Failed to save todo' });
    } finally {
      setSubmitting(false);
    }
  };

  const handleEdit = (todo: Todo) => {
    setEditingId(todo.id);
    setFormState({
      title: todo.title,
      description: todo.description ?? '',
      notes: todo.notes ?? '',
      dueDate: formatDateForInput(todo.due_date),
      priority: todo.priority ?? '',
    });
  };

  const handleComplete = async (todo: Todo) => {
    setActionLoadingId(todo.id);
    try {
      await todosApi.complete(todo.id);
      showToast({ type: 'success', title: 'Todo completed' });
      await loadTodos();
    } catch (err) {
      console.error(err);
      showToast({ type: 'error', title: err instanceof Error ? err.message : 'Failed to complete todo' });
    } finally {
      setActionLoadingId(null);
    }
  };

  const handleReopen = async (todo: Todo) => {
    setActionLoadingId(todo.id);
    try {
      await todosApi.reopen(todo.id);
      showToast({ type: 'success', title: 'Todo reopened' });
      await loadTodos();
    } catch (err) {
      console.error(err);
      showToast({ type: 'error', title: err instanceof Error ? err.message : 'Failed to reopen todo' });
    } finally {
      setActionLoadingId(null);
    }
  };

  const handleDelete = async (todo: Todo) => {
    setActionLoadingId(todo.id);
    try {
      await todosApi.remove(todo.id);
      showToast({ type: 'success', title: 'Todo deleted' });
      await loadTodos();
    } catch (err) {
      console.error(err);
      showToast({ type: 'error', title: err instanceof Error ? err.message : 'Failed to delete todo' });
    } finally {
      setActionLoadingId(null);
    }
  };

  const activeTodos = useMemo(
    () => todos.filter((todo) => !['completed', 'expired'].includes(todo.status)),
    [todos],
  );

  const expiredTodos = useMemo(
    () => todos.filter((todo) => todo.status === 'expired' || todo.is_expired),
    [todos],
  );

  const completedTodos = useMemo(
    () => todos.filter((todo) => todo.status === 'completed'),
    [todos],
  );

  if (loading) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center h-96">
          <LoadingSpinner className="w-10 h-10" />
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout>
      <div className="p-6 space-y-6">
        <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <div>
            <h1 className="text-3xl font-bold" style={{ color: 'var(--text-primary)' }}>My Todos</h1>
            <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
              Track tasks, jot quick memos, and stay on top of due dates.
            </p>
          </div>
          <Badge variant="secondary" size="md" className="inline-flex items-center gap-2">
            <ListCheck className="h-4 w-4" /> {stats.total} total items
          </Badge>
        </div>

        {error && (
          <div className="border border-red-200 bg-red-50 dark:border-red-900/40 dark:bg-red-900/20 text-red-700 dark:text-red-200 rounded-xl p-4 flex items-center gap-2">
            <AlertCircle className="h-5 w-5" />
            <span>{error}</span>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card className="p-4 space-y-2">
            <div className="flex items-center gap-2">
              <ListCheck className="h-5 w-5 text-blue-500" />
              <span className="text-sm font-semibold" style={{ color: 'var(--text-secondary)' }}>Active</span>
            </div>
            <p className="text-3xl font-bold" style={{ color: 'var(--text-primary)' }}>{stats.pendingCount}</p>
          </Card>
          <Card className="p-4 space-y-2">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="h-5 w-5 text-emerald-500" />
              <span className="text-sm font-semibold" style={{ color: 'var(--text-secondary)' }}>Completed</span>
            </div>
            <p className="text-3xl font-bold" style={{ color: 'var(--text-primary)' }}>{stats.completedCount}</p>
          </Card>
          <Card className="p-4 space-y-2">
            <div className="flex items-center gap-2">
              <Clock className="h-5 w-5 text-red-500" />
              <span className="text-sm font-semibold" style={{ color: 'var(--text-secondary)' }}>Expired</span>
            </div>
            <p className="text-3xl font-bold" style={{ color: 'var(--text-primary)' }}>{stats.expiredCount}</p>
          </Card>
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-[2fr_1fr] gap-6">
          <Card className="p-6 space-y-4">
            <div className="flex items-center gap-2">
              <ClipboardList className="h-5 w-5" style={{ color: 'var(--brand-primary)' }} />
              <h2 className="text-xl font-semibold" style={{ color: 'var(--text-primary)' }}>
                {editingId ? 'Edit todo' : 'Create new todo'}
              </h2>
            </div>
            <form onSubmit={handleSubmit} className="space-y-4">
              <Input
                label="Title"
                placeholder="What needs to get done?"
                value={formState.title}
                onChange={handleInputChange('title')}
                required
              />
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>
                    Due date
                  </label>
                  <input
                    type="datetime-local"
                    value={formState.dueDate}
                    onChange={handleInputChange('dueDate')}
                    className="input mt-2"
                  />
                </div>
                <Input
                  label="Priority"
                  placeholder="Optional priority (e.g. High)"
                  value={formState.priority}
                  onChange={handleInputChange('priority')}
                />
              </div>
              <div>
                <label className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>
                  Details
                </label>
                <textarea
                  value={formState.description}
                  onChange={handleInputChange('description')}
                  placeholder="Add more context..."
                  className="input mt-2 min-h-[100px]"
                />
              </div>
              <div>
                <label className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>
                  Memo
                </label>
                <textarea
                  value={formState.notes}
                  onChange={handleInputChange('notes')}
                  placeholder="Quick reminder or notes"
                  className="input mt-2 min-h-[80px]"
                />
              </div>
              <div className="flex flex-wrap gap-2 justify-end">
                {editingId && (
                  <Button type="button" variant="ghost" onClick={resetForm}>
                    Cancel
                  </Button>
                )}
                <Button type="submit" loading={submitting} leftIcon={<Plus className="h-4 w-4" />}>
                  {editingId ? 'Update todo' : 'Add todo'}
                </Button>
              </div>
            </form>
          </Card>

          <Card className="p-6 space-y-4">
            <div className="flex items-center gap-2">
              <Clock className="h-5 w-5" style={{ color: 'var(--brand-primary)' }} />
              <h2 className="text-lg font-semibold" style={{ color: 'var(--text-primary)' }}>
                Recent activity
              </h2>
            </div>
            <div className="space-y-3">
              {recentTodos.length === 0 && (
                <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
                  No recent todos yet. Create one to get started!
                </p>
              )}
              {recentTodos.map((todo) => (
                <div key={todo.id} className="border border-gray-200 dark:border-gray-700 rounded-lg p-3">
                  <div className="flex items-center justify-between gap-2">
                    <div>
                      <p className="font-medium" style={{ color: 'var(--text-primary)' }}>{todo.title}</p>
                      <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
                        Updated {new Date(todo.updated_at).toLocaleString()}
                      </p>
                    </div>
                    <Badge variant={statusVariants[todo.status]} size="sm">
                      {statusLabels[todo.status]}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
          <Card className="p-6 space-y-4">
            <div className="flex items-center gap-2">
              <ListCheck className="h-5 w-5" style={{ color: 'var(--brand-primary)' }} />
              <h2 className="text-lg font-semibold" style={{ color: 'var(--text-primary)' }}>
                Active todos
              </h2>
            </div>
            <div className="space-y-3">
              {activeTodos.length === 0 ? (
                <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
                  No active todos. Enjoy the clear list!
                </p>
              ) : (
                activeTodos.map((todo) => (
                  <TodoItem
                    key={todo.id}
                    todo={todo}
                    onEdit={handleEdit}
                    onComplete={handleComplete}
                    onReopen={handleReopen}
                    onDelete={handleDelete}
                    loadingId={actionLoadingId}
                  />
                ))
              )}
            </div>
          </Card>

          <Card className="p-6 space-y-4">
            <div className="flex items-center gap-2">
              <AlertCircle className="h-5 w-5 text-red-500" />
              <h2 className="text-lg font-semibold" style={{ color: 'var(--text-primary)' }}>
                Expired
              </h2>
            </div>
            <div className="space-y-3">
              {expiredTodos.length === 0 ? (
                <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
                  No overdue items. Great job staying on track!
                </p>
              ) : (
                expiredTodos.map((todo) => (
                  <TodoItem
                    key={todo.id}
                    todo={todo}
                    onEdit={handleEdit}
                    onComplete={handleComplete}
                    onReopen={handleReopen}
                    onDelete={handleDelete}
                    loadingId={actionLoadingId}
                  />
                ))
              )}
            </div>
          </Card>

          <Card className="p-6 space-y-4">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="h-5 w-5 text-emerald-500" />
              <h2 className="text-lg font-semibold" style={{ color: 'var(--text-primary)' }}>
                Completed
              </h2>
            </div>
            <div className="space-y-3">
              {completedTodos.length === 0 ? (
                <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
                  No completed todos yet. Mark tasks as done to see them here.
                </p>
              ) : (
                completedTodos.map((todo) => (
                  <TodoItem
                    key={todo.id}
                    todo={todo}
                    onEdit={handleEdit}
                    onComplete={handleComplete}
                    onReopen={handleReopen}
                    onDelete={handleDelete}
                    loadingId={actionLoadingId}
                  />
                ))
              )}
            </div>
          </Card>
        </div>
      </div>
    </AppLayout>
  );
}

export default function TodosPage() {
  return (
    <ProtectedRoute>
      <TodosPageContent />
    </ProtectedRoute>
  );
}
