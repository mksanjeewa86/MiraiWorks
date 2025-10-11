'use client';

import { useLocale } from 'next-intl';
import { useRouter, usePathname } from 'next/navigation';
import { locales, localeNames } from '@/i18n/config';
import { Globe } from 'lucide-react';

interface LanguageSwitcherProps {
  variant?: 'dropdown' | 'compact' | 'inline';
  className?: string;
}

export default function LanguageSwitcher({ variant = 'dropdown', className = '' }: LanguageSwitcherProps) {
  const locale = useLocale();
  const router = useRouter();
  const pathname = usePathname();

  const handleChange = async (newLocale: string) => {
    if (newLocale === locale) return;

    // Replace the locale in the pathname
    const segments = pathname.split('/');
    segments[1] = newLocale; // Replace locale segment (e.g., /en/ -> /ja/)
    const newPath = segments.join('/');

    // Navigate to the new locale path
    router.push(newPath);
    router.refresh();
  };

  // Compact toggle button
  if (variant === 'compact') {
    const currentLocale = locale || 'en';
    const nextLocale = currentLocale === 'en' ? 'ja' : 'en';

    return (
      <button
        onClick={() => handleChange(nextLocale)}
        className={`flex items-center gap-2 px-3 py-2 text-sm font-medium rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors ${className}`}
        title={`Switch to ${localeNames[nextLocale]}`}
      >
        <Globe className="h-4 w-4" />
        <span className="uppercase">{currentLocale}</span>
      </button>
    );
  }

  // Inline button group
  if (variant === 'inline') {
    return (
      <div className={`flex items-center gap-2 ${className}`}>
        {locales.map((loc) => (
          <button
            key={loc}
            onClick={() => handleChange(loc)}
            className={`px-3 py-1.5 text-sm font-medium rounded-md transition-all duration-200 ${
              locale === loc
                ? 'bg-brand-primary text-white'
                : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'
            }`}
          >
            {localeNames[loc]}
          </button>
        ))}
      </div>
    );
  }

  // Default dropdown
  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <Globe className="h-4 w-4 text-gray-600 dark:text-gray-400" />
      <select
        value={locale}
        onChange={(e) => handleChange(e.target.value)}
        className="px-3 py-1.5 border border-gray-300 dark:border-gray-700 rounded-md text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-brand-primary cursor-pointer"
      >
        {locales.map((loc) => (
          <option key={loc} value={loc}>
            {localeNames[loc]}
          </option>
        ))}
      </select>
    </div>
  );
}
