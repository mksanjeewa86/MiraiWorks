'use client';

import { useAuth } from '@/contexts/AuthContext';
import AppLayout from '@/components/layout/AppLayout';
import CandidateDashboard from '@/components/dashboard/CandidateDashboard';
import RecruiterDashboard from '@/components/dashboard/RecruiterDashboard';
import EmployerDashboard from '@/components/dashboard/EmployerDashboard';
import CompanyAdminDashboard from '@/components/dashboard/CompanyAdminDashboard';
import SuperAdminDashboard from '@/components/dashboard/SuperAdminDashboard';
import ProtectedRoute from '@/components/auth/ProtectedRoute';

function DashboardPageContent() {
  const { user } = useAuth();

  const renderDashboard = () => {
    switch (user?.roles?.[0]?.role?.name) {
      case 'candidate':
        return <CandidateDashboard />;
      case 'member':
        return <RecruiterDashboard />;
      case 'employer':
        return <EmployerDashboard />;
      case 'admin':
        return <CompanyAdminDashboard />;
      case 'system_admin':
        return <SuperAdminDashboard />;
      default:
        return <CandidateDashboard />;
    }
  };

  return <AppLayout>{renderDashboard()}</AppLayout>;
}

export default function DashboardPage() {
  return (
    <ProtectedRoute>
      <DashboardPageContent />
    </ProtectedRoute>
  );
}
