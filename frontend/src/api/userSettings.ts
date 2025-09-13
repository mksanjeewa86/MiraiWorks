import {
  UserSettings,
  UserProfile,
  UserSettingsUpdate,
  UserProfileUpdate
} from '../types/userSettings';
import { makeAuthenticatedRequest } from '@/lib/apiClient';
import { API_ENDPOINTS } from '@/config/api';

export const userSettingsApi = {
  // Get current user's settings
  getSettings: () =>
    makeAuthenticatedRequest<UserSettings>(API_ENDPOINTS.USER.SETTINGS),

  // Update user settings
  updateSettings: (settings: UserSettingsUpdate) =>
    makeAuthenticatedRequest<UserSettings>(API_ENDPOINTS.USER.SETTINGS, {
      method: 'PUT',
      body: JSON.stringify(settings),
    }),

  // Get current user's profile
  getProfile: () =>
    makeAuthenticatedRequest<UserProfile>(API_ENDPOINTS.AUTH.ME),

  // Update user profile
  updateProfile: (profile: UserProfileUpdate) =>
    makeAuthenticatedRequest<UserProfile>(API_ENDPOINTS.AUTH.ME, {
      method: 'PUT',
      body: JSON.stringify(profile),
    }),
};