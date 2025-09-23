// Centralized API client with automatic authentication handling
import { API_CONFIG } from './config';

// Global auth handler reference
let authHandlerRef: {
  logout?: () => void;
  refreshAuth?: () => Promise<unknown>;
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
  options: RequestInit = {}
): Promise<{ data: T }> => {
  const token = getAuthToken();
  
  const makeRequest = async (authToken: string | null) => {
    const isFormData = options.body instanceof FormData;
    const response = await fetch(`${API_CONFIG.BASE_URL}${url}`, {
      ...options,
      headers: {
        // Don't set Content-Type for FormData (browser will set it with boundary)
        ...(isFormData ? {} : { 'Content-Type': 'application/json' }),
        ...(authToken && { Authorization: `Bearer ${authToken}` }),
        ...options.headers,
      },
    });

    return response;
  };

  try {
    let response = await makeRequest(token);

    // Handle 401 Unauthorized - token expired or invalid
    if (response.status === 401) {
      // Try to refresh the token once
      if (authHandlerRef.refreshAuth) {
        try {
          await authHandlerRef.refreshAuth();
          const newToken = getAuthToken();
          
          // Retry the request with new token
          response = await makeRequest(newToken);
        } catch {
          // Refresh failed, force logout
          if (authHandlerRef.logout) {
            authHandlerRef.logout();
          }
          throw new Error('Authentication failed. Please log in again.');
        }
      } else {
        // No refresh handler available, force logout
        if (authHandlerRef.logout) {
          authHandlerRef.logout();
        }
        throw new Error('Authentication failed. Please log in again.');
      }
    }

    // Handle other HTTP errors
    if (!response.ok) {
      let errorMessage = `API request failed: ${response.status} ${response.statusText}`;

      try {
        const errorData = await response.json();
        if (errorData.message) {
          errorMessage = typeof errorData.message === 'string'
            ? errorData.message
            : JSON.stringify(errorData.message);
        } else if (errorData.detail) {
          // Handle both string and array/object details
          if (typeof errorData.detail === 'string') {
            errorMessage = errorData.detail;
          } else if (Array.isArray(errorData.detail)) {
            // Handle validation errors array
            errorMessage = errorData.detail.map((error: unknown) =>
              typeof error === 'string' ? error : (error as { msg?: string }).msg || JSON.stringify(error)
            ).join(', ');
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
        errorMessage = typeof errorData.message === 'string'
          ? errorData.message
          : JSON.stringify(errorData.message);
      } else if (errorData.detail) {
        // Handle both string and array/object details
        if (typeof errorData.detail === 'string') {
          errorMessage = errorData.detail;
        } else if (Array.isArray(errorData.detail)) {
          // Handle validation errors array
          errorMessage = errorData.detail.map((error: unknown) =>
            typeof error === 'string' ? error : (error as { msg?: string }).msg || JSON.stringify(error)
          ).join(', ');
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
  get: <T>(url: string) => makeAuthenticatedRequest<T>(url, { method: 'GET' }),

  post: <T>(url: string, data?: unknown, config?: { headers?: Record<string, string> }) => {
    const isFormData = data instanceof FormData;
    const options: RequestInit = {
      method: 'POST',
      body: isFormData ? data : (data ? JSON.stringify(data) : undefined),
      ...(config?.headers && { headers: config.headers })
    };

    return makeAuthenticatedRequest<T>(url, options);
  },

  put: <T>(url: string, data?: unknown) =>
    makeAuthenticatedRequest<T>(url, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined
    }),

  patch: <T>(url: string, data?: unknown) =>
    makeAuthenticatedRequest<T>(url, {
      method: 'PATCH',
      body: data ? JSON.stringify(data) : undefined
    }),

  delete: <T>(url: string) => makeAuthenticatedRequest<T>(url, { method: 'DELETE' }),
};

// Public client for non-authenticated requests
export const publicApiClient = {
  get: <T>(url: string) => makePublicRequest<T>(url, { method: 'GET' }),

  post: <T>(url: string, data?: unknown) =>
    makePublicRequest<T>(url, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined
    }),
};