'use client';

import { useState, useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';
import Brand from '@/components/common/Brand';
import ResetPasswordForm from '@/components/auth/ResetPasswordForm';

function ResetPasswordContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [error, setError] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);

  const token = searchParams.get('token');

  useEffect(() => {
    if (!token) {
      router.push('/auth/forgot-password');
    }
  }, [token, router]);

  const handleResetPassword = async (password: string) => {
    if (!token) {
      setError('Invalid reset token');
      return;
    }

    setError('');
    setIsLoading(true);

    try {
      // Call reset password API
      const response = await fetch('http://localhost:8001/api/auth/reset-password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ token, password }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Failed to reset password');
      }

      // Success is handled by the form component
      // After a short delay, redirect to login
      setTimeout(() => {
        router.push('/auth/login?message=password-reset-success');
      }, 2000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to reset password');
      throw err; // Re-throw so form knows about the error
    } finally {
      setIsLoading(false);
    }
  };

  if (!token) {
    return (
      <div className="min-h-screen flex items-center justify-center px-4 sm:px-6 lg:px-8 bg-gray-50 dark:bg-gray-950">
        <div className="max-w-md w-full">
          <div className="text-center">
            <Brand className="justify-center mb-8" />
            <div className="card p-8">
              <h2 className="text-2xl font-bold mb-4" style={{ color: 'var(--text-primary)' }}>
                Invalid Reset Link
              </h2>
              <p className="text-sm mb-6" style={{ color: 'var(--text-secondary)' }}>
                The password reset link is invalid or has expired. Please request a new one.
              </p>
              <Link
                href="/auth/forgot-password"
                className="btn btn-primary w-full"
              >
                Request New Reset Link
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
            Reset your password
          </h2>
          <p className="mt-2 text-sm" style={{ color: 'var(--text-secondary)' }}>
            Enter your new password below
          </p>
        </div>

        {/* Reset Password Form */}
        <div className="card p-8">
          <ResetPasswordForm
            onSubmit={handleResetPassword}
            isLoading={isLoading}
            error={error}
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

export default function ResetPasswordPage() {
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
      <ResetPasswordContent />
    </Suspense>
  );
}