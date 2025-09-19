'use client';

import AppLayout from '@/components/layout/AppLayout';
import PlaceholderPage from '@/components/common/PlaceholderPage';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import { Users } from 'lucide-react';

function InterviewsPageContent() {
  return (
    <AppLayout>
      <PlaceholderPage
        icon={<Users className="h-16 w-16" style={{ color: 'var(--brand-primary)' }} />}
        title="Interview management is coming soon"
        description="We are polishing the end-to-end interview scheduling experience. For now, please coordinate interviews outside the app."
      />
    </AppLayout>
  );
}

export default function InterviewsPage() {
  return (
    <ProtectedRoute>
      <InterviewsPageContent />
    </ProtectedRoute>
  );
}
