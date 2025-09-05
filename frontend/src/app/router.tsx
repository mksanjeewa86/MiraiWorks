import { createBrowserRouter, Navigate } from 'react-router-dom'
import { useContext } from 'react'
import { AuthContext } from '../contexts/AuthContext'
import AppLayout from '../layout/AppLayout'
import PublicLayout from '../layouts/PublicLayout'

// Auth pages
import LoginPage from '../pages/auth/LoginPage'
import TwoFactorPage from '../pages/auth/TwoFactorPage'
import RegisterPage from '../pages/auth/RegisterPage'
import ForgotPasswordPage from '../pages/auth/ForgotPasswordPage'
import ResetPasswordPage from '../pages/auth/ResetPasswordPage'

// Dashboard pages
import CandidateDashboard from '../pages/dashboard/CandidateDashboard'
import RecruiterDashboard from '../pages/dashboard/RecruiterDashboard'
import EmployerDashboard from '../pages/dashboard/EmployerDashboard'
import CompanyAdminDashboard from '../pages/dashboard/CompanyAdminDashboard'
import SuperAdminDashboard from '../pages/dashboard/SuperAdminDashboard'

// Feature pages
import MessagesPage from '../pages/messages/MessagesPage'
import CalendarPage from '../pages/calendar/CalendarPage'
import InterviewsPage from '../pages/interviews/InterviewsPage'
import ResumesPage from '../pages/resumes/ResumesPage'
import SettingsPage from '../pages/settings/SettingsPage'
import ProfilePage from '../pages/profile/ProfilePage'

// Public pages
import HomePage from '../pages/public/HomePage'
import AboutPage from '../pages/public/AboutPage'
import ContactPage from '../pages/public/ContactPage'
import JobsPage from '../pages/public/JobsPage'
import CompaniesPage from '../pages/public/CompaniesPage'

// Error pages
import NotFoundPage from '../pages/error/NotFoundPage'
import UnauthorizedPage from '../pages/error/UnauthorizedPage'

// Route Guard Component
function ProtectedRoute({ 
  children, 
  requiredRoles 
}: { 
  children: React.ReactNode
  requiredRoles?: string[]
}) {
  const { isAuthenticated, user, loading } = useContext(AuthContext)

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2" style={{ borderColor: 'var(--brand-primary)' }}></div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  if (requiredRoles && user?.role && !requiredRoles.includes(user.role)) {
    return <Navigate to="/unauthorized" replace />
  }

  return <>{children}</>
}

// Public Route Guard (redirect authenticated users)
function PublicRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, loading } = useContext(AuthContext)

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2" style={{ borderColor: 'var(--brand-primary)' }}></div>
      </div>
    )
  }

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />
  }

  return <>{children}</>
}

// Dashboard Route Component
function DashboardRoute() {
  const { user } = useContext(AuthContext)

  switch (user?.role) {
    case 'candidate':
      return <CandidateDashboard />
    case 'recruiter':
      return <RecruiterDashboard />
    case 'employer':
      return <EmployerDashboard />
    case 'company_admin':
      return <CompanyAdminDashboard />
    case 'super_admin':
      return <SuperAdminDashboard />
    default:
      return <Navigate to="/unauthorized" replace />
  }
}

export const router = createBrowserRouter([
  // Public routes
  {
    path: '/',
    element: <PublicLayout />,
    children: [
      {
        index: true,
        element: <PublicRoute><HomePage /></PublicRoute>
      },
      {
        path: 'about',
        element: <AboutPage />
      },
      {
        path: 'contact',
        element: <ContactPage />
      },
      {
        path: 'jobs',
        element: <JobsPage />
      },
      {
        path: 'companies',
        element: <CompaniesPage />
      }
    ]
  },

  // Auth routes
  {
    path: '/login',
    element: <PublicRoute><LoginPage /></PublicRoute>
  },
  {
    path: '/2fa',
    element: <TwoFactorPage />
  },
  {
    path: '/register',
    element: <PublicRoute><RegisterPage /></PublicRoute>
  },
  {
    path: '/forgot-password',
    element: <PublicRoute><ForgotPasswordPage /></PublicRoute>
  },
  {
    path: '/reset-password',
    element: <PublicRoute><ResetPasswordPage /></PublicRoute>
  },

  // Protected app routes
  {
    path: '/dashboard',
    element: (
      <ProtectedRoute>
        <AppLayout />
      </ProtectedRoute>
    ),
    children: [
      {
        index: true,
        element: <DashboardRoute />
      }
    ]
  },

  // Feature routes
  {
    path: '/messages',
    element: (
      <ProtectedRoute requiredRoles={['candidate', 'recruiter', 'employer', 'company_admin']}>
        <AppLayout />
      </ProtectedRoute>
    ),
    children: [
      {
        index: true,
        element: <MessagesPage />
      }
    ]
  },
  {
    path: '/calendar',
    element: (
      <ProtectedRoute requiredRoles={['candidate', 'recruiter', 'employer', 'company_admin']}>
        <AppLayout />
      </ProtectedRoute>
    ),
    children: [
      {
        index: true,
        element: <CalendarPage />
      }
    ]
  },
  {
    path: '/interviews',
    element: (
      <ProtectedRoute requiredRoles={['candidate', 'recruiter', 'employer', 'company_admin']}>
        <AppLayout />
      </ProtectedRoute>
    ),
    children: [
      {
        index: true,
        element: <InterviewsPage />
      }
    ]
  },
  {
    path: '/resumes',
    element: (
      <ProtectedRoute requiredRoles={['candidate']}>
        <AppLayout />
      </ProtectedRoute>
    ),
    children: [
      {
        index: true,
        element: <ResumesPage />
      }
    ]
  },
  {
    path: '/settings',
    element: (
      <ProtectedRoute>
        <AppLayout />
      </ProtectedRoute>
    ),
    children: [
      {
        index: true,
        element: <SettingsPage />
      }
    ]
  },
  {
    path: '/profile',
    element: (
      <ProtectedRoute>
        <AppLayout />
      </ProtectedRoute>
    ),
    children: [
      {
        index: true,
        element: <ProfilePage />
      }
    ]
  },

  // Error routes
  {
    path: '/unauthorized',
    element: <UnauthorizedPage />
  },
  {
    path: '*',
    element: <NotFoundPage />
  }
])