'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Mail, CheckCircle } from 'lucide-react';
import { Button } from '@/components/ui';
import type { ForgotPasswordFormProps } from '@/types/components';
import { forgotPasswordSchema, type ForgotPasswordFormData } from '@/types/forms';

export default function ForgotPasswordForm({
  onSubmit,
  isLoading = false,
  error,
}: ForgotPasswordFormProps) {
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
    getValues,
  } = useForm<ForgotPasswordFormData>({
    resolver: zodResolver(forgotPasswordSchema),
  });

  const handleFormSubmit = async (data: ForgotPasswordFormData) => {
    setIsSubmitting(true);
    try {
      await onSubmit(data.email);
      setIsSubmitted(true);
    } catch {
      // Error handled by parent
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isSubmitted) {
    return (
      <div className="text-center space-y-6">
        <div
          className="w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-4"
          style={{ backgroundColor: 'rgba(34, 197, 94, 0.1)' }}
        >
          <CheckCircle className="h-8 w-8 text-green-500" />
        </div>
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
          Check your email
        </h3>
        <p className="text-sm text-muted-600 dark:text-muted-300 mb-4">
          We&apos;ve sent a password reset link to:
        </p>
        <p className="text-sm font-medium text-gray-900 dark:text-white mb-6">
          {getValues('email')}
        </p>
        <p className="text-xs text-muted-500 dark:text-muted-400">
          Didn&apos;t receive the email? Check your spam folder or try again.
        </p>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-6">
      <div className="text-center">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
          Reset your password
        </h3>
        <p className="text-sm text-muted-600 dark:text-muted-300">
          Enter your email address and we&apos;ll send you a link to reset your password
        </p>
      </div>

      {error && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-2xl p-4">
          <p className="text-sm text-red-700 dark:text-red-300 text-center">{error}</p>
        </div>
      )}

      <div>
        <label
          htmlFor="email"
          className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-2"
        >
          Email address
        </label>
        <div className="relative">
          <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-500 h-5 w-5" />
          <input
            id="email"
            type="email"
            autoComplete="email"
            {...register('email')}
            className={`
              w-full pl-10 pr-4 py-3 bg-gray-50 dark:bg-gray-800 border rounded-2xl text-sm 
              focus:outline-none focus:ring-2 focus:ring-brand-primary focus:border-transparent 
              transition-colors placeholder-muted-400 dark:placeholder-muted-500
              ${
                errors.email
                  ? 'border-red-300 dark:border-red-700 bg-red-50 dark:bg-red-900/20'
                  : 'border-gray-200 dark:border-gray-700'
              }
            `}
            placeholder="Enter your email address"
          />
        </div>
        {errors.email && (
          <p className="mt-2 text-sm text-red-600 dark:text-red-400">{errors.email.message}</p>
        )}
      </div>

      <Button
        type="submit"
        loading={isSubmitting || isLoading}
        disabled={isSubmitting || isLoading}
        className="w-full btn-primary py-3"
      >
        Send Reset Link
      </Button>
    </form>
  );
}
