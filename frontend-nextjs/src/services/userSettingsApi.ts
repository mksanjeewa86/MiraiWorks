const API_BASE_URL = 'http://localhost:8000';

export interface UserSettings {
  // Profile settings
  job_title?: string;
  bio?: string;
  
  // Notification preferences
  email_notifications: boolean;
  push_notifications: boolean;
  sms_notifications: boolean;
  interview_reminders: boolean;
  application_updates: boolean;
  message_notifications: boolean;
  
  // UI preferences
  theme: 'light' | 'dark' | 'system';
  language: string;
  timezone: string;
  date_format: string;
  
  // Security settings
  require_2fa: boolean;
}

export interface UserProfile {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  phone?: string;
  full_name: string;
  job_title?: string;
  bio?: string;
}

export interface UserSettingsUpdate {
  // Profile settings
  job_title?: string;
  bio?: string;
  
  // Notification preferences
  email_notifications?: boolean;
  push_notifications?: boolean;
  sms_notifications?: boolean;
  interview_reminders?: boolean;
  application_updates?: boolean;
  message_notifications?: boolean;
  
  // UI preferences
  theme?: 'light' | 'dark' | 'system';
  language?: string;
  timezone?: string;
  date_format?: string;
  
  // Security settings
  require_2fa?: boolean;
}

export interface UserProfileUpdate {
  first_name?: string;
  last_name?: string;
  phone?: string;
  job_title?: string;
  bio?: string;
}

// Helper function to get auth token from localStorage
const getAuthToken = (): string | null => {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('accessToken');
  }
  return null;
};

// Helper function to make authenticated requests
const makeAuthenticatedRequest = async <T>(
  url: string, 
  options: RequestInit = {}
): Promise<{ data: T }> => {
  const token = getAuthToken();
  
  const response = await fetch(`${API_BASE_URL}${url}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
      ...options.headers,
    },
  });

  if (!response.ok) {
    throw new Error(`API request failed: ${response.status} ${response.statusText}`);
  }

  const data = await response.json();
  return { data };
};

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