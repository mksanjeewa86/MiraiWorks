import { type ReactNode } from 'react';
import type { User, AuthResponse, LoginCredentials, RegisterData } from '@/types';
import { AppNotification } from './notification';

// ====================
// AUTH CONTEXT INTERFACES
// ====================

export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  accessToken: string | null;
  refreshToken: string | null;
  require2FA: boolean;
  pendingUserId: number | null;
}

export type AuthAction =
  | { type: 'AUTH_START' }
  | { type: 'AUTH_SUCCESS'; payload: AuthResponse }
  | { type: 'AUTH_ERROR'; payload: string }
  | { type: 'LOGOUT' }
  | { type: 'CLEAR_ERROR' }
  | { type: 'UPDATE_USER'; payload: User }
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'REQUIRE_2FA'; payload: { userId: number; email: string } };

export interface AuthContextType extends AuthState {
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => void;
  verifyTwoFactor: (code: string) => Promise<void>;
  refreshAuth: () => Promise<AuthResponse>;
  updateUser: (user: User) => void;
  clearError: () => void;
}

export interface AuthProviderProps {
  children: ReactNode;
}

// ====================
// NOTIFICATIONS CONTEXT INTERFACES
// ====================

export interface NotificationsContextType {
  notifications: AppNotification[];
  unreadCount: number;
  showNotification: (title: string, message: string, type?: string) => void;
  markAsRead: (notificationIds: number[]) => Promise<void>;
  markAllAsRead: () => Promise<void>;
  refreshNotifications: () => Promise<void>;
  refreshUnreadCount: () => Promise<void>;
}

export interface NotificationsProviderProps {
  children: ReactNode;
}

// ====================
// TOAST CONTEXT INTERFACES
// ====================

export interface ToastContextType {
  // Will be defined when ToastContext implementation is examined
  showToast?: (message: string, type?: 'success' | 'error' | 'info' | 'warning') => void;
}

export interface ToastProviderProps {
  children: ReactNode;
}
