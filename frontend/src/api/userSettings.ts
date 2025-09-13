import {
  UserSettings,
  UserProfile,
  UserSettingsUpdate,
  UserProfileUpdate
} from '../types/userSettings';
import { makeAuthenticatedRequest } from '@/api/apiClient';

export const userSettingsApi = {
  // Get current user's settings
  getSettings: () =>
    makeAuthenticatedRequest<UserSettings>('/api/user/settings'),

  // Update user settings
  updateSettings: (settings: UserSettingsUpdate) =>
    makeAuthenticatedRequest<UserSettings>('/api/user/settings', {
      method: 'PUT',
      body: JSON.stringify(settings),
    }),

  // Get current user's profile
  getProfile: () =>
    makeAuthenticatedRequest<UserProfile>('/api/user/profile'),

  // Update user profile
  updateProfile: (profile: UserProfileUpdate) =>
    makeAuthenticatedRequest<UserProfile>('/api/user/profile', {
      method: 'PUT',
      body: JSON.stringify(profile),
    }),
};