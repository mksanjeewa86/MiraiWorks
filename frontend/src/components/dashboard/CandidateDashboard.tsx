'use client';

import { useEffect, useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import { BriefcaseIcon, ChatBubbleLeftRightIcon } from '@heroicons/react/24/outline';
import { CalendarDaysIcon, ClipboardDocumentCheckIcon } from '@heroicons/react/24/solid';
import { useAuth } from '@/contexts/AuthContext';
import { dashboardApi } from '@/api/dashboard';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { LoadingSpinner } from '@/components/ui/loading-spinner';
import {
  DashboardContentGate,
  DashboardHeader,
  DashboardMetricCard,
} from '@/components/dashboard/common';
import { SimpleAreaChart, SimpleBarChart } from '@/components/dashboard/Charts';
import type { CandidateDashboardStats } from '@/types/dashboard';
import type { ActivityItem } from '@/types';
import MBTITestButton from '@/components/mbti/MBTITestButton';
import MBTITestModal from '@/components/mbti/MBTITestModal';
import MBTIResultCard from '@/components/mbti/MBTIResultCard';
import { mbtiApi } from '@/api/mbti';
import type { MBTITestSummary } from '@/types/mbti';

export default function CandidateDashboard() {
  const { user } = useAuth();
  const router = useRouter();
  const [stats, setStats] = useState<CandidateDashboardStats | null>(null);
  const [recentActivity, setRecentActivity] = useState<ActivityItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [activityLoading, setActivityLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activityError, setActivityError] = useState<string | null>(null);
  const [showMBTITest, setShowMBTITest] = useState(false);
  const [mbtiSummary, setMbtiSummary] = useState<MBTITestSummary | null>(null);
  const [mbtiLoading, setMbtiLoading] = useState(false);

  useEffect(() => {
    loadDashboardData();
    loadRecentActivity();
    loadMBTISummary();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const response = await dashboardApi.getStats();
      setStats(response.data as CandidateDashboardStats);
      setError(null);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const loadRecentActivity = async () => {
    try {
      setActivityLoading(true);
      const response = await dashboardApi.getRecentActivity(8);
      setRecentActivity(response.data ?? []);
      setActivityError(null);
    } catch (err: unknown) {
      setActivityError(err instanceof Error ? err.message : 'Failed to load activity');
    } finally {
      setActivityLoading(false);
    }
  };

  const loadMBTISummary = async () => {
    try {
      setMbtiLoading(true);
      const progress = await mbtiApi.getProgress();
      if (progress.status === 'completed') {
        const summary = await mbtiApi.getSummary('ja');
        setMbtiSummary(summary);
      } else {
        setMbtiSummary(null);
      }
    } catch (err) {
      console.info('Could not load MBTI data', err);
      setMbtiSummary(null);
    } finally {
      setMbtiLoading(false);
    }
  };

  const handleMBTIComplete = async () => {
    await loadMBTISummary();
  };

  const metrics = useMemo(() => {
    if (!stats) {
      return [] as {
        label: string;
        value: number | string;
        helperText?: string;
        trendLabel?: string;
        trendTone?: 'positive' | 'negative' | 'neutral';
        icon: React.ReactElement;
      }[];
    }

    return [
      {
        label: 'Active applications',
        value: stats.total_applications ?? 0,
        helperText: 'Across all active job submissions',
        trendLabel: `${stats.application_stats?.find((s) => s.status === 'in_review')?.count ?? 0} in review`,
        trendTone: 'neutral' as const,
        icon: <ClipboardDocumentCheckIcon className="h-6 w-6" />,
      },
      {
        label: 'Interviews scheduled',
        value: stats.interviews_scheduled ?? 0,
        helperText: 'Upcoming meetings in the next weeks',
        trendLabel: `${stats.interviews_completed ?? 0} completed`,
        trendTone: 'positive' as const,
        icon: <CalendarDaysIcon className="h-6 w-6" />,
      },
      {
        label: 'Resumes on file',
        value: stats.resumes_created ?? 0,
        helperText: 'Keep resumes updated for better matches',
        trendLabel: `${stats.recent_resumes?.[0]?.title ? 'Most recent updated' : 'No updates yet'}`,
        trendTone: (stats.recent_resumes?.length ? 'positive' : 'neutral') as
          | 'positive'
          | 'negative'
          | 'neutral',
        icon: <BriefcaseIcon className="h-6 w-6" />,
      },
      {
        label: 'Unread conversations',
        value: stats.activeConversations ?? 0,
        helperText: 'Messages from recruiters and companies',
        trendLabel: 'Stay responsive to stand out',
        trendTone: 'neutral' as const,
        icon: <ChatBubbleLeftRightIcon className="h-6 w-6" />,
      },
    ];
  }, [stats]);

  const applicationChartData = useMemo(() => {
    return (stats?.application_stats ?? []).map((item) => ({
      name: item.status,
      value: item.count,
    }));
  }, [stats]);

  const interviewTimelineData = useMemo(() => {
    return (stats?.recent_interviews ?? [])
      .filter((interview) => Boolean(interview.scheduled_at))
      .map((interview) => ({
        name: new Date(interview.scheduled_at as string).toLocaleDateString('en-US', {
          month: 'short',
          day: 'numeric',
        }),
        value: 1,
      }));
  }, [stats]);

  const renderActivityBadge = (type?: ActivityItem['type']) => {
    switch (type) {
      case 'interview':
        return <Badge variant="primary">Interview</Badge>;
      case 'message':
        return <Badge variant="secondary">Message</Badge>;
      case 'resume':
        return <Badge variant="success">Resume</Badge>;
      case 'user':
        return <Badge variant="outline">Profile</Badge>;
      default:
        return <Badge variant="outline">Update</Badge>;
    }
  };

  const formatDateTime = (value?: string) => {
    if (!value) return 'N/A';
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return 'N/A';
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="space-y-6 p-6">
      <DashboardHeader
        title="Candidate control center"
        subtitle={`Welcome back${user?.full_name ? `, ${user.full_name}` : ''}`}
        description="Track your applications, interviews, and career growth in one place."
        actions={
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={loadDashboardData}>
              Refresh
            </Button>
            <Button size="sm" onClick={() => router.push('/app/jobs')}>
              Discover roles
            </Button>
          </div>
        }
        meta={`Last updated ${new Date().toLocaleTimeString()}`}
      />

      <DashboardContentGate loading={loading} error={error} onRetry={loadDashboardData}>
        <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          {metrics.map((metric) => (
            <DashboardMetricCard
              key={metric.label}
              label={metric.label}
              value={metric.value}
              helperText={metric.helperText}
              trendLabel={metric.trendLabel}
              trendTone={metric.trendTone}
              icon={metric.icon}
            />
          ))}
        </section>

        <section className="grid gap-6 lg:grid-cols-3">
          <Card className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-900 lg:col-span-2">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-50">
                Application pipeline
              </h2>
              <Badge variant="outline">Status breakdown</Badge>
            </div>
            <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
              Monitor how your applications are progressing across the pipeline.
            </p>
            <div className="mt-6 h-[260px]">
              {applicationChartData.length ? (
                <SimpleBarChart data={applicationChartData} dataKey="value" color="#6366F1" />
              ) : (
                <div className="flex h-full items-center justify-center text-sm text-gray-500">
                  No application data yet.
                </div>
              )}
            </div>
          </Card>

          <Card className="flex flex-col justify-between gap-4 rounded-2xl border border-gray-100 bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-900">
            <div>
              <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-50">
                Interview cadence
              </h2>
              <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                A quick look at your upcoming interview schedule.
              </p>
            </div>
            <div className="h-[220px]">
              {interviewTimelineData.length ? (
                <SimpleAreaChart data={interviewTimelineData} dataKey="value" color="#22C55E" />
              ) : (
                <div className="flex h-full items-center justify-center text-sm text-gray-500">
                  Interviews will appear here once scheduled.
                </div>
              )}
            </div>
          </Card>
        </section>

        <section className="grid gap-6 xl:grid-cols-2">
          <Card className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-900">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-50">
                Upcoming interviews
              </h2>
              <Badge variant="secondary">Next 5</Badge>
            </div>
            <div className="mt-4 space-y-4">
              {stats?.recent_interviews?.length ? (
                stats.recent_interviews.slice(0, 5).map((interview) => (
                  <div
                    key={interview.id}
                    className="flex items-center justify-between rounded-xl border border-gray-100 px-4 py-3 dark:border-gray-800"
                  >
                    <div className="flex-1">
                      <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                        {interview.title}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        {interview.company_name} • {formatDateTime(interview.scheduled_at)}
                      </p>
                    </div>
                    <Badge variant="outline">{interview.status}</Badge>
                  </div>
                ))
              ) : (
                <div className="flex flex-col items-center gap-3 rounded-xl border border-dashed border-gray-200 p-6 text-center text-sm text-gray-500 dark:border-gray-800">
                  <CalendarDaysIcon className="h-6 w-6" />
                  <p>No interviews on your calendar yet.</p>
                  <Button variant="outline" size="sm">
                    Browse opportunities
                  </Button>
                </div>
              )}
            </div>
          </Card>

          <Card className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-900">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-50">
                Recent resumes
              </h2>
              <Badge variant="outline">Updates</Badge>
            </div>
            <div className="mt-4 space-y-4">
              {stats?.recent_resumes?.length ? (
                stats.recent_resumes.slice(0, 5).map((resume) => (
                  <div
                    key={resume.id}
                    className="flex items-center justify-between rounded-xl border border-gray-100 px-4 py-3 dark:border-gray-800"
                  >
                    <div>
                      <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                        {resume.title}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        Updated {formatDateTime(resume.updated_at)}
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
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
                <div className="flex flex-col items-center gap-3 rounded-xl border border-dashed border-gray-200 p-6 text-center text-sm text-gray-500 dark:border-gray-800">
                  <ClipboardDocumentCheckIcon className="h-6 w-6" />
                  <p>No resumes created yet.</p>
                  <Button size="sm">Create resume</Button>
                </div>
              )}
            </div>
          </Card>
        </section>

        <section className="grid gap-6 lg:grid-cols-3">
          <Card className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-900 lg:col-span-2">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-50">
                Career activity feed
              </h2>
              <Badge variant="outline">Live updates</Badge>
            </div>
            {activityLoading ? (
              <div className="flex h-40 items-center justify-center">
                <LoadingSpinner className="h-6 w-6" />
              </div>
            ) : activityError ? (
              <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700 dark:border-red-800/60 dark:bg-red-900/20 dark:text-red-200">
                {activityError}
              </div>
            ) : recentActivity.length ? (
              <div className="mt-4 space-y-4">
                {recentActivity.map((activity) => (
                  <div
                    key={activity.id}
                    className="flex items-start justify-between rounded-xl border border-gray-100 px-4 py-3 dark:border-gray-800"
                  >
                    <div className="space-y-1">
                      <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                        {activity.title}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        {activity.description}
                      </p>
                      <p className="text-xs text-gray-400">{formatDateTime(activity.timestamp)}</p>
                    </div>
                    {renderActivityBadge(activity.type)}
                  </div>
                ))}
              </div>
            ) : (
              <div className="flex h-full items-center justify-center rounded-xl border border-dashed border-gray-200 p-6 text-sm text-gray-500 dark:border-gray-800">
                Activity will appear here as you start engaging with the platform.
              </div>
            )}
          </Card>

          <Card className="flex flex-col gap-4 rounded-2xl border border-gray-100 bg-gradient-to-br from-indigo-50 via-white to-indigo-50 p-6 shadow-sm dark:border-indigo-900/40 dark:from-indigo-950 dark:via-slate-950 dark:to-indigo-950">
            <div>
              <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-50">
                MBTI insights
              </h2>
              <p className="mt-2 text-sm text-gray-600 dark:text-gray-300">
                Discover strengths and tailored role recommendations based on your personality
                profile.
              </p>
            </div>
            {mbtiLoading ? (
              <div className="flex h-32 items-center justify-center">
                <LoadingSpinner className="h-6 w-6" />
              </div>
            ) : mbtiSummary ? (
              <MBTIResultCard summary={mbtiSummary} language="ja" showDetails={false} />
            ) : (
              <div className="flex flex-col gap-3 rounded-xl border border-dashed border-indigo-200 p-4 text-sm text-gray-600 dark:border-indigo-900/60 dark:text-gray-300">
                <p>
                  Complete the MBTI career alignment assessment to unlock personalized coaching
                  tips.
                </p>
                <MBTITestButton onStartTest={() => setShowMBTITest(true)} />
              </div>
            )}
          </Card>
        </section>
      </DashboardContentGate>

      <MBTITestModal
        isOpen={showMBTITest}
        onClose={() => setShowMBTITest(false)}
        onComplete={handleMBTIComplete}
      />
    </div>
  );
}
