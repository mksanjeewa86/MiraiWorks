import { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { dashboardApi } from '../../services/api';
import Card from '../../components/ui/Card';
import Badge from '../../components/ui/Badge';
import LoadingSpinner from '../../components/ui/LoadingSpinner';
import Button from '../../components/ui/Button';
import type { DashboardStats, Interview, Resume } from '../../types';

interface CandidateStats extends DashboardStats {
  total_applications: number;
  interviews_scheduled: number;
  interviews_completed: number;
  resumes_created: number;
  recent_interviews: Interview[];
  recent_resumes: Resume[];
  application_stats: {
    status: string;
    count: number;
  }[];
}

export default function CandidateDashboard() {
  const { user } = useAuth();
  const [stats, setStats] = useState<CandidateStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadDashboardData = async () => {
    try {
      const response = await dashboardApi.getStats();
      setStats(response.data as CandidateStats);
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
      case 'accepted':
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
        <h1 className="text-3xl font-bold text-gray-900">Candidate Dashboard</h1>
        <p className="text-gray-600 mt-1">Welcome back, {user?.full_name}! Here's your career progress.</p>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Applications</p>
              <p className="text-3xl font-bold text-gray-900">{stats?.total_applications || 0}</p>
            </div>
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <span className="text-2xl">📝</span>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Interviews Scheduled</p>
              <p className="text-3xl font-bold text-gray-900">{stats?.interviews_scheduled || 0}</p>
            </div>
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
              <span className="text-2xl">📅</span>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Interviews Completed</p>
              <p className="text-3xl font-bold text-gray-900">{stats?.interviews_completed || 0}</p>
            </div>
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
              <span className="text-2xl">✅</span>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Resumes Created</p>
              <p className="text-3xl font-bold text-gray-900">{stats?.resumes_created || 0}</p>
            </div>
            <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
              <span className="text-2xl">📄</span>
            </div>
          </div>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Application Status Breakdown */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Application Status</h3>
          <div className="space-y-4">
            {stats?.application_stats?.length ? (
              stats.application_stats.map((stat, index) => (
                <div key={index} className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <Badge variant={getStatusColor(stat.status)}>
                      {stat.status}
                    </Badge>
                  </div>
                  <span className="font-semibold text-gray-900">{stat.count}</span>
                </div>
              ))
            ) : (
              <div className="text-center py-4">
                <span className="text-3xl mb-2 block">💼</span>
                <p className="text-gray-500">No applications yet</p>
                <Button className="mt-4" size="sm">
                  Start Applying
                </Button>
              </div>
            )}
          </div>
        </Card>

        {/* Progress Chart */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">This Month's Progress</h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Applications Sent</span>
              <div className="flex items-center space-x-2">
                <div className="w-24 bg-gray-200 rounded-full h-2">
                  <div className="bg-blue-600 h-2 rounded-full" style={{width: '65%'}}></div>
                </div>
                <span className="text-sm font-semibold">13/20</span>
              </div>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Interviews Attended</span>
              <div className="flex items-center space-x-2">
                <div className="w-24 bg-gray-200 rounded-full h-2">
                  <div className="bg-green-600 h-2 rounded-full" style={{width: '80%'}}></div>
                </div>
                <span className="text-sm font-semibold">4/5</span>
              </div>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Resume Updates</span>
              <div className="flex items-center space-x-2">
                <div className="w-24 bg-gray-200 rounded-full h-2">
                  <div className="bg-purple-600 h-2 rounded-full" style={{width: '40%'}}></div>
                </div>
                <span className="text-sm font-semibold">2/5</span>
              </div>
            </div>
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
                      {interview.company_name} • {formatDate(interview.scheduled_at || '')}
                    </p>
                  </div>
                  <Badge variant={getStatusColor(interview.status)}>
                    {interview.status}
                  </Badge>
                </div>
              ))
            ) : (
              <div className="text-center py-8">
                <span className="text-4xl mb-4 block">📅</span>
                <p className="text-gray-500">No interviews scheduled</p>
                <Button variant="outline" className="mt-4" size="sm">
                  Schedule Interview
                </Button>
              </div>
            )}
          </div>
        </Card>

        {/* Recent Resume Activity */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Resumes</h3>
          <div className="space-y-4">
            {stats?.recent_resumes?.length ? (
              stats.recent_resumes.slice(0, 5).map((resume) => (
                <div key={resume.id} className="flex items-center justify-between py-3 border-b border-gray-100 last:border-b-0">
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">{resume.title}</p>
                    <p className="text-xs text-gray-500 mt-1">
                      Updated {formatDate(resume.updated_at)}
                    </p>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Badge variant={resume.is_public ? 'success' : 'secondary'}>
                      {resume.is_public ? 'Public' : 'Private'}
                    </Badge>
                    <Button variant="outline" size="sm">
                      Edit
                    </Button>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-8">
                <span className="text-4xl mb-4 block">📄</span>
                <p className="text-gray-500">No resumes created yet</p>
                <Button className="mt-4" size="sm">
                  Create Resume
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
            <span>📝</span>
            Create Resume
          </Button>
          <Button variant="outline" className="flex items-center justify-center gap-2 p-4">
            <span>🔍</span>
            Browse Jobs
          </Button>
          <Button variant="outline" className="flex items-center justify-center gap-2 p-4">
            <span>📅</span>
            Schedule Interview
          </Button>
          <Button variant="outline" className="flex items-center justify-center gap-2 p-4">
            <span>💬</span>
            Message Recruiter
          </Button>
        </div>
      </Card>

      {/* Career Tips */}
      <Card className="p-6 mt-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Career Tips</h3>
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-start space-x-3">
            <span className="text-2xl">💡</span>
            <div>
              <h4 className="font-semibold text-blue-900">Tip of the Day</h4>
              <p className="text-blue-800 mt-1">
                Keep your resume updated regularly. Employers value candidates who showcase their latest achievements and skills.
              </p>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
}