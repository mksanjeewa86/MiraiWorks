'use client';

import { useState, useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import TwoFactorForm from '@/components/auth/TwoFactorForm';
import Brand from '@/components/common/Brand';

function TwoFactorContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { isAuthenticated, verifyTwoFactor, error, clearError } = useAuth();
  const [twoFactorError, setTwoFactorError] = useState<string>('');

  const email = searchParams.get('email');

  useEffect(() => {
    if (isAuthenticated) {
      router.push('/dashboard');
    }
  }, [isAuthenticated, router]);

  const handleTwoFactorSubmit = async (code: string) => {
    clearError();
    setTwoFactorError('');

    try {
      await verifyTwoFactor(code);
      router.push('/dashboard');
    } catch (err) {
      setTwoFactorError(err instanceof Error ? err.message : 'Invalid verification code');
    }
  };

  const handleResend = async () => {
    // Implementation would depend on your auth system
    // For now, just show a success message
    console.log('Resend code for:', email);
  };

  if (!email) {
    return (
      <div className="min-h-screen flex items-center justify-center px-4 sm:px-6 lg:px-8 bg-gray-50 dark:bg-gray-950">
        <div className="max-w-md w-full">
          <div className="text-center">
            <Brand className="justify-center mb-8" />
            <div className="card p-8">
              <h2 className="text-2xl font-bold mb-4" style={{ color: 'var(--text-primary)' }}>
                Session Expired
              </h2>
              <p className="text-sm mb-6" style={{ color: 'var(--text-secondary)' }}>
                Your session has expired. Please log in again.
              </p>
              <Link
                href="/auth/login"
                className="btn btn-primary w-full"
              >
                Back to Login
              </Link>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4 sm:px-6 lg:px-8 bg-gray-50 dark:bg-gray-950">
      <div className="max-w-md w-full">
        {/* Header */}
        <div className="text-center mb-8">
          <Brand className="justify-center" />
          <h2 className="mt-6 text-3xl font-bold" style={{ color: 'var(--text-primary)' }}>
            Two-Factor Authentication
          </h2>
          <p className="mt-2 text-sm" style={{ color: 'var(--text-secondary)' }}>
            We sent a verification code to your authenticator app
          </p>
          <p className="mt-1 text-xs" style={{ color: 'var(--text-muted)' }}>
            {email}
          </p>
        </div>

        {/* Two-Factor Form */}
        <div className="card p-8">
          <TwoFactorForm
            onSubmit={handleTwoFactorSubmit}
            onResend={handleResend}
            error={twoFactorError || error || undefined}
          />

          {/* Back to Login */}
          <div className="mt-6 text-center">
            <Link
              href="/auth/login"
              className="inline-flex items-center text-sm font-medium text-brand-primary hover:opacity-80 transition-colors"
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Login
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function TwoFactorPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center px-4 sm:px-6 lg:px-8 bg-gray-50 dark:bg-gray-950">
        <div className="max-w-md w-full">
          <div className="text-center">
            <Brand className="justify-center mb-8" />
            <div className="card p-8">
              <div className="animate-pulse">
                <div className="h-4 bg-gray-200 rounded w-3/4 mx-auto"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    }>
      <TwoFactorContent />
    </Suspense>
  );
}