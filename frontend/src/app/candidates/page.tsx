'use client';

import AppLayout from '@/components/layout/AppLayout';
import PlaceholderPage from '@/components/common/PlaceholderPage';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import { UserRound } from 'lucide-react';

function CandidatesPageContent() {
  return (
    <AppLayout>
      <PlaceholderPage
        icon={<UserRound className="h-16 w-16" style={{ color: 'var(--brand-primary)' }} />}
        title="Candidate management coming soon"
        description="Candidate pipelines, screening tools, and collaborative reviews are on the roadmap. Until then, please manage candidates outside the app."
      />
    </AppLayout>
  );
}

export default function CandidatesPage() {
  return (
    <ProtectedRoute>
      <CandidatesPageContent />
    </ProtectedRoute>
  );
}
