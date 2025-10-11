/**
 * Locale-aware router hook
 * Automatically adds locale prefix to all navigation calls
 */

'use client';

import { useRouter as useNextRouter } from 'next/navigation';
import { useLocale } from 'next-intl';
import { useCallback } from 'react';

interface LocaleRouter {
  push: (href: string) => void;
  replace: (href: string) => void;
  back: () => void;
  forward: () => void;
  refresh: () => void;
  prefetch: (href: string) => void;
}

/**
 * Custom hook that wraps Next.js router with automatic locale prefixing
 *
 * @example
 * const router = useLocaleRouter();
 * router.push('/dashboard'); // Automatically becomes '/en/dashboard' or '/ja/dashboard'
 * router.replace('/auth/login'); // Automatically becomes '/en/auth/login' or '/ja/auth/login'
 */
export function useLocaleRouter(): LocaleRouter {
  const nextRouter = useNextRouter();
  const locale = useLocale();

  /**
   * Add locale prefix to a route if it doesn't already have one
   */
  const addLocalePrefix = useCallback(
    (href: string): string => {
      // If href already starts with locale, return as-is
      if (href.startsWith(`/${locale}/`)) {
        return href;
      }

      // If href is absolute URL, return as-is
      if (href.startsWith('http://') || href.startsWith('https://')) {
        return href;
      }

      // If href is just '/', make it '/{locale}'
      if (href === '/') {
        return `/${locale}`;
      }

      // Add locale prefix to relative paths
      return `/${locale}${href}`;
    },
    [locale]
  );

  const push = useCallback(
    (href: string) => {
      const localeHref = addLocalePrefix(href);
      nextRouter.push(localeHref);
    },
    [nextRouter, addLocalePrefix]
  );

  const replace = useCallback(
    (href: string) => {
      const localeHref = addLocalePrefix(href);
      nextRouter.replace(localeHref);
    },
    [nextRouter, addLocalePrefix]
  );

  const prefetch = useCallback(
    (href: string) => {
      const localeHref = addLocalePrefix(href);
      nextRouter.prefetch(localeHref);
    },
    [nextRouter, addLocalePrefix]
  );

  return {
    push,
    replace,
    back: nextRouter.back,
    forward: nextRouter.forward,
    refresh: nextRouter.refresh,
    prefetch,
  };
}
