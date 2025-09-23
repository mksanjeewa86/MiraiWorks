'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { dashboardApi } from "@/api/dashboard";
import Card from '@/components/ui/card';
import Badge from '@/components/ui/badge';
import LoadingSpinner from '@/components/ui/loading-spinner';
import Button from '@/components/ui/button';
import type { CandidateDashboardStats } from '@/types/dashboard';
import MBTITestButton from '@/components/mbti/MBTITestButton';
import MBTITestModal from '@/components/mbti/MBTITestModal';
import MBTIResultCard from '@/components/mbti/MBTIResultCard';
import { mbtiApi } from '@/api/mbti';
import type { MBTITestSummary } from '@/types/mbti';

export default function CandidateDashboard() {
  const { user } = useAuth();
  const [stats, setStats] = useState<CandidateDashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showMBTITest, setShowMBTITest] = useState(false);
  const [mbtiSummary, setMbtiSummary] = useState<MBTITestSummary | null>(null);
  const [mbtiLoading, setMbtiLoading] = useState(false);

  const loadDashboardData = async () => {
    try {
      const response = await dashboardApi.getStats();
      setStats(response.data as CandidateDashboardStats);
      setError(null);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
    loadMBTISummary();
  }, []);

  const loadMBTISummary = async () => {
    try {
      setMbtiLoading(true);

      // First check the test progress to avoid 404 errors
      const progress = await mbtiApi.getProgress();

      // Only try to get summary if test is completed
      if (progress.status === 'completed') {
        const summary = await mbtiApi.getSummary('ja');
        setMbtiSummary(summary);
      } else {
        // User hasn't completed the test yet - this is normal, no error needed
        setMbtiSummary(null);
      }
    } catch (err) {
      // Only log actual errors, not expected 404s
      console.log('Could not load MBTI data:', err);
      setMbtiSummary(null);
    } finally {
      setMbtiLoading(false);
    }
  };

  const handleMBTIComplete = async () => {
    await loadMBTISummary();
  };

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
        <h1 className="text-3xl font-bold" style={{ color: 'var(--text-primary)' }}>Candidate Dashboard</h1>
        <p className="mt-1" style={{ color: 'var(--text-secondary)' }}>Welcome back, {user?.full_name}! Here&apos;s your career progress.</p>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium" style={{ color: 'var(--text-secondary)' }}>Applications</p>
              <p className="text-3xl font-bold" style={{ color: 'var(--text-primary)' }}>{stats?.total_applications || 0}</p>
            </div>
            <div className="w-12 h-12 rounded-lg flex items-center justify-center" style={{ backgroundColor: 'rgba(108, 99, 255, 0.1)' }}>
              <span className="text-2xl">📝</span>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium" style={{ color: 'var(--text-secondary)' }}>Interviews Scheduled</p>
              <p className="text-3xl font-bold" style={{ color: 'var(--text-primary)' }}>{stats?.interviews_scheduled || 0}</p>
            </div>
            <div className="w-12 h-12 rounded-lg flex items-center justify-center" style={{ backgroundColor: 'rgba(34, 197, 94, 0.1)' }}>
              <span className="text-2xl">📅</span>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium" style={{ color: 'var(--text-secondary)' }}>Interviews Completed</p>
              <p className="text-3xl font-bold" style={{ color: 'var(--text-primary)' }}>{stats?.interviews_completed || 0}</p>
            </div>
            <div className="w-12 h-12 rounded-lg flex items-center justify-center" style={{ backgroundColor: 'rgba(168, 85, 247, 0.1)' }}>
              <span className="text-2xl">✅</span>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium" style={{ color: 'var(--text-secondary)' }}>Resumes Created</p>
              <p className="text-3xl font-bold" style={{ color: 'var(--text-primary)' }}>{stats?.resumes_created || 0}</p>
            </div>
            <div className="w-12 h-12 rounded-lg flex items-center justify-center" style={{ backgroundColor: 'rgba(251, 146, 60, 0.1)' }}>
              <span className="text-2xl">📄</span>
            </div>
          </div>
        </Card>
      </div>

      {/* MBTI Personality Test Section */}
      <div className="mb-8">
        <Card className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold" style={{ color: 'var(--text-primary)' }}>
              MBTI性格診断
            </h3>
            {mbtiSummary && (
              <Badge variant="success">診断完了</Badge>
            )}
          </div>
          
          {mbtiLoading ? (
            <div className="flex justify-center py-8">
              <LoadingSpinner className="w-8 h-8" />
            </div>
          ) : mbtiSummary ? (
            <MBTIResultCard summary={mbtiSummary} language="ja" showDetails={false} />
          ) : (
            <div className="text-center py-6">
              <div className="mb-4">
                <span className="text-5xl">🧠</span>
              </div>
              <p className="text-gray-600 dark:text-gray-400 mb-4">
                あなたの性格タイプを診断して、プロフィールに表示しましょう
              </p>
              <MBTITestButton 
                onStartTest={() => setShowMBTITest(true)} 
                language="ja"
              />
            </div>
          )}
        </Card>
      </div>

      {/* MBTI Test Modal */}
      <MBTITestModal
        isOpen={showMBTITest}
        onClose={() => setShowMBTITest(false)}
        onComplete={handleMBTIComplete}
      />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Application Status Breakdown */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>Application Status</h3>
          <div className="space-y-4">
            {stats?.application_stats?.length ? (
              stats.application_stats.map((stat, index) => (
                <div key={index} className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <Badge variant={getStatusColor(stat.status)}>
                      {stat.status}
                    </Badge>
                  </div>
                  <span className="font-semibold" style={{ color: 'var(--text-primary)' }}>{stat.count}</span>
                </div>
              ))
            ) : (
              <div className="text-center py-4">
                <span className="text-3xl mb-2 block">💼</span>
                <p style={{ color: 'var(--text-muted)' }}>No applications yet</p>
                <Button className="mt-4" size="sm">
                  Start Applying
                </Button>
              </div>
            )}
          </div>
        </Card>

        {/* Progress Chart */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>This Month&apos;s Progress</h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span style={{ color: 'var(--text-secondary)' }}>Applications Sent</span>
              <div className="flex items-center space-x-2">
                <div className="w-24 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div className="bg-brand-primary h-2 rounded-full" style={{width: '65%'}}></div>
                </div>
                <span className="text-sm font-semibold">13/20</span>
              </div>
            </div>
            <div className="flex justify-between items-center">
              <span style={{ color: 'var(--text-secondary)' }}>Interviews Attended</span>
              <div className="flex items-center space-x-2">
                <div className="w-24 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div className="bg-green-600 h-2 rounded-full" style={{width: '80%'}}></div>
                </div>
                <span className="text-sm font-semibold">4/5</span>
              </div>
            </div>
            <div className="flex justify-between items-center">
              <span style={{ color: 'var(--text-secondary)' }}>Resume Updates</span>
              <div className="flex items-center space-x-2">
                <div className="w-24 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
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
          <h3 className="text-lg font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>Upcoming Interviews</h3>
          <div className="space-y-4">
            {stats?.recent_interviews?.length ? (
              stats.recent_interviews.slice(0, 5).map((interview) => (
                <div key={interview.id} className="flex items-center justify-between py-3 border-b border-gray-100 dark:border-gray-800 last:border-b-0">
                  <div className="flex-1">
                    <p className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>{interview.title}</p>
                    <p className="text-xs mt-1" style={{ color: 'var(--text-muted)' }}>
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
                <p style={{ color: 'var(--text-muted)' }}>No interviews scheduled</p>
                <Button variant="outline" className="mt-4" size="sm">
                  Schedule Interview
                </Button>
              </div>
            )}
          </div>
        </Card>

        {/* Recent Resume Activity */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>Recent Resumes</h3>
          <div className="space-y-4">
            {stats?.recent_resumes?.length ? (
              stats.recent_resumes.slice(0, 5).map((resume) => (
                <div key={resume.id} className="flex items-center justify-between py-3 border-b border-gray-100 dark:border-gray-800 last:border-b-0">
                  <div className="flex-1">
                    <p className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>{resume.title}</p>
                    <p className="text-xs mt-1" style={{ color: 'var(--text-muted)' }}>
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
                <p style={{ color: 'var(--text-muted)' }}>No resumes created yet</p>
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
        <h3 className="text-lg font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Button className="flex items-center justify-center gap-2 p-4">
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
        <h3 className="text-lg font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>Career Tips</h3>
        <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
          <div className="flex items-start space-x-3">
            <span className="text-2xl">💡</span>
            <div>
              <h4 className="font-semibold text-blue-900 dark:text-blue-100">Tip of the Day</h4>
              <p className="text-blue-800 dark:text-blue-200 mt-1">
                Keep your resume updated regularly. Employers value candidates who showcase their latest achievements and skills.
              </p>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
}