import { useState, useEffect, useCallback } from 'react';
import { todoViewersApi } from '@/api/todo-viewers';
import type { TodoViewerCreate, TodoViewerWithUser } from '@/types/todo-viewer';
import type { Todo } from '@/types/todo';
import { toast } from 'sonner';

/**
 * Hook to manage todo viewers
 */
export const useTodoViewers = (todoId: number) => {
  const [viewers, setViewers] = useState<TodoViewerWithUser[]>([]);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [isAddingViewer, setIsAddingViewer] = useState(false);
  const [isRemovingViewer, setIsRemovingViewer] = useState(false);
  const [addViewerError, setAddViewerError] = useState<Error | null>(null);
  const [removeViewerError, setRemoveViewerError] = useState<Error | null>(null);

  const fetchViewers = useCallback(async () => {
    if (!todoId) return;

    setIsLoading(true);
    setError(null);

    try {
      const response = await todoViewersApi.getViewers(todoId);
      setViewers(response.items);
      setTotal(response.total);
    } catch (err: any) {
      const error = new Error(err.response?.data?.detail || err.message || 'Failed to load viewers');
      setError(error);
      toast.error(error.message);
    } finally {
      setIsLoading(false);
    }
  }, [todoId]);

  useEffect(() => {
    fetchViewers();
  }, [fetchViewers]);

  const addViewer = useCallback(
    async (payload: TodoViewerCreate, options?: { onSuccess?: () => void }) => {
      setIsAddingViewer(true);
      setAddViewerError(null);

      try {
        await todoViewersApi.addViewer(todoId, payload);
        toast.success('Viewer added successfully');
        await fetchViewers(); // Refresh the list
        options?.onSuccess?.();
      } catch (err: any) {
        const error = new Error(err.response?.data?.detail || err.message || 'Failed to add viewer');
        setAddViewerError(error);
        toast.error(error.message);
      } finally {
        setIsAddingViewer(false);
      }
    },
    [todoId, fetchViewers]
  );

  const removeViewer = useCallback(
    async (viewerUserId: number) => {
      setIsRemovingViewer(true);
      setRemoveViewerError(null);

      try {
        await todoViewersApi.removeViewer(todoId, viewerUserId);
        toast.success('Viewer removed successfully');
        await fetchViewers(); // Refresh the list
      } catch (err: any) {
        const error = new Error(err.response?.data?.detail || err.message || 'Failed to remove viewer');
        setRemoveViewerError(error);
        toast.error(error.message);
      } finally {
        setIsRemovingViewer(false);
      }
    },
    [todoId, fetchViewers]
  );

  return {
    viewers,
    total,
    isLoading,
    error,
    addViewer,
    removeViewer,
    isAddingViewer,
    isRemovingViewer,
    addViewerError,
    removeViewerError,
    refetch: fetchViewers,
  };
};

/**
 * Hook to get todos that the current user can view as a viewer
 */
export const useViewableTodos = () => {
  const [todos, setTodos] = useState<Todo[]>([]);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const fetchViewableTodos = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await todoViewersApi.listViewableTodos();
      setTodos(response.items);
      setTotal(response.total);
    } catch (err: any) {
      const error = new Error(
        err.response?.data?.detail || err.message || 'Failed to load viewable todos'
      );
      setError(error);
      toast.error(error.message);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchViewableTodos();
  }, [fetchViewableTodos]);

  return {
    todos,
    total,
    isLoading,
    error,
    refetch: fetchViewableTodos,
  };
};
