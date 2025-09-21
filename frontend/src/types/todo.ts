export type TodoStatus = 'pending' | 'in_progress' | 'completed' | 'expired';

export interface Todo {
  id: number;
  owner_id: number;
  title: string;
  description?: string | null;
  notes?: string | null;
  status: TodoStatus;
  priority?: string | null;
  due_date?: string | null;
  completed_at?: string | null;
  expired_at?: string | null;
  is_deleted: boolean;
  deleted_at?: string | null;
  created_at: string;
  updated_at: string;
  is_expired: boolean;
}

export interface TodoListResponse {
  items: Todo[];
  total: number;
}

export interface TodoPayload {
  title: string;
  description?: string | null;
  notes?: string | null;
  priority?: string | null;
  due_date?: string | null;
  status?: TodoStatus;
}

export interface TodoListParams {
  includeCompleted?: boolean;
  includeDeleted?: boolean;
  status?: TodoStatus | 'pending' | 'in_progress' | 'completed' | 'expired';
  limit?: number;
  offset?: number;
}

// UI-related types
export type ViewFilter = 'all' | 'active' | 'completed' | 'expired' | 'deleted';

export interface TodoItemProps {
  todo: Todo;
  onEdit: (todo: Todo) => void;
  onComplete: (todo: Todo) => void;
  onReopen: (todo: Todo) => void;
  onDelete: (todo: Todo) => void;
  onRestore: (todo: Todo) => void;
  loadingId: number | null;
}

// TaskModal component types
export interface TaskFormState {
  title: string;
  description: string;
  notes: string;
  dueDate: string;
  priority: string;
}

export interface TaskModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  editingTodo?: Todo | null;
}
