'use client';

import AppLayout from '@/components/layout/AppLayout';
import PlaceholderPage from '@/components/common/PlaceholderPage';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import { CalendarCheck } from 'lucide-react';

function CalendarPageContent() {
  return (
    <AppLayout>
      <PlaceholderPage
        icon={<CalendarCheck className="h-16 w-16" style={{ color: 'var(--brand-primary)' }} />}
        title="Calendar is on the way"
        description="Scheduling, syncing, and event management are coming soon. In the meantime, you can continue to manage interviews and meetings manually."
      />
    </AppLayout>
  );
}

export default function CalendarPage() {
  return (
    <ProtectedRoute>
      <CalendarPageContent />
    </ProtectedRoute>
  );
}
