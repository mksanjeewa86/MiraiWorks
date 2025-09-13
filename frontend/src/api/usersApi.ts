import {
  User,
  UserCreate,
  UserUpdate,
  UserListResponse,
  UserFilters,
  PasswordResetRequest
} from '../types/user';
import { API_CONFIG } from '@/config/api';

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
  
  const response = await fetch(`${API_CONFIG.BASE_URL}${url}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
      ...options.headers,
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(errorData.detail || `API request failed: ${response.status} ${response.statusText}`);
  }

  const data = await response.json();
  return { data };
};

export const usersApi = {
  // Get users with filters and pagination
  getUsers: (filters: UserFilters = {}) => {
    const params = new URLSearchParams();
    
    if (filters.page) params.append('page', filters.page.toString());
    if (filters.size) params.append('size', filters.size.toString());
    if (filters.search) params.append('search', filters.search);
    if (filters.company_id) params.append('company_id', filters.company_id.toString());
    if (filters.is_active !== undefined) params.append('is_active', filters.is_active.toString());
    if (filters.is_admin !== undefined) params.append('is_admin', filters.is_admin.toString());
    if (filters.role) params.append('role', filters.role);
    
    const queryString = params.toString();
    const url = `/api/admin/users${queryString ? `?${queryString}` : ''}`;
    
    return makeAuthenticatedRequest<UserListResponse>(url);
  },

  // Get single user by ID
  getUser: (userId: number) =>
    makeAuthenticatedRequest<User>(`/api/admin/users/${userId}`),

  // Create new user
  createUser: (userData: UserCreate) =>
    makeAuthenticatedRequest<User>('/api/admin/users', {
      method: 'POST',
      body: JSON.stringify(userData),
    }),

  // Update user
  updateUser: (userId: number, userData: UserUpdate) =>
    makeAuthenticatedRequest<User>(`/api/admin/users/${userId}`, {
      method: 'PUT',
      body: JSON.stringify(userData),
    }),

  // Delete user (soft delete)
  deleteUser: (userId: number) =>
    makeAuthenticatedRequest<{ message: string }>(`/api/admin/users/${userId}`, {
      method: 'DELETE',
    }),

  // Reset user password
  resetPassword: (userId: number) =>
    makeAuthenticatedRequest<PasswordResetRequest>(`/api/admin/users/${userId}/reset-password`, {
      method: 'POST',
    }),

  // Resend activation email
  resendActivation: (userId: number) =>
    makeAuthenticatedRequest<{ message: string }>(`/api/admin/users/${userId}/resend-activation`, {
      method: 'POST',
    }),

  // Toggle user status (suspend/activate)
  toggleStatus: (userId: number) =>
    makeAuthenticatedRequest<User>(`/api/admin/users/${userId}/toggle-status`, {
      method: 'POST',
    }),
};