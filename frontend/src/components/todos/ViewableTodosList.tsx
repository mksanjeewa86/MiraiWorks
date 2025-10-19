'use client';

import { useViewableTodos } from '@/hooks/useTodoViewers';
import { TodoItem } from './TodoItem';
import type { Todo } from '@/types/todo';

/**
 * Component to display todos that the user can view as a viewer
 *
 * These are todos where the user is added as a viewer (read-only access)
 */
export const ViewableTodosList: React.FC = () => {
  const { todos, total, isLoading, error } = useViewableTodos();

  if (isLoading) {
    return (
      <div className="p-4">
        <p className="text-gray-500">Loading viewable todos...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4">
        <p className="text-red-600">
          Error loading viewable todos: {error instanceof Error ? error.message : 'Unknown error'}
        </p>
      </div>
    );
  }

  if (total === 0) {
    return (
      <div className="p-4">
        <p className="text-gray-500">
          No shared todos. Todos shared with you will appear here.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold">Shared with Me ({total})</h2>
        <span className="text-sm text-gray-500">Read-only access</span>
      </div>
      <div className="space-y-2">
        {todos.map((todo: Todo) => (
          <TodoItem
            key={todo.id}
            todo={todo}
            onEdit={() => {}}
            onDelete={() => {}}
          />
        ))}
      </div>
    </div>
  );
};

export default ViewableTodosList;
