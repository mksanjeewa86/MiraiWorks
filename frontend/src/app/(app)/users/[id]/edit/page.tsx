'use client';

import { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import {
  ArrowLeft,
  Save,
  User,
  Trash2,
  UserX,
  UserCheck,
  Key,
  Mail,
  AlertTriangle,
} from 'lucide-react';
import { UserEditFormData, ActionState } from '@/types/user';
import { usersApi } from '@/api/users';
import { UserManagement as UserType } from '@/types/user';
import { useToast } from '@/contexts/ToastContext';
import AppLayout from '@/components/layout/AppLayout';
import ProtectedRoute from '@/components/auth/ProtectedRoute';

function EditUserContent() {
  const router = useRouter();
  const params = useParams();
  const { showToast } = useToast();
  const [user, setUser] = useState<UserType | null>(null);
  const [formData, setFormData] = useState<UserEditFormData>({
    first_name: '',
    last_name: '',
  });
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [actionState, setActionState] = useState<ActionState>({
    loading: false,
    type: null,
  });
  const [error, setError] = useState<string | null>(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  const userId = params?.id as string;

  useEffect(() => {
    const loadUser = async () => {
      if (!userId) return;

      try {
        setLoading(true);
        const response = await usersApi.getUser(parseInt(userId));
        const userData = response.data;

        if (!userData) {
          setError('User not found');
          return;
        }

        setUser(userData);
        setFormData({
          first_name: userData.first_name,
          last_name: userData.last_name,
        });
      } catch (err) {
        console.error('Error loading user:', err);
        setError('Failed to load user');
        showToast({ type: 'error', title: 'Failed to load user' });
      } finally {
        setLoading(false);
      }
    };

    loadUser();
  }, [userId, showToast]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? (e.target as HTMLInputElement).checked : value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!userId) return;

    try {
      setSubmitting(true);
      const response = await usersApi.updateUser(parseInt(userId), formData);
      if (response.data) {
        setUser(response.data);
      }
      showToast({ type: 'success', title: 'User updated successfully' });
    } catch (err) {
      console.error('Error updating user:', err);
      showToast({ type: 'error', title: 'Failed to update user' });
    } finally {
      setSubmitting(false);
    }
  };

  const handleAction = async (action: string) => {
    if (!userId || !user) return;

    try {
      setActionState({ loading: true, type: action });

      switch (action) {
        case 'suspend':
          await usersApi.suspendUser(parseInt(userId));
          setUser((prev: UserType | null) => (prev ? { ...prev, is_suspended: true } : null));
          showToast({ type: 'success', title: 'User suspended successfully' });
          break;

        case 'unsuspend':
          await usersApi.unsuspendUser(parseInt(userId));
          setUser((prev: UserType | null) => (prev ? { ...prev, is_suspended: false } : null));
          showToast({ type: 'success', title: 'User unsuspended successfully' });
          break;

        case 'reset-password':
          await usersApi.resetPassword(parseInt(userId));
          showToast({ type: 'success', title: 'Password reset email sent' });
          break;

        case 'resend-activation':
          await usersApi.resendActivation(parseInt(userId));
          showToast({ type: 'success', title: 'Activation email sent' });
          break;

        case 'delete':
          await usersApi.deleteUser(parseInt(userId));
          showToast({ type: 'success', title: 'User deleted successfully' });
          router.push('/users');
          break;
      }
    } catch (err) {
      console.error(`Error performing ${action}:`, err);
      showToast({ type: 'error', title: `Failed to ${action.replace('-', ' ')} user` });
    } finally {
      setActionState({ loading: false, type: null });
      setShowDeleteConfirm(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-lg">Loading user...</div>
      </div>
    );
  }

  if (error || !user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="text-lg text-red-600 mb-4">{error || 'User not found'}</div>
          <button
            onClick={() => router.push('/users')}
            className="bg-gray-600 text-white px-4 py-2 rounded hover:bg-gray-700"
          >
            Back to Users
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-6">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Back Navigation */}
        <div className="mb-4">
          <button
            onClick={() => router.push('/users')}
            className="flex items-center text-blue-600 hover:text-blue-800 font-medium"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Users
          </button>
        </div>

        {/* Header */}
        <div className="bg-white shadow-sm rounded-lg mb-6">
          <div className="px-6 py-6">
            <div className="flex items-start justify-between">
              <div className="flex items-center space-x-4">
                <div className="flex-shrink-0">
                  <div className="h-16 w-16 bg-blue-100 rounded-full flex items-center justify-center">
                    <User className="h-8 w-8 text-blue-600" />
                  </div>
                </div>
                <div>
                  <h1 className="text-3xl font-bold text-gray-900">
                    {user.first_name} {user.last_name}
                  </h1>
                  <p className="text-sm text-gray-500 mt-1">{user.email}</p>
                  <div className="flex items-center space-x-2 mt-3">
                    {user.is_suspended && (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                        Suspended
                      </span>
                    )}
                    {!user.is_active && (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                        Inactive
                      </span>
                    )}
                    {user.is_admin && (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                        Admin
                      </span>
                    )}
                    {user.is_active && !user.is_suspended && (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                        Active
                      </span>
                    )}
                  </div>
                </div>
              </div>
              {/* Quick Info */}
              {user.company_name && (
                <div className="text-right">
                  <p className="text-sm text-gray-500">Company</p>
                  <p className="text-sm font-medium text-gray-900">{user.company_name}</p>
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Form */}
          <div className="lg:col-span-2">
            <div className="bg-white shadow rounded-lg">
              <div className="px-6 py-4 border-b border-gray-200">
                <h2 className="text-lg font-medium text-gray-900">User Information</h2>
              </div>
              <form onSubmit={handleSubmit} className="px-6 py-4 space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label
                      htmlFor="first_name"
                      className="block text-sm font-medium text-gray-700 mb-1"
                    >
                      First Name
                    </label>
                    <input
                      type="text"
                      id="first_name"
                      name="first_name"
                      value={formData.first_name}
                      onChange={handleInputChange}
                      required
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>

                  <div>
                    <label
                      htmlFor="last_name"
                      className="block text-sm font-medium text-gray-700 mb-1"
                    >
                      Last Name
                    </label>
                    <input
                      type="text"
                      id="last_name"
                      name="last_name"
                      value={formData.last_name}
                      onChange={handleInputChange}
                      required
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                </div>

                <div>
                  <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                    Email Address
                  </label>
                  <input
                    type="email"
                    id="email"
                    name="email"
                    value={user.email}
                    readOnly
                    className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50 text-gray-500 cursor-not-allowed"
                    title="Email cannot be changed"
                  />
                  <p className="mt-1 text-sm text-gray-500">Email address cannot be changed</p>
                </div>

                <div className="flex justify-end pt-6 border-t border-gray-200">
                  <button
                    type="submit"
                    disabled={submitting}
                    className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 flex items-center"
                  >
                    <Save className="h-4 w-4 mr-2" />
                    {submitting ? 'Saving...' : 'Save Changes'}
                  </button>
                </div>
              </form>
            </div>
          </div>

          {/* Actions Panel */}
          <div className="space-y-6">
            {/* Account Actions */}
            <div className="bg-white shadow rounded-lg">
              <div className="px-6 py-4 border-b border-gray-200">
                <h2 className="text-lg font-medium text-gray-900">Account Actions</h2>
              </div>
              <div className="px-6 py-4 space-y-3">
                {/* Suspend/Unsuspend */}
                {user.is_suspended ? (
                  <button
                    onClick={() => handleAction('unsuspend')}
                    disabled={actionState.loading && actionState.type === 'unsuspend'}
                    className="w-full flex items-center justify-center px-4 py-2 border border-green-300 rounded-md text-green-700 bg-green-50 hover:bg-green-100 focus:outline-none focus:ring-2 focus:ring-green-500 disabled:opacity-50"
                  >
                    <UserCheck className="h-4 w-4 mr-2" />
                    {actionState.loading && actionState.type === 'unsuspend'
                      ? 'Unsuspending...'
                      : 'Unsuspend User'}
                  </button>
                ) : (
                  <button
                    onClick={() => handleAction('suspend')}
                    disabled={actionState.loading && actionState.type === 'suspend'}
                    className="w-full flex items-center justify-center px-4 py-2 border border-orange-300 rounded-md text-orange-700 bg-orange-50 hover:bg-orange-100 focus:outline-none focus:ring-2 focus:ring-orange-500 disabled:opacity-50"
                  >
                    <UserX className="h-4 w-4 mr-2" />
                    {actionState.loading && actionState.type === 'suspend'
                      ? 'Suspending...'
                      : 'Suspend User'}
                  </button>
                )}

                {/* Reset Password */}
                <button
                  onClick={() => handleAction('reset-password')}
                  disabled={actionState.loading && actionState.type === 'reset-password'}
                  className="w-full flex items-center justify-center px-4 py-2 border border-blue-300 rounded-md text-blue-700 bg-blue-50 hover:bg-blue-100 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
                >
                  <Key className="h-4 w-4 mr-2" />
                  {actionState.loading && actionState.type === 'reset-password'
                    ? 'Sending...'
                    : 'Reset Password'}
                </button>

                {/* Resend Activation (only for inactive users) */}
                {!user.is_active && (
                  <button
                    onClick={() => handleAction('resend-activation')}
                    disabled={actionState.loading && actionState.type === 'resend-activation'}
                    className="w-full flex items-center justify-center px-4 py-2 border border-purple-300 rounded-md text-purple-700 bg-purple-50 hover:bg-purple-100 focus:outline-none focus:ring-2 focus:ring-purple-500 disabled:opacity-50"
                  >
                    <Mail className="h-4 w-4 mr-2" />
                    {actionState.loading && actionState.type === 'resend-activation'
                      ? 'Sending...'
                      : 'Resend Activation'}
                  </button>
                )}
              </div>
            </div>

            {/* Danger Zone */}
            <div className="bg-white shadow rounded-lg">
              <div className="px-6 py-4 border-b border-gray-200">
                <h2 className="text-lg font-medium text-red-900">Danger Zone</h2>
              </div>
              <div className="px-6 py-4">
                {!showDeleteConfirm ? (
                  <button
                    onClick={() => setShowDeleteConfirm(true)}
                    className="w-full flex items-center justify-center px-4 py-2 border border-red-300 rounded-md text-red-700 bg-red-50 hover:bg-red-100 focus:outline-none focus:ring-2 focus:ring-red-500"
                  >
                    <Trash2 className="h-4 w-4 mr-2" />
                    Delete User
                  </button>
                ) : (
                  <div className="space-y-3">
                    <div className="flex items-center space-x-2 text-sm text-red-600">
                      <AlertTriangle className="h-4 w-4" />
                      <span>Are you sure? This action cannot be undone.</span>
                    </div>
                    <div className="flex space-x-3">
                      <button
                        onClick={() => setShowDeleteConfirm(false)}
                        className="flex-1 px-3 py-2 border border-gray-300 rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      >
                        Cancel
                      </button>
                      <button
                        onClick={() => handleAction('delete')}
                        disabled={actionState.loading && actionState.type === 'delete'}
                        className="flex-1 px-3 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 disabled:opacity-50"
                      >
                        {actionState.loading && actionState.type === 'delete'
                          ? 'Deleting...'
                          : 'Delete'}
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function EditUserPage() {
  return (
    <ProtectedRoute>
      <AppLayout>
        <EditUserContent />
      </AppLayout>
    </ProtectedRoute>
  );
}
