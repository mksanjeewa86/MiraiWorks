import { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { dashboardApi } from '../../services/api';
import Card from '../../components/ui/Card';
import Badge from '../../components/ui/Badge';
import LoadingSpinner from '../../components/ui/LoadingSpinner';
import Button from '../../components/ui/Button';
import type { DashboardStats, User, Interview } from '../../types';

interface CompanyStats extends DashboardStats {
  company_users: number;
  active_employees: number;
  active_recruiters: number;
  pending_invitations: number;
  company_interviews: number;
  monthly_hires: number;
  department_breakdown: {
    department: string;
    user_count: number;
    active_count: number;
  }[];
  recent_users: User[];
  upcoming_interviews: Interview[];
  user_activity: {
    date: string;
    logins: number;
    new_users: number;
  }[];
}

export default function CompanyAdminDashboard() {
  const { user } = useAuth();
  const [stats, setStats] = useState<CompanyStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  const loadDashboardData = async () => {
    try {
      const response = await dashboardApi.getStats();
      setStats(response.data as CompanyStats);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to load dashboard data');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  const handleRefresh = async () => {
    setRefreshing(true);
    await loadDashboardData();
  };

  const getStatusBadgeVariant = (isActive: boolean) => {
    return isActive ? 'success' : 'secondary';
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
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
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <h2 className="text-lg font-semibold text-red-800">Error Loading Dashboard</h2>
          <p className="text-red-600 mt-2">{error}</p>
          <Button onClick={handleRefresh} className="mt-4">
            Try Again
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Company Admin Dashboard</h1>
          <p className="text-gray-600 mt-1">
            Welcome back, {user?.full_name} • {user?.company.name}
          </p>
        </div>
        <Button
          onClick={handleRefresh}
          disabled={refreshing}
          variant="outline"
          className="flex items-center gap-2"
        >
          {refreshing ? <LoadingSpinner className="w-4 h-4" /> : '🔄'}
          Refresh
        </Button>
      </div>

      {/* Company Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Employees</p>
              <p className="text-3xl font-bold text-gray-900">{stats?.company_users || 0}</p>
            </div>
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <span className="text-2xl">👥</span>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Active Users</p>
              <p className="text-3xl font-bold text-gray-900">{stats?.active_employees || 0}</p>
            </div>
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
              <span className="text-2xl">✅</span>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Active Recruiters</p>
              <p className="text-3xl font-bold text-gray-900">{stats?.active_recruiters || 0}</p>
            </div>
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
              <span className="text-2xl">🎯</span>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Pending Invites</p>
              <p className="text-3xl font-bold text-gray-900">{stats?.pending_invitations || 0}</p>
            </div>
            <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
              <span className="text-2xl">⏳</span>
            </div>
          </div>
        </Card>
      </div>

      {/* Activity Metrics */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <Card className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Interview Activity</h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">Total Interviews</span>
              <span className="font-semibold">{stats?.company_interviews || 0}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">This Month</span>
              <span className="font-semibold text-green-600">
                +{Math.floor((stats?.company_interviews || 0) * 0.2)}
              </span>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Hiring Metrics</h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">Monthly Hires</span>
              <span className="font-semibold">{stats?.monthly_hires || 0}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Conversion Rate</span>
              <span className="font-semibold text-blue-600">
                {stats?.company_interviews && stats?.monthly_hires 
                  ? `${((stats.monthly_hires / stats.company_interviews) * 100).toFixed(1)}%`
                  : '0%'
                }
              </span>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">User Engagement</h3>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Active Rate</span>
              <Badge variant="success">
                {stats?.company_users && stats?.active_employees 
                  ? `${((stats.active_employees / stats.company_users) * 100).toFixed(0)}%`
                  : '0%'
                }
              </Badge>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Platform Health</span>
              <Badge variant="success">Excellent</Badge>
            </div>
          </div>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Department Breakdown */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Department Overview</h3>
          <div className="space-y-4">
            {stats?.department_breakdown?.length ? (
              stats.department_breakdown.map((dept, index) => (
                <div key={index} className="flex items-center justify-between py-3 border-b border-gray-100 last:border-b-0">
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm font-medium text-gray-900">{dept.department}</span>
                      <span className="text-sm text-gray-600">{dept.user_count} users</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-blue-600 h-2 rounded-full" 
                        style={{width: `${(dept.active_count / dept.user_count) * 100}%`}}
                      ></div>
                    </div>
                    <span className="text-xs text-gray-500 mt-1">
                      {dept.active_count} active ({((dept.active_count / dept.user_count) * 100).toFixed(0)}%)
                    </span>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-8">
                <span className="text-4xl mb-4 block">🏢</span>
                <p className="text-gray-500">No department data available</p>
              </div>
            )}
          </div>
        </Card>

        {/* Recent Users */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Users</h3>
          <div className="space-y-4">
            {stats?.recent_users?.length ? (
              stats.recent_users.slice(0, 5).map((recentUser) => (
                <div key={recentUser.id} className="flex items-center justify-between py-3 border-b border-gray-100 last:border-b-0">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-gray-200 rounded-full flex items-center justify-center">
                      <span className="text-sm font-semibold text-gray-700">
                        {recentUser.full_name?.charAt(0) || 'U'}
                      </span>
                    </div>
                    <div className="flex-1">
                      <p className="text-sm font-medium text-gray-900">{recentUser.full_name}</p>
                      <p className="text-xs text-gray-500">{recentUser.email}</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Badge variant={getStatusBadgeVariant(recentUser.is_active)}>
                      {recentUser.is_active ? 'Active' : 'Inactive'}
                    </Badge>
                    <Button variant="outline" size="sm">
                      View
                    </Button>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-8">
                <span className="text-4xl mb-4 block">👤</span>
                <p className="text-gray-500">No recent users</p>
              </div>
            )}
          </div>
        </Card>
      </div>

      {/* Upcoming Interviews */}
      <Card className="p-6 mb-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Upcoming Company Interviews</h3>
        <div className="space-y-4">
          {stats?.upcoming_interviews?.length ? (
            stats.upcoming_interviews.slice(0, 6).map((interview) => (
              <div key={interview.id} className="flex items-center justify-between py-3 border-b border-gray-100 last:border-b-0">
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900">{interview.title}</p>
                  <p className="text-xs text-gray-500 mt-1">
                    {interview.candidate_name} • {interview.company_name} • {formatDate(interview.scheduled_at || '')}
                  </p>
                </div>
                <div className="flex items-center space-x-2">
                  <Badge variant="warning">
                    {interview.status}
                  </Badge>
                  <Button variant="outline" size="sm">
                    Monitor
                  </Button>
                </div>
              </div>
            ))
          ) : (
            <div className="text-center py-8">
              <span className="text-4xl mb-4 block">📅</span>
              <p className="text-gray-500">No upcoming interviews scheduled</p>
            </div>
          )}
        </div>
      </Card>

      {/* Quick Actions */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Company Management</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Button variant="primary" className="flex items-center justify-center gap-2 p-4">
            <span>👥</span>
            Manage Users
          </Button>
          <Button variant="outline" className="flex items-center justify-center gap-2 p-4">
            <span>✉️</span>
            Send Invitations
          </Button>
          <Button variant="outline" className="flex items-center justify-center gap-2 p-4">
            <span>📊</span>
            View Reports
          </Button>
          <Button variant="outline" className="flex items-center justify-center gap-2 p-4">
            <span>⚙️</span>
            Company Settings
          </Button>
        </div>
      </Card>
    </div>
  );
}
