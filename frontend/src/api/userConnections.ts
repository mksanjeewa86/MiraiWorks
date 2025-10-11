import { apiClient } from './apiClient';
import { API_ENDPOINTS } from './config';
import type { ApiResponse, ConnectedUser } from '@/types';

export const userConnectionsApi = {
  /**
   * Get all users connected to the current user
   */
  async getMyConnections(): Promise<ApiResponse<ConnectedUser[]>> {
    try {
      const response = await apiClient.get<ConnectedUser[]>(
        API_ENDPOINTS.USER_CONNECTIONS.MY_CONNECTIONS
      );
      return {
        data: response.data,
        success: true,
      };
    } catch (error) {
      return {
        data: undefined,
        success: false,
        message: error instanceof Error ? error.message : 'Failed to fetch connected users',
      };
    }
  },

  /**
   * Connect to a user
   */
  async connectToUser(userId: number): Promise<ApiResponse<{ message: string; connection_id: number }>> {
    try {
      const response = await apiClient.post<{ message: string; connection_id: number }>(
        API_ENDPOINTS.USER_CONNECTIONS.CONNECT(userId)
      );
      return {
        data: response.data,
        success: true,
      };
    } catch (error) {
      return {
        data: undefined,
        success: false,
        message: error instanceof Error ? error.message : 'Failed to connect to user',
      };
    }
  },

  /**
   * Disconnect from a user
   */
  async disconnectFromUser(userId: number): Promise<ApiResponse<{ message: string }>> {
    try {
      const response = await apiClient.delete<{ message: string }>(
        API_ENDPOINTS.USER_CONNECTIONS.DISCONNECT(userId)
      );
      return {
        data: response.data,
        success: true,
      };
    } catch (error) {
      return {
        data: undefined,
        success: false,
        message: error instanceof Error ? error.message : 'Failed to disconnect from user',
      };
    }
  },
};
