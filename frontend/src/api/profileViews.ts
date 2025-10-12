/**
 * Profile Views API
 *
 * API functions for tracking and retrieving profile view analytics.
 */

import { apiClient } from './apiClient';
import { API_ENDPOINTS } from './config';
import type { ApiResponse } from '@/types';

/**
 * Profile view data when recording a view
 */
export interface ProfileViewCreate {
  profile_user_id: number;
  view_duration?: number;
  referrer?: string;
}

/**
 * Profile view information
 */
export interface ProfileViewInfo {
  id: number;
  profile_user_id: number;
  viewer_user_id: number | null;
  viewer_company_id: number | null;
  viewer_ip: string | null;
  viewer_user_agent: string | null;
  view_duration: number | null;
  referrer: string | null;
  created_at: string;
}

/**
 * Company view count
 */
export interface CompanyViewCount {
  company_id: number;
  company_name: string;
  view_count: number;
}

/**
 * Views over time data point
 */
export interface ViewOverTime {
  date: string;
  count: number;
}

/**
 * Profile view statistics
 */
export interface ProfileViewStats {
  total_views: number;
  unique_viewers: number;
  views_by_company: CompanyViewCount[];
  views_over_time: ViewOverTime[];
}

/**
 * Recent viewer information
 */
export interface RecentViewer {
  viewer_user_id: number;
  first_name: string;
  last_name: string;
  email: string;
  company_id: number | null;
  company_name: string | null;
  last_viewed: string;
  view_count: number;
}

/**
 * Profile views API client
 */
export const profileViewsApi = {
  /**
   * Record a profile view
   */
  async recordView(data: ProfileViewCreate): Promise<ApiResponse<ProfileViewInfo>> {
    try {
      const response = await apiClient.post<ProfileViewInfo>(
        API_ENDPOINTS.PROFILE_VIEWS.RECORD,
        data
      );
      return {
        data: response.data,
        success: true,
      };
    } catch (error: any) {
      console.error('Error recording profile view:', error);
      return {
        success: false,
        message: error.response?.data?.detail || 'Failed to record profile view',
      };
    }
  },

  /**
   * Get all profile views for the current user
   */
  async getMyViews(params?: {
    skip?: number;
    limit?: number;
    include_anonymous?: boolean;
  }): Promise<ApiResponse<ProfileViewInfo[]>> {
    try {
      let url = API_ENDPOINTS.PROFILE_VIEWS.MY_VIEWS;
      if (params) {
        const searchParams = new URLSearchParams();
        if (params.skip !== undefined) searchParams.append('skip', params.skip.toString());
        if (params.limit !== undefined) searchParams.append('limit', params.limit.toString());
        if (params.include_anonymous !== undefined) searchParams.append('include_anonymous', params.include_anonymous.toString());
        const queryString = searchParams.toString();
        if (queryString) url += `?${queryString}`;
      }
      const response = await apiClient.get<ProfileViewInfo[]>(url);
      return {
        data: response.data,
        success: true,
      };
    } catch (error: any) {
      console.error('Error fetching profile views:', error);
      return {
        success: false,
        message: error.response?.data?.detail || 'Failed to fetch profile views',
      };
    }
  },

  /**
   * Get profile view statistics
   */
  async getStats(days?: number): Promise<ApiResponse<ProfileViewStats>> {
    try {
      let url = API_ENDPOINTS.PROFILE_VIEWS.STATS;
      if (days !== undefined) {
        url += `?days=${days}`;
      }
      const response = await apiClient.get<ProfileViewStats>(url);
      return {
        data: response.data,
        success: true,
      };
    } catch (error: any) {
      console.error('Error fetching profile view stats:', error);
      return {
        success: false,
        message: error.response?.data?.detail || 'Failed to fetch profile view stats',
      };
    }
  },

  /**
   * Get recent profile viewers
   */
  async getRecentViewers(params?: {
    limit?: number;
    days?: number;
  }): Promise<ApiResponse<RecentViewer[]>> {
    try {
      let url = API_ENDPOINTS.PROFILE_VIEWS.RECENT_VIEWERS;
      if (params) {
        const searchParams = new URLSearchParams();
        if (params.limit !== undefined) searchParams.append('limit', params.limit.toString());
        if (params.days !== undefined) searchParams.append('days', params.days.toString());
        const queryString = searchParams.toString();
        if (queryString) url += `?${queryString}`;
      }
      const response = await apiClient.get<RecentViewer[]>(url);
      return {
        data: response.data,
        success: true,
      };
    } catch (error: any) {
      console.error('Error fetching recent viewers:', error);
      return {
        success: false,
        message: error.response?.data?.detail || 'Failed to fetch recent viewers',
      };
    }
  },

  /**
   * Get profile view count
   */
  async getViewCount(days?: number): Promise<ApiResponse<{ count: number }>> {
    try {
      let url = API_ENDPOINTS.PROFILE_VIEWS.COUNT;
      if (days !== undefined) {
        url += `?days=${days}`;
      }
      const response = await apiClient.get<{ count: number }>(url);
      return {
        data: response.data,
        success: true,
      };
    } catch (error: any) {
      console.error('Error fetching profile view count:', error);
      return {
        success: false,
        message: error.response?.data?.detail || 'Failed to fetch profile view count',
      };
    }
  },
};
