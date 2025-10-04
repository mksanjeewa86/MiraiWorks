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

export default function EmployerDashboard() {
  const { user } = useAuth();
  const router = useRouter();
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
        label: 'Open positions',
        value: stats.open_positions ?? 0,
        helperText: 'Roles currently accepting applicants',
        trendLabel: `${stats.open_positions && stats.hires_made ? Math.max(stats.open_positions - stats.hires_made, 0) : 0} to fill`,
        trendTone: 'neutral' as const,
        icon: <BriefcaseIcon className="h-6 w-6" />,
      },
      {
        label: 'Applications received',
        value: stats.applications_received ?? 0,
        helperText: 'Total submissions across openings',
        trendLabel: `${stats.applications_received ?? 0} this month`,
        trendTone: 'positive' as const,
        icon: <BuildingOffice2Icon className="h-6 w-6" />,
      },
      {
        label: 'Interviews scheduled',
        value: stats.interviews_scheduled ?? 0,
        helperText: 'Upcoming interviews on the calendar',
        trendLabel: `${stats.hires_made ?? 0} hires this month`,
        trendTone: 'neutral' as const,
        icon: <CalendarDaysIcon className="h-6 w-6" />,
      },
      {
        label: 'Hires made',
        value: stats.hires_made ?? 0,
        helperText: 'Converted candidates from interviews',
        trendLabel: 'Keep up the momentum',
        trendTone: (stats.hires_made && stats.hires_made > 0 ? 'positive' : 'neutral') as
          | 'positive'
          | 'negative'
          | 'neutral',
        icon: <UserGroupIcon className="h-6 w-6" />,
      },
    ];
  }, [stats]);

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
      return { percentage: 0, message: 'Set your hiring goals to start tracking progress.' };
    const totalTargets = (stats.open_positions ?? 0) + (stats.hires_made ?? 0);
    if (!totalTargets)
      return { percentage: 0, message: 'Set your hiring goals to start tracking progress.' };
    const percentage = Math.round(((stats.hires_made ?? 0) / totalTargets) * 100);
    return {
      percentage,
      message:
        percentage >= 75
          ? 'Great job! You are close to filling all openings.'
          : 'Keep interviewing to boost your conversion rate.',
    };
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
        title="Employer hiring overview"
        subtitle={`Welcome back${user?.full_name ? `, ${user.full_name}` : ''}`}
        description="Monitor openings, move candidates forward, and celebrate new hires."
        actions={
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={loadDashboardData}>
              Refresh
            </Button>
            <Button size="sm" onClick={() => router.push('/app/jobs/new')}>
              Post a job
            </Button>
          </div>
        }
        meta={`Synced ${new Date().toLocaleTimeString()}`}
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
                Hiring activity timeline
              </h2>
              <Badge variant="outline">Last updates</Badge>
            </div>
            <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
              Daily pulse of applications, interviews, and offers.
            </p>
            <div className="mt-6 h-[260px]">
              {activityTimeline.length ? (
                <SimpleAreaChart data={activityTimeline} dataKey="value" color="#60A5FA" />
              ) : (
                <div className="flex h-full items-center justify-center text-sm text-gray-500">
                  Recent activity will populate here as candidates interact with your team.
                </div>
              )}
            </div>
          </Card>

          <Card className="flex flex-col gap-4 rounded-2xl border border-gray-100 bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-900">
            <div>
              <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-50">
                Activity by type
              </h2>
              <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                Which actions are keeping your team busy this week.
              </p>
            </div>
            <div className="h-[220px]">
              {activityByType.length ? (
                <SimpleBarChart data={activityByType} dataKey="value" color="#34D399" />
              ) : (
                <div className="flex h-full items-center justify-center text-sm text-gray-500">
                  Activity data will appear once candidates engage.
                </div>
              )}
            </div>
          </Card>
        </section>

        <section className="grid gap-6 xl:grid-cols-2">
          <Card className="flex flex-col gap-4 rounded-2xl border border-gray-100 bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-900">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-50">
                Hiring velocity
              </h2>
              <Badge variant="secondary">Goal tracker</Badge>
            </div>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Visualize how quickly applications turn into hires.
            </p>
            <div>
              <div className="flex items-center justify-between text-sm text-gray-500 dark:text-gray-400">
                <span>Progress to goal</span>
                <span>{hiringProgress.percentage}%</span>
              </div>
              <Progress className="mt-2" value={hiringProgress.percentage} max={100} />
            </div>
            <p className="text-sm text-gray-600 dark:text-gray-300">{hiringProgress.message}</p>
            <div className="grid grid-cols-2 gap-3 text-sm">
              <div className="rounded-xl border border-gray-100 p-3 dark:border-gray-800">
                <p className="text-xs uppercase tracking-wide text-gray-500 dark:text-gray-400">
                  Openings
                </p>
                <p className="mt-1 text-lg font-semibold text-gray-900 dark:text-gray-100">
                  {stats?.open_positions ?? 0}
                </p>
              </div>
              <div className="rounded-xl border border-gray-100 p-3 dark:border-gray-800">
                <p className="text-xs uppercase tracking-wide text-gray-500 dark:text-gray-400">
                  Hires
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
                Latest hiring activity
              </h2>
              <Badge variant="outline">Team feed</Badge>
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
                Team activity will show up here as you collaborate on roles.
              </div>
            )}
          </Card>
        </section>

        <Card className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-900">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-50">Quick actions</h2>
            <Badge variant="outline">Productivity</Badge>
          </div>
          <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <Button
              className="h-24 flex-col justify-center gap-2"
              onClick={() => router.push('/app/jobs/new')}
            >
              Post opening
            </Button>
            <Button
              variant="outline"
              className="h-24 flex-col justify-center gap-2"
              onClick={() => router.push('/app/applications')}
            >
              Review applications
            </Button>
            <Button
              variant="outline"
              className="h-24 flex-col justify-center gap-2"
              onClick={() => router.push('/app/interviews')}
            >
              Schedule interview
            </Button>
            <Button
              variant="outline"
              className="h-24 flex-col justify-center gap-2"
              onClick={() => router.push('/app/reports')}
            >
              View reports
            </Button>
          </div>
        </Card>
      </DashboardContentGate>
    </div>
  );
}
