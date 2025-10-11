'use client';

import { useEffect, useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import { FunnelIcon, UsersIcon } from '@heroicons/react/24/outline';
import { ClipboardDocumentCheckIcon, CalendarDaysIcon } from '@heroicons/react/24/solid';
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
import type { RecruiterStats } from '@/types/dashboard';
import type { ActivityItem } from '@/types';
import { ROUTES } from '@/routes/config';
import { useTranslations, useLocale } from 'next-intl';

export default function RecruiterDashboard() {
  const { user } = useAuth();
  const router = useRouter();
  const locale = useLocale();
  const t = useTranslations('dashboard.recruiter');
  const [stats, setStats] = useState<RecruiterStats | null>(null);
  const [activity, setActivity] = useState<ActivityItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [activityLoading, setActivityLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activityError, setActivityError] = useState<string | null>(null);

  useEffect(() => {
    loadDashboardData();
    loadActivity();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const response = await dashboardApi.getStats();
      setStats(response.data as RecruiterStats);
      setError(null);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const loadActivity = async () => {
    try {
      setActivityLoading(true);
      const response = await dashboardApi.getRecentActivity(6);
      setActivity(response.data ?? []);
      setActivityError(null);
    } catch (err: unknown) {
      setActivityError(err instanceof Error ? err.message : 'Failed to load recent activity');
    } finally {
      setActivityLoading(false);
    }
  };

  const metrics = useMemo(() => {
    if (!stats) return [];
    return [
      {
        label: t('metrics.activeCandidates.label'),
        value: stats.active_candidates ?? 0,
        helperText: t('metrics.activeCandidates.helperText'),
        trendLabel: `${stats.interview_pipeline?.[0]?.count ?? 0} ${t('metrics.activeCandidates.inScreening')}`,
        trendTone: 'neutral' as const,
        icon: <UsersIcon className="h-6 w-6" />,
      },
      {
        label: t('metrics.interviewsThisWeek.label'),
        value: stats.interviews_this_week ?? 0,
        helperText: t('metrics.interviewsThisWeek.helperText'),
        trendLabel: `${stats.recent_interviews?.length ?? 0} ${t('metrics.interviewsThisWeek.logged')}`,
        trendTone: 'positive' as const,
        icon: <CalendarDaysIcon className="h-6 w-6" />,
      },
      {
        label: t('metrics.pendingProposals.label'),
        value: stats.pending_proposals ?? 0,
        helperText: t('metrics.pendingProposals.helperText'),
        trendLabel: `${stats.placement_rate ? Math.round(stats.placement_rate * 100) : 0}% ${t('metrics.pendingProposals.conversion')}`,
        trendTone: 'neutral' as const,
        icon: <ClipboardDocumentCheckIcon className="h-6 w-6" />,
      },
      {
        label: t('metrics.placementRate.label'),
        value: stats.placement_rate ? `${(stats.placement_rate * 100).toFixed(1)}%` : '0%',
        helperText: t('metrics.placementRate.helperText'),
        trendLabel: t('metrics.placementRate.target'),
        trendTone: (stats.placement_rate && stats.placement_rate >= 0.45
          ? 'positive'
          : 'neutral') as 'positive' | 'negative' | 'neutral',
        icon: <FunnelIcon className="h-6 w-6" />,
      },
    ];
  }, [stats, t]);

  const pipelineData = useMemo(() => {
    return (stats?.interview_pipeline ?? []).map((stage) => ({
      name: stage.stage,
      value: stage.count,
    }));
  }, [stats]);

  const interviewsTimeline = useMemo(() => {
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

  const formatTimestamp = (value?: string) => {
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
        title={t('header.title')}
        subtitle={`${t('header.welcomeBack')}${user?.full_name ? `, ${user.full_name}` : ''}`}
        description={t('header.description')}
        actions={
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={loadDashboardData}>
              {t('header.refreshButton')}
            </Button>
            <Button size="sm" onClick={() => router.push(`/${locale}${ROUTES.APP.JOBS.NEW}`)}>
              {t('header.createJobButton')}
            </Button>
          </div>
        }
        meta={`${t('header.lastUpdated')} ${new Date().toLocaleTimeString()}`}
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
                {t('interviewPipeline.title')}
              </h2>
              <Badge variant="outline">{t('interviewPipeline.badge')}</Badge>
            </div>
            <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
              {t('interviewPipeline.description')}
            </p>
            <div className="mt-6 h-[260px]">
              {pipelineData.length ? (
                <SimpleBarChart data={pipelineData} dataKey="value" color="#8B5CF6" horizontal />
              ) : (
                <div className="flex h-full items-center justify-center text-sm text-gray-500">
                  {t('interviewPipeline.noData')}
                </div>
              )}
            </div>
          </Card>

          <Card className="flex flex-col gap-4 rounded-2xl border border-gray-100 bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-900">
            <div>
              <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-50">
                {t('weeklyInterviewLoad.title')}
              </h2>
              <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                {t('weeklyInterviewLoad.description')}
              </p>
            </div>
            <div className="h-[220px]">
              {interviewsTimeline.length ? (
                <SimpleAreaChart data={interviewsTimeline} dataKey="value" color="#34D399" />
              ) : (
                <div className="flex h-full items-center justify-center text-sm text-gray-500">
                  {t('weeklyInterviewLoad.noData')}
                </div>
              )}
            </div>
          </Card>
        </section>

        <section className="grid gap-6 xl:grid-cols-2">
          <Card className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-900">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-50">
                {t('upcomingInterviews.title')}
              </h2>
              <Badge variant="secondary">{t('upcomingInterviews.badge')}</Badge>
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
                        {formatTimestamp(interview.scheduled_at)}
                      </p>
                    </div>
                    <Badge variant="outline">{interview.status}</Badge>
                  </div>
                ))
              ) : (
                <div className="flex flex-col items-center gap-3 rounded-xl border border-dashed border-gray-200 p-6 text-center text-sm text-gray-500 dark:border-gray-800">
                  <CalendarDaysIcon className="h-6 w-6" />
                  <p>{t('upcomingInterviews.noInterviews')}</p>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => router.push(`/${locale}${ROUTES.APP.CANDIDATES}`)}
                  >
                    {t('upcomingInterviews.viewCandidatesButton')}
                  </Button>
                </div>
              )}
            </div>
          </Card>

          <Card className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-900">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-50">
                {t('topCandidates.title')}
              </h2>
              <Badge variant="outline">{t('topCandidates.badge')}</Badge>
            </div>
            <div className="mt-4 space-y-4">
              {stats?.top_candidates?.length ? (
                stats.top_candidates.slice(0, 5).map((candidate) => (
                  <div
                    key={candidate.id}
                    className="flex items-center justify-between rounded-xl border border-gray-100 px-4 py-3 dark:border-gray-800"
                  >
                    <div>
                      <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                        {candidate.name}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">{candidate.email}</p>
                    </div>
                    <Badge variant="success">{t('topCandidates.scoreBadge')} {candidate.score}</Badge>
                  </div>
                ))
              ) : (
                <div className="flex flex-col items-center gap-3 rounded-xl border border-dashed border-gray-200 p-6 text-center text-sm text-gray-500 dark:border-gray-800">
                  <UsersIcon className="h-6 w-6" />
                  <p>{t('topCandidates.noCandidates')}</p>
                  <Button size="sm" onClick={() => router.push(`/${locale}${ROUTES.APP.CANDIDATES}`)}>
                    {t('topCandidates.sourceTalentButton')}
                  </Button>
                </div>
              )}
            </div>
          </Card>
        </section>

        <section className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-900">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-50">
              {t('latestActivity.title')}
            </h2>
            <Badge variant="outline">{t('latestActivity.badge')}</Badge>
          </div>
          {activityLoading ? (
            <div className="flex h-40 items-center justify-center">
              <LoadingSpinner className="h-6 w-6" />
            </div>
          ) : activityError ? (
            <div className="mt-4 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700 dark:border-red-800/60 dark:bg-red-900/20 dark:text-red-100">
              {activityError}
            </div>
          ) : activity.length ? (
            <div className="mt-4 space-y-4">
              {activity.map((item) => (
                <div
                  key={item.id}
                  className="flex items-start justify-between rounded-xl border border-gray-100 px-4 py-3 dark:border-gray-800"
                >
                  <div className="space-y-1">
                    <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                      {item.title}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">{item.description}</p>
                    <p className="text-xs text-gray-400">{formatTimestamp(item.timestamp)}</p>
                  </div>
                  <Badge variant="outline">{item.type}</Badge>
                </div>
              ))}
            </div>
          ) : (
            <div className="mt-4 flex items-center justify-center rounded-xl border border-dashed border-gray-200 p-6 text-sm text-gray-500 dark:border-gray-800">
              {t('latestActivity.noActivity')}
            </div>
          )}
        </section>
      </DashboardContentGate>
    </div>
  );
}
