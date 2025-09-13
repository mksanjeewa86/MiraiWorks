'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import {
  Users,
  Search,
  Plus,
  Edit,
  Trash2,
  Mail,
  Phone,
  Building2,
  Shield,
  ShieldCheck,
  UserX,
  UserCheck,
  Key,
  RefreshCw,
  X,
  Power,
  PowerOff,
  AlertTriangle,
  CheckCircle,
  Mail as MailIcon,
} from 'lucide-react';
import { usersApi } from '@/api/usersApi';
import { User, UserFilters } from '@/types/user';
import AppLayout from '@/components/layout/AppLayout';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import ConfirmationModal from '@/components/ui/ConfirmationModal';

function UsersPageContent() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedUsers, setSelectedUsers] = useState<Set<number>>(new Set());
  const [confirmationModal, setConfirmationModal] = useState<{
    isOpen: boolean;
    title: string;
    message: string;
    onConfirm: () => void;
    confirmText?: string;
    confirmButtonClass?: string;
    icon?: React.ReactNode;
  }>({ isOpen: false, title: '', message: '', onConfirm: () => {} });
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState<UserFilters>({
    page: 1,
    size: 20,
    search: '',
    company_id: undefined,
    is_active: undefined,
    is_admin: undefined,
    role: undefined,
  });

  const [pagination, setPagination] = useState({
    total: 0,
    pages: 0,
    page: 1,
    size: 20,
  });

  const loadUsers = async () => {
    try {
      setLoading(true);
      const response = await usersApi.getUsers(filters);
      setUsers(response.data.users);
      setPagination({
        total: response.data.total,
        pages: response.data.pages,
        page: response.data.page,
        size: response.data.size,
      });
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load users');
    } finally {
      setLoading(false);
    }
  };

  // Debounce search term to avoid API calls on every keystroke
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      setFilters(prev => ({ ...prev, search: searchTerm, page: 1 }));
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [searchTerm]);

  useEffect(() => {
    loadUsers();
  }, [filters]);

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(e.target.value);
  };

  const handleActiveFilter = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value;
    setFilters(prev => ({ 
      ...prev, 
      is_active: value === '' ? undefined : value === 'true',
      page: 1 
    }));
  };

  const handleAdminFilter = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value;
    setFilters(prev => ({ 
      ...prev, 
      is_admin: value === '' ? undefined : value === 'true',
      page: 1 
    }));
  };

  const handleRoleFilter = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value;
    setFilters(prev => ({ 
      ...prev, 
      role: value === '' ? undefined : value,
      page: 1 
    }));
  };

  const handlePageChange = (page: number) => {
    setFilters(prev => ({ ...prev, page }));
  };


  const handleSelectUser = (userId: number) => {
    const newSelected = new Set(selectedUsers);
    if (newSelected.has(userId)) {
      newSelected.delete(userId);
    } else {
      newSelected.add(userId);
    }
    setSelectedUsers(newSelected);
  };

  const handleSelectAll = () => {
    if (selectedUsers.size === users.length) {
      setSelectedUsers(new Set());
    } else {
      setSelectedUsers(new Set(users.map(user => user.id)));
    }
  };

  const handleBulkDelete = async () => {
    if (selectedUsers.size === 0) return;

    setConfirmationModal({
      isOpen: true,
      title: 'Confirm Delete',
      message: `Are you sure you want to delete ${selectedUsers.size} user(s)? This action cannot be undone.`,
      confirmText: 'Delete',
      confirmButtonClass: 'bg-red-600 hover:bg-red-700',
      icon: <Trash2 className="h-6 w-6 text-red-500" />,
      onConfirm: async () => {
        try {
          const response = await usersApi.bulkDelete(Array.from(selectedUsers));
          if (response.data.errors.length > 0) {
            setError(`Bulk delete completed with some errors: ${response.data.errors.join(', ')}`);
          } else {
            setSuccessMessage(response.data.message);
          }
          setSelectedUsers(new Set());
          await loadUsers();
        } catch (err) {
          setError(err instanceof Error ? err.message : 'Failed to delete users');
        }
      }
    });
  };

  const handleBulkResetPassword = async () => {
    if (selectedUsers.size === 0) return;

    setConfirmationModal({
      isOpen: true,
      title: 'Reset Passwords',
      message: `Reset passwords for ${selectedUsers.size} user(s)? Temporary passwords will be generated and sent via email.`,
      confirmText: 'Reset Passwords',
      confirmButtonClass: 'bg-purple-600 hover:bg-purple-700',
      icon: <Key className="h-6 w-6 text-purple-500" />,
      onConfirm: async () => {
        try {
          const response = await usersApi.bulkResetPassword(Array.from(selectedUsers));
          if (response.data.errors.length > 0) {
            setError(`Bulk password reset completed with some errors: ${response.data.errors.join(', ')}`);
          } else {
            setSuccessMessage(response.data.message);
          }
          setSelectedUsers(new Set());
        } catch (err) {
          setError(err instanceof Error ? err.message : 'Failed to reset passwords');
        }
      }
    });
  };

  const handleBulkResendActivation = async () => {
    if (selectedUsers.size === 0) return;

    setConfirmationModal({
      isOpen: true,
      title: 'Resend Activation Emails',
      message: `Send activation emails to ${selectedUsers.size} user(s)?`,
      confirmText: 'Send Emails',
      confirmButtonClass: 'bg-blue-600 hover:bg-blue-700',
      icon: <MailIcon className="h-6 w-6 text-blue-500" />,
      onConfirm: async () => {
        try {
          const response = await usersApi.bulkResendActivation(Array.from(selectedUsers));
          if (response.data.errors.length > 0) {
            setError(`Bulk activation email send completed with some errors: ${response.data.errors.join(', ')}`);
          } else {
            setSuccessMessage(response.data.message);
          }
          setSelectedUsers(new Set());
        } catch (err) {
          setError(err instanceof Error ? err.message : 'Failed to send activation emails');
        }
      }
    });
  };

  const handleBulkToggleStatus = async (activate: boolean) => {
    if (selectedUsers.size === 0) return;

    const action = activate ? 'activate' : 'deactivate';
    const actionTitle = activate ? 'Activate Users' : 'Deactivate Users';

    setConfirmationModal({
      isOpen: true,
      title: actionTitle,
      message: `Are you sure you want to ${action} ${selectedUsers.size} user(s)?`,
      confirmText: activate ? 'Activate' : 'Deactivate',
      confirmButtonClass: activate ? 'bg-green-600 hover:bg-green-700' : 'bg-red-600 hover:bg-red-700',
      icon: activate ? <Power className="h-6 w-6 text-green-500" /> : <PowerOff className="h-6 w-6 text-red-500" />,
      onConfirm: async () => {
        try {
          const response = await usersApi.bulkToggleStatus(Array.from(selectedUsers), activate);
          if (response.data.errors.length > 0) {
            setError(`Bulk ${action} completed with some errors: ${response.data.errors.join(', ')}`);
          } else {
            setSuccessMessage(response.data.message);
          }
          setSelectedUsers(new Set());
          await loadUsers();
        } catch (err) {
          setError(err instanceof Error ? err.message : `Failed to ${action} users`);
        }
      }
    });
  };

  const closeModal = () => {
    setConfirmationModal({ isOpen: false, title: '', message: '', onConfirm: () => {} });
  };

  // Auto-hide success message after 5 seconds
  useEffect(() => {
    if (successMessage) {
      const timer = setTimeout(() => {
        setSuccessMessage(null);
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [successMessage]);

  if (loading && users.length === 0) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center min-h-96">
          <div className="text-gray-600 dark:text-gray-400">Loading users...</div>
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
            <button
              onClick={() => setError(null)}
              className="text-red-500 hover:text-red-700"
            >
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
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Users</h1>
            <p className="text-gray-600 dark:text-gray-400">Manage users in the system</p>
          </div>
          <Link
            href="/users/add"
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center space-x-2"
          >
            <Plus className="h-4 w-4" />
            <span>Add User</span>
          </Link>
        </div>

        {selectedUsers.size > 0 && (
          <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4 mb-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <span className="text-blue-700 dark:text-blue-300 font-medium">
                  {selectedUsers.size} user(s) selected
                </span>
                <button
                  onClick={() => setSelectedUsers(new Set())}
                  className="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-200 text-sm"
                >
                  Clear selection
                </button>
              </div>
              <div className="flex items-center space-x-2">
                {(() => {
                  const selectedUserObjects = users.filter(user => selectedUsers.has(user.id));
                  const hasInactiveUsers = selectedUserObjects.some(user => !user.is_active);
                  const hasActiveUsers = selectedUserObjects.some(user => user.is_active);

                  return (
                    <>
                      {hasInactiveUsers && (
                        <button
                          onClick={() => handleBulkToggleStatus(true)}
                          className="bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700 flex items-center space-x-1"
                        >
                          <Power className="h-3 w-3" />
                          <span>Activate</span>
                        </button>
                      )}
                      {hasActiveUsers && (
                        <button
                          onClick={() => handleBulkToggleStatus(false)}
                          className="bg-red-600 text-white px-3 py-1 rounded text-sm hover:bg-red-700 flex items-center space-x-1"
                        >
                          <PowerOff className="h-3 w-3" />
                          <span>Deactivate</span>
                        </button>
                      )}
                    </>
                  );
                })()}
                <button
                  onClick={handleBulkResetPassword}
                  className="bg-purple-600 text-white px-3 py-1 rounded text-sm hover:bg-purple-700 flex items-center space-x-1"
                >
                  <Key className="h-3 w-3" />
                  <span>Reset Passwords</span>
                </button>
                <button
                  onClick={handleBulkResendActivation}
                  className="bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700 flex items-center space-x-1"
                >
                  <RefreshCw className="h-3 w-3" />
                  <span>Resend Activation</span>
                </button>
                <button
                  onClick={handleBulkDelete}
                  className="bg-red-600 text-white px-3 py-1 rounded text-sm hover:bg-red-700 flex items-center space-x-1"
                >
                  <Trash2 className="h-3 w-3" />
                  <span>Delete</span>
                </button>
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
                  placeholder="Search users..."
                  value={searchTerm}
                  onChange={handleSearchChange}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                />
              </div>
            </div>

            <div className="min-w-32">
              <select
                value={filters.is_active === undefined ? '' : filters.is_active.toString()}
                onChange={handleActiveFilter}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
              >
                <option value="">All Status</option>
                <option value="true">Active</option>
                <option value="false">Inactive</option>
              </select>
            </div>

            <div className="min-w-32">
              <select
                value={filters.is_admin === undefined ? '' : filters.is_admin.toString()}
                onChange={handleAdminFilter}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
              >
                <option value="">All Users</option>
                <option value="true">Admins</option>
                <option value="false">Regular Users</option>
              </select>
            </div>

            <div className="min-w-40">
              <select
                value={filters.role || ''}
                onChange={handleRoleFilter}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
              >
                <option value="">All Roles</option>
                <option value="company_admin">Company Admin</option>
                <option value="recruiter">Recruiter</option>
                <option value="job_seeker">Job Seeker</option>
              </select>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
          {users.length === 0 ? (
            <div className="p-8 text-center">
              <Users className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">No users found</h3>
              <p className="text-gray-600 dark:text-gray-400 mb-4">Get started by creating your first user.</p>
              <Link
                href="/users/add"
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 inline-flex items-center space-x-2"
              >
                <Plus className="h-4 w-4" />
                <span>Add User</span>
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
                        checked={users.length > 0 && selectedUsers.size === users.length}
                        onChange={handleSelectAll}
                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                      />
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      User
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Company
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Contact
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Role
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                  {users.map((user) => (
                    <tr key={user.id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                      <td className="px-6 py-4">
                        <input
                          type="checkbox"
                          checked={selectedUsers.has(user.id)}
                          onChange={() => handleSelectUser(user.id)}
                          className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                        />
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center">
                          <div className="flex-shrink-0">
                            <Users className="h-8 w-8 text-gray-400" />
                          </div>
                          <div className="ml-4">
                            <div className="text-sm font-medium text-gray-900 dark:text-white">
                              {user.first_name} {user.last_name}
                            </div>
                            <div className="text-sm text-gray-500 dark:text-gray-400">
                              {user.email}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm text-gray-900 dark:text-white">
                          {user.company_name ? (
                            <div className="flex items-center">
                              <Building2 className="h-3 w-3 mr-1 text-gray-400" />
                              {user.company_name}
                            </div>
                          ) : (
                            <span className="text-gray-400 italic">No company</span>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm text-gray-900 dark:text-white">
                          <div className="flex items-center mb-1">
                            <Mail className="h-3 w-3 mr-1 text-gray-400" />
                            {user.email}
                          </div>
                          {user.phone && (
                            <div className="flex items-center">
                              <Phone className="h-3 w-3 mr-1 text-gray-400" />
                              {user.phone}
                            </div>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex flex-col space-y-1">
                          {user.is_admin && (
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                              <Shield className="h-3 w-3 mr-1" />
                              Admin
                            </span>
                          )}
                          {user.roles.map((role) => (
                            <span key={role} className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                              {role.replace('_', ' ')}
                            </span>
                          ))}
                          {user.require_2fa && (
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                              <ShieldCheck className="h-3 w-3 mr-1" />
                              2FA
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          user.is_active
                            ? 'bg-green-100 text-green-800'
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {user.is_active ? (
                            <>
                              <UserCheck className="h-3 w-3 mr-1" />
                              Active
                            </>
                          ) : (
                            <>
                              <UserX className="h-3 w-3 mr-1" />
                              Inactive
                            </>
                          )}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-right">
                        <div className="flex items-center justify-end">
                          <Link
                            href={`/users/${user.id}/edit`}
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
                  Showing {((pagination.page - 1) * pagination.size) + 1} to {Math.min(pagination.page * pagination.size, pagination.total)} of {pagination.total} results
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

        <ConfirmationModal
          isOpen={confirmationModal.isOpen}
          onClose={closeModal}
          onConfirm={confirmationModal.onConfirm}
          title={confirmationModal.title}
          message={confirmationModal.message}
          confirmText={confirmationModal.confirmText}
          confirmButtonClass={confirmationModal.confirmButtonClass}
          icon={confirmationModal.icon}
        />
      </div>
    </AppLayout>
  );
}

export default function UsersPage() {
  return (
    <ProtectedRoute>
      <UsersPageContent />
    </ProtectedRoute>
  );
}