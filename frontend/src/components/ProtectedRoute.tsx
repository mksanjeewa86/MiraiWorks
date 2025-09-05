import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import LoadingSpinner from './ui/LoadingSpinner';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRoles?: string[];
  redirectTo?: string;
}

export default function ProtectedRoute({ 
  children, 
  requiredRoles, 
  redirectTo = '/login' 
}: ProtectedRouteProps) {
  const { isAuthenticated, isLoading, user } = useAuth();
  const location = useLocation();

  // Show loading spinner while checking authentication
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  // Redirect to login if not authenticated
  if (!isAuthenticated || !user) {
    return <Navigate to={redirectTo} state={{ from: location }} replace />;
  }

  // Check role-based access
  if (requiredRoles && requiredRoles.length > 0) {
    const userRoles = user.roles?.map(role => role.role.name) || [];
    const hasRequiredRole = requiredRoles.some(role => userRoles.includes(role));
    
    if (!hasRequiredRole) {
      return <Navigate to="/unauthorized" replace />;
    }
  }

  return <>{children}</>;
}

// Hook for checking permissions
export function usePermissions() {
  const { user } = useAuth();

  const hasRole = (roleName: string): boolean => {
    if (!user?.roles) return false;
    return user.roles.some(role => role.role.name === roleName);
  };

  const hasPermission = (resource: string, action: string): boolean => {
    if (!user?.roles) return false;
    
    return user.roles.some(role => 
      role.role.permissions?.some(permission => 
        permission.resource === resource && permission.action === action
      )
    );
  };

  const isSuperAdmin = (): boolean => hasRole('super_admin');
  const isCompanyAdmin = (): boolean => hasRole('company_admin');
  const isRecruiter = (): boolean => hasRole('recruiter');
  const isEmployer = (): boolean => hasRole('employer');
  const isCandidate = (): boolean => hasRole('candidate');

  return {
    hasRole,
    hasPermission,
    isSuperAdmin,
    isCompanyAdmin,
    isRecruiter,
    isEmployer,
    isCandidate,
    userRoles: user?.roles?.map(role => role.role.name) || [],
  };
}