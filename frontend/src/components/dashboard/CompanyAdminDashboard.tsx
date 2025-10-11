'use client';

import { useAuth } from '@/contexts/AuthContext';

export default function CompanyAdminDashboard() {
  const { user } = useAuth();

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
          Welcome, {user?.full_name || 'Company Admin'}
        </h1>
        <p className="text-gray-600 dark:text-gray-400 mt-2">
          Company Admin Dashboard - Coming Soon
        </p>
      </div>
    </div>
  );
}
