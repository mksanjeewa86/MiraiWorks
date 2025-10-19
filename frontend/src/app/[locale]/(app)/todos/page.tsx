'use client';

import { useEffect, useMemo, useState, useCallback } from 'react';
import { useSearchParams } from 'next/navigation';
import { useTranslations } from 'next-intl';
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
  CalendarRange,
  FileText,
  X,
} from 'lucide-react';

import ProtectedRoute from '@/components/auth/ProtectedRoute';
import AppLayout from '@/components/layout/AppLayout';
import { Card } from '@/components/ui';
import { Badge } from '@/components/ui';
import { Button } from '@/components/ui';
import { Input } from '@/components/ui';
import { LoadingSpinner } from '@/components/ui';
import { ConfirmationModal } from '@/components/ui';
import TaskModal from '@/components/todos/TaskModal';
import ExtensionRequestModal from '@/components/todos/ExtensionRequestModal';
import ExtensionApproveDialog from '@/components/todos/ExtensionApproveDialog';
import ExtensionRejectDialog from '@/components/todos/ExtensionRejectDialog';
import ExtensionChangeDateDialog from '@/components/todos/ExtensionChangeDateDialog';
import { useToast } from '@/contexts/ToastContext';
import { useAuth } from '@/contexts/AuthContext';
import { todosApi } from '@/api/todos';
import { todoExtensionsApi } from '@/api/todo-extensions';
import type { Todo, ViewFilter, TodoItemProps, TodoExtensionRequest } from '@/types/todo';

function formatDisplayDate(input?: string | null, noDueDateText?: string): string {
  if (!input) return noDueDateText || 'No due date';
  const date = new Date(input);
  if (Number.isNaN(date.getTime())) return noDueDateText || 'No due date';
  return date.toLocaleString();
}

function formatRelativeTime(input?: string | null, t?: ReturnType<typeof useTranslations<'todos'>>): string {
  if (!input) return '';

  // Parse date in local timezone by appending local time if only date is provided
  let date: Date;
  if (input.includes('T')) {
    // Full datetime string
    date = new Date(input);
  } else {
    // Date-only string - treat as local date at midnight
    const [year, month, day] = input.split('-').map(Number);
    date = new Date(year, month - 1, day);
  }

  if (Number.isNaN(date.getTime())) return '';

  // Compare dates at midnight local time
  const now = new Date();
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const dueDate = new Date(date.getFullYear(), date.getMonth(), date.getDate());
  const diff = dueDate.getTime() - today.getTime();
  const days = Math.round(diff / (1000 * 60 * 60 * 24));

  if (!t) {
    // Fallback for when translation function is not provided
    if (days === 0) return 'Today';
    if (days > 0) return `${days} day${days === 1 ? '' : 's'} remaining`;
    const abs = Math.abs(days);
    return `${abs} day${abs === 1 ? '' : 's'} overdue`;
  }

  if (days === 0) return t('dates.today');
  if (days > 0) {
    return days === 1
      ? t('dates.daysRemaining', { count: days })
      : t('dates.daysRemaining_other', { count: days });
  }
  const abs = Math.abs(days);
  return abs === 1
    ? t('dates.daysOverdue', { count: abs })
    : t('dates.daysOverdue_other', { count: abs });
}

