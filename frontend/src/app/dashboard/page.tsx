'use client';

import { useAuth } from '@/contexts/AuthContext';
import AppLayout from '@/components/layout/AppLayout';
import CandidateDashboard from '@/components/dashboard/CandidateDashboard';
import RecruiterDashboard from '@/components/dashboard/RecruiterDashboard';
import EmployerDashboard from '@/components/dashboard/EmployerDashboard';
import CompanyAdminDashboard from '@/components/dashboard/CompanyAdminDashboard';
import SuperAdminDashboard from '@/components/dashboard/SuperAdminDashboard';
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
    switch (user?.roles?.[0]?.role?.name) {
      case 'candidate':
        return <CandidateDashboard />;
      case 'recruiter':
        return <RecruiterDashboard />;
      case 'employer':
        return <EmployerDashboard />;
      case 'company_admin':
        return <CompanyAdminDashboard />;
      case 'super_admin':
        return <SuperAdminDashboard />;
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