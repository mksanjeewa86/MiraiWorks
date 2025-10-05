/**
 * Features API Client
 * Handles feature catalog and plan-feature management API calls
 */

import { apiClient } from './apiClient';
import { API_ENDPOINTS } from './config';
import type {
  Feature,
  FeatureCreate,
  FeatureNode,
  FeatureUpdate,
  PlanFeature,
  PlanFeatureAdd,
  SubscriptionApiResponse,
} from '@/types/subscription';

/**
 * Feature Catalog API
 */
export const featureCatalogApi = {
  /**
   * Get all features in hierarchical tree structure
   */
  async getHierarchical(): Promise<SubscriptionApiResponse<FeatureNode[]>> {
    try {
      const response = await apiClient.get<FeatureNode[]>(API_ENDPOINTS.FEATURES.HIERARCHICAL);
      return { data: response.data, success: true };
    } catch (error: any) {
      return { success: false, error: error.response?.data?.detail || 'Failed to fetch features' };
    }
  },

  /**
   * Get all features in flat list
   */
  async getFlat(skip = 0, limit = 100): Promise<SubscriptionApiResponse<Feature[]>> {
    try {
      const queryParams = new URLSearchParams();
      queryParams.append('skip', skip.toString());
      queryParams.append('limit', limit.toString());
      const url = `${API_ENDPOINTS.FEATURES.FLAT}?${queryParams.toString()}`;

      const response = await apiClient.get<Feature[]>(url);
      return { data: response.data, success: true };
    } catch (error: any) {
      return { success: false, error: error.response?.data?.detail || 'Failed to fetch features' };
    }
  },

  /**
   * Get a specific feature with its children
   */
  async getById(featureId: number): Promise<SubscriptionApiResponse<FeatureNode>> {
    try {
      const response = await apiClient.get<FeatureNode>(API_ENDPOINTS.FEATURES.BY_ID(featureId));
      return { data: response.data, success: true };
    } catch (error: any) {
      return { success: false, error: error.response?.data?.detail || 'Failed to fetch feature' };
    }
  },

  /**
   * Create a new feature (System Admin)
   */
  async create(data: FeatureCreate): Promise<SubscriptionApiResponse<Feature>> {
    try {
      const response = await apiClient.post<Feature>(API_ENDPOINTS.FEATURES.BASE, data);
      return { data: response.data, success: true };
    } catch (error: any) {
      return { success: false, error: error.response?.data?.detail || 'Failed to create feature' };
    }
  },

  /**
   * Update a feature (System Admin)
   */
  async update(featureId: number, data: FeatureUpdate): Promise<SubscriptionApiResponse<Feature>> {
    try {
      const response = await apiClient.put<Feature>(API_ENDPOINTS.FEATURES.BY_ID(featureId), data);
      return { data: response.data, success: true };
    } catch (error: any) {
      return { success: false, error: error.response?.data?.detail || 'Failed to update feature' };
    }
  },

  /**
   * Delete a feature (System Admin)
   */
  async delete(featureId: number): Promise<SubscriptionApiResponse<void>> {
    try {
      await apiClient.delete(API_ENDPOINTS.FEATURES.BY_ID(featureId));
      return { success: true };
    } catch (error: any) {
      return { success: false, error: error.response?.data?.detail || 'Failed to delete feature' };
    }
  },

  /**
   * Search features by name or display name
   */
  async search(searchTerm: string): Promise<SubscriptionApiResponse<Feature[]>> {
    try {
      const response = await apiClient.get<Feature[]>(API_ENDPOINTS.FEATURES.SEARCH(searchTerm));
      return { data: response.data, success: true };
    } catch (error: any) {
      return { success: false, error: error.response?.data?.detail || 'Failed to search features' };
    }
  },
};

/**
 * Plan-Feature Management API
 */
export const planFeatureApi = {
  /**
   * Get all features for a specific plan in hierarchical structure
   */
  async getPlanFeatures(planId: number): Promise<SubscriptionApiResponse<FeatureNode[]>> {
    try {
      const response = await apiClient.get<FeatureNode[]>(API_ENDPOINTS.FEATURES.PLAN_FEATURES(planId));
      return { data: response.data, success: true };
    } catch (error: any) {
      return { success: false, error: error.response?.data?.detail || 'Failed to fetch plan features' };
    }
  },

  /**
   * Add a feature to a plan (System Admin)
   */
  async addFeatureToPlan(planId: number, featureId: number): Promise<SubscriptionApiResponse<PlanFeature>> {
    try {
      const data: PlanFeatureAdd = { feature_id: featureId };
      const response = await apiClient.post<PlanFeature>(API_ENDPOINTS.FEATURES.ADD_TO_PLAN(planId), data);
      return { data: response.data, success: true };
    } catch (error: any) {
      return { success: false, error: error.response?.data?.detail || 'Failed to add feature to plan' };
    }
  },

  /**
   * Remove a feature from a plan (System Admin)
   */
  async removeFeatureFromPlan(planId: number, featureId: number): Promise<SubscriptionApiResponse<void>> {
    try {
      await apiClient.delete(API_ENDPOINTS.FEATURES.REMOVE_FROM_PLAN(planId, featureId));
      return { success: true };
    } catch (error: any) {
      return { success: false, error: error.response?.data?.detail || 'Failed to remove feature from plan' };
    }
  },
};

/**
 * Convenience export for all feature APIs
 */
export const featuresApi = {
  catalog: featureCatalogApi,
  planFeatures: planFeatureApi,
};

export default featuresApi;
