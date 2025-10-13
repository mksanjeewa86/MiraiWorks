/**
 * Recruiter profile API client
 */

import { makeAuthenticatedRequest } from './apiClient';
import { API_ENDPOINTS } from './config';
import type { ApiResponse } from '@/types';
import type {
  RecruiterProfile,
  RecruiterProfileCreate,
  RecruiterProfileUpdate,
} from '@/types/profile';

export const recruiterProfileApi = {
  /**
   * Get current user's recruiter profile
   */
  async getMyProfile(): Promise<RecruiterProfile> {
    const response = await makeAuthenticatedRequest<RecruiterProfile>(
      API_ENDPOINTS.RECRUITER_PROFILE.ME,
      { method: 'GET' }
    );
    return response.data;
  },

  /**
   * Create recruiter profile for current user
   */
  async createMyProfile(data: RecruiterProfileCreate): Promise<RecruiterProfile> {
    const response = await makeAuthenticatedRequest<RecruiterProfile>(
      API_ENDPOINTS.RECRUITER_PROFILE.ME,
      {
        method: 'POST',
        body: JSON.stringify(data),
      }
    );
    return response.data;
  },

  /**
   * Update current user's recruiter profile
   */
  async updateMyProfile(data: RecruiterProfileUpdate): Promise<RecruiterProfile> {
    const response = await makeAuthenticatedRequest<RecruiterProfile>(
      API_ENDPOINTS.RECRUITER_PROFILE.ME,
      {
        method: 'PUT',
        body: JSON.stringify(data),
      }
    );
    return response.data;
  },

  /**
   * Delete current user's recruiter profile
   */
  async deleteMyProfile(): Promise<void> {
    await makeAuthenticatedRequest<void>(
      API_ENDPOINTS.RECRUITER_PROFILE.ME,
      { method: 'DELETE' }
    );
  },

  /**
   * Get recruiter profile by user ID
   */
  async getProfileByUserId(userId: number): Promise<RecruiterProfile> {
    const response = await makeAuthenticatedRequest<RecruiterProfile>(
      API_ENDPOINTS.RECRUITER_PROFILE.BY_USER_ID(userId),
      { method: 'GET' }
    );
    return response.data;
  },
};
