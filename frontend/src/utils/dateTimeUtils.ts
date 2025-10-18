/**
 * Datetime utility functions for handling timezone conversions
 */

/**
 * Converts a Date object to local datetime string format for datetime-local inputs
 * Format: YYYY-MM-DDTHH:mm
 *
 * This properly converts UTC times to the user's local timezone
 */
export const toLocalDatetimeString = (date: Date): string => {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');
  return `${year}-${month}-${day}T${hours}:${minutes}`;
};

/**
 * Converts an ISO datetime string or Date to local datetime string
 * Returns empty string if input is invalid
 */
export const formatDateForInput = (value?: string | Date | null): string => {
  if (!value) return '';

  const date = typeof value === 'string' ? new Date(value) : value;

  if (Number.isNaN(date.getTime())) return '';

  return toLocalDatetimeString(date);
};

/**
 * Converts a datetime-local string to ISO format for backend
 * The browser's Date constructor automatically handles the local timezone conversion
 */
export const toISOString = (datetimeLocal: string): string => {
  return new Date(datetimeLocal).toISOString();
};
