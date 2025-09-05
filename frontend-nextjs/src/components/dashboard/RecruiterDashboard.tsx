'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { dashboardApi } from '@/services/api';
import Card from '@/components/ui/Card';
import Badge from '@/components/ui/Badge';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import Button from '@/components/ui/Button';
import type { DashboardStats, Interview, User } from '@/types';

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
      setError(err.message || 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  const formatPercentage = (value: number) => {
    return `${(value * 100).toFixed(1)}%`;
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
        <h1 className="text-3xl font-bold" style={{ color: 'var(--text-primary)' }}>Recruiter Dashboard</h1>
        <p className="mt-1" style={{ color: 'var(--text-secondary)' }}>Hello {user?.full_name}, here's your recruitment overview.</p>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium" style={{ color: 'var(--text-secondary)' }}>Active Candidates</p>
              <p className="text-3xl font-bold" style={{ color: 'var(--text-primary)' }}>{stats?.active_candidates || 0}</p>
            </div>
            <div className="w-12 h-12 rounded-lg flex items-center justify-center" style={{ backgroundColor: 'rgba(108, 99, 255, 0.1)' }}>
              <span className="text-2xl">👥</span>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium" style={{ color: 'var(--text-secondary)' }}>Interviews This Week</p>
              <p className="text-3xl font-bold" style={{ color: 'var(--text-primary)' }}>{stats?.interviews_this_week || 0}</p>
            </div>
            <div className="w-12 h-12 rounded-lg flex items-center justify-center" style={{ backgroundColor: 'rgba(34, 197, 94, 0.1)' }}>
              <span className="text-2xl">📅</span>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium" style={{ color: 'var(--text-secondary)' }}>Pending Proposals</p>
              <p className="text-3xl font-bold" style={{ color: 'var(--text-primary)' }}>{stats?.pending_proposals || 0}</p>
            </div>
            <div className="w-12 h-12 rounded-lg flex items-center justify-center" style={{ backgroundColor: 'rgba(251, 146, 60, 0.1)' }}>
              <span className="text-2xl">⏳</span>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium" style={{ color: 'var(--text-secondary)' }}>Placement Rate</p>
              <p className="text-3xl font-bold" style={{ color: 'var(--text-primary)' }}>{formatPercentage(stats?.placement_rate || 0)}</p>
            </div>
            <div className="w-12 h-12 rounded-lg flex items-center justify-center" style={{ backgroundColor: 'rgba(168, 85, 247, 0.1)' }}>
              <span className="text-2xl">🎯</span>
            </div>
          </div>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Interview Pipeline */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>Interview Pipeline</h3>
          <div className="space-y-4">
            {stats?.interview_pipeline?.length ? (
              stats.interview_pipeline.map((stage, index) => (
                <div key={index} className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>{stage.stage}</span>
                      <span className="text-sm" style={{ color: 'var(--text-secondary)' }}>{stage.count} candidates</span>
                    </div>
                    <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                      <div 
                        className="bg-brand-primary h-2 rounded-full" 
                        style={{width: `${stage.conversion_rate * 100}%`}}
                      ></div>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-4">
                <span className="text-3xl mb-2 block">📊</span>
                <p style={{ color: 'var(--text-muted)' }}>No pipeline data available</p>
              </div>
            )}
          </div>
        </Card>

        {/* Quick Actions */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>Quick Actions</h3>
          <div className="space-y-3">
            <Button className="w-full flex items-center justify-center gap-2">
              <span>👥</span>
              Search Candidates
            </Button>
            <Button variant="outline" className="w-full flex items-center justify-center gap-2">
              <span>📅</span>
              Schedule Interview
            </Button>
            <Button variant="outline" className="w-full flex items-center justify-center gap-2">
              <span>📝</span>
              Create Job Posting
            </Button>
            <Button variant="outline" className="w-full flex items-center justify-center gap-2">
              <span>📊</span>
              View Reports
            </Button>
          </div>
        </Card>
      </div>

      {/* Recent Activity */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>Recent Interviews</h3>
        <div className="space-y-4">
          {stats?.recent_interviews?.length ? (
            stats.recent_interviews.slice(0, 5).map((interview) => (
              <div key={interview.id} className="flex items-center justify-between py-3 border-b border-gray-100 dark:border-gray-800 last:border-b-0">
                <div className="flex-1">
                  <p className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>{interview.title}</p>
                  <p className="text-xs mt-1" style={{ color: 'var(--text-muted)' }}>
                    {formatDate(interview.scheduled_at || '')}
                  </p>
                </div>
                <Badge variant="primary">
                  {interview.status}
                </Badge>
              </div>
            ))
          ) : (
            <div className="text-center py-8">
              <span className="text-4xl mb-4 block">📅</span>
              <p style={{ color: 'var(--text-muted)' }}>No recent interviews</p>
            </div>
          )}
        </div>
      </Card>
    </div>
  );
}