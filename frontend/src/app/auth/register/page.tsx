'use client';

import { useState, useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { Loader2, User, Mail, Phone, Briefcase, CheckCircle } from 'lucide-react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useAuth } from '@/contexts/AuthContext';

const registerSchema = z.object({
  email: z.string().email('Invalid email address'),
  first_name: z.string().min(1, 'First name is required'),
  last_name: z.string().min(1, 'Last name is required'),
  phone: z.string().optional(),
  role: z.enum(['candidate', 'employer', 'recruiter']),
});

type RegisterFormData = z.infer<typeof registerSchema>;

function RegisterContent() {
  const [loading, setLoading] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');
  const [showSuccessScreen, setShowSuccessScreen] = useState(false);
  const { register: registerUser, isAuthenticated, error, clearError } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();
  const roleParam = searchParams.get('role') as 'candidate' | 'employer' | 'recruiter' | null;

  const {
    register,
    handleSubmit,
    formState: { errors },
    setValue,
    watch,
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      role: (roleParam as 'candidate' | 'employer' | 'recruiter') || 'candidate',
    },
  });

  const watchedEmail = watch('email');

  useEffect(() => {
    if (roleParam) {
      setValue('role', roleParam);
    }
  }, [roleParam, setValue]);

  useEffect(() => {
    if (isAuthenticated) {
      router.push('/dashboard');
    }
  }, [isAuthenticated, router]);

  const getRoleInfo = (role: string | null) => {
    switch (role) {
      case 'employer':
        return {
          title: 'Start Your Free Trial',
          subtitle: 'Find and hire top talent for your company',
          color: 'from-purple-500 to-pink-500',
          buttonText: 'Start Free Trial',
        };
      case 'recruiter':
        return {
          title: 'Start Your Free Trial',
          subtitle: 'Connect candidates with opportunities',
          color: 'from-blue-500 to-cyan-500',
          buttonText: 'Start Free Trial',
        };
      case 'candidate':
        return {
          title: 'Create Your Account',
          subtitle: 'Find your dream job and advance your career',
          color: 'from-green-500 to-teal-500',
          buttonText: 'Create Account',
        };
      default:
        return {
          title: 'Create your account',
          subtitle: 'Join MiraiWorks and start your career journey',
          color: 'from-purple-500 to-pink-500',
          buttonText: 'Create Account',
        };
    }
  };

  const roleInfo = getRoleInfo(roleParam);

  const onSubmit = async (data: RegisterFormData) => {
    setLoading(true);
    clearError();
    setSuccessMessage('');

    try {
      const submitData = {
        ...data,
        company_name: 'Default Company',
        company_domain: 'default.com',
      };
      await registerUser(submitData);

      setSuccessMessage('Account created successfully! Check your email for activation instructions.');
      setShowSuccessScreen(true);
    } catch {
      // Error is handled by AuthContext
    } finally {
      setLoading(false);
    }
  };

  if (showSuccessScreen) {
    return (
      <div className="min-h-screen flex items-center justify-center px-4 sm:px-6 lg:px-8 bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 relative overflow-hidden">
        {/* Background Pattern */}
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiM5Q0EzQUYiIGZpbGwtb3BhY2l0eT0iMC4xIj48cGF0aCBkPSJtMzYgMzQgMjItMjIgNCAyMiA0LTIgMC0yIDItNCAwLTJ6bTAtMjIgMjAgMjAtMTIgMTItMTIgMCAwLTggMTItMTJ6bTI0IDI0IDEyLTEyIDAtOCAwLTEwLTQgMCAwIDRoLTh2OGgtNGwtNCAwIDQgNGgxMnptMC0xNiA4LTggMCAwIDAgOGgtOHoiLz48L2c+PC9nPjwvc3ZnPg==')] opacity-20"></div>

        {/* Floating Elements */}
        <div className="absolute top-20 left-10 w-72 h-72 bg-green-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob"></div>
        <div className="absolute top-40 right-10 w-72 h-72 bg-purple-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-2000"></div>

        <div className="relative max-w-xl w-full">
          <div className="bg-white/10 backdrop-blur-lg rounded-3xl p-8 border-2 border-white/20 shadow-2xl">
            <div className="text-center">
              <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-green-500 mb-6">
                <CheckCircle className="h-10 w-10 text-white" />
              </div>

              <h2 className="text-3xl font-bold text-white mb-4">
                Check Your Email!
              </h2>

              <p className="text-gray-300 mb-6 text-lg">
                We've sent an email to:
              </p>

              <div className="bg-white/10 border border-white/20 rounded-xl p-4 mb-6">
                <p className="text-white font-semibold text-lg">{watchedEmail}</p>
              </div>

              <div className="bg-blue-500/20 border border-blue-400/50 rounded-xl p-6 mb-8 text-left">
                <h3 className="text-white font-semibold mb-3 flex items-center">
                  <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                  </svg>
                  Next Steps:
                </h3>
                <ol className="text-gray-200 space-y-2 text-sm">
                  <li className="flex items-start">
                    <span className="text-blue-300 font-bold mr-2">1.</span>
                    <span>Check your email inbox (and spam folder)</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-blue-300 font-bold mr-2">2.</span>
                    <span>Find your temporary password in the email</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-blue-300 font-bold mr-2">3.</span>
                    <span>Click the login button or visit the login page</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-blue-300 font-bold mr-2">4.</span>
                    <span>Enter your email and temporary password</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-blue-300 font-bold mr-2">5.</span>
                    <span>Set a new secure password to activate your account</span>
                  </li>
                </ol>
              </div>

              <div className="bg-amber-500/20 border border-amber-400/50 rounded-xl p-4 mb-8">
                <p className="text-amber-200 text-sm">
                  <strong>⚠️ Important:</strong> Your temporary password will expire in 24 hours.
                  Please activate your account as soon as possible.
                </p>
              </div>

              <div className="space-y-4">
                <Link
                  href="/auth/login"
                  className={`block w-full py-3 px-4 bg-gradient-to-r ${roleInfo.color} hover:opacity-90 text-white font-semibold rounded-xl shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-300`}
                >
                  Go to Login Page
                </Link>

                <button
                  onClick={() => setShowSuccessScreen(false)}
                  className="block w-full py-3 px-4 bg-white/10 hover:bg-white/20 text-white font-semibold rounded-xl border border-white/20 transition-all duration-300"
                >
                  Back to Registration
                </button>
              </div>
            </div>
          </div>

          {/* Back to Home */}
          <div className="mt-6 text-center">
            <Link
              href="/"
              className="inline-flex items-center text-sm text-gray-300 hover:text-white transition-colors duration-300"
            >
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
              Back to Home
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4 sm:px-6 lg:px-8 bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 relative overflow-hidden">
      {/* Background Pattern */}
      <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiM5Q0EzQUYiIGZpbGwtb3BhY2l0eT0iMC4xIj48cGF0aCBkPSJtMzYgMzQgMjItMjIgNCAyMiA0LTIgMC0yIDItNCAwLTJ6bTAtMjIgMjAgMjAtMTIgMTItMTIgMCAwLTggMTItMTJ6bTI0IDI0IDEyLTEyIDAtOCAwLTEwLTQgMCAwIDRoLTh2OGgtNGwtNCAwIDQgNGgxMnptMC0xNiA4LTggMCAwIDAgOGgtOHoiLz48L2c+PC9nPjwvc3ZnPg==')] opacity-20"></div>

      {/* Floating Elements */}
      <div className="absolute top-20 left-10 w-72 h-72 bg-purple-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob"></div>
      <div className="absolute top-40 right-10 w-72 h-72 bg-yellow-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-2000"></div>
      <div className="absolute -bottom-8 left-20 w-72 h-72 bg-pink-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-4000"></div>

      <div className="relative max-w-xl w-full">
        {/* Header */}
        <div className="text-center mb-8 animate-fade-in-up">
          <Link href="/" className="inline-block mb-6">
            <h1 className="text-4xl font-extrabold text-white">
              MiraiWorks
            </h1>
          </Link>
          <h2 className="text-3xl font-bold text-white mb-2">
            {roleInfo.title}
          </h2>
          <p className="text-gray-300">
            {roleInfo.subtitle}
          </p>
        </div>

        {/* Register Form */}
        <div className="bg-white/10 backdrop-blur-lg rounded-3xl p-8 border-2 border-white/20 shadow-2xl">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
            {/* Error Message */}
            {error && (
              <div className="p-4 rounded-2xl bg-red-500/20 border border-red-400/50 backdrop-blur-sm">
                <p className="text-sm text-red-100 font-medium">{error}</p>
              </div>
            )}

            {/* Info Message */}
            <div className="p-4 rounded-2xl bg-blue-500/20 border border-blue-400/50 backdrop-blur-sm">
              <p className="text-sm text-blue-100">
                <strong>📧 Note:</strong> We'll send you a temporary password via email. You'll set your own password on first login.
              </p>
            </div>

            {/* Role Selection - Only show if not set via URL */}
            {!roleParam && (
              <div>
                <label htmlFor="role" className="block text-sm font-medium mb-2 text-gray-200">
                  I am a
                </label>
                <div className="relative">
                  <Briefcase className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5 z-10" />
                  <select
                    id="role"
                    {...register('role')}
                    className="w-full pl-11 pr-4 py-3 bg-white/10 border border-white/20 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-400 focus:border-transparent transition-all duration-300 appearance-none cursor-pointer"
                  >
                    <option value="" className="bg-slate-800">Select your role</option>
                    <option value="candidate" className="bg-slate-800">Candidate - Looking for jobs</option>
                    <option value="employer" className="bg-slate-800">Employer - Hiring talent</option>
                    <option value="recruiter" className="bg-slate-800">Recruiter - Connecting talent</option>
                  </select>
                  <div className="absolute right-3 top-1/2 transform -translate-y-1/2 pointer-events-none">
                    <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
                    </svg>
                  </div>
                </div>
                {errors.role && (
                  <p className="mt-1 text-sm text-red-300">{errors.role.message}</p>
                )}
              </div>
            )}

            {/* Personal Information */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label htmlFor="first_name" className="block text-sm font-medium mb-2 text-gray-200">
                  First Name
                </label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5 z-10" />
                  <input
                    id="first_name"
                    type="text"
                    {...register('first_name')}
                    className="w-full pl-11 pr-4 py-3 bg-white/10 border border-white/20 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-400 focus:border-transparent transition-all duration-300"
                    placeholder="First name"
                  />
                </div>
                {errors.first_name && (
                  <p className="mt-1 text-sm text-red-300">{errors.first_name.message}</p>
                )}
              </div>

              <div>
                <label htmlFor="last_name" className="block text-sm font-medium mb-2 text-gray-200">
                  Last Name
                </label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5 z-10" />
                  <input
                    id="last_name"
                    type="text"
                    {...register('last_name')}
                    className="w-full pl-11 pr-4 py-3 bg-white/10 border border-white/20 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-400 focus:border-transparent transition-all duration-300"
                    placeholder="Last name"
                  />
                </div>
                {errors.last_name && (
                  <p className="mt-1 text-sm text-red-300">{errors.last_name.message}</p>
                )}
              </div>
            </div>

            {/* Email */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium mb-2 text-gray-200">
                Email
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5 z-10" />
                <input
                  id="email"
                  type="email"
                  {...register('email')}
                  className="w-full pl-11 pr-4 py-3 bg-white/10 border border-white/20 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-400 focus:border-transparent transition-all duration-300"
                  placeholder="your.email@example.com"
                  autoComplete="email"
                />
              </div>
              {errors.email && <p className="mt-1 text-sm text-red-300">{errors.email.message}</p>}
            </div>

            {/* Phone (Optional) */}
            <div>
              <label htmlFor="phone" className="block text-sm font-medium mb-2 text-gray-200">
                Phone Number <span className="text-gray-400 text-xs">(Optional)</span>
              </label>
              <div className="relative">
                <Phone className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5 z-10" />
                <input
                  id="phone"
                  type="tel"
                  {...register('phone')}
                  className="w-full pl-11 pr-4 py-3 bg-white/10 border border-white/20 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-400 focus:border-transparent transition-all duration-300"
                  placeholder="+81 (90) 1234-5678"
                  autoComplete="tel"
                />
              </div>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className={`w-full py-3 px-4 bg-gradient-to-r ${roleInfo.color} hover:opacity-90 text-white font-semibold rounded-xl shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none flex items-center justify-center`}
            >
              {loading ? (
                <>
                  <Loader2 className="animate-spin h-5 w-5 mr-2" />
                  {roleParam === 'employer' || roleParam === 'recruiter' ? 'Starting trial...' : 'Creating account...'}
                </>
              ) : (
                roleInfo.buttonText
              )}
            </button>
          </form>

          {/* Sign In Link */}
          <div className="mt-6 text-center">
            <p className="text-sm text-gray-300">
              Already have an account?{' '}
              <Link
                href="/auth/login"
                className="font-semibold text-purple-300 hover:text-purple-200 transition-colors duration-300"
              >
                Sign in
              </Link>
            </p>
          </div>
        </div>

        {/* Back to Home */}
        <div className="mt-6 text-center">
          <Link
            href="/"
            className="inline-flex items-center text-sm text-gray-300 hover:text-white transition-colors duration-300"
          >
            <svg
              className="w-4 h-4 mr-2"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M10 19l-7-7m0 0l7-7m-7 7h18"
              />
            </svg>
            Back to Home
          </Link>
        </div>
      </div>
    </div>
  );
}

export default function RegisterPage() {
  return (
    <Suspense fallback={<div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900"><Loader2 className="h-8 w-8 animate-spin text-white" /></div>}>
      <RegisterContent />
    </Suspense>
  );
}
