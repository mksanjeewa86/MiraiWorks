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

/**
 * Converts UTC datetime string from API to local date and time parts for form inputs
 * Returns { date: 'YYYY-MM-DD', time: 'HH:MM' }
 */
export const utcToLocalDateTimeParts = (
  utcDatetime?: string | null
): { date: string; time: string } => {
  if (!utcDatetime) return { date: '', time: '' };

  const date = new Date(utcDatetime);
  if (Number.isNaN(date.getTime())) return { date: '', time: '' };

  // Get local date and time components
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');

  return {
    date: `${year}-${month}-${day}`,
    time: `${hours}:${minutes}`
  };
};

/**
 * Converts local date and time parts to UTC ISO string for API
 * @param date Date in YYYY-MM-DD format
 * @param time Time in HH:MM format (optional)
 * @returns ISO datetime string in UTC
 */
export const localDateTimePartsToUTC = (
  date: string,
  time?: string
): string | null => {
  if (!date) return null;

  // If no time provided, use 23:59:59 (end of day)
  const timeStr = time || '23:59';

  // Combine date and time (browser treats as local timezone)
  const datetimeStr = `${date}T${timeStr}:00`;
  const localDate = new Date(datetimeStr);

  if (Number.isNaN(localDate.getTime())) return null;

  // Convert to UTC ISO string
  return localDate.toISOString();
};

/**
 * Formats UTC datetime for display in local timezone
 * @param utcDatetime UTC datetime string from API
 * @returns Formatted string like "Oct 19, 2025 at 15:00" in local timezone
 */
export const formatUTCDateTimeForDisplay = (
  utcDatetime?: string | null
): string => {
  if (!utcDatetime) return '';

  const date = new Date(utcDatetime);
  if (Number.isNaN(date.getTime())) return '';

  // Format date part in local timezone
  const formattedDate = date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  });

  // Format time part in local timezone (24-hour format)
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');

  return `${formattedDate} at ${hours}:${minutes}`;
};
