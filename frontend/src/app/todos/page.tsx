'use client';

import { useEffect, useMemo, useState, useCallback } from 'react';
import {
  CheckCircle2,
  ClipboardList,
  Clock,
  ListCheck,
  Plus,
  RotateCcw,
  Trash2,
  AlertCircle,
  StickyNote,
  Sparkles,
  CalendarCheck,
  Sun,
  Search,
} from 'lucide-react';

import ProtectedRoute from '@/components/auth/ProtectedRoute';
import AppLayout from '@/components/layout/AppLayout';
import Card from '@/components/ui/card';
import Badge from '@/components/ui/badge';
import Button from '@/components/ui/button';
import Input from '@/components/ui/input';
import LoadingSpinner from '@/components/ui/loading-spinner';
import ConfirmationModal from '@/components/ui/confirmation-modal';
import TaskModal from '@/components/todos/TaskModal';
import { useToast } from '@/contexts/ToastContext';
import { todosApi } from '@/api/todos';
import type { Todo, ViewFilter, TodoItemProps } from '@/types/todo';

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

function TodoItem({ todo, onEdit, onComplete, onReopen, onDelete, onRestore, loadingId }: TodoItemProps) {
  const isProcessing = loadingId === todo.id;
  const showExpired = todo.status === 'expired' || todo.is_expired;
  const showCompleteAction = !todo.is_deleted && todo.status !== 'completed';
  const showReopenAction = !todo.is_deleted && (todo.status === 'completed' || showExpired);
  const isCompleted = todo.status === 'completed';
  const isDeleted = todo.is_deleted;

  const statusAccentClass = isDeleted
    ? 'bg-red-500/20 text-red-700 dark:bg-red-500/25 dark:text-red-300'
    : showExpired
    ? 'bg-red-500/20 text-red-600 dark:bg-red-500/25 dark:text-red-200'
    : isCompleted
    ? 'bg-emerald-500/20 text-emerald-600 dark:bg-emerald-500/25 dark:text-emerald-200'
    : 'bg-blue-500/20 text-blue-600 dark:bg-blue-500/25 dark:text-blue-200';

  const gradientClass = isDeleted
    ? 'from-red-500/20'
    : showExpired
    ? 'from-red-500/20'
    : isCompleted
    ? 'from-emerald-500/20'
    : 'from-blue-500/20';

  return (
    <div className={`group relative overflow-hidden rounded-xl shadow-sm transition-all duration-200 ${
      isDeleted
        ? 'border border-red-200/80 bg-red-50/50 hover:shadow-xl hover:border-red-300/80 dark:border-red-700/50 dark:bg-red-900/10 dark:hover:border-red-600/70'
        : 'border border-gray-200/60 bg-white hover:shadow-xl hover:border-gray-300/80 dark:border-gray-700/50 dark:bg-gray-800 dark:hover:border-gray-600/70'
    }`}>
      <div className={`pointer-events-none absolute inset-0 bg-gradient-to-br ${gradientClass} via-transparent to-transparent opacity-50`} />
      <div className="relative flex flex-col gap-4 p-6">
        <div className="space-y-4">
          <div className="flex items-start gap-4">
            <div className={`flex h-12 w-12 items-center justify-center rounded-full ${statusAccentClass} ring-2 ring-white/50 dark:ring-gray-800/50`}>
              {isDeleted ? (
                <Trash2 className="h-6 w-6" />
              ) : isCompleted ? (
                <CheckCircle2 className="h-6 w-6" />
              ) : showExpired ? (
                <AlertCircle className="h-6 w-6" />
              ) : (
                <ClipboardList className="h-6 w-6" />
              )}
            </div>
            <div className="min-w-0 flex-1 space-y-3">
              <div>
                <h3 className={`text-lg font-semibold leading-tight group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors line-clamp-2 ${
                  isDeleted ? 'line-through opacity-70' : ''
                }`} style={{ color: 'var(--text-primary)' }}>
                  {todo.title}
                </h3>
                <div className="mt-2 flex flex-wrap items-center gap-2">
                  {isDeleted && (
                    <Badge variant="error" size="sm" className="flex items-center gap-1">
                      <Trash2 className="h-3 w-3" /> Deleted
                    </Badge>
                  )}
                  {showExpired && !isDeleted && (
                    <Badge variant="error" size="sm" className="flex items-center gap-1">
                      <AlertCircle className="h-3 w-3" /> Overdue
                    </Badge>
                  )}
                </div>
              </div>
              {todo.description && (
                <p className={`text-sm leading-relaxed line-clamp-2 ${
                  isDeleted ? 'opacity-60' : ''
                }`} style={{ color: 'var(--text-secondary)' }}>
                  {todo.description}
                </p>
              )}
            </div>
          </div>

          <div className="space-y-3">
            <div className="grid grid-cols-1 gap-2 text-sm" style={{ color: 'var(--text-secondary)' }}>
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <Clock className="h-4 w-4 text-blue-500" />
                  <span className="font-medium">Due:</span>
                </div>
                <div className="pl-6 space-y-1">
                  <div>{formatDisplayDate(todo.due_date)}</div>
                  {todo.due_date && (
                    <div>
                      <span className="text-xs px-2 py-1 rounded-full bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300">
                        {formatRelativeTime(todo.due_date)}
                      </span>
                    </div>
                  )}
                </div>
              </div>
              {todo.priority && (
                <div className="flex items-center gap-3">
                  <div className="flex items-center gap-2">
                    <ListCheck className="h-4 w-4 text-purple-500" />
                    <span className="font-medium">Priority:</span>
                  </div>
                  <span className="px-2 py-1 rounded-full bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-300 text-xs font-medium">
                    {todo.priority}
                  </span>
                </div>
              )}
            </div>
          </div>

          {todo.notes && (
            <div className="p-3 rounded-lg bg-amber-50/80 border border-amber-200/50 dark:bg-amber-900/20 dark:border-amber-700/30">
              <div className="flex items-start gap-3">
                <div className="flex items-center gap-2 text-sm font-medium text-amber-700 dark:text-amber-300">
                  <StickyNote className="h-4 w-4" />
                  <span>Notes:</span>
                </div>
              </div>
              <p className="mt-2 text-sm leading-relaxed text-amber-800 dark:text-amber-200 line-clamp-3">
                {todo.notes}
              </p>
            </div>
          )}

          {isCompleted && todo.completed_at && (
            <div className="p-3 rounded-lg bg-emerald-50/80 border border-emerald-200/50 dark:bg-emerald-900/20 dark:border-emerald-700/30">
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-2 text-sm font-medium text-emerald-700 dark:text-emerald-300">
                  <CheckCircle2 className="h-4 w-4" />
                  <span>Completed:</span>
                </div>
                <span className="text-sm text-emerald-800 dark:text-emerald-200">
                  {new Date(todo.completed_at).toLocaleString()}
                </span>
              </div>
            </div>
          )}
        </div>

        <div className="pt-4 border-t border-gray-100 dark:border-gray-700">
          {isDeleted ? (
            <div className="grid grid-cols-2 gap-2">
              {/* Restore Action */}
              <Button
                size="sm"
                variant="primary"
                className="w-full shadow-sm"
                loading={isProcessing}
                onClick={() => onRestore?.(todo)}
                leftIcon={<RotateCcw className="h-4 w-4" />}
              >
                Restore
              </Button>

              {/* View/Edit Action */}
              <Button
                size="sm"
                variant="ghost"
                className="w-full text-gray-600 hover:bg-gray-100 hover:text-gray-900 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-white"
                onClick={() => onEdit(todo)}
                leftIcon={<ClipboardList className="h-4 w-4" />}
              >
                View
              </Button>
            </div>
          ) : (
            <div className="grid grid-cols-3 gap-2">
              {/* Primary Action (Complete/Reopen) */}
              {showCompleteAction && (
                <Button
                  size="sm"
                  variant="primary"
                  className="w-full shadow-sm"
                  loading={isProcessing}
                  onClick={() => onComplete?.(todo)}
                  leftIcon={<CheckCircle2 className="h-4 w-4" />}
                >
                  Finish
                </Button>
              )}
              {showReopenAction && (
                <Button
                  size="sm"
                  variant="outline"
                  className="w-full border-gray-300 dark:border-gray-600"
                  loading={isProcessing}
                  onClick={() => onReopen?.(todo)}
                  leftIcon={<RotateCcw className="h-4 w-4" />}
                >
                  Reopen
                </Button>
              )}

              {/* Edit Action */}
              <Button
                size="sm"
                variant="ghost"
                className="w-full text-gray-600 hover:bg-gray-100 hover:text-gray-900 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-white"
                onClick={() => onEdit(todo)}
                leftIcon={<ClipboardList className="h-4 w-4" />}
              >
                Edit
              </Button>

              {/* Delete Action */}
              <Button
                size="sm"
                variant="ghost"
                className="w-full text-red-600 hover:bg-red-100 hover:text-red-700 dark:text-red-400 dark:hover:bg-red-900/30 dark:hover:text-red-300"
                loading={isProcessing}
                onClick={() => onDelete(todo)}
                leftIcon={<Trash2 className="h-4 w-4" />}
              >
                Delete
              </Button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function TodosPageContent() {
  const { showToast } = useToast();
  const [todos, setTodos] = useState<Todo[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionLoadingId, setActionLoadingId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [viewFilter, setViewFilter] = useState<ViewFilter>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingTodo, setEditingTodo] = useState<Todo | null>(null);

  // Confirmation modal state
  const [confirmationModal, setConfirmationModal] = useState<{
    isOpen: boolean;
    todo: Todo | null;
    action: 'delete' | 'restore' | 'complete' | 'reopen' | null;
  }>({
    isOpen: false,
    todo: null,
    action: null,
  });

  const loadTodos = useCallback(async () => {
    setLoading(true);
    try {
      const listResponse = await todosApi.list({
        includeCompleted: true,
        includeDeleted: viewFilter === 'deleted',
        limit: 200
      });
      setTodos(listResponse.items);
      setError(null);
    } catch (err) {
      console.error(err);
      setError(err instanceof Error ? err.message : 'Failed to load todos');
      showToast({ type: 'error', title: 'Failed to load todos' });
    } finally {
      setLoading(false);
    }
  }, [showToast, viewFilter]);

  useEffect(() => {
    void loadTodos();
  }, [loadTodos]);

  const stats = useMemo(() => {
    const nonDeletedTodos = todos.filter((todo) => !todo.is_deleted);
    const pendingCount = nonDeletedTodos.filter((todo) => !['completed', 'expired'].includes(todo.status)).length;
    const completedCount = nonDeletedTodos.filter((todo) => todo.status === 'completed').length;
    const expiredCount = nonDeletedTodos.filter((todo) => todo.status === 'expired' || todo.is_expired).length;
    const deletedCount = todos.filter((todo) => todo.is_deleted).length;
    return { pendingCount, completedCount, expiredCount, deletedCount, total: nonDeletedTodos.length };
  }, [todos]);

  const activeTodos = useMemo(
    () => todos.filter((todo) => !todo.is_deleted && !['completed', 'expired'].includes(todo.status)),
    [todos],
  );

  const expiredTodos = useMemo(
    () => todos.filter((todo) => !todo.is_deleted && (todo.status === 'expired' || todo.is_expired)),
    [todos],
  );

  const completedTodos = useMemo(
    () => todos.filter((todo) => !todo.is_deleted && todo.status === 'completed'),
    [todos],
  );

  const deletedTodos = useMemo(
    () => todos.filter((todo) => todo.is_deleted),
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
    } else if (viewFilter === 'deleted') {
      baseList = deletedTodos;
    }

    const getStatusWeight = (todo: Todo) => {
      if (todo.status === 'completed') return 2;
      if (todo.status === 'expired' || todo.is_expired) return 1;
      return 0;
    };

    const result = [...baseList];
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
  }, [todos, activeTodos, completedTodos, expiredTodos, deletedTodos, viewFilter, searchQuery]);

  // Confirmation modal helpers
  const openConfirmationModal = (todo: Todo, action: 'delete' | 'restore' | 'complete' | 'reopen') => {
    setConfirmationModal({ isOpen: true, todo, action });
  };

  const closeConfirmationModal = () => {
    setConfirmationModal({ isOpen: false, todo: null, action: null });
  };

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
    deleted: {
      title: 'No deleted tasks',
      description: 'Deleted tasks will appear here and can be restored.',
    },
  };

  const viewFilters: Array<{ label: string; value: ViewFilter }> = [
    { label: 'All', value: 'all' },
    { label: 'Active', value: 'active' },
    { label: 'Completed', value: 'completed' },
    { label: 'Expired', value: 'expired' },
    { label: 'Deleted', value: 'deleted' },
  ];

  const renderEmptyIcon = () => {
    switch (viewFilter) {
      case 'active':
        return <ListCheck className="h-6 w-6" />;
      case 'completed':
        return <CheckCircle2 className="h-6 w-6" />;
      case 'expired':
        return <AlertCircle className="h-6 w-6" />;
      case 'deleted':
        return <Trash2 className="h-6 w-6" />;
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

  const handleOpenModal = () => {
    setEditingTodo(null);
    setIsModalOpen(true);
  };

  const handleModalSuccess = async () => {
    await loadTodos();
  };

  const handleEdit = (todo: Todo) => {
    setEditingTodo(todo);
    setIsModalOpen(true);
  };

  const handleComplete = (todo: Todo) => {
    openConfirmationModal(todo, 'complete');
  };

  const executeComplete = async (todo: Todo) => {
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

  const handleReopen = (todo: Todo) => {
    openConfirmationModal(todo, 'reopen');
  };

  const executeReopen = async (todo: Todo) => {
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

  const handleDelete = (todo: Todo) => {
    openConfirmationModal(todo, 'delete');
  };

  const executeDelete = async (todo: Todo) => {
    setActionLoadingId(todo.id);
    try {
      await todosApi.remove(todo.id);
      showToast({ type: 'success', title: 'Todo moved to trash' });
      await loadTodos();
    } catch (err) {
      console.error(err);
      showToast({ type: 'error', title: err instanceof Error ? err.message : 'Failed to delete todo' });
    } finally {
      setActionLoadingId(null);
    }
  };

  const handleRestore = (todo: Todo) => {
    openConfirmationModal(todo, 'restore');
  };

  const executeRestore = async (todo: Todo) => {
    setActionLoadingId(todo.id);
    try {
      await todosApi.restore(todo.id);
      showToast({ type: 'success', title: 'Todo restored' });
      await loadTodos();
    } catch (err) {
      console.error(err);
      showToast({ type: 'error', title: err instanceof Error ? err.message : 'Failed to restore todo' });
    } finally {
      setActionLoadingId(null);
    }
  };

  const handleConfirmAction = async () => {
    if (!confirmationModal.todo || !confirmationModal.action) return;

    const { todo, action } = confirmationModal;
    closeConfirmationModal();

    switch (action) {
      case 'delete':
        await executeDelete(todo);
        break;
      case 'restore':
        await executeRestore(todo);
        break;
      case 'complete':
        await executeComplete(todo);
        break;
      case 'reopen':
        await executeReopen(todo);
        break;
    }
  };

  const getConfirmationTitle = () => {
    if (!confirmationModal.action) return '';
    switch (confirmationModal.action) {
      case 'delete':
        return 'Delete Todo';
      case 'restore':
        return 'Restore Todo';
      case 'complete':
        return 'Complete Todo';
      case 'reopen':
        return 'Reopen Todo';
      default:
        return '';
    }
  };

  const getConfirmationMessage = () => {
    if (!confirmationModal.todo || !confirmationModal.action) return '';
    const todoTitle = confirmationModal.todo.title;
    switch (confirmationModal.action) {
      case 'delete':
        return `Are you sure you want to move "${todoTitle}" to trash? You can restore it later if needed.`;
      case 'restore':
        return `Are you sure you want to restore "${todoTitle}" from trash?`;
      case 'complete':
        return `Are you sure you want to mark "${todoTitle}" as completed?`;
      case 'reopen':
        return `Are you sure you want to reopen "${todoTitle}"?`;
      default:
        return '';
    }
  };

  const getConfirmationButtonText = () => {
    if (!confirmationModal.action) return '';
    switch (confirmationModal.action) {
      case 'delete':
        return 'Move to Trash';
      case 'restore':
        return 'Restore';
      case 'complete':
        return 'Complete';
      case 'reopen':
        return 'Reopen';
      default:
        return '';
    }
  };

  const getConfirmationButtonClass = () => {
    if (!confirmationModal.action) return '';
    switch (confirmationModal.action) {
      case 'delete':
        return 'bg-red-600 hover:bg-red-700';
      case 'restore':
        return 'bg-blue-600 hover:bg-blue-700';
      case 'complete':
        return 'bg-green-600 hover:bg-green-700';
      case 'reopen':
        return 'bg-orange-600 hover:bg-orange-700';
      default:
        return 'bg-gray-600 hover:bg-gray-700';
    }
  };

  const getConfirmationIcon = () => {
    if (!confirmationModal.action) return null;
    switch (confirmationModal.action) {
      case 'delete':
        return <Trash2 className="h-6 w-6 text-red-500" />;
      case 'restore':
        return <RotateCcw className="h-6 w-6 text-blue-500" />;
      case 'complete':
        return <CheckCircle2 className="h-6 w-6 text-green-500" />;
      case 'reopen':
        return <RotateCcw className="h-6 w-6 text-orange-500" />;
      default:
        return null;
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
      <TaskModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSuccess={handleModalSuccess}
        editingTodo={editingTodo}
      />

      <ConfirmationModal
        isOpen={confirmationModal.isOpen}
        onClose={closeConfirmationModal}
        onConfirm={handleConfirmAction}
        title={getConfirmationTitle()}
        message={getConfirmationMessage()}
        confirmText={getConfirmationButtonText()}
        confirmButtonClass={getConfirmationButtonClass()}
        icon={getConfirmationIcon()}
      />

      <div className="space-y-6 px-4 py-4 md:px-8 lg:px-12">
        <div className="relative overflow-hidden rounded-2xl border border-gray-200/80 bg-white/80 shadow-md dark:border-gray-800/70 dark:bg-gray-900/70">
          <div className="absolute inset-0 bg-gradient-to-r from-blue-500/20 via-purple-500/20 to-transparent dark:from-blue-500/15 dark:via-purple-500/20" />
          <div className="relative z-10 flex flex-col gap-6 p-6 lg:flex-row lg:items-center lg:justify-between">
            <div className="max-w-2xl space-y-3">
              <span className="inline-flex items-center gap-2 rounded-full bg-white/70 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-blue-600 dark:bg-gray-900/70 dark:text-blue-300">
                <Sparkles className="h-4 w-4" /> Focus mode
              </span>
              <div>
                <h1 className="text-3xl font-bold tracking-tight" style={{ color: 'var(--text-primary)' }}>
                  My Todos
                </h1>
              </div>
              <div className="flex flex-wrap items-center gap-3">
                <Button leftIcon={<Plus className="h-4 w-4" />} onClick={handleOpenModal} className="shadow-md">
                  Add new task
                </Button>
                <div className="flex items-center gap-2 text-sm" style={{ color: 'var(--text-muted)' }}>
                  <CalendarCheck className="h-4 w-4" />
                  {heroMeta}
                </div>
              </div>
            </div>
            <div className="grid w-full max-w-xl grid-cols-2 gap-3 sm:grid-cols-2 md:grid-cols-4">
              {statHighlights.map((stat) => (
                <div
                  key={stat.label}
                  className="rounded-xl border border-gray-200/70 bg-white/70 p-3 shadow-sm dark:border-gray-800/60 dark:bg-gray-900/60"
                >
                  <div className={`mb-2 inline-flex h-8 w-8 items-center justify-center rounded-lg ${stat.accentClass}`}>
                    {stat.icon}
                  </div>
                  <p className="text-xs font-medium uppercase tracking-wide" style={{ color: 'var(--text-muted)' }}>
                    {stat.label}
                  </p>
                  <p className="text-xl font-semibold" style={{ color: 'var(--text-primary)' }}>
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

        <div className="max-w-5xl mx-auto">
          <Card
            className="space-y-6 border border-gray-200/80 bg-white/80 backdrop-blur-sm dark:border-gray-800/70 dark:bg-gray-900/70"
            shadow="md"
          >
            <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
              <div>
                <h2 className="text-xl font-semibold" style={{ color: 'var(--text-primary)' }}>
                  Task overview
                </h2>
              </div>
              <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-end">
                <div className="flex flex-wrap items-center gap-1 rounded-full border border-gray-200/70 bg-gradient-to-r from-white/80 to-gray-50/80 p-1.5 shadow-inner backdrop-blur-sm dark:border-gray-700/60 dark:from-gray-800/80 dark:to-gray-900/80">
                  {viewFilters.map((filter) => {
                    const isActive = viewFilter === filter.value;
                    const baseClasses =
                      'relative rounded-full px-4 py-2 text-sm font-medium transition-all duration-200 ease-in-out focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 transform hover:scale-105';
                    const activeClasses = 'bg-gradient-to-r from-blue-600 to-blue-700 text-white shadow-lg shadow-blue-500/25 ring-2 ring-blue-200/50 dark:from-blue-500 dark:to-blue-600 dark:ring-blue-400/30';
                    const inactiveClasses =
                      'text-gray-600 hover:bg-gradient-to-r hover:from-gray-100 hover:to-gray-50 hover:text-gray-900 hover:shadow-md dark:text-gray-300 dark:hover:from-gray-700 dark:hover:to-gray-800 dark:hover:text-white';
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
                <div className="w-full sm:w-80">
                  <Input
                    type="search"
                    placeholder="Search by keyword..."
                    value={searchQuery}
                    onChange={(event) => setSearchQuery(event.target.value)}
                    leftIcon={<Search className="h-4 w-4" style={{ marginLeft: '4px' }} />}
                    className="rounded-full border-none bg-white/80 py-2 pl-11 pr-4 shadow-inner focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2 dark:bg-gray-900/60 !pl-11"
                    fullWidth={false}
                  />
                </div>
              </div>
            </div>

            <div>
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
                <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4">
                  {filteredTodos.map((todo) => (
                    <TodoItem
                      key={todo.id}
                      todo={todo}
                      onEdit={handleEdit}
                      onComplete={handleComplete}
                      onReopen={handleReopen}
                      onDelete={handleDelete}
                      onRestore={handleRestore}
                      loadingId={actionLoadingId}
                    />
                  ))}
                </div>
              )}
            </div>
          </Card>

          <Card
            className="mt-6 border border-gray-200/80 bg-white/80 backdrop-blur-sm dark:border-gray-800/70 dark:bg-gray-900/70"
            shadow="md"
          >
            <div className="flex flex-col items-center justify-center text-center p-4 space-y-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-500/20 text-blue-600 dark:bg-blue-500/25 dark:text-blue-200">
                <Plus className="h-5 w-5" />
              </div>
              <div>
                <h2 className="font-semibold" style={{ color: 'var(--text-primary)' }}>
                  Create a task
                </h2>
                <p className="text-xs" style={{ color: 'var(--text-secondary)' }}>
                  Stay organized and track your progress by adding new tasks.
                </p>
              </div>
              <Button
                onClick={handleOpenModal}
                leftIcon={<Plus className="h-4 w-4" />}
                className="shadow-md"
              >
                Add new task
              </Button>
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