function TodoItem({
  todo,
  onEdit,
  onComplete,
  onReopen,
  onDelete,
  onRestore,
  loadingId,
  onRequestExtension,
  t,
}: TodoItemProps & { onRequestExtension?: (todo: Todo) => void; t: ReturnType<typeof useTranslations<'todos'>> }) {
  const { user } = useAuth();
  const isProcessing = loadingId === todo.id;
  const showExpired = todo.status === 'expired' || todo.is_expired;
  const isCompleted = todo.status === 'completed';
  const isDeleted = todo.is_deleted;

  // Check if current user is owner or assignee
  const isOwner = user && todo.owner_id === user.id;
  const isAssignee = user && todo.assignee_id === user.id;

  // Import utility for formatting UTC datetime in local timezone
  const formatDueDate = (dueDatetime?: string | null): string => {
    if (!dueDatetime) return '';

    // Parse UTC datetime and convert to local timezone
    const date = new Date(dueDatetime);
    if (Number.isNaN(date.getTime())) return '';

    // Format date part in local timezone
    const formattedDate = date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });

    // Format time part in local timezone (24-hour format)
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');

    return `${formattedDate} at ${hours}:${minutes}`;
  };

  // Different card styles based on assignment status
  const isAssignment = todo.todo_type === 'assignment';

  // Modern color scheme
  const cardColors = isDeleted
    ? 'bg-gray-50 border-gray-300 dark:bg-gray-900/50 dark:border-gray-700'
    : showExpired
      ? 'bg-rose-50 border-rose-300 dark:bg-rose-900/10 dark:border-rose-800'
      : isCompleted
        ? 'bg-emerald-50 border-emerald-300 dark:bg-emerald-900/10 dark:border-emerald-800'
        : isAssignment
          ? 'bg-gradient-to-br from-purple-50 to-pink-50 border-purple-300 dark:from-purple-900/10 dark:to-pink-900/10 dark:border-purple-700'
          : 'bg-white border-slate-200 dark:bg-slate-800/50 dark:border-slate-700';

  const iconColors = isDeleted
    ? 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400'
    : showExpired
      ? 'bg-rose-100 text-rose-600 dark:bg-rose-900/30 dark:text-rose-400'
      : isCompleted
        ? 'bg-emerald-100 text-emerald-600 dark:bg-emerald-900/30 dark:text-emerald-400'
        : isAssignment
          ? 'bg-gradient-to-br from-purple-100 to-pink-100 text-purple-600 dark:from-purple-900/30 dark:to-pink-900/30 dark:text-purple-400'
          : 'bg-indigo-100 text-indigo-600 dark:bg-indigo-900/30 dark:text-indigo-400';

  const assignmentBadgeColors = isAssignee
    ? 'bg-gradient-to-r from-blue-500 to-cyan-500 text-white'
    : 'bg-gradient-to-r from-purple-500 to-pink-500 text-white';

  return (
    <div
      className={`group relative overflow-hidden rounded-xl border-2 ${cardColors} shadow-sm hover:shadow-lg transition-all duration-300 flex flex-col h-full`}
    >
      {/* Assignment indicator ribbon - only show for assignees */}
      {isAssignment && isAssignee && (
        <div className="absolute top-0 right-0 z-10">
          <div className={`${assignmentBadgeColors} px-3 py-1 text-[10px] font-bold uppercase tracking-wider rounded-bl-lg shadow-md`}>
            Assigned to You
          </div>
        </div>
      )}

      {/* Header with icon and title - flex-1 to push footer down */}
      <div className="flex items-start gap-3 p-4 pb-3 flex-1">
        <div className={`flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-xl ${iconColors} shadow-sm`}>
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

        <div className="min-w-0 flex-1">
          {/* Title - adjusted spacing for assignment ribbon */}
          <div className={`mb-2 min-h-[3rem] ${isAssignment && isAssignee ? 'pr-20' : ''}`}>
            <h3
              className={`text-base font-bold leading-snug line-clamp-2 ${
                isDeleted ? 'line-through opacity-60' : ''
              }`}
              style={{
                color: 'var(--text-primary)',
                minHeight: '3rem',
                display: '-webkit-box',
                WebkitLineClamp: 2,
                WebkitBoxOrient: 'vertical',
                overflow: 'hidden'
              }}
            >
              {todo.title}
            </h3>
          </div>

          {/* Priority badge - after title */}
          {todo.priority && (
            <div className="mb-2">
              <span className="inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-bold bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-300 whitespace-nowrap shadow-sm">
                <ListCheck className="h-3.5 w-3.5" />
                {todo.priority.toUpperCase()}
              </span>
            </div>
          )}

          {/* Status badges */}
          <div className="flex flex-wrap items-center gap-1.5 mb-2">
            {isDeleted && (
              <span className="inline-flex items-center gap-1 rounded-lg px-2 py-1 text-xs font-semibold bg-gray-200 text-gray-700 dark:bg-gray-800 dark:text-gray-300">
                <Trash2 className="h-3.5 w-3.5" /> {t('badges.deleted')}
              </span>
            )}
            {showExpired && !isDeleted && (
              <span className="inline-flex items-center gap-1 rounded-lg px-2 py-1 text-xs font-semibold bg-rose-200 text-rose-800 dark:bg-rose-900/30 dark:text-rose-300">
                <AlertCircle className="h-3.5 w-3.5" /> {t('badges.overdue')}
              </span>
            )}
            {isCompleted && todo.completed_at && (
              <span className="inline-flex items-center gap-1 rounded-lg px-2 py-1 text-xs font-semibold bg-emerald-200 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-300">
                <CheckCircle2 className="h-3.5 w-3.5" /> Completed {new Date(todo.completed_at).toLocaleDateString()}
              </span>
            )}
          </div>

          {/* Due date - prominent display */}
          <div className="mb-2 min-h-[3.5rem]">
            {todo.due_datetime ? (
              <div className={`flex items-center gap-2 rounded-lg px-3 py-2 h-full ${
                showExpired
                  ? 'bg-rose-100 border border-rose-300 dark:bg-rose-900/20 dark:border-rose-800'
                  : isCompleted
                    ? 'bg-emerald-100 border border-emerald-300 dark:bg-emerald-900/20 dark:border-emerald-800'
                    : 'bg-blue-100 border border-blue-300 dark:bg-blue-900/20 dark:border-blue-800'
              }`}>
                <CalendarRange className={`h-4 w-4 flex-shrink-0 ${
                  showExpired
                    ? 'text-rose-600 dark:text-rose-400'
                    : isCompleted
                      ? 'text-emerald-600 dark:text-emerald-400'
                      : 'text-blue-600 dark:text-blue-400'
                }`} />
                <div className="flex-1 min-w-0">
                  <div className={`text-xs font-semibold truncate ${
                    showExpired
                      ? 'text-rose-700 dark:text-rose-300'
                      : isCompleted
                        ? 'text-emerald-700 dark:text-emerald-300'
                        : 'text-blue-700 dark:text-blue-300'
                  }`}>
                    {formatDueDate(todo.due_datetime)}
                  </div>
                  <div className={`text-[10px] font-medium ${
                    showExpired
                      ? 'text-rose-600 dark:text-rose-400'
                      : isCompleted
                        ? 'text-emerald-600 dark:text-emerald-400'
                        : 'text-blue-600 dark:text-blue-400'
                  }`}>
                    {formatRelativeTime(todo.due_datetime, t)}
                  </div>
                </div>
              </div>
            ) : (
              <div className="flex items-center justify-center h-full rounded-lg px-3 py-2 bg-gray-100 border border-gray-200 dark:bg-gray-800/50 dark:border-gray-700">
                <span className="text-xs text-gray-500 dark:text-gray-400">No due date</span>
              </div>
            )}
          </div>

          {/* Description */}
          {todo.description && (
            <p
              className={`text-sm leading-relaxed line-clamp-2 ${
                isDeleted ? 'opacity-50' : 'opacity-75'
              }`}
              style={{ color: 'var(--text-secondary)' }}
            >
              {todo.description}
            </p>
          )}

          {/* Notes - compact */}
          {todo.notes && (
            <div className="mt-2 rounded-lg bg-amber-50 border border-amber-300 p-2.5 dark:bg-amber-900/20 dark:border-amber-800/50 shadow-sm">
              <div className="flex items-center gap-1.5 text-xs font-semibold text-amber-700 dark:text-amber-300">
                <StickyNote className="h-3.5 w-3.5" />
                <span>{t('labels.notes')}</span>
              </div>
              <p className="mt-1 text-xs leading-relaxed text-amber-800 dark:text-amber-200 line-clamp-2">
                {todo.notes}
              </p>
            </div>
          )}
        </div>
      </div>

      {/* View button footer - flex-shrink-0 to keep at bottom */}
      <div className="border-t border-slate-200 dark:border-slate-700/50 bg-gradient-to-r from-slate-50 to-slate-100/50 dark:from-slate-800/30 dark:to-slate-900/30 px-4 py-3 flex-shrink-0 mt-auto">
        <Button
          size="sm"
          variant="outline"
          className="w-full h-9 text-sm font-semibold border-2 bg-white/80 border-slate-300 text-slate-700 hover:bg-slate-50 hover:border-slate-400 dark:bg-slate-800/50 dark:border-slate-600 dark:text-slate-300 dark:hover:bg-slate-800 dark:hover:border-slate-500 shadow-sm transition-all"
          onClick={() => onEdit(todo)}
          leftIcon={<ClipboardList className="h-4 w-4" />}
        >
          {t('actions.view')}
        </Button>
      </div>
    </div>
  );
}

