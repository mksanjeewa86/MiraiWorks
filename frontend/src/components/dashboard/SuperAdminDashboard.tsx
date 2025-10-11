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
import { ROUTES } from '@/routes/config';
import { useTranslations } from 'next-intl';

export default function SuperAdminDashboard() {
  const router = useRouter();
  const t = useTranslations('dashboard.superAdmin');
  const tCommon = useTranslations('dashboard.common');
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
        label: t('metrics.companiesOnboarded.label'),
        value: stats.total_companies ?? 0,
        helperText: t('metrics.companiesOnboarded.helperText'),
        trendLabel: `${stats.active_companies ?? 0} ${t('metrics.companiesOnboarded.active')}`,
        trendTone: 'positive' as const,
        icon: <BuildingOffice2Icon className="h-6 w-6" />,
      },
      {
        label: t('metrics.registeredUsers.label'),
        value: stats.total_users ?? 0,
        helperText: t('metrics.registeredUsers.helperText'),
        trendLabel: `${stats.active_users ?? 0} ${t('metrics.registeredUsers.activeMonthly')}`,
        trendTone: 'positive' as const,
        icon: <UsersIcon className="h-6 w-6" />,
      },
      {
        label: t('metrics.openPositions.label'),
        value: stats.total_positions ?? 0,
        helperText: t('metrics.openPositions.helperText'),
        trendLabel: `${stats.total_applications ?? 0} ${t('metrics.openPositions.totalApplications')}`,
        trendTone: 'neutral' as const,
        icon: <BarChart3 className="h-6 w-6" />,
      },
      {
        label: t('metrics.systemUptime.label'),
        value: stats.platform_metrics?.system_uptime
          ? `${stats.platform_metrics.system_uptime}%`
          : tCommon('noData'),
        helperText: t('metrics.systemUptime.helperText'),
        trendLabel: `${stats.system_health?.api_response_time ?? 0}ms ${t('metrics.systemUptime.response')}`,
        trendTone: (stats.platform_metrics?.system_uptime &&
        stats.platform_metrics.system_uptime >= 99.5
          ? 'positive'
          : 'neutral') as 'positive' | 'negative' | 'neutral',
        icon: <ShieldCheckIcon className="h-6 w-6" />,
      },
    ];
  }, [stats, t, tCommon]);

  const examMetrics = useMemo(() => {
    if (!stats) return [];
    const completionRate =
      stats.total_exam_sessions && stats.total_exam_sessions > 0
        ? ((stats.completed_exam_sessions ?? 0) / stats.total_exam_sessions) * 100
        : 0;

    return [
      {
        label: t('examMetrics.totalExams.label'),
        value: stats.total_exams ?? 0,
        helperText: t('examMetrics.totalExams.helperText'),
        trendLabel: `${stats.total_exam_assignments ?? 0} ${t('examMetrics.totalExams.assignments')}`,
        trendTone: 'neutral' as const,
        icon: <ClipboardCheck className="h-6 w-6" />,
      },
      {
        label: t('examMetrics.examSessions.label'),
        value: stats.total_exam_sessions ?? 0,
        helperText: t('examMetrics.examSessions.helperText'),
        trendLabel: `${completionRate.toFixed(1)}% ${t('examMetrics.examSessions.completionRate')}`,
        trendTone: completionRate >= 70 ? ('positive' as const) : ('neutral' as const),
        icon: <Activity className="h-6 w-6" />,
      },
      {
        label: t('examMetrics.averageScore.label'),
        value: stats.avg_exam_score ? `${stats.avg_exam_score.toFixed(1)}%` : tCommon('noData'),
        helperText: t('examMetrics.averageScore.helperText'),
        trendLabel: `${stats.completed_exam_sessions ?? 0} ${t('examMetrics.averageScore.completed')}`,
        trendTone:
          stats.avg_exam_score && stats.avg_exam_score >= 70
            ? ('positive' as const)
            : ('neutral' as const),
        icon: <Award className="h-6 w-6" />,
      },
    ];
  }, [stats, t, tCommon]);

  const platformMetricsData = useMemo(() => {
    if (!stats?.platform_metrics) return [];
    return [
      { name: t('platformEngagement.dailySignups'), value: stats.platform_metrics.daily_signups ?? 0 },
      { name: t('platformEngagement.weeklySignups'), value: stats.platform_metrics.weekly_signups ?? 0 },
      { name: t('platformEngagement.monthlySignups'), value: stats.platform_metrics.monthly_signups ?? 0 },
      { name: t('platformEngagement.monthlyActiveUsers'), value: stats.platform_metrics.monthly_active_users ?? 0 },
    ];
  }, [stats, t]);

  const systemHealthSummary = useMemo(() => {
    const health = stats?.system_health;
    const na = tCommon('noData');
    if (!health) {
      return [
        { label: t('systemHealth.database'), value: na, tone: 'neutral' as const },
        { label: t('systemHealth.apiResponse'), value: na, tone: 'neutral' as const },
        { label: t('systemHealth.activeSessions'), value: na, tone: 'neutral' as const },
        { label: t('systemHealth.errorRate'), value: na, tone: 'neutral' as const },
      ];
    }
    return [
      {
        label: t('systemHealth.database'),
        value: health.database_status === 'healthy' ? t('systemHealth.healthy') : health.database_status === 'warning' ? t('systemHealth.warning') : health.database_status,
        tone:
          health.database_status === 'healthy'
            ? 'positive'
            : health.database_status === 'warning'
              ? 'neutral'
              : 'negative',
      },
      {
        label: t('systemHealth.apiResponse'),
        value: `${health.api_response_time ?? 0} ${t('systemHealth.ms')}`,
        tone: health.api_response_time && health.api_response_time < 400 ? 'positive' : 'neutral',
      },
      {
        label: t('systemHealth.activeSessions'),
        value: health.active_sessions ?? 0,
        tone: 'neutral' as const,
      },
      {
        label: t('systemHealth.errorRate'),
        value: `${health.error_rate ?? 0}%`,
        tone: health.error_rate && health.error_rate > 3 ? 'negative' : 'positive',
      },
    ];
  }, [stats, t, tCommon]);

  const activityByType = useMemo(() => {
    const counts = new Map<string, number>();
    activity.forEach((item) => {
      const key = item.type ?? 'update';
      counts.set(key, (counts.get(key) ?? 0) + 1);
    });
    return Array.from(counts.entries()).map(([name, value]) => ({ name, value }));
  }, [activity]);

  const formatTimestamp = (value?: string) => {
    if (!value) return tCommon('noData');
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return tCommon('noData');
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
        return <Badge variant="error">{t('systemLogs.error')}</Badge>;
      case 'warning':
        return <Badge variant="warning">{t('systemLogs.warningBadge')}</Badge>;
      default:
        return <Badge variant="secondary">{t('systemLogs.info')}</Badge>;
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
        title={t('header.title')}
        subtitle={t('header.subtitle')}
        description={t('header.description')}
        actions={
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={loadDashboardData}>
              {t('header.refreshButton')}
            </Button>
            <Button size="sm" onClick={() => router.push(ROUTES.ADMIN.SETTINGS)}>
              {t('header.managePlatformButton')}
            </Button>
          </div>
        }
        meta={`${t('header.telemetrySynced')} ${new Date().toLocaleTimeString()}`}
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
              {t('examMetrics.title')}
            </h2>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              {t('examMetrics.description')}
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
                {t('platformEngagement.title')}
              </h2>
              <Badge variant="outline">{t('platformEngagement.badge')}</Badge>
            </div>
            <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
              {t('platformEngagement.description')}
            </p>
            <div className="mt-6 h-[260px]">
              {platformMetricsData.length ? (
                <SimpleAreaChart data={platformMetricsData} dataKey="value" color="#6366F1" />
              ) : (
                <div className="flex h-full items-center justify-center text-sm text-gray-500">
                  {t('platformEngagement.noData')}
                </div>
              )}
            </div>
          </Card>

          <Card className="flex flex-col gap-4 rounded-2xl border border-gray-100 bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-900">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-50">
                {t('systemHealth.title')}
              </h2>
              <Badge variant="secondary">{t('systemHealth.badge')}</Badge>
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
                {t('platformActivity.title')}
              </h2>
              <Badge variant="outline">{t('platformActivity.badge')}</Badge>
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
                {t('platformActivity.noActivity')}
              </div>
            )}
          </Card>

          <Card className="flex flex-col gap-6 rounded-2xl border border-gray-100 bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-900">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-50">
                {t('systemLogs.title')}
              </h2>
              <Badge variant="outline">{t('systemLogs.badge')}</Badge>
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
                  {t('systemLogs.noLogs')}
                </div>
              )}
            </div>
          </Card>
        </section>

        <section className="grid gap-6 xl:grid-cols-2">
          <Card className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-900">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-50">
                {t('activityBreakdown.title')}
              </h2>
              <Badge variant="outline">{t('activityBreakdown.badge')}</Badge>
            </div>
            <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
              {t('activityBreakdown.description')}
            </p>
            <div className="mt-6 h-[240px]">
              {activityByType.length ? (
                <SimpleBarChart data={activityByType} dataKey="value" color="#22D3EE" />
              ) : (
                <div className="flex h-full items-center justify-center text-sm text-gray-500">
                  {t('activityBreakdown.noData')}
                </div>
              )}
            </div>
          </Card>

          <Card className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-900">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-50">
                {t('operationalSummary.title')}
              </h2>
              <Badge variant="outline">{t('operationalSummary.badge')}</Badge>
            </div>
            <div className="mt-4 grid gap-4 md:grid-cols-2">
              <div className="flex flex-col gap-2 rounded-xl border border-gray-100 p-4 dark:border-gray-800">
                <GaugeCircle className="h-6 w-6 text-indigo-500" />
                <p className="text-sm text-gray-500 dark:text-gray-400">{t('operationalSummary.conversionRate')}</p>
                <p className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                  {stats?.platform_metrics?.conversion_rate ?? 0}%
                </p>
              </div>
              <div className="flex flex-col gap-2 rounded-xl border border-gray-100 p-4 dark:border-gray-800">
                <ServerStackIcon className="h-6 w-6 text-emerald-500" />
                <p className="text-sm text-gray-500 dark:text-gray-400">{t('operationalSummary.activeSessions')}</p>
                <p className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                  {stats?.system_health?.active_sessions ?? 0}
                </p>
              </div>
              <div className="flex flex-col gap-2 rounded-xl border border-gray-100 p-4 dark:border-gray-800">
                <BarChart3 className="h-6 w-6 text-sky-500" />
                <p className="text-sm text-gray-500 dark:text-gray-400">{t('operationalSummary.weeklySignups')}</p>
                <p className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                  {stats?.platform_metrics?.weekly_signups ?? 0}
                </p>
              </div>
              <div className="flex flex-col gap-2 rounded-xl border border-gray-100 p-4 dark:border-gray-800">
                <ShieldCheckIcon className="h-6 w-6 text-amber-500" />
                <p className="text-sm text-gray-500 dark:text-gray-400">{t('operationalSummary.errorRate')}</p>
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
