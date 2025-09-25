'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Check, Eye, EyeOff, Loader2 } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import Brand from '@/components/common/Brand';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [redirected, setRedirected] = useState(false);
  const emailRef = useRef('');
  const { login, isAuthenticated, require2FA, error, clearError } = useAuth();
  const router = useRouter();

  const sellingPoints = [
    {
      title: 'Smart dashboards',
      description: 'Get instant visibility into team performance and hiring funnels.',
    },
    {
      title: 'Automated workflows',
      description: 'Replace manual work with collaborative, no-code automations.',
    },
    {
      title: 'Enterprise-grade security',
      description: 'SOC 2 compliant infrastructure with continuous monitoring.',
    },
  ];

  useEffect(() => {
    emailRef.current = email;
  }, [email]);

  useEffect(() => {
    if (redirected) return;

    if (isAuthenticated && typeof window !== 'undefined') {
      const currentPath = window.location.pathname;
      if (currentPath !== '/dashboard') {
        console.log(`LoginPage: User authenticated, redirecting from ${currentPath} to /dashboard`);
        setRedirected(true);
        router.push('/dashboard');
      }
    } else if (require2FA) {
      console.log('LoginPage: 2FA required, redirecting to two-factor page');
      setRedirected(true);
      router.push(`/auth/two-factor?email=${encodeURIComponent(emailRef.current)}`);
    }
  }, [isAuthenticated, require2FA, router, redirected]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    clearError();

    try {
      await login({ email, password });
    } catch {
      // AuthContext handles error state
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative min-h-screen overflow-hidden bg-slate-950">
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute inset-0 bg-gradient-to-br from-slate-950 via-slate-900 to-black" />
        <div className="absolute -top-36 -left-24 h-96 w-96 rounded-full bg-brand-primary/30 blur-3xl" />
        <div className="absolute bottom-[-6rem] right-[-4rem] h-80 w-80 rounded-full bg-purple-500/20 blur-3xl" />
        <div className="absolute top-1/3 left-1/2 h-64 w-64 -translate-x-1/2 rounded-full bg-blue-500/10 blur-3xl" />
      </div>

      <div className="relative flex min-h-screen items-center px-4 py-12 sm:px-6 lg:px-8">
        <div className="mx-auto grid w-full max-w-6xl overflow-hidden rounded-3xl bg-white/80 shadow-2xl ring-1 ring-black/5 backdrop-blur supports-[backdrop-filter]:bg-white/60 dark:bg-gray-950/90 dark:ring-white/10 dark:supports-[backdrop-filter]:bg-gray-950/70 lg:grid-cols-[1.1fr_1fr]">
          <div className="relative hidden flex-col justify-between bg-gradient-to-br from-brand-primary via-brand-primary/80 to-purple-700 p-12 text-white lg:flex">
            <div>
              <Brand className="justify-start text-white [&>a]:text-white [&>a:hover]:text-white/90" />
              <h1 className="mt-16 text-4xl font-semibold leading-tight xl:text-5xl">
                Work smarter with MiraiWorks
              </h1>
              <p className="mt-6 max-w-md text-base text-white/80">
                Centralize hiring, onboarding, people analytics, and team feedback in one connected workspace designed for modern HR teams.
              </p>
            </div>

            <div className="mt-16 space-y-6">
              {sellingPoints.map(({ title, description }) => (
                <div key={title} className="flex items-start gap-4">
                  <span className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-full bg-white/15">
                    <Check className="h-5 w-5 text-white" />
                  </span>
                  <div>
                    <p className="text-sm font-semibold text-white">{title}</p>
                    <p className="mt-1 text-sm text-white/80">{description}</p>
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-16 rounded-2xl bg-white/10 p-6 backdrop-blur-lg">
              <p className="text-xs font-medium uppercase tracking-widest text-white/70">
                Trusted by teams at
              </p>
              <div className="mt-4 flex flex-wrap gap-x-6 gap-y-3 text-sm font-medium text-white/90">
                <span>Hikari Labs</span>
                <span>FutureForge</span>
                <span>Nimbus AI</span>
                <span>Zenith Finance</span>
              </div>
            </div>
          </div>

          <div className="flex flex-col justify-center p-8 sm:p-12">
            <div className="mb-10 text-center lg:hidden">
              <Brand className="justify-center" />
              <h2 className="mt-6 text-3xl font-semibold text-slate-900 dark:text-white">Welcome back</h2>
              <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">
                Sign in to your account to continue
              </p>
            </div>

            <h2 className="hidden text-3xl font-semibold text-slate-900 dark:text-white lg:block">
              Sign in to your workspace
            </h2>
            <p className="hidden mt-2 text-sm text-slate-500 dark:text-slate-400 lg:block">
              Enter your credentials to access your dashboard and stay in sync with your team.
            </p>

            <form onSubmit={handleSubmit} className="mt-10 space-y-6">
              {error && (
                <div
                  className="rounded-2xl border border-red-200/70 bg-red-50/80 p-4 text-left dark:border-red-500/40 dark:bg-red-500/10"
                  data-testid="error-message"
                >
                  <p className="text-sm text-red-600 dark:text-red-300">{error}</p>
                </div>
              )}

              <div className="space-y-1.5">
                <label htmlFor="email" className="block text-sm font-medium text-slate-700 dark:text-slate-200">
                  Email
                </label>
                <input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="input w-full bg-white/90 focus:ring-2 focus:ring-brand-primary"
                  placeholder="name@company.com"
                  required
                  autoComplete="email"
                  data-testid="email-input"
                />
              </div>

              <div className="space-y-1.5">
                <label htmlFor="password" className="block text-sm font-medium text-slate-700 dark:text-slate-200">
                  Password
                </label>
                <div className="relative">
                  <input
                    id="password"
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="input w-full bg-white/90 pr-12 focus:ring-2 focus:ring-brand-primary"
                    placeholder="Enter your password"
                    required
                    autoComplete="current-password"
                    data-testid="password-input"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 flex h-8 w-8 -translate-y-1/2 items-center justify-center rounded-full bg-white/60 text-slate-500 transition hover:bg-white/80 dark:bg-gray-800/80 dark:text-slate-300 dark:hover:bg-gray-800"
                  >
                    {showPassword ? (
                      <EyeOff className="h-4 w-4" />
                    ) : (
                      <Eye className="h-4 w-4" />
                    )}
                  </button>
                </div>
              </div>

              <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                <label htmlFor="remember-me" className="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-300">
                  <input
                    id="remember-me"
                    type="checkbox"
                    className="h-4 w-4 rounded border-slate-300 text-brand-primary focus:ring-brand-primary"
                  />
                  Keep me signed in
                </label>
                <Link
                  href="/auth/forgot-password"
                  className="text-sm font-medium text-brand-primary hover:text-brand-primary-dark"
                >
                  Forgot password?
                </Link>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="btn btn-primary w-full justify-center"
                data-testid="login-button"
              >
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Signing in...
                  </>
                ) : (
                  'Sign in'
                )}
              </button>
            </form>

            <div className="mt-10 space-y-4 text-center">
              <p className="text-sm text-slate-500 dark:text-slate-400">
                By continuing you agree to our{' '}
                <Link href="/legal/terms" className="font-medium text-brand-primary hover:text-brand-primary-dark">
                  Terms of Service
                </Link>{' '}
                and{' '}
                <Link href="/legal/privacy" className="font-medium text-brand-primary hover:text-brand-primary-dark">
                  Privacy Policy
                </Link>
                .
              </p>
              <p className="text-sm text-slate-500 dark:text-slate-400">
                Don&apos;t have an account?{' '}
                <Link href="/auth/register" className="font-medium text-brand-primary hover:text-brand-primary-dark">
                  Create one now
                </Link>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
