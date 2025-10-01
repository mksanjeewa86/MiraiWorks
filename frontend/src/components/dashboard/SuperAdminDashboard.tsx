'use client';

import { useState, useEffect } from 'react';
import { dashboardApi } from '@/api/dashboard';
import { Card } from '@/components/ui';
import { Badge } from '@/components/ui';
import { LoadingSpinner } from '@/components/ui';
import { Button } from '@/components/ui';
import {
  Building2,
  Users,
  Activity,
  Shield,
  Database,
  Server,
  AlertTriangle,
  TrendingUp,
  BarChart3,
  Settings,
  UserCog,
} from 'lucide-react';
import { SuperAdminStats } from '@/types/dashboard';

export default function SuperAdminDashboard() {
  const [stats, setStats] = useState<SuperAdminStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadDashboardData = async () => {
    try {
      const response = await dashboardApi.getStats();
      setStats(response.data as SuperAdminStats);
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

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'healthy':
        return 'success';
      case 'warning':
        return 'warning';
      case 'error':
        return 'error';
      default:
        return 'secondary';
    }
  };

  const getLogIcon = (level: string) => {
    switch (level.toLowerCase()) {
      case 'error':
        return <AlertTriangle className="h-4 w-4 text-red-600" />;
      case 'warning':
        return <AlertTriangle className="h-4 w-4 text-yellow-600" />;
      default:
        return <Activity className="h-4 w-4 text-blue-600" />;
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
      {/* Platform Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium" style={{ color: 'var(--text-secondary)' }}>
                Total Companies
              </p>
              <p className="text-3xl font-bold" style={{ color: 'var(--text-primary)' }}>
                {stats?.total_companies || 0}
              </p>
            </div>
            <div
              className="w-12 h-12 rounded-lg flex items-center justify-center"
              style={{ backgroundColor: 'rgba(34, 197, 94, 0.1)' }}
            >
              <Building2 className="h-6 w-6 text-green-600" />
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium" style={{ color: 'var(--text-secondary)' }}>
                Total Users
              </p>
              <p className="text-3xl font-bold" style={{ color: 'var(--text-primary)' }}>
                {stats?.total_users || 0}
              </p>
            </div>
            <div
              className="w-12 h-12 rounded-lg flex items-center justify-center"
              style={{ backgroundColor: 'rgba(59, 130, 246, 0.1)' }}
            >
              <Users className="h-6 w-6 text-blue-600" />
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium" style={{ color: 'var(--text-secondary)' }}>
                Total Positions
              </p>
              <p className="text-3xl font-bold" style={{ color: 'var(--text-primary)' }}>
                {stats?.total_positions || 0}
              </p>
            </div>
            <div
              className="w-12 h-12 rounded-lg flex items-center justify-center"
              style={{ backgroundColor: 'rgba(168, 85, 247, 0.1)' }}
            >
              <BarChart3 className="h-6 w-6 text-purple-600" />
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium" style={{ color: 'var(--text-secondary)' }}>
                Total Applications
              </p>
              <p className="text-3xl font-bold" style={{ color: 'var(--text-primary)' }}>
                {stats?.total_applications || 0}
              </p>
            </div>
            <div
              className="w-12 h-12 rounded-lg flex items-center justify-center"
              style={{ backgroundColor: 'rgba(251, 146, 60, 0.1)' }}
            >
              <TrendingUp className="h-6 w-6 text-orange-600" />
            </div>
          </div>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* System Health */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>
            System Health
          </h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <Database className="h-4 w-4" />
                <span>Database Status</span>
              </div>
              <Badge variant={getStatusColor(stats?.system_health?.database_status || 'healthy')}>
                {stats?.system_health?.database_status || 'healthy'}
              </Badge>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <Server className="h-4 w-4" />
                <span>API Response Time</span>
              </div>
              <span className="font-semibold" style={{ color: 'var(--text-primary)' }}>
                {stats?.system_health?.api_response_time || 0}ms
              </span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <Activity className="h-4 w-4" />
                <span>Active Sessions</span>
              </div>
              <span className="font-semibold" style={{ color: 'var(--text-primary)' }}>
                {stats?.system_health?.active_sessions || 0}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <AlertTriangle className="h-4 w-4" />
                <span>Error Rate</span>
              </div>
              <span className="font-semibold" style={{ color: 'var(--text-primary)' }}>
                {stats?.system_health?.error_rate || 0}%
              </span>
            </div>
          </div>
        </Card>

        {/* Platform Metrics */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>
            Platform Metrics
          </h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span>Daily Signups</span>
              <span className="font-semibold" style={{ color: 'var(--text-primary)' }}>
                {stats?.platform_metrics?.daily_signups || 0}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span>Weekly Signups</span>
              <span className="font-semibold" style={{ color: 'var(--text-primary)' }}>
                {stats?.platform_metrics?.weekly_signups || 0}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span>Monthly Signups</span>
              <span className="font-semibold" style={{ color: 'var(--text-primary)' }}>
                {stats?.platform_metrics?.monthly_signups || 0}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span>Conversion Rate</span>
              <span className="font-semibold" style={{ color: 'var(--text-primary)' }}>
                {stats?.platform_metrics?.conversion_rate || 0}%
              </span>
            </div>
          </div>
        </Card>
      </div>

      {/* Recent System Logs */}
      <Card className="p-6 mb-8">
        <h3 className="text-lg font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>
          Recent System Logs
        </h3>
        <div className="space-y-3">
          {stats?.recent_system_logs?.length ? (
            stats.recent_system_logs.slice(0, 6).map((log) => (
              <div
                key={log.id}
                className="flex items-start space-x-3 py-3 border-b border-gray-100 dark:border-gray-800 last:border-b-0"
              >
                <div className="flex-shrink-0 mt-1">{getLogIcon(log.level)}</div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>
                    {log.message}
                  </p>
                  <p className="text-xs mt-1" style={{ color: 'var(--text-muted)' }}>
                    {log.source} • {formatDate(log.timestamp)}
                  </p>
                </div>
                <Badge
                  variant={
                    log.level === 'error'
                      ? 'error'
                      : log.level === 'warning'
                        ? 'warning'
                        : 'secondary'
                  }
                >
                  {log.level}
                </Badge>
              </div>
            ))
          ) : (
            <div className="text-center py-8">
              <Activity className="h-12 w-12 mx-auto mb-4" style={{ color: 'var(--text-muted)' }} />
              <p style={{ color: 'var(--text-muted)' }}>No recent system logs</p>
            </div>
          )}
        </div>
      </Card>

      {/* Quick Actions */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>
          Quick Actions
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Button className="flex items-center justify-center gap-2 p-4">
            <Building2 className="h-4 w-4" />
            Manage Companies
          </Button>
          <Button variant="outline" className="flex items-center justify-center gap-2 p-4">
            <UserCog className="h-4 w-4" />
            User Management
          </Button>
          <Button variant="outline" className="flex items-center justify-center gap-2 p-4">
            <Shield className="h-4 w-4" />
            Security Settings
          </Button>
          <Button variant="outline" className="flex items-center justify-center gap-2 p-4">
            <Settings className="h-4 w-4" />
            System Settings
          </Button>
        </div>
      </Card>
    </div>
  );
}
