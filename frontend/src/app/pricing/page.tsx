'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  Button,
  Badge,
} from '@/components/ui';
import { Check, Zap, Star, ArrowRight } from 'lucide-react';
import { LoadingSpinner } from '@/components/ui';
import { subscriptionPlanApi } from '@/api/subscription';
import { SubscriptionPlan, FeatureNode } from '@/types/subscription';
import { toast } from 'sonner';
import { useAuth } from '@/contexts/AuthContext';

function PricingPageContent() {
  const router = useRouter();
  const { user, isAuthenticated } = useAuth();
  const [plans, setPlans] = useState<SubscriptionPlan[]>([]);
  const [planFeatures, setPlanFeatures] = useState<Record<number, FeatureNode[]>>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadPlans();
  }, []);

  const loadPlans = async () => {
    try {
      setLoading(true);
      const result = await subscriptionPlanApi.getPublicPlans();

      if (result.success && result.data) {
        setPlans(result.data);

        // Load features for each plan
        for (const plan of result.data) {
          const featuresResult = await subscriptionPlanApi.getPlanWithFeatures(plan.id);
          if (featuresResult.success && featuresResult.data) {
            setPlanFeatures(prev => ({
              ...prev,
              [plan.id]: featuresResult.data!.features
            }));
          }
        }
      }
    } catch (error) {
      toast.error('Failed to load pricing plans');
    } finally {
      setLoading(false);
    }
  };

  const handleSelectPlan = (plan: SubscriptionPlan) => {
    if (!isAuthenticated) {
      toast.info('Please login to subscribe to a plan');
      router.push('/auth/login');
      return;
    }

    // Redirect to subscription page with plan pre-selected
    router.push(`/subscription?plan=${plan.id}`);
  };

  const formatPrice = (price: string | number) => {
    const numPrice = typeof price === 'string' ? parseFloat(price) : price;
    return new Intl.NumberFormat('ja-JP', {
      style: 'currency',
      currency: 'JPY',
      minimumFractionDigits: 0,
    }).format(numPrice);
  };

  const renderFeatureList = (features: FeatureNode[]) => {
    return features.map((feature) => (
      <div key={feature.id} className="space-y-2">
        <div className="flex items-start gap-2">
          <Check className="h-5 w-5 text-green-600 mt-0.5 flex-shrink-0" />
          <div>
            <p className="font-medium">{feature.display_name}</p>
            {feature.children && feature.children.length > 0 && (
              <ul className="ml-6 mt-1 space-y-1">
                {feature.children.map((child) => (
                  <li key={child.id} className="text-sm text-muted-foreground flex items-center gap-2">
                    <div className="w-1 h-1 rounded-full bg-muted-foreground" />
                    {child.display_name}
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      </div>
    ));
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  const sortedPlans = [...plans].sort((a, b) => a.display_order - b.display_order);

  return (
    <div className="min-h-screen bg-gradient-to-b from-background to-muted/20">
      {/* Header */}
      <div className="container mx-auto px-4 py-16">
        <div className="text-center mb-12">
          <Badge className="mb-4" variant="outline">
            Pricing Plans
          </Badge>
          <h1 className="text-4xl font-bold mb-4">
            Choose the Perfect Plan for Your Team
          </h1>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Powerful recruitment tools to streamline your hiring process
          </p>
        </div>

        {/* Pricing Cards */}
        <div className="grid md:grid-cols-2 gap-8 max-w-5xl mx-auto">
          {sortedPlans.map((plan) => {
            const isBasic = plan.name === 'basic';
            const isPremium = plan.name === 'premium';
            const features = planFeatures[plan.id] || [];

            return (
              <Card
                key={plan.id}
                className={`relative ${
                  isPremium
                    ? 'border-primary shadow-lg scale-105'
                    : 'border-border'
                }`}
              >
                {isPremium && (
                  <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                    <Badge className="bg-primary text-primary-foreground px-4 py-1">
                      <Star className="h-3 w-3 mr-1" />
                      Most Popular
                    </Badge>
                  </div>
                )}

                <CardHeader className="text-center pb-8">
                  <div className="mb-4">
                    {isBasic ? (
                      <Zap className="h-12 w-12 mx-auto text-blue-600" />
                    ) : (
                      <Star className="h-12 w-12 mx-auto text-amber-600" />
                    )}
                  </div>
                  <CardTitle className="text-2xl">{plan.display_name}</CardTitle>
                  <CardDescription className="mt-2">
                    {plan.description}
                  </CardDescription>

                  <div className="mt-6">
                    <div className="text-4xl font-bold">
                      {formatPrice(plan.price_monthly)}
                    </div>
                    <div className="text-muted-foreground mt-1">
                      per month
                    </div>
                    {plan.price_yearly && parseFloat(plan.price_yearly.toString()) > 0 && (
                      <div className="text-sm text-muted-foreground mt-2">
                        or {formatPrice(plan.price_yearly)}/year
                      </div>
                    )}
                  </div>
                </CardHeader>

                <CardContent className="space-y-6">
                  {/* Plan Limits */}
                  <div className="border-t border-b py-4 space-y-2">
                    {plan.max_users && (
                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">Max Users</span>
                        <span className="font-medium">{plan.max_users}</span>
                      </div>
                    )}
                    {plan.max_workflows && (
                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">Max Workflows</span>
                        <span className="font-medium">{plan.max_workflows}</span>
                      </div>
                    )}
                    {plan.max_exams && (
                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">Max Exams</span>
                        <span className="font-medium">{plan.max_exams}</span>
                      </div>
                    )}
                    {plan.max_storage_gb && (
                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">Storage</span>
                        <span className="font-medium">{plan.max_storage_gb} GB</span>
                      </div>
                    )}
                  </div>

                  {/* Features */}
                  <div className="space-y-3">
                    <h4 className="font-semibold">Features included:</h4>
                    {renderFeatureList(features)}
                  </div>

                  {/* CTA Button */}
                  <Button
                    onClick={() => handleSelectPlan(plan)}
                    className={`w-full ${
                      isPremium
                        ? 'bg-primary hover:bg-primary/90'
                        : ''
                    }`}
                    variant={isPremium ? 'default' : 'outline'}
                    size="lg"
                  >
                    {isBasic ? 'Get Started Free' : 'Upgrade to Premium'}
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </Button>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* FAQ or Additional Info */}
        <div className="mt-16 text-center">
          <p className="text-muted-foreground">
            Need a custom plan for your organization?{' '}
            <a href="/contact" className="text-primary hover:underline">
              Contact us
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}

export default function PricingPage() {
  return <PricingPageContent />;
}
