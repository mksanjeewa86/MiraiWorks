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
    // Clear tokens from both storage types
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('rememberMe');
    localStorage.removeItem('tokenVersion');
    sessionStorage.removeItem('accessToken');
    sessionStorage.removeItem('refreshToken');
    sessionStorage.removeItem('rememberMe');
    sessionStorage.removeItem('tokenVersion');
    dispatch({ type: 'LOGOUT' });

    // Redirect to login page using Next.js router
    if (typeof window !== 'undefined') {
      router.replace(ROUTES.AUTH.LOGIN);
    }
  };

  const refreshAuth = async (silent: boolean = false) => {
    // Check both storage types for refresh token
    const refreshToken = localStorage.getItem('refreshToken') || sessionStorage.getItem('refreshToken');
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    // Determine which storage to use based on where we found the refresh token
    const useLocalStorage = !!localStorage.getItem('refreshToken');
    const storage = useLocalStorage ? localStorage : sessionStorage;

    try {
      const response = await authApi.refreshToken(refreshToken);

      // Store new tokens in the same storage type
      storage.setItem('accessToken', response.data!.access_token);
      if (response.data!.refresh_token) {
        storage.setItem('refreshToken', response.data!.refresh_token);
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

      // If 401, clear all tokens and force logout (token is invalid)
      if (is401) {
        // Clear all storage
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        localStorage.removeItem('rememberMe');
        localStorage.removeItem('tokenVersion');
        sessionStorage.removeItem('accessToken');
        sessionStorage.removeItem('refreshToken');
        sessionStorage.removeItem('rememberMe');
        sessionStorage.removeItem('tokenVersion');

        // Dispatch logout
        dispatch({ type: 'LOGOUT' });

        // Only show toast and redirect if not in silent mode
        if (!silent) {
          toast.error('Your session has expired. Please log in again.', {
            duration: 5000,
          });

          // Redirect to login page
          if (typeof window !== 'undefined') {
            router.replace(ROUTES.AUTH.LOGIN);
          }
        }
      } else {
        // Network or other error - just log it
        if (!silent) {
          console.error('[AuthContext] Token refresh failed (non-auth error):', error);
        }
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

        // TOKEN VERSION CHECK: Clear old tokens from before remember_me migration
        // Migration date: 2025-10-17
        const tokenVersion = localStorage.getItem('tokenVersion') || sessionStorage.getItem('tokenVersion');
        const CURRENT_TOKEN_VERSION = '2.0'; // Updated for remember_me feature

        if (!tokenVersion || tokenVersion !== CURRENT_TOKEN_VERSION) {
          localStorage.removeItem('accessToken');
          localStorage.removeItem('refreshToken');
          localStorage.removeItem('rememberMe');
          sessionStorage.removeItem('accessToken');
          sessionStorage.removeItem('refreshToken');
          sessionStorage.removeItem('rememberMe');

          if (isMounted) {
            dispatch({ type: 'LOGOUT' });
          }
          return;
        }

        // Check both localStorage and sessionStorage for tokens
        const token = localStorage.getItem('accessToken') || sessionStorage.getItem('accessToken');
        const refreshToken = localStorage.getItem('refreshToken') || sessionStorage.getItem('refreshToken');

        if (token && refreshToken) {
          // Skip token validation, just try to use the access token
          // If it fails, the API client will handle token refresh automatically
          try {
            const userResponse = await authApi.me(token);

            // Token is valid, set auth state
            if (isMounted) {
              dispatch({
                type: 'AUTH_SUCCESS',
                payload: {
                  user: userResponse.data!,
                  access_token: token,
                  refresh_token: refreshToken,
                  expires_in: 3600,
                },
              });
            }
          } catch (verifyError) {
            // Access token invalid, clear everything and require re-login
            console.warn('[AuthContext] Access token invalid, clearing storage');
            localStorage.removeItem('accessToken');
            localStorage.removeItem('refreshToken');
            localStorage.removeItem('rememberMe');
            localStorage.removeItem('tokenVersion');
            sessionStorage.removeItem('accessToken');
            sessionStorage.removeItem('refreshToken');
            sessionStorage.removeItem('rememberMe');
            sessionStorage.removeItem('tokenVersion');

            if (isMounted) {
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
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        localStorage.removeItem('rememberMe');
        localStorage.removeItem('tokenVersion');
        sessionStorage.removeItem('accessToken');
        sessionStorage.removeItem('refreshToken');
        sessionStorage.removeItem('rememberMe');
        sessionStorage.removeItem('tokenVersion');
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

      // Store tokens based on rememberMe preference
      // If rememberMe is true, use localStorage (persists across sessions)
      // If rememberMe is false, use sessionStorage (cleared when browser closes)
      const storage = credentials.rememberMe ? localStorage : sessionStorage;
      storage.setItem('accessToken', response.data!.access_token);
      storage.setItem('refreshToken', response.data!.refresh_token);
      storage.setItem('tokenVersion', '2.0'); // Set token version for future validation

      // Also store the rememberMe preference itself
      if (credentials.rememberMe) {
        localStorage.setItem('rememberMe', 'true');
      } else {
        sessionStorage.setItem('rememberMe', 'false');
        // Clear any existing localStorage tokens
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        localStorage.removeItem('rememberMe');
        localStorage.removeItem('tokenVersion');
      }

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
    // Get refresh token before clearing storage (check both storage types)
    const refreshToken = state.refreshToken || localStorage.getItem('refreshToken') || sessionStorage.getItem('refreshToken');

    // Clear both storage types
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('rememberMe');
    localStorage.removeItem('tokenVersion');
    sessionStorage.removeItem('accessToken');
    sessionStorage.removeItem('refreshToken');
    sessionStorage.removeItem('rememberMe');
    sessionStorage.removeItem('tokenVersion');

    // Dispatch logout to clear auth state
    dispatch({ type: 'LOGOUT' });

    // Try to call logout API silently (don't wait for it)
    // This will invalidate the refresh token on the backend if it's still valid
    if (refreshToken) {
      authApi.logout(refreshToken).catch(() => {
        // Silently ignore - logout is already complete on frontend
      });
    }

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
