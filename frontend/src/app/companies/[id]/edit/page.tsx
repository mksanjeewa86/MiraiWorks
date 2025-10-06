'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { ArrowLeft, Save, Calendar, Settings, Trash2, UserX } from 'lucide-react';
import { PREFECTURES } from '@/utils/prefectures';
import { companiesApi } from '@/api/companies';
import { Company, CompanyType, CompanyUpdate } from '@/types/company';
import { CompanyFormData } from '@/types/forms';
import { useToast } from '@/contexts/ToastContext';
import AppLayout from '@/components/layout/AppLayout';
import ProtectedRoute from '@/components/auth/ProtectedRoute';

function EditCompanyContent() {
  const router = useRouter();
  const params = useParams();
  const { showToast } = useToast();
  const [showPrefectureDropdown, setShowPrefectureDropdown] = useState(false);
  const prefectureDropdownRef = useRef<HTMLDivElement>(null);
  const [company, setCompany] = useState<Company | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    type: 'recruiter' as CompanyType,
    email: '',
    phone: '',
    website: '',
    postal_code: '',
    prefecture: '',
    city: '',
    description: '',
  });
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [showDeactivateModal, setShowDeactivateModal] = useState(false);

  const companyId = params?.id as string;

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

  useEffect(() => {
    const loadCompany = async () => {
      if (!companyId) return;

      try {
        setLoading(true);
        const response = await companiesApi.getCompany(parseInt(companyId));
        const companyData = response.data;

        if (!companyData) {
          setError('Company not found');
          return;
        }

        setCompany(companyData);
        setFormData({
          name: companyData.name,
          type: companyData.type,
          email: companyData.email,
          phone: companyData.phone || '',
          website: companyData.website || '',
          postal_code: companyData.postal_code || '',
          prefecture: companyData.prefecture || '',
          city: companyData.city || '',
          description: companyData.description || '',
        });
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load company');
      } finally {
        setLoading(false);
      }
    };

    loadCompany();
  }, [companyId]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (submitting || !company) return;

    try {
      setSubmitting(true);
      setError(null);

      const updateData: CompanyUpdate = {
        name: formData.name,
        type: formData.type,
        email: formData.email,
        phone: formData.phone || undefined,
        website: formData.website || undefined,
        postal_code: formData.postal_code || undefined,
        prefecture: formData.prefecture || undefined,
        city: formData.city || undefined,
        description: formData.description || undefined,
      };

      await companiesApi.updateCompany(company.id, updateData);
      showToast({
        type: 'success',
        title: 'Company updated successfully!',
        message: `${formData.name} has been updated.`,
      });
      router.push('/companies');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update company');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDeactivate = async () => {
    if (!company) return;

    try {
      setSubmitting(true);
      // Assuming there's a deactivate endpoint
      await companiesApi.updateCompany(company.id, { is_active: false });
      showToast({
        type: 'success',
        title: 'Company deactivated',
        message: `${company.name} has been deactivated.`,
      });
      router.push('/companies');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to deactivate company');
      setSubmitting(false);
    }
    setShowDeactivateModal(false);
  };

  const handleDelete = async () => {
    if (!company) return;

    try {
      setSubmitting(true);
      await companiesApi.deleteCompany(company.id);
      showToast({
        type: 'success',
        title: 'Company deleted',
        message: `${company.name} has been permanently deleted.`,
      });
      router.push('/companies');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete company');
      setSubmitting(false);
    }
    setShowDeleteModal(false);
  };

  if (loading) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center min-h-96">
          <div className="text-gray-600 dark:text-gray-400">Loading company...</div>
        </div>
      </AppLayout>
    );
  }

  if (!company) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center min-h-96">
          <div className="text-center">
            <div className="text-red-600 dark:text-red-400 mb-4">Company not found</div>
            <button
              onClick={() => router.push('/companies')}
              className="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300"
            >
              Back to companies
            </button>
          </div>
        </div>
      </AppLayout>
    );
  }

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
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Edit Company</h1>
            <p className="text-gray-600 dark:text-gray-400">Update {company.name} information</p>
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
                  disabled
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-gray-100 dark:bg-gray-600 text-gray-500 dark:text-gray-400 cursor-not-allowed"
                  placeholder="contact@company.com"
                />
                <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                  Email cannot be changed
                </p>
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
                  Phone
                </label>
                <input
                  type="tel"
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
                  onChange={(e) => {
                    let value = e.target.value.replace(/[^0-9]/g, '');
                    if (value.length > 3) {
                      value = value.slice(0, 3) + '-' + value.slice(3, 7);
                    }
                    setFormData((prev) => ({ ...prev, postal_code: value }));
                  }}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                  placeholder="123-4567"
                  maxLength={8}
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
                        {prefecture.nameJa} ({prefecture.nameEn})
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

            {/* Action Buttons */}
            <div className="flex items-center justify-between pt-6 border-t border-gray-200 dark:border-gray-700">
              {/* Danger Actions */}
              <div className="flex space-x-3">
                <button
                  type="button"
                  onClick={() => setShowDeactivateModal(true)}
                  className="px-4 py-2 text-sm font-medium text-orange-700 dark:text-orange-300 bg-orange-50 dark:bg-orange-900/20 border border-orange-300 dark:border-orange-600 rounded-lg hover:bg-orange-100 dark:hover:bg-orange-900/30 flex items-center space-x-2"
                >
                  <UserX className="h-4 w-4" />
                  <span>Deactivate</span>
                </button>
                <button
                  type="button"
                  onClick={() => setShowDeleteModal(true)}
                  className="px-4 py-2 text-sm font-medium text-red-700 dark:text-red-300 bg-red-50 dark:bg-red-900/20 border border-red-300 dark:border-red-600 rounded-lg hover:bg-red-100 dark:hover:bg-red-900/30 flex items-center space-x-2"
                >
                  <Trash2 className="h-4 w-4" />
                  <span>Delete</span>
                </button>
              </div>

              {/* Main Actions */}
              <div className="flex space-x-3">
                <button
                  type="button"
                  onClick={() => router.back()}
                  className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting || !formData.name || !formData.email}
                  className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
                >
                  <Save className="h-4 w-4" />
                  <span>{submitting ? 'Updating...' : 'Update Company'}</span>
                </button>
              </div>
            </div>
          </form>
        </div>

        {/* Delete Modal */}
        {showDeleteModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-md mx-4">
              <div className="flex items-center mb-4">
                <Trash2 className="h-6 w-6 text-red-500 mr-3" />
                <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                  Delete Company
                </h3>
              </div>
              <p className="text-gray-600 dark:text-gray-400 mb-6">
                Are you sure you want to permanently delete <strong>{company?.name}</strong>? This
                action cannot be undone and will remove all associated data.
              </p>
              <div className="flex justify-end space-x-3">
                <button
                  onClick={() => setShowDeleteModal(false)}
                  disabled={submitting}
                  className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700"
                >
                  Cancel
                </button>
                <button
                  onClick={handleDelete}
                  disabled={submitting}
                  className="px-4 py-2 text-sm font-medium text-white bg-red-600 border border-transparent rounded-lg hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {submitting ? 'Deleting...' : 'Delete Company'}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Deactivate Modal */}
        {showDeactivateModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-md mx-4">
              <div className="flex items-center mb-4">
                <UserX className="h-6 w-6 text-orange-500 mr-3" />
                <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                  Deactivate Company
                </h3>
              </div>
              <p className="text-gray-600 dark:text-gray-400 mb-6">
                Are you sure you want to deactivate <strong>{company?.name}</strong>? The company
                will no longer be able to access the system but data will be preserved.
              </p>
              <div className="flex justify-end space-x-3">
                <button
                  onClick={() => setShowDeactivateModal(false)}
                  disabled={submitting}
                  className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700"
                >
                  Cancel
                </button>
                <button
                  onClick={handleDeactivate}
                  disabled={submitting}
                  className="px-4 py-2 text-sm font-medium text-white bg-orange-600 border border-transparent rounded-lg hover:bg-orange-700 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {submitting ? 'Deactivating...' : 'Deactivate Company'}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </AppLayout>
  );
}

export default function EditCompanyPage() {
  return (
    <ProtectedRoute allowedRoles={['system_admin']}>
      <EditCompanyContent />
    </ProtectedRoute>
  );
}
