'use client';

import { useEffect, useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import { BuildingOffice2Icon, UsersIcon, UserPlusIcon } from '@heroicons/react/24/outline';
import { CalendarDaysIcon } from '@heroicons/react/24/solid';
import { Activity } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { dashboardApi } from '@/api/dashboard';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import {
  DashboardContentGate,
  DashboardHeader,
  DashboardMetricCard,
} from '@/components/dashboard/common';
import { SimpleBarChart } from '@/components/dashboard/Charts';
import type { CompanyAdminStats } from '@/types/dashboard';

export default function CompanyAdminDashboard() {
  const { user } = useAuth();
  const router = useRouter();
  const [stats, setStats] = useState<CompanyAdminStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const response = await dashboardApi.getStats();
      setStats(response.data as CompanyAdminStats);
      setError(null);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const metrics = useMemo(() => {
    if (!stats) return [];
    return [
      {
        label: 'Total employees',
        value: stats.total_employees ?? 0,
        helperText: 'All workforce members',
        trendLabel: `${stats.active_employees ?? 0} active`,
        trendTone: 'positive' as const,
        icon: <UsersIcon className="h-6 w-6" />,
      },
      {
        label: 'Active positions',
        value: stats.active_positions ?? 0,
        helperText: 'Open roles across the company',
        trendLabel: `${stats.total_positions ?? 0} total roles`,
        trendTone: 'neutral' as const,
        icon: <BuildingOffice2Icon className="h-6 w-6" />,
      },
      {
        label: 'Pending employees',
        value: stats.pending_employees ?? 0,
        helperText: 'Awaiting onboarding approval',
        trendLabel: `${stats.total_recruiters ?? 0} recruiters supporting`,
        trendTone: (stats.pending_employees && stats.pending_employees > 0
          ? 'negative'
          : 'neutral') as 'positive' | 'negative' | 'neutral',
        icon: <UserPlusIcon className="h-6 w-6" />,
      },
      {
        label: 'Interviews scheduled',
        value: stats.interviews_scheduled ?? 0,
        helperText: 'Upcoming interviews company-wide',
        trendLabel: `${stats.total_applications ?? 0} applications`,
        trendTone: 'neutral' as const,
        icon: <CalendarDaysIcon className="h-6 w-6" />,
      },
    ];
  }, [stats]);

  const activityByType = useMemo(() => {
    const counts = new Map<string, number>();
    (stats?.recent_activities ?? []).forEach((activity) => {
      const key = activity.type ?? 'update';
      counts.set(key, (counts.get(key) ?? 0) + 1);
    });
    return Array.from(counts.entries()).map(([name, value]) => ({ name, value }));
  }, [stats]);

  const employeeRatios = useMemo(() => {
    if (!stats) return { active: 0, pending: 0 };
    const total = Math.max(stats.total_employees ?? 0, 1);
    return {
      active: Math.round(((stats.active_employees ?? 0) / total) * 100),
      pending: Math.round(((stats.pending_employees ?? 0) / total) * 100),
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
        title="Company administration portal"
        subtitle={`Hello${user?.full_name ? `, ${user.full_name}` : ''}`}
        description="Oversee staffing health, approve team members, and keep operations moving."
        actions={
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={loadDashboardData}>
              Refresh
            </Button>
            <Button size="sm" onClick={() => router.push('/app/employees/new')}>
              Add employee
            </Button>
          </div>
        }
        meta={`Snapshot ${new Date().toLocaleTimeString()}`}
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

        <section className="grid gap-6 xl:grid-cols-3">
          <Card className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-900 xl:col-span-2">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-50">
                Employee distribution
              </h2>
              <Badge variant="outline">Team health</Badge>
            </div>
            <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
              View how your workforce is balanced between active, pending, and recruiter members.
            </p>
            <div className="mt-6 grid gap-4 md:grid-cols-3">
              <div className="rounded-xl border border-gray-100 p-4 dark:border-gray-800">
                <p className="text-xs uppercase tracking-wide text-gray-500 dark:text-gray-400">
                  Active
                </p>
                <p className="mt-2 text-2xl font-semibold text-gray-900 dark:text-gray-50">
                  {stats?.active_employees ?? 0}
                </p>
                <Progress className="mt-3" value={employeeRatios.active} max={100} />
                <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                  {employeeRatios.active}% of total
                </p>
              </div>
              <div className="rounded-xl border border-gray-100 p-4 dark:border-gray-800">
                <p className="text-xs uppercase tracking-wide text-gray-500 dark:text-gray-400">
                  Pending
                </p>
                <p className="mt-2 text-2xl font-semibold text-gray-900 dark:text-gray-50">
                  {stats?.pending_employees ?? 0}
                </p>
                <Progress className="mt-3" value={employeeRatios.pending} max={100} />
                <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                  {employeeRatios.pending}% of total
                </p>
              </div>
              <div className="rounded-xl border border-gray-100 p-4 dark:border-gray-800">
                <p className="text-xs uppercase tracking-wide text-gray-500 dark:text-gray-400">
                  Recruiters
                </p>
                <p className="mt-2 text-2xl font-semibold text-gray-900 dark:text-gray-50">
                  {stats?.total_recruiters ?? 0}
                </p>
                <p className="mt-3 text-sm text-gray-500 dark:text-gray-400">
                  Ensure recruiters have the right access and capacity.
                </p>
              </div>
            </div>
          </Card>

          <Card className="flex flex-col gap-4 rounded-2xl border border-gray-100 bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-900">
            <div>
              <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-50">
                Activity by category
              </h2>
              <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                Track where your team spends most of its time.
              </p>
            </div>
            <div className="h-[220px]">
              {activityByType.length ? (
                <SimpleBarChart data={activityByType} dataKey="value" color="#F97316" />
              ) : (
                <div className="flex h-full items-center justify-center text-sm text-gray-500">
                  Recent activity will populate here once actions are logged.
                </div>
              )}
            </div>
          </Card>
        </section>

        <section className="grid gap-6 xl:grid-cols-2">
          <Card className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-900">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-50">
                Recent company activity
              </h2>
              <Badge variant="outline">Last 5</Badge>
            </div>
            <div className="mt-4 space-y-4">
              {stats?.recent_activities?.length ? (
                stats.recent_activities.slice(0, 6).map((activity) => (
                  <div
                    key={activity.id}
                    className="flex items-start justify-between rounded-xl border border-gray-100 px-4 py-3 dark:border-gray-800"
                  >
                    <div className="flex items-start gap-3">
                      <Activity className="h-5 w-5 text-indigo-500" />
                      <div>
                        <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                          {activity.description}
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-400">
                          by {activity.user_name}
                        </p>
                        <p className="text-xs text-gray-400">
                          {formatTimestamp(activity.timestamp)}
                        </p>
                      </div>
                    </div>
                    <Badge variant="outline">{activity.type}</Badge>
                  </div>
                ))
              ) : (
                <div className="flex h-full items-center justify-center rounded-xl border border-dashed border-gray-200 p-6 text-sm text-gray-500 dark:border-gray-800">
                  Company activity will display once actions are performed.
                </div>
              )}
            </div>
          </Card>

          <Card className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-900">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-50">
                Admin quick actions
              </h2>
              <Badge variant="outline">Shortcuts</Badge>
            </div>
            <div className="mt-4 grid gap-4 sm:grid-cols-2">
              <Button
                className="h-20 flex-col justify-center gap-2"
                onClick={() => router.push('/app/employees')}
              >
                Manage employees
              </Button>
              <Button
                variant="outline"
                className="h-20 flex-col justify-center gap-2"
                onClick={() => router.push('/app/positions')}
              >
                Manage positions
              </Button>
              <Button
                variant="outline"
                className="h-20 flex-col justify-center gap-2"
                onClick={() => router.push('/app/applications')}
              >
                Review applications
              </Button>
              <Button
                variant="outline"
                className="h-20 flex-col justify-center gap-2"
                onClick={() => router.push('/app/settings')}
              >
                Company settings
              </Button>
            </div>
          </Card>
        </section>
      </DashboardContentGate>
    </div>
  );
}
