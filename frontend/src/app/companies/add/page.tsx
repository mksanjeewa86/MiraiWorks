'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowLeft, Save, Calendar, Settings } from 'lucide-react';
import { companiesApi } from '@/api/companies';
import { subscriptionPlanApi } from '@/api/subscription';
import { CompanyCreate, CompanyType } from '@/types/company';
import { CompanyFormData } from '@/types/forms';
import { useToast } from '@/contexts/ToastContext';
import AppLayout from '@/components/layout/AppLayout';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import { PREFECTURES } from '@/utils/prefectures';
import type { SubscriptionPlan } from '@/types/subscription';

const emptyFormData: CompanyFormData = {
  name: '',
  type: 'recruiter',
  email: '',
  phone: '',
  website: '',
  postal_code: '',
  prefecture: '',
  city: '',
  description: '',
  plan_id: undefined,
  is_trial: false,
  trial_days: 30,
};

function AddCompanyContent() {
  const router = useRouter();
  const { showToast } = useToast();
  const [formData, setFormData] = useState<CompanyFormData>(emptyFormData);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showPrefectureDropdown, setShowPrefectureDropdown] = useState(false);
  const prefectureDropdownRef = useRef<HTMLDivElement>(null);
  const [plans, setPlans] = useState<SubscriptionPlan[]>([]);
  const [loadingPlans, setLoadingPlans] = useState(true);

  // Fetch subscription plans
  useEffect(() => {
    const fetchPlans = async () => {
      try {
        setLoadingPlans(true);
        const response = await subscriptionPlanApi.getPlans();
        setPlans(response.data || []);
      } catch (err) {
        console.error('Failed to load subscription plans:', err);
      } finally {
        setLoadingPlans(false);
      }
    };
    fetchPlans();
  }, []);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        prefectureDropdownRef.current &&
        !prefectureDropdownRef.current.contains(event.target as Node)
      ) {
        setShowPrefectureDropdown(false);
      }
    };

    if (showPrefectureDropdown) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [showPrefectureDropdown]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (submitting) return;

    try {
      setSubmitting(true);
      setError(null);

      const companyData: CompanyCreate = {
        name: formData.name,
        type: formData.type,
        email: formData.email,
        phone: formData.phone,
        website: formData.website || undefined,
        postal_code: formData.postal_code || undefined,
        prefecture: formData.prefecture || undefined,
        city: formData.city || undefined,
        description: formData.description || undefined,
        plan_id: formData.plan_id || undefined,
        is_trial: formData.is_trial || false,
        trial_days: formData.is_trial ? (formData.trial_days || 30) : undefined,
      };

      await companiesApi.createCompany(companyData);
      showToast({
        type: 'success',
        title: 'Company created successfully!',
        message: `${formData.name} has been created. An activation email will be sent to ${formData.email}.`,
      });
      router.push('/companies');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create company');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <AppLayout>
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="flex items-center mb-6">
          <button
            onClick={() => router.back()}
            className="mr-4 p-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800"
          >
            <ArrowLeft className="h-5 w-5" />
          </button>
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Add Company</h1>
            <p className="text-gray-600 dark:text-gray-400">Create a new company in the system</p>
          </div>
        </div>

        {/* Form */}
        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
          {error && (
            <div className="mb-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-400 px-4 py-3 rounded">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Company Name */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Company Name *
                </label>
                <input
                  type="text"
                  required
                  value={formData.name}
                  onChange={(e) => setFormData((prev) => ({ ...prev, name: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                  placeholder="Enter company name"
                />
              </div>

              {/* Email */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Email *
                </label>
                <input
                  type="email"
                  required
                  value={formData.email}
                  onChange={(e) => setFormData((prev) => ({ ...prev, email: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                  placeholder="contact@company.com"
                />
              </div>

              {/* Type */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Type *
                </label>
                <select
                  required
                  value={formData.type}
                  onChange={(e) =>
                    setFormData((prev) => ({ ...prev, type: e.target.value as CompanyType }))
                  }
                  className="w-full px-3 py-2 pr-8 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white appearance-none bg-white"
                  style={{
                    backgroundImage: `url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M6 8l4 4 4-4'/%3e%3c/svg%3e")`,
                    backgroundPosition: 'right 12px center',
                    backgroundRepeat: 'no-repeat',
                    backgroundSize: '16px',
                  }}
                >
                  <option value="member">Employer</option>
                  <option value="member">Recruiter</option>
                </select>
              </div>

              {/* Phone */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Phone *
                </label>
                <input
                  type="tel"
                  required
                  value={formData.phone}
                  onChange={(e) => setFormData((prev) => ({ ...prev, phone: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                  placeholder="03-1234-5678"
                />
              </div>

              {/* Website */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Website
                </label>
                <input
                  type="url"
                  value={formData.website}
                  onChange={(e) => setFormData((prev) => ({ ...prev, website: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                  placeholder="https://company.com"
                />
              </div>
            </div>

            {/* Address Fields */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Postal Code */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  郵便番号 (Postal Code)
                </label>
                <input
                  type="text"
                  value={formData.postal_code}
                  onChange={(e) =>
                    setFormData((prev) => ({ ...prev, postal_code: e.target.value }))
                  }
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                  placeholder="123-4567"
                />
              </div>

              {/* Prefecture */}
              <div className="relative" ref={prefectureDropdownRef}>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  都道府県 (Prefecture)
                </label>
                <button
                  type="button"
                  onClick={() => setShowPrefectureDropdown(!showPrefectureDropdown)}
                  className="w-full px-3 py-2 pr-8 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white bg-white text-left"
                  style={{
                    backgroundImage: `url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M6 8l4 4 4-4'/%3e%3c/svg%3e")`,
                    backgroundPosition: 'right 12px center',
                    backgroundRepeat: 'no-repeat',
                    backgroundSize: '16px',
                  }}
                >
                  {formData.prefecture || '選択してください'}
                </button>
                {showPrefectureDropdown && (
                  <div className="absolute z-10 w-full mt-1 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg shadow-lg max-h-[400px] overflow-y-auto">
                    <button
                      type="button"
                      onClick={() => {
                        setFormData((prev) => ({ ...prev, prefecture: '' }));
                        setShowPrefectureDropdown(false);
                      }}
                      className="w-full px-3 py-2 text-left hover:bg-gray-100 dark:hover:bg-gray-600 text-gray-900 dark:text-white"
                    >
                      選択してください
                    </button>
                    {PREFECTURES.map((prefecture) => (
                      <button
                        key={prefecture.code}
                        type="button"
                        onClick={() => {
                          setFormData((prev) => ({ ...prev, prefecture: prefecture.nameJa }));
                          setShowPrefectureDropdown(false);
                        }}
                        className="w-full px-3 py-2 text-left hover:bg-gray-100 dark:hover:bg-gray-600 text-gray-900 dark:text-white"
                      >
                        {prefecture.nameJa}
                      </button>
                    ))}
                  </div>
                )}
              </div>

              {/* City */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  市区町村 (City)
                </label>
                <input
                  type="text"
                  value={formData.city}
                  onChange={(e) => setFormData((prev) => ({ ...prev, city: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                  placeholder="渋谷区"
                />
              </div>
            </div>

            {/* Description */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Description
              </label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData((prev) => ({ ...prev, description: e.target.value }))}
                rows={4}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white resize-none"
                placeholder="Brief description of the company..."
              />
            </div>

            {/* Subscription Settings Section */}
            <div className="border-t border-gray-200 dark:border-gray-700 pt-6">
              <div className="flex items-center mb-4">
                <Settings className="h-5 w-5 text-gray-500 mr-2" />
                <h3 className="text-lg font-medium text-gray-900 dark:text-white">Subscription Settings</h3>
              </div>

              <div className="space-y-6">
                {/* Subscription Plan Selection */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Subscription Plan
                  </label>
                  <select
                    value={formData.plan_id || ''}
                    onChange={(e) =>
                      setFormData((prev) => ({
                        ...prev,
                        plan_id: e.target.value ? parseInt(e.target.value) : undefined
                      }))
                    }
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                    disabled={loadingPlans}
                  >
                    <option value="">Auto-assign Basic Plan</option>
                    {plans.map((plan) => (
                      <option key={plan.id} value={plan.id}>
                        {plan.display_name} - ¥{plan.price_monthly.toLocaleString()}/month
                      </option>
                    ))}
                  </select>
                  <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                    Select a subscription plan or leave empty to auto-assign Basic Plan
                  </p>
                </div>

                {/* Trial Subscription Toggle */}
                <div className="mb-6">
                  <div className="flex items-center">
                    <input
                      id="is_trial"
                      type="checkbox"
                      checked={formData.is_trial}
                      onChange={(e) =>
                        setFormData((prev) => ({ ...prev, is_trial: e.target.checked }))
                      }
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <label
                      htmlFor="is_trial"
                      className="ml-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
                    >
                      Create as trial subscription
                    </label>
                  </div>
                  <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                    Enable trial period with limited time access to the selected plan
                  </p>
                </div>

                {/* Trial Days - Only show when is_trial is checked */}
                {formData.is_trial && (
                  <div className="bg-amber-50 dark:bg-amber-900/20 p-4 rounded-lg border border-amber-200 dark:border-amber-800">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        <Calendar className="inline h-4 w-4 mr-1" />
                        Trial Period (days)
                      </label>
                      <input
                        type="number"
                        min="1"
                        max="365"
                        value={formData.trial_days}
                        onChange={(e) =>
                          setFormData((prev) => ({
                            ...prev,
                            trial_days: parseInt(e.target.value) || 30
                          }))
                        }
                        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                        placeholder="30"
                      />
                      <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                        Trial will expire after this many days from creation
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Submit Buttons */}
            <div className="flex items-center justify-end space-x-3 pt-6 border-t border-gray-200 dark:border-gray-700">
              <button
                type="button"
                onClick={() => router.back()}
                className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={submitting || !formData.name || !formData.email || !formData.phone}
                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
              >
                <Save className="h-4 w-4" />
                <span>{submitting ? 'Creating...' : 'Create Company'}</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </AppLayout>
  );
}

export default function AddCompanyPage() {
  return (
    <ProtectedRoute allowedRoles={['system_admin']}>
      <AddCompanyContent />
    </ProtectedRoute>
  );
}
