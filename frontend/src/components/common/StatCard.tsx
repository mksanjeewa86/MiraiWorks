import { type LucideIcon } from 'lucide-react';

interface StatCardProps {
  title: string;
  value: string | number;
  icon: LucideIcon;
  change?: {
    value: number;
    trend: 'up' | 'down' | 'neutral';
    period: string;
  };
  color?: 'primary' | 'accent' | 'orange' | 'red' | 'blue';
  loading?: boolean;
}

export default function StatCard({ 
  title, 
  value, 
  icon: Icon, 
  change, 
  color = 'primary', 
  loading = false 
}: StatCardProps) {
  const colorStyles = {
    primary: {
      bg: { backgroundColor: 'rgba(108, 99, 255, 0.1)' },
      icon: { color: 'var(--brand-primary)' },
      trend: {
        up: { color: 'var(--brand-accent)' },
        down: { color: '#dc2626' },
        neutral: { color: 'var(--text-muted)' }
      }
    },
    accent: {
      bg: { backgroundColor: 'rgba(34, 197, 94, 0.1)' },
      icon: { color: 'var(--brand-accent)' },
      trend: {
        up: { color: 'var(--brand-accent)' },
        down: { color: '#dc2626' },
        neutral: { color: 'var(--text-muted)' }
      }
    },
    orange: {
      bg: { backgroundColor: 'rgba(245, 158, 11, 0.1)' },
      icon: { color: '#ea580c' },
      trend: {
        up: { color: 'var(--brand-accent)' },
        down: { color: '#dc2626' },
        neutral: { color: 'var(--text-muted)' }
      }
    },
    red: {
      bg: { backgroundColor: 'rgba(239, 68, 68, 0.1)' },
      icon: { color: '#dc2626' },
      trend: {
        up: { color: 'var(--brand-accent)' },
        down: { color: '#dc2626' },
        neutral: { color: 'var(--text-muted)' }
      }
    },
    blue: {
      bg: { backgroundColor: 'rgba(59, 130, 246, 0.1)' },
      icon: { color: '#2563eb' },
      trend: {
        up: { color: 'var(--brand-accent)' },
        down: { color: '#dc2626' },
        neutral: { color: 'var(--text-muted)' }
      }
    }
  };

  const colors = colorStyles[color];

  if (loading) {
    return (
      <div className="card p-6 shadow-sm">
        <div className="flex items-center">
          <div className="flex-shrink-0">
            <div className="w-12 h-12 bg-gray-200 dark:bg-gray-700 rounded-2xl animate-pulse" />
          </div>
          <div className="ml-5 w-0 flex-1">
            <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded animate-pulse mb-2" />
            <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
          </div>
        </div>
        {change && (
          <div className="mt-4">
            <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded animate-pulse w-24" />
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="card p-6 shadow-sm hover:shadow-md transition-shadow">
      <div className="flex items-center">
        <div className="flex-shrink-0">
          <div className="w-12 h-12 rounded-2xl flex items-center justify-center" style={colors.bg}>
            <Icon className="h-6 w-6" style={colors.icon} />
          </div>
        </div>
        <div className="ml-5 w-0 flex-1">
          <dl>
            <dt className="text-sm font-medium text-muted-600 dark:text-muted-300 truncate">
              {title}
            </dt>
            <dd className="text-2xl font-bold text-gray-900 dark:text-white">
              {typeof value === 'number' ? value.toLocaleString() : value}
            </dd>
          </dl>
        </div>
      </div>
      
      {change && (
        <div className="mt-4">
          <div className="flex items-center text-sm">
            <span className="font-medium" style={colors.trend[change.trend]}>
              {change.trend === 'up' ? '↗' : change.trend === 'down' ? '↘' : '→'} 
              {Math.abs(change.value)}%
            </span>
            <span className="text-muted-500 dark:text-muted-400 ml-2">
              vs {change.period}
            </span>
          </div>
        </div>
      )}
    </div>
  );
}