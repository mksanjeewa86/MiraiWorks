import { useState, useEffect, useRef } from 'react';
import { UseTranscriptionResult } from '@/types/hooks';
import { TranscriptionSegment, TranscriptionState } from '../types/video';
import { apiClient } from '../api/apiClient';


export const useTranscription = (
  callId?: string,
  enabled: boolean = true
): UseTranscriptionResult => {
  const [state, setState] = useState<TranscriptionState>({
    segments: [],
    isTranscribing: false,
    language: 'ja',
    searchQuery: '',
    highlightedSegments: [],
  });

  const websocket = useRef<WebSocket | null>(null);
  const audioContext = useRef<AudioContext | null>(null);
  const mediaRecorder = useRef<MediaRecorder | null>(null);

  const connectTranscriptionWS = () => {
    if (!callId || !enabled) return;

    const wsUrl = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws/transcription/${callId}`;
    websocket.current = new WebSocket(wsUrl);

    websocket.current.onopen = () => {
      console.log('Connected to transcription service');
      setState((prev) => ({ ...prev, isTranscribing: true }));
    };

    websocket.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      handleTranscriptionMessage(data);
    };

    websocket.current.onclose = () => {
      console.log('Disconnected from transcription service');
      setState((prev) => ({ ...prev, isTranscribing: false }));
    };

    websocket.current.onerror = (error) => {
      console.error('Transcription WebSocket error:', error);
      setState((prev) => ({ ...prev, isTranscribing: false }));
    };
  };

  const handleTranscriptionMessage = (data: unknown) => {
    const message = data as {
      type?: string;
      segment?: {
        video_call_id: number;
        speaker_id: number;
        segment_text: string;
        start_time: number;
        end_time: number;
        confidence?: number;
      };
      status?: string;
      message?: string;
    };
    switch (message.type) {
      case 'segment':
        if (message.segment) {
          addSegment({
            video_call_id: parseInt(callId || '0'),
            speaker_id: message.segment.speaker_id,
            speaker_name: '',
            segment_text: message.segment.segment_text,
            start_time: message.segment.start_time,
            end_time: message.segment.end_time,
            confidence: message.segment.confidence,
          });
        }
        break;

      case 'error':
        console.error('Transcription error:', message.message);
        setState((prev) => ({ ...prev, isTranscribing: false }));
        break;
    }
  };

  const startTranscription = async () => {
    try {
      if (!callId || !enabled) return;

      // Initialize audio context for processing
      audioContext.current = new AudioContext();

      // Start audio capture for transcription
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount: 1,
          sampleRate: 16000,
          echoCancellation: true,
          noiseSuppression: true,
        },
      });

      // Set up media recorder for audio chunks
      mediaRecorder.current = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus',
      });

      mediaRecorder.current.ondataavailable = (event) => {
        if (event.data.size > 0 && websocket.current?.readyState === WebSocket.OPEN) {
          // Send audio chunk to transcription service
          const reader = new FileReader();
          reader.onload = () => {
            websocket.current?.send(
              JSON.stringify({
                type: 'audio_chunk',
                data: reader.result,
                language: state.language,
                timestamp: Date.now(),
              })
            );
          };
          reader.readAsArrayBuffer(event.data);
        }
      };

      // Start recording in 1-second chunks
      mediaRecorder.current.start(1000);

      // Connect to transcription WebSocket
      connectTranscriptionWS();
    } catch (error) {
      console.error('Failed to start transcription:', error);
    }
  };

  const stopTranscription = async () => {
    // Stop media recorder
    if (mediaRecorder.current && mediaRecorder.current.state !== 'inactive') {
      mediaRecorder.current.stop();
    }

    // Close audio context
    if (audioContext.current) {
      await audioContext.current.close();
      audioContext.current = null;
    }

    // Close WebSocket connection
    if (websocket.current) {
      websocket.current.close();
      websocket.current = null;
    }

    setState((prev) => ({ ...prev, isTranscribing: false }));
  };

  const setTranscriptionLanguage = (language: string) => {
    setState((prev) => ({ ...prev, language }));

    // Notify transcription service of language change
    if (websocket.current?.readyState === WebSocket.OPEN) {
      websocket.current.send(
        JSON.stringify({
          type: 'language_change',
          language,
        })
      );
    }
  };

  const addSegment = (segmentData: Omit<TranscriptionSegment, 'id' | 'created_at'>) => {
    const newSegment: TranscriptionSegment = {
      ...segmentData,
      id: Date.now(), // Temporary ID
      created_at: new Date().toISOString(),
    };

    setState((prev) => ({
      ...prev,
      segments: [...prev.segments, newSegment],
    }));

    // Also save to backend
    saveSegmentToBackend(newSegment);
  };

  const saveSegmentToBackend = async (segment: TranscriptionSegment) => {
    try {
      await apiClient.post<TranscriptionSegment>(`/api/video-calls/${callId}/transcript/segments`, {
        speaker_id: segment.speaker_id,
        segment_text: segment.segment_text,
        start_time: segment.start_time,
        end_time: segment.end_time,
        confidence: segment.confidence,
      });
    } catch (error) {
      console.error('Error saving transcription segment:', error);
    }
  };

  const searchTranscript = (query: string) => {
    setState((prev) => {
      const highlighted = query.trim()
        ? prev.segments
            .filter((segment) => segment.segment_text.toLowerCase().includes(query.toLowerCase()))
            .map((segment) => segment.id)
        : [];

      return {
        ...prev,
        searchQuery: query,
        highlightedSegments: highlighted,
      };
    });
  };

  const exportTranscript = async (format: 'txt' | 'pdf' | 'srt'): Promise<string | null> => {
    try {
      const response = await apiClient.get<{ download_url: string }>(
        `/api/video-calls/${callId}/transcript/download?format=${format}`
      );
      return response.data.download_url;
    } catch (error) {
      console.error('Error exporting transcript:', error);
      return null;
    }
  };

  // Load existing segments on mount
  useEffect(() => {
    if (callId && enabled) {
      loadExistingSegments();
    }
  }, [callId, enabled]);

  const loadExistingSegments = async () => {
    try {
      const response = await apiClient.get<{ segments: TranscriptionSegment[] }>(
        `/api/video-calls/${callId}/transcript`
      );
      if (response.data.segments) {
        setState((prev) => ({
          ...prev,
          segments: response.data.segments,
        }));
      }
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : '';
      // It's normal for new video calls to not have existing transcripts
      if (
        errorMessage.includes('Transcript not available') ||
        errorMessage.includes('404') ||
        errorMessage.includes('not found')
      ) {
        console.log(
          'No existing transcript found for this video call - this is normal for new calls'
        );
      } else {
        console.error('Error loading existing segments:', error);
      }
    }
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopTranscription();
    };
  }, []);

  return {
    ...state,
    setTranscriptionLanguage,
    startTranscription,
    stopTranscription,
    addSegment,
    searchTranscript,
    exportTranscript,
  };
};
