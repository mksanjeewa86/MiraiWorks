import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';

// Import page components (will be created)
import LoginPage from './pages/auth/LoginPage';
import RegisterPage from './pages/auth/RegisterPage';
import TwoFactorPage from './pages/auth/TwoFactorPage';
import ForgotPasswordPage from './pages/auth/ForgotPasswordPage';
import ResetPasswordPage from './pages/auth/ResetPasswordPage';

// Dashboard layouts
import DashboardLayout from './layouts/DashboardLayout';
import SuperAdminDashboard from './pages/dashboard/SuperAdminDashboard';
import CompanyAdminDashboard from './pages/dashboard/CompanyAdminDashboard';
import RecruiterDashboard from './pages/dashboard/RecruiterDashboard';
import EmployerDashboard from './pages/dashboard/EmployerDashboard';
import CandidateDashboard from './pages/dashboard/CandidateDashboard';

// Feature pages
import MessagesPage from './pages/messages/MessagesPage';
import InterviewsPage from './pages/interviews/InterviewsPage';
import InterviewDetailsPage from './pages/interviews/InterviewDetailsPage';
import CalendarPage from './pages/calendar/CalendarPage';
import ResumesPage from './pages/resumes/ResumesPage';
import ResumeBuilderPage from './pages/resumes/ResumeBuilderPage';
import ResumePreviewPage from './pages/resumes/ResumePreviewPage';
import ProfilePage from './pages/profile/ProfilePage';
import SettingsPage from './pages/settings/SettingsPage';

// Public pages
import PublicLayout from './layouts/PublicLayout';
import HomePage from './pages/public/HomePage';
import AboutPage from './pages/public/AboutPage';
import ContactPage from './pages/public/ContactPage';
import CompanyProfilePage from './pages/public/CompanyProfilePage';
import PublicResumePage from './pages/public/PublicResumePage';

// Error pages
import NotFoundPage from './pages/error/NotFoundPage';
import UnauthorizedPage from './pages/error/UnauthorizedPage';
import ErrorBoundary from './components/ErrorBoundary';

// Create React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <ErrorBoundary>
          <Router>
            <Routes>
              {/* Public routes */}
              <Route path="/" element={<PublicLayout />}>
                <Route index element={<HomePage />} />
                <Route path="about" element={<AboutPage />} />
                <Route path="contact" element={<ContactPage />} />
                <Route path="company/:slug" element={<CompanyProfilePage />} />
                <Route path="resume/:slug" element={<PublicResumePage />} />
              </Route>

              {/* Authentication routes */}
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
              <Route path="/verify-2fa" element={<TwoFactorPage />} />
              <Route path="/forgot-password" element={<ForgotPasswordPage />} />
              <Route path="/reset-password" element={<ResetPasswordPage />} />

              {/* Protected dashboard routes */}
              <Route
                path="/dashboard"
                element={
                  <ProtectedRoute>
                    <DashboardLayout />
                  </ProtectedRoute>
                }
              >
                {/* Role-based dashboard redirects */}
                <Route index element={<DashboardRedirect />} />
                
                {/* Super Admin Dashboard */}
                <Route
                  path="super-admin"
                  element={
                    <ProtectedRoute requiredRoles={['super_admin']}>
                      <SuperAdminDashboard />
                    </ProtectedRoute>
                  }
                />
                
                {/* Company Admin Dashboard */}
                <Route
                  path="company-admin"
                  element={
                    <ProtectedRoute requiredRoles={['company_admin']}>
                      <CompanyAdminDashboard />
                    </ProtectedRoute>
                  }
                />
                
                {/* Recruiter Dashboard */}
                <Route
                  path="recruiter"
                  element={
                    <ProtectedRoute requiredRoles={['recruiter']}>
                      <RecruiterDashboard />
                    </ProtectedRoute>
                  }
                />
                
                {/* Employer Dashboard */}
                <Route
                  path="employer"
                  element={
                    <ProtectedRoute requiredRoles={['employer']}>
                      <EmployerDashboard />
                    </ProtectedRoute>
                  }
                />
                
                {/* Candidate Dashboard */}
                <Route
                  path="candidate"
                  element={
                    <ProtectedRoute requiredRoles={['candidate']}>
                      <CandidateDashboard />
                    </ProtectedRoute>
                  }
                />

                {/* Shared feature routes */}
                <Route path="messages" element={<MessagesPage />} />
                <Route path="messages/:conversationId" element={<MessagesPage />} />
                
                <Route path="interviews" element={<InterviewsPage />} />
                <Route path="interviews/:interviewId" element={<InterviewDetailsPage />} />
                
                <Route path="calendar" element={<CalendarPage />} />
                
                <Route path="resumes" element={<ResumesPage />} />
                <Route path="resumes/new" element={<ResumeBuilderPage />} />
                <Route path="resumes/:resumeId" element={<ResumeBuilderPage />} />
                <Route path="resumes/:resumeId/preview" element={<ResumePreviewPage />} />
                
                <Route path="profile" element={<ProfilePage />} />
                <Route path="settings" element={<SettingsPage />} />
              </Route>

              {/* Error routes */}
              <Route path="/unauthorized" element={<UnauthorizedPage />} />
              <Route path="/404" element={<NotFoundPage />} />
              <Route path="*" element={<Navigate to="/404" replace />} />
            </Routes>
          </Router>
        </ErrorBoundary>
      </AuthProvider>
    </QueryClientProvider>
  );
}

// Component to redirect to appropriate dashboard based on user role
function DashboardRedirect() {
  const { user } = useAuth();

  if (!user?.roles || user.roles.length === 0) {
    return <Navigate to="/unauthorized" replace />;
  }

  // Get the primary role (first role)
  const primaryRole = user.roles[0].role.name;

  const roleRoutes = {
    super_admin: '/dashboard/super-admin',
    company_admin: '/dashboard/company-admin',
    recruiter: '/dashboard/recruiter',
    employer: '/dashboard/employer',
    candidate: '/dashboard/candidate',
  };

  const redirectPath = roleRoutes[primaryRole as keyof typeof roleRoutes];
  
  if (redirectPath) {
    return <Navigate to={redirectPath} replace />;
  }

  return <Navigate to="/unauthorized" replace />;
}

export default App
