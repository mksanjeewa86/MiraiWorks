'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowLeft, Save } from 'lucide-react';
import { usersApi } from '@/api/usersApi';
import { companiesApi } from '@/api/companiesApi';
import { UserCreate } from '@/types/user';
import { Company } from '@/types/company';
import { UserFormData } from '@/types/forms';
import { useToast } from '@/contexts/ToastContext';
import { useAuth } from '@/contexts/AuthContext';
import AppLayout from '@/components/layout/AppLayout';
import ProtectedRoute from '@/components/auth/ProtectedRoute';

const emptyFormData: UserFormData = {
  email: '',
  first_name: '',
  last_name: '',
  phone: '',
  company_id: '',
  role: '', // Will be set based on company type
  is_admin: false,
  require_2fa: false,
};

function AddUserPageContent() {
  const router = useRouter();
  const { showToast } = useToast();
  const { user } = useAuth();
  const [formData, setFormData] = useState<UserFormData>(emptyFormData);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [companies, setCompanies] = useState<Company[]>([]);
  const [loadingCompanies, setLoadingCompanies] = useState(true);
  const [companySearch, setCompanySearch] = useState('');
  const [showCompanyDropdown, setShowCompanyDropdown] = useState(false);
  const [filteredCompanies, setFilteredCompanies] = useState<Company[]>([]);

  // Get user's role
  const userRole = user?.roles?.[0]?.role?.name;
  const isCompanyAdmin = userRole === 'company_admin';
  const isSuperAdmin = userRole === 'super_admin';


  // Filter companies based on search
  useEffect(() => {
    if (companySearch.trim() === '') {
      setFilteredCompanies(companies);
    } else {
      const filtered = companies.filter(company =>
        company.name.toLowerCase().includes(companySearch.toLowerCase())
      );
      setFilteredCompanies(filtered);
    }
  }, [companies, companySearch]);

  // Get available roles based on user permissions
  const getAvailableRoles = () => {
    if (isSuperAdmin) {
      return [
        { value: 'candidate', label: 'Candidate' },
        { value: 'recruiter', label: 'Recruiter' },
        { value: 'employer', label: 'Employer' },
        { value: 'company_admin', label: 'Company Admin' },
        { value: 'super_admin', label: 'Super Admin' }
      ];
    } else if (isCompanyAdmin) {
      return [
        { value: 'candidate', label: 'Candidate' },
        { value: 'recruiter', label: 'Recruiter' },
        { value: 'employer', label: 'Employer' },
        { value: 'company_admin', label: 'Company Admin' }
      ];
    } else {
      return [
        { value: 'candidate', label: 'Candidate' },
        { value: 'recruiter', label: 'Recruiter' },
        { value: 'employer', label: 'Employer' }
      ];
    }
  };

  // Auto-set company and role for company admins
  useEffect(() => {
    if (user && isCompanyAdmin && user.company) {
      // Always set company and role for company admins on initial load
      setFormData(prev => ({
        ...prev,
        company_id: user.company.id.toString(),
        role: user.company.type === 'employer' ? 'employer' : 'recruiter'
      }));
    }
  }, [user, isCompanyAdmin]);

  // Auto-set default role based on selected company type (for super admins)
  useEffect(() => {
    if (isSuperAdmin && formData.company_id && !formData.role) {
      const selectedCompany = companies.find(c => c.id.toString() === formData.company_id);
      if (selectedCompany) {
        const role = selectedCompany.type === 'employer' ? 'employer' : 'recruiter';
        setFormData(prev => ({ ...prev, role }));
      }
    }
  }, [formData.company_id, companies, isSuperAdmin]);

  // Load companies for the dropdown
  useEffect(() => {
    const loadCompanies = async () => {
      try {
        setLoadingCompanies(true);

        if (isCompanyAdmin && user?.company) {
          // Company admin can only see their own company
          setCompanies([user.company]);
        } else if (isSuperAdmin) {
          // Super admin can see all companies
          const response = await companiesApi.getCompanies({ size: 100 });
          setCompanies(response.data.companies);
        } else {
          // Other roles - no company selection needed
          setCompanies([]);
        }
      } catch (err) {
        console.error('Failed to load companies:', err);
        // If API fails and user is company admin, fallback to their company
        if (isCompanyAdmin && user?.company) {
          setCompanies([user.company]);
        }
      } finally {
        setLoadingCompanies(false);
      }
    };

    // Only load companies if user data is available
    if (user) {
      loadCompanies();
    }
  }, [user, isCompanyAdmin, isSuperAdmin]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (submitting) return;

    try {
      setSubmitting(true);
      setError(null);

      const userData: UserCreate = {
        email: formData.email,
        first_name: formData.first_name,
        last_name: formData.last_name,
        phone: formData.phone || undefined,
        company_id: formData.company_id ? parseInt(formData.company_id) : undefined,
        roles: [formData.role], // Convert single role to array for API
        is_admin: false, // Users created here are never admins
        require_2fa: false, // Regular users don't need 2FA
      };

      await usersApi.createUser(userData);
      showToast({
        type: 'success',
        title: 'User created successfully!',
        message: `${formData.first_name} ${formData.last_name} has been created. An activation email has been sent to ${formData.email}.`
      });
      router.push('/users');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create user');
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
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Add User</h1>
            <p className="text-gray-600 dark:text-gray-400">Create a new user in the system</p>
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
              {/* First Name */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  First Name *
                </label>
                <input
                  type="text"
                  required
                  value={formData.first_name}
                  onChange={(e) => setFormData(prev => ({ ...prev, first_name: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                  placeholder="Enter first name"
                />
              </div>

              {/* Last Name */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Last Name *
                </label>
                <input
                  type="text"
                  required
                  value={formData.last_name}
                  onChange={(e) => setFormData(prev => ({ ...prev, last_name: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                  placeholder="Enter last name"
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
                  placeholder="user@example.com"
                />
              </div>

              {/* Phone */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Phone
                </label>
                <input
                  type="tel"
                  value={formData.phone}
                  onChange={(e) => setFormData(prev => ({ ...prev, phone: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                  placeholder="03-1234-5678"
                />
              </div>

              {/* Company - Select with Search (Only for Super Admin) */}
              {isSuperAdmin && (
              <div className="md:col-span-2 relative">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Company
                </label>
                <div className="relative">
                  {/* Select-like button */}
                  <button
                    type="button"
                    onClick={() => setShowCompanyDropdown(!showCompanyDropdown)}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white text-left flex items-center justify-between"
                    disabled={loadingCompanies}
                  >
                    <span className={formData.company_id ? 'text-gray-900 dark:text-white' : 'text-gray-500'}>
                      {formData.company_id
                        ? companies.find(c => c.id.toString() === formData.company_id)?.name || 'Select a company...'
                        : 'Select a company...'
                      }
                    </span>
                    <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </button>

                  {loadingCompanies && (
                    <p className="text-sm text-gray-500 mt-1">Loading companies...</p>
                  )}

                  {/* Dropdown with search */}
                  {showCompanyDropdown && !loadingCompanies && (
                    <div className="absolute z-10 w-full mt-1 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg shadow-lg max-h-60 overflow-hidden">
                      {/* Search input as first option */}
                      <div className="p-2 border-b border-gray-200 dark:border-gray-600">
                        <input
                          type="text"
                          value={companySearch}
                          onChange={(e) => setCompanySearch(e.target.value)}
                          placeholder="Search companies..."
                          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white text-sm"
                          autoFocus
                        />
                      </div>

                      {/* Company options */}
                      <div className="max-h-48 overflow-y-auto">
                        {filteredCompanies.length > 0 ? (
                          filteredCompanies.map((company) => (
                            <button
                              key={company.id}
                              type="button"
                              onClick={() => {
                                setFormData(prev => ({ ...prev, company_id: company.id.toString() }));
                                setCompanySearch('');
                                setShowCompanyDropdown(false);
                              }}
                              className="w-full text-left px-3 py-2 hover:bg-gray-100 dark:hover:bg-gray-700 focus:bg-gray-100 dark:focus:bg-gray-700 focus:outline-none"
                            >
                              <div className="font-medium">{company.name}</div>
                              <div className="text-sm text-gray-500">({company.type})</div>
                            </button>
                          ))
                        ) : (
                          <div className="px-3 py-2 text-gray-500 text-sm">No companies found</div>
                        )}
                      </div>
                    </div>
                  )}
                </div>

                {/* Click outside to close dropdown */}
                {showCompanyDropdown && (
                  <div
                    className="fixed inset-0 z-5"
                    onClick={() => setShowCompanyDropdown(false)}
                  />
                )}
              </div>
              )}
            </div>

            {/* Company Info for Company Admin */}
            {isCompanyAdmin && user?.company && (
              <div className="md:col-span-2 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Creating user for: <strong className="text-gray-900 dark:text-white">{user.company.name}</strong>
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                  New users will be assigned the {user.company.type === 'employer' ? 'employer' : 'recruiter'} role
                </p>
              </div>
            )}

            {/* User Role Selection (Only for Super Admin) */}
            {isSuperAdmin && formData.company_id && (
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  User Role <span className="text-red-500">*</span>
                </label>
                <select
                  required
                  value={formData.role}
                  onChange={(e) => setFormData(prev => ({ ...prev, role: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                >
                  <option value="">Select a role...</option>
                  {getAvailableRoles().map(role => (
                    <option key={role.value} value={role.value}>
                      {role.label}
                    </option>
                  ))}
                </select>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  Role determines the user&apos;s permissions and access level
                </p>
              </div>
            )}



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
                disabled={submitting || !formData.first_name || !formData.last_name || !formData.email || !formData.company_id || !formData.role}
                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
              >
                <Save className="h-4 w-4" />
                <span>{submitting ? 'Creating...' : 'Create User'}</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </AppLayout>
  );
}

export default function AddUserPage() {
  return (
    <ProtectedRoute>
      <AddUserPageContent />
    </ProtectedRoute>
  );
}