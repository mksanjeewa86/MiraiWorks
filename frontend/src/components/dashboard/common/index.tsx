import type { ReactNode } from 'react';
import { clsx } from 'clsx';

import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { LoadingSpinner } from '@/components/ui/loading-spinner';

interface DashboardContentGateProps {
  loading: boolean;
  error?: string | null;
  onRetry?: () => void;
  children: ReactNode;
}

export function DashboardContentGate({
  loading,
  error,
  onRetry,
  children,
}: DashboardContentGateProps) {
  if (loading) {
    return (
      <div className="flex h-80 items-center justify-center rounded-2xl border border-dashed border-gray-200 dark:border-gray-800">
        <LoadingSpinner className="h-10 w-10" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-2xl border border-red-200 bg-red-50 p-6 dark:border-red-900/50 dark:bg-red-900/10">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 className="text-lg font-semibold text-red-800 dark:text-red-200">
              We couldn't load your dashboard
            </h2>
            <p className="mt-1 text-sm text-red-700 dark:text-red-300">{error}</p>
          </div>
          {onRetry ? (
            <Button onClick={onRetry} variant="outline" className="self-start sm:self-auto">
              Try again
            </Button>
          ) : null}
        </div>
      </div>
    );
  }

  return <>{children}</>;
}

interface DashboardHeaderProps {
  title: string;
  subtitle?: string;
  description?: string;
  actions?: ReactNode;
  meta?: ReactNode;
}

export function DashboardHeader({
  title,
  subtitle,
  description,
  actions,
  meta,
}: DashboardHeaderProps) {
  return (
    <div className="flex flex-col gap-4 rounded-2xl border border-transparent bg-gradient-to-br from-gray-50 via-white to-gray-50 p-6 dark:from-gray-900 dark:via-gray-950 dark:to-gray-900 lg:flex-row lg:items-center lg:justify-between">
      <div className="space-y-2">
        <div className="flex items-center gap-3">
          <span
            aria-hidden="true"
            className="flex h-10 w-10 items-center justify-center rounded-2xl bg-gradient-to-tr from-indigo-500/10 to-indigo-500/20"
          >
            <span className="h-2.5 w-2.5 rounded-full bg-indigo-500 dark:bg-indigo-300" />
          </span>
          <h1 className="text-2xl font-semibold text-gray-900 dark:text-gray-50">{title}</h1>
        </div>
        {subtitle ? <p className="text-sm text-gray-500 dark:text-gray-400">{subtitle}</p> : null}
        {description ? (
          <p className="text-sm text-gray-600 dark:text-gray-400">{description}</p>
        ) : null}
        {meta ? <div className="pt-2 text-xs text-gray-400">{meta}</div> : null}
      </div>
      {actions ? <div className="flex flex-wrap gap-2">{actions}</div> : null}
    </div>
  );
}

interface DashboardMetricCardProps {
  label: string;
  value: string | number;
  helperText?: string;
  icon?: ReactNode;
  iconClassName?: string;
  trendLabel?: string;
  trendTone?: 'positive' | 'negative' | 'neutral';
}

const trendToneClasses: Record<NonNullable<DashboardMetricCardProps['trendTone']>, string> = {
  positive: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-500/10 dark:text-emerald-300',
  negative: 'bg-rose-100 text-rose-700 dark:bg-rose-500/10 dark:text-rose-300',
  neutral: 'bg-gray-100 text-gray-600 dark:bg-gray-700/60 dark:text-gray-300',
};

export function DashboardMetricCard({
  label,
  value,
  helperText,
  icon,
  iconClassName,
  trendLabel,
  trendTone = 'neutral',
}: DashboardMetricCardProps) {
  return (
    <Card className="h-full rounded-2xl border border-gray-100/70 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md dark:border-gray-800/80 dark:bg-gray-900">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-medium uppercase tracking-wide text-gray-500 dark:text-gray-400">
            {label}
          </p>
          <p className="mt-3 text-3xl font-semibold tracking-tight text-gray-900 dark:text-gray-50">
            {typeof value === 'number' ? formatNumber(value) : value}
          </p>
        </div>
        {icon ? (
          <span
            className={clsx(
              'rounded-xl bg-gradient-to-tr from-indigo-500/10 to-indigo-500/20 p-3 text-indigo-600 dark:from-indigo-500/10 dark:to-indigo-400/20 dark:text-indigo-200',
              iconClassName
            )}
          >
            {icon}
          </span>
        ) : null}
      </div>
      <div className="mt-4 flex items-center gap-3 text-sm">
        {trendLabel ? (
          <span
            className={clsx(
              'inline-flex items-center gap-2 rounded-full px-2.5 py-1 text-xs font-medium',
              trendToneClasses[trendTone]
            )}
          >
            {trendLabel}
          </span>
        ) : null}
        {helperText ? (
          <span className="text-sm text-gray-500 dark:text-gray-400">{helperText}</span>
        ) : null}
      </div>
    </Card>
  );
}

export function formatNumber(value: number) {
  return new Intl.NumberFormat('en-US', { maximumFractionDigits: 1 }).format(value);
}
