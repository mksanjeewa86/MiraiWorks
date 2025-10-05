import { apiClient } from './apiClient';
import { API_ENDPOINTS } from './config';
import type { ApiResponse } from '@/types/api';
import type {
  QuestionBank,
  QuestionBankDetail,
  QuestionBankFormData,
  QuestionBankListResponse,
  QuestionBankStats,
} from '@/types/questionBank';

export const questionBankApi = {
  /**
   * Get all question banks with optional filters
   */
  async getQuestionBanks(params?: {
    page?: number;
    page_size?: number;
    exam_type?: string;
    difficulty?: string;
    is_public?: boolean;
    include_global?: boolean;
  }): Promise<ApiResponse<QuestionBankListResponse>> {
    try {
      let url = API_ENDPOINTS.QUESTION_BANKS.BASE;
      if (params) {
        const queryParams = new URLSearchParams();
        Object.entries(params).forEach(([key, value]) => {
          if (value !== undefined) {
            queryParams.append(key, String(value));
          }
        });
        const queryString = queryParams.toString();
        if (queryString) {
          url += `?${queryString}`;
        }
      }

      const response = await apiClient.get<QuestionBankListResponse>(url);
      return { data: response.data, success: true };
    } catch (error: any) {
      return {
        success: false,
        message: error.response?.data?.detail || 'Failed to fetch question banks',
        errors: [error.response?.data?.detail || 'Failed to fetch question banks'],
      };
    }
  },

  /**
   * Get a single question bank with details
   */
  async getQuestionBank(bankId: number): Promise<ApiResponse<QuestionBankDetail>> {
    try {
      const response = await apiClient.get<QuestionBankDetail>(
        API_ENDPOINTS.QUESTION_BANKS.BY_ID(bankId)
      );
      return { data: response.data, success: true };
    } catch (error: any) {
      return {
        success: false,
        message: error.response?.data?.detail || 'Failed to fetch question bank',
        errors: [error.response?.data?.detail || 'Failed to fetch question bank'],
      };
    }
  },

  /**
   * Create a new question bank
   */
  async createQuestionBank(
    data: QuestionBankFormData
  ): Promise<ApiResponse<QuestionBankDetail>> {
    try {
      const response = await apiClient.post<QuestionBankDetail>(
        API_ENDPOINTS.QUESTION_BANKS.BASE,
        data
      );
      return { data: response.data, success: true };
    } catch (error: any) {
      return {
        success: false,
        message: error.response?.data?.detail || 'Failed to create question bank',
        errors: [error.response?.data?.detail || 'Failed to create question bank'],
      };
    }
  },

  /**
   * Update a question bank
   */
  async updateQuestionBank(
    bankId: number,
    data: Partial<QuestionBankFormData>
  ): Promise<ApiResponse<QuestionBankDetail>> {
    try {
      const response = await apiClient.put<QuestionBankDetail>(
        API_ENDPOINTS.QUESTION_BANKS.BY_ID(bankId),
        data
      );
      return { data: response.data, success: true };
    } catch (error: any) {
      return {
        success: false,
        message: error.response?.data?.detail || 'Failed to update question bank',
        errors: [error.response?.data?.detail || 'Failed to update question bank'],
      };
    }
  },

  /**
   * Delete a question bank
   */
  async deleteQuestionBank(bankId: number): Promise<ApiResponse<void>> {
    try {
      await apiClient.delete(API_ENDPOINTS.QUESTION_BANKS.BY_ID(bankId));
      return { success: true };
    } catch (error: any) {
      return {
        success: false,
        message: error.response?.data?.detail || 'Failed to delete question bank',
        errors: [error.response?.data?.detail || 'Failed to delete question bank'],
      };
    }
  },

  /**
   * Get question bank statistics
   */
  async getQuestionBankStats(bankId: number): Promise<ApiResponse<QuestionBankStats>> {
    try {
      const response = await apiClient.get<QuestionBankStats>(
        API_ENDPOINTS.QUESTION_BANKS.STATS(bankId)
      );
      return { data: response.data, success: true };
    } catch (error: any) {
      return {
        success: false,
        message: error.response?.data?.detail || 'Failed to fetch question bank stats',
        errors: [error.response?.data?.detail || 'Failed to fetch question bank stats'],
      };
    }
  },

  /**
   * Clone a question bank
   */
  async cloneQuestionBank(bankId: number): Promise<ApiResponse<QuestionBankDetail>> {
    try {
      const response = await apiClient.post<QuestionBankDetail>(
        API_ENDPOINTS.QUESTION_BANKS.CLONE(bankId)
      );
      return { data: response.data, success: true };
    } catch (error: any) {
      return {
        success: false,
        message: error.response?.data?.detail || 'Failed to clone question bank',
        errors: [error.response?.data?.detail || 'Failed to clone question bank'],
      };
    }
  },
};
