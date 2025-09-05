import { useState, useRef, useCallback, useEffect } from 'react';

interface ParticipantMetrics {
  user_id: number;
  name: string;
  speaking_time: number; // milliseconds
  silence_time: number;  // milliseconds
  engagement_scores: number[];
  video_quality_issues: number;
  audio_quality_issues: number;
  connection_issues: number;
  interactions: number; // chat messages, reactions, etc.
  join_time: number;
  leave_time?: number;
}

interface MeetingAnalyticsData {
  meeting_id?: number;
  start_time: number;
  end_time?: number;
  total_duration: number; // milliseconds
  participant_metrics: Record<number, ParticipantMetrics>;
  overall_engagement: number; // 0-1
  speaking_distribution: Record<number, number>; // user_id -> percentage
  quality_metrics: {
    avg_video_quality: number;
    avg_audio_quality: number;
    connection_stability: number;
    total_interruptions: number;
  };
  interaction_metrics: {
    total_chat_messages: number;
    screen_shares_count: number;
    file_shares_count: number;
    reactions_count: number;
  };
  insights: string[];
  recommendations: string[];
}

interface AudioLevelData {
  user_id: number;
  level: number; // 0-1
  timestamp: number;
  is_speaking: boolean;
}

export const useMeetingAnalytics = () => {
  const [analytics, setAnalytics] = useState<MeetingAnalyticsData>({
    start_time: Date.now(),
    total_duration: 0,
    participant_metrics: {},
    overall_engagement: 0,
    speaking_distribution: {},
    quality_metrics: {
      avg_video_quality: 1,
      avg_audio_quality: 1,
      connection_stability: 1,
      total_interruptions: 0
    },
    interaction_metrics: {
      total_chat_messages: 0,
      screen_shares_count: 0,
      file_shares_count: 0,
      reactions_count: 0
    },
    insights: [],
    recommendations: []
  });

  const [isTracking, setIsTracking] = useState(false);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserNodesRef = useRef<Map<number, AnalyserNode>>(new Map());
  const audioDataRef = useRef<Map<number, AudioLevelData[]>>(new Map());
  const speakingThreshold = 0.1; // Audio level threshold for detecting speech

  // Initialize audio analysis
  const initializeAudioAnalysis = useCallback(async () => {
    try {
      audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)();
    } catch (error) {
      console.error('Failed to initialize audio context:', error);
    }
  }, []);

  // Add participant to tracking
  const addParticipant = useCallback((participant: { user_id: number; name: string }) => {
    const now = Date.now();
    
    setAnalytics(prev => ({
      ...prev,
      participant_metrics: {
        ...prev.participant_metrics,
        [participant.user_id]: {
          user_id: participant.user_id,
          name: participant.name,
          speaking_time: 0,
          silence_time: 0,
          engagement_scores: [],
          video_quality_issues: 0,
          audio_quality_issues: 0,
          connection_issues: 0,
          interactions: 0,
          join_time: now
        }
      }
    }));

    // Initialize audio data tracking
    audioDataRef.current.set(participant.user_id, []);
  }, []);

  // Remove participant from tracking
  const removeParticipant = useCallback((userId: number) => {
    const now = Date.now();
    
    setAnalytics(prev => {
      const participant = prev.participant_metrics[userId];
      if (participant) {
        participant.leave_time = now;
      }
      return { ...prev };
    });

    // Clean up audio tracking
    analyserNodesRef.current.delete(userId);
    audioDataRef.current.delete(userId);
  }, []);

  // Track audio stream for participant
  const trackParticipantAudio = useCallback((userId: number, stream: MediaStream) => {
    if (!audioContextRef.current) return;

    try {
      const audioTrack = stream.getAudioTracks()[0];
      if (!audioTrack) return;

      const source = audioContextRef.current.createMediaStreamSource(stream);
      const analyser = audioContextRef.current.createAnalyser();
      
      analyser.fftSize = 256;
      analyser.smoothingTimeConstant = 0.8;
      
      source.connect(analyser);
      analyserNodesRef.current.set(userId, analyser);

      // Start monitoring audio levels
      monitorAudioLevel(userId, analyser);
    } catch (error) {
      console.error('Error setting up audio analysis for participant:', error);
    }
  }, []);

  // Monitor audio levels for speech detection
  const monitorAudioLevel = useCallback((userId: number, analyser: AnalyserNode) => {
    const bufferLength = analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);
    
    const checkAudioLevel = () => {
      if (!isTracking) return;
      
      analyser.getByteFrequencyData(dataArray);
      
      // Calculate RMS (Root Mean Square) for audio level
      let sum = 0;
      for (let i = 0; i < bufferLength; i++) {
        sum += dataArray[i] * dataArray[i];
      }
      const rms = Math.sqrt(sum / bufferLength) / 255;
      
      const audioData: AudioLevelData = {
        user_id: userId,
        level: rms,
        timestamp: Date.now(),
        is_speaking: rms > speakingThreshold
      };

      // Store audio data
      const userAudioData = audioDataRef.current.get(userId) || [];
      userAudioData.push(audioData);
      
      // Keep only last 5 minutes of audio data
      const fiveMinutesAgo = Date.now() - 5 * 60 * 1000;
      const filteredData = userAudioData.filter(data => data.timestamp > fiveMinutesAgo);
      audioDataRef.current.set(userId, filteredData);

      requestAnimationFrame(checkAudioLevel);
    };

    checkAudioLevel();
  }, [isTracking, speakingThreshold]);

  // Calculate speaking time distribution
  const calculateSpeakingDistribution = useCallback((): Record<number, number> => {
    const distribution: Record<number, number> = {};
    let totalSpeakingTime = 0;

    // Calculate speaking time for each participant
    audioDataRef.current.forEach((audioData, userId) => {
      let speakingTime = 0;
      let lastSpeakingTimestamp: number | null = null;

      audioData.forEach(data => {
        if (data.is_speaking) {
          if (!lastSpeakingTimestamp) {
            lastSpeakingTimestamp = data.timestamp;
          }
        } else if (lastSpeakingTimestamp) {
          // End of speaking segment
          speakingTime += data.timestamp - lastSpeakingTimestamp;
          lastSpeakingTimestamp = null;
        }
      });

      // Handle ongoing speaking session
      if (lastSpeakingTimestamp) {
        speakingTime += Date.now() - lastSpeakingTimestamp;
      }

      distribution[userId] = speakingTime;
      totalSpeakingTime += speakingTime;
    });

    // Convert to percentages
    if (totalSpeakingTime > 0) {
      Object.keys(distribution).forEach(userId => {
        distribution[parseInt(userId)] = (distribution[parseInt(userId)] / totalSpeakingTime) * 100;
      });
    }

    return distribution;
  }, []);

  // Update participant engagement score
  const updateEngagementScore = useCallback((userId: number, score: number) => {
    setAnalytics(prev => {
      const participant = prev.participant_metrics[userId];
      if (participant) {
        participant.engagement_scores.push(score);
        
        // Keep only last 10 scores for average calculation
        if (participant.engagement_scores.length > 10) {
          participant.engagement_scores = participant.engagement_scores.slice(-10);
        }
      }
      return { ...prev };
    });
  }, []);

  // Track interaction (chat message, reaction, etc.)
  const trackInteraction = useCallback((type: 'chat' | 'screen_share' | 'file_share' | 'reaction', userId?: number) => {
    setAnalytics(prev => {
      const newAnalytics = { ...prev };

      // Update overall interaction metrics
      switch (type) {
        case 'chat':
          newAnalytics.interaction_metrics.total_chat_messages++;
          break;
        case 'screen_share':
          newAnalytics.interaction_metrics.screen_shares_count++;
          break;
        case 'file_share':
          newAnalytics.interaction_metrics.file_shares_count++;
          break;
        case 'reaction':
          newAnalytics.interaction_metrics.reactions_count++;
          break;
      }

      // Update participant-specific interaction count
      if (userId && newAnalytics.participant_metrics[userId]) {
        newAnalytics.participant_metrics[userId].interactions++;
      }

      return newAnalytics;
    });
  }, []);

  // Track quality issues
  const trackQualityIssue = useCallback((userId: number, type: 'video' | 'audio' | 'connection') => {
    setAnalytics(prev => {
      const participant = prev.participant_metrics[userId];
      if (participant) {
        switch (type) {
          case 'video':
            participant.video_quality_issues++;
            break;
          case 'audio':
            participant.audio_quality_issues++;
            break;
          case 'connection':
            participant.connection_issues++;
            prev.quality_metrics.total_interruptions++;
            break;
        }
      }
      return { ...prev };
    });
  }, []);

  // Generate insights and recommendations
  const generateInsights = useCallback((): { insights: string[]; recommendations: string[] } => {
    const insights: string[] = [];
    const recommendations: string[] = [];
    
    const speakingDistribution = calculateSpeakingDistribution();
    const participants = Object.values(analytics.participant_metrics);
    
    // Speaking time analysis
    const speakingTimes = Object.values(speakingDistribution);
    if (speakingTimes.length > 1) {
      const maxSpeaking = Math.max(...speakingTimes);
      const minSpeaking = Math.min(...speakingTimes);
      
      if (maxSpeaking - minSpeaking > 50) {
        insights.push('Uneven speaking distribution detected');
        recommendations.push('Consider encouraging quieter participants to share their thoughts');
      }
      
      if (maxSpeaking > 70) {
        insights.push('One participant dominated the conversation');
        recommendations.push('Try to facilitate more balanced discussions');
      }
    }

    // Engagement analysis
    const avgEngagements = participants.map(p => {
      const avg = p.engagement_scores.length > 0 
        ? p.engagement_scores.reduce((sum, score) => sum + score, 0) / p.engagement_scores.length
        : 0;
      return avg;
    });
    
    const overallEngagement = avgEngagements.length > 0 
      ? avgEngagements.reduce((sum, eng) => sum + eng, 0) / avgEngagements.length
      : 0;
    
    if (overallEngagement < 0.4) {
      insights.push('Overall engagement was low during the meeting');
      recommendations.push('Consider using interactive features like polls or breakout rooms');
    } else if (overallEngagement > 0.8) {
      insights.push('High engagement levels maintained throughout the meeting');
    }

    // Quality analysis
    const totalQualityIssues = participants.reduce((sum, p) => 
      sum + p.video_quality_issues + p.audio_quality_issues + p.connection_issues, 0
    );
    
    if (totalQualityIssues > 5) {
      insights.push('Multiple quality issues detected during the meeting');
      recommendations.push('Consider checking internet connection and device settings');
    }

    // Duration analysis
    const duration = analytics.total_duration / (1000 * 60); // minutes
    if (duration > 60) {
      insights.push('Long meeting detected (over 60 minutes)');
      recommendations.push('Consider breaking long meetings into shorter sessions');
    }

    return { insights, recommendations };
  }, [analytics, calculateSpeakingDistribution]);

  // Start tracking analytics
  const startTracking = useCallback(async () => {
    setIsTracking(true);
    await initializeAudioAnalysis();
    
    setAnalytics(prev => ({
      ...prev,
      start_time: Date.now()
    }));
  }, [initializeAudioAnalysis]);

  // Stop tracking and finalize analytics
  const stopTracking = useCallback(() => {
    setIsTracking(false);
    const endTime = Date.now();
    
    setAnalytics(prev => {
      const duration = endTime - prev.start_time;
      const speakingDistribution = calculateSpeakingDistribution();
      const { insights, recommendations } = generateInsights();

      return {
        ...prev,
        end_time: endTime,
        total_duration: duration,
        speaking_distribution: speakingDistribution,
        insights,
        recommendations
      };
    });
  }, [calculateSpeakingDistribution, generateInsights]);

  // Get real-time analytics summary
  const getAnalyticsSummary = useCallback(() => {
    const participants = Object.values(analytics.participant_metrics);
    const currentTime = Date.now();
    const duration = currentTime - analytics.start_time;
    
    return {
      duration: Math.floor(duration / 1000), // seconds
      participant_count: participants.length,
      active_speakers: participants.filter(p => {
        const recentAudio = audioDataRef.current.get(p.user_id) || [];
        const recentActivity = recentAudio.filter(a => currentTime - a.timestamp < 5000);
        return recentActivity.some(a => a.is_speaking);
      }).length,
      overall_engagement: analytics.overall_engagement,
      quality_score: (
        analytics.quality_metrics.avg_video_quality + 
        analytics.quality_metrics.avg_audio_quality + 
        analytics.quality_metrics.connection_stability
      ) / 3
    };
  }, [analytics]);

  // Initialize on mount
  useEffect(() => {
    return () => {
      if (audioContextRef.current) {
        audioContextRef.current.close();
      }
    };
  }, []);

  return {
    analytics,
    isTracking,
    startTracking,
    stopTracking,
    addParticipant,
    removeParticipant,
    trackParticipantAudio,
    updateEngagementScore,
    trackInteraction,
    trackQualityIssue,
    getAnalyticsSummary,
    generateInsights
  };
};