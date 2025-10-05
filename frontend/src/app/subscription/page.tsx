'use client';

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
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
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui';
import {
  Check,
  X,
  ArrowUpRight,
  ArrowDownRight,
  Clock,
  CreditCard,
  AlertCircle,
  Zap,
} from 'lucide-react';
import { LoadingSpinner } from '@/components/ui';
import AppLayout from '@/components/layout/AppLayout';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import {
  useMySubscription,
  useSubscriptionPlans,
  useMyPlanChangeRequests,
  useSubscriptionMutations,
  usePlanChangeRequestMutations,
} from '@/hooks/useSubscription';
import { SubscriptionPlan, FeatureNode } from '@/types/subscription';
import { toast } from 'sonner';

function SubscriptionManagementContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const preselectedPlan = searchParams?.get('plan');

  const { subscription, loading: subLoading, refetch: refetchSubscription } = useMySubscription();
  const { plans, loading: plansLoading } = useSubscriptionPlans();
  const { requests, refetch: refetchRequests } = useMyPlanChangeRequests();
  const { subscribe, updateSubscription } = useSubscriptionMutations();
  const { requestPlanChange } = usePlanChangeRequestMutations();

  const [showUpgradeModal, setShowUpgradeModal] = useState(false);
  const [selectedPlan, setSelectedPlan] = useState<SubscriptionPlan | null>(null);
  const [upgradeMessage, setUpgradeMessage] = useState('');
  const [billingCycle, setBillingCycle] = useState<'monthly' | 'yearly'>('monthly');
  const [autoRenew, setAutoRenew] = useState(true);

  useEffect(() => {
    if (preselectedPlan && plans.length > 0 && !subscription) {
      const plan = plans.find(p => p.id === parseInt(preselectedPlan));
      if (plan) {
        setSelectedPlan(plan);
        setShowUpgradeModal(true);
      }
    }
  }, [preselectedPlan, plans, subscription]);

  const formatPrice = (price: string | number) => {
    const numPrice = typeof price === 'string' ? parseFloat(price) : price;
    return new Intl.NumberFormat('ja-JP', {
      style: 'currency',
      currency: 'JPY',
      minimumFractionDigits: 0,
    }).format(numPrice);
  };

  const handleInitialSubscribe = async () => {
    if (!selectedPlan) return;

    try {
      await subscribe({
        plan_id: selectedPlan.id,
        billing_cycle: billingCycle,
        auto_renew: autoRenew,
      });
      setShowUpgradeModal(false);
      refetchSubscription();
    } catch (error) {
      // Error already handled by hook
    }
  };

  const handleRequestPlanChange = async (targetPlan: SubscriptionPlan) => {
    if (!subscription) return;

    const isUpgrade = parseFloat(targetPlan.price_monthly.toString()) >
                      parseFloat(subscription.plan.price_monthly.toString());

    try {
      await requestPlanChange({
        requested_plan_id: targetPlan.id,
        request_message: upgradeMessage || `Request to ${isUpgrade ? 'upgrade' : 'downgrade'} to ${targetPlan.display_name}`,
      });
      setShowUpgradeModal(false);
      setUpgradeMessage('');
      refetchRequests();
    } catch (error) {
      // Error already handled by hook
    }
  };

  const handleUpdateSettings = async () => {
    try {
      await updateSubscription({
        billing_cycle: billingCycle,
        auto_renew: autoRenew,
      });
      refetchSubscription();
    } catch (error) {
      // Error already handled by hook
    }
  };

  const renderFeatureList = (features: FeatureNode[]) => {
    return features.map((feature) => (
      <div key={feature.id} className="flex items-start gap-2">
        <Check className="h-4 w-4 text-green-600 mt-0.5" />
        <span className="text-sm">{feature.display_name}</span>
      </div>
    ));
  };

  const getRequestStatusBadge = (status: string) => {
    switch (status) {
      case 'pending':
        return <Badge variant="outline" className="text-yellow-600"><Clock className="h-3 w-3 mr-1" />Pending</Badge>;
      case 'approved':
        return <Badge variant="outline" className="text-green-600"><Check className="h-3 w-3 mr-1" />Approved</Badge>;
      case 'rejected':
        return <Badge variant="outline" className="text-red-600"><X className="h-3 w-3 mr-1" />Rejected</Badge>;
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  if (subLoading || plansLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  // No subscription - show initial subscribe flow
  if (!subscription) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold mb-2">Choose Your Plan</h1>
          <p className="text-muted-foreground">
            Select a subscription plan to get started
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-6 max-w-4xl mx-auto">
          {plans.map((plan) => (
            <Card key={plan.id} className="relative">
              <CardHeader>
                <CardTitle>{plan.display_name}</CardTitle>
                <CardDescription>{plan.description}</CardDescription>
                <div className="text-3xl font-bold mt-4">
                  {formatPrice(plan.price_monthly)}
                  <span className="text-sm font-normal text-muted-foreground">/month</span>
                </div>
              </CardHeader>
              <CardContent>
                <Button
                  onClick={() => {
                    setSelectedPlan(plan);
                    setShowUpgradeModal(true);
                  }}
                  className="w-full"
                  variant={plan.name === 'premium' ? 'default' : 'outline'}
                >
                  Select {plan.display_name}
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Initial Subscribe Modal */}
        {showUpgradeModal && selectedPlan && (
          <div className="fixed inset-0 bg-background/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
            <Card className="max-w-md w-full">
              <CardHeader>
                <CardTitle>Subscribe to {selectedPlan.display_name}</CardTitle>
                <CardDescription>
                  {formatPrice(selectedPlan.price_monthly)}/month
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="text-sm font-medium">Billing Cycle</label>
                  <Select value={billingCycle} onValueChange={(value) => setBillingCycle(value as 'monthly' | 'yearly')}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="monthly">Monthly</SelectItem>
                      <SelectItem value="yearly">Yearly</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={autoRenew}
                    onChange={(e) => setAutoRenew(e.target.checked)}
                    className="rounded"
                  />
                  <label className="text-sm">Auto-renew subscription</label>
                </div>

                <div className="flex gap-2">
                  <Button onClick={handleInitialSubscribe} className="flex-1">
                    Subscribe Now
                  </Button>
                  <Button variant="outline" onClick={() => setShowUpgradeModal(false)}>
                    Cancel
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    );
  }

  const currentPlan = subscription.plan;
  const otherPlans = plans.filter(p => p.id !== currentPlan.id);
  const pendingRequest = requests.find(r => r.status === 'pending');

  return (
    <div className="container mx-auto px-4 py-8 space-y-8">
      {/* Current Subscription */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                Current Plan: {currentPlan.display_name}
                <Badge>{subscription.is_trial ? 'Trial' : 'Active'}</Badge>
              </CardTitle>
              <CardDescription>
                {formatPrice(currentPlan.price_monthly)}/month
              </CardDescription>
            </div>
            {subscription.is_active ? (
              <Badge variant="outline" className="text-green-600">
                <Check className="h-3 w-3 mr-1" />
                Active
              </Badge>
            ) : (
              <Badge variant="outline" className="text-red-600">
                <X className="h-3 w-3 mr-1" />
                Inactive
              </Badge>
            )}
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Subscription Details */}
          <div className="grid md:grid-cols-2 gap-4 p-4 bg-muted/50 rounded-lg">
            <div>
              <p className="text-sm text-muted-foreground">Billing Cycle</p>
              <p className="font-medium capitalize">{subscription.billing_cycle}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Auto-Renew</p>
              <p className="font-medium">{subscription.auto_renew ? 'Enabled' : 'Disabled'}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Start Date</p>
              <p className="font-medium">{new Date(subscription.start_date).toLocaleDateString()}</p>
            </div>
            {subscription.next_billing_date && (
              <div>
                <p className="text-sm text-muted-foreground">Next Billing</p>
                <p className="font-medium">{new Date(subscription.next_billing_date).toLocaleDateString()}</p>
              </div>
            )}
          </div>

          {/* Features */}
          <div>
            <h4 className="font-semibold mb-3">Your Features</h4>
            <div className="grid md:grid-cols-2 gap-3">
              {renderFeatureList(subscription.plan.features)}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Pending Request Alert */}
      {pendingRequest && (
        <Card className="border-yellow-500/50 bg-yellow-50/10">
          <CardHeader>
            <CardTitle className="text-yellow-600 flex items-center gap-2">
              <AlertCircle className="h-5 w-5" />
              Plan Change Request Pending
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground mb-2">
              Your request to change to <strong>{pendingRequest.requested_plan?.display_name}</strong> is awaiting admin approval.
            </p>
            {pendingRequest.request_message && (
              <p className="text-sm text-muted-foreground">
                Message: {pendingRequest.request_message}
              </p>
            )}
          </CardContent>
        </Card>
      )}

      {/* Available Plans */}
      {!pendingRequest && otherPlans.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Change Plan</CardTitle>
            <CardDescription>
              Upgrade or downgrade your subscription (requires admin approval)
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {otherPlans.map((plan) => {
              const isUpgrade = parseFloat(plan.price_monthly.toString()) >
                               parseFloat(currentPlan.price_monthly.toString());

              return (
                <div key={plan.id} className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="flex-1">
                    <h4 className="font-semibold flex items-center gap-2">
                      {plan.display_name}
                      {isUpgrade ? (
                        <ArrowUpRight className="h-4 w-4 text-green-600" />
                      ) : (
                        <ArrowDownRight className="h-4 w-4 text-blue-600" />
                      )}
                    </h4>
                    <p className="text-sm text-muted-foreground">{plan.description}</p>
                    <p className="text-lg font-bold mt-1">
                      {formatPrice(plan.price_monthly)}/month
                    </p>
                  </div>
                  <Button
                    onClick={() => {
                      setSelectedPlan(plan);
                      setShowUpgradeModal(true);
                    }}
                    variant={isUpgrade ? 'default' : 'outline'}
                  >
                    {isUpgrade ? 'Upgrade' : 'Downgrade'}
                  </Button>
                </div>
              );
            })}
          </CardContent>
        </Card>
      )}

      {/* Plan Change Request Modal */}
      {showUpgradeModal && selectedPlan && (
        <div className="fixed inset-0 bg-background/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <Card className="max-w-md w-full">
            <CardHeader>
              <CardTitle>Request Plan Change</CardTitle>
              <CardDescription>
                {selectedPlan.display_name} - {formatPrice(selectedPlan.price_monthly)}/month
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-sm font-medium">Message to Admin (optional)</label>
                <Textarea
                  value={upgradeMessage}
                  onChange={(e) => setUpgradeMessage(e.target.value)}
                  placeholder="Why do you need this plan change?"
                  rows={3}
                />
              </div>

              <div className="flex gap-2">
                <Button onClick={() => handleRequestPlanChange(selectedPlan)} className="flex-1">
                  Submit Request
                </Button>
                <Button variant="outline" onClick={() => {
                  setShowUpgradeModal(false);
                  setUpgradeMessage('');
                }}>
                  Cancel
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Request History */}
      {requests.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Request History</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {requests.map((request) => (
                <div key={request.id} className="flex items-center justify-between p-3 border rounded-lg">
                  <div>
                    <p className="font-medium">
                      {request.current_plan?.display_name} → {request.requested_plan?.display_name}
                    </p>
                    <p className="text-sm text-muted-foreground">
                      {new Date(request.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  {getRequestStatusBadge(request.status)}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

export default function SubscriptionManagementPage() {
  return (
    <ProtectedRoute allowedRoles={['admin']}>
      <AppLayout>
        <SubscriptionManagementContent />
      </AppLayout>
    </ProtectedRoute>
  );
}
