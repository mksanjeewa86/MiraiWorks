'use client';

import { useEffect, useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import { BuildingOffice2Icon, BriefcaseIcon } from '@heroicons/react/24/outline';
import { CalendarDaysIcon, UserGroupIcon } from '@heroicons/react/24/solid';
import { useAuth } from '@/contexts/AuthContext';
import { dashboardApi } from '@/api/dashboard';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { LoadingSpinner } from '@/components/ui/loading-spinner';
import { Progress } from '@/components/ui/progress';
import {
  DashboardContentGate,
  DashboardHeader,
  DashboardMetricCard,
} from '@/components/dashboard/common';
import { SimpleAreaChart, SimpleBarChart } from '@/components/dashboard/Charts';
import type { EmployerStats } from '@/types/dashboard';
import type { ActivityItem } from '@/types';
import { ROUTES } from '@/routes/config';
import { useTranslations, useLocale } from 'next-intl';

export default function EmployerDashboard() {
  const { user } = useAuth();
  const router = useRouter();
  const locale = useLocale();
  const t = useTranslations('dashboard.employer');
  const [stats, setStats] = useState<EmployerStats | null>(null);
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
      setStats(response.data as EmployerStats);
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
      const response = await dashboardApi.getRecentActivity(12);
      setActivity(response.data ?? []);
      setActivityError(null);
    } catch (err: unknown) {
      setActivityError(err instanceof Error ? err.message : 'Failed to load hiring activity');
    } finally {
      setActivityLoading(false);
    }
  };

  const metrics = useMemo(() => {
    if (!stats) return [];
    return [
      {
        label: t('metrics.openPositions.label'),
        value: stats.open_positions ?? 0,
        helperText: t('metrics.openPositions.helperText'),
        trendLabel: `${stats.open_positions && stats.hires_made ? Math.max(stats.open_positions - stats.hires_made, 0) : 0} ${t('metrics.openPositions.toFill')}`,
        trendTone: 'neutral' as const,
        icon: <BriefcaseIcon className="h-6 w-6" />,
      },
      {
        label: t('metrics.applicationsReceived.label'),
        value: stats.applications_received ?? 0,
        helperText: t('metrics.applicationsReceived.helperText'),
        trendLabel: `${stats.applications_received ?? 0} ${t('metrics.applicationsReceived.thisMonth')}`,
        trendTone: 'positive' as const,
        icon: <BuildingOffice2Icon className="h-6 w-6" />,
      },
      {
        label: t('metrics.interviewsScheduled.label'),
        value: stats.interviews_scheduled ?? 0,
        helperText: t('metrics.interviewsScheduled.helperText'),
        trendLabel: `${stats.hires_made ?? 0} ${t('metrics.interviewsScheduled.hiresThisMonth')}`,
        trendTone: 'neutral' as const,
        icon: <CalendarDaysIcon className="h-6 w-6" />,
      },
      {
        label: t('metrics.hiresMade.label'),
        value: stats.hires_made ?? 0,
        helperText: t('metrics.hiresMade.helperText'),
        trendLabel: t('metrics.hiresMade.keepMomentum'),
        trendTone: (stats.hires_made && stats.hires_made > 0 ? 'positive' : 'neutral') as
          | 'positive'
          | 'negative'
          | 'neutral',
        icon: <UserGroupIcon className="h-6 w-6" />,
      },
    ];
  }, [stats, t]);

  const activityByType = useMemo(() => {
    const counts = new Map<string, number>();
    activity.forEach((item) => {
      const key = item.type ?? 'update';
      counts.set(key, (counts.get(key) ?? 0) + 1);
    });
    return Array.from(counts.entries()).map(([name, value]) => ({ name, value }));
  }, [activity]);

  const activityTimeline = useMemo(() => {
    const grouped = new Map<string, number>();
    activity.forEach((item) => {
      if (!item.timestamp) return;
      const date = new Date(item.timestamp);
      if (Number.isNaN(date.getTime())) return;
      const key = date.toISOString().slice(0, 10);
      grouped.set(key, (grouped.get(key) ?? 0) + 1);
    });
    return Array.from(grouped.entries())
      .sort((a, b) => (a[0] > b[0] ? 1 : -1))
      .map(([dateKey, value]) => ({
        name: new Date(dateKey).toLocaleDateString('en-US', {
          month: 'short',
          day: 'numeric',
        }),
        value,
      }));
  }, [activity]);

  const hiringProgress = useMemo(() => {
    if (!stats)
      return { percentage: 0, message: t('hiringVelocity.setGoals') };
    const totalTargets = (stats.open_positions ?? 0) + (stats.hires_made ?? 0);
    if (!totalTargets)
      return { percentage: 0, message: t('hiringVelocity.setGoals') };
    const percentage = Math.round(((stats.hires_made ?? 0) / totalTargets) * 100);
    return {
      percentage,
      message:
        percentage >= 75
          ? t('hiringVelocity.greatJob')
          : t('hiringVelocity.keepInterviewing'),
    };
  }, [stats, t]);

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
              {t('header.postJobButton')}
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
                {t('hiringActivityTimeline.title')}
              </h2>
              <Badge variant="outline">{t('hiringActivityTimeline.badge')}</Badge>
            </div>
            <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
              {t('hiringActivityTimeline.description')}
            </p>
            <div className="mt-6 h-[260px]">
              {activityTimeline.length ? (
                <SimpleAreaChart data={activityTimeline} dataKey="value" color="#60A5FA" />
              ) : (
                <div className="flex h-full items-center justify-center text-sm text-gray-500">
                  {t('hiringActivityTimeline.noData')}
                </div>
              )}
            </div>
          </Card>

          <Card className="flex flex-col gap-4 rounded-2xl border border-gray-100 bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-900">
            <div>
              <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-50">
                {t('activityByType.title')}
              </h2>
              <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                {t('activityByType.description')}
              </p>
            </div>
            <div className="h-[220px]">
              {activityByType.length ? (
                <SimpleBarChart data={activityByType} dataKey="value" color="#34D399" />
              ) : (
                <div className="flex h-full items-center justify-center text-sm text-gray-500">
                  {t('activityByType.noData')}
                </div>
              )}
            </div>
          </Card>
        </section>

        <section className="grid gap-6 xl:grid-cols-2">
          <Card className="flex flex-col gap-4 rounded-2xl border border-gray-100 bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-900">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-50">
                {t('hiringVelocity.title')}
              </h2>
              <Badge variant="secondary">{t('hiringVelocity.badge')}</Badge>
            </div>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              {t('hiringVelocity.description')}
            </p>
            <div>
              <div className="flex items-center justify-between text-sm text-gray-500 dark:text-gray-400">
                <span>{t('hiringVelocity.progressLabel')}</span>
                <span>{hiringProgress.percentage}%</span>
              </div>
              <Progress className="mt-2" value={hiringProgress.percentage} max={100} />
            </div>
            <p className="text-sm text-gray-600 dark:text-gray-300">{hiringProgress.message}</p>
            <div className="grid grid-cols-2 gap-3 text-sm">
              <div className="rounded-xl border border-gray-100 p-3 dark:border-gray-800">
                <p className="text-xs uppercase tracking-wide text-gray-500 dark:text-gray-400">
                  {t('hiringVelocity.openingsLabel')}
                </p>
                <p className="mt-1 text-lg font-semibold text-gray-900 dark:text-gray-100">
                  {stats?.open_positions ?? 0}
                </p>
              </div>
              <div className="rounded-xl border border-gray-100 p-3 dark:border-gray-800">
                <p className="text-xs uppercase tracking-wide text-gray-500 dark:text-gray-400">
                  {t('hiringVelocity.hiresLabel')}
                </p>
                <p className="mt-1 text-lg font-semibold text-gray-900 dark:text-gray-100">
                  {stats?.hires_made ?? 0}
                </p>
              </div>
            </div>
          </Card>

          <Card className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-900">
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
              <div className="mt-4 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700 dark:border-red-800/60 dark:bg-red-900/20 dark:text-red-200">
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
          </Card>
        </section>

        <Card className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-900">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-50">{t('quickActions.title')}</h2>
            <Badge variant="outline">{t('quickActions.badge')}</Badge>
          </div>
          <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <Button
              className="h-24 flex-col justify-center gap-2"
              onClick={() => router.push(`/${locale}${ROUTES.APP.JOBS.NEW}`)}
            >
              {t('quickActions.postOpening')}
            </Button>
            <Button
              variant="outline"
              className="h-24 flex-col justify-center gap-2"
              onClick={() => router.push(`/${locale}${ROUTES.APP.APPLICATIONS}`)}
            >
              {t('quickActions.reviewApplications')}
            </Button>
            <Button
              variant="outline"
              className="h-24 flex-col justify-center gap-2"
              onClick={() => router.push(`/${locale}${ROUTES.APP.INTERVIEWS}`)}
            >
              {t('quickActions.scheduleInterview')}
            </Button>
            <Button
              variant="outline"
              className="h-24 flex-col justify-center gap-2"
              onClick={() => router.push(`/${locale}${ROUTES.APP.REPORTS}`)}
            >
              {t('quickActions.viewReports')}
            </Button>
          </div>
        </Card>
      </DashboardContentGate>
    </div>
  );
}
