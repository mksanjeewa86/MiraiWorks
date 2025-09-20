'use client';

import { useState, useEffect, useCallback } from 'react';
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
import { usersApi } from '@/api/users';
import { UserManagement, UserFilters } from '@/types/user';
import AppLayout from '@/components/layout/AppLayout';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import ConfirmationModal from '@/components/ui/ConfirmationModal';

function UsersPageContent() {
  const [users, setUsers] = useState<UserManagement[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedUsers, setSelectedUsers] = useState<Set<number>>(new Set());
  const [confirmationModal, setConfirmationModal] = useState<{
    isOpen: boolean;
    title: string;
    message: string | React.ReactNode;
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
    role: undefined,
  });

  const [pagination, setPagination] = useState({
    total: 0,
    pages: 0,
    page: 1,
    size: 20,
  });

  const loadUsers = useCallback(async () => {
    try {
      setLoading(true);
      const response = await usersApi.getUsers(filters);

      if (!response.data) {
        setError('No data received');
        return;
      }

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
  }, [filters]);

  // Debounce search term to avoid API calls on every keystroke
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      setFilters(prev => ({ ...prev, search: searchTerm, page: 1 }));
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [searchTerm]);

  useEffect(() => {
    loadUsers();
  }, [loadUsers]);

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(e.target.value);
  };

  const handleStatusFilter = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value;
    setFilters(prev => ({
      ...prev,
      page: 1,
      // Reset all status-related filters
      is_active: value === 'active' ? true : value === 'inactive' ? false : undefined,
      is_suspended: value === 'suspended' ? true : value === 'active' || value === 'inactive' || value === '2fa_active' ? false : undefined,
      require_2fa: value === '2fa_active' ? true : undefined,
      status_filter: value || undefined,
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

    const selectedUserObjects = users.filter(user => selectedUsers.has(user.id));

    const message = (
      <div>
        <p className="mb-3">
          Are you sure you want to delete the following {selectedUsers.size} user(s)? This action cannot be undone.
        </p>
        <ul className="list-none space-y-2 max-h-48 overflow-y-auto bg-gradient-to-r from-red-50 to-pink-50 dark:from-red-900/20 dark:to-pink-900/20 p-4 rounded-lg">
          {selectedUserObjects.map((user) => (
            <li key={user.id} className="flex items-center space-x-2 text-sm">
              <span className="w-2 h-2 bg-red-400 rounded-full flex-shrink-0"></span>
              <span className="text-red-700 dark:text-red-300">{user.email}</span>
            </li>
          ))}
        </ul>
      </div>
    );

    setConfirmationModal({
      isOpen: true,
      title: 'Confirm Delete',
      message,
      confirmText: 'Delete',
      confirmButtonClass: 'bg-red-600 hover:bg-red-700',
      icon: <Trash2 className="h-6 w-6 text-red-500" />,
      onConfirm: async () => {
        try {
          const response = await usersApi.bulkDelete(Array.from(selectedUsers));
          setSuccessMessage(response.data?.message || 'Users deleted successfully');
          setSelectedUsers(new Set());
          await loadUsers();
        } catch (err) {
          console.error('Bulk delete error:', err);
          setError(err instanceof Error ? err.message : 'Failed to delete users');
        }
      }
    });
  };

  const handleBulkResetPassword = async () => {
    if (selectedUsers.size === 0) return;

    const selectedUserObjects = users.filter(user => selectedUsers.has(user.id));

    const message = (
      <div>
        <p className="mb-3">
          Reset passwords for the following {selectedUsers.size} user(s)? Temporary passwords will be generated and sent via email.
        </p>
        <ul className="list-none space-y-2 max-h-48 overflow-y-auto bg-gradient-to-r from-purple-50 to-indigo-50 dark:from-purple-900/20 dark:to-indigo-900/20 p-4 rounded-lg">
          {selectedUserObjects.map((user) => (
            <li key={user.id} className="flex items-center space-x-2 text-sm">
              <span className="w-2 h-2 bg-purple-400 rounded-full flex-shrink-0"></span>
              <span className="text-purple-700 dark:text-purple-300">{user.email}</span>
            </li>
          ))}
        </ul>
      </div>
    );

    setConfirmationModal({
      isOpen: true,
      title: 'Reset Passwords',
      message,
      confirmText: 'Reset Passwords',
      confirmButtonClass: 'bg-purple-600 hover:bg-purple-700',
      icon: <Key className="h-6 w-6 text-purple-500" />,
      onConfirm: async () => {
        try {
          const response = await usersApi.bulkResetPassword(Array.from(selectedUsers));
          setSuccessMessage(response.data?.message || 'Password reset emails sent successfully');
          setSelectedUsers(new Set());
        } catch (err) {
          console.error('Bulk reset password error:', err);
          setError(err instanceof Error ? err.message : 'Failed to reset passwords');
        }
      }
    });
  };

  const handleBulkResendActivation = async () => {
    if (selectedUsers.size === 0) return;

    const selectedUserObjects = users.filter(user => selectedUsers.has(user.id));

    const message = (
      <div>
        <p className="mb-3">
          Send activation emails to the following {selectedUsers.size} user(s)?
        </p>
        <ul className="list-none space-y-2 max-h-48 overflow-y-auto bg-gradient-to-r from-blue-50 to-cyan-50 dark:from-blue-900/20 dark:to-cyan-900/20 p-4 rounded-lg">
          {selectedUserObjects.map((user) => (
            <li key={user.id} className="flex items-center space-x-2 text-sm">
              <span className="w-2 h-2 bg-blue-400 rounded-full flex-shrink-0"></span>
              <span className="text-blue-700 dark:text-blue-300">{user.email}</span>
            </li>
          ))}
        </ul>
      </div>
    );

    setConfirmationModal({
      isOpen: true,
      title: 'Resend Activation Emails',
      message,
      confirmText: 'Send Emails',
      confirmButtonClass: 'bg-blue-600 hover:bg-blue-700',
      icon: <MailIcon className="h-6 w-6 text-blue-500" />,
      onConfirm: async () => {
        try {
          const response = await usersApi.bulkResendActivation(Array.from(selectedUsers));
          setSuccessMessage(response.data?.message || 'Activation emails sent successfully');
          setSelectedUsers(new Set());
        } catch (err) {
          console.error('Bulk resend activation error:', err);
          setError(err instanceof Error ? err.message : 'Failed to send activation emails');
        }
      }
    });
  };

  const handleBulkSuspend = async () => {
    if (selectedUsers.size === 0) return;

    const selectedUserObjects = users.filter(user => selectedUsers.has(user.id));
    const targetUsers = selectedUserObjects.filter(user => !user.is_suspended);

    if (targetUsers.length === 0) {
      setError('No active users selected to suspend.');
      return;
    }

    const message = (
      <div>
        <p className="mb-3">
          Are you sure you want to suspend the following {targetUsers.length} user(s)? They will not be able to login until unsuspended.
        </p>
        <ul className="list-none space-y-2 max-h-48 overflow-y-auto p-4 rounded-lg bg-gradient-to-r from-red-50 to-orange-50 dark:from-red-900/20 dark:to-orange-900/20">
          {targetUsers.map((user) => (
            <li key={user.id} className="flex items-center space-x-2 text-sm">
              <span className="w-2 h-2 bg-red-400 rounded-full flex-shrink-0"></span>
              <span className="text-red-700 dark:text-red-300">{user.email}</span>
            </li>
          ))}
        </ul>
      </div>
    );

    setConfirmationModal({
      isOpen: true,
      title: 'Suspend Users',
      message,
      confirmText: 'Suspend',
      confirmButtonClass: 'bg-red-600 hover:bg-red-700',
      icon: <PowerOff className="h-6 w-6 text-red-500" />,
      onConfirm: async () => {
        try {
          const response = await usersApi.bulkSuspend(Array.from(selectedUsers));
          setSuccessMessage(response.data?.message || 'Users suspended successfully');
          setSelectedUsers(new Set());
          await loadUsers();
        } catch (err) {
          console.error('Bulk suspend error:', err);
          setError(err instanceof Error ? err.message : 'Failed to suspend users');
        }
      }
    });
  };

  const handleBulkUnsuspend = async () => {
    if (selectedUsers.size === 0) return;

    const selectedUserObjects = users.filter(user => selectedUsers.has(user.id));
    const targetUsers = selectedUserObjects.filter(user => user.is_suspended);

    if (targetUsers.length === 0) {
      setError('No suspended users selected to unsuspend.');
      return;
    }

    const message = (
      <div>
        <p className="mb-3">
          Are you sure you want to unsuspend the following {targetUsers.length} user(s)? They will be able to login again.
        </p>
        <ul className="list-none space-y-2 max-h-48 overflow-y-auto p-4 rounded-lg bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20">
          {targetUsers.map((user) => (
            <li key={user.id} className="flex items-center space-x-2 text-sm">
              <span className="w-2 h-2 bg-green-400 rounded-full flex-shrink-0"></span>
              <span className="text-green-700 dark:text-green-300">{user.email}</span>
            </li>
          ))}
        </ul>
      </div>
    );

    setConfirmationModal({
      isOpen: true,
      title: 'Unsuspend Users',
      message,
      confirmText: 'Unsuspend',
      confirmButtonClass: 'bg-green-600 hover:bg-green-700',
      icon: <Power className="h-6 w-6 text-green-500" />,
      onConfirm: async () => {
        try {
          const response = await usersApi.bulkUnsuspend(Array.from(selectedUsers));
          setSuccessMessage(response.data?.message || 'Users unsuspended successfully');
          setSelectedUsers(new Set());
          await loadUsers();
        } catch (err) {
          console.error('Bulk unsuspend error:', err);
          setError(err instanceof Error ? err.message : 'Failed to unsuspend users');
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
          <div></div>
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
                  const hasSuspendedUsers = selectedUserObjects.some(user => user.is_suspended);
                  const hasActiveUsers = selectedUserObjects.some(user => !user.is_suspended);

                  return (
                    <>
                      {hasSuspendedUsers && (
                        <button
                          onClick={handleBulkUnsuspend}
                          className="bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700 flex items-center space-x-1"
                        >
                          <Power className="h-3 w-3" />
                          <span>Unsuspend</span>
                        </button>
                      )}
                      {hasActiveUsers && (
                        <button
                          onClick={handleBulkSuspend}
                          className="bg-red-600 text-white px-3 py-1 rounded text-sm hover:bg-red-700 flex items-center space-x-1"
                        >
                          <PowerOff className="h-3 w-3" />
                          <span>Suspend</span>
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

            <div className="min-w-40">
              <select
                value={filters.status_filter || ''}
                onChange={handleStatusFilter}
                className="w-full px-3 py-2 pr-8 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
              >
                <option value="">All Status</option>
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
                <option value="suspended">Suspended</option>
                <option value="2fa_active">2FA Active</option>
              </select>
            </div>

            <div className="min-w-40">
              <select
                value={filters.role || ''}
                onChange={handleRoleFilter}
                className="w-full px-3 py-2 pr-8 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
              >
                <option value="">All Roles</option>
                <option value="company_admin">Company Admin</option>
                <option value="recruiter">Recruiter</option>
                <option value="employer">Employer</option>
                <option value="candidate">Candidate</option>
              </select>
            </div>

            <div className="min-w-40">
              <div className="flex items-center">
                <input
                  id="include_deleted"
                  type="checkbox"
                  checked={filters.include_deleted || false}
                  onChange={(e) => setFilters(prev => ({
                    ...prev,
                    include_deleted: e.target.checked,
                    page: 1
                  }))}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label htmlFor="include_deleted" className="ml-2 block text-sm font-medium text-gray-700 dark:text-gray-300">
                  Include deleted users
                </label>
              </div>
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
                    <tr
                      key={user.id}
                      className={`cursor-pointer transition-colors ${
                        selectedUsers.has(user.id)
                          ? 'bg-blue-50 dark:bg-blue-900/20 hover:bg-blue-100 dark:hover:bg-blue-900/30'
                          : 'hover:bg-gray-50 dark:hover:bg-gray-700'
                      }`}
                      onClick={() => handleSelectUser(user.id)}
                    >
                      <td className="px-6 py-4">
                        <input
                          type="checkbox"
                          checked={selectedUsers.has(user.id)}
                          onChange={() => handleSelectUser(user.id)}
                          onClick={(e) => e.stopPropagation()}
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
                          {user.roles.map((role: string) => (
                            <span key={role} className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                              {role.replace('_', ' ')}
                            </span>
                          ))}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex flex-wrap gap-1">
                          {user.is_deleted ? (
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-300">
                              <UserX className="h-3 w-3 mr-1" />
                              Deleted
                            </span>
                          ) : user.is_suspended ? (
                            <>
                              {!user.is_active && (
                                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-300">
                                  <UserX className="h-3 w-3 mr-1" />
                                  Inactive
                                </span>
                              )}
                              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-orange-100 text-orange-800 dark:bg-orange-900/20 dark:text-orange-300">
                                <PowerOff className="h-3 w-3 mr-1" />
                                Suspended
                              </span>
                            </>
                          ) : (
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
                          )}
                          {user.require_2fa && !user.is_deleted && (
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-300">
                              <ShieldCheck className="h-3 w-3 mr-1" />
                              2FA
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4 text-right">
                        <div className="flex items-center justify-end" onClick={(e) => e.stopPropagation()}>
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