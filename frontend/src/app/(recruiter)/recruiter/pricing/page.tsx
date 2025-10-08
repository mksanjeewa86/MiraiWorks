'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Check, Zap, Star, Sparkles } from 'lucide-react';

export default function RecruiterPricingPage() {
  const [billingCycle, setBillingCycle] = useState<'monthly' | 'yearly'>('monthly');

  const plans = [
    {
      name: 'Starter',
      description: 'Perfect for independent recruiters',
      price: {
        monthly: 39,
        yearly: 390,
      },
      icon: Zap,
      color: 'blue',
      features: [
        'Up to 20 active candidates',
        'Basic candidate management',
        'Up to 3 client companies',
        'Email support',
        'Basic placement tracking',
        'Mobile access',
      ],
      cta: 'Start Free Trial',
      popular: false,
    },
    {
      name: 'Professional',
      description: 'Best for growing recruitment businesses',
      price: {
        monthly: 89,
        yearly: 890,
      },
      icon: Star,
      color: 'blue',
      features: [
        'Unlimited candidates',
        'Advanced candidate database',
        'Unlimited client companies',
        'Priority email & chat support',
        'Advanced placement analytics',
        'Commission tracking',
        'Team collaboration',
        'Interview scheduling',
        'API access',
      ],
      cta: 'Start Free Trial',
      popular: true,
    },
    {
      name: 'Enterprise',
      description: 'For large recruitment agencies',
      price: {
        monthly: 249,
        yearly: 2490,
      },
      icon: Sparkles,
      color: 'gradient',
      features: [
        'Everything in Professional',
        'Dedicated account manager',
        'Custom integrations',
        'SSO & advanced security',
        'Onboarding & training',
        'SLA guarantee',
        'White-label options',
        'Custom reporting',
        'Unlimited team members',
      ],
      cta: 'Contact Sales',
      popular: false,
    },
  ];

  const calculateYearlySavings = (monthlyPrice: number, yearlyPrice: number) => {
    const monthlyCost = monthlyPrice * 12;
    const savings = monthlyCost - yearlyPrice;
    const percentage = Math.round((savings / monthlyCost) * 100);
    return percentage;
  };

  return (
    <>
      {/* Hero Section */}
      <section className="py-24 bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 relative overflow-hidden">
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiM5Q0EzQUYiIGZpbGwtb3BhY2l0eT0iMC4xIj48cGF0aCBkPSJtMzYgMzQgMjItMjIgNCAyMiA0LTIgMC0yIDItNCAwLTJ6bTAtMjIgMjAgMjAtMTIgMTItMTIgMCAwLTggMTItMTJ6bTI0IDI0IDEyLTEyIDAtOCAwLTEwLTQgMCAwIDRoLTh2OGgtNGwtNCAwIDQgNGgxMnptMC0xNiA4LTggMCAwIDAgOGgtOHoiLz48L2c+PC9nPjwvc3ZnPg==')] opacity-20"></div>

        <div className="absolute top-20 left-10 w-72 h-72 bg-blue-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob"></div>
        <div className="absolute top-40 right-10 w-72 h-72 bg-cyan-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-2000"></div>

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="animate-fade-in-up">
            <span className="inline-block px-4 py-2 text-sm font-semibold text-blue-300 bg-blue-500/20 rounded-full mb-8">
              Pricing Plans
            </span>
            <h1 className="text-5xl md:text-6xl font-bold text-white mb-8">
              Simple, Transparent
              <span className="block bg-gradient-to-r from-blue-400 via-cyan-400 to-teal-400 bg-clip-text text-transparent">
                Pricing
              </span>
            </h1>
            <p className="text-xl md:text-2xl text-blue-100 max-w-3xl mx-auto mb-12">
              Choose the perfect plan for your recruitment business. All plans include a 14-day free trial.
            </p>

            {/* Billing Toggle */}
            <div className="inline-flex items-center bg-white/10 backdrop-blur-sm rounded-full p-1 border border-white/20">
              <button
                onClick={() => setBillingCycle('monthly')}
                className={`px-6 py-3 rounded-full text-sm font-semibold transition-all duration-300 ${
                  billingCycle === 'monthly'
                    ? 'bg-white text-blue-900 shadow-lg'
                    : 'text-white hover:text-blue-200'
                }`}
              >
                Monthly
              </button>
              <button
                onClick={() => setBillingCycle('yearly')}
                className={`px-6 py-3 rounded-full text-sm font-semibold transition-all duration-300 ${
                  billingCycle === 'yearly'
                    ? 'bg-white text-blue-900 shadow-lg'
                    : 'text-white hover:text-blue-200'
                }`}
              >
                Yearly
                <span className="ml-2 text-xs bg-green-500 text-white px-2 py-1 rounded-full">
                  Save 20%
                </span>
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing Cards */}
      <section className="py-24 bg-gradient-to-b from-gray-50 to-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {plans.map((plan, index) => {
              const Icon = plan.icon;
              const price = billingCycle === 'monthly' ? plan.price.monthly : plan.price.yearly;
              const savings = calculateYearlySavings(plan.price.monthly, plan.price.yearly);

              return (
                <div
                  key={plan.name}
                  className={`group relative animate-fade-in-up ${
                    plan.popular ? 'md:scale-110 md:z-10' : ''
                  }`}
                  style={{ animationDelay: `${index * 100}ms` }}
                >
                  {/* Popular Badge */}
                  {plan.popular && (
                    <div className="absolute -top-5 left-1/2 -translate-x-1/2 z-20">
                      <div className="bg-gradient-to-r from-blue-600 to-cyan-600 text-white px-6 py-2 rounded-full text-sm font-bold shadow-lg flex items-center gap-2">
                        <Star className="w-4 h-4 fill-current" />
                        Most Popular
                      </div>
                    </div>
                  )}

                  {/* Card */}
                  <div
                    className={`relative h-full bg-white rounded-3xl shadow-xl border-2 transition-all duration-500 ${
                      plan.popular
                        ? 'border-blue-500 shadow-blue-500/20'
                        : 'border-gray-200 hover:border-blue-300'
                    } overflow-hidden group-hover:shadow-2xl group-hover:-translate-y-2`}
                  >
                    {/* Gradient Background Effect */}
                    <div
                      className={`absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500 ${
                        plan.color === 'blue'
                          ? 'bg-gradient-to-br from-blue-50 to-cyan-50'
                          : plan.color === 'purple'
                          ? 'bg-gradient-to-br from-blue-50 to-cyan-50'
                          : 'bg-gradient-to-br from-yellow-50 to-orange-50'
                      }`}
                    ></div>

                    <div className="relative p-8">
                      {/* Icon */}
                      <div
                        className={`w-16 h-16 rounded-2xl flex items-center justify-center mb-6 transform group-hover:scale-110 transition-transform duration-300 ${
                          plan.color === 'blue'
                            ? 'bg-gradient-to-r from-blue-500 to-cyan-500'
                            : plan.color === 'purple'
                            ? 'bg-gradient-to-r from-blue-500 to-cyan-500'
                            : 'bg-gradient-to-r from-cyan-500 to-orange-500'
                        }`}
                      >
                        <Icon className="w-8 h-8 text-white" />
                      </div>

                      {/* Plan Name */}
                      <h3 className="text-2xl font-bold text-gray-900 mb-2">{plan.name}</h3>
                      <p className="text-gray-600 mb-6 min-h-[3rem]">{plan.description}</p>

                      {/* Price */}
                      <div className="mb-8">
                        <div className="flex items-baseline gap-2">
                          <span className="text-5xl font-bold text-gray-900">${price}</span>
                          <span className="text-gray-600">
                            /{billingCycle === 'monthly' ? 'month' : 'year'}
                          </span>
                        </div>
                        {billingCycle === 'yearly' && (
                          <p className="text-sm text-green-600 mt-2 font-semibold">
                            Save {savings}% with yearly billing
                          </p>
                        )}
                      </div>

                      {/* CTA Button */}
                      <Link
                        href={plan.name === 'Enterprise' ? '/recruiter/contact' : '/auth/register'}
                        className={`block w-full px-6 py-4 rounded-xl text-center font-bold text-lg transition-all duration-300 transform group-hover:scale-105 ${
                          plan.popular
                            ? 'bg-gradient-to-r from-blue-600 to-cyan-600 text-white shadow-lg hover:shadow-blue-500/50'
                            : 'bg-gray-900 text-white hover:bg-gray-800'
                        }`}
                      >
                        {plan.cta}
                      </Link>

                      {/* Features */}
                      <div className="mt-8 space-y-4">
                        <p className="text-sm font-semibold text-gray-900 mb-4">
                          What&apos;s included:
                        </p>
                        {plan.features.map((feature, idx) => (
                          <div
                            key={idx}
                            className="flex items-start gap-3 animate-fade-in"
                            style={{ animationDelay: `${idx * 50}ms` }}
                          >
                            <div
                              className={`flex-shrink-0 w-5 h-5 rounded-full flex items-center justify-center mt-0.5 ${
                                plan.color === 'blue'
                                  ? 'bg-blue-100'
                                  : plan.color === 'purple'
                                  ? 'bg-blue-100'
                                  : 'bg-yellow-100'
                              }`}
                            >
                              <Check
                                className={`w-3 h-3 ${
                                  plan.color === 'blue'
                                    ? 'text-blue-600'
                                    : plan.color === 'purple'
                                    ? 'text-blue-600'
                                    : 'text-yellow-600'
                                }`}
                              />
                            </div>
                            <span className="text-gray-700 text-sm">{feature}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="py-24 bg-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Frequently Asked Questions
            </h2>
            <p className="text-xl text-gray-600">
              Everything you need to know about our pricing
            </p>
          </div>

          <div className="space-y-6">
            <details className="group">
              <summary className="flex justify-between items-center font-semibold cursor-pointer list-none p-6 bg-gradient-to-r from-blue-50 to-cyan-50 rounded-2xl border border-blue-100 hover:from-blue-100 hover:to-pink-100 transition-all duration-300">
                <span className="text-gray-900">Can I change my plan later?</span>
                <span className="transition-transform duration-300 group-open:rotate-180 text-blue-600">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="m6 9 6 6 6-6" />
                  </svg>
                </span>
              </summary>
              <div className="mt-4 p-6 bg-white rounded-2xl border border-gray-100">
                <p className="text-gray-600 leading-relaxed">
                  Yes! You can upgrade or downgrade your plan at any time. Changes take effect immediately, and we&apos;ll prorate the charges accordingly.
                </p>
              </div>
            </details>

            <details className="group">
              <summary className="flex justify-between items-center font-semibold cursor-pointer list-none p-6 bg-gradient-to-r from-blue-50 to-cyan-50 rounded-2xl border border-blue-100 hover:from-blue-100 hover:to-cyan-100 transition-all duration-300">
                <span className="text-gray-900">What payment methods do you accept?</span>
                <span className="transition-transform duration-300 group-open:rotate-180 text-blue-600">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="m6 9 6 6 6-6" />
                  </svg>
                </span>
              </summary>
              <div className="mt-4 p-6 bg-white rounded-2xl border border-gray-100">
                <p className="text-gray-600 leading-relaxed">
                  We accept all major credit cards (Visa, MasterCard, American Express) and bank transfers for Enterprise plans.
                </p>
              </div>
            </details>

            <details className="group">
              <summary className="flex justify-between items-center font-semibold cursor-pointer list-none p-6 bg-gradient-to-r from-yellow-50 to-orange-50 rounded-2xl border border-yellow-100 hover:from-yellow-100 hover:to-orange-100 transition-all duration-300">
                <span className="text-gray-900">Is there a free trial?</span>
                <span className="transition-transform duration-300 group-open:rotate-180 text-yellow-600">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="m6 9 6 6 6-6" />
                  </svg>
                </span>
              </summary>
              <div className="mt-4 p-6 bg-white rounded-2xl border border-gray-100">
                <p className="text-gray-600 leading-relaxed">
                  Yes! All plans come with a 14-day free trial. No credit card required to start your trial.
                </p>
              </div>
            </details>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 bg-gradient-to-r from-gray-900 via-blue-900 to-gray-900 relative overflow-hidden">
        <div className="absolute inset-0">
          <div className="absolute top-0 left-1/4 w-96 h-96 bg-blue-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob"></div>
          <div className="absolute top-0 right-1/4 w-96 h-96 bg-cyan-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-2000"></div>
        </div>

        <div className="relative max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
            Ready to Grow Your Recruitment Business?
          </h2>
          <p className="text-xl text-blue-100 mb-12">
            Start your free trial today. No credit card required.
          </p>
          <div className="flex flex-col sm:flex-row gap-6 justify-center">
            <Link
              href="/auth/register"
              className="inline-flex items-center px-10 py-5 text-xl font-bold rounded-2xl text-white bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 transition-all duration-300 transform hover:scale-105 shadow-2xl"
            >
              Start Free Trial
            </Link>
            <Link
              href="/recruiter/contact"
              className="inline-flex items-center px-10 py-5 text-xl font-bold rounded-2xl border-2 border-white/30 text-white bg-white/10 backdrop-blur-sm hover:bg-white/20 transition-all duration-300 transform hover:scale-105"
            >
              Contact Sales
            </Link>
          </div>
        </div>
      </section>
    </>
  );
}
