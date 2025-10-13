'use client';

import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import { useTranslations } from 'next-intl';
import AppLayout from '@/components/layout/AppLayout';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import { Button } from '@/components/ui';
import { LoadingSpinner } from '@/components/ui';
import ProfileViewsAnalytics from '@/components/profile/ProfileViewsAnalytics';
import { ArrowLeft, BarChart3 } from 'lucide-react';

function ProfileAnalyticsPageContent() {
  const { user } = useAuth();
  const router = useRouter();
  const t = useTranslations('profile');

  if (!user) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center h-64">
          <LoadingSpinner className="w-8 h-8" />
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout>
      <div className="bg-gray-50 dark:bg-gray-900 min-h-screen py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Header */}
          <div className="mb-8">
            <Button
              variant="outline"
              leftIcon={<ArrowLeft className="h-4 w-4" />}
              onClick={() => router.push('/profile')}
              className="mb-4"
            >
              Back to Profile
            </Button>

            <div className="flex items-center gap-3 mb-2">
              <div className="p-3 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-lg">
                <BarChart3 className="h-6 w-6 text-white" />
              </div>
              <h1 className="text-3xl font-bold" style={{ color: 'var(--text-primary)' }}>
                Profile View Analytics
              </h1>
            </div>
            <p className="text-lg" style={{ color: 'var(--text-secondary)' }}>
              Track who's viewing your profile and gain insights into your professional visibility
            </p>
          </div>

          {/* Analytics Component */}
          <ProfileViewsAnalytics userId={user.id} days={30} />
        </div>
      </div>
    </AppLayout>
  );
}

export default function ProfileAnalyticsPage() {
  return (
    <ProtectedRoute>
      <ProfileAnalyticsPageContent />
    </ProtectedRoute>
  );
}
