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
