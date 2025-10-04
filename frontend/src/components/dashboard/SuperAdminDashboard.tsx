'use client';

import { useEffect, useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import { BuildingOffice2Icon, UsersIcon } from '@heroicons/react/24/outline';
import { ServerStackIcon, ShieldCheckIcon } from '@heroicons/react/24/solid';
import {
  AlertTriangle,
  Activity,
  BarChart3,
  GaugeCircle,
  ClipboardCheck,
  Award,
} from 'lucide-react';
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
import type { SuperAdminStats } from '@/types/dashboard';
import type { ActivityItem } from '@/types';

export default function SuperAdminDashboard() {
  const router = useRouter();
  const [stats, setStats] = useState<SuperAdminStats | null>(null);
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
      setStats(response.data as SuperAdminStats);
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
      const response = await dashboardApi.getRecentActivity(10);
      setActivity(response.data ?? []);
      setActivityError(null);
    } catch (err: unknown) {
      setActivityError(err instanceof Error ? err.message : 'Failed to load platform activity');
    } finally {
      setActivityLoading(false);
    }
  };

  const metrics = useMemo(() => {
    if (!stats) return [];
    return [
      {
        label: 'Companies onboarded',
        value: stats.total_companies ?? 0,
        helperText: 'Across all active tenants',
        trendLabel: `${stats.active_companies ?? 0} active`,
        trendTone: 'positive' as const,
        icon: <BuildingOffice2Icon className="h-6 w-6" />,
      },
      {
        label: 'Registered users',
        value: stats.total_users ?? 0,
        helperText: 'Global user base across roles',
        trendLabel: `${stats.active_users ?? 0} active monthly`,
        trendTone: 'positive' as const,
        icon: <UsersIcon className="h-6 w-6" />,
      },
      {
        label: 'Open positions',
        value: stats.total_positions ?? 0,
        helperText: 'Positions currently published',
        trendLabel: `${stats.total_applications ?? 0} total applications`,
        trendTone: 'neutral' as const,
        icon: <BarChart3 className="h-6 w-6" />,
      },
      {
        label: 'System uptime',
        value: stats.platform_metrics?.system_uptime
          ? `${stats.platform_metrics.system_uptime}%`
          : 'N/A',
        helperText: 'Rolling 30-day uptime',
        trendLabel: `${stats.system_health?.api_response_time ?? 0}ms response`,
        trendTone: (stats.platform_metrics?.system_uptime &&
        stats.platform_metrics.system_uptime >= 99.5
          ? 'positive'
          : 'neutral') as 'positive' | 'negative' | 'neutral',
        icon: <ShieldCheckIcon className="h-6 w-6" />,
      },
    ];
  }, [stats]);

  const examMetrics = useMemo(() => {
    if (!stats) return [];
    const completionRate =
      stats.total_exam_sessions && stats.total_exam_sessions > 0
        ? ((stats.completed_exam_sessions ?? 0) / stats.total_exam_sessions) * 100
        : 0;

    return [
      {
        label: 'Total exams',
        value: stats.total_exams ?? 0,
        helperText: 'Exams created system-wide',
        trendLabel: `${stats.total_exam_assignments ?? 0} assignments`,
        trendTone: 'neutral' as const,
        icon: <ClipboardCheck className="h-6 w-6" />,
      },
      {
        label: 'Exam sessions',
        value: stats.total_exam_sessions ?? 0,
        helperText: 'Total exam attempts',
        trendLabel: `${completionRate.toFixed(1)}% completion rate`,
        trendTone: completionRate >= 70 ? ('positive' as const) : ('neutral' as const),
        icon: <Activity className="h-6 w-6" />,
      },
      {
        label: 'Average score',
        value: stats.avg_exam_score ? `${stats.avg_exam_score.toFixed(1)}%` : 'N/A',
        helperText: 'Across completed exams',
        trendLabel: `${stats.completed_exam_sessions ?? 0} completed`,
        trendTone:
          stats.avg_exam_score && stats.avg_exam_score >= 70
            ? ('positive' as const)
            : ('neutral' as const),
        icon: <Award className="h-6 w-6" />,
      },
    ];
  }, [stats]);

  const platformMetricsData = useMemo(() => {
    if (!stats?.platform_metrics) return [];
    return [
      { name: 'Daily signups', value: stats.platform_metrics.daily_signups ?? 0 },
      { name: 'Weekly signups', value: stats.platform_metrics.weekly_signups ?? 0 },
      { name: 'Monthly signups', value: stats.platform_metrics.monthly_signups ?? 0 },
      { name: 'Monthly active users', value: stats.platform_metrics.monthly_active_users ?? 0 },
    ];
  }, [stats]);

  const systemHealthSummary = useMemo(() => {
    const health = stats?.system_health;
    if (!health) {
      return [
        { label: 'Database', value: 'N/A', tone: 'neutral' as const },
        { label: 'API response', value: 'N/A', tone: 'neutral' as const },
        { label: 'Active sessions', value: 'N/A', tone: 'neutral' as const },
        { label: 'Error rate', value: 'N/A', tone: 'neutral' as const },
      ];
    }
    return [
      {
        label: 'Database',
        value: health.database_status,
        tone:
          health.database_status === 'healthy'
            ? 'positive'
            : health.database_status === 'warning'
              ? 'neutral'
              : 'negative',
      },
      {
        label: 'API response',
        value: `${health.api_response_time ?? 0} ms`,
        tone: health.api_response_time && health.api_response_time < 400 ? 'positive' : 'neutral',
      },
      {
        label: 'Active sessions',
        value: health.active_sessions ?? 0,
        tone: 'neutral' as const,
      },
      {
        label: 'Error rate',
        value: `${health.error_rate ?? 0}%`,
        tone: health.error_rate && health.error_rate > 3 ? 'negative' : 'positive',
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

  const renderLogBadge = (level: string) => {
    switch (level.toLowerCase()) {
      case 'error':
        return <Badge variant="error">error</Badge>;
      case 'warning':
        return <Badge variant="warning">warning</Badge>;
      default:
        return <Badge variant="secondary">info</Badge>;
    }
  };

  const renderLogIcon = (level: string) => {
    switch (level.toLowerCase()) {
      case 'error':
        return <AlertTriangle className="h-5 w-5 text-red-500" />;
      case 'warning':
        return <AlertTriangle className="h-5 w-5 text-amber-500" />;
      default:
        return <Activity className="h-5 w-5 text-sky-500" />;
    }
  };

  return (
    <div className="space-y-6 p-6">
      <DashboardHeader
        title="Platform control center"
        subtitle="System-wide visibility at a glance"
        description="Observe tenant growth, infrastructure health, and operational signals."
        actions={
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={loadDashboardData}>
              Refresh
            </Button>
            <Button size="sm" onClick={() => router.push('/admin/settings')}>
              Manage platform
            </Button>
          </div>
        }
        meta={`Telemetry synced ${new Date().toLocaleTimeString()}`}
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

        <section className="mt-6">
          <div className="mb-4">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-50">
              Exam system metrics
            </h2>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              System-wide exam performance and usage statistics
            </p>
          </div>
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
            {examMetrics.map((metric) => (
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
          </div>
        </section>

        <section className="grid gap-6 lg:grid-cols-3">
          <Card className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-900 lg:col-span-2">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-50">
                Platform engagement
              </h2>
              <Badge variant="outline">Signups</Badge>
            </div>
            <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
              Track how new users are joining and returning to the platform.
            </p>
            <div className="mt-6 h-[260px]">
              {platformMetricsData.length ? (
                <SimpleAreaChart data={platformMetricsData} dataKey="value" color="#6366F1" />
              ) : (
                <div className="flex h-full items-center justify-center text-sm text-gray-500">
                  Platform metrics will show here once data is available.
                </div>
              )}
            </div>
          </Card>

          <Card className="flex flex-col gap-4 rounded-2xl border border-gray-100 bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-900">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-50">
                System health
              </h2>
              <Badge variant="secondary">Realtime</Badge>
            </div>
            <div className="space-y-3">
              {systemHealthSummary.map((item) => (
                <div
                  key={item.label}
                  className="flex items-center justify-between rounded-xl border border-gray-100 px-4 py-3 dark:border-gray-800"
                >
                  <div className="flex items-center gap-3 text-sm text-gray-600 dark:text-gray-300">
                    <ServerStackIcon className="h-5 w-5 text-indigo-400" />
                    <span className="font-medium text-gray-900 dark:text-gray-100">
                      {item.label}
                    </span>
                  </div>
                  <Badge
                    variant={
                      item.tone === 'positive'
                        ? 'success'
                        : item.tone === 'negative'
                          ? 'error'
                          : 'secondary'
                    }
                  >
                    {item.value}
                  </Badge>
                </div>
              ))}
            </div>
          </Card>
        </section>

        <section className="grid gap-6 xl:grid-cols-2">
          <Card className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-900">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-50">
                Platform activity feed
              </h2>
              <Badge variant="outline">Global</Badge>
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
                Platform activity will appear as teams interact across tenants.
              </div>
            )}
          </Card>

          <Card className="flex flex-col gap-6 rounded-2xl border border-gray-100 bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-900">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-50">
                System log stream
              </h2>
              <Badge variant="outline">Latest</Badge>
            </div>
            <div className="space-y-4">
              {stats?.recent_system_logs?.length ? (
                stats.recent_system_logs.slice(0, 6).map((log) => (
                  <div
                    key={log.id}
                    className="flex items-start justify-between rounded-xl border border-gray-100 px-4 py-3 dark:border-gray-800"
                  >
                    <div className="flex items-start gap-3">
                      {renderLogIcon(log.level)}
                      <div>
                        <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                          {log.message}
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-400">{log.source}</p>
                        <p className="text-xs text-gray-400">{formatTimestamp(log.timestamp)}</p>
                      </div>
                    </div>
                    {renderLogBadge(log.level)}
                  </div>
                ))
              ) : (
                <div className="flex items-center justify-center rounded-xl border border-dashed border-gray-200 p-6 text-sm text-gray-500 dark:border-gray-800">
                  System logs will show here once events are recorded.
                </div>
              )}
            </div>
          </Card>
        </section>

        <section className="grid gap-6 xl:grid-cols-2">
          <Card className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-900">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-50">
                Activity breakdown
              </h2>
              <Badge variant="outline">By type</Badge>
            </div>
            <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
              Compare which actions are driving activity across tenants.
            </p>
            <div className="mt-6 h-[240px]">
              {activityByType.length ? (
                <SimpleBarChart data={activityByType} dataKey="value" color="#22D3EE" />
              ) : (
                <div className="flex h-full items-center justify-center text-sm text-gray-500">
                  Activity data will appear here once events are collected.
                </div>
              )}
            </div>
          </Card>

          <Card className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-900">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-50">
                Operational summary
              </h2>
              <Badge variant="outline">At a glance</Badge>
            </div>
            <div className="mt-4 grid gap-4 md:grid-cols-2">
              <div className="flex flex-col gap-2 rounded-xl border border-gray-100 p-4 dark:border-gray-800">
                <GaugeCircle className="h-6 w-6 text-indigo-500" />
                <p className="text-sm text-gray-500 dark:text-gray-400">Conversion rate</p>
                <p className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                  {stats?.platform_metrics?.conversion_rate ?? 0}%
                </p>
              </div>
              <div className="flex flex-col gap-2 rounded-xl border border-gray-100 p-4 dark:border-gray-800">
                <ServerStackIcon className="h-6 w-6 text-emerald-500" />
                <p className="text-sm text-gray-500 dark:text-gray-400">Active sessions</p>
                <p className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                  {stats?.system_health?.active_sessions ?? 0}
                </p>
              </div>
              <div className="flex flex-col gap-2 rounded-xl border border-gray-100 p-4 dark:border-gray-800">
                <BarChart3 className="h-6 w-6 text-sky-500" />
                <p className="text-sm text-gray-500 dark:text-gray-400">Weekly signups</p>
                <p className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                  {stats?.platform_metrics?.weekly_signups ?? 0}
                </p>
              </div>
              <div className="flex flex-col gap-2 rounded-xl border border-gray-100 p-4 dark:border-gray-800">
                <ShieldCheckIcon className="h-6 w-6 text-amber-500" />
                <p className="text-sm text-gray-500 dark:text-gray-400">Error rate</p>
                <p className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                  {stats?.system_health?.error_rate ?? 0}%
                </p>
              </div>
            </div>
          </Card>
        </section>
      </DashboardContentGate>
    </div>
  );
}
