import { API_ENDPOINTS, API_CONFIG } from './config';
import { publicApiClient } from './apiClient';
import type { ApiResponse, AuthResponse, LoginCredentials, RegisterData, User } from '@/types';

export const authApi = {
  async login(credentials: LoginCredentials): Promise<ApiResponse<AuthResponse>> {
    const response = await publicApiClient.post<AuthResponse>(
      API_ENDPOINTS.AUTH.LOGIN,
      credentials
    );
    return { data: response.data, success: true };
  },

  async register(registerData: RegisterData): Promise<ApiResponse<AuthResponse>> {
    const response = await publicApiClient.post<AuthResponse>(
      API_ENDPOINTS.AUTH.REGISTER,
      registerData
    );
    return { data: response.data, success: true };
  },

  async me(token: string): Promise<ApiResponse<User>> {
    // For this method we need to pass token manually since it's called before auth context is set up
    const response = await fetch(`${API_CONFIG.BASE_URL}${API_ENDPOINTS.AUTH.ME}`, {
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return { data, success: true };
  },

  async refreshToken(refreshToken: string): Promise<ApiResponse<AuthResponse>> {
    const response = await publicApiClient.post<AuthResponse>(API_ENDPOINTS.AUTH.REFRESH, {
      refresh_token: refreshToken,
    });
    return { data: response.data, success: true };
  },

  async verifyTwoFactor(data: {
    user_id: number;
    code: string;
  }): Promise<ApiResponse<AuthResponse>> {
    const response = await publicApiClient.post<AuthResponse>(API_ENDPOINTS.AUTH.VERIFY_2FA, data);
    return { data: response.data, success: true };
  },

  async logout(token: string): Promise<void> {
    try {
      // Use manual fetch since logout should work even if auth fails
      const response = await fetch(`${API_CONFIG.BASE_URL}${API_ENDPOINTS.AUTH.LOGOUT}`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      // If token is expired (401), that's fine - we still want to logout locally
      if (!response.ok && response.status !== 401) {
        console.warn('Logout API returned non-401 error:', response.status);
      }
    } catch (error) {
      // Don't throw error for logout - just clear local storage regardless
      console.warn('Logout API failed, but continuing with local cleanup', error);
    }
  },

  async forgotPassword(email: string): Promise<void> {
    await publicApiClient.post<void>(API_ENDPOINTS.AUTH.FORGOT_PASSWORD, { email });
  },

  async resetPassword(token: string, password: string): Promise<void> {
    await publicApiClient.post<void>(API_ENDPOINTS.AUTH.RESET_PASSWORD, { token, password });
  },
};
