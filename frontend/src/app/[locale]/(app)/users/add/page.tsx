'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowLeft, Save } from 'lucide-react';
import { usersApi } from '@/api/users';
import { companiesApi } from '@/api/companies';
import { UserCreate } from '@/types/user';
import { Company } from '@/types/company';
import { UserFormData } from '@/types/forms';
import { useToast } from '@/contexts/ToastContext';
import { useAuth } from '@/contexts/AuthContext';
import AppLayout from '@/components/layout/AppLayout';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import { ROUTES } from '@/routes/config';

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
  const [showRoleDropdown, setShowRoleDropdown] = useState(false);
  const [companyHasAdmin, setCompanyHasAdmin] = useState(false);
  const [checkingAdmin, setCheckingAdmin] = useState(false);

  // Get user's role
  const userRole = user?.roles?.[0]?.role?.name;
  const isCompanyAdmin = userRole === 'admin';
  const isSuperAdmin = userRole === 'system_admin';

  // Filter companies based on search
  useEffect(() => {
    if (companySearch.trim() === '') {
      setFilteredCompanies(companies);
    } else {
      const filtered = companies.filter((company) =>
        company.name.toLowerCase().includes(companySearch.toLowerCase())
      );
      setFilteredCompanies(filtered);
    }
  }, [companies, companySearch]);

  // Get super admin's company ID (the company where system_admin user belongs)
  const getSuperAdminCompanyId = () => {
    // Super admin's company is the one where the system_admin user belongs
    // This company cannot have candidates
    if (user?.roles?.[0]?.role?.name === 'system_admin') {
      return user.company_id;
    }
    return null;
  };

  // Get available roles based on user permissions and selected company
  const getAvailableRoles = () => {
    // Candidate role is not available on this page
    // Candidates should be created from the Candidates page

    if (isSuperAdmin) {
      // System admin role is not available for creation
      // Only one system admin exists in the system
      const roles = [
        { value: 'member', label: 'Member' },
      ];

      // Company Admin role is NOT allowed if company already has an admin
      if (!companyHasAdmin) {
        roles.push({ value: 'admin', label: 'Company Admin' });
      }

      return roles;
    } else if (isCompanyAdmin) {
      // Company admins can only create members
      return [
        { value: 'member', label: 'Member' },
      ];
    } else {
      return [
        { value: 'member', label: 'Member' },
      ];
    }
  };

  // Auto-set company and role for company admins
  useEffect(() => {
    if (user && isCompanyAdmin && user.company) {
      // Always set company and role for company admins on initial load
      setFormData((prev) => ({
        ...prev,
        company_id: user.company.id.toString(),
        role: 'member', // Default role for company users
      }));
    }
  }, [user, isCompanyAdmin]);

  // Auto-set role to member if it's the only available option
  useEffect(() => {
    if (formData.company_id) {
      const availableRoles = getAvailableRoles();

      // If only one role is available and it's not already set, auto-select it
      if (availableRoles.length === 1 && !formData.role) {
        setFormData((prev) => ({
          ...prev,
          role: availableRoles[0].value,
        }));
      }
    }
  }, [formData.company_id, companyHasAdmin]);

  // Check if selected company already has an admin
  useEffect(() => {
    const checkCompanyAdmin = async () => {
      if (!formData.company_id) {
        setCompanyHasAdmin(false);
        return;
      }

      const superAdminCompanyId = getSuperAdminCompanyId();
      const selectedCompanyId = parseInt(formData.company_id);

      // Super admin's company can have unlimited admins
      if (superAdminCompanyId && selectedCompanyId === superAdminCompanyId) {
        setCompanyHasAdmin(false);
        return;
      }

      try {
        setCheckingAdmin(true);
        const response = await usersApi.getUsers({
          company_id: selectedCompanyId,
          is_admin: true,
          size: 1, // We only need to know if at least one exists
        });

        // If total > 0, the company already has an admin
        setCompanyHasAdmin((response.data?.total || 0) > 0);
      } catch (err) {
        console.error('Failed to check company admin:', err);
        setCompanyHasAdmin(false);
      } finally {
        setCheckingAdmin(false);
      }
    };

    checkCompanyAdmin();
  }, [formData.company_id, user]);

  // Clear admin role if company already has an admin
  useEffect(() => {
    // If company already has an admin and admin role is selected, clear the role
    if (companyHasAdmin && formData.role === 'admin') {
      setFormData((prev) => ({
        ...prev,
        role: '', // Clear role selection
      }));
    }
  }, [formData.company_id, formData.role, companyHasAdmin]);

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
          if (response.data?.companies) {
            setCompanies(response.data.companies);
          }
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
        message: `${formData.first_name} ${formData.last_name} has been created. An activation email has been sent to ${formData.email}.`,
      });
      router.push(ROUTES.USERS.BASE);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create user');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <AppLayout>
      <div className="max-w-4xl mx-auto px-4 py-6">
        {/* Windows 11 Style Header */}
        <div className="mb-6">
          <button
            onClick={() => router.back()}
            className="mb-4 px-4 py-2 text-sm font-medium rounded-md bg-white/60 hover:bg-white/80 text-gray-800 backdrop-blur-xl border border-gray-200/60 transition-all duration-200 flex items-center gap-2 shadow-sm hover:shadow-md"
            style={{
              fontFamily: 'Segoe UI, sans-serif',
            }}
          >
            <ArrowLeft className="h-4 w-4" />
            <span>Back</span>
          </button>
          <div className="bg-white/70 backdrop-blur-xl rounded-xl p-6 border border-gray-200/60 shadow-lg">
            <h1 className="text-2xl font-semibold text-gray-900 mb-1" style={{ fontFamily: 'Segoe UI, sans-serif' }}>
              Add New User
            </h1>
            <p className="text-sm text-gray-600" style={{ fontFamily: 'Segoe UI, sans-serif' }}>
              Create a new user account in the system
            </p>
          </div>
        </div>

        {/* Windows 11 Style Form Container */}
        <div
          className="bg-white/70 backdrop-blur-xl rounded-xl p-8 border border-gray-200/60 shadow-lg"
          style={{
            fontFamily: 'Segoe UI, sans-serif',
          }}
        >
          {error && (
            <div
              className="mb-6 bg-red-50/80 backdrop-blur-sm rounded-lg px-4 py-3 text-red-800 border border-red-200/60 shadow-sm"
              style={{
                fontFamily: 'Segoe UI, sans-serif',
              }}
            >
              <strong className="font-semibold">⚠ Error: </strong>
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* First Name */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2" style={{ fontFamily: 'Segoe UI, sans-serif' }}>
                  First Name
                </label>
                <input
                  type="text"
                  required
                  value={formData.first_name}
                  onChange={(e) => setFormData((prev) => ({ ...prev, first_name: e.target.value }))}
                  className="w-full px-4 py-2.5 rounded-lg bg-white/80 backdrop-blur-sm border border-gray-300/60 text-gray-900 font-normal focus:outline-none focus:ring-2 focus:ring-blue-500/40 focus:border-blue-500/60 transition-all duration-200 shadow-sm hover:border-gray-400/60"
                  style={{
                    fontFamily: 'Segoe UI, sans-serif',
                  }}
                  placeholder="Enter first name"
                />
              </div>

              {/* Last Name */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2" style={{ fontFamily: 'Segoe UI, sans-serif' }}>
                  Last Name
                </label>
                <input
                  type="text"
                  required
                  value={formData.last_name}
                  onChange={(e) => setFormData((prev) => ({ ...prev, last_name: e.target.value }))}
                  className="w-full px-4 py-2.5 rounded-lg bg-white/80 backdrop-blur-sm border border-gray-300/60 text-gray-900 font-normal focus:outline-none focus:ring-2 focus:ring-blue-500/40 focus:border-blue-500/60 transition-all duration-200 shadow-sm hover:border-gray-400/60"
                  style={{
                    fontFamily: 'Segoe UI, sans-serif',
                  }}
                  placeholder="Enter last name"
                />
              </div>

              {/* Email */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2" style={{ fontFamily: 'Segoe UI, sans-serif' }}>
                  Email Address
                </label>
                <input
                  type="email"
                  required
                  value={formData.email}
                  onChange={(e) => setFormData((prev) => ({ ...prev, email: e.target.value }))}
                  className="w-full px-4 py-2.5 rounded-lg bg-white/80 backdrop-blur-sm border border-gray-300/60 text-gray-900 font-normal focus:outline-none focus:ring-2 focus:ring-blue-500/40 focus:border-blue-500/60 transition-all duration-200 shadow-sm hover:border-gray-400/60"
                  style={{
                    fontFamily: 'Segoe UI, sans-serif',
                  }}
                  placeholder="user@example.com"
                />
              </div>

              {/* Phone */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2" style={{ fontFamily: 'Segoe UI, sans-serif' }}>
                  Phone Number
                </label>
                <input
                  type="tel"
                  value={formData.phone}
                  onChange={(e) => setFormData((prev) => ({ ...prev, phone: e.target.value }))}
                  className="w-full px-4 py-2.5 rounded-lg bg-white/80 backdrop-blur-sm border border-gray-300/60 text-gray-900 font-normal focus:outline-none focus:ring-2 focus:ring-blue-500/40 focus:border-blue-500/60 transition-all duration-200 shadow-sm hover:border-gray-400/60"
                  style={{
                    fontFamily: 'Segoe UI, sans-serif',
                  }}
                  placeholder="03-1234-5678"
                />
              </div>

              {/* Company - Select with Search (Only for Super Admin) */}
              {isSuperAdmin && (
                <div className="md:col-span-2 relative">
                  <label className="block text-sm font-medium text-gray-700 mb-2" style={{ fontFamily: 'Segoe UI, sans-serif' }}>
                    Company
                  </label>
                  <div className="relative">
                    {/* Windows 11 Select button */}
                    <button
                      type="button"
                      onClick={() => setShowCompanyDropdown(!showCompanyDropdown)}
                      className="w-full px-4 py-2.5 rounded-lg bg-white/80 backdrop-blur-sm border border-gray-300/60 text-gray-900 text-left flex items-center justify-between focus:outline-none focus:ring-2 focus:ring-blue-500/40 focus:border-blue-500/60 transition-all duration-200 shadow-sm hover:border-gray-400/60"
                      disabled={loadingCompanies}
                      style={{
                        fontFamily: 'Segoe UI, sans-serif',
                      }}
                    >
                      <span className={formData.company_id ? 'text-gray-900' : 'text-gray-500'}>
                        {formData.company_id
                          ? companies.find((c) => c.id.toString() === formData.company_id)?.name ||
                            'Select a company...'
                          : 'Select a company...'}
                      </span>
                      <svg
                        className="w-5 h-5 text-gray-500"
                        fill="currentColor"
                        viewBox="0 0 20 20"
                      >
                        <path
                          fillRule="evenodd"
                          d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"
                          clipRule="evenodd"
                        />
                      </svg>
                    </button>

                    {loadingCompanies && (
                      <p className="text-sm text-gray-600 mt-2" style={{ fontFamily: 'Segoe UI, sans-serif' }}>
                        Loading companies...
                      </p>
                    )}

                    {/* Windows 11 Dropdown with search */}
                    {showCompanyDropdown && !loadingCompanies && (
                      <div
                        className="absolute z-10 w-full mt-2 bg-white/95 backdrop-blur-xl rounded-lg border border-gray-200/60 shadow-2xl max-h-60 overflow-hidden"
                        style={{
                          fontFamily: 'Segoe UI, sans-serif',
                        }}
                      >
                        {/* Search input */}
                        <div className="p-3 bg-gray-50/80 backdrop-blur-sm border-b border-gray-200/60">
                          <input
                            type="text"
                            value={companySearch}
                            onChange={(e) => setCompanySearch(e.target.value)}
                            placeholder="Search companies..."
                            className="w-full px-3 py-2 rounded-md bg-white border border-gray-300/60 text-gray-900 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/40 focus:border-blue-500/60 transition-all duration-200"
                            style={{
                              fontFamily: 'Segoe UI, sans-serif',
                            }}
                            autoFocus
                          />
                        </div>

                        {/* Company options with Windows 11 hover style */}
                        <div className="max-h-48 overflow-y-auto bg-white/95 backdrop-blur-sm">
                          {filteredCompanies.length > 0 ? (
                            <>
                              {/* Employer Companies */}
                              {filteredCompanies.filter((c) => c.type === 'employer').length >
                                0 && (
                                <>
                                  <div
                                    className="px-4 py-2 text-xs font-semibold text-gray-700 bg-gray-100/80 backdrop-blur-sm sticky top-0"
                                    style={{ fontFamily: 'Segoe UI, sans-serif' }}
                                  >
                                    EMPLOYER
                                  </div>
                                  {filteredCompanies
                                    .filter((c) => c.type === 'employer')
                                    .map((company) => (
                                      <button
                                        key={company.id}
                                        type="button"
                                        onClick={() => {
                                          setFormData((prev) => ({
                                            ...prev,
                                            company_id: company.id.toString(),
                                          }));
                                          setCompanySearch('');
                                          setShowCompanyDropdown(false);
                                        }}
                                        className="w-full text-left px-4 py-2.5 text-gray-900 hover:bg-blue-50/80 hover:text-blue-900 focus:bg-blue-50/80 focus:text-blue-900 focus:outline-none transition-colors duration-150"
                                        style={{ fontFamily: 'Segoe UI, sans-serif' }}
                                      >
                                        <div className="font-normal">{company.name}</div>
                                      </button>
                                    ))}
                                </>
                              )}

                              {/* Recruiter Companies */}
                              {filteredCompanies.filter((c) => c.type === 'recruiter').length >
                                0 && (
                                <>
                                  <div
                                    className="px-4 py-2 text-xs font-semibold text-gray-700 bg-gray-100/80 backdrop-blur-sm sticky top-0"
                                    style={{ fontFamily: 'Segoe UI, sans-serif' }}
                                  >
                                    RECRUITER
                                  </div>
                                  {filteredCompanies
                                    .filter((c) => c.type === 'recruiter')
                                    .map((company) => (
                                      <button
                                        key={company.id}
                                        type="button"
                                        onClick={() => {
                                          setFormData((prev) => ({
                                            ...prev,
                                            company_id: company.id.toString(),
                                          }));
                                          setCompanySearch('');
                                          setShowCompanyDropdown(false);
                                        }}
                                        className="w-full text-left px-4 py-2.5 text-gray-900 hover:bg-blue-50/80 hover:text-blue-900 focus:bg-blue-50/80 focus:text-blue-900 focus:outline-none transition-colors duration-150"
                                        style={{ fontFamily: 'Segoe UI, sans-serif' }}
                                      >
                                        <div className="font-normal">{company.name}</div>
                                      </button>
                                    ))}
                                </>
                              )}
                            </>
                          ) : (
                            <div className="px-4 py-3 text-gray-600 text-sm" style={{ fontFamily: 'Segoe UI, sans-serif' }}>
                              No companies found
                            </div>
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

            {/* Company Info for Company Admin - Windows 11 Info Box */}
            {isCompanyAdmin && user?.company && (
              <div
                className="md:col-span-2 bg-blue-50/60 backdrop-blur-sm rounded-lg border border-blue-200/60 p-4 shadow-sm"
                style={{
                  fontFamily: 'Segoe UI, sans-serif',
                }}
              >
                <p className="text-sm text-gray-700 font-normal">
                  Creating user for:{' '}
                  <strong className="font-semibold text-gray-900">{user.company.name}</strong>
                </p>
                <p className="text-xs text-gray-600 mt-1">
                  New users will be assigned the member role
                </p>
              </div>
            )}

            {/* User Role Selection (Only for Super Admin and when multiple roles available) */}
            {isSuperAdmin && formData.company_id && (() => {
              const availableRoles = getAvailableRoles();

              // If only one role is available, show it as read-only info
              if (availableRoles.length === 1) {
                return (
                  <div
                    className="bg-blue-50/60 backdrop-blur-sm rounded-lg border border-blue-200/60 p-4 shadow-sm"
                    style={{
                      fontFamily: 'Segoe UI, sans-serif',
                    }}
                  >
                    <p className="text-sm text-gray-700 font-normal">
                      User will be assigned the <strong className="font-semibold text-gray-900">{availableRoles[0].label}</strong> role
                    </p>
                    <p className="text-xs text-gray-600 mt-1">
                      To create candidate users, please use the Candidates page.
                    </p>
                  </div>
                );
              }

              // If multiple roles available, show dropdown
              return (
                <div className="relative">
                  <label className="block text-sm font-medium text-gray-700 mb-2" style={{ fontFamily: 'Segoe UI, sans-serif' }}>
                    User Role
                  </label>
                  <div className="relative">
                    {/* Windows 11 Select button */}
                    <button
                      type="button"
                      onClick={() => setShowRoleDropdown(!showRoleDropdown)}
                      className="w-full px-4 py-2.5 rounded-lg bg-white/80 backdrop-blur-sm border border-gray-300/60 text-gray-900 text-left flex items-center justify-between focus:outline-none focus:ring-2 focus:ring-blue-500/40 focus:border-blue-500/60 transition-all duration-200 shadow-sm hover:border-gray-400/60"
                      style={{
                        fontFamily: 'Segoe UI, sans-serif',
                      }}
                    >
                      <span className={formData.role ? 'text-gray-900' : 'text-gray-500'}>
                        {formData.role
                          ? availableRoles.find((r) => r.value === formData.role)?.label ||
                            'Select a role...'
                          : 'Select a role...'}
                      </span>
                      <svg
                        className="w-5 h-5 text-gray-500"
                        fill="currentColor"
                        viewBox="0 0 20 20"
                      >
                        <path
                          fillRule="evenodd"
                          d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"
                          clipRule="evenodd"
                        />
                      </svg>
                    </button>

                    {/* Windows 11 Dropdown */}
                    {showRoleDropdown && (
                      <div
                        className="absolute z-10 w-full mt-2 bg-white/95 backdrop-blur-xl rounded-lg border border-gray-200/60 shadow-2xl max-h-60 overflow-hidden"
                        style={{
                          fontFamily: 'Segoe UI, sans-serif',
                        }}
                      >
                        <div className="max-h-48 overflow-y-auto bg-white/95 backdrop-blur-sm">
                          {availableRoles.map((role) => (
                            <button
                              key={role.value}
                              type="button"
                              onClick={() => {
                                setFormData((prev) => ({ ...prev, role: role.value }));
                                setShowRoleDropdown(false);
                              }}
                              className="w-full text-left px-4 py-2.5 text-gray-900 hover:bg-blue-50/80 hover:text-blue-900 focus:bg-blue-50/80 focus:text-blue-900 focus:outline-none transition-colors duration-150"
                              style={{ fontFamily: 'Segoe UI, sans-serif' }}
                            >
                              <div className="font-normal">{role.label}</div>
                            </button>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Click outside to close dropdown */}
                  {showRoleDropdown && (
                    <div className="fixed inset-0 z-5" onClick={() => setShowRoleDropdown(false)} />
                  )}

                  <div className="mt-3 space-y-1">
                    <p className="text-xs text-gray-600" style={{ fontFamily: 'Segoe UI, sans-serif' }}>
                      Role determines the user&apos;s permissions and access level
                    </p>
                    <p className="text-xs text-gray-600" style={{ fontFamily: 'Segoe UI, sans-serif' }}>
                      <strong className="font-semibold">Note:</strong> To create candidate users, please use the Candidates page.
                    </p>
                  </div>
                </div>
              );
            })()}

            {/* Windows 11 Submit Buttons */}
            <div
              className="flex items-center justify-end space-x-3 pt-6 border-t border-gray-200/60"
            >
              <button
                type="button"
                onClick={() => router.back()}
                className="px-5 py-2.5 text-sm font-medium text-gray-700 bg-white/80 backdrop-blur-sm rounded-lg border border-gray-300/60 hover:bg-gray-50/80 hover:border-gray-400/60 transition-all duration-200 shadow-sm hover:shadow-md"
                style={{
                  fontFamily: 'Segoe UI, sans-serif',
                }}
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={
                  submitting ||
                  !formData.first_name ||
                  !formData.last_name ||
                  !formData.email ||
                  !formData.company_id ||
                  !formData.role
                }
                className="px-5 py-2.5 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-blue-600 flex items-center space-x-2 rounded-lg border border-blue-700/40 transition-all duration-200 shadow-md hover:shadow-lg"
                style={{
                  fontFamily: 'Segoe UI, sans-serif',
                }}
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
