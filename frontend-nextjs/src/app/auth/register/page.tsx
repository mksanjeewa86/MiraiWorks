'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Eye, EyeOff, Loader2, User, Building, Mail, Lock, Phone } from 'lucide-react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useAuth } from '@/contexts/AuthContext';
import Brand from '@/components/common/Brand';

const registerSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(6, 'Password must be at least 6 characters'),
  first_name: z.string().min(1, 'First name is required'),
  last_name: z.string().min(1, 'Last name is required'),
  phone: z.string().optional(),
  company_name: z.string().min(1, 'Company name is required'),
  company_domain: z.string().min(1, 'Company domain is required'),
  industry: z.string().optional(),
});

type RegisterFormData = z.infer<typeof registerSchema>;

export default function RegisterPage() {
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const { register: registerUser, isAuthenticated, error, clearError } = useAuth();
  const router = useRouter();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
  });

  useEffect(() => {
    if (isAuthenticated) {
      router.push('/dashboard');
    }
  }, [isAuthenticated, router]);

  const onSubmit = async (data: RegisterFormData) => {
    setLoading(true);
    clearError();
    
    try {
      await registerUser(data);
      router.push('/dashboard');
    } catch (err) {
      // Error is handled by AuthContext
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 sm:px-6 lg:px-8 bg-gray-50 dark:bg-gray-950">
      <div className="max-w-md w-full">
        {/* Header */}
        <div className="text-center mb-8">
          <Brand className="justify-center" />
          <h2 className="mt-6 text-3xl font-bold" style={{ color: 'var(--text-primary)' }}>
            Create your account
          </h2>
          <p className="mt-2 text-sm" style={{ color: 'var(--text-secondary)' }}>
            Join MiraiWorks and start your career journey
          </p>
        </div>

        {/* Register Form */}
        <div className="card p-8">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            {/* Error Message */}
            {error && (
              <div className="p-4 rounded-2xl bg-red-50 border border-red-200">
                <p className="text-sm text-red-600">{error}</p>
              </div>
            )}

            {/* Personal Information */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label htmlFor="first_name" className="block text-sm font-medium mb-2" style={{ color: 'var(--text-primary)' }}>
                  First Name
                </label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-500 h-4 w-4" />
                  <input
                    id="first_name"
                    type="text"
                    {...register('first_name')}
                    className="input w-full pl-9"
                    placeholder="John"
                  />
                </div>
                {errors.first_name && (
                  <p className="mt-1 text-sm text-red-600">{errors.first_name.message}</p>
                )}
              </div>

              <div>
                <label htmlFor="last_name" className="block text-sm font-medium mb-2" style={{ color: 'var(--text-primary)' }}>
                  Last Name
                </label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-500 h-4 w-4" />
                  <input
                    id="last_name"
                    type="text"
                    {...register('last_name')}
                    className="input w-full pl-9"
                    placeholder="Doe"
                  />
                </div>
                {errors.last_name && (
                  <p className="mt-1 text-sm text-red-600">{errors.last_name.message}</p>
                )}
              </div>
            </div>

            {/* Email */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium mb-2" style={{ color: 'var(--text-primary)' }}>
                Email
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-500 h-4 w-4" />
                <input
                  id="email"
                  type="email"
                  {...register('email')}
                  className="input w-full pl-9"
                  placeholder="john@company.com"
                  autoComplete="email"
                />
              </div>
              {errors.email && (
                <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>
              )}
            </div>

            {/* Password */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium mb-2" style={{ color: 'var(--text-primary)' }}>
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-500 h-4 w-4" />
                <input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  {...register('password')}
                  className="input w-full pl-9 pr-12"
                  placeholder="Create a secure password"
                  autoComplete="new-password"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 p-1 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800"
                >
                  {showPassword ? (
                    <EyeOff className="h-4 w-4" style={{ color: 'var(--text-muted)' }} />
                  ) : (
                    <Eye className="h-4 w-4" style={{ color: 'var(--text-muted)' }} />
                  )}
                </button>
              </div>
              {errors.password && (
                <p className="mt-1 text-sm text-red-600">{errors.password.message}</p>
              )}
            </div>

            {/* Phone (Optional) */}
            <div>
              <label htmlFor="phone" className="block text-sm font-medium mb-2" style={{ color: 'var(--text-primary)' }}>
                Phone Number (Optional)
              </label>
              <div className="relative">
                <Phone className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-500 h-4 w-4" />
                <input
                  id="phone"
                  type="tel"
                  {...register('phone')}
                  className="input w-full pl-9"
                  placeholder="+1 (555) 123-4567"
                  autoComplete="tel"
                />
              </div>
            </div>

            {/* Company Information */}
            <div className="border-t pt-6">
              <h3 className="text-lg font-medium mb-4" style={{ color: 'var(--text-primary)' }}>
                Company Information
              </h3>
              
              <div>
                <label htmlFor="company_name" className="block text-sm font-medium mb-2" style={{ color: 'var(--text-primary)' }}>
                  Company Name
                </label>
                <div className="relative">
                  <Building className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-500 h-4 w-4" />
                  <input
                    id="company_name"
                    type="text"
                    {...register('company_name')}
                    className="input w-full pl-9"
                    placeholder="Acme Corporation"
                  />
                </div>
                {errors.company_name && (
                  <p className="mt-1 text-sm text-red-600">{errors.company_name.message}</p>
                )}
              </div>

              <div className="mt-4">
                <label htmlFor="company_domain" className="block text-sm font-medium mb-2" style={{ color: 'var(--text-primary)' }}>
                  Company Domain
                </label>
                <input
                  id="company_domain"
                  type="text"
                  {...register('company_domain')}
                  className="input w-full"
                  placeholder="acme.com"
                />
                {errors.company_domain && (
                  <p className="mt-1 text-sm text-red-600">{errors.company_domain.message}</p>
                )}
              </div>

              <div className="mt-4">
                <label htmlFor="industry" className="block text-sm font-medium mb-2" style={{ color: 'var(--text-primary)' }}>
                  Industry (Optional)
                </label>
                <input
                  id="industry"
                  type="text"
                  {...register('industry')}
                  className="input w-full"
                  placeholder="Technology"
                />
              </div>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="btn btn-primary w-full"
            >
              {loading ? (
                <>
                  <Loader2 className="animate-spin h-4 w-4 mr-2" />
                  Creating account...
                </>
              ) : (
                'Create Account'
              )}
            </button>
          </form>

          {/* Sign In Link */}
          <div className="mt-6 text-center">
            <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
              Already have an account?{' '}
              <Link
                href="/auth/login"
                className="font-medium text-brand-primary hover:text-brand-primary-dark"
              >
                Sign in
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}