function TodosPageContent() {
  const t = useTranslations('todos');
  const searchParams = useSearchParams();
  const { showToast } = useToast();
  const { user } = useAuth();

  // Tab state
  const [activeTab, setActiveTab] = useState<'todos' | 'extension-requests'>('todos');

  // Todos state
  const [todos, setTodos] = useState<Todo[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionLoadingId, setActionLoadingId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [viewFilter, setViewFilter] = useState<ViewFilter>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingTodo, setEditingTodo] = useState<Todo | null>(null);
  const [extensionRequestModal, setExtensionRequestModal] = useState<{
    isOpen: boolean;
    todo: Todo | null;
  }>({ isOpen: false, todo: null });

  // Extension requests state
  const [extensionRequests, setExtensionRequests] = useState<TodoExtensionRequest[]>([]);
  const [extensionRequestsLoading, setExtensionRequestsLoading] = useState(false);
  const [reviewingRequest, setReviewingRequest] = useState<TodoExtensionRequest | null>(null);
  const [approveDialogOpen, setApproveDialogOpen] = useState(false);
  const [rejectDialogOpen, setRejectDialogOpen] = useState(false);
  const [changeDateDialogOpen, setChangeDateDialogOpen] = useState(false);
  const [extensionActionLoading, setExtensionActionLoading] = useState(false);

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
      // Fetch both owned todos and assigned todos
      const [ownedResponse, assignedResponse] = await Promise.all([
        todosApi.list({
          includeCompleted: true,
          includeDeleted: true, // Always load all todos, filter client-side
          limit: 200,
        }),
        todosApi.listAssignedTodos({
          includeCompleted: true,
          limit: 200,
        }),
      ]);

      // Combine and deduplicate todos by ID
      const allTodos = [...ownedResponse.items, ...assignedResponse.items];
      const uniqueTodos = Array.from(
        new Map(allTodos.map(todo => [todo.id, todo])).values()
      );

      setTodos(uniqueTodos);
      setError(null);
    } catch (err) {
      console.error(err);
      setError(err instanceof Error ? err.message : t('toasts.loadError'));
      showToast({ type: 'error', title: t('toasts.loadError') });
    } finally {
      setLoading(false);
    }
  }, [showToast, t]);

  const loadExtensionRequests = useCallback(async () => {
    setExtensionRequestsLoading(true);
    try {
      const response = await todoExtensionsApi.listRequestsToReview({
        status: 'pending',
        limit: 100,
      });
      setExtensionRequests(response.items || []);
    } catch (err) {
      console.error(err);
      showToast({ type: 'error', title: 'Failed to load extension requests' });
    } finally {
      setExtensionRequestsLoading(false);
    }
  }, [showToast]);

  useEffect(() => {
    void loadTodos();
    void loadExtensionRequests(); // Load extension requests on mount for badge count
  }, [loadTodos, loadExtensionRequests]);

  // Check URL for edit parameter and open modal automatically
  useEffect(() => {
    const editId = searchParams?.get('edit');
    if (editId && todos.length > 0) {
      const todoId = parseInt(editId, 10);
      if (!isNaN(todoId)) {
        const todoToEdit = todos.find(t => t.id === todoId);
        if (todoToEdit) {
          setEditingTodo(todoToEdit);
          setIsModalOpen(true);
          // Clear the URL parameter after opening the modal
          window.history.replaceState({}, '', '/todos');
        }
      }
    }
  }, [searchParams, todos]);

  const stats = useMemo(() => {
    const nonDeletedTodos = todos.filter((todo) => !todo.is_deleted);
    const pendingCount = nonDeletedTodos.filter(
      (todo) => !['completed', 'expired'].includes(todo.status)
    ).length;
    const completedCount = nonDeletedTodos.filter((todo) => todo.status === 'completed').length;
    const expiredCount = nonDeletedTodos.filter(
      (todo) => todo.status === 'expired' || todo.is_expired
    ).length;
    const deletedCount = todos.filter((todo) => todo.is_deleted).length;
    return {
      pendingCount,
      completedCount,
      expiredCount,
      deletedCount,
      total: nonDeletedTodos.length,
    };
  }, [todos]);

  const activeTodos = useMemo(
    () =>
      todos.filter((todo) => !todo.is_deleted && !['completed', 'expired'].includes(todo.status)),
    [todos]
  );

  const expiredTodos = useMemo(
    () =>
      todos.filter((todo) => !todo.is_deleted && (todo.status === 'expired' || todo.is_expired)),
    [todos]
  );

  const completedTodos = useMemo(
    () => todos.filter((todo) => !todo.is_deleted && todo.status === 'completed'),
    [todos]
  );

  const deletedTodos = useMemo(() => todos.filter((todo) => todo.is_deleted), [todos]);

  const dueTodayCount = useMemo(() => {
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const todayString = today.toDateString();

    return activeTodos.filter((todo) => {
      if (!todo.due_datetime) return false;

      // Parse UTC datetime and convert to local timezone
      const due = new Date(todo.due_datetime);
      if (Number.isNaN(due.getTime())) return false;

      return due.toDateString() === todayString;
    }).length;
  }, [activeTodos]);

  const upcomingCount = useMemo(() => {
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const inSevenDays = new Date(today.getTime() + 7 * 24 * 60 * 60 * 1000);

    return activeTodos.filter((todo) => {
      if (!todo.due_datetime) return false;

      // Parse UTC datetime and convert to local timezone
      const due = new Date(todo.due_datetime);
      if (Number.isNaN(due.getTime())) return false;

      // Compare at date level (midnight)
      const dueDate = new Date(due.getFullYear(), due.getMonth(), due.getDate());
      return dueDate > today && dueDate <= inSevenDays;
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

    // Helper to parse UTC datetime
    const parseDatetime = (datetimeStr?: string | null): number => {
      if (!datetimeStr) return Number.POSITIVE_INFINITY;

      const date = new Date(datetimeStr);
      return Number.isNaN(date.getTime()) ? Number.POSITIVE_INFINITY : date.getTime();
    };

    const result = [...baseList];
    result.sort((a, b) => {
      const weightDiff = viewFilter === 'all' ? getStatusWeight(a) - getStatusWeight(b) : 0;
      if (weightDiff !== 0) return weightDiff;

      const dateA = parseDatetime(a.due_datetime);
      const dateB = parseDatetime(b.due_datetime);
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
  const openConfirmationModal = (
    todo: Todo,
    action: 'delete' | 'restore' | 'complete' | 'reopen'
  ) => {
    setConfirmationModal({ isOpen: true, todo, action });
  };

  const closeConfirmationModal = () => {
    setConfirmationModal({ isOpen: false, todo: null, action: null });
  };

  const trimmedSearch = searchQuery.trim();
  const hasSearch = trimmedSearch.length > 0;

  const emptyStateCopy: Record<ViewFilter, { title: string; description: string }> = {
    all: {
      title: t('emptyStates.all.title'),
      description: t('emptyStates.all.description'),
    },
    active: {
      title: t('emptyStates.active.title'),
      description: t('emptyStates.active.description'),
    },
    completed: {
      title: t('emptyStates.completed.title'),
      description: t('emptyStates.completed.description'),
    },
    expired: {
      title: t('emptyStates.expired.title'),
      description: t('emptyStates.expired.description'),
    },
    deleted: {
      title: t('emptyStates.deleted.title'),
      description: t('emptyStates.deleted.description'),
    },
  };

  const viewFilters: Array<{ label: string; value: ViewFilter }> = [
    { label: t('filters.all'), value: 'all' },
    { label: t('filters.active'), value: 'active' },
    { label: t('filters.completed'), value: 'completed' },
    { label: t('filters.expired'), value: 'expired' },
    { label: t('filters.deleted'), value: 'deleted' },
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
      label: t('stats.inProgress'),
      value: stats.pendingCount,
      icon: <ListCheck className="h-5 w-5" />,
      accentClass: 'bg-blue-500/20 text-blue-700 dark:bg-blue-500/25 dark:text-blue-200',
    },
    {
      label: t('stats.dueToday'),
      value: dueTodayCount,
      icon: <Sun className="h-5 w-5" />,
      accentClass: 'bg-amber-500/20 text-amber-700 dark:bg-amber-500/25 dark:text-amber-200',
    },
    {
      label: t('stats.completed'),
      value: stats.completedCount,
      icon: <CheckCircle2 className="h-5 w-5" />,
      accentClass:
        'bg-emerald-500/20 text-emerald-700 dark:bg-emerald-500/25 dark:text-emerald-200',
    },
    {
      label: t('stats.overdue'),
      value: stats.expiredCount,
      icon: <AlertCircle className="h-5 w-5" />,
      accentClass: 'bg-red-500/20 text-red-700 dark:bg-red-500/25 dark:text-red-200',
    },
  ];

  const heroMeta = `${upcomingCount === 1 ? t('hero.tasksThisWeek', { count: upcomingCount }) : t('hero.tasksThisWeek_other', { count: upcomingCount })} ${t('hero.and')} ${t('hero.overdue', { count: stats.expiredCount })}`;

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
      showToast({ type: 'success', title: t('toasts.completed') });
      await loadTodos();
    } catch (err) {
      console.error(err);
      showToast({
        type: 'error',
        title: err instanceof Error ? err.message : t('toasts.completeError'),
      });
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
      showToast({ type: 'success', title: t('toasts.reopened') });
      await loadTodos();
    } catch (err) {
      console.error(err);
      showToast({
        type: 'error',
        title: err instanceof Error ? err.message : t('toasts.reopenError'),
      });
    } finally {
      setActionLoadingId(null);
    }
  };

  const handleDelete = (todo: Todo) => {
    openConfirmationModal(todo, 'delete');
  };

  const handleRequestExtension = (todo: Todo) => {
    // Check if current user is the owner or assignee
    const isOwner = user && todo.owner_id === user.id;
    const isAssignee = user && todo.assignee_id === user.id;

    if (user && (isOwner || isAssignee)) {
      setExtensionRequestModal({ isOpen: true, todo });
    } else {
      showToast({
        type: 'error',
        title: t('toasts.extensionOnlyOwner'),
      });
    }
  };

  const handleApproveRequest = (request: TodoExtensionRequest) => {
    setReviewingRequest(request);
    setApproveDialogOpen(true);
  };

  const handleChangeDate = (request: TodoExtensionRequest) => {
    setReviewingRequest(request);
    setChangeDateDialogOpen(true);
  };

  const handleRejectRequest = (request: TodoExtensionRequest) => {
    setReviewingRequest(request);
    setRejectDialogOpen(true);
  };

  const executeApprove = async () => {
    if (!reviewingRequest) return;

    setExtensionActionLoading(true);
    try {
      await todoExtensionsApi.respondToExtensionRequest(reviewingRequest.id, {
        status: 'approved',
      });
      showToast({ type: 'success', title: 'Extension request approved' });
      await loadExtensionRequests();
      await loadTodos();
      setApproveDialogOpen(false);
      setReviewingRequest(null);
    } catch (err) {
      console.error(err);
      showToast({ type: 'error', title: 'Failed to approve extension request' });
    } finally {
      setExtensionActionLoading(false);
    }
  };

  const executeReject = async (reason: string) => {
    if (!reviewingRequest) return;

    setExtensionActionLoading(true);
    try {
      await todoExtensionsApi.respondToExtensionRequest(reviewingRequest.id, {
        status: 'rejected',
        response_reason: reason,
      });
      showToast({ type: 'error', title: 'Extension request rejected' });
      await loadExtensionRequests();
      await loadTodos();
      setRejectDialogOpen(false);
      setReviewingRequest(null);
    } catch (err) {
      console.error(err);
      showToast({ type: 'error', title: 'Failed to reject extension request' });
    } finally {
      setExtensionActionLoading(false);
    }
  };

  const executeChangeDate = async (newDate: string, newTime: string, reason?: string) => {
    if (!reviewingRequest) return;

    setExtensionActionLoading(true);
    try {
      // Combine date and time into ISO datetime string and convert to UTC
      // User enters in local timezone, we need to send UTC to backend
      const localDateTime = `${newDate}T${newTime}:00`;
      const localDate = new Date(localDateTime);
      const newDueDateTime = localDate.toISOString(); // Converts to UTC ISO format

      await todoExtensionsApi.respondToExtensionRequest(reviewingRequest.id, {
        status: 'approved',
        response_reason: reason || `Date changed to ${newDate} ${newTime}`,
        new_due_date: newDueDateTime,
      });
      showToast({ type: 'success', title: 'Extension approved with modified date' });
      await loadExtensionRequests();
      await loadTodos();
      setChangeDateDialogOpen(false);
      setReviewingRequest(null);
    } catch (err) {
      console.error(err);
      showToast({ type: 'error', title: 'Failed to approve extension request' });
    } finally {
      setExtensionActionLoading(false);
    }
  };

  const executeDelete = async (todo: Todo) => {
    setActionLoadingId(todo.id);
    try {
      await todosApi.remove(todo.id);
      showToast({ type: 'success', title: t('toasts.deleted') });
      await loadTodos();
    } catch (err) {
      console.error(err);
      showToast({
        type: 'error',
        title: err instanceof Error ? err.message : t('toasts.deleteError'),
      });
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
      showToast({ type: 'success', title: t('toasts.restored') });
      await loadTodos();
    } catch (err) {
      console.error(err);
      showToast({
        type: 'error',
        title: err instanceof Error ? err.message : t('toasts.restoreError'),
      });
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
        return t('confirmations.delete.title');
      case 'restore':
        return t('confirmations.restore.title');
      case 'complete':
        return t('confirmations.complete.title');
      case 'reopen':
        return t('confirmations.reopen.title');
      default:
        return '';
    }
  };

  const getConfirmationMessage = () => {
    if (!confirmationModal.todo || !confirmationModal.action) return '';
    const todoTitle = confirmationModal.todo.title;
    switch (confirmationModal.action) {
      case 'delete':
        return t('confirmations.delete.message', { title: todoTitle });
      case 'restore':
        return t('confirmations.restore.message', { title: todoTitle });
      case 'complete':
        return t('confirmations.complete.message', { title: todoTitle });
      case 'reopen':
        return t('confirmations.reopen.message', { title: todoTitle });
      default:
        return '';
    }
  };

  const getConfirmationButtonText = () => {
    if (!confirmationModal.action) return '';
    switch (confirmationModal.action) {
      case 'delete':
        return t('confirmations.delete.confirmButton');
      case 'restore':
        return t('confirmations.restore.confirmButton');
      case 'complete':
        return t('confirmations.complete.confirmButton');
      case 'reopen':
        return t('confirmations.reopen.confirmButton');
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
        onComplete={handleComplete}
        onReopen={handleReopen}
        onDelete={handleDelete}
        onRestore={handleRestore}
        onRequestExtension={handleRequestExtension}
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

      {extensionRequestModal.todo && (
        <ExtensionRequestModal
          isOpen={extensionRequestModal.isOpen}
          onClose={() => setExtensionRequestModal({ isOpen: false, todo: null })}
          todo={extensionRequestModal.todo}
          onSuccess={() => {
            setExtensionRequestModal({ isOpen: false, todo: null });
            showToast({ type: 'success', title: t('toasts.extensionSubmitted') });
          }}
        />
      )}

      <ExtensionApproveDialog
        isOpen={approveDialogOpen}
        onClose={() => {
          setApproveDialogOpen(false);
          setReviewingRequest(null);
        }}
        onConfirm={executeApprove}
        request={reviewingRequest}
        loading={extensionActionLoading}
      />

      <ExtensionRejectDialog
        isOpen={rejectDialogOpen}
        onClose={() => {
          setRejectDialogOpen(false);
          setReviewingRequest(null);
        }}
        onConfirm={executeReject}
        request={reviewingRequest}
        loading={extensionActionLoading}
      />

      <ExtensionChangeDateDialog
        isOpen={changeDateDialogOpen}
        onClose={() => {
          setChangeDateDialogOpen(false);
          setReviewingRequest(null);
        }}
        onConfirm={executeChangeDate}
        request={reviewingRequest}
        loading={extensionActionLoading}
      />

      <div className="space-y-6 px-4 py-4 md:px-8 lg:px-12">
        <div className="relative overflow-hidden rounded-2xl border border-gray-200/80 bg-white/80 shadow-md dark:border-gray-800/70 dark:bg-gray-900/70">
          <div className="absolute inset-0 bg-gradient-to-r from-blue-500/20 via-purple-500/20 to-transparent dark:from-blue-500/15 dark:via-purple-500/20" />
          <div className="relative z-10 flex flex-col gap-6 p-6 lg:flex-row lg:items-center lg:justify-between">
            <div className="max-w-2xl space-y-3">
              <span className="inline-flex items-center gap-2 rounded-full bg-white/70 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-blue-600 dark:bg-gray-900/70 dark:text-blue-300">
                <Sparkles className="h-4 w-4" /> {t('page.focusMode')}
              </span>
              <div>
                <h1
                  className="text-3xl font-bold tracking-tight"
                  style={{ color: 'var(--text-primary)' }}
                >
                  {t('page.title')}
                </h1>
              </div>
              <div className="flex flex-wrap items-center gap-3">
                <Button
                  leftIcon={<Plus className="h-4 w-4" />}
                  onClick={handleOpenModal}
                  className="shadow-md"
                >
                  {t('page.addNewTask')}
                </Button>
                <div
                  className="flex items-center gap-2 text-sm"
                  style={{ color: 'var(--text-muted)' }}
                >
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
                  <div
                    className={`mb-2 inline-flex h-8 w-8 items-center justify-center rounded-lg ${stat.accentClass}`}
                  >
                    {stat.icon}
                  </div>
                  <p
                    className="text-xs font-medium uppercase tracking-wide"
                    style={{ color: 'var(--text-muted)' }}
                  >
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

        {/* Tab Navigation */}
        <div className="mb-6">
          <div className="border-b border-gray-200 dark:border-gray-700">
            <nav className="-mb-px flex space-x-8">
              <button
                onClick={() => setActiveTab('todos')}
                className={`
                  py-4 px-1 border-b-2 font-medium text-sm transition-colors
                  ${activeTab === 'todos'
                    ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
                  }
                `}
              >
                <div className="flex items-center gap-2">
                  <ClipboardList className="h-5 w-5" />
                  Todos
                </div>
              </button>
              <button
                onClick={() => setActiveTab('extension-requests')}
                className={`
                  py-4 px-1 border-b-2 font-medium text-sm transition-colors
                  ${activeTab === 'extension-requests'
                    ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
                  }
                `}
              >
                <div className="flex items-center gap-2">
                  <FileText className="h-5 w-5" />
                  Extension Requests
                  {extensionRequests.length > 0 && (
                    <span className="inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-white bg-red-600 rounded-full">
                      {extensionRequests.length}
                    </span>
                  )}
                </div>
              </button>
            </nav>
          </div>
        </div>

        <div className="max-w-5xl mx-auto">
          {/* Todos Tab */}
          {activeTab === 'todos' && (
            <>
              <Card
                className="space-y-6 border border-gray-200/80 bg-white/80 backdrop-blur-sm dark:border-gray-800/70 dark:bg-gray-900/70"
                shadow="md"
              >
            <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
              <div>
                <h2 className="text-xl font-semibold" style={{ color: 'var(--text-primary)' }}>
                  {t('page.taskOverview')}
                </h2>
              </div>
              <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-end">
                <div className="flex flex-wrap items-center gap-1 rounded-full border border-gray-200/70 bg-gradient-to-r from-white/80 to-gray-50/80 p-1.5 shadow-inner backdrop-blur-sm dark:border-gray-700/60 dark:from-gray-800/80 dark:to-gray-900/80">
                  {viewFilters.map((filter) => {
                    const isActive = viewFilter === filter.value;
                    const baseClasses =
                      'relative rounded-full px-4 py-2 text-sm font-medium transition-all duration-200 ease-in-out focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 transform hover:scale-105';
                    const activeClasses =
                      'bg-gradient-to-r from-blue-600 to-blue-700 text-white shadow-lg shadow-blue-500/25 ring-2 ring-blue-200/50 dark:from-blue-500 dark:to-blue-600 dark:ring-blue-400/30';
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
                    placeholder={t('search.placeholder')}
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
                    {hasSearch ? t('emptyStates.noSearchResults.title') : emptyStateCopy[viewFilter].title}
                  </h3>
                  <p className="mt-2 text-sm" style={{ color: 'var(--text-secondary)' }}>
                    {hasSearch
                      ? t('emptyStates.noSearchResults.description')
                      : emptyStateCopy[viewFilter].description}
                  </p>
                </div>
              ) : (
                <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4 auto-rows-fr">
                  {filteredTodos.map((todo) => (
                    <TodoItem
                      key={todo.id}
                      todo={todo}
                      onEdit={handleEdit}
                      onComplete={handleComplete}
                      onReopen={handleReopen}
                      onDelete={handleDelete}
                      onRestore={handleRestore}
                      onRequestExtension={handleRequestExtension}
                      loadingId={actionLoadingId}
                      t={t}
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
                  {t('createTask.title')}
                </h2>
                <p className="text-xs" style={{ color: 'var(--text-secondary)' }}>
                  {t('createTask.description')}
                </p>
              </div>
              <Button
                onClick={handleOpenModal}
                leftIcon={<Plus className="h-4 w-4" />}
                className="shadow-md"
              >
                {t('page.addNewTask')}
              </Button>
            </div>
          </Card>
            </>
          )}

          {/* Extension Requests Tab */}
          {activeTab === 'extension-requests' && (
            <Card
              className="space-y-6 border border-gray-200/80 bg-white/80 backdrop-blur-sm dark:border-gray-800/70 dark:bg-gray-900/70"
              shadow="md"
            >
              <div>
                <h2 className="text-xl font-semibold" style={{ color: 'var(--text-primary)' }}>
                  Extension Requests
                </h2>
                <p className="text-sm mt-1" style={{ color: 'var(--text-secondary)' }}>
                  Review and respond to extension requests from your team
                </p>
              </div>

              {extensionRequestsLoading ? (
                <div className="flex items-center justify-center h-40">
                  <LoadingSpinner className="w-8 h-8" />
                </div>
              ) : extensionRequests.length === 0 ? (
                <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed border-gray-300 bg-white/70 p-10 text-center dark:border-gray-700 dark:bg-gray-900/60">
                  <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-300">
                    <FileText className="h-6 w-6" />
                  </div>
                  <h3 className="text-lg font-semibold" style={{ color: 'var(--text-primary)' }}>
                    No Extension Requests
                  </h3>
                  <p className="mt-2 text-sm" style={{ color: 'var(--text-secondary)' }}>
                    You have no pending extension requests to review
                  </p>
                </div>
              ) : (
                <div className="space-y-4">
                  {extensionRequests.map((request) => (
                    <div
                      key={request.id}
                      className="rounded-xl border-2 border-slate-200 bg-white p-4 shadow-sm hover:shadow-lg transition-all duration-300 dark:border-slate-700 dark:bg-slate-800/50"
                    >
                      <div className="space-y-3">
                        <div className="flex items-start justify-between gap-4">
                          <div className="flex-1">
                            <h3 className="text-base font-bold text-slate-900 dark:text-slate-100">
                              {request.todo.title}
                            </h3>
                            <p className="text-sm text-slate-600 dark:text-slate-400 mt-1">
                              Requested by: {request.requested_by.full_name}
                            </p>
                          </div>
                          <span className="inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-bold bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-300 whitespace-nowrap shadow-sm">
                            Pending
                          </span>
                        </div>

                        <div className="grid gap-3 sm:grid-cols-2">
                          <div className="rounded-lg bg-slate-50 p-3 dark:bg-slate-900/50">
                            <p className="text-xs font-medium text-slate-500 dark:text-slate-400">
                              Current Due Date
                            </p>
                            <p className="text-sm font-semibold text-slate-900 dark:text-slate-100 mt-1">
                              {(() => {
                                // Use actual todo's due datetime, convert from UTC to local
                                if (!request.todo.due_datetime) return 'No due date';
                                const date = new Date(request.todo.due_datetime);
                                if (Number.isNaN(date.getTime())) return 'Invalid date';

                                const formatted = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
                                const hours = String(date.getHours()).padStart(2, '0');
                                const minutes = String(date.getMinutes()).padStart(2, '0');
                                return `${formatted} at ${hours}:${minutes}`;
                              })()}
                            </p>
                          </div>
                          <div className="rounded-lg bg-blue-50 p-3 dark:bg-blue-900/20">
                            <p className="text-xs font-medium text-blue-700 dark:text-blue-400">
                              Requested Due Date
                            </p>
                            <p className="text-sm font-semibold text-blue-900 dark:text-blue-100 mt-1">
                              {new Date(request.requested_due_date).toLocaleString()}
                            </p>
                          </div>
                        </div>

                        {request.reason && (
                          <div className="rounded-lg bg-amber-50 border border-amber-300 p-3 dark:bg-amber-900/20 dark:border-amber-800/50">
                            <p className="text-xs font-semibold text-amber-700 dark:text-amber-300 mb-1">
                              Reason
                            </p>
                            <p className="text-sm text-amber-900 dark:text-amber-100">
                              {request.reason}
                            </p>
                          </div>
                        )}

                        <div className="flex gap-2 pt-2">
                          <Button
                            size="sm"
                            className="flex-1 bg-green-600 hover:bg-green-700 text-white"
                            leftIcon={<CheckCircle2 className="h-4 w-4" />}
                            onClick={() => handleApproveRequest(request)}
                          >
                            Approve
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            className="flex-1 border-blue-500 text-blue-600 hover:bg-blue-50 dark:border-blue-400 dark:text-blue-400"
                            leftIcon={<CalendarRange className="h-4 w-4" />}
                            onClick={() => handleChangeDate(request)}
                          >
                            Change Date
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            className="flex-1 border-red-500 text-red-600 hover:bg-red-50 dark:border-red-400 dark:text-red-400"
                            leftIcon={<X className="h-4 w-4" />}
                            onClick={() => handleRejectRequest(request)}
                          >
                            Reject
                          </Button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </Card>
          )}
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
