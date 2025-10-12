/**
 * Privacy settings API client
 */

import { makeAuthenticatedRequest } from './apiClient';
import { API_ENDPOINTS } from './config';

export interface PrivacySettings {
  id: number;
  user_id: number;
  profile_visibility: 'public' | 'recruiters' | 'private';
  searchable: boolean;
  show_email: boolean;
  show_phone: boolean;
  show_work_experience: boolean;
  show_education: boolean;
  show_skills: boolean;
  show_certifications: boolean;
  show_projects: boolean;
  show_resume: boolean;
  created_at: string;
  updated_at: string;
}

export interface PrivacySettingsUpdate {
  profile_visibility?: 'public' | 'recruiters' | 'private';
  searchable?: boolean;
  show_email?: boolean;
  show_phone?: boolean;
  show_work_experience?: boolean;
  show_education?: boolean;
  show_skills?: boolean;
  show_certifications?: boolean;
  show_projects?: boolean;
  show_resume?: boolean;
}

export const privacyApi = {
  /**
   * Get current user's privacy settings (creates defaults if not exists)
   */
  async getMySettings(): Promise<PrivacySettings> {
    const response = await makeAuthenticatedRequest<PrivacySettings>(
      API_ENDPOINTS.PRIVACY.ME,
      { method: 'GET' }
    );
    return response.data;
  },

  /**
   * Update current user's privacy settings
   */
  async updateMySettings(settings: PrivacySettingsUpdate): Promise<PrivacySettings> {
    const response = await makeAuthenticatedRequest<PrivacySettings>(
      API_ENDPOINTS.PRIVACY.ME,
      {
        method: 'PUT',
        body: JSON.stringify(settings),
      }
    );
    return response.data;
  },

  /**
   * Create privacy settings for current user
   */
  async createMySettings(settings: PrivacySettingsUpdate): Promise<PrivacySettings> {
    const response = await makeAuthenticatedRequest<PrivacySettings>(
      API_ENDPOINTS.PRIVACY.ME,
      {
        method: 'POST',
        body: JSON.stringify(settings),
      }
    );
    return response.data;
  },

  /**
   * Delete current user's privacy settings (resets to defaults)
   */
  async deleteMySettings(): Promise<void> {
    await makeAuthenticatedRequest<void>(
      API_ENDPOINTS.PRIVACY.ME,
      { method: 'DELETE' }
    );
  },
};
