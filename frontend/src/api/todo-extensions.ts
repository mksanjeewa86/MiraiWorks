import { API_ENDPOINTS } from './config';
import { apiClient } from './apiClient';
import type { 
  TodoExtensionValidation,
  TodoExtensionRequestCreate,
  TodoExtensionRequestResponse,
  TodoExtensionRequest,
  TodoExtensionRequestList,
  ExtensionRequestStatus
} from '@/types/todo';

export const todoExtensionsApi = {
  async validateExtensionRequest(
    todoId: number, 
    requestedDueDate: string
  ): Promise<TodoExtensionValidation> {
    const params = new URLSearchParams({ requested_due_date: requestedDueDate });
    const url = `${API_ENDPOINTS.TODOS.EXTENSIONS.VALIDATE(todoId)}?${params}`;
    const response = await apiClient.get<TodoExtensionValidation>(url);
    return response.data;
  },

  async createExtensionRequest(
    todoId: number, 
    request: TodoExtensionRequestCreate
  ): Promise<TodoExtensionRequest> {
    const response = await apiClient.post<TodoExtensionRequest>(
      API_ENDPOINTS.TODOS.EXTENSIONS.CREATE(todoId), 
      request
    );
    return response.data;
  },

  async respondToExtensionRequest(
    requestId: number, 
    response: TodoExtensionRequestResponse
  ): Promise<TodoExtensionRequest> {
    const apiResponse = await apiClient.put<TodoExtensionRequest>(
      API_ENDPOINTS.TODOS.EXTENSIONS.RESPOND(requestId), 
      response
    );
    return apiResponse.data;
  },

  async listMyRequests(params?: {
    status?: ExtensionRequestStatus;
    limit?: number;
    offset?: number;
  }): Promise<TodoExtensionRequestList> {
    const searchParams = new URLSearchParams();
    
    if (params?.status) {
      searchParams.set('status_filter', params.status);
    }
    if (params?.limit) {
      searchParams.set('limit', String(params.limit));
    }
    if (params?.offset) {
      searchParams.set('offset', String(params.offset));
    }
    
    const query = searchParams.toString();
    const url = query ? 
      `${API_ENDPOINTS.TODOS.EXTENSIONS.MY_REQUESTS}?${query}` : 
      API_ENDPOINTS.TODOS.EXTENSIONS.MY_REQUESTS;
    
    const response = await apiClient.get<TodoExtensionRequestList>(url);
    return response.data;
  },

  async listRequestsToReview(params?: {
    status?: ExtensionRequestStatus;
    limit?: number;
    offset?: number;
  }): Promise<TodoExtensionRequestList> {
    const searchParams = new URLSearchParams();
    
    if (params?.status) {
      searchParams.set('status_filter', params.status);
    }
    if (params?.limit) {
      searchParams.set('limit', String(params.limit));
    }
    if (params?.offset) {
      searchParams.set('offset', String(params.offset));
    }
    
    const query = searchParams.toString();
    const url = query ? 
      `${API_ENDPOINTS.TODOS.EXTENSIONS.TO_REVIEW}?${query}` : 
      API_ENDPOINTS.TODOS.EXTENSIONS.TO_REVIEW;
    
    const response = await apiClient.get<TodoExtensionRequestList>(url);
    return response.data;
  },

  async getExtensionRequest(requestId: number): Promise<TodoExtensionRequest> {
    const response = await apiClient.get<TodoExtensionRequest>(
      API_ENDPOINTS.TODOS.EXTENSIONS.BY_ID(requestId)
    );
    return response.data;
  }
};