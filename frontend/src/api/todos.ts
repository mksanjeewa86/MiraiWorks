import { API_ENDPOINTS } from '@/config/api';
import { apiClient } from './apiClient';
import type { Todo, TodoListResponse, TodoPayload, TodoListParams } from '@/types/todo';

export const todosApi = {
  async list(params: TodoListParams = {}): Promise<TodoListResponse> {
    const searchParams = new URLSearchParams();

    if (params.includeCompleted === false) {
      searchParams.set('include_completed', 'false');
    }

    if (params.status) {
      searchParams.set('status', params.status);
    }

    if (typeof params.limit === 'number') {
      searchParams.set('limit', String(params.limit));
    }

    if (typeof params.offset === 'number') {
      searchParams.set('offset', String(params.offset));
    }

    const query = searchParams.toString();
    const url = query ? `${API_ENDPOINTS.TODOS.BASE}?${query}` : API_ENDPOINTS.TODOS.BASE;
    const response = await apiClient.get<TodoListResponse>(url);
    return response.data as TodoListResponse;
  },

  async listRecent(limit = 5): Promise<Todo[]> {
    const response = await apiClient.get<Todo[]>(`${API_ENDPOINTS.TODOS.BASE}/recent?limit=${limit}`);
    return response.data as Todo[];
  },

  async create(payload: TodoPayload): Promise<Todo> {
    const response = await apiClient.post<Todo>(API_ENDPOINTS.TODOS.BASE, payload);
    return response.data as Todo;
  },

  async update(id: number, payload: Partial<TodoPayload>): Promise<Todo> {
    const response = await apiClient.put<Todo>(API_ENDPOINTS.TODOS.BY_ID(id), payload);
    return response.data as Todo;
  },

  async complete(id: number): Promise<Todo> {
    const response = await apiClient.post<Todo>(`${API_ENDPOINTS.TODOS.BY_ID(id)}/complete`);
    return response.data as Todo;
  },

  async reopen(id: number): Promise<Todo> {
    const response = await apiClient.post<Todo>(`${API_ENDPOINTS.TODOS.BY_ID(id)}/reopen`);
    return response.data as Todo;
  },

  async remove(id: number): Promise<void> {
    await apiClient.delete<void>(API_ENDPOINTS.TODOS.BY_ID(id));
  },
};
