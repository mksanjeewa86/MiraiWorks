import { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { dashboardApi } from '../../services/api';
import Card from '../../components/ui/Card';
import Badge from '../../components/ui/Badge';
import LoadingSpinner from '../../components/ui/LoadingSpinner';
import Button from '../../components/ui/Button';
import type { DashboardStats, Interview, User } from '../../types';

interface RecruiterStats extends DashboardStats {
  active_candidates: number;
  interviews_this_week: number;
  pending_proposals: number;
  placement_rate: number;
  recent_interviews: Interview[];
  top_candidates: User[];
  interview_pipeline: {
    stage: string;
    count: number;
    conversion_rate: number;
  }[];
  monthly_metrics: {
    month: string;
    placements: number;
    interviews: number;
  }[];
}

export default function RecruiterDashboard() {
  const { user } = useAuth();
  const [stats, setStats] = useState<RecruiterStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadDashboardData = async () => {
    try {
      const response = await dashboardApi.getStats();
      setStats(response.data as RecruiterStats);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'scheduled':
      case 'pending':
        return 'warning';
      case 'completed':
      case 'confirmed':
        return 'success';
      case 'cancelled':
      case 'rejected':
        return 'error';
      default:
        return 'secondary';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatPercentage = (value: number) => {
    return `${(value * 100).toFixed(1)}%`;
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
        <h1 className="text-3xl font-bold text-gray-900">Recruiter Dashboard</h1>
        <p className="text-gray-600 mt-1">Hello {user?.full_name}, here's your recruitment overview.</p>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Active Candidates</p>
              <p className="text-3xl font-bold text-gray-900">{stats?.active_candidates || 0}</p>
            </div>
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <span className="text-2xl">👥</span>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Interviews This Week</p>
              <p className="text-3xl font-bold text-gray-900">{stats?.interviews_this_week || 0}</p>
            </div>
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
              <span className="text-2xl">📅</span>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Pending Proposals</p>
              <p className="text-3xl font-bold text-gray-900">{stats?.pending_proposals || 0}</p>
            </div>
            <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
              <span className="text-2xl">⏳</span>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Placement Rate</p>
              <p className="text-3xl font-bold text-gray-900">{formatPercentage(stats?.placement_rate || 0)}</p>
            </div>
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
              <span className="text-2xl">🎯</span>
            </div>
          </div>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Interview Pipeline */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Interview Pipeline</h3>
          <div className="space-y-4">
            {stats?.interview_pipeline?.length ? (
              stats.interview_pipeline.map((stage, index) => (
                <div key={index} className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm font-medium text-gray-900">{stage.stage}</span>
                      <span className="text-sm text-gray-600">{stage.count} candidates</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-blue-600 h-2 rounded-full" 
                        style={{width: `${stage.conversion_rate * 100}%`}}
                      ></div>
                    </div>
                    <span className="text-xs text-gray-500 mt-1">{formatPercentage(stage.conversion_rate)} conversion</span>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-8">
                <span className="text-4xl mb-4 block">📊</span>
                <p className="text-gray-500">No pipeline data available</p>
              </div>
            )}
          </div>
        </Card>

        {/* Monthly Performance */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Monthly Performance</h3>
          <div className="space-y-4">
            {stats?.monthly_metrics?.length ? (
              stats.monthly_metrics.slice(0, 4).map((metric, index) => (
                <div key={index} className="flex items-center justify-between py-2">
                  <span className="text-sm font-medium text-gray-900">{metric.month}</span>
                  <div className="flex items-center space-x-4">
                    <div className="text-center">
                      <p className="text-sm font-bold text-green-600">{metric.placements}</p>
                      <p className="text-xs text-gray-500">Placed</p>
                    </div>
                    <div className="text-center">
                      <p className="text-sm font-bold text-blue-600">{metric.interviews}</p>
                      <p className="text-xs text-gray-500">Interviewed</p>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-8">
                <span className="text-4xl mb-4 block">📈</span>
                <p className="text-gray-500">No performance data yet</p>
              </div>
            )}
          </div>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Upcoming Interviews */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Upcoming Interviews</h3>
          <div className="space-y-4">
            {stats?.recent_interviews?.length ? (
              stats.recent_interviews.slice(0, 5).map((interview) => (
                <div key={interview.id} className="flex items-center justify-between py-3 border-b border-gray-100 last:border-b-0">
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">{interview.title}</p>
                    <p className="text-xs text-gray-500 mt-1">
                      {interview.candidate_name} • {formatDate(interview.scheduled_at || '')}
                    </p>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Badge variant={getStatusColor(interview.status)}>
                      {interview.status}
                    </Badge>
                    <Button variant="outline" size="sm">
                      View
                    </Button>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-8">
                <span className="text-4xl mb-4 block">📅</span>
                <p className="text-gray-500">No interviews scheduled</p>
                <Button className="mt-4" size="sm">
                  Schedule Interview
                </Button>
              </div>
            )}
          </div>
        </Card>

        {/* Top Candidates */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Top Candidates</h3>
          <div className="space-y-4">
            {stats?.top_candidates?.length ? (
              stats.top_candidates.slice(0, 5).map((candidate) => (
                <div key={candidate.id} className="flex items-center justify-between py-3 border-b border-gray-100 last:border-b-0">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-gray-200 rounded-full flex items-center justify-center">
                      <span className="text-sm font-semibold text-gray-700">
                        {candidate.full_name?.charAt(0) || 'C'}
                      </span>
                    </div>
                    <div className="flex-1">
                      <p className="text-sm font-medium text-gray-900">{candidate.full_name}</p>
                      <p className="text-xs text-gray-500">{candidate.email}</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Badge variant="success">Active</Badge>
                    <Button variant="outline" size="sm">
                      Contact
                    </Button>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-8">
                <span className="text-4xl mb-4 block">⭐</span>
                <p className="text-gray-500">No candidates yet</p>
                <Button className="mt-4" size="sm">
                  Find Candidates
                </Button>
              </div>
            )}
          </div>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Button variant="primary" className="flex items-center justify-center gap-2 p-4">
            <span>📅</span>
            Schedule Interview
          </Button>
          <Button variant="outline" className="flex items-center justify-center gap-2 p-4">
            <span>👥</span>
            Browse Candidates
          </Button>
          <Button variant="outline" className="flex items-center justify-center gap-2 p-4">
            <span>💼</span>
            Manage Jobs
          </Button>
          <Button variant="outline" className="flex items-center justify-center gap-2 p-4">
            <span>📊</span>
            View Reports
          </Button>
        </div>
      </Card>

      {/* Recruitment Tips */}
      <Card className="p-6 mt-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Recruitment Insights</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <div className="flex items-start space-x-3">
              <span className="text-2xl">📈</span>
              <div>
                <h4 className="font-semibold text-green-900">Performance Trend</h4>
                <p className="text-green-800 mt-1">
                  Your placement rate increased by 15% this month. Keep up the great work!
                </p>
              </div>
            </div>
          </div>
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-start space-x-3">
              <span className="text-2xl">💡</span>
              <div>
                <h4 className="font-semibold text-blue-900">Tip of the Week</h4>
                <p className="text-blue-800 mt-1">
                  Follow up within 24 hours after interviews to maintain candidate engagement.
                </p>
              </div>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
}