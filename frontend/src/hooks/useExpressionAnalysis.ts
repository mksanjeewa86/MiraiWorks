import { useState, useRef, useCallback, useEffect } from 'react';

interface EmotionData {
  happy: number;
  sad: number;
  angry: number;
  fearful: number;
  disgusted: number;
  surprised: number;
  neutral: number;
}

interface EngagementMetrics {
  attentiveness: number; // 0-1, based on eye tracking and facial orientation
  engagement: number;    // 0-1, based on overall expression analysis
  speakingTime: number;  // milliseconds
  timestamp: number;
}

interface ExpressionAnalysisState {
  isSupported: boolean;
  isEnabled: boolean;
  isAnalyzing: boolean;
  hasConsent: boolean;
  currentEmotion: EmotionData | null;
  dominantEmotion: keyof EmotionData | null;
  engagementLevel: number; // 0-1
  engagementHistory: EngagementMetrics[];
  error?: string;
}

export const useExpressionAnalysis = (videoStream?: MediaStream) => {
  const [state, setState] = useState<ExpressionAnalysisState>({
    isSupported: false,
    isEnabled: false,
    isAnalyzing: false,
    hasConsent: false,
    currentEmotion: null,
    dominantEmotion: null,
    engagementLevel: 0,
    engagementHistory: []
  });

  const videoRef = useRef<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const faceApiRef = useRef<any>(null);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const startTimeRef = useRef<number>(Date.now());

  // Check if expression analysis is supported
  const checkSupport = useCallback(async () => {
    try {
      // Check for required browser features
      const hasWebGL = !!document.createElement('canvas').getContext('webgl');
      const hasWebAssembly = 'WebAssembly' in window;
      const hasMediaDevices = 'mediaDevices' in navigator;

      const supported = hasWebGL && hasWebAssembly && hasMediaDevices;

      setState(prev => ({
        ...prev,
        isSupported: supported
      }));

      return supported;
    } catch (error) {
      console.error('Error checking expression analysis support:', error);
      setState(prev => ({
        ...prev,
        isSupported: false,
        error: 'Failed to check browser support'
      }));
      return false;
    }
  }, []);

  // Load Face-API.js models
  const loadFaceApiModels = useCallback(async () => {
    try {
      setState(prev => ({ ...prev, isAnalyzing: true }));

      // Dynamically import face-api.js (optional dependency)
      const faceapi = await import('face-api.js').catch(() => {
        throw new Error('Face-API.js is not available. Please install it with: npm install face-api.js');
      });

      // Load required models
      const MODEL_URL = '/models'; // Assumes models are served from public/models/
      
      await Promise.all([
        faceapi.nets.tinyFaceDetector.loadFromUri(MODEL_URL),
        faceapi.nets.faceExpressionNet.loadFromUri(MODEL_URL),
        faceapi.nets.faceLandmark68Net.loadFromUri(MODEL_URL)
      ]);

      faceApiRef.current = faceapi;
      setState(prev => ({ ...prev, isAnalyzing: false }));

      return faceapi;
    } catch (error) {
      console.error('Error loading Face-API models:', error);
      setState(prev => ({
        ...prev,
        isAnalyzing: false,
        error: 'Failed to load facial analysis models. Please check your internet connection.'
      }));
      throw error;
    }
  }, []);

  // Analyze facial expressions from video frame
  const analyzeFrame = useCallback(async () => {
    if (!videoRef.current || !canvasRef.current || !faceApiRef.current || !state.isEnabled) {
      return;
    }

    const video = videoRef.current;
    const canvas = canvasRef.current;
    const faceapi = faceApiRef.current;

    try {
      // Set canvas size to match video
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;

      // Detect faces and expressions
      const detections = await faceapi
        .detectAllFaces(video, new faceapi.TinyFaceDetectorOptions())
        .withFaceExpressions()
        .withFaceLandmarks();

      if (detections && detections.length > 0) {
        const detection = detections[0]; // Use first detected face
        const expressions = detection.expressions;

        // Convert expressions to our format
        const emotionData: EmotionData = {
          happy: expressions.happy,
          sad: expressions.sad,
          angry: expressions.angry,
          fearful: expressions.fearful,
          disgusted: expressions.disgusted,
          surprised: expressions.surprised,
          neutral: expressions.neutral
        };

        // Find dominant emotion
        const dominantEmotion = Object.entries(emotionData).reduce((a, b) =>
          emotionData[a[0] as keyof EmotionData] > emotionData[b[0] as keyof EmotionData] ? a : b
        )[0] as keyof EmotionData;

        // Calculate engagement level based on expressions
        const engagementLevel = calculateEngagement(emotionData);

        // Update state
        setState(prev => ({
          ...prev,
          currentEmotion: emotionData,
          dominantEmotion,
          engagementLevel
        }));

        // Record engagement metrics
        recordEngagementMetrics(engagementLevel);
      }
    } catch (error) {
      console.error('Error analyzing frame:', error);
      // Don't update error state for individual frame failures to avoid UI flicker
    }
  }, [state.isEnabled]);

  // Calculate engagement level from facial data
  const calculateEngagement = useCallback((emotions: EmotionData): number => {
    // Basic engagement calculation based on emotions
    const positiveEmotions = emotions.happy + emotions.surprised;
    const negativeEmotions = emotions.sad + emotions.angry + emotions.fearful + emotions.disgusted;
    const attentiveness = 1 - emotions.neutral; // Less neutral = more attentive

    // Weight the factors
    const emotionalEngagement = (positiveEmotions - negativeEmotions * 0.5) * 0.4;
    const attentionScore = attentiveness * 0.6;

    // Normalize to 0-1 range
    const engagement = Math.max(0, Math.min(1, emotionalEngagement + attentionScore));

    return engagement;
  }, []);

  // Record engagement metrics over time
  const recordEngagementMetrics = useCallback((engagementLevel: number) => {
    const now = Date.now();
    const metrics: EngagementMetrics = {
      attentiveness: engagementLevel,
      engagement: engagementLevel,
      speakingTime: 0, // Would be filled by audio analysis
      timestamp: now
    };

    setState(prev => {
      const newHistory = [...prev.engagementHistory, metrics];
      
      // Keep only last 5 minutes of data (300 data points at 1 per second)
      const fiveMinutesAgo = now - 5 * 60 * 1000;
      const filteredHistory = newHistory.filter(m => m.timestamp > fiveMinutesAgo);

      return {
        ...prev,
        engagementHistory: filteredHistory
      };
    });
  }, []);

  // Request user consent for expression analysis
  const requestConsent = useCallback(async (): Promise<boolean> => {
    return new Promise((resolve) => {
      const consent = window.confirm(
        'This feature analyzes facial expressions to provide engagement insights during meetings. ' +
        'Your facial data is processed locally and never stored or transmitted. ' +
        'Do you consent to enable expression analysis?'
      );

      setState(prev => ({ ...prev, hasConsent: consent }));
      resolve(consent);
    });
  }, []);

  // Enable expression analysis
  const enableAnalysis = useCallback(async (skipConsent = false) => {
    try {
      // Request consent if not already granted
      if (!skipConsent && !state.hasConsent) {
        const hasConsent = await requestConsent();
        if (!hasConsent) {
          return false;
        }
      }

      setState(prev => ({ ...prev, isAnalyzing: true, error: undefined }));

      // Load models if not already loaded
      if (!faceApiRef.current) {
        await loadFaceApiModels();
      }

      setState(prev => ({ ...prev, isEnabled: true, isAnalyzing: false }));

      // Start analysis interval (analyze every 1 second for performance)
      intervalRef.current = setInterval(analyzeFrame, 1000);
      
      return true;
    } catch (error) {
      console.error('Error enabling expression analysis:', error);
      setState(prev => ({
        ...prev,
        isAnalyzing: false,
        error: error instanceof Error ? error.message : 'Failed to enable expression analysis'
      }));
      return false;
    }
  }, [state.hasConsent, requestConsent, loadFaceApiModels, analyzeFrame]);

  // Disable expression analysis
  const disableAnalysis = useCallback(() => {
    setState(prev => ({
      ...prev,
      isEnabled: false,
      currentEmotion: null,
      dominantEmotion: null,
      engagementLevel: 0
    }));

    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  }, []);

  // Get average engagement over time period
  const getAverageEngagement = useCallback((minutes: number = 5): number => {
    const cutoffTime = Date.now() - minutes * 60 * 1000;
    const recentMetrics = state.engagementHistory.filter(m => m.timestamp > cutoffTime);

    if (recentMetrics.length === 0) return 0;

    const sum = recentMetrics.reduce((acc, metric) => acc + metric.engagement, 0);
    return sum / recentMetrics.length;
  }, [state.engagementHistory]);

  // Get engagement trend (increasing, decreasing, stable)
  const getEngagementTrend = useCallback((): 'increasing' | 'decreasing' | 'stable' => {
    if (state.engagementHistory.length < 10) return 'stable';

    const recent = state.engagementHistory.slice(-5);
    const earlier = state.engagementHistory.slice(-10, -5);

    const recentAvg = recent.reduce((acc, m) => acc + m.engagement, 0) / recent.length;
    const earlierAvg = earlier.reduce((acc, m) => acc + m.engagement, 0) / earlier.length;

    const threshold = 0.1;
    if (recentAvg > earlierAvg + threshold) return 'increasing';
    if (recentAvg < earlierAvg - threshold) return 'decreasing';
    return 'stable';
  }, [state.engagementHistory]);

  // Setup video element
  useEffect(() => {
    if (videoStream && !videoRef.current) {
      videoRef.current = document.createElement('video');
      videoRef.current.srcObject = videoStream;
      videoRef.current.autoplay = true;
      videoRef.current.muted = true;
      videoRef.current.playsInline = true;
    }

    if (!canvasRef.current) {
      canvasRef.current = document.createElement('canvas');
    }
  }, [videoStream]);

  // Initialize on mount
  useEffect(() => {
    checkSupport();
    startTimeRef.current = Date.now();
  }, [checkSupport]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, []);

  return {
    ...state,
    enableAnalysis,
    disableAnalysis,
    requestConsent,
    getAverageEngagement,
    getEngagementTrend,
    checkSupport
  };
};