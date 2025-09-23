'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Eye, EyeOff, Mail, Lock } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import Button from '@/components/ui/button';
import type { LoginFormProps } from '@/types/components';
import { loginSchema, type LoginFormData } from '@/types/forms';

export default function LoginForm({ onSuccess, onForgotPassword }: LoginFormProps) {
  const { login, error, clearError } = useAuth();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginFormData) => {
    if (isSubmitting) return;
    
    setIsSubmitting(true);
    clearError();
    
    try {
      await login(data);
      onSuccess?.();
    } catch {
      // Error is handled by the auth context
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      {error && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-2xl p-4">
          <div className="flex">
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800 dark:text-red-200">
                Sign in failed
              </h3>
              <div className="mt-2 text-sm text-red-700 dark:text-red-300">
                {error}
              </div>
            </div>
          </div>
        </div>
      )}

      <div>
        <label htmlFor="email" className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-2">
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
              ${errors.email 
                ? 'border-red-300 dark:border-red-700 bg-red-50 dark:bg-red-900/20' 
                : 'border-gray-200 dark:border-gray-700'
              }
            `}
            placeholder="Enter your email"
          />
        </div>
        {errors.email && (
          <p className="mt-2 text-sm text-red-600 dark:text-red-400">{errors.email.message}</p>
        )}
      </div>

      <div>
        <label htmlFor="password" className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-2">
          Password
        </label>
        <div className="relative">
          <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-500 h-5 w-5" />
          <input
            id="password"
            type={showPassword ? 'text' : 'password'}
            autoComplete="current-password"
            {...register('password')}
            className={`
              w-full pl-10 pr-12 py-3 bg-gray-50 dark:bg-gray-800 border rounded-2xl text-sm 
              focus:outline-none focus:ring-2 focus:ring-brand-primary focus:border-transparent 
              transition-colors placeholder-muted-400 dark:placeholder-muted-500
              ${errors.password 
                ? 'border-red-300 dark:border-red-700 bg-red-50 dark:bg-red-900/20' 
                : 'border-gray-200 dark:border-gray-700'
              }
            `}
            placeholder="Enter your password"
          />
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            className="absolute right-3 top-1/2 transform -translate-y-1/2 text-muted-500 hover:text-muted-600 transition-colors"
            aria-label={showPassword ? "Hide password" : "Show password"}
          >
            {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
          </button>
        </div>
        {errors.password && (
          <p className="mt-2 text-sm text-red-600 dark:text-red-400">{errors.password.message}</p>
        )}
      </div>

      <div className="flex items-center justify-end">
        <div className="text-sm">
          <button
            type="button"
            onClick={onForgotPassword}
            className="font-medium text-brand-primary hover:opacity-80 transition-colors"
          >
            Forgot your password?
          </button>
        </div>
      </div>

      <Button
        type="submit"
        loading={isSubmitting}
        className="w-full btn-primary py-3"
        disabled={isSubmitting}
      >
        Sign in
      </Button>
    </form>
  );
}