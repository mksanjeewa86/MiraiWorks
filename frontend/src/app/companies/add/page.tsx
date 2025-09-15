'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowLeft, Save, Calendar, Settings } from 'lucide-react';
import { companiesApi } from '@/api/companiesApi';
import { CompanyCreate, CompanyType } from '@/types/company';
import { CompanyFormData } from '@/types/forms';
import { useToast } from '@/contexts/ToastContext';
import AppLayout from '@/components/layout/AppLayout';

const emptyFormData: CompanyFormData = {
  name: '',
  type: 'employer',
  email: '',
  phone: '',
  website: '',
  postal_code: '',
  prefecture: '',
  city: '',
  description: '',
  is_demo: false,
  demo_end_date: '',
  demo_features: '',
  demo_notes: '',
};

export default function AddCompanyPage() {
  const router = useRouter();
  const { showToast } = useToast();
  const [formData, setFormData] = useState<CompanyFormData>(emptyFormData);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

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
        is_demo: formData.is_demo,
        demo_end_date: formData.is_demo && formData.demo_end_date ? formData.demo_end_date : undefined,
        demo_features: formData.is_demo && formData.demo_features ? formData.demo_features : undefined,
        demo_notes: formData.is_demo && formData.demo_notes ? formData.demo_notes : undefined,
      };

      await companiesApi.createCompany(companyData);
      showToast({
        type: 'success',
        title: 'Company created successfully!',
        message: `${formData.name} has been created. An activation email will be sent to ${formData.email}.`
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
                onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
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
                onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
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
                onChange={(e) => setFormData(prev => ({ ...prev, type: e.target.value as CompanyType }))}
                className="w-full px-3 py-2 pr-8 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
              >
                <option value="employer">Employer</option>
                <option value="recruiter">Recruiter</option>
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
                onChange={(e) => setFormData(prev => ({ ...prev, phone: e.target.value }))}
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
                onChange={(e) => setFormData(prev => ({ ...prev, website: e.target.value }))}
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
                onChange={(e) => setFormData(prev => ({ ...prev, postal_code: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                placeholder="123-4567"
              />
            </div>

            {/* Prefecture */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                都道府県 (Prefecture)
              </label>
              <input
                type="text"
                value={formData.prefecture}
                onChange={(e) => setFormData(prev => ({ ...prev, prefecture: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                placeholder="東京都"
              />
            </div>

            {/* City */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                市区町村 (City)
              </label>
              <input
                type="text"
                value={formData.city}
                onChange={(e) => setFormData(prev => ({ ...prev, city: e.target.value }))}
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
              onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
              rows={4}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white resize-none"
              placeholder="Brief description of the company..."
            />
          </div>

          {/* Demo Settings Section */}
          <div className="border-t border-gray-200 dark:border-gray-700 pt-6">
            <div className="flex items-center mb-4">
              <Settings className="h-5 w-5 text-gray-500 mr-2" />
              <h3 className="text-lg font-medium text-gray-900 dark:text-white">Demo Settings</h3>
            </div>

            {/* Demo Company Toggle */}
            <div className="mb-6">
              <div className="flex items-center">
                <input
                  id="is_demo"
                  type="checkbox"
                  checked={formData.is_demo}
                  onChange={(e) => setFormData(prev => ({ ...prev, is_demo: e.target.checked }))}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label htmlFor="is_demo" className="ml-2 block text-sm font-medium text-gray-700 dark:text-gray-300">
                  This is a demo company
                </label>
              </div>
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                Enable demo features and set expiration for this company
              </p>
            </div>

            {/* Demo Fields - Only show when is_demo is checked */}
            {formData.is_demo && (
              <div className="space-y-6 bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg border border-blue-200 dark:border-blue-800">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Demo End Date */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      <Calendar className="inline h-4 w-4 mr-1" />
                      Demo End Date
                    </label>
                    <input
                      type="date"
                      value={formData.demo_end_date}
                      onChange={(e) => setFormData(prev => ({ ...prev, demo_end_date: e.target.value }))}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                      min={new Date().toISOString().split('T')[0]}
                    />
                  </div>

                  {/* Demo Features */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Demo Features
                    </label>
                    <input
                      type="text"
                      value={formData.demo_features}
                      onChange={(e) => setFormData(prev => ({ ...prev, demo_features: e.target.value }))}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                      placeholder="e.g., Basic Plan, 50 job posts, 100 applications"
                    />
                  </div>
                </div>

                {/* Demo Notes */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Demo Notes
                  </label>
                  <textarea
                    value={formData.demo_notes}
                    onChange={(e) => setFormData(prev => ({ ...prev, demo_notes: e.target.value }))}
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white resize-none"
                    placeholder="Internal notes about this demo account..."
                  />
                </div>
              </div>
            )}
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