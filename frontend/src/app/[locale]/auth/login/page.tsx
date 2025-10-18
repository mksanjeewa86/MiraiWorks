'use client';

import { useState, useEffect, useRef, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { Eye, EyeOff, Loader2, Mail, Lock } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { useTranslations, useLocale } from 'next-intl';
import { ROUTES } from '@/routes/config';

function LoginContent() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [redirected, setRedirected] = useState(false);
  const emailRef = useRef('');
  const { login, isAuthenticated, require2FA, error, clearError } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();
  const sessionExpired = searchParams.get('expired') === 'true';
  const t = useTranslations('auth.login');
  const tErrors = useTranslations('errors.auth');
  const locale = useLocale();

  useEffect(() => {
    emailRef.current = email;
  }, [email]);

  useEffect(() => {
    if (redirected) return;

    if (isAuthenticated && typeof window !== 'undefined') {
      const currentPath = window.location.pathname;
      if (!currentPath.includes('/dashboard')) {
        setRedirected(true);
        router.push(`/${locale}${ROUTES.DASHBOARD}`);
      }
    } else if (require2FA) {
      setRedirected(true);
      router.push(`/${locale}${ROUTES.AUTH.TWO_FACTOR_WITH_EMAIL(emailRef.current)}`);
    }
  }, [isAuthenticated, require2FA, router, redirected, locale]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    clearError();

    try {
      await login({ email, password, rememberMe });
    } catch {
      // AuthContext handles error state
    } finally {
      setLoading(false);
    }
  };

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
          <Link href={`/${locale}/`} className="inline-block mb-6">
            <h1 className="text-4xl font-extrabold text-white">
              MiraiWorks
            </h1>
          </Link>
          <h2 className="text-3xl font-bold text-white mb-2">
            {t('title')}
          </h2>
          <p className="text-gray-300">
            {t('subtitle')}
          </p>
        </div>

        {/* Login Form */}
        <div className="bg-white/10 backdrop-blur-lg rounded-3xl p-8 border-2 border-white/20 shadow-2xl">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Session Expired Message */}
            {sessionExpired && !error && (
              <div
                className="p-4 rounded-2xl bg-amber-500/20 border border-amber-400/50 backdrop-blur-sm"
                data-testid="session-expired-message"
              >
                <p className="text-sm text-amber-100 font-medium">
                  {tErrors('sessionExpired')}
                </p>
              </div>
            )}

            {/* Error Message */}
            {error && (
              <div
                className="p-4 rounded-2xl bg-red-500/20 border border-red-400/50 backdrop-blur-sm"
                data-testid="error-message"
              >
                <p className="text-sm text-red-100 font-medium">{error}</p>
              </div>
            )}

            {/* Email */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium mb-2 text-gray-200">
                {t('emailLabel')}
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5 z-10" />
                <input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full pl-11 pr-4 py-3 bg-white/10 border border-white/20 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-400 focus:border-transparent transition-all duration-300"
                  placeholder={t('emailPlaceholder')}
                  required
                  autoComplete="email"
                  data-testid="email-input"
                />
              </div>
            </div>

            {/* Password */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium mb-2 text-gray-200">
                {t('passwordLabel')}
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5 z-10" />
                <input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full pl-11 pr-12 py-3 bg-white/10 border border-white/20 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-400 focus:border-transparent transition-all duration-300"
                  placeholder={t('passwordPlaceholder')}
                  required
                  autoComplete="current-password"
                  data-testid="password-input"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 p-1 rounded-full hover:bg-white/10 z-10 transition-all duration-300"
                >
                  {showPassword ? (
                    <EyeOff className="h-5 w-5 text-gray-400" />
                  ) : (
                    <Eye className="h-5 w-5 text-gray-400" />
                  )}
                </button>
              </div>
            </div>

            {/* Remember Me & Forgot Password */}
            <div className="flex items-center justify-between">
              <label
                htmlFor="remember-me"
                className="flex items-center gap-2 text-sm text-gray-300 cursor-pointer"
              >
                <input
                  id="remember-me"
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  className="h-4 w-4 rounded border-gray-300 text-purple-600 focus:ring-purple-400 focus:ring-offset-0 bg-white/10 border-white/20"
                  data-testid="remember-me-checkbox"
                />
                {t('rememberMe')}
              </label>
              <Link
                href={`/${locale}${ROUTES.AUTH.FORGOT_PASSWORD}`}
                className="text-sm font-medium text-purple-300 hover:text-purple-200 transition-colors duration-300"
              >
                {t('forgotPassword')}
              </Link>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 px-4 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-semibold rounded-xl shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none flex items-center justify-center"
              data-testid="login-button"
            >
              {loading ? (
                <>
                  <Loader2 className="animate-spin h-5 w-5 mr-2" />
                  {t('success.redirecting')}
                </>
              ) : (
                t('submitButton')
              )}
            </button>
          </form>

          {/* Sign Up Link */}
          <div className="mt-6 text-center">
            <p className="text-sm text-gray-300">
              {t('noAccount')}{' '}
              <Link
                href={`/${locale}${ROUTES.AUTH.REGISTER}`}
                className="font-semibold text-purple-300 hover:text-purple-200 transition-colors duration-300"
              >
                {t('signUpLink')}
              </Link>
            </p>
          </div>
        </div>

        {/* Back to Home */}
        <div className="mt-6 text-center">
          <Link
            href={`/${locale}/`}
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

export default function LoginPage() {
  return (
    <Suspense fallback={<div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900"><Loader2 className="h-8 w-8 animate-spin text-white" /></div>}>
      <LoginContent />
    </Suspense>
  );
}
