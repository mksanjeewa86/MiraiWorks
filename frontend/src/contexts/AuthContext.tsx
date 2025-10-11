'use client';

import { createContext, useContext, useReducer, useEffect, type ReactNode } from 'react';
import type {
  User,
  LoginCredentials,
  RegisterData,
  AuthState,
  AuthAction,
  AuthContextType,
} from '@/types';
import { authApi } from '@/api/auth';
import { setAuthHandler } from '@/api/apiClient';
import { toast } from 'sonner';
import { ROUTES } from '@/routes/config';
import { useLocaleRouter } from '@/hooks/useLocaleRouter';

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

const initialState: AuthState = {
  user: null,
  isAuthenticated: false,
  isLoading: true, // Set to true initially to prevent redirects while checking auth state
  error: null,
  accessToken: null,
  refreshToken: null,
  require2FA: false,
  pendingUserId: null,
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
        user: action.payload.user || null,
        isAuthenticated: true,
        isLoading: false,
        error: null,
        accessToken: action.payload.access_token,
        refreshToken: action.payload.refresh_token,
        require2FA: false,
        pendingUserId: null,
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
        require2FA: false,
        pendingUserId: null,
      };
    case 'REQUIRE_2FA':
      return {
        ...state,
        isLoading: false,
        error: null,
        require2FA: true,
        pendingUserId: action.payload.userId,
        isAuthenticated: false,
        user: null,
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
    case 'AUTH_IDLE':
      return {
        ...state,
        isLoading: false,
        error: null,
        isAuthenticated: false,
        user: null,
        accessToken: null,
        refreshToken: null,
      };
    default:
      return state;
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(authReducer, initialState);
  const router = useLocaleRouter();

  // Force logout without API call (used by API interceptor)
  const forceLogout = () => {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    dispatch({ type: 'LOGOUT' });

    // Redirect to login page using Next.js router
    if (typeof window !== 'undefined') {
      router.replace(ROUTES.AUTH.LOGIN);
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

      // If user data is not included in refresh response, fetch it separately
      let userData = response.data!.user;
      if (!userData) {
        const userResponse = await authApi.me(response.data!.access_token);
        userData = userResponse.data!;
      }

      dispatch({
        type: 'AUTH_SUCCESS',
        payload: {
          ...response.data!,
          user: userData,
        },
      });
      return response.data!;
    } catch (error: any) {
      // Check if this is a 401 error
      const is401 = error?.response?.status === 401;

      // Only logout and show message if it's truly a session expiration (401)
      if (is401) {
        // Refresh failed, clear auth
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        dispatch({ type: 'LOGOUT' });

        // Show user-friendly message
        toast.error('Your session has expired. Please log in again.', {
          duration: 5000,
        });

        // Redirect to login page
        if (typeof window !== 'undefined') {
          router.replace(ROUTES.AUTH.LOGIN_EXPIRED);
        }
      } else {
        // Network or other error - don't logout, just log the error
        console.error('Token refresh failed (non-auth error):', error);
      }

      throw error;
    }
  };

  // Register auth handlers for API client
  useEffect(() => {
    setAuthHandler({
      logout: forceLogout,
      refreshAuth: refreshAuth,
    });
  }, []);

  // Initialize auth state on mount
  useEffect(() => {
    let isMounted = true;
    let isInitializing = false;

    const initAuth = async () => {
      // Prevent multiple simultaneous initializations
      if (isInitializing || !isMounted) return;
      isInitializing = true;

      try {
        // Set loading to true when starting authentication check
        if (isMounted) {
          dispatch({ type: 'SET_LOADING', payload: true });
        }

        const token = localStorage.getItem('accessToken');
        const refreshToken = localStorage.getItem('refreshToken');

        if (token && refreshToken) {
          // Try to verify current token first by calling /me endpoint
          try {
            const userResponse = await authApi.me(token);

            // Token is valid, set auth state without refreshing
            if (isMounted) {
              dispatch({
                type: 'AUTH_SUCCESS',
                payload: {
                  user: userResponse.data!,
                  access_token: token,
                  refresh_token: refreshToken,
                  expires_in: 3600, // Default 1 hour for existing tokens
                },
              });
            }
          } catch (verifyError) {
            if (!isMounted) return;

            // Current token invalid, try refresh
            try {
              await refreshAuth();
              if (isMounted) {
                // refreshAuth already dispatches AUTH_SUCCESS which sets isLoading to false
              }
            } catch (refreshError) {
              if (!isMounted) return;

              // Both tokens invalid, clear auth completely
              localStorage.removeItem('accessToken');
              localStorage.removeItem('refreshToken');
              dispatch({ type: 'LOGOUT' });
            }
          }
        } else {
          // No tokens found, ensure clean state
          if (isMounted) {
            dispatch({ type: 'LOGOUT' });
          }
        }
      } catch (error) {
        if (!isMounted) return;

        // Any unexpected error, clear auth
        console.error('Auth initialization error:', error);
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        dispatch({ type: 'LOGOUT' });
      } finally {
        isInitializing = false;
      }
    };

    // Initialize immediately
    initAuth();

    // Cleanup function
    return () => {
      isMounted = false;
    };
  }, []);

  const login = async (credentials: LoginCredentials) => {
    dispatch({ type: 'AUTH_START' });
    try {
      const response = await authApi.login(credentials);

      // Check if 2FA is required
      if (response.data!.require_2fa && response.data!.user) {
        dispatch({
          type: 'REQUIRE_2FA',
          payload: {
            userId: response.data!.user.id,
            email: response.data!.user.email,
          },
        });
        // Redirect will be handled by the component using this context
        return;
      }

      // Store tokens for successful login
      localStorage.setItem('accessToken', response.data!.access_token);
      localStorage.setItem('refreshToken', response.data!.refresh_token);

      dispatch({ type: 'AUTH_SUCCESS', payload: response.data! });
    } catch (error: unknown) {
      const errorMessage =
        (error as { response?: { data?: { message?: string } } })?.response?.data?.message ||
        'Login failed';
      dispatch({ type: 'AUTH_ERROR', payload: errorMessage });
      throw error;
    }
  };

  const register = async (data: RegisterData) => {
    dispatch({ type: 'AUTH_START' });
    try {
      const response = await authApi.register(data);

      // Only store tokens if they exist (backward compatibility)
      // New flow: No tokens returned, user must activate account first
      if (response.data?.access_token && response.data?.refresh_token) {
        localStorage.setItem('accessToken', response.data.access_token);
        localStorage.setItem('refreshToken', response.data.refresh_token);
        dispatch({ type: 'AUTH_SUCCESS', payload: response.data });
      } else {
        // Registration successful but no auto-login (account inactive)
        dispatch({ type: 'AUTH_IDLE' });
      }
    } catch (error: unknown) {
      let errorMessage = 'Registration failed';

      // Handle different error response formats
      if (error && typeof error === 'object') {
        const err = error as {
          response?: { data?: { detail?: string; message?: string } };
          message?: string;
        };
        if (err.response?.data?.detail) {
          errorMessage = err.response.data.detail;
        } else if (err.response?.data?.message) {
          errorMessage = err.response.data.message;
        } else if (err.message) {
          errorMessage = err.message;
        }
      }

      dispatch({ type: 'AUTH_ERROR', payload: errorMessage });
      throw error;
    }
  };

  const verifyTwoFactor = async (code: string) => {
    dispatch({ type: 'AUTH_START' });
    try {
      if (!state.pendingUserId) {
        throw new Error('No pending 2FA verification');
      }

      const response = await authApi.verifyTwoFactor({
        user_id: state.pendingUserId,
        code,
      });

      // Store tokens
      localStorage.setItem('accessToken', response.data!.access_token);
      localStorage.setItem('refreshToken', response.data!.refresh_token);

      dispatch({ type: 'AUTH_SUCCESS', payload: response.data! });
    } catch (error: unknown) {
      const errorMessage =
        (error as { response?: { data?: { message?: string } } })?.response?.data?.message ||
        '2FA verification failed';
      dispatch({ type: 'AUTH_ERROR', payload: errorMessage });
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

    // Redirect to login page after logout using Next.js router
    if (typeof window !== 'undefined') {
      router.replace(ROUTES.AUTH.LOGIN);
    }
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

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
