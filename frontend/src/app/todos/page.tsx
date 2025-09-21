'use client';

import { useEffect, useMemo, useState, useCallback, useRef } from 'react';
import {
  CheckCircle2,
  ClipboardList,
  Clock,
  ListCheck,
  Plus,
  RotateCcw,
  Trash2,
  AlertCircle,
  CalendarDays,
  StickyNote,
  Sparkles,
  CalendarCheck,
  Sun,
  Search,
} from 'lucide-react';

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

type ViewFilter = 'all' | 'active' | 'completed' | 'expired';

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
  const isCompleted = todo.status === 'completed';

  const statusAccentClass = showExpired
    ? 'bg-red-500/20 text-red-600 dark:bg-red-500/25 dark:text-red-200'
    : isCompleted
    ? 'bg-emerald-500/20 text-emerald-600 dark:bg-emerald-500/25 dark:text-emerald-200'
    : 'bg-blue-500/20 text-blue-600 dark:bg-blue-500/25 dark:text-blue-200';

  const gradientClass = showExpired
    ? 'from-red-500/20'
    : isCompleted
    ? 'from-emerald-500/20'
    : 'from-blue-500/20';

  return (
    <div className="relative overflow-hidden rounded-2xl border border-gray-200/80 bg-white/80 shadow-sm transition-all hover:-translate-y-0.5 hover:shadow-lg dark:border-gray-700/70 dark:bg-gray-900/75">
      <div className={`pointer-events-none absolute inset-0 bg-gradient-to-r ${gradientClass} via-transparent to-transparent`} />
      <div className="relative flex flex-col gap-4 p-5 sm:flex-row sm:items-start sm:justify-between">
        <div className="flex-1 space-y-3">
          <div className="flex flex-wrap items-start gap-3">
            <div className={`flex h-11 w-11 items-center justify-center rounded-xl ${statusAccentClass}`}>
              {isCompleted ? (
                <CheckCircle2 className="h-5 w-5" />
              ) : showExpired ? (
                <AlertCircle className="h-5 w-5" />
              ) : (
                <ClipboardList className="h-5 w-5" />
              )}
            </div>
            <div className="min-w-0 flex-1 space-y-2">
              <div className="flex flex-wrap items-center gap-2">
                <h3 className="text-lg font-semibold leading-tight" style={{ color: 'var(--text-primary)' }}>
                  {todo.title}
                </h3>
                <Badge variant={statusVariants[todo.status]} size="sm">
                  {statusLabels[todo.status]}
                </Badge>
                {showExpired && (
                  <Badge variant="error" size="sm" className="flex items-center gap-1">
                    <AlertCircle className="h-3 w-3" /> Overdue
                  </Badge>
                )}
              </div>
              {todo.description && (
                <p className="text-sm leading-relaxed" style={{ color: 'var(--text-secondary)' }}>
                  {todo.description}
                </p>
              )}
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-4 text-sm" style={{ color: 'var(--text-secondary)' }}>
            <span className="flex items-center gap-1">
              <Clock className="h-4 w-4" />
              {formatDisplayDate(todo.due_date)}
            </span>
            {todo.priority && (
              <span className="flex items-center gap-1">
                <ListCheck className="h-4 w-4" />
                Priority: {todo.priority}
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
            <div className="flex items-start gap-2 text-sm leading-relaxed" style={{ color: 'var(--text-secondary)' }}>
              <StickyNote className="h-4 w-4 mt-0.5" />
              <span>{todo.notes}</span>
            </div>
          )}

          {isCompleted && todo.completed_at && (
            <p className="text-xs uppercase tracking-wide" style={{ color: 'var(--text-muted)' }}>
              Completed on {new Date(todo.completed_at).toLocaleString()}
            </p>
          )}
        </div>

        <div className="flex flex-wrap items-center justify-end gap-2">
          {showCompleteAction && (
            <Button
              size="sm"
              variant="primary"
              className="shadow-sm"
              loading={isProcessing}
              onClick={() => onComplete(todo)}
              leftIcon={<CheckCircle2 className="h-4 w-4" />}
            >
              Complete
            </Button>
          )}
          {showReopenAction && (
            <Button
              size="sm"
              variant="outline"
              className="border-gray-300 dark:border-gray-700"
              loading={isProcessing}
              onClick={() => onReopen(todo)}
              leftIcon={<RotateCcw className="h-4 w-4" />}
            >
              Reopen
            </Button>
          )}
          <Button
            size="sm"
            variant="ghost"
            className="text-gray-600 hover:bg-gray-100 hover:text-gray-900 dark:text-gray-300 dark:hover:bg-gray-800"
            onClick={() => onEdit(todo)}
            leftIcon={<ClipboardList className="h-4 w-4" />}
          >
            Edit
          </Button>
          <Button
            size="sm"
            variant="ghost"
            className="text-red-600 hover:bg-red-100 hover:text-red-700 dark:text-red-300 dark:hover:bg-red-900/30"
            loading={isProcessing}
            onClick={() => onDelete(todo)}
            leftIcon={<Trash2 className="h-4 w-4" />}
          >
            Delete
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
  const [viewFilter, setViewFilter] = useState<ViewFilter>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const formRef = useRef<HTMLDivElement>(null);

  const loadTodos = useCallback(async () => {
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
  }, [showToast]);

  useEffect(() => {
    void loadTodos();
  }, [loadTodos]);

  const stats = useMemo(() => {
    const pendingCount = todos.filter((todo) => !['completed', 'expired'].includes(todo.status)).length;
    const completedCount = todos.filter((todo) => todo.status === 'completed').length;
    const expiredCount = todos.filter((todo) => todo.status === 'expired' || todo.is_expired).length;
    return { pendingCount, completedCount, expiredCount, total: todos.length };
  }, [todos]);

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

  const dueTodayCount = useMemo(() => {
    const today = new Date();
    const todayString = today.toDateString();
    return activeTodos.filter((todo) => {
      if (!todo.due_date) return false;
      const due = new Date(todo.due_date);
      if (Number.isNaN(due.getTime())) return false;
      return due.toDateString() === todayString;
    }).length;
  }, [activeTodos]);

  const upcomingCount = useMemo(() => {
    const now = new Date();
    const inSevenDays = new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000);
    return activeTodos.filter((todo) => {
      if (!todo.due_date) return false;
      const due = new Date(todo.due_date);
      if (Number.isNaN(due.getTime())) return false;
      return due > now && due <= inSevenDays;
    }).length;
  }, [activeTodos]);

  const filteredTodos = useMemo(() => {
    const trimmed = searchQuery.trim().toLowerCase();
    let baseList: Todo[] = todos;
    if (viewFilter === 'active') {
      baseList = activeTodos;
    } else if (viewFilter === 'completed') {
      baseList = completedTodos;
    } else if (viewFilter === 'expired') {
      baseList = expiredTodos;
    }

    const getStatusWeight = (todo: Todo) => {
      if (todo.status === 'completed') return 2;
      if (todo.status === 'expired' || todo.is_expired) return 1;
      return 0;
    };

    let result = [...baseList];
    result.sort((a, b) => {
      const weightDiff = viewFilter === 'all' ? getStatusWeight(a) - getStatusWeight(b) : 0;
      if (weightDiff !== 0) return weightDiff;

      const dateA = a.due_date ? new Date(a.due_date).getTime() : Number.POSITIVE_INFINITY;
      const dateB = b.due_date ? new Date(b.due_date).getTime() : Number.POSITIVE_INFINITY;
      return dateA - dateB;
    });

    if (!trimmed) {
      return result;
    }

    return result.filter((todo) => {
      return (
        todo.title.toLowerCase().includes(trimmed) ||
        (todo.description?.toLowerCase().includes(trimmed) ?? false) ||
        (todo.notes?.toLowerCase().includes(trimmed) ?? false) ||
        (todo.priority?.toLowerCase().includes(trimmed) ?? false)
      );
    });
  }, [todos, activeTodos, completedTodos, expiredTodos, viewFilter, searchQuery]);

  const trimmedSearch = searchQuery.trim();
  const hasSearch = trimmedSearch.length > 0;

  const emptyStateCopy: Record<ViewFilter, { title: string; description: string }> = {
    all: {
      title: "You're all caught up",
      description: 'Create a task or adjust your filters to see more items.',
    },
    active: {
      title: 'Nothing active right now',
      description: 'Add a task or reopen an item when you are ready.',
    },
    completed: {
      title: 'No completed tasks yet',
      description: 'Mark tasks as done to celebrate them here.',
    },
    expired: {
      title: 'No overdue tasks',
      description: 'Stay ahead by keeping an eye on due dates.',
    },
  };

  const viewFilters: Array<{ label: string; value: ViewFilter }> = [
    { label: 'All', value: 'all' },
    { label: 'Active', value: 'active' },
    { label: 'Completed', value: 'completed' },
    { label: 'Expired', value: 'expired' },
  ];

  const renderEmptyIcon = () => {
    switch (viewFilter) {
      case 'active':
        return <ListCheck className="h-6 w-6" />;
      case 'completed':
        return <CheckCircle2 className="h-6 w-6" />;
      case 'expired':
        return <AlertCircle className="h-6 w-6" />;
      default:
        return <Sparkles className="h-6 w-6" />;
    }
  };

  const statHighlights = [
    {
      label: 'In progress',
      value: stats.pendingCount,
      icon: <ListCheck className="h-5 w-5" />,
      accentClass: 'bg-blue-500/20 text-blue-700 dark:bg-blue-500/25 dark:text-blue-200',
    },
    {
      label: 'Due today',
      value: dueTodayCount,
      icon: <Sun className="h-5 w-5" />,
      accentClass: 'bg-amber-500/20 text-amber-700 dark:bg-amber-500/25 dark:text-amber-200',
    },
    {
      label: 'Completed',
      value: stats.completedCount,
      icon: <CheckCircle2 className="h-5 w-5" />,
      accentClass: 'bg-emerald-500/20 text-emerald-700 dark:bg-emerald-500/25 dark:text-emerald-200',
    },
    {
      label: 'Overdue',
      value: stats.expiredCount,
      icon: <AlertCircle className="h-5 w-5" />,
      accentClass: 'bg-red-500/20 text-red-700 dark:bg-red-500/25 dark:text-red-200',
    },
  ];

  const heroMeta = `${upcomingCount} task${upcomingCount === 1 ? '' : 's'} due this week | ${stats.expiredCount} overdue`;

  const handleScrollToForm = () => {
    formRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };

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
      <div className="space-y-8 px-4 py-6 md:px-8 lg:px-12">
        <div className="relative overflow-hidden rounded-3xl border border-gray-200/80 bg-white/80 shadow-lg dark:border-gray-800/70 dark:bg-gray-900/70">
          <div className="absolute inset-0 bg-gradient-to-r from-blue-500/20 via-purple-500/20 to-transparent dark:from-blue-500/15 dark:via-purple-500/20" />
          <div className="relative z-10 flex flex-col gap-8 p-8 lg:flex-row lg:items-center lg:justify-between">
            <div className="max-w-2xl space-y-5">
              <span className="inline-flex items-center gap-2 rounded-full bg-white/70 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-blue-600 dark:bg-gray-900/70 dark:text-blue-300">
                <Sparkles className="h-4 w-4" /> Focus mode
              </span>
              <div className="space-y-3">
                <h1 className="text-4xl font-bold tracking-tight" style={{ color: 'var(--text-primary)' }}>
                  My Todos
                </h1>
                <p className="text-base leading-relaxed" style={{ color: 'var(--text-secondary)' }}>
                  A refreshed board to help you prioritize, keep momentum, and celebrate progress at a glance.
                </p>
              </div>
              <div className="flex flex-wrap items-center gap-3">
                <Button leftIcon={<Plus className="h-4 w-4" />} onClick={handleScrollToForm} className="shadow-md">
                  Add new task
                </Button>
                <div className="flex items-center gap-2 text-sm" style={{ color: 'var(--text-muted)' }}>
                  <CalendarCheck className="h-4 w-4" />
                  {heroMeta}
                </div>
              </div>
            </div>
            <div className="grid w-full max-w-xl grid-cols-2 gap-4 sm:grid-cols-2 md:grid-cols-4">
              {statHighlights.map((stat) => (
                <div
                  key={stat.label}
                  className="rounded-2xl border border-gray-200/70 bg-white/70 p-4 shadow-sm dark:border-gray-800/60 dark:bg-gray-900/60"
                >
                  <div className={`mb-3 inline-flex h-10 w-10 items-center justify-center rounded-xl ${stat.accentClass}`}>
                    {stat.icon}
                  </div>
                  <p className="text-xs font-medium uppercase tracking-wide" style={{ color: 'var(--text-muted)' }}>
                    {stat.label}
                  </p>
                  <p className="text-2xl font-semibold" style={{ color: 'var(--text-primary)' }}>
                    {stat.value}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {error && (
          <div className="flex items-start gap-3 rounded-2xl border border-red-500/20 bg-red-500/10 p-4 text-sm text-red-700 dark:border-red-500/30 dark:bg-red-500/15 dark:text-red-200">
            <AlertCircle className="mt-0.5 h-5 w-5" />
            <span>{error}</span>
          </div>
        )}

        <div className="grid grid-cols-1 gap-6 xl:grid-cols-[minmax(0,2fr)_minmax(0,1fr)]">
          <Card
            className="space-y-6 border border-gray-200/80 bg-white/80 backdrop-blur-sm dark:border-gray-800/70 dark:bg-gray-900/70"
            shadow="md"
          >
            <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
              <div className="space-y-1">
                <h2 className="text-xl font-semibold" style={{ color: 'var(--text-primary)' }}>
                  Task overview
                </h2>
                <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                  Use filters to focus, or search to jump straight to what you need.
                </p>
              </div>
              <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-end">
                <div className="flex flex-wrap items-center gap-2 rounded-full border border-gray-200/70 bg-white/70 p-1 dark:border-gray-800/60 dark:bg-gray-900/60">
                  {viewFilters.map((filter) => {
                    const isActive = viewFilter === filter.value;
                    const baseClasses =
                      'rounded-full px-4 py-2 text-sm font-medium transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500';
                    const activeClasses = 'bg-blue-600 text-white shadow-sm dark:bg-blue-500';
                    const inactiveClasses =
                      'text-gray-600 hover:bg-gray-100 hover:text-gray-900 dark:text-gray-300 dark:hover:bg-gray-800 dark:hover:text-white';
                    return (
                      <button
                        key={filter.value}
                        type="button"
                        onClick={() => setViewFilter(filter.value)}
                        className={`${baseClasses} ${isActive ? activeClasses : inactiveClasses}`}
                      >
                        {filter.label}
                      </button>
                    );
                  })}
                </div>
                <div className="w-full sm:w-64">
                  <Input
                    type="search"
                    placeholder="Search tasks..."
                    value={searchQuery}
                    onChange={(event) => setSearchQuery(event.target.value)}
                    leftIcon={<Search className="h-4 w-4" />}
                    className="rounded-full border-none bg-white/80 py-2 pl-11 pr-4 shadow-inner focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2 dark:bg-gray-900/60"
                    fullWidth={false}
                  />
                </div>
              </div>
            </div>

            <div className="space-y-4">
              {filteredTodos.length === 0 ? (
                <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed border-gray-300 bg-white/70 p-10 text-center dark:border-gray-700 dark:bg-gray-900/60">
                  <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-300">
                    {renderEmptyIcon()}
                  </div>
                  <h3 className="text-lg font-semibold" style={{ color: 'var(--text-primary)' }}>
                    {hasSearch ? 'No tasks match your search' : emptyStateCopy[viewFilter].title}
                  </h3>
                  <p className="mt-2 text-sm" style={{ color: 'var(--text-secondary)' }}>
                    {hasSearch ? 'Try a different keyword or clear the filters.' : emptyStateCopy[viewFilter].description}
                  </p>
                </div>
              ) : (
                filteredTodos.map((todo) => (
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

          <div className="space-y-6">
            <div ref={formRef}>
              <Card
                className="space-y-5 border border-gray-200/80 bg-white/80 backdrop-blur-sm dark:border-gray-800/70 dark:bg-gray-900/70"
                shadow="md"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <ClipboardList className="h-5 w-5" style={{ color: 'var(--brand-primary)' }} />
                      <h2 className="text-lg font-semibold" style={{ color: 'var(--text-primary)' }}>
                        {editingId ? 'Update task' : 'Create a task'}
                      </h2>
                    </div>
                    <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                      Capture the essentials—title, due date, and any quick notes for context.
                    </p>
                  </div>
                  {editingId && (
                    <Badge variant="secondary" size="sm">
                      Editing
                    </Badge>
                  )}
                </div>

                <form onSubmit={handleSubmit} className="space-y-4">
                  <Input
                    label="Title"
                    placeholder="What needs to get done?"
                    value={formState.title}
                    onChange={handleInputChange('title')}
                    required
                  />
                  <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
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
                  <div className="flex flex-wrap justify-end gap-2">
                    {editingId && (
                      <Button type="button" variant="ghost" onClick={resetForm}>
                        Cancel
                      </Button>
                    )}
                    <Button
                      type="submit"
                      loading={submitting}
                      leftIcon={<Plus className="h-4 w-4" />}
                    >
                      {editingId ? 'Save changes' : 'Save task'}
                    </Button>
                  </div>
                </form>
              </Card>
            </div>

            <Card
              className="space-y-4 border border-gray-200/80 bg-white/80 backdrop-blur-sm dark:border-gray-800/70 dark:bg-gray-900/70"
              shadow="md"
            >
              <div className="flex items-center gap-2">
                <Clock className="h-5 w-5" style={{ color: 'var(--brand-primary)' }} />
                <h2 className="text-lg font-semibold" style={{ color: 'var(--text-primary)' }}>
                  Recent activity
                </h2>
              </div>
              {recentTodos.length === 0 ? (
                <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
                  No recent todos yet. Create one to get started!
                </p>
              ) : (
                <div className="space-y-3">
                  {recentTodos.map((todo) => (
                    <div
                      key={todo.id}
                      className="rounded-2xl border border-gray-200/70 bg-white/70 p-4 dark:border-gray-700/60 dark:bg-gray-900/60"
                    >
                      <div className="flex items-start justify-between gap-3">
                        <div>
                          <p className="font-medium" style={{ color: 'var(--text-primary)' }}>
                            {todo.title}
                          </p>
                          <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
                            Updated {new Date(todo.updated_at).toLocaleString()}
                          </p>
                        </div>
                        <Badge variant={statusVariants[todo.status]} size="sm">
                          {statusLabels[todo.status]}
                        </Badge>
                      </div>
                      {todo.due_date && (
                        <p className="mt-2 text-xs" style={{ color: 'var(--text-secondary)' }}>
                          Due {formatDisplayDate(todo.due_date)}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </Card>
          </div>
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
