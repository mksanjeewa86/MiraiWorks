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
  avatar_url?: string;
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
  avatar_url?: string;
}
