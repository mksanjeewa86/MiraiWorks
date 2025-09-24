'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Eye, EyeOff, Lock, CheckCircle } from 'lucide-react';
import Button from '@/components/ui/button';
import type { ResetPasswordFormProps } from '@/types/components';
import { resetPasswordSchema, type ResetPasswordFormData } from '@/types/forms';

export default function ResetPasswordForm({
  onSubmit,
  isLoading = false,
  error,
}: ResetPasswordFormProps) {
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ResetPasswordFormData>({
    resolver: zodResolver(resetPasswordSchema),
  });

  const handleFormSubmit = async (data: ResetPasswordFormData) => {
    setIsSubmitting(true);
    try {
      await onSubmit(data.password);
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
          Password Reset Successful
        </h3>
        <p className="text-sm text-muted-600 dark:text-muted-300 mb-6">
          Your password has been successfully reset. You can now sign in with your new password.
        </p>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-6">
      <div className="text-center">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
          Create new password
        </h3>
        <p className="text-sm text-muted-600 dark:text-muted-300">
          Your new password must be different from your previous password
        </p>
      </div>

      {error && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-2xl p-4">
          <p className="text-sm text-red-700 dark:text-red-300 text-center">{error}</p>
        </div>
      )}

      <div>
        <label
          htmlFor="password"
          className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-2"
        >
          New Password
        </label>
        <div className="relative">
          <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-500 h-5 w-5" />
          <input
            id="password"
            type={showPassword ? 'text' : 'password'}
            autoComplete="new-password"
            {...register('password')}
            className={`
              w-full pl-10 pr-12 py-3 bg-gray-50 dark:bg-gray-800 border rounded-2xl text-sm 
              focus:outline-none focus:ring-2 focus:ring-brand-primary focus:border-transparent 
              transition-colors placeholder-muted-400 dark:placeholder-muted-500
              ${
                errors.password
                  ? 'border-red-300 dark:border-red-700 bg-red-50 dark:bg-red-900/20'
                  : 'border-gray-200 dark:border-gray-700'
              }
            `}
            placeholder="Enter your new password"
          />
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            className="absolute right-3 top-1/2 transform -translate-y-1/2 text-muted-500 hover:text-muted-600 transition-colors"
            aria-label={showPassword ? 'Hide password' : 'Show password'}
          >
            {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
          </button>
        </div>
        {errors.password && (
          <p className="mt-2 text-sm text-red-600 dark:text-red-400">{errors.password.message}</p>
        )}
      </div>

      <div>
        <label
          htmlFor="confirmPassword"
          className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-2"
        >
          Confirm Password
        </label>
        <div className="relative">
          <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-500 h-5 w-5" />
          <input
            id="confirmPassword"
            type={showConfirmPassword ? 'text' : 'password'}
            autoComplete="new-password"
            {...register('confirmPassword')}
            className={`
              w-full pl-10 pr-12 py-3 bg-gray-50 dark:bg-gray-800 border rounded-2xl text-sm 
              focus:outline-none focus:ring-2 focus:ring-brand-primary focus:border-transparent 
              transition-colors placeholder-muted-400 dark:placeholder-muted-500
              ${
                errors.confirmPassword
                  ? 'border-red-300 dark:border-red-700 bg-red-50 dark:bg-red-900/20'
                  : 'border-gray-200 dark:border-gray-700'
              }
            `}
            placeholder="Confirm your new password"
          />
          <button
            type="button"
            onClick={() => setShowConfirmPassword(!showConfirmPassword)}
            className="absolute right-3 top-1/2 transform -translate-y-1/2 text-muted-500 hover:text-muted-600 transition-colors"
            aria-label={showConfirmPassword ? 'Hide password' : 'Show password'}
          >
            {showConfirmPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
          </button>
        </div>
        {errors.confirmPassword && (
          <p className="mt-2 text-sm text-red-600 dark:text-red-400">
            {errors.confirmPassword.message}
          </p>
        )}
      </div>

      <Button
        type="submit"
        loading={isSubmitting || isLoading}
        disabled={isSubmitting || isLoading}
        className="w-full btn-primary py-3"
      >
        Reset Password
      </Button>
    </form>
  );
}
