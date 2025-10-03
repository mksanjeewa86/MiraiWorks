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
} from 'lucide-react';
import { companiesApi } from '@/api/companies';
import { Company, CompanyFilters, CompanyType } from '@/types/company';
import AppLayout from '@/components/layout/AppLayout';
import ProtectedRoute from '@/components/auth/ProtectedRoute';

function CompaniesPageContent() {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedCompanies, setSelectedCompanies] = useState<Set<number>>(new Set());
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState<CompanyFilters>({
    page: 1,
    size: 20,
    search: '',
    company_type: undefined,
    is_active: undefined,
    is_demo: undefined,
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
    const newSelected = new Set(selectedCompanies);
    if (newSelected.has(companyId)) {
      newSelected.delete(companyId);
    } else {
      newSelected.add(companyId);
    }
    setSelectedCompanies(newSelected);
  };

  const handleSelectAll = () => {
    if (selectedCompanies.size === companies.length) {
      setSelectedCompanies(new Set());
    } else {
      setSelectedCompanies(new Set(companies.map((company) => company.id)));
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

        <div className="flex items-center justify-between mb-6">
          <div></div>
          <Link
            href="/companies/add"
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center space-x-2"
          >
            <Plus className="h-4 w-4" />
            <span>Add Company</span>
          </Link>
        </div>

        {selectedCompanies.size > 0 && (
          <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4 mb-4">
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
                  const hasInactiveCompanies = selectedCompanyObjects.some(
                    (company) => !company.is_active
                  );
                  const hasActiveCompanies = selectedCompanyObjects.some(
                    (company) => company.is_active
                  );

                  return (
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
                <option value="member">Employer</option>
                <option value="member">Recruiter</option>
              </select>
            </div>

            <div className="min-w-32">
              <select
                value={
                  filters.is_active === undefined && filters.is_demo === undefined
                    ? ''
                    : filters.is_demo === true
                      ? 'demo'
                      : filters.is_active === true
                        ? 'true'
                        : filters.is_active === false
                          ? 'false'
                          : ''
                }
                onChange={(e) => {
                  const value = e.target.value;
                  if (value === 'demo') {
                    setFilters((prev) => ({
                      ...prev,
                      is_demo: true,
                      is_active: undefined,
                      page: 1,
                    }));
                  } else if (value === 'true') {
                    setFilters((prev) => ({
                      ...prev,
                      is_active: true,
                      is_demo: undefined,
                      page: 1,
                    }));
                  } else if (value === 'false') {
                    setFilters((prev) => ({
                      ...prev,
                      is_active: false,
                      is_demo: undefined,
                      page: 1,
                    }));
                  } else {
                    setFilters((prev) => ({
                      ...prev,
                      is_active: undefined,
                      is_demo: undefined,
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
                <option value="demo">Demo</option>
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
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 dark:bg-gray-900">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider w-12">
                      <input
                        type="checkbox"
                        checked={
                          companies.length > 0 && selectedCompanies.size === companies.length
                        }
                        onChange={handleSelectAll}
                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                      />
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Company
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Type
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Contact
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Stats
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider"></th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                  {companies.map((company) => (
                    <tr
                      key={company.id}
                      className={`cursor-pointer transition-colors ${
                        selectedCompanies.has(company.id)
                          ? 'bg-blue-50 dark:bg-blue-900/20 hover:bg-blue-100 dark:hover:bg-blue-900/30'
                          : 'hover:bg-gray-50 dark:hover:bg-gray-700'
                      }`}
                      onClick={() => handleSelectCompany(company.id)}
                    >
                      <td className="px-6 py-4">
                        <input
                          type="checkbox"
                          checked={selectedCompanies.has(company.id)}
                          onChange={() => handleSelectCompany(company.id)}
                          onClick={(e) => e.stopPropagation()}
                          className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                        />
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
                          {company.is_demo && (
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-orange-100 text-orange-800 dark:bg-orange-900/20 dark:text-orange-300">
                              Demo
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4 text-right">
                        <div
                          className="flex items-center justify-end"
                          onClick={(e) => e.stopPropagation()}
                        >
                          <Link
                            href={`/companies/${company.id}/edit`}
                            className="bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700 flex items-center space-x-1"
                          >
                            <Edit className="h-3 w-3" />
                            <span>Edit</span>
                          </Link>
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
