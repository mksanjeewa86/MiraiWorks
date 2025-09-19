'use client';

import AppLayout from '@/components/layout/AppLayout';
import PlaceholderPage from '@/components/common/PlaceholderPage';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import { BriefcaseBusiness } from 'lucide-react';

function PositionsPageContent() {
  return (
    <AppLayout>
      <PlaceholderPage
        icon={<BriefcaseBusiness className="h-16 w-16" style={{ color: 'var(--brand-primary)' }} />}
        title="Position management in progress"
        description="Job requisitions, approval workflows, and publishing tools are being built. We appreciate your patience while we finish this module."
      />
    </AppLayout>
  );
}

export default function PositionsPage() {
  return (
    <ProtectedRoute>
      <PositionsPageContent />
    </ProtectedRoute>
  );
}
