import { apiClient } from './apiClient';
import { API_ENDPOINTS } from './config';
import type { ApiResponse } from '@/types';
import type {
  CompanyConnection,
  UserToCompanyConnectionCreate,
  CompanyToCompanyConnectionCreate,
  CompanyConnectionUpdate,
} from '@/types/company-connection';

export const companyConnectionsApi = {
  /**
   * Get all company connections for the current user
   */
  async getMyConnections(): Promise<ApiResponse<CompanyConnection[]>> {
    try {
      const response = await apiClient.get<CompanyConnection[]>(
        API_ENDPOINTS.COMPANY_CONNECTIONS.MY_CONNECTIONS
      );
      return {
        data: response.data,
        success: true,
      };
    } catch (error) {
      return {
        data: undefined,
        success: false,
        message: error instanceof Error ? error.message : 'Failed to fetch company connections',
      };
    }
  },

  /**
   * Get a specific company connection by ID
   */
  async getConnectionById(connectionId: number): Promise<ApiResponse<CompanyConnection>> {
    try {
      const response = await apiClient.get<CompanyConnection>(
        API_ENDPOINTS.COMPANY_CONNECTIONS.BY_ID(connectionId)
      );
      return {
        data: response.data,
        success: true,
      };
    } catch (error) {
      return {
        data: undefined,
        success: false,
        message: error instanceof Error ? error.message : 'Failed to fetch company connection',
      };
    }
  },

  /**
   * Create a user-to-company connection
   */
  async createUserToCompanyConnection(
    connectionData: UserToCompanyConnectionCreate
  ): Promise<ApiResponse<CompanyConnection>> {
    try {
      const response = await apiClient.post<CompanyConnection>(
        API_ENDPOINTS.COMPANY_CONNECTIONS.USER_TO_COMPANY,
        connectionData
      );
      return {
        data: response.data,
        success: true,
        message: 'Connection created successfully',
      };
    } catch (error) {
      return {
        data: undefined,
        success: false,
        message:
          error instanceof Error ? error.message : 'Failed to create user-to-company connection',
      };
    }
  },

  /**
   * Create a company-to-company connection
   */
  async createCompanyToCompanyConnection(
    connectionData: CompanyToCompanyConnectionCreate
  ): Promise<ApiResponse<CompanyConnection>> {
    try {
      const response = await apiClient.post<CompanyConnection>(
        API_ENDPOINTS.COMPANY_CONNECTIONS.COMPANY_TO_COMPANY,
        connectionData
      );
      return {
        data: response.data,
        success: true,
        message: 'Company connection created successfully',
      };
    } catch (error) {
      return {
        data: undefined,
        success: false,
        message:
          error instanceof Error
            ? error.message
            : 'Failed to create company-to-company connection',
      };
    }
  },

  /**
   * Update a company connection's permissions
   */
  async updateConnection(
    connectionId: number,
    updateData: CompanyConnectionUpdate
  ): Promise<ApiResponse<CompanyConnection>> {
    try {
      const response = await apiClient.put<CompanyConnection>(
        API_ENDPOINTS.COMPANY_CONNECTIONS.BY_ID(connectionId),
        updateData
      );
      return {
        data: response.data,
        success: true,
        message: 'Connection updated successfully',
      };
    } catch (error) {
      return {
        data: undefined,
        success: false,
        message: error instanceof Error ? error.message : 'Failed to update connection',
      };
    }
  },

  /**
   * Deactivate a company connection
   */
  async deactivateConnection(connectionId: number): Promise<ApiResponse<CompanyConnection>> {
    try {
      const response = await apiClient.put<CompanyConnection>(
        API_ENDPOINTS.COMPANY_CONNECTIONS.DEACTIVATE(connectionId)
      );
      return {
        data: response.data,
        success: true,
        message: 'Connection deactivated successfully',
      };
    } catch (error) {
      return {
        data: undefined,
        success: false,
        message: error instanceof Error ? error.message : 'Failed to deactivate connection',
      };
    }
  },

  /**
   * Activate a company connection
   */
  async activateConnection(connectionId: number): Promise<ApiResponse<CompanyConnection>> {
    try {
      const response = await apiClient.put<CompanyConnection>(
        API_ENDPOINTS.COMPANY_CONNECTIONS.ACTIVATE(connectionId)
      );
      return {
        data: response.data,
        success: true,
        message: 'Connection activated successfully',
      };
    } catch (error) {
      return {
        data: undefined,
        success: false,
        message: error instanceof Error ? error.message : 'Failed to activate connection',
      };
    }
  },
};
