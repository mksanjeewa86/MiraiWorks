'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { dashboardApi } from "@/api/dashboard";
import Card from '@/components/ui/card';
import LoadingSpinner from '@/components/ui/loading-spinner';
import Button from '@/components/ui/button';
import type { EmployerStats } from '@/types/dashboard';

export default function EmployerDashboard() {
  const { user } = useAuth();
  const [stats, setStats] = useState<EmployerStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadDashboardData = async () => {
    try {
      const response = await dashboardApi.getStats();
      setStats(response.data as EmployerStats);
      setError(null);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner className="w-8 h-8" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
          <h2 className="text-lg font-semibold text-red-800 dark:text-red-200">Error Loading Dashboard</h2>
          <p className="text-red-600 dark:text-red-400 mt-2">{error}</p>
          <Button onClick={loadDashboardData} className="mt-4">
            Try Again
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold" style={{ color: 'var(--text-primary)' }}>Employer Dashboard</h1>
        <p className="mt-1" style={{ color: 'var(--text-secondary)' }}>Welcome {user?.full_name}, manage your hiring process efficiently.</p>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium" style={{ color: 'var(--text-secondary)' }}>Open Positions</p>
              <p className="text-3xl font-bold" style={{ color: 'var(--text-primary)' }}>{stats?.open_positions || 0}</p>
            </div>
            <div className="w-12 h-12 rounded-lg flex items-center justify-center" style={{ backgroundColor: 'rgba(108, 99, 255, 0.1)' }}>
              <span className="text-2xl">💼</span>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium" style={{ color: 'var(--text-secondary)' }}>Applications Received</p>
              <p className="text-3xl font-bold" style={{ color: 'var(--text-primary)' }}>{stats?.applications_received || 0}</p>
            </div>
            <div className="w-12 h-12 rounded-lg flex items-center justify-center" style={{ backgroundColor: 'rgba(34, 197, 94, 0.1)' }}>
              <span className="text-2xl">📄</span>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium" style={{ color: 'var(--text-secondary)' }}>Interviews Scheduled</p>
              <p className="text-3xl font-bold" style={{ color: 'var(--text-primary)' }}>{stats?.interviews_scheduled || 0}</p>
            </div>
            <div className="w-12 h-12 rounded-lg flex items-center justify-center" style={{ backgroundColor: 'rgba(251, 146, 60, 0.1)' }}>
              <span className="text-2xl">📅</span>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium" style={{ color: 'var(--text-secondary)' }}>Hires Made</p>
              <p className="text-3xl font-bold" style={{ color: 'var(--text-primary)' }}>{stats?.hires_made || 0}</p>
            </div>
            <div className="w-12 h-12 rounded-lg flex items-center justify-center" style={{ backgroundColor: 'rgba(168, 85, 247, 0.1)' }}>
              <span className="text-2xl">✅</span>
            </div>
          </div>
        </Card>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>Quick Actions</h3>
          <div className="space-y-3">
            <Button className="w-full flex items-center justify-center gap-2">
              <span>➕</span>
              Post New Job
            </Button>
            <Button variant="outline" className="w-full flex items-center justify-center gap-2">
              <span>📋</span>
              Review Applications
            </Button>
            <Button variant="outline" className="w-full flex items-center justify-center gap-2">
              <span>📅</span>
              Schedule Interviews
            </Button>
            <Button variant="outline" className="w-full flex items-center justify-center gap-2">
              <span>📊</span>
              View Analytics
            </Button>
          </div>
        </Card>

        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>Hiring Tips</h3>
          <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
            <div className="flex items-start space-x-3">
              <span className="text-2xl">💡</span>
              <div>
                <h4 className="font-semibold text-blue-900 dark:text-blue-100">Tip of the Day</h4>
                <p className="text-blue-800 dark:text-blue-200 mt-1">
                  Create detailed job descriptions to attract the right candidates. Include specific requirements and company culture details.
                </p>
              </div>
            </div>
          </div>
        </Card>
      </div>

      {/* Recent Activity */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>Recent Activity</h3>
        <div className="text-center py-8">
          <span className="text-4xl mb-4 block">📊</span>
          <p style={{ color: 'var(--text-muted)' }}>Activity feed will be displayed here</p>
        </div>
      </Card>
    </div>
  );
}