import { useState, useEffect } from 'react';
import { VideoCall } from '../types/video';
import { apiClient } from '../api/apiClient';
import { API_ENDPOINTS } from '../api/config';
import type { UseVideoCallResult, UseVideoCallOptions } from '../types/hooks';

export const useVideoCall = (
  identifier?: string,
  options: UseVideoCallOptions = { type: 'id' }
): UseVideoCallResult => {
  const [videoCall, setVideoCall] = useState<VideoCall | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchVideoCall = async () => {
    if (!identifier) return;

    try {
      setLoading(true);
      const endpoint =
        options.type === 'roomCode'
          ? API_ENDPOINTS.VIDEO_CALLS.BY_ROOM(identifier)
          : API_ENDPOINTS.VIDEO_CALLS.BY_ID(identifier);

      const response = await apiClient.get<VideoCall>(endpoint);
      setVideoCall(response.data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  const joinCall = async () => {
    if (!identifier || !videoCall) return;

    try {
      const endpoint =
        options.type === 'roomCode'
          ? API_ENDPOINTS.VIDEO_CALLS.JOIN_ROOM(identifier)
          : API_ENDPOINTS.VIDEO_CALLS.JOIN(identifier);

      await apiClient.post(endpoint);
      await fetchVideoCall(); // Refresh call data
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to join call');
      throw err;
    }
  };

  const endCall = async () => {
    if (!identifier || !videoCall) return;

    try {
      const endpoint =
        options.type === 'roomCode'
          ? API_ENDPOINTS.VIDEO_CALLS.LEAVE_ROOM(identifier)
          : API_ENDPOINTS.VIDEO_CALLS.LEAVE(identifier);

      // Use /leave endpoint instead of /end to allow any participant to leave
      const response = await apiClient.post<{ message: string; call_ended: boolean }>(endpoint);
      await fetchVideoCall(); // Refresh call data
      return response.data;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to leave call');
      throw err;
    }
  };

  const recordConsent = async (consented: boolean) => {
    if (!identifier || !videoCall) return;

    try {
      const endpoint =
        options.type === 'roomCode'
          ? API_ENDPOINTS.VIDEO_CALLS.CONSENT_ROOM(identifier)
          : API_ENDPOINTS.VIDEO_CALLS.CONSENT(identifier);

      await apiClient.post(endpoint, { consented });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to record consent');
      throw err;
    }
  };

  const refreshCall = async () => {
    await fetchVideoCall();
  };

  useEffect(() => {
    fetchVideoCall();
  }, [identifier, options.type]);

  return {
    videoCall,
    loading,
    error,
    joinCall,
    endCall,
    recordConsent,
    refreshCall,
  };
};
