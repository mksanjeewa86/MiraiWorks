import { API_ENDPOINTS } from './config';
import { apiClient } from './apiClient';
import type {
  Todo,
  TodoListResponse,
  TodoPayload,
  TodoListParams,
  AssignableUser,
  TodoWithAssignedUser,
  TodoAssignmentUpdate,
  TodoViewersUpdate,
} from '@/types/todo';

export const todosApi = {
  async list(params: TodoListParams = {}): Promise<TodoListResponse> {
    const searchParams = new URLSearchParams();

    if (params.includeCompleted === false) {
      searchParams.set('include_completed', 'false');
    }

    if (params.includeDeleted === true) {
      searchParams.set('include_deleted', 'true');
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
    const response = await apiClient.get<Todo[]>(`${API_ENDPOINTS.TODOS.RECENT}?limit=${limit}`);
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
    const response = await apiClient.post<Todo>(API_ENDPOINTS.TODOS.COMPLETE(id));
    return response.data as Todo;
  },

  async reopen(id: number): Promise<Todo> {
    const response = await apiClient.post<Todo>(API_ENDPOINTS.TODOS.REOPEN(id));
    return response.data as Todo;
  },

  async remove(id: number): Promise<Todo> {
    const response = await apiClient.delete<Todo>(API_ENDPOINTS.TODOS.BY_ID(id));
    return response.data as Todo;
  },

  async restore(id: number): Promise<Todo> {
    const response = await apiClient.post<Todo>(API_ENDPOINTS.TODOS.RESTORE(id));
    return response.data as Todo;
  },

  // Assignment-related methods
  async getAssignableUsers(): Promise<AssignableUser[]> {
    const response = await apiClient.get<AssignableUser[]>(API_ENDPOINTS.TODOS.ASSIGNABLE_USERS);
    return response.data as AssignableUser[];
  },

  async getTodoWithAssignedUser(id: number): Promise<TodoWithAssignedUser> {
    const response = await apiClient.get<TodoWithAssignedUser>(API_ENDPOINTS.TODOS.DETAILS(id));
    return response.data as TodoWithAssignedUser;
  },

  async assignTodo(id: number, assignment: TodoAssignmentUpdate): Promise<Todo> {
    const response = await apiClient.put<Todo>(API_ENDPOINTS.TODOS.ASSIGN(id), assignment);
    return response.data as Todo;
  },

  async listAssignedTodos(params: TodoListParams = {}): Promise<TodoListResponse> {
    const searchParams = new URLSearchParams();

    if (params.includeCompleted === false) {
      searchParams.set('include_completed', 'false');
    }

    if (typeof params.limit === 'number') {
      searchParams.set('limit', String(params.limit));
    }

    if (typeof params.offset === 'number') {
      searchParams.set('offset', String(params.offset));
    }

    const query = searchParams.toString();
    const url = query ? `${API_ENDPOINTS.TODOS.ASSIGNED}?${query}` : API_ENDPOINTS.TODOS.ASSIGNED;
    const response = await apiClient.get<TodoListResponse>(url);
    return response.data as TodoListResponse;
  },

  async updateViewers(id: number, viewers: TodoViewersUpdate): Promise<Todo> {
    const response = await apiClient.put<Todo>(API_ENDPOINTS.TODOS.VIEWERS(id), viewers);
    return response.data as Todo;
  },
};
