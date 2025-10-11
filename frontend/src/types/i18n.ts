/**
 * I18n Type Definitions
 * Types for internationalization and localization
 */

import { locales } from '@/i18n/config';

/**
 * Supported locale types
 * Automatically derived from the locales array in i18n config
 */
export type Locale = typeof locales[number];
