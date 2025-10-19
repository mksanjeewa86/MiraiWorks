'use client';

import { useEffect, useState } from 'react';
import { companyConnectionsApi } from '@/api';
import type { CompanyConnection } from '@/types/company-connection';
import { useToast } from '@/hooks/useToast';

export default function ConnectionsManagementPage() {
  const toast = useToast();
  const [connections, setConnections] = useState<CompanyConnection[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadConnections();
  }, []);

  const loadConnections = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await companyConnectionsApi.getMyConnections();
      if (response.success && response.data) {
        setConnections(response.data);
      } else {
        setError(response.message || 'Failed to load connections');
      }
    } catch (err) {
      setError('An error occurred while loading connections');
    } finally {
      setLoading(false);
    }
  };

  const handleDeactivate = async (connectionId: number) => {
    if (!confirm('Are you sure you want to deactivate this connection?')) {
      return;
    }

    try {
      const response = await companyConnectionsApi.deactivateConnection(connectionId);
      if (response.success) {
        await loadConnections();
        toast.success('Connection deactivated successfully');
      } else {
        toast.error(response.message || 'Failed to deactivate connection');
      }
    } catch (err) {
      toast.error('An error occurred while deactivating connection');
    }
  };

  const handleActivate = async (connectionId: number) => {
    try {
      const response = await companyConnectionsApi.activateConnection(connectionId);
      if (response.success) {
        await loadConnections();
        toast.success('Connection activated successfully');
      } else {
        toast.error(response.message || 'Failed to activate connection');
      }
    } catch (err) {
      toast.error('An error occurred while activating connection');
    }
  };

  if (loading) {
    return (
      <div className="flex h-96 items-center justify-center">
        <div className="text-center">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-gray-300 border-t-blue-600" />
          <p className="mt-4 text-sm text-gray-600">Loading connections...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-md bg-red-50 p-4">
        <div className="flex">
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800">Error</h3>
            <div className="mt-2 text-sm text-red-700">{error}</div>
            <button
              onClick={loadConnections}
              className="mt-4 rounded bg-red-100 px-3 py-1 text-sm text-red-800 hover:bg-red-200"
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Company Connections</h1>
        <p className="mt-1 text-sm text-gray-600">
          Manage connections between users and companies
        </p>
      </div>

      {connections.length === 0 ? (
        <div className="rounded-lg border border-dashed border-gray-300 p-12 text-center">
          <svg
            className="mx-auto h-12 w-12 text-gray-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M13 10V3L4 14h7v7l9-11h-7z"
            />
          </svg>
          <h3 className="mt-2 text-sm font-medium text-gray-900">No connections</h3>
          <p className="mt-1 text-sm text-gray-500">
            Get started by creating a new connection
          </p>
        </div>
      ) : (
        <div className="overflow-hidden bg-white shadow ring-1 ring-black ring-opacity-5 sm:rounded-lg">
          <table className="min-w-full divide-y divide-gray-300">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                  Type
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                  Source
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                  Target Company
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                  Permissions
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 bg-white">
              {connections.map((connection) => (
                <tr key={connection.id}>
                  <td className="whitespace-nowrap px-6 py-4 text-sm text-gray-900">
                    <span
                      className={`inline-flex rounded-full px-2 py-1 text-xs font-semibold ${
                        connection.source_type === 'user'
                          ? 'bg-blue-100 text-blue-800'
                          : 'bg-green-100 text-green-800'
                      }`}
                    >
                      {connection.source_type === 'user' ? 'User → Company' : 'Company → Company'}
                    </span>
                  </td>
                  <td className="whitespace-nowrap px-6 py-4 text-sm text-gray-900">
                    {connection.source_display_name || 'N/A'}
                  </td>
                  <td className="whitespace-nowrap px-6 py-4 text-sm text-gray-900">
                    {connection.target_company_name || `Company #${connection.target_company_id}`}
                  </td>
                  <td className="whitespace-nowrap px-6 py-4 text-sm text-gray-500">
                    <div className="flex flex-wrap gap-1">
                      {connection.can_message && (
                        <span className="inline-flex items-center rounded-full bg-green-50 px-2 py-0.5 text-xs text-green-700">
                          Message
                        </span>
                      )}
                      {connection.can_view_profile && (
                        <span className="inline-flex items-center rounded-full bg-blue-50 px-2 py-0.5 text-xs text-blue-700">
                          View
                        </span>
                      )}
                      {connection.can_assign_tasks && (
                        <span className="inline-flex items-center rounded-full bg-purple-50 px-2 py-0.5 text-xs text-purple-700">
                          Assign
                        </span>
                      )}
                    </div>
                  </td>
                  <td className="whitespace-nowrap px-6 py-4 text-sm text-gray-500">
                    <span
                      className={`inline-flex rounded-full px-2 py-1 text-xs font-semibold ${
                        connection.is_active
                          ? 'bg-green-100 text-green-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}
                    >
                      {connection.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td className="whitespace-nowrap px-6 py-4 text-sm font-medium">
                    {connection.is_active ? (
                      <button
                        onClick={() => handleDeactivate(connection.id)}
                        className="text-red-600 hover:text-red-900"
                      >
                        Deactivate
                      </button>
                    ) : (
                      <button
                        onClick={() => handleActivate(connection.id)}
                        className="text-green-600 hover:text-green-900"
                      >
                        Activate
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div className="rounded-lg bg-blue-50 p-4">
        <h3 className="text-sm font-medium text-blue-900">About Company Connections</h3>
        <div className="mt-2 text-sm text-blue-700">
          <ul className="list-disc space-y-1 pl-5">
            <li>
              <strong>User → Company:</strong> Individual user can message all users in the target
              company
            </li>
            <li>
              <strong>Company → Company:</strong> All users from both companies can message each
              other
            </li>
            <li>
              <strong>Same Company:</strong> Users in the same company can always message each other
              (no connection needed)
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}
