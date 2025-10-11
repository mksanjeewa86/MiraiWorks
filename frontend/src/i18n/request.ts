/**
 * Server-side i18n setup for next-intl
 * Handles loading translation messages for server components
 */

import { getRequestConfig } from 'next-intl/server';
import { notFound } from 'next/navigation';
import { locales } from './config';

export default getRequestConfig(async ({ requestLocale }): Promise<{ locale: string; messages: any }> => {
  // Wait for the locale to be determined
  const locale = await requestLocale;

  // Validate that the incoming `locale` parameter is valid
  if (!locale || !locales.includes(locale as any)) {
    console.error('Invalid locale:', locale);
    console.log('Available locales:', locales);
    notFound();
  }

  // Load all translation namespaces
  const [
    common,
    auth,
    errors,
    validation,
    dashboard,
    settings,
    jobs,
    interviews,
    candidates,
    messages,
    calendar,
    companies,
    exams,
    profile,
    notifications,
    todos,
  ] = await Promise.all([
    import(`./locales/${locale}/common.json`),
    import(`./locales/${locale}/auth.json`),
    import(`./locales/${locale}/errors.json`),
    import(`./locales/${locale}/validation.json`),
    import(`./locales/${locale}/dashboard.json`),
    import(`./locales/${locale}/settings.json`),
    import(`./locales/${locale}/jobs.json`),
    import(`./locales/${locale}/interviews.json`),
    import(`./locales/${locale}/candidates.json`),
    import(`./locales/${locale}/messages.json`),
    import(`./locales/${locale}/calendar.json`),
    import(`./locales/${locale}/companies.json`),
    import(`./locales/${locale}/exams.json`),
    import(`./locales/${locale}/profile.json`),
    import(`./locales/${locale}/notifications.json`),
    import(`./locales/${locale}/todos.json`),
  ]);

  return {
    locale: locale as string,
    messages: {
      common: common.default,
      auth: auth.default,
      errors: errors.default,
      validation: validation.default,
      dashboard: dashboard.default,
      settings: settings.default,
      jobs: jobs.default,
      interviews: interviews.default,
      candidates: candidates.default,
      messages: messages.default,
      calendar: calendar.default,
      companies: companies.default,
      exams: exams.default,
      profile: profile.default,
      notifications: notifications.default,
      todos: todos.default,
    },
  };
});
