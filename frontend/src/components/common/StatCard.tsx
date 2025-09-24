import type { StatCardProps } from '@/types/components';

const colorMap = {
  primary: {
    icon: 'var(--brand-primary)',
    bg: 'rgba(108, 99, 255, 0.1)',
    border: 'rgba(108, 99, 255, 0.2)',
  },
  blue: {
    icon: '#3B82F6',
    bg: 'rgba(59, 130, 246, 0.1)',
    border: 'rgba(59, 130, 246, 0.2)',
  },
  green: {
    icon: 'var(--brand-accent)',
    bg: 'rgba(34, 197, 94, 0.1)',
    border: 'rgba(34, 197, 94, 0.2)',
  },
  accent: {
    icon: 'var(--brand-accent)',
    bg: 'rgba(34, 197, 94, 0.1)',
    border: 'rgba(34, 197, 94, 0.2)',
  },
  orange: {
    icon: '#F59E0B',
    bg: 'rgba(245, 158, 11, 0.1)',
    border: 'rgba(245, 158, 11, 0.2)',
  },
  red: {
    icon: '#EF4444',
    bg: 'rgba(239, 68, 68, 0.1)',
    border: 'rgba(239, 68, 68, 0.2)',
  },
};

export default function StatCard({
  title,
  value,
  icon: Icon,
  change,
  color = 'primary',
  loading = false,
}: StatCardProps) {
  const colors = colorMap[color];

  if (loading) {
    return (
      <div className="card p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="loading-skeleton" style={{ width: '120px', height: '16px' }} />
          <div
            className="loading-skeleton"
            style={{ width: '24px', height: '24px', borderRadius: '50%' }}
          />
        </div>
        <div
          className="loading-skeleton"
          style={{ width: '80px', height: '32px', marginBottom: '8px' }}
        />
        <div className="loading-skeleton" style={{ width: '140px', height: '14px' }} />
      </div>
    );
  }

  return (
    <div className="card p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-medium" style={{ color: 'var(--text-secondary)' }}>
          {title}
        </h3>
        <div
          className="p-2 rounded-lg"
          style={{
            backgroundColor: colors.bg,
            border: `1px solid ${colors.border}`,
          }}
        >
          <Icon
            style={{
              width: '20px',
              height: '20px',
              color: colors.icon,
            }}
          />
        </div>
      </div>

      <div className="mb-2">
        <div className="text-3xl font-bold" style={{ color: 'var(--text-primary)' }}>
          {value}
        </div>
      </div>

      {change && (
        <div className="flex items-center text-sm">
          <span
            className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
              change.trend === 'up' ? 'text-green-700 bg-green-100' : 'text-red-700 bg-red-100'
            }`}
          >
            {change.trend === 'up' ? '+' : '-'}
            {change.value}%
          </span>
          <span className="ml-2" style={{ color: 'var(--text-muted)' }}>
            vs {change.period}
          </span>
        </div>
      )}
    </div>
  );
}
