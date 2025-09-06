'use client';

import { createContext, useContext, useReducer, useEffect, type ReactNode } from 'react';
import type { User, AuthResponse, LoginCredentials, RegisterData } from '@/types';
import { authApi } from '@/services/authApi';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  accessToken: string | null;
  refreshToken: string | null;
}

type AuthAction =
  | { type: 'AUTH_START' }
  | { type: 'AUTH_SUCCESS'; payload: AuthResponse }
  | { type: 'AUTH_ERROR'; payload: string }
  | { type: 'LOGOUT' }
  | { type: 'CLEAR_ERROR' }
  | { type: 'UPDATE_USER'; payload: User }
  | { type: 'SET_LOADING'; payload: boolean };

interface AuthContextType extends AuthState {
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => void;
  verifyTwoFactor: (code: string) => Promise<void>;
  refreshAuth: () => Promise<AuthResponse>;
  updateUser: (user: User) => void;
  clearError: () => void;
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

const initialState: AuthState = {
  user: null,
  isAuthenticated: false,
  isLoading: true,
  error: null,
  accessToken: null,
  refreshToken: null,
};

function authReducer(state: AuthState, action: AuthAction): AuthState {
  switch (action.type) {
    case 'AUTH_START':
      return {
        ...state,
        isLoading: true,
        error: null,
      };
    case 'AUTH_SUCCESS':
      return {
        ...state,
        user: action.payload.user,
        isAuthenticated: true,
        isLoading: false,
        error: null,
        accessToken: action.payload.access_token,
        refreshToken: action.payload.refresh_token,
      };
    case 'AUTH_ERROR':
      return {
        ...state,
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: action.payload,
        accessToken: null,
        refreshToken: null,
      };
    case 'LOGOUT':
      return {
        ...state,
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: null,
        accessToken: null,
        refreshToken: null,
      };
    case 'CLEAR_ERROR':
      return {
        ...state,
        error: null,
      };
    case 'UPDATE_USER':
      return {
        ...state,
        user: action.payload,
      };
    case 'SET_LOADING':
      return {
        ...state,
        isLoading: action.payload,
      };
    default:
      return state;
  }
}


export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(authReducer, initialState);

  // Initialize auth state on mount
  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem('accessToken');
      const refreshToken = localStorage.getItem('refreshToken');

      if (token && refreshToken) {
        try {
          // Verify token and get user data
          const response = await authApi.me(token);
          dispatch({
            type: 'AUTH_SUCCESS',
            payload: {
              user: response.data!,
              access_token: token,
              refresh_token: refreshToken,
              expires_in: 3600, // Will be updated on refresh
            },
          });
        } catch {
          // Token might be expired, try to refresh
          try {
            await refreshAuth();
          } catch {
            // Both tokens invalid, clear auth
            localStorage.removeItem('accessToken');
            localStorage.removeItem('refreshToken');
            dispatch({ type: 'LOGOUT' });
          }
        }
      } else {
        dispatch({ type: 'SET_LOADING', payload: false });
      }
    };

    initAuth();
  }, []);

  const login = async (credentials: LoginCredentials) => {
    dispatch({ type: 'AUTH_START' });
    try {
      const response = await authApi.login(credentials);
      
      // Store tokens
      localStorage.setItem('accessToken', response.data!.access_token);
      localStorage.setItem('refreshToken', response.data!.refresh_token);
      
      dispatch({ type: 'AUTH_SUCCESS', payload: response.data! });
    } catch (error: unknown) {
      const errorMessage = (error as { response?: { data?: { message?: string } } })?.response?.data?.message || 'Login failed';
      dispatch({ type: 'AUTH_ERROR', payload: errorMessage });
      throw error;
    }
  };

  const register = async (data: RegisterData) => {
    dispatch({ type: 'AUTH_START' });
    try {
      const response = await authApi.register(data);
      
      // Store tokens
      localStorage.setItem('accessToken', response.data!.access_token);
      localStorage.setItem('refreshToken', response.data!.refresh_token);
      
      dispatch({ type: 'AUTH_SUCCESS', payload: response.data! });
    } catch (error: unknown) {
      const errorMessage = (error as { response?: { data?: { message?: string } } })?.response?.data?.message || 'Registration failed';
      dispatch({ type: 'AUTH_ERROR', payload: errorMessage });
      throw error;
    }
  };

  const verifyTwoFactor = async (code: string) => {
    dispatch({ type: 'AUTH_START' });
    try {
      const response = await authApi.verifyTwoFactor({ code });
      
      // Store tokens
      localStorage.setItem('accessToken', response.data!.access_token);
      localStorage.setItem('refreshToken', response.data!.refresh_token);
      
      dispatch({ type: 'AUTH_SUCCESS', payload: response.data! });
    } catch (error: unknown) {
      const errorMessage = (error as { response?: { data?: { message?: string } } })?.response?.data?.message || '2FA verification failed';
      dispatch({ type: 'AUTH_ERROR', payload: errorMessage });
      throw error;
    }
  };

  const refreshAuth = async () => {
    const refreshToken = localStorage.getItem('refreshToken');
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    try {
      const response = await authApi.refreshToken(refreshToken);
      
      // Store new tokens
      localStorage.setItem('accessToken', response.data!.access_token);
      if (response.data!.refresh_token) {
        localStorage.setItem('refreshToken', response.data!.refresh_token);
      }
      
      dispatch({ type: 'AUTH_SUCCESS', payload: response.data! });
      return response.data!;
    } catch (error) {
      // Refresh failed, clear auth
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
      dispatch({ type: 'LOGOUT' });
      throw error;
    }
  };

  const logout = () => {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    
    // Call logout API if token exists
    if (state.accessToken) {
      authApi.logout(state.accessToken).catch(() => {
        // Ignore errors on logout
      });
    }
    
    dispatch({ type: 'LOGOUT' });
  };

  const updateUser = (user: User) => {
    dispatch({ type: 'UPDATE_USER', payload: user });
  };

  const clearError = () => {
    dispatch({ type: 'CLEAR_ERROR' });
  };

  const value: AuthContextType = {
    ...state,
    login,
    register,
    logout,
    verifyTwoFactor,
    refreshAuth,
    updateUser,
    clearError,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}