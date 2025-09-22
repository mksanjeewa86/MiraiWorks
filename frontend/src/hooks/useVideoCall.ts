import { useState, useEffect } from 'react';
import { VideoCall } from '../types/video';

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
      const token = localStorage.getItem('access_token');
      
      const response = await fetch(`/api/video-calls/${callId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch video call');
      }

      const data = await response.json();
      setVideoCall(data);
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
      const token = localStorage.getItem('access_token');
      
      const response = await fetch(`/api/video-calls/${callId}/join`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to join call');
      }

      await fetchVideoCall(); // Refresh call data
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to join call');
      throw err;
    }
  };

  const endCall = async () => {
    if (!callId) return;

    try {
      const token = localStorage.getItem('access_token');
      
      const response = await fetch(`/api/video-calls/${callId}/end`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to end call');
      }

      await fetchVideoCall(); // Refresh call data
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to end call');
      throw err;
    }
  };

  const recordConsent = async (consented: boolean) => {
    if (!callId) return;

    try {
      const token = localStorage.getItem('access_token');
      
      const response = await fetch(`/api/video-calls/${callId}/consent`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ consented }),
      });

      if (!response.ok) {
        throw new Error('Failed to record consent');
      }
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