// Centralized API client with automatic authentication handling
import { API_CONFIG } from './config';
import { apiRateLimiter, checkRateLimit } from '@/utils/rateLimiter';

// Global auth handler reference
let authHandlerRef: {
  logout?: () => void;
  refreshAuth?: (silent?: boolean) => Promise<unknown>;
} = {};

// Set auth handler (called from AuthContext)
export const setAuthHandler = (handler: typeof authHandlerRef) => {
  authHandlerRef = handler;
};

// Helper function to get auth token
const getAuthToken = (): string | null => {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('accessToken');
  }
  return null;
};

// Enhanced request handler with automatic auth error handling
export const makeAuthenticatedRequest = async <T>(
  url: string,
  options: RequestInit = {},
  silent: boolean = false
): Promise<{ data: T }> => {
  // Check rate limit before making request
  checkRateLimit(apiRateLimiter, url);

  const token = getAuthToken();

  const makeRequest = async (authToken: string | null) => {
    const isFormData = options.body instanceof FormData;

    // Create abort controller for timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), API_CONFIG.TIMEOUT);

    try {
      const response = await fetch(`${API_CONFIG.BASE_URL}${url}`, {
        ...options,
        signal: controller.signal,
        credentials: 'include', // Required for CORS with credentials
        headers: {
          // Don't set Content-Type for FormData (browser will set it with boundary)
          ...(isFormData ? {} : { 'Content-Type': 'application/json' }),
          ...(authToken && { Authorization: `Bearer ${authToken}` }),
          ...options.headers,
        },
      });

      clearTimeout(timeoutId);
      return response;
    } catch (error) {
      clearTimeout(timeoutId);
      if ((error as Error).name === 'AbortError') {
        throw new Error('Request timeout. Please try again.');
      }
      throw error;
    }
  };

  try {
    let response = await makeRequest(token);

    // Handle 401 Unauthorized - token expired or invalid
    if (response.status === 401) {
      // Try to refresh the token once
      if (authHandlerRef.refreshAuth) {
        try {
          await authHandlerRef.refreshAuth(silent);
          const newToken = getAuthToken();

          // Retry the request with new token
          response = await makeRequest(newToken);
        } catch (refreshError) {
          // Refresh failed - don't logout, just throw error
          // This allows the user to stay logged in even if refresh fails
          // They'll only be truly logged out when they manually logout or their session fully expires
          if (!silent) {
            console.warn('Token refresh failed, but keeping user session:', refreshError);
          }
          throw new Error('Session refresh failed. Some features may be unavailable.');
        }
      } else {
        // No refresh handler available - throw error without logout
        if (!silent) {
          console.error('No refresh handler available');
        }
        throw new Error('Authentication failed. Please try refreshing the page.');
      }
    }

    // Handle other HTTP errors
    if (!response.ok) {
      let errorMessage = `API request failed: ${response.status} ${response.statusText}`;

      try {
        const errorData = await response.json();
        if (errorData.message) {
          errorMessage =
            typeof errorData.message === 'string'
              ? errorData.message
              : JSON.stringify(errorData.message);
        } else if (errorData.detail) {
          // Handle both string and array/object details
          if (typeof errorData.detail === 'string') {
            errorMessage = errorData.detail;
          } else if (Array.isArray(errorData.detail)) {
            // Handle validation errors array
            errorMessage = errorData.detail
              .map((error: unknown) =>
                typeof error === 'string'
                  ? error
                  : (error as { msg?: string }).msg || JSON.stringify(error)
              )
              .join(', ');
          } else {
            errorMessage = JSON.stringify(errorData.detail);
          }
        } else {
          // Fallback to stringify the entire error object
          errorMessage = JSON.stringify(errorData);
        }
      } catch {
        // Use default error message if parsing fails
      }

      throw new Error(errorMessage);
    }

    // Handle 204 No Content responses (no body to parse)
    if (response.status === 204) {
      return { data: null as T };
    }

    const data = await response.json();
    return { data };
  } catch (error) {
    // If it's a fetch error (network issue), handle it gracefully
    if (error instanceof TypeError && error.message.includes('fetch')) {
      throw new Error('Network error. Please check your connection and try again.');
    }

    // Re-throw other errors
    throw error;
  }
};

// Simple request handler for non-authenticated requests
export const makePublicRequest = async <T>(
  url: string,
  options: RequestInit = {}
): Promise<{ data: T }> => {
  const response = await fetch(`${API_CONFIG.BASE_URL}${url}`, {
    ...options,
    credentials: 'include', // Required for CORS with credentials
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  if (!response.ok) {
    let errorMessage = `API request failed: ${response.status} ${response.statusText}`;

    try {
      const errorData = await response.json();
      if (errorData.message) {
        errorMessage =
          typeof errorData.message === 'string'
            ? errorData.message
            : JSON.stringify(errorData.message);
      } else if (errorData.detail) {
        // Handle both string and array/object details
        if (typeof errorData.detail === 'string') {
          errorMessage = errorData.detail;
        } else if (Array.isArray(errorData.detail)) {
          // Handle validation errors array
          errorMessage = errorData.detail
            .map((error: unknown) =>
              typeof error === 'string'
                ? error
                : (error as { msg?: string }).msg || JSON.stringify(error)
            )
            .join(', ');
        } else {
          errorMessage = JSON.stringify(errorData.detail);
        }
      } else {
        // Fallback to stringify the entire error object
        errorMessage = JSON.stringify(errorData);
      }
    } catch {
      // Use default error message if parsing fails
    }

    throw new Error(errorMessage);
  }

  const data = await response.json();
  return { data };
};

// Standard HTTP methods
export const apiClient = {
  get: <T>(url: string, silent?: boolean) => makeAuthenticatedRequest<T>(url, { method: 'GET' }, silent),

  post: <T>(url: string, data?: unknown, config?: { headers?: Record<string, string>; silent?: boolean }) => {
    const isFormData = data instanceof FormData;
    const options: RequestInit = {
      method: 'POST',
      body: isFormData ? data : data ? JSON.stringify(data) : undefined,
      ...(config?.headers && { headers: config.headers }),
    };

    return makeAuthenticatedRequest<T>(url, options, config?.silent);
  },

  put: <T>(url: string, data?: unknown, silent?: boolean) =>
    makeAuthenticatedRequest<T>(url, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    }, silent),

  patch: <T>(url: string, data?: unknown, silent?: boolean) =>
    makeAuthenticatedRequest<T>(url, {
      method: 'PATCH',
      body: data ? JSON.stringify(data) : undefined,
    }, silent),

  delete: <T>(url: string, silent?: boolean) => makeAuthenticatedRequest<T>(url, { method: 'DELETE' }, silent),
};

// Public client for non-authenticated requests
export const publicApiClient = {
  get: <T>(url: string) => makePublicRequest<T>(url, { method: 'GET' }),

  post: <T>(url: string, data?: unknown) =>
    makePublicRequest<T>(url, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    }),
};
