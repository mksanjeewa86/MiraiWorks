export interface AppNotification {
  id: number;
  type: string;
  title: string;
  message: string;
  payload?: unknown;
  is_read: boolean;
  created_at: string;
  read_at?: string;
}

export interface NotificationsResponse {
  notifications: AppNotification[];
}

export interface UnreadCountResponse {
  unread_count: number;
}
