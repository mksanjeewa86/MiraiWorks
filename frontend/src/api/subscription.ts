/**
 * Subscription API Client
 * Handles all subscription-related API calls
 */

import { apiClient } from './apiClient';
import { API_ENDPOINTS } from './config';
import type {
  CompanySubscription,
  CompanySubscriptionCreate,
  CompanySubscriptionUpdate,
  CompanySubscriptionWithFeatures,
  FeatureAccessCheck,
  PlanChangeRequest,
  PlanChangeRequestCreate,
  PlanChangeRequestReview,
  PlanChangeRequestWithDetails,
  SubscriptionApiResponse,
  SubscriptionPlan,
  SubscriptionPlanWithFeatures,
} from '@/types/subscription';

/**
 * Subscription Plan API
 */
export const subscriptionPlanApi = {
  /**
   * Get all public subscription plans
   */
  async getPublicPlans(): Promise<SubscriptionApiResponse<SubscriptionPlan[]>> {
    try {
      const response = await apiClient.get<SubscriptionPlan[]>(API_ENDPOINTS.SUBSCRIPTION_PLANS.PUBLIC);
      return { data: response.data, success: true };
    } catch (error: any) {
      return { success: false, error: error.response?.data?.detail || 'Failed to fetch plans' };
    }
  },

  /**
   * Get a specific plan with its features
   */
  async getPlanWithFeatures(planId: number): Promise<SubscriptionApiResponse<SubscriptionPlanWithFeatures>> {
    try {
      const response = await apiClient.get<SubscriptionPlanWithFeatures>(API_ENDPOINTS.SUBSCRIPTION_PLANS.WITH_FEATURES(planId));
      return { data: response.data, success: true };
    } catch (error: any) {
      return { success: false, error: error.response?.data?.detail || 'Failed to fetch plan' };
    }
  },
};

/**
 * Company Subscription API
 */
export const companySubscriptionApi = {
  /**
   * Get current company's subscription
   */
  async getMySubscription(): Promise<SubscriptionApiResponse<CompanySubscriptionWithFeatures>> {
    try {
      const response = await apiClient.get<CompanySubscriptionWithFeatures>(API_ENDPOINTS.SUBSCRIPTIONS.MY_SUBSCRIPTION);
      return { data: response.data, success: true };
    } catch (error: any) {
      return { success: false, error: error.response?.data?.detail || 'Failed to fetch subscription' };
    }
  },

  /**
   * Subscribe company to a plan (initial subscription)
   */
  async subscribe(data: CompanySubscriptionCreate): Promise<SubscriptionApiResponse<CompanySubscription>> {
    try {
      const response = await apiClient.post<CompanySubscription>(API_ENDPOINTS.SUBSCRIPTIONS.SUBSCRIBE, data);
      return { data: response.data, success: true };
    } catch (error: any) {
      return { success: false, error: error.response?.data?.detail || 'Failed to subscribe' };
    }
  },

  /**
   * Update subscription settings (billing cycle, auto-renew, etc.)
   */
  async updateSubscription(data: CompanySubscriptionUpdate): Promise<SubscriptionApiResponse<CompanySubscription>> {
    try {
      const response = await apiClient.put<CompanySubscription>(API_ENDPOINTS.SUBSCRIPTIONS.UPDATE_SUBSCRIPTION, data);
      return { data: response.data, success: true };
    } catch (error: any) {
      return { success: false, error: error.response?.data?.detail || 'Failed to update subscription' };
    }
  },

  /**
   * Check if current company has access to a specific feature
   */
  async checkFeatureAccess(featureName: string): Promise<SubscriptionApiResponse<FeatureAccessCheck>> {
    try {
      const response = await apiClient.get<FeatureAccessCheck>(API_ENDPOINTS.SUBSCRIPTIONS.CHECK_FEATURE_ACCESS(featureName));
      return { data: response.data, success: true };
    } catch (error: any) {
      return { success: false, error: error.response?.data?.detail || 'Failed to check feature access' };
    }
  },
};

/**
 * Plan Change Request API
 */
export const planChangeRequestApi = {
  /**
   * Request a plan change (Company Admin)
   */
  async requestPlanChange(data: PlanChangeRequestCreate): Promise<SubscriptionApiResponse<PlanChangeRequest>> {
    try {
      const response = await apiClient.post<PlanChangeRequest>(API_ENDPOINTS.SUBSCRIPTIONS.REQUEST_PLAN_CHANGE, data);
      return { data: response.data, success: true };
    } catch (error: any) {
      return { success: false, error: error.response?.data?.detail || 'Failed to create plan change request' };
    }
  },

  /**
   * Get my company's plan change requests (Company Admin)
   */
  async getMyRequests(): Promise<SubscriptionApiResponse<PlanChangeRequestWithDetails[]>> {
    try {
      const response = await apiClient.get<PlanChangeRequestWithDetails[]>(API_ENDPOINTS.SUBSCRIPTIONS.MY_PLAN_CHANGE_REQUESTS);
      return { data: response.data, success: true };
    } catch (error: any) {
      return { success: false, error: error.response?.data?.detail || 'Failed to fetch requests' };
    }
  },

  /**
   * Get all plan change requests with optional status filter (System Admin)
   */
  async getAllRequests(status?: string): Promise<SubscriptionApiResponse<PlanChangeRequestWithDetails[]>> {
    try {
      let url = API_ENDPOINTS.SUBSCRIPTIONS.ALL_PLAN_CHANGE_REQUESTS;
      if (status) {
        const queryParams = new URLSearchParams();
        queryParams.append('status', status);
        url += `?${queryParams.toString()}`;
      }

      const response = await apiClient.get<PlanChangeRequestWithDetails[]>(url);
      return { data: response.data, success: true };
    } catch (error: any) {
      return { success: false, error: error.response?.data?.detail || 'Failed to fetch requests' };
    }
  },

  /**
   * Review a plan change request (System Admin)
   */
  async reviewRequest(
    requestId: number,
    data: PlanChangeRequestReview
  ): Promise<SubscriptionApiResponse<PlanChangeRequestWithDetails>> {
    try {
      const response = await apiClient.post<PlanChangeRequestWithDetails>(
        API_ENDPOINTS.SUBSCRIPTIONS.REVIEW_PLAN_CHANGE(requestId),
        data
      );
      return { data: response.data, success: true };
    } catch (error: any) {
      return { success: false, error: error.response?.data?.detail || 'Failed to review request' };
    }
  },

  /**
   * Cancel a plan change request (Company Admin - own requests only)
   */
  async cancelRequest(requestId: number): Promise<SubscriptionApiResponse<PlanChangeRequestWithDetails>> {
    try {
      const response = await apiClient.post<PlanChangeRequestWithDetails>(
        API_ENDPOINTS.SUBSCRIPTIONS.CANCEL_PLAN_CHANGE(requestId),
        {}
      );
      return { data: response.data, success: true };
    } catch (error: any) {
      return { success: false, error: error.response?.data?.detail || 'Failed to cancel request' };
    }
  },
};

/**
 * Convenience export for all subscription APIs
 */
export const subscriptionApi = {
  plans: subscriptionPlanApi,
  subscription: companySubscriptionApi,
  changeRequests: planChangeRequestApi,
};

export default subscriptionApi;
