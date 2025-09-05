'use client';

import { useAuth } from '@/contexts/AuthContext';
import AppLayout from '@/components/layout/AppLayout';
import CandidateOverview from '@/components/dashboard/CandidateOverview';
import CandidateDashboard from '@/components/dashboard/CandidateDashboard';
import RecruiterDashboard from '@/components/dashboard/RecruiterDashboard';
import EmployerDashboard from '@/components/dashboard/EmployerDashboard';
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function DashboardPage() {
  const { user, isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/auth/login');
    }
  }, [isAuthenticated, isLoading, router]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="loading-skeleton w-16 h-16 rounded-full"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  const renderDashboard = () => {
    switch (user?.role) {
      case 'candidate':
        return <CandidateDashboard />;
      case 'recruiter':
        return <RecruiterDashboard />;
      case 'employer':
        return <EmployerDashboard />;
      case 'company_admin':
        return <div className="p-6"><h1 className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>Company Admin Dashboard</h1><p style={{ color: 'var(--text-secondary)' }}>Coming soon...</p></div>;
      case 'super_admin':
        return <div className="p-6"><h1 className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>Super Admin Dashboard</h1><p style={{ color: 'var(--text-secondary)' }}>Coming soon...</p></div>;
      default:
        return <CandidateDashboard />;
    }
  };

  return (
    <AppLayout>
      {renderDashboard()}
    </AppLayout>
  );
}