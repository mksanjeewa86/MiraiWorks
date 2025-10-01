'use client';

import { Card } from '@/components/ui';
import { Button } from '@/components/ui';
import type { PlaceholderPageProps } from '@/types/components';

export default function PlaceholderPage({
  title,
  description,
  icon,
  actions,
  primaryAction,
}: PlaceholderPageProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16">
      <Card className="max-w-2xl w-full text-center p-10 space-y-6">
        <div className="flex justify-center text-5xl" aria-hidden>
          <span>{icon ?? '🚧'}</span>
        </div>
        <div className="space-y-3">
          <h1 className="text-2xl font-semibold" style={{ color: 'var(--text-primary)' }}>
            {title}
          </h1>
          <p className="text-base" style={{ color: 'var(--text-secondary)' }}>
            {description}
          </p>
        </div>
        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          {primaryAction && <Button onClick={primaryAction.onClick}>{primaryAction.label}</Button>}
          {actions}
        </div>
      </Card>
    </div>
  );
}
