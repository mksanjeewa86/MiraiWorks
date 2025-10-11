'use client';

import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  Button,
  Badge,
  Input,
  Textarea,
} from '@/components/ui';
import {
  Plus,
  Settings,
  Check,
  X,
  Edit,
  Trash2,
  Package,
} from 'lucide-react';
import { LoadingSpinner } from '@/components/ui';
import AppLayout from '@/components/layout/AppLayout';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import { useSubscriptionPlans } from '@/hooks/useSubscription';
import { featureCatalogApi, planFeatureApi } from '@/api/features';
import { SubscriptionPlan, FeatureNode, Feature } from '@/types/subscription';
import { toast } from 'sonner';

function AdminPlansContent() {
  const { plans, loading: plansLoading, refetch } = useSubscriptionPlans();
  const [features, setFeatures] = useState<FeatureNode[]>([]);
  const [planFeatures, setPlanFeatures] = useState<Record<number, FeatureNode[]>>({});
  const [selectedPlan, setSelectedPlan] = useState<SubscriptionPlan | null>(null);
  const [showFeatureModal, setShowFeatureModal] = useState(false);

  useEffect(() => {
    loadFeatures();
  }, []);

  useEffect(() => {
    if (plans.length > 0) {
      loadPlanFeatures();
    }
  }, [plans]);

  const loadFeatures = async () => {
    try {
      const result = await featureCatalogApi.getHierarchical();
      if (result.success && result.data) {
        setFeatures(result.data);
      }
    } catch (error) {
      toast.error('Failed to load features');
    }
  };

  const loadPlanFeatures = async () => {
    try {
      const featuresMap: Record<number, FeatureNode[]> = {};

      for (const plan of plans) {
        const result = await planFeatureApi.getPlanFeatures(plan.id);
        if (result.success && result.data) {
          featuresMap[plan.id] = result.data;
        }
      }

      setPlanFeatures(featuresMap);
    } catch (error) {
      toast.error('Failed to load plan features');
    }
  };

  const handleAddFeatureToPlan = async (planId: number, featureId: number) => {
    try {
      const result = await planFeatureApi.addFeatureToPlan(planId, featureId);
      if (result.success) {
        toast.success('Feature added to plan');
        loadPlanFeatures();
      } else {
        toast.error(result.error || 'Failed to add feature');
      }
    } catch (error) {
      // Error handled by API
    }
  };

  const handleRemoveFeatureFromPlan = async (planId: number, featureId: number) => {
    if (!confirm('Remove this feature from the plan?')) return;

    try {
      const result = await planFeatureApi.removeFeatureFromPlan(planId, featureId);
      if (result.success) {
        toast.success('Feature removed from plan');
        loadPlanFeatures();
      } else {
        toast.error(result.error || 'Failed to remove feature');
      }
    } catch (error) {
      // Error handled by API
    }
  };

  const formatPrice = (price: string | number) => {
    const numPrice = typeof price === 'string' ? parseFloat(price) : price;
    return new Intl.NumberFormat('ja-JP', {
      style: 'currency',
      currency: 'JPY',
      minimumFractionDigits: 0,
    }).format(numPrice);
  };

  const isPlanHasFeature = (planId: number, featureId: number): boolean => {
    const features = planFeatures[planId] || [];

    const hasFeature = (feats: FeatureNode[]): boolean => {
      for (const feat of feats) {
        if (feat.id === featureId) return true;
        if (feat.children && feat.children.length > 0) {
          if (hasFeature(feat.children)) return true;
        }
      }
      return false;
    };

    return hasFeature(features);
  };

  const renderFeatureTree = (
    features: FeatureNode[],
    planId: number,
    level = 0
  ): React.JSX.Element[] => {
    return features.map((feature) => {
      const hasFeature = isPlanHasFeature(planId, feature.id);

      return (
        <div key={feature.id} className="space-y-2">
          <div
            className={`flex items-center justify-between p-2 rounded-lg ${
              level > 0 ? 'ml-6' : ''
            } ${hasFeature ? 'bg-green-50' : 'bg-muted/30'}`}
          >
            <div className="flex items-center gap-2">
              {hasFeature ? (
                <Check className="h-4 w-4 text-green-600" />
              ) : (
                <X className="h-4 w-4 text-muted-foreground" />
              )}
              <div>
                <p className="font-medium text-sm">{feature.display_name}</p>
                {feature.permission_key && (
                  <p className="text-xs text-muted-foreground">
                    {feature.permission_key}
                  </p>
                )}
              </div>
            </div>
            <Button
              size="sm"
              variant={hasFeature ? 'destructive' : 'default'}
              onClick={() =>
                hasFeature
                  ? handleRemoveFeatureFromPlan(planId, feature.id)
                  : handleAddFeatureToPlan(planId, feature.id)
              }
            >
              {hasFeature ? 'Remove' : 'Add'}
            </Button>
          </div>
          {feature.children && feature.children.length > 0 && (
            <div>
              {renderFeatureTree(feature.children, planId, level + 1)}
            </div>
          )}
        </div>
      );
    });
  };

  if (plansLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Plan Management</h1>
          <p className="text-muted-foreground">
            Manage subscription plans and features
          </p>
        </div>
      </div>

      {/* Plans */}
      <div className="grid md:grid-cols-2 gap-6">
        {plans.map((plan) => {
          const features = planFeatures[plan.id] || [];
          const featureCount = features.reduce((count, f) => {
            return count + 1 + (f.children?.length || 0);
          }, 0);

          return (
            <Card key={plan.id}>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="flex items-center gap-2">
                      {plan.display_name}
                      <Badge variant={plan.is_active ? 'default' : 'secondary'}>
                        {plan.is_active ? 'Active' : 'Inactive'}
                      </Badge>
                    </CardTitle>
                    <CardDescription>{plan.description}</CardDescription>
                  </div>
                  <Package className="h-8 w-8 text-muted-foreground" />
                </div>

                <div className="mt-4">
                  <div className="text-3xl font-bold">
                    {formatPrice(plan.price_monthly)}
                  </div>
                  <div className="text-sm text-muted-foreground">
                    per month
                  </div>
                </div>
              </CardHeader>

              <CardContent className="space-y-4">
                {/* Plan Limits */}
                <div className="border rounded-lg p-3 space-y-2">
                  <p className="text-sm font-semibold">Plan Limits</p>
                  {plan.max_users && (
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Max Users</span>
                      <span>{plan.max_users}</span>
                    </div>
                  )}
                  {plan.max_workflows && (
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Max Workflows</span>
                      <span>{plan.max_workflows}</span>
                    </div>
                  )}
                  {plan.max_exams && (
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Max Exams</span>
                      <span>{plan.max_exams}</span>
                    </div>
                  )}
                  {plan.max_storage_gb && (
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Storage</span>
                      <span>{plan.max_storage_gb} GB</span>
                    </div>
                  )}
                </div>

                {/* Feature Count */}
                <div className="flex justify-between items-center">
                  <p className="text-sm text-muted-foreground">
                    {featureCount} features assigned
                  </p>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => {
                      setSelectedPlan(plan);
                      setShowFeatureModal(true);
                    }}
                  >
                    <Settings className="h-4 w-4 mr-2" />
                    Manage Features
                  </Button>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Feature Management Modal */}
      {showFeatureModal && selectedPlan && (
        <div className="fixed inset-0 bg-background/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <Card className="max-w-3xl w-full max-h-[80vh] overflow-hidden flex flex-col">
            <CardHeader>
              <CardTitle>Manage Features for {selectedPlan.display_name}</CardTitle>
              <CardDescription>
                Add or remove features from this plan
              </CardDescription>
            </CardHeader>
            <CardContent className="flex-1 overflow-y-auto space-y-3">
              {renderFeatureTree(features, selectedPlan.id)}
            </CardContent>
            <div className="p-4 border-t">
              <Button
                onClick={() => {
                  setShowFeatureModal(false);
                  setSelectedPlan(null);
                }}
                className="w-full"
              >
                Done
              </Button>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
}

export default function AdminPlansPage() {
  return (
    <ProtectedRoute allowedRoles={['system_admin']}>
      <AppLayout>
        <AdminPlansContent />
      </AppLayout>
    </ProtectedRoute>
  );
}
