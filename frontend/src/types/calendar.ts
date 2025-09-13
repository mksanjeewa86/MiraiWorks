export interface CalendarConnection {
  id: number;
  provider: 'google' | 'outlook';
  provider_email: string;
  display_name?: string;
  is_enabled: boolean;
  sync_events: boolean;
  sync_reminders: boolean;
  auto_create_meetings: boolean;
  status: 'connected' | 'error' | 'expired' | 'disabled';
  last_sync_at?: string;
  sync_error?: string;
  created_at: string;
  updated_at: string;
}

export interface CalendarConnectionUpdate {
  display_name?: string;
  is_enabled?: boolean;
  sync_events?: boolean;
  sync_reminders?: boolean;
  auto_create_meetings?: boolean;
  calendar_ids?: string[];
  default_calendar_id?: string;
}

export interface CalendarConnectionResponse {
  message: string;
  connection: CalendarConnection;
}

export interface CalendarListResponse {
  connections: CalendarConnection[];
}

export interface CalendarAuthResponse {
  auth_url: string;
}

export type CalendarProvider = 'google' | 'outlook';