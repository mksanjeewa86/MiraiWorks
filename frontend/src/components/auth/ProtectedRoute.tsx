'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { LoadingSpinner } from '@/components/ui';
import type { ProtectedRouteProps } from '@/types/components';
import { useLocale } from 'next-intl';
import { ROUTES } from '@/routes/config';

export default function ProtectedRoute({
  children,
  allowedRoles,
  fallback,
  redirectTo = ROUTES.AUTH.LOGIN,
}: ProtectedRouteProps) {
  const { isAuthenticated, isLoading, user } = useAuth();
  const router = useRouter();
  const locale = useLocale();

  useEffect(() => {
    // Add a small delay to ensure auth state is fully determined
    const timeoutId = setTimeout(() => {
      if (!isLoading && !isAuthenticated && typeof window !== 'undefined') {
        const currentPath = window.location.pathname;
        const localeRedirectTo = `/${locale}${redirectTo}`;
        // Only redirect if not already on the redirect page and not authenticated
        if (currentPath !== localeRedirectTo) {
          router.push(localeRedirectTo);
        }
      }
    }, 100); // Small delay to let auth state settle

    return () => clearTimeout(timeoutId);
  }, [isAuthenticated, isLoading, router, redirectTo, locale]);

  // Check role-based access if allowedRoles is specified
  const hasRequiredRole = () => {
    if (!allowedRoles || allowedRoles.length === 0) {
      return true; // No role restriction
    }

    if (!user || !user.roles) {
      return false;
    }

    // Check if user has any of the allowed roles
    return user.roles.some((userRole) => allowedRoles.includes(userRole.role.name));
  };

  // Show loading while auth is being determined
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  // Show fallback while redirecting or if not authenticated
  if (!isAuthenticated || !user) {
    return fallback ? (
      <>{fallback}</>
    ) : (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  // Check role-based access
  if (!hasRequiredRole()) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="text-6xl mb-4">🚫</div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Access Denied</h1>
          <p className="text-gray-600 mb-4">You don&apos;t have permission to access this page.</p>
          <button
            onClick={() => router.back()}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg"
          >
            Go Back
          </button>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}
