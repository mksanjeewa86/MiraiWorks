import { useState, useEffect, useCallback } from 'react';
import { getProfileCompleteness } from '@/api/profile';
import type { ProfileCompleteness } from '@/types/profile';

/**
 * Hook for fetching user's profile completeness data
 * @param options.enabled - If false, skip fetching completeness (default: true)
 */
export function useProfileCompleteness(options?: { enabled?: boolean }) {
  const enabled = options?.enabled ?? true; // Default to true if not provided

  const [completeness, setCompleteness] = useState<ProfileCompleteness | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchCompleteness = useCallback(async () => {
    if (!enabled) return; // Skip if disabled

    setLoading(true);
    setError(null);

    try {
      const data = await getProfileCompleteness();
      setCompleteness(data);
    } catch (err: any) {
      const errorMessage =
        err.response?.data?.detail || err.message || 'Failed to load profile completeness';
      setError(errorMessage);
      console.error('Error fetching profile completeness:', err);
    } finally {
      setLoading(false);
    }
  }, [enabled]);

  useEffect(() => {
    if (enabled) {
      fetchCompleteness();
    }
  }, [fetchCompleteness, enabled]);

  return { completeness, loading, error, refetch: fetchCompleteness };
}
