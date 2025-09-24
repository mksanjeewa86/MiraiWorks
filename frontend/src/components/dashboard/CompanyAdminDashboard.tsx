'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { dashboardApi } from '@/api/dashboard';
import Card from '@/components/ui/card';
import Badge from '@/components/ui/badge';
import LoadingSpinner from '@/components/ui/loading-spinner';
import Button from '@/components/ui/button';
import {
  Users,
  Building2,
  UserCheck,
  UserX,
  Activity,
  TrendingUp,
  Calendar,
  MessageSquare,
} from 'lucide-react';
import { CompanyAdminStats } from '@/types/dashboard';

export default function CompanyAdminDashboard() {
  const {} = useAuth();
  const [stats, setStats] = useState<CompanyAdminStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadDashboardData = async () => {
    try {
      const response = await dashboardApi.getStats();
      setStats(response.data as CompanyAdminStats);
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

  const getActivityIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'user_created':
        return <UserCheck className="h-4 w-4 text-green-600" />;
      case 'user_deactivated':
        return <UserX className="h-4 w-4 text-red-600" />;
      case 'position_created':
        return <Building2 className="h-4 w-4 text-blue-600" />;
      case 'interview_scheduled':
        return <Calendar className="h-4 w-4 text-purple-600" />;
      default:
        return <Activity className="h-4 w-4 text-gray-600" />;
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

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
          <h2 className="text-lg font-semibold text-red-800 dark:text-red-200">
            Error Loading Dashboard
          </h2>
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
      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium" style={{ color: 'var(--text-secondary)' }}>
                Total Employees
              </p>
              <p className="text-3xl font-bold" style={{ color: 'var(--text-primary)' }}>
                {stats?.total_employees || 0}
              </p>
            </div>
            <div
              className="w-12 h-12 rounded-lg flex items-center justify-center"
              style={{ backgroundColor: 'rgba(34, 197, 94, 0.1)' }}
            >
              <Users className="h-6 w-6 text-green-600" />
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium" style={{ color: 'var(--text-secondary)' }}>
                Active Positions
              </p>
              <p className="text-3xl font-bold" style={{ color: 'var(--text-primary)' }}>
                {stats?.active_positions || 0}
              </p>
            </div>
            <div
              className="w-12 h-12 rounded-lg flex items-center justify-center"
              style={{ backgroundColor: 'rgba(59, 130, 246, 0.1)' }}
            >
              <Building2 className="h-6 w-6 text-blue-600" />
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium" style={{ color: 'var(--text-secondary)' }}>
                Applications
              </p>
              <p className="text-3xl font-bold" style={{ color: 'var(--text-primary)' }}>
                {stats?.total_applications || 0}
              </p>
            </div>
            <div
              className="w-12 h-12 rounded-lg flex items-center justify-center"
              style={{ backgroundColor: 'rgba(168, 85, 247, 0.1)' }}
            >
              <TrendingUp className="h-6 w-6 text-purple-600" />
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium" style={{ color: 'var(--text-secondary)' }}>
                Interviews Scheduled
              </p>
              <p className="text-3xl font-bold" style={{ color: 'var(--text-primary)' }}>
                {stats?.interviews_scheduled || 0}
              </p>
            </div>
            <div
              className="w-12 h-12 rounded-lg flex items-center justify-center"
              style={{ backgroundColor: 'rgba(251, 146, 60, 0.1)' }}
            >
              <Calendar className="h-6 w-6 text-orange-600" />
            </div>
          </div>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Employee Status */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>
            Employee Status
          </h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <Badge variant="success">Active</Badge>
              </div>
              <span className="font-semibold" style={{ color: 'var(--text-primary)' }}>
                {stats?.active_employees || 0}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <Badge variant="warning">Pending</Badge>
              </div>
              <span className="font-semibold" style={{ color: 'var(--text-primary)' }}>
                {stats?.pending_employees || 0}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <Badge variant="secondary">Recruiters</Badge>
              </div>
              <span className="font-semibold" style={{ color: 'var(--text-primary)' }}>
                {stats?.total_recruiters || 0}
              </span>
            </div>
          </div>
        </Card>

        {/* Recent Activities */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>
            Recent Activities
          </h3>
          <div className="space-y-4">
            {stats?.recent_activities?.length ? (
              stats.recent_activities.slice(0, 5).map((activity) => (
                <div
                  key={activity.id}
                  className="flex items-start space-x-3 py-3 border-b border-gray-100 dark:border-gray-800 last:border-b-0"
                >
                  <div className="flex-shrink-0 mt-1">{getActivityIcon(activity.type)}</div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>
                      {activity.description}
                    </p>
                    <p className="text-xs mt-1" style={{ color: 'var(--text-muted)' }}>
                      by {activity.user_name} • {formatDate(activity.timestamp)}
                    </p>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-8">
                <Activity
                  className="h-12 w-12 mx-auto mb-4"
                  style={{ color: 'var(--text-muted)' }}
                />
                <p style={{ color: 'var(--text-muted)' }}>No recent activities</p>
              </div>
            )}
          </div>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>
          Quick Actions
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Button className="flex items-center justify-center gap-2 p-4">
            <Users className="h-4 w-4" />
            Manage Employees
          </Button>
          <Button variant="outline" className="flex items-center justify-center gap-2 p-4">
            <Building2 className="h-4 w-4" />
            Manage Positions
          </Button>
          <Button variant="outline" className="flex items-center justify-center gap-2 p-4">
            <UserCheck className="h-4 w-4" />
            Review Applications
          </Button>
          <Button variant="outline" className="flex items-center justify-center gap-2 p-4">
            <MessageSquare className="h-4 w-4" />
            Company Settings
          </Button>
        </div>
      </Card>
    </div>
  );
}
