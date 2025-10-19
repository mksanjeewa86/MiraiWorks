import { API_ENDPOINTS } from './config';
import { apiClient } from './apiClient';
import type {
  TodoViewerCreate,
  TodoViewerListResponse,
  TodoViewer,
} from '@/types/todo-viewer';
import type { TodoListResponse } from '@/types/todo';

export const todoViewersApi = {
  /**
   * Get all todos that the current user can view as a viewer
   */
  async listViewableTodos(): Promise<TodoListResponse> {
    const response = await apiClient.get<TodoListResponse>(API_ENDPOINTS.TODOS.VIEWABLE);
    return response.data as TodoListResponse;
  },

  /**
   * Get list of viewers for a specific todo (creator only)
   */
  async getViewers(todoId: number): Promise<TodoViewerListResponse> {
    const response = await apiClient.get<TodoViewerListResponse>(
      API_ENDPOINTS.TODOS.VIEWERS.LIST(todoId)
    );
    return response.data as TodoViewerListResponse;
  },

  /**
   * Add a viewer to a todo (creator only)
   */
  async addViewer(todoId: number, payload: TodoViewerCreate): Promise<TodoViewer> {
    const response = await apiClient.post<TodoViewer>(
      API_ENDPOINTS.TODOS.VIEWERS.ADD(todoId),
      payload
    );
    return response.data as TodoViewer;
  },

  /**
   * Remove a viewer from a todo (creator only)
   */
  async removeViewer(todoId: number, viewerUserId: number): Promise<void> {
    await apiClient.delete(API_ENDPOINTS.TODOS.VIEWERS.REMOVE(todoId, viewerUserId));
  },
};
