/**
 * Subscription and Plan Management Types
 * Types for subscription plans, features, and plan change requests
 */

// ============================================================================
// Feature Types (Hierarchical)
// ============================================================================

export interface Feature {
  id: number;
  name: string;
  display_name: string;
  description?: string;
  category?: string;
  parent_feature_id?: number;
  permission_key?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface FeatureNode extends Feature {
  children: FeatureNode[];
}

export interface FeatureCreate {
  name: string;
  display_name: string;
  description?: string;
  category?: string;
  parent_feature_id?: number;
  permission_key?: string;
  is_active?: boolean;
}

export interface FeatureUpdate {
  display_name?: string;
  description?: string;
  category?: string;
  parent_feature_id?: number;
  permission_key?: string;
  is_active?: boolean;
}

// ============================================================================
// Subscription Plan Types
// ============================================================================

export interface SubscriptionPlan {
  id: number;
  name: string;
  display_name: string;
  description?: string;
  price_monthly: number;
  price_yearly?: number;
  currency: string;
  max_users?: number;
  max_exams?: number;
  max_workflows?: number;
  max_storage_gb?: number;
  is_active: boolean;
  is_public: boolean;
  display_order: number;
  created_at: string;
  updated_at: string;
}

export interface SubscriptionPlanWithFeatures extends SubscriptionPlan {
  features: FeatureNode[];
}

export interface SubscriptionPlanCreate {
  name: string;
  display_name: string;
  description?: string;
  price_monthly: number;
  price_yearly?: number;
  currency?: string;
  max_users?: number;
  max_exams?: number;
  max_workflows?: number;
  max_storage_gb?: number;
  is_active?: boolean;
  is_public?: boolean;
  display_order?: number;
}

export interface SubscriptionPlanUpdate {
  display_name?: string;
  description?: string;
  price_monthly?: number;
  price_yearly?: number;
  currency?: string;
  max_users?: number;
  max_exams?: number;
  max_workflows?: number;
  max_storage_gb?: number;
  is_active?: boolean;
  is_public?: boolean;
  display_order?: number;
}

// ============================================================================
// Plan-Feature Junction Types
// ============================================================================

export interface PlanFeature {
  id: number;
  plan_id: number;
  feature_id: number;
  added_by?: number;
  added_at: string;
  feature: Feature;
  plan: SubscriptionPlan;
}

export interface PlanFeatureAdd {
  feature_id: number;
}

// ============================================================================
// Company Subscription Types
// ============================================================================

export interface CompanySubscription {
  id: number;
  company_id: number;
  plan_id: number;
  is_active: boolean;
  is_trial: boolean;
  start_date: string;
  end_date?: string;
  trial_end_date?: string;
  billing_cycle: 'monthly' | 'yearly';
  next_billing_date?: string;
  auto_renew: boolean;
  cancelled_at?: string;
  cancellation_reason?: string;
  created_at: string;
  updated_at: string;
  plan: SubscriptionPlan;
}

export interface CompanySubscriptionWithFeatures extends CompanySubscription {
  plan: SubscriptionPlanWithFeatures;
}

export interface CompanySubscriptionCreate {
  plan_id: number;
  billing_cycle?: 'monthly' | 'yearly';
  auto_renew?: boolean;
  is_trial?: boolean;
  trial_end_date?: string;
}

export interface CompanySubscriptionUpdate {
  billing_cycle?: 'monthly' | 'yearly';
  auto_renew?: boolean;
  is_active?: boolean;
}

// ============================================================================
// Plan Change Request Types
// ============================================================================

export type PlanChangeRequestType = 'upgrade' | 'downgrade';
export type PlanChangeRequestStatus = 'pending' | 'approved' | 'rejected';

export interface PlanChangeRequest {
  id: number;
  company_id: number;
  subscription_id: number;
  current_plan_id: number;
  requested_plan_id: number;
  request_type: PlanChangeRequestType;
  requested_by: number;
  request_message?: string;
  status: PlanChangeRequestStatus;
  reviewed_by?: number;
  review_message?: string;
  reviewed_at?: string;
  created_at: string;
  updated_at: string;
}

export interface PlanChangeRequestWithDetails extends PlanChangeRequest {
  current_plan: SubscriptionPlan;
  requested_plan: SubscriptionPlan;
  company_name?: string;
  requester_name?: string;
  reviewer_name?: string;
}

export interface PlanChangeRequestCreate {
  requested_plan_id: number;
  request_message?: string;
}

export interface PlanChangeRequestReview {
  status: 'approved' | 'rejected';
  review_message?: string;
}

// ============================================================================
// Permission Check Types
// ============================================================================

export interface FeatureAccessCheck {
  has_access: boolean;
  message?: string;
  feature_name: string;
  plan_name?: string;
}

export interface BulkFeatureAccessCheck {
  features: Record<string, boolean>;
  plan_name?: string;
  subscription_active: boolean;
}

// ============================================================================
// UI Component Props Types
// ============================================================================

export interface PlanCardProps {
  plan: SubscriptionPlanWithFeatures;
  isCurrentPlan?: boolean;
  onSubscribe?: (planId: number) => void;
  onRequestChange?: (planId: number) => void;
}

export interface FeatureTreeProps {
  features: FeatureNode[];
  planId?: number;
  onAddFeature?: (featureId: number) => void;
  onRemoveFeature?: (featureId: number) => void;
  showActions?: boolean;
}

export interface PlanChangeRequestCardProps {
  request: PlanChangeRequestWithDetails;
  onApprove?: (requestId: number, message?: string) => void;
  onReject?: (requestId: number, message?: string) => void;
  showActions?: boolean;
}

// ============================================================================
// Filter and Sort Types
// ============================================================================

export interface PlanFilters {
  is_active?: boolean;
  is_public?: boolean;
  min_price?: number;
  max_price?: number;
}

export interface FeatureFilters {
  category?: string;
  is_active?: boolean;
  parent_feature_id?: number;
}

export interface PlanChangeRequestFilters {
  status?: PlanChangeRequestStatus;
  company_id?: number;
  request_type?: PlanChangeRequestType;
}

// ============================================================================
// API Response Types
// ============================================================================

export interface SubscriptionApiResponse<T> {
  data?: T;
  success: boolean;
  error?: string;
}
