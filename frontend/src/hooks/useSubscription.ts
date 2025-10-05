import { useState, useEffect, useCallback } from 'react';
import {
  subscriptionPlanApi,
  companySubscriptionApi,
  planChangeRequestApi,
} from '@/api/subscription';
import type {
  SubscriptionPlan,
  CompanySubscriptionWithFeatures,
  CompanySubscriptionCreate,
  PlanChangeRequest,
  PlanChangeRequestCreate,
  PlanChangeRequestWithDetails,
  FeatureAccessCheck,
} from '@/types/subscription';
import { toast } from 'sonner';

// ============================================================================
// SUBSCRIPTION MANAGEMENT HOOKS
// ============================================================================

/**
 * Hook for fetching company's current subscription
 */
export function useMySubscription() {
  const [subscription, setSubscription] = useState<CompanySubscriptionWithFeatures | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchSubscription = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await companySubscriptionApi.getMySubscription();

      if (response.success && response.data) {
        setSubscription(response.data);
      } else {
        setError(response.error || 'Failed to load subscription');
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to load subscription';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchSubscription();
  }, [fetchSubscription]);

  return { subscription, loading, error, refetch: fetchSubscription };
}

/**
 * Hook for fetching public subscription plans
 */
export function useSubscriptionPlans() {
  const [plans, setPlans] = useState<SubscriptionPlan[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchPlans = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await subscriptionPlanApi.getPublicPlans();

      if (response.success && response.data) {
        setPlans(response.data);
      } else {
        setError(response.error || 'Failed to load plans');
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to load plans';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchPlans();
  }, [fetchPlans]);

  return { plans, loading, error, refetch: fetchPlans };
}

/**
 * Hook for subscription mutations (subscribe, update)
 */
export function useSubscriptionMutations() {
  const subscribe = async (data: CompanySubscriptionCreate) => {
    try {
      const response = await companySubscriptionApi.subscribe(data);

      if (response.success) {
        toast.success('Successfully subscribed to plan!');
        return response.data;
      } else {
        toast.error(response.error || 'Failed to subscribe');
        throw new Error(response.error);
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to subscribe';
      toast.error(errorMessage);
      throw err;
    }
  };

  const updateSubscription = async (data: Partial<CompanySubscriptionCreate>) => {
    try {
      const response = await companySubscriptionApi.updateSubscription(data);

      if (response.success) {
        toast.success('Subscription updated successfully!');
        return response.data;
      } else {
        toast.error(response.error || 'Failed to update subscription');
        throw new Error(response.error);
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to update subscription';
      toast.error(errorMessage);
      throw err;
    }
  };

  return { subscribe, updateSubscription };
}

/**
 * Hook for plan change requests
 */
export function useMyPlanChangeRequests() {
  const [requests, setRequests] = useState<PlanChangeRequestWithDetails[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchRequests = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await planChangeRequestApi.getMyRequests();

      if (response.success && response.data) {
        setRequests(response.data);
      } else {
        setError(response.error || 'Failed to load requests');
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to load requests';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchRequests();
  }, [fetchRequests]);

  return { requests, loading, error, refetch: fetchRequests };
}

/**
 * Hook for plan change request mutations
 */
export function usePlanChangeRequestMutations() {
  const requestPlanChange = async (data: PlanChangeRequestCreate) => {
    try {
      const response = await planChangeRequestApi.requestPlanChange(data);

      if (response.success) {
        toast.success('Plan change request submitted! Admin will review it.');
        return response.data;
      } else {
        toast.error(response.error || 'Failed to submit request');
        throw new Error(response.error);
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to submit request';
      toast.error(errorMessage);
      throw err;
    }
  };

  return { requestPlanChange };
}

/**
 * Hook for checking feature access
 */
export function useFeatureAccess(featureName: string) {
  const [access, setAccess] = useState<FeatureAccessCheck | null>(null);
  const [loading, setLoading] = useState(false);

  const checkAccess = useCallback(async () => {
    if (!featureName) return;

    setLoading(true);

    try {
      const response = await companySubscriptionApi.checkFeatureAccess(featureName);

      if (response.success && response.data) {
        setAccess(response.data);
      }
    } catch (err) {
      // Silent fail - feature access defaults to false
      setAccess({
        has_access: false,
        message: 'Failed to check access',
        feature_name: featureName,
      });
    } finally {
      setLoading(false);
    }
  }, [featureName]);

  useEffect(() => {
    checkAccess();
  }, [checkAccess]);

  return { access, loading, refetch: checkAccess };
}

// ============================================================================
// ADMIN HOOKS (System Admin Only)
// ============================================================================

/**
 * Hook for fetching all plan change requests (System Admin)
 */
export function useAllPlanChangeRequests(status?: string) {
  const [requests, setRequests] = useState<PlanChangeRequestWithDetails[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchRequests = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await planChangeRequestApi.getAllRequests(status);

      if (response.success && response.data) {
        setRequests(response.data);
      } else {
        setError(response.error || 'Failed to load requests');
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to load requests';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  }, [status]);

  useEffect(() => {
    fetchRequests();
  }, [fetchRequests]);

  return { requests, loading, error, refetch: fetchRequests };
}

/**
 * Hook for reviewing plan change requests (System Admin)
 */
export function useReviewPlanChangeRequest() {
  const reviewRequest = async (
    requestId: number,
    status: 'approved' | 'rejected',
    reviewMessage?: string
  ) => {
    try {
      const response = await planChangeRequestApi.reviewRequest(requestId, {
        status,
        review_message: reviewMessage,
      });

      if (response.success) {
        toast.success(`Request ${status} successfully!`);
        return response.data;
      } else {
        toast.error(response.error || 'Failed to review request');
        throw new Error(response.error);
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to review request';
      toast.error(errorMessage);
      throw err;
    }
  };

  return { reviewRequest };
}
