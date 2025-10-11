/**
 * i18n Configuration
 * Defines supported locales and locale names for MiraiWorks
 */

import { defineRouting } from 'next-intl/routing';
import type { Locale } from '@/types/i18n';

export const locales = ['en', 'ja'] as const;

export const defaultLocale: Locale = 'en';
export type { Locale };

export const localeNames: Record<Locale, string> = {
  en: 'English',
  ja: '日本語',
};

/**
 * Routing configuration for next-intl
 */
export const routing = defineRouting({
  locales: locales,
  defaultLocale: defaultLocale,
  localePrefix: 'always',
});

/**
 * Check if a locale is supported
 */
export function isValidLocale(locale: string): locale is Locale {
  return locales.includes(locale as Locale);
}
