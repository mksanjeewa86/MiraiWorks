'use client';

import { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import {
  Building2,
  Search,
  Plus,
  Edit,
  Trash2,
  Users,
  Briefcase,
  Mail,
  Phone,
  X,
  CheckCircle,
  AlertTriangle,
  Power,
  PowerOff,
  CreditCard,
  Clock,
  ArrowUpRight,
  ArrowDownRight,
  MessageSquare,
} from 'lucide-react';
import { companiesApi } from '@/api/companies';
import { Company, CompanyFilters, CompanyType } from '@/types/company';
import AppLayout from '@/components/layout/AppLayout';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import { useAllPlanChangeRequests, useReviewPlanChangeRequest } from '@/hooks/useSubscription';
import { PlanChangeRequestWithDetails } from '@/types/subscription';
import { Button, Card } from '@/components/ui';

function CompaniesPageContent() {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedCompanies, setSelectedCompanies] = useState<Set<number>>(new Set());
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [viewingCompany, setViewingCompany] = useState<Company | null>(null);
  const [activeTab, setActiveTab] = useState<'companies' | 'subscription-requests'>('companies');

  // Subscription requests management
  const { requests: subscriptionRequests, refetch: refetchRequests } = useAllPlanChangeRequests('pending');
  const { reviewRequest } = useReviewPlanChangeRequest();
  const [selectedRequest, setSelectedRequest] = useState<PlanChangeRequestWithDetails | null>(null);
  const [reviewMessage, setReviewMessage] = useState('');
  const [showReviewModal, setShowReviewModal] = useState(false);
  const [reviewAction, setReviewAction] = useState<'approved' | 'rejected'>('approved');

  // Prevent body scroll on this page
  useEffect(() => {
    document.body.style.overflow = 'hidden';
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, []);

  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState<CompanyFilters>({
    page: 1,
    size: 20,
    search: '',
    company_type: undefined,
    is_active: undefined,
    include_deleted: false,
  });

  const [pagination, setPagination] = useState({
    total: 0,
    pages: 0,
    page: 1,
    size: 20,
  });

  const loadCompanies = useCallback(async () => {
    try {
      setLoading(true);
      const response = await companiesApi.getCompanies(filters);

      if (!response.data) {
        setError('No data received');
        return;
      }

      setCompanies(response.data.companies);
      setPagination({
        total: response.data.total,
        pages: response.data.pages,
        page: response.data.page,
        size: response.data.size,
      });
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load companies');
    } finally {
      setLoading(false);
    }
  }, [filters]);

  // Debounce search term to avoid API calls on every keystroke
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      setFilters((prev) => ({ ...prev, search: searchTerm, page: 1 }));
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [searchTerm]);

  useEffect(() => {
    loadCompanies();
  }, [loadCompanies]);

  // Auto-hide success message after 5 seconds
  useEffect(() => {
    if (successMessage) {
      const timer = setTimeout(() => {
        setSuccessMessage(null);
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [successMessage]);

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(e.target.value);
  };

  const handleTypeFilter = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value;
    setFilters((prev) => ({
      ...prev,
      company_type: value === '' ? undefined : (value as CompanyType),
      page: 1,
    }));
  };

  const handlePageChange = (page: number) => {
    setFilters((prev) => ({ ...prev, page }));
  };

  const handleSelectCompany = (companyId: number) => {
    const company = companies.find((c) => c.id === companyId);
    // Don't allow selection of deleted companies
    if (company?.is_deleted) return;

    const newSelected = new Set(selectedCompanies);
    if (newSelected.has(companyId)) {
      newSelected.delete(companyId);
    } else {
      newSelected.add(companyId);
    }
    setSelectedCompanies(newSelected);
  };

  const handleSelectAll = () => {
    // Only select non-deleted companies
    const selectableCompanies = companies.filter((c) => !c.is_deleted);
    if (selectedCompanies.size === selectableCompanies.length) {
      setSelectedCompanies(new Set());
    } else {
      setSelectedCompanies(new Set(selectableCompanies.map((company) => company.id)));
    }
  };

  const handleBulkActivate = async () => {
    if (selectedCompanies.size === 0) return;

    try {
      const selectedCompanyObjects = companies.filter((company) =>
        selectedCompanies.has(company.id)
      );
      const inactiveCompanies = selectedCompanyObjects.filter((company) => !company.is_active);

      for (const company of inactiveCompanies) {
        await companiesApi.updateCompany(company.id, { is_active: true });
      }

      setSuccessMessage(`Successfully activated ${inactiveCompanies.length} companies`);
      setSelectedCompanies(new Set());
      await loadCompanies();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to activate companies');
    }
  };

  const handleBulkDeactivate = async () => {
    if (selectedCompanies.size === 0) return;

    try {
      const selectedCompanyObjects = companies.filter((company) =>
        selectedCompanies.has(company.id)
      );
      const activeCompanies = selectedCompanyObjects.filter((company) => company.is_active);

      for (const company of activeCompanies) {
        await companiesApi.updateCompany(company.id, { is_active: false });
      }

      setSuccessMessage(`Successfully deactivated ${activeCompanies.length} companies`);
      setSelectedCompanies(new Set());
      await loadCompanies();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to deactivate companies');
    }
  };

  const handleBulkDelete = async () => {
    if (selectedCompanies.size === 0) return;

    const selectedCompanyObjects = companies.filter((company) => selectedCompanies.has(company.id));

    if (
      !confirm(
        `Are you sure you want to delete ${selectedCompanies.size} companies? This action cannot be undone.`
      )
    ) {
      return;
    }

    try {
      for (const company of selectedCompanyObjects) {
        await companiesApi.deleteCompany(company.id);
      }

      setSuccessMessage(`Successfully deleted ${selectedCompanies.size} companies`);
      setSelectedCompanies(new Set());
      await loadCompanies();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete companies');
    }
  };

  const handleReviewSubscriptionRequest = async () => {
    if (!selectedRequest) return;

    try {
      await reviewRequest(selectedRequest.id, reviewAction, reviewMessage);
      setShowReviewModal(false);
      setSelectedRequest(null);
      setReviewMessage('');
      refetchRequests();
      setSuccessMessage(`Request ${reviewAction} successfully`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to review request');
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

  if (loading && companies.length === 0) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center min-h-96">
          <div className="text-gray-600 dark:text-gray-400">Loading companies...</div>
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout>
      <div className="max-w-7xl mx-auto">
        {error && (
          <div className="mb-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-400 px-4 py-3 rounded flex items-center justify-between">
            <div className="flex items-center">
              <AlertTriangle className="h-4 w-4 mr-2" />
              {error}
            </div>
            <button onClick={() => setError(null)} className="text-red-500 hover:text-red-700">
              <X className="h-4 w-4" />
            </button>
          </div>
        )}

        {successMessage && (
          <div className="mb-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 text-green-700 dark:text-green-400 px-4 py-3 rounded flex items-center justify-between">
            <div className="flex items-center">
              <CheckCircle className="h-4 w-4 mr-2" />
              {successMessage}
            </div>
            <button
              onClick={() => setSuccessMessage(null)}
              className="text-green-500 hover:text-green-700"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        )}

        {/* Tab Navigation */}
        <div className="mb-6 mt-6">
          <div className="border-b border-gray-200 dark:border-gray-700">
            <nav className="-mb-px flex space-x-8">
              <button
                onClick={() => setActiveTab('companies')}
                className={`
                  py-4 px-1 border-b-2 font-medium text-sm transition-colors
                  ${activeTab === 'companies'
                    ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
                  }
                `}
              >
                <div className="flex items-center gap-2">
                  <Building2 className="h-5 w-5" />
                  Companies
                </div>
              </button>
              <button
                onClick={() => setActiveTab('subscription-requests')}
                className={`
                  py-4 px-1 border-b-2 font-medium text-sm transition-colors
                  ${activeTab === 'subscription-requests'
                    ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
                  }
                `}
              >
                <div className="flex items-center gap-2">
                  <CreditCard className="h-5 w-5" />
                  Subscription Requests
                  {subscriptionRequests.length > 0 && (
                    <span className="inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-white bg-red-600 rounded-full">
                      {subscriptionRequests.length}
                    </span>
                  )}
                </div>
              </button>
            </nav>
          </div>
        </div>

        {/* Companies Tab Content */}
        {activeTab === 'companies' && (
          <>
            {selectedCompanies.size === 0 && (
              <div className="flex items-center justify-end mb-6 mt-6 min-h-[56px]">
                <Link
                  href="/companies/add"
                  className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center space-x-2"
                >
                  <Plus className="h-4 w-4" />
                  <span>Add Company</span>
                </Link>
              </div>
            )}

        {selectedCompanies.size > 0 && (
          <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4 mb-6 mt-6 min-h-[56px]">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <span className="text-blue-700 dark:text-blue-300 font-medium">
                  {selectedCompanies.size} company(s) selected
                </span>
                <button
                  onClick={() => setSelectedCompanies(new Set())}
                  className="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-200 text-sm"
                >
                  Clear selection
                </button>
              </div>
              <div className="flex items-center space-x-2">
                {(() => {
                  const selectedCompanyObjects = companies.filter((company) =>
                    selectedCompanies.has(company.id)
                  );
                  const hasDeletedCompanies = selectedCompanyObjects.some(
                    (company) => company.is_deleted
                  );
                  const hasInactiveCompanies = selectedCompanyObjects.some(
                    (company) => !company.is_active && !company.is_deleted
                  );
                  const hasActiveCompanies = selectedCompanyObjects.some(
                    (company) => company.is_active && !company.is_deleted
                  );

                  return (
                    <>
                      {!hasDeletedCompanies && (
                        <>
                          {hasInactiveCompanies && (
                            <button
                              onClick={handleBulkActivate}
                              className="bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700 flex items-center space-x-1"
                            >
                              <Power className="h-3 w-3" />
                              <span>Activate</span>
                            </button>
                          )}
                          {hasActiveCompanies && (
                            <button
                              onClick={handleBulkDeactivate}
                              className="bg-orange-600 text-white px-3 py-1 rounded text-sm hover:bg-orange-700 flex items-center space-x-1"
                            >
                              <PowerOff className="h-3 w-3" />
                              <span>Deactivate</span>
                            </button>
                          )}
                          <button
                            onClick={handleBulkDelete}
                            className="bg-red-600 text-white px-3 py-1 rounded text-sm hover:bg-red-700 flex items-center space-x-1"
                          >
                            <Trash2 className="h-3 w-3" />
                            <span>Delete</span>
                          </button>
                        </>
                      )}
                    </>
                  );
                })()}
              </div>
            </div>
          </div>
        )}

        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4 mb-6">
          <div className="flex flex-wrap gap-4 items-center">
            <div className="flex-1 min-w-64">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                <input
                  type="text"
                  placeholder="Search companies..."
                  value={searchTerm}
                  onChange={handleSearchChange}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                />
              </div>
            </div>

            <div className="min-w-40">
              <select
                value={filters.company_type || ''}
                onChange={handleTypeFilter}
                className="w-full px-3 py-2 pr-8 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white appearance-none bg-white"
                style={{
                  backgroundImage: `url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M6 8l4 4 4-4'/%3e%3c/svg%3e")`,
                  backgroundPosition: 'right 12px center',
                  backgroundRepeat: 'no-repeat',
                  backgroundSize: '16px',
                }}
              >
                <option value="">All Types</option>
                <option value="employer">Employer</option>
                <option value="recruiter">Recruiter</option>
              </select>
            </div>

            <div className="min-w-32">
              <select
                value={
                  filters.is_active === undefined
                    ? ''
                    : filters.is_active === true
                      ? 'true'
                      : 'false'
                }
                onChange={(e) => {
                  const value = e.target.value;
                  if (value === 'true') {
                    setFilters((prev) => ({
                      ...prev,
                      is_active: true,
                      page: 1,
                    }));
                  } else if (value === 'false') {
                    setFilters((prev) => ({
                      ...prev,
                      is_active: false,
                      page: 1,
                    }));
                  } else {
                    setFilters((prev) => ({
                      ...prev,
                      is_active: undefined,
                      page: 1,
                    }));
                  }
                }}
                className="w-full px-3 py-2 pr-8 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white appearance-none bg-white"
                style={{
                  backgroundImage: `url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M6 8l4 4 4-4'/%3e%3c/svg%3e")`,
                  backgroundPosition: 'right 12px center',
                  backgroundRepeat: 'no-repeat',
                  backgroundSize: '16px',
                }}
              >
                <option value="">All Status</option>
                <option value="true">Active</option>
                <option value="false">Inactive</option>
              </select>
            </div>

            <div className="min-w-40">
              <div className="flex items-center">
                <input
                  id="include_deleted"
                  type="checkbox"
                  checked={filters.include_deleted || false}
                  onChange={(e) =>
                    setFilters((prev) => ({
                      ...prev,
                      include_deleted: e.target.checked,
                      page: 1,
                    }))
                  }
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label
                  htmlFor="include_deleted"
                  className="ml-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
                >
                  Include deleted companies
                </label>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
          {companies.length === 0 ? (
            <div className="p-8 text-center">
              <Building2 className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                No companies found
              </h3>
              <p className="text-gray-600 dark:text-gray-400 mb-4">
                Get started by creating your first company.
              </p>
              <Link
                href="/companies/add"
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 inline-flex items-center space-x-2"
              >
                <Plus className="h-4 w-4" />
                <span>Add Company</span>
              </Link>
            </div>
          ) : (
            <div
              className="overflow-x-auto"
              style={{ maxHeight: 'calc(100vh - 350px)', overflowY: 'auto' }}
            >
              <table className="w-full">
                <thead className="bg-gray-50 dark:bg-gray-900 sticky top-0 z-10">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider w-12 bg-gray-50 dark:bg-gray-900">
                      <input
                        type="checkbox"
                        checked={
                          companies.filter((c) => !c.is_deleted).length > 0 &&
                          selectedCompanies.size === companies.filter((c) => !c.is_deleted).length
                        }
                        onChange={handleSelectAll}
                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                      />
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider bg-gray-50 dark:bg-gray-900">
                      Company
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider bg-gray-50 dark:bg-gray-900">
                      Type
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider bg-gray-50 dark:bg-gray-900">
                      Contact
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider bg-gray-50 dark:bg-gray-900">
                      Stats
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider bg-gray-50 dark:bg-gray-900">
                      Status
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider bg-gray-50 dark:bg-gray-900"></th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                  {companies.map((company) => (
                    <tr
                      key={company.id}
                      className={`cursor-pointer transition-colors ${
                        company.is_deleted
                          ? selectedCompanies.has(company.id)
                            ? 'bg-red-100 dark:bg-red-900/30 hover:bg-red-200 dark:hover:bg-red-900/40'
                            : 'bg-red-50 dark:bg-red-900/20 hover:bg-red-100 dark:hover:bg-red-900/30'
                          : selectedCompanies.has(company.id)
                            ? 'bg-blue-50 dark:bg-blue-900/20 hover:bg-blue-100 dark:hover:bg-blue-900/30'
                            : 'hover:bg-gray-50 dark:hover:bg-gray-700'
                      }`}
                      onClick={() => handleSelectCompany(company.id)}
                    >
                      <td className="px-6 py-4">
                        {!company.is_deleted && (
                          <input
                            type="checkbox"
                            checked={selectedCompanies.has(company.id)}
                            onChange={() => handleSelectCompany(company.id)}
                            onClick={(e) => e.stopPropagation()}
                            className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                          />
                        )}
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center">
                          <div className="flex-shrink-0">
                            <Building2 className="h-8 w-8 text-gray-400" />
                          </div>
                          <div className="ml-4">
                            <div className="text-sm font-medium text-gray-900 dark:text-white">
                              {company.name}
                            </div>
                            {(company.prefecture || company.city) && (
                              <div className="text-sm text-gray-500 dark:text-gray-400">
                                {company.prefecture}
                                {company.city}
                              </div>
                            )}
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span
                          className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                            company.type === 'employer'
                              ? 'bg-blue-100 text-blue-800'
                              : 'bg-green-100 text-green-800'
                          }`}
                        >
                          {company.type === 'employer' ? 'Employer' : 'Recruiter'}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm text-gray-900 dark:text-white">
                          {company.email && (
                            <div className="flex items-center mb-1">
                              <Mail className="h-3 w-3 mr-1 text-gray-400" />
                              {company.email}
                            </div>
                          )}
                          {company.phone && (
                            <div className="flex items-center">
                              <Phone className="h-3 w-3 mr-1 text-gray-400" />
                              {company.phone}
                            </div>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex space-x-4 text-sm text-gray-500 dark:text-gray-400">
                          <div className="flex items-center">
                            <Users className="h-3 w-3 mr-1" />
                            {company.user_count} users
                          </div>
                          <div className="flex items-center">
                            <Briefcase className="h-3 w-3 mr-1" />
                            {company.job_count} jobs
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex flex-col space-y-1">
                          {company.is_deleted ? (
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-300">
                              Deleted
                            </span>
                          ) : (
                            <span
                              className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                                company.is_active
                                  ? 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-300'
                                  : 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-300'
                              }`}
                            >
                              {company.is_active ? 'Active' : 'Inactive'}
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4 text-right">
                        <div
                          className="flex items-center justify-end space-x-2"
                          onClick={(e) => e.stopPropagation()}
                        >
                          {company.is_deleted ? (
                            <button
                              onClick={() => setViewingCompany(company)}
                              className="bg-gray-600 text-white px-3 py-1 rounded text-sm hover:bg-gray-700 flex items-center space-x-1"
                            >
                              <Building2 className="h-3 w-3" />
                              <span>Details</span>
                            </button>
                          ) : (
                            <>
                              <Link
                                href={`/companies/${company.id}/edit`}
                                className="bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700 flex items-center space-x-1"
                              >
                                <Edit className="h-3 w-3" />
                                <span>Edit</span>
                              </Link>
                              <button
                                onClick={async () => {
                                  if (confirm(`Are you sure you want to delete ${company.name}?`)) {
                                    try {
                                      await companiesApi.deleteCompany(company.id);
                                      setSuccessMessage(`Successfully deleted ${company.name}`);
                                      await loadCompanies();
                                    } catch (err) {
                                      setError(
                                        err instanceof Error
                                          ? err.message
                                          : 'Failed to delete company'
                                      );
                                    }
                                  }
                                }}
                                className="bg-red-600 text-white px-3 py-1 rounded text-sm hover:bg-red-700 flex items-center space-x-1"
                              >
                                <Trash2 className="h-3 w-3" />
                                <span>Delete</span>
                              </button>
                            </>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {pagination.pages > 1 && (
            <div className="bg-white dark:bg-gray-800 px-4 py-3 border-t border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between">
                <div className="text-sm text-gray-700 dark:text-gray-300">
                  Showing {(pagination.page - 1) * pagination.size + 1} to{' '}
                  {Math.min(pagination.page * pagination.size, pagination.total)} of{' '}
                  {pagination.total} results
                </div>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => handlePageChange(pagination.page - 1)}
                    disabled={pagination.page <= 1}
                    className="px-3 py-1 text-sm bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed text-gray-700 dark:text-gray-300"
                  >
                    Previous
                  </button>
                  <span className="text-sm text-gray-700 dark:text-gray-300">
                    Page {pagination.page} of {pagination.pages}
                  </span>
                  <button
                    onClick={() => handlePageChange(pagination.page + 1)}
                    disabled={pagination.page >= pagination.pages}
                    className="px-3 py-1 text-sm bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed text-gray-700 dark:text-gray-300"
                  >
                    Next
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Company Details Modal */}
        {viewingCompany && (
          <div className="fixed inset-0 bg-slate-900/20 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <div className="bg-white dark:bg-gray-800 rounded-3xl border border-slate-200 dark:border-gray-700 shadow-[0_30px_80px_-20px_rgba(15,23,42,0.2)] max-w-2xl w-full max-h-[90vh] overflow-hidden flex flex-col">
              {/* Header */}
              <div className="flex-shrink-0 px-6 pt-6">
                <div className="flex items-start justify-between gap-4">
                  <div className="space-y-3">
                    <div className="flex items-center gap-3">
                      <span className="inline-flex h-10 w-10 items-center justify-center rounded-full bg-blue-100 text-blue-600">
                        <Building2 className="h-5 w-5" />
                      </span>
                      <div>
                        <h2 className="text-xl font-semibold text-slate-900 dark:text-white">
                          Company Details
                        </h2>
                        <p className="text-sm text-slate-500 dark:text-gray-400">
                          View information about this company
                        </p>
                      </div>
                    </div>
                  </div>
                  <button
                    onClick={() => setViewingCompany(null)}
                    className="rounded-lg border border-slate-200 dark:border-gray-600 p-2 text-slate-500 dark:text-gray-400 transition hover:bg-slate-100 dark:hover:bg-gray-700 hover:text-slate-700 dark:hover:text-gray-200"
                  >
                    <X className="h-4 w-4" />
                  </button>
                </div>
              </div>

              {/* Content */}
              <div className="flex-1 overflow-y-auto px-6 py-6 min-h-0">
                <div className="space-y-6">
                  {/* Basic Information Section */}
                  <div className="rounded-2xl border border-slate-200 dark:border-gray-700 bg-slate-50 dark:bg-gray-900/20 p-6">
                    <h3 className="text-sm font-semibold text-slate-700 dark:text-gray-300 mb-4">
                      Basic Information
                    </h3>
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-slate-500 dark:text-gray-400">
                          Company Name
                        </label>
                        <p className="mt-1 text-slate-900 dark:text-white">{viewingCompany.name}</p>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-slate-500 dark:text-gray-400">
                          Type
                        </label>
                        <p className="mt-1">
                          <span
                            className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                              viewingCompany.type === 'employer'
                                ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-300'
                                : 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-300'
                            }`}
                          >
                            {viewingCompany.type === 'employer' ? 'Employer' : 'Recruiter'}
                          </span>
                        </p>
                      </div>

                      {viewingCompany.description && (
                        <div>
                          <label className="block text-sm font-medium text-slate-500 dark:text-gray-400">
                            Description
                          </label>
                          <p className="mt-1 text-slate-900 dark:text-white whitespace-pre-wrap">
                            {viewingCompany.description}
                          </p>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Contact Information Section */}
                  <div className="rounded-2xl border border-slate-200 dark:border-gray-700 bg-slate-50 dark:bg-gray-900/20 p-6">
                    <h3 className="text-sm font-semibold text-slate-700 dark:text-gray-300 mb-4">
                      Contact Information
                    </h3>
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-slate-500 dark:text-gray-400">
                          Email
                        </label>
                        <p className="mt-1 text-slate-900 dark:text-white">
                          {viewingCompany.email}
                        </p>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-slate-500 dark:text-gray-400">
                          Phone
                        </label>
                        <p className="mt-1 text-slate-900 dark:text-white">
                          {viewingCompany.phone}
                        </p>
                      </div>

                      {viewingCompany.website && (
                        <div>
                          <label className="block text-sm font-medium text-slate-500 dark:text-gray-400">
                            Website
                          </label>
                          <p className="mt-1 text-slate-900 dark:text-white">
                            {viewingCompany.website}
                          </p>
                        </div>
                      )}

                      {(viewingCompany.postal_code ||
                        viewingCompany.prefecture ||
                        viewingCompany.city) && (
                        <div>
                          <label className="block text-sm font-medium text-slate-500 dark:text-gray-400">
                            Address
                          </label>
                          <p className="mt-1 text-slate-900 dark:text-white">
                            {viewingCompany.postal_code && `〒${viewingCompany.postal_code} `}
                            {viewingCompany.prefecture}
                            {viewingCompany.city}
                          </p>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Status & Statistics Section */}
                  <div className="rounded-2xl border border-slate-200 dark:border-gray-700 bg-slate-50 dark:bg-gray-900/20 p-6">
                    <h3 className="text-sm font-semibold text-slate-700 dark:text-gray-300 mb-4">
                      Status & Statistics
                    </h3>
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-slate-500 dark:text-gray-400">
                          Status
                        </label>
                        <div className="mt-1 flex flex-wrap gap-2">
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800 dark:bg-gray-900/40 dark:text-gray-300">
                            Deleted
                          </span>
                        </div>
                      </div>

                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <label className="block text-sm font-medium text-slate-500 dark:text-gray-400">
                            Total Users
                          </label>
                          <p className="mt-1 text-slate-900 dark:text-white">
                            {viewingCompany.user_count || 0}
                          </p>
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-slate-500 dark:text-gray-400">
                            Total Jobs
                          </label>
                          <p className="mt-1 text-slate-900 dark:text-white">
                            {viewingCompany.job_count || 0}
                          </p>
                        </div>
                      </div>

                      {viewingCompany.deleted_at && (
                        <div>
                          <label className="block text-sm font-medium text-slate-500 dark:text-gray-400">
                            Deleted At
                          </label>
                          <p className="mt-1 text-slate-900 dark:text-white">
                            {new Date(viewingCompany.deleted_at).toLocaleString()}
                          </p>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>

              {/* Footer */}
              <div className="flex-shrink-0 gap-3 border-t border-slate-200 dark:border-gray-700 bg-white dark:bg-gray-800 px-6 py-4 flex justify-end">
                <button
                  onClick={() => setViewingCompany(null)}
                  className="min-w-[120px] border border-slate-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-slate-600 dark:text-gray-300 hover:bg-slate-100 dark:hover:bg-gray-600 px-4 py-2 rounded-lg transition"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        )}
          </>
        )}

        {/* Subscription Requests Tab Content */}
        {activeTab === 'subscription-requests' && (
          <div className="space-y-6">
            {subscriptionRequests.length === 0 ? (
              <Card className="p-8 text-center">
                <CreditCard className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                  No Pending Requests
                </h3>
                <p className="text-gray-600 dark:text-gray-400">
                  There are no subscription plan change requests awaiting review.
                </p>
              </Card>
            ) : (
              subscriptionRequests.map((request) => {
                const isUpgrade =
                  parseFloat(request.requested_plan?.price_monthly?.toString() || '0') >
                  parseFloat(request.current_plan?.price_monthly?.toString() || '0');

                return (
                  <Card key={request.id} className="p-6">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          {isUpgrade ? (
                            <ArrowUpRight className="h-5 w-5 text-green-600" />
                          ) : (
                            <ArrowDownRight className="h-5 w-5 text-blue-600" />
                          )}
                          <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
                            {request.current_plan?.display_name} → {request.requested_plan?.display_name}
                          </h3>
                        </div>

                        <div className="grid md:grid-cols-2 gap-4 mt-4">
                          <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                            <Building2 className="h-4 w-4" />
                            <span>{request.company_name || 'Unknown Company'}</span>
                          </div>

                          <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                            <Users className="h-4 w-4" />
                            <span>Requested by {request.requester_name || 'Unknown User'}</span>
                          </div>

                          <div className="text-sm text-gray-600 dark:text-gray-400">
                            {new Date(request.created_at).toLocaleDateString('en-US', {
                              year: 'numeric',
                              month: 'long',
                              day: 'numeric',
                            })}
                          </div>

                          {request.current_plan && request.requested_plan && (
                            <div className="text-sm font-medium text-gray-900 dark:text-white">
                              {formatPrice(request.current_plan.price_monthly)} → {formatPrice(request.requested_plan.price_monthly)}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>

                    {request.request_message && (
                      <div className="bg-gray-50 dark:bg-gray-900/20 p-4 rounded-lg mb-4">
                        <div className="flex items-center gap-2 mb-2">
                          <MessageSquare className="h-4 w-4 text-gray-600 dark:text-gray-400" />
                          <p className="text-sm font-medium text-gray-900 dark:text-white">Request Message</p>
                        </div>
                        <p className="text-sm text-gray-700 dark:text-gray-300">
                          {request.request_message}
                        </p>
                      </div>
                    )}

                    <div className="flex gap-2">
                      <Button
                        onClick={() => {
                          setSelectedRequest(request);
                          setReviewAction('approved');
                          setShowReviewModal(true);
                        }}
                        className="flex-1 bg-green-600 hover:bg-green-700"
                      >
                        <CheckCircle className="h-4 w-4 mr-2" />
                        Approve
                      </Button>
                      <Button
                        onClick={() => {
                          setSelectedRequest(request);
                          setReviewAction('rejected');
                          setShowReviewModal(true);
                        }}
                        variant="outline"
                        className="flex-1 text-red-600 border-red-300 hover:bg-red-50 dark:hover:bg-red-900/20"
                      >
                        <X className="h-4 w-4 mr-2" />
                        Reject
                      </Button>
                    </div>
                  </Card>
                );
              })
            )}
          </div>
        )}

        {/* Review Modal */}
        {showReviewModal && selectedRequest && (
          <div className="fixed inset-0 bg-background/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
            <Card className="max-w-md w-full p-6">
              <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">
                {reviewAction === 'approved' ? 'Approve' : 'Reject'} Request
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                {selectedRequest.current_plan?.display_name} → {selectedRequest.requested_plan?.display_name}
              </p>

              <div className="mb-4">
                <label className="block text-sm font-medium mb-2 text-gray-900 dark:text-white">
                  Review Message (optional)
                </label>
                <textarea
                  value={reviewMessage}
                  onChange={(e) => setReviewMessage(e.target.value)}
                  placeholder={
                    reviewAction === 'approved'
                      ? 'Approved. Welcome to the new plan!'
                      : 'Reason for rejection...'
                  }
                  rows={3}
                  className="w-full p-3 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                />
              </div>

              {reviewAction === 'approved' && (
                <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 p-3 rounded-lg mb-4">
                  <p className="text-sm text-green-800 dark:text-green-200">
                    <strong>Note:</strong> Approving this request will immediately change the company's plan to {selectedRequest.requested_plan?.display_name}.
                  </p>
                </div>
              )}

              <div className="flex gap-2">
                <Button
                  onClick={handleReviewSubscriptionRequest}
                  className={`flex-1 ${reviewAction === 'approved' ? 'bg-green-600 hover:bg-green-700' : 'bg-red-600 hover:bg-red-700'}`}
                >
                  {reviewAction === 'approved' ? 'Approve' : 'Reject'}
                </Button>
                <Button
                  variant="outline"
                  onClick={() => {
                    setShowReviewModal(false);
                    setSelectedRequest(null);
                    setReviewMessage('');
                  }}
                >
                  Cancel
                </Button>
              </div>
            </Card>
          </div>
        )}
      </div>
    </AppLayout>
  );
}

export default function CompaniesPage() {
  return (
    <ProtectedRoute allowedRoles={['system_admin']}>
      <CompaniesPageContent />
    </ProtectedRoute>
  );
}
