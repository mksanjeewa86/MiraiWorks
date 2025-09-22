'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Eye, EyeOff, Loader2, User, Mail, Lock, Phone } from 'lucide-react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useAuth } from '@/contexts/AuthContext';
import Brand from '@/components/common/Brand';

const registerSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string()
    .min(8, 'Password must be at least 8 characters')
    .regex(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/,
      'Password must contain at least one uppercase letter, one lowercase letter, one number, and one special character'),
  confirmPassword: z.string(),
  first_name: z.string().min(1, 'First name is required'),
  last_name: z.string().min(1, 'Last name is required'),
  phone: z.string().optional(),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"],
});

type RegisterFormData = z.infer<typeof registerSchema>;

export default function RegisterPage() {
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
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

  // Password strength calculation
  const getPasswordStrength = (password: string): string => {
    let score = 0;
    if (password.length >= 8) score++;
    if (/[A-Z]/.test(password) && /[a-z]/.test(password)) score++;
    if (/\d/.test(password)) score++;
    if (/[@$!%*?&]/.test(password)) score++;

    if (score <= 1) return 'weak';
    if (score <= 2) return 'medium';
    if (score <= 3) return 'strong';
    return 'very strong';
  };

  // Check if passwords match
  const getPasswordMatchStatus = (): 'none' | 'matching' | 'not-matching' => {
    if (!confirmPassword) return 'none';
    return password === confirmPassword ? 'matching' : 'not-matching';
  };

  const onSubmit = async (data: RegisterFormData) => {
    setLoading(true);
    clearError();
    setSuccessMessage('');

    try {
      // Remove confirmPassword from data before sending to API
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
      const { confirmPassword, ...formData } = data;
      const submitData = {
        ...formData,
        company_name: 'Default Company', // TODO: Add company fields to form
        company_domain: 'default.com'
      };
      await registerUser(submitData);

      // Show success message
      setSuccessMessage('Account created successfully! Redirecting...');

      // Redirect to jobs page after a short delay
      setTimeout(() => {
        router.push('/jobs');
      }, 2000);
    } catch {
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
            {/* Success Message */}
            {successMessage && (
              <div className="p-4 rounded-2xl bg-green-50 border border-green-200">
                <p className="text-sm text-green-600">{successMessage}</p>
              </div>
            )}

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
                  <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4 z-10" />
                  <input
                    id="first_name"
                    type="text"
                    {...register('first_name')}
                    className="input w-full"
                    style={{ paddingLeft: '3rem', paddingRight: '0.75rem' }}
                    placeholder="First name"
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
                  <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4 z-10" />
                  <input
                    id="last_name"
                    type="text"
                    {...register('last_name')}
                    className="input w-full"
                    style={{ paddingLeft: '3rem', paddingRight: '0.75rem' }}
                    placeholder="Last name"
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
                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4 z-10" />
                <input
                  id="email"
                  type="email"
                  {...register('email')}
                  className="input w-full"
                  style={{ paddingLeft: '3rem', paddingRight: '0.75rem' }}
                  placeholder="your.email@example.com"
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
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4 z-10" />
                <input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  {...register('password', {
                    onChange: (e) => setPassword(e.target.value)
                  })}
                  className="input w-full"
                  style={{ paddingLeft: '3rem', paddingRight: '3rem' }}
                  placeholder="Create a secure password"
                  autoComplete="new-password"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 p-1 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800 z-10"
                >
                  {showPassword ? (
                    <EyeOff className="h-4 w-4 text-gray-400" />
                  ) : (
                    <Eye className="h-4 w-4 text-gray-400" />
                  )}
                </button>
              </div>

              {/* Password Strength Indicator */}
              {password && (
                <div className="mt-2">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs font-medium text-gray-600">Password strength:</span>
                    <span className={`text-xs font-medium ${
                      getPasswordStrength(password) === 'weak' ? 'text-red-600' :
                      getPasswordStrength(password) === 'medium' ? 'text-yellow-600' :
                      getPasswordStrength(password) === 'strong' ? 'text-green-600' : 'text-gray-400'
                    }`}>
                      {getPasswordStrength(password)}
                    </span>
                  </div>
                  <div className="flex gap-1">
                    <div className={`h-1 w-full rounded ${
                      password.length >= 8 ? 'bg-green-500' : 'bg-gray-200'
                    }`}></div>
                    <div className={`h-1 w-full rounded ${
                      /[A-Z]/.test(password) && /[a-z]/.test(password) ? 'bg-green-500' : 'bg-gray-200'
                    }`}></div>
                    <div className={`h-1 w-full rounded ${
                      /\d/.test(password) ? 'bg-green-500' : 'bg-gray-200'
                    }`}></div>
                    <div className={`h-1 w-full rounded ${
                      /[@$!%*?&]/.test(password) ? 'bg-green-500' : 'bg-gray-200'
                    }`}></div>
                  </div>
                  <div className="mt-1 text-xs text-gray-500">
                    <ul className="space-y-1">
                      <li className={password.length >= 8 ? 'text-green-600' : 'text-gray-500'}>
                        ✓ At least 8 characters
                      </li>
                      <li className={/[A-Z]/.test(password) && /[a-z]/.test(password) ? 'text-green-600' : 'text-gray-500'}>
                        ✓ Upper and lowercase letters
                      </li>
                      <li className={/\d/.test(password) ? 'text-green-600' : 'text-gray-500'}>
                        ✓ At least one number
                      </li>
                      <li className={/[@$!%*?&]/.test(password) ? 'text-green-600' : 'text-gray-500'}>
                        ✓ At least one special character (@$!%*?&)
                      </li>
                    </ul>
                  </div>
                </div>
              )}

              {errors.password && (
                <p className="mt-1 text-sm text-red-600">{errors.password.message}</p>
              )}
            </div>

            {/* Confirm Password */}
            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium mb-2" style={{ color: 'var(--text-primary)' }}>
                Confirm Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4 z-10" />
                <input
                  id="confirmPassword"
                  type={showConfirmPassword ? 'text' : 'password'}
                  {...register('confirmPassword', {
                    onChange: (e) => setConfirmPassword(e.target.value)
                  })}
                  className="input w-full"
                  style={{ paddingLeft: '3rem', paddingRight: '3rem' }}
                  placeholder="Confirm your password"
                  autoComplete="new-password"
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 p-1 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800 z-10"
                >
                  {showConfirmPassword ? (
                    <EyeOff className="h-4 w-4 text-gray-400" />
                  ) : (
                    <Eye className="h-4 w-4 text-gray-400" />
                  )}
                </button>
              </div>

              {/* Password Match Indicator */}
              {confirmPassword && (
                <div className="mt-2">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs font-medium text-gray-600">Password match:</span>
                    <span className={`text-xs font-medium ${
                      getPasswordMatchStatus() === 'matching' ? 'text-green-600' :
                      getPasswordMatchStatus() === 'not-matching' ? 'text-red-600' : 'text-gray-400'
                    }`}>
                      {getPasswordMatchStatus() === 'matching' && '✓ Passwords match'}
                      {getPasswordMatchStatus() === 'not-matching' && '✗ Passwords do not match'}
                    </span>
                  </div>
                  <div className="flex gap-1">
                    <div className={`h-1 w-full rounded ${
                      getPasswordMatchStatus() === 'matching' ? 'bg-green-500' :
                      getPasswordMatchStatus() === 'not-matching' ? 'bg-red-500' : 'bg-gray-200'
                    }`}></div>
                  </div>
                </div>
              )}

              {errors.confirmPassword && (
                <p className="mt-1 text-sm text-red-600">{errors.confirmPassword.message}</p>
              )}
            </div>

            {/* Phone (Optional) */}
            <div>
              <label htmlFor="phone" className="block text-sm font-medium mb-2" style={{ color: 'var(--text-primary)' }}>
                Phone Number (Optional)
              </label>
              <div className="relative">
                <Phone className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4 z-10" />
                <input
                  id="phone"
                  type="tel"
                  {...register('phone')}
                  className="input w-full"
                  style={{ paddingLeft: '3rem', paddingRight: '0.75rem' }}
                  placeholder="+81 (90) 1234-5678"
                  autoComplete="tel"
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