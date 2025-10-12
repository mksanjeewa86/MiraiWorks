import { API_ENDPOINTS } from './config';
import { apiClient } from './apiClient';
import type {
  UserSettings,
  UserProfile,
  UserSettingsUpdate,
  UserProfileUpdate,
} from '@/types/userSettings';

export const userSettingsApi = {
  async getSettings(): Promise<{ data: UserSettings }> {
    return await apiClient.get<UserSettings>(API_ENDPOINTS.USER.SETTINGS);
  },

  async updateSettings(settings: UserSettingsUpdate): Promise<{ data: UserSettings }> {
    return await apiClient.put<UserSettings>(API_ENDPOINTS.USER.SETTINGS, settings);
  },

  async getProfile(): Promise<{ data: UserProfile }> {
    return await apiClient.get<UserProfile>(API_ENDPOINTS.USER.UPDATE_PROFILE);
  },

  async updateProfile(profile: UserProfileUpdate): Promise<{ data: UserProfile }> {
    return await apiClient.put<UserProfile>(API_ENDPOINTS.USER.UPDATE_PROFILE, profile);
  },
};
