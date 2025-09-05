'use client';

import { useState } from 'react';
import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';
import Brand from '@/components/common/Brand';
import ForgotPasswordForm from '@/components/auth/ForgotPasswordForm';

export default function ForgotPasswordPage() {
  const [error, setError] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);

  const handleForgotPassword = async (email: string) => {
    setError('');
    setIsLoading(true);

    try {
      // Call forgot password API
      const response = await fetch('http://localhost:8001/api/auth/forgot-password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      });

      if (!response.ok) {
        throw new Error('Failed to send reset email');
      }

      // Success is handled by the form component
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send reset email');
      throw err; // Re-throw so form knows about the error
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 sm:px-6 lg:px-8 bg-gray-50 dark:bg-gray-950">
      <div className="max-w-md w-full">
        {/* Header */}
        <div className="text-center mb-8">
          <Brand className="justify-center" />
          <h2 className="mt-6 text-3xl font-bold" style={{ color: 'var(--text-primary)' }}>
            Forgot your password?
          </h2>
          <p className="mt-2 text-sm" style={{ color: 'var(--text-secondary)' }}>
            No worries, we'll send you reset instructions
          </p>
        </div>

        {/* Forgot Password Form */}
        <div className="card p-8">
          <ForgotPasswordForm
            onSubmit={handleForgotPassword}
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