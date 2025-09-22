import { useState, useEffect } from 'react';
import { VideoCall } from '../types/video';
import { apiClient } from '../api/apiClient';

interface UseVideoCallResult {
  videoCall: VideoCall | null;
  loading: boolean;
  error: string | null;
  joinCall: () => Promise<void>;
  endCall: () => Promise<void>;
  recordConsent: (consented: boolean) => Promise<void>;
  refreshCall: () => Promise<void>;
}

export const useVideoCall = (callId?: string): UseVideoCallResult => {
  const [videoCall, setVideoCall] = useState<VideoCall | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchVideoCall = async () => {
    if (!callId) return;

    try {
      setLoading(true);
      const response = await apiClient.get(`/api/video-calls/${callId}`);
      setVideoCall(response.data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  const joinCall = async () => {
    if (!callId) return;

    try {
      await apiClient.post(`/api/video-calls/${callId}/join`);
      await fetchVideoCall(); // Refresh call data
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to join call');
      throw err;
    }
  };

  const endCall = async () => {
    if (!callId) return;

    try {
      await apiClient.post(`/api/video-calls/${callId}/end`);
      await fetchVideoCall(); // Refresh call data
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to end call');
      throw err;
    }
  };

  const recordConsent = async (consented: boolean) => {
    if (!callId) return;

    try {
      await apiClient.post(`/api/video-calls/${callId}/consent`, { consented });
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
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [callId]);

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