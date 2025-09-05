import { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { dashboardApi } from '../../services/api';
import Card from '../../components/ui/Card';
import Badge from '../../components/ui/Badge';
import LoadingSpinner from '../../components/ui/LoadingSpinner';
import Button from '../../components/ui/Button';
import type { DashboardStats, Interview } from '../../types';

interface EmployerStats extends DashboardStats {
  active_job_postings: number;
  total_applications: number;
  interviews_scheduled: number;
  hired_candidates: number;
  open_positions: {
    title: string;
    department: string;
    applications: number;
    status: 'open' | 'paused' | 'closed';
  }[];
  recent_applications: {
    id: number;
    candidate_name: string;
    position_title: string;
    applied_at: string;
    status: 'pending' | 'reviewing' | 'interview' | 'hired' | 'rejected';
  }[];
  upcoming_interviews: Interview[];
  hiring_funnel: {
    stage: string;
    count: number;
    conversion_rate: number;
  }[];
  time_to_hire: number;
  offer_acceptance_rate: number;
}

export default function EmployerDashboard() {
  const { user } = useAuth();
  const [stats, setStats] = useState<EmployerStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  const loadDashboardData = async () => {
    try {
      const response = await dashboardApi.getStats();
      setStats(response.data as EmployerStats);
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

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'open':
      case 'pending':
      case 'reviewing':
        return 'warning';
      case 'hired':
      case 'interview':
        return 'success';
      case 'rejected':
      case 'closed':
      case 'paused':
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
          <h1 className="text-3xl font-bold text-gray-900">Employer Dashboard</h1>
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

      {/* Hiring Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Active Job Postings</p>
              <p className="text-3xl font-bold text-gray-900">{stats?.active_job_postings || 0}</p>
            </div>
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <span className="text-2xl">💼</span>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Applications</p>
              <p className="text-3xl font-bold text-gray-900">{stats?.total_applications || 0}</p>
            </div>
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
              <span className="text-2xl">📄</span>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Interviews Scheduled</p>
              <p className="text-3xl font-bold text-gray-900">{stats?.interviews_scheduled || 0}</p>
            </div>
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
              <span className="text-2xl">📅</span>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Hired Candidates</p>
              <p className="text-3xl font-bold text-gray-900">{stats?.hired_candidates || 0}</p>
            </div>
            <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
              <span className="text-2xl">🎉</span>
            </div>
          </div>
        </Card>
      </div>

      {/* Hiring Metrics */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <Card className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Hiring Performance</h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">Time to Hire</span>
              <span className="font-semibold">{stats?.time_to_hire || 0} days</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Offer Acceptance Rate</span>
              <span className="font-semibold text-green-600">
                {formatPercentage(stats?.offer_acceptance_rate || 0)}
              </span>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Application Quality</h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">Interview Rate</span>
              <span className="font-semibold text-blue-600">
                {stats?.total_applications && stats?.interviews_scheduled 
                  ? formatPercentage(stats.interviews_scheduled / stats.total_applications)
                  : '0%'
                }
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Hire Rate</span>
              <span className="font-semibold text-purple-600">
                {stats?.interviews_scheduled && stats?.hired_candidates 
                  ? formatPercentage(stats.hired_candidates / stats.interviews_scheduled)
                  : '0%'
                }
              </span>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Recruitment Health</h3>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Pipeline Status</span>
              <Badge variant="success">Healthy</Badge>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Talent Pool</span>
              <Badge variant="success">Active</Badge>
            </div>
          </div>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Open Positions */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Open Positions</h3>
          <div className="space-y-4">
            {stats?.open_positions?.length ? (
              stats.open_positions.slice(0, 5).map((position, index) => (
                <div key={index} className="flex items-center justify-between py-3 border-b border-gray-100 last:border-b-0">
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">{position.title}</p>
                    <p className="text-xs text-gray-500 mt-1">
                      {position.department} • {position.applications} applications
                    </p>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Badge variant={getStatusColor(position.status)}>
                      {position.status}
                    </Badge>
                    <Button variant="outline" size="sm">
                      View
                    </Button>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-8">
                <span className="text-4xl mb-4 block">💼</span>
                <p className="text-gray-500">No open positions</p>
                <Button className="mt-4" size="sm">
                  Post Job
                </Button>
              </div>
            )}
          </div>
        </Card>

        {/* Hiring Funnel */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Hiring Funnel</h3>
          <div className="space-y-4">
            {stats?.hiring_funnel?.length ? (
              stats.hiring_funnel.map((stage, index) => (
                <div key={index} className="flex items-center justify-between py-2">
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
                    <span className="text-xs text-gray-500 mt-1">
                      {formatPercentage(stage.conversion_rate)} conversion
                    </span>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-8">
                <span className="text-4xl mb-4 block">📊</span>
                <p className="text-gray-500">No funnel data available</p>
              </div>
            )}
          </div>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Recent Applications */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Applications</h3>
          <div className="space-y-4">
            {stats?.recent_applications?.length ? (
              stats.recent_applications.slice(0, 6).map((application) => (
                <div key={application.id} className="flex items-center justify-between py-3 border-b border-gray-100 last:border-b-0">
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">{application.candidate_name}</p>
                    <p className="text-xs text-gray-500 mt-1">
                      {application.position_title} • {formatDate(application.applied_at)}
                    </p>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Badge variant={getStatusColor(application.status)}>
                      {application.status}
                    </Badge>
                    <Button variant="outline" size="sm">
                      Review
                    </Button>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-8">
                <span className="text-4xl mb-4 block">📝</span>
                <p className="text-gray-500">No recent applications</p>
              </div>
            )}
          </div>
        </Card>

        {/* Upcoming Interviews */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Upcoming Interviews</h3>
          <div className="space-y-4">
            {stats?.upcoming_interviews?.length ? (
              stats.upcoming_interviews.slice(0, 6).map((interview) => (
                <div key={interview.id} className="flex items-center justify-between py-3 border-b border-gray-100 last:border-b-0">
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">{interview.title}</p>
                    <p className="text-xs text-gray-500 mt-1">
                      {interview.candidate_name} • {formatDate(interview.scheduled_at || '')}
                    </p>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Badge variant="warning">
                      {interview.status}
                    </Badge>
                    <Button variant="outline" size="sm">
                      Join
                    </Button>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-8">
                <span className="text-4xl mb-4 block">📅</span>
                <p className="text-gray-500">No upcoming interviews</p>
                <Button className="mt-4" size="sm">
                  Schedule Interview
                </Button>
              </div>
            )}
          </div>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card className="p-6 mb-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Button variant="primary" className="flex items-center justify-center gap-2 p-4">
            <span>💼</span>
            Post New Job
          </Button>
          <Button variant="outline" className="flex items-center justify-center gap-2 p-4">
            <span>📄</span>
            Review Applications
          </Button>
          <Button variant="outline" className="flex items-center justify-center gap-2 p-4">
            <span>📅</span>
            Schedule Interview
          </Button>
          <Button variant="outline" className="flex items-center justify-center gap-2 p-4">
            <span>📊</span>
            View Analytics
          </Button>
        </div>
      </Card>

      {/* Hiring Insights */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Hiring Insights</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-start space-x-3">
              <span className="text-2xl">🎯</span>
              <div>
                <h4 className="font-semibold text-blue-900">Quality Improvement</h4>
                <p className="text-blue-800 mt-1">
                  Your interview-to-hire ratio is above industry average. Great job screening candidates!
                </p>
              </div>
            </div>
          </div>
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <div className="flex items-start space-x-3">
              <span className="text-2xl">⚡</span>
              <div>
                <h4 className="font-semibold text-green-900">Speed Optimization</h4>
                <p className="text-green-800 mt-1">
                  Consider streamlining your hiring process to reduce time-to-hire by 20%.
                </p>
              </div>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
}
