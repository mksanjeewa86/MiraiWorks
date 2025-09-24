'use client';

import React, { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { ArrowLeft, AlertCircle } from 'lucide-react';
import Link from 'next/link';
import AppLayout from '@/components/layout/AppLayout';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import { VideoCallRoom } from '@/components/video/VideoCallRoom';
import { useToast } from '@/contexts/ToastContext';
import { interviewsApi } from '@/api/interviews';
import { apiClient } from '@/api/apiClient';
import type { Interview } from '@/types/interview';
import type { VideoCall } from '@/types/video';

function VideoCallContent() {
  const params = useParams();
  // const router = useRouter(); // TODO: Use for navigation if needed
  const { showToast } = useToast();
  const [interview, setInterview] = useState<Interview | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [videoCallId, setVideoCallId] = useState<string | null>(null);

  const interviewId = typeof params.id === 'string' ? parseInt(params.id) : null;

  useEffect(() => {
    if (!interviewId) {
      setError('Invalid interview ID');
      setLoading(false);
      return;
    }

    const fetchInterview = async () => {
      try {
        setLoading(true);

        // Fetch interview details
        const response = await interviewsApi.getById(interviewId);
        const interview = response.data;

        if (!interview) {
          throw new Error('Interview not found');
        }

        if (interview.interview_type !== 'video') {
          throw new Error('This interview is not configured for video calls');
        }

        setInterview(interview);

        // Try to get or create video call for this interview
        try {
          try {
            // Try to get existing video call
            const videoCallResponse = await apiClient.get<VideoCall>(
              `/api/interviews/${interviewId}/video-call`
            );
            setVideoCallId(videoCallResponse.data.id.toString());
          } catch (error: unknown) {
            const errorMessage = error instanceof Error ? error.message : 'Unknown error';
            console.log('Video call not found, creating new one:', errorMessage);

            // If video call doesn't exist (404), create one
            if (
              errorMessage.includes('404') ||
              errorMessage.toLowerCase().includes('not found') ||
              errorMessage.includes('No video call found')
            ) {
              const videoCallData = {
                candidate_id: interview.candidate?.id || interview.candidate_id,
                scheduled_at: interview.scheduled_start || new Date().toISOString(),
                transcription_enabled: true,
                transcription_language: 'ja',
              };

              console.log('Creating video call with data:', videoCallData);
              console.log('Interview data:', interview);

              const newVideoCall = await apiClient.post<VideoCall>(
                `/api/interviews/${interviewId}/video-call`,
                videoCallData
              );

              setVideoCallId(newVideoCall.data.id.toString());
              showToast({
                type: 'success',
                title: 'Video Call Created',
                message: 'Video call session has been created for this interview',
              });
            } else {
              throw new Error(`Failed to access video call: ${errorMessage}`);
            }
          }
        } catch (videoCallError) {
          console.error('Video call error:', videoCallError);
          const errorMessage =
            videoCallError instanceof Error
              ? videoCallError.message
              : 'Failed to initialize video call';
          showToast({
            type: 'error',
            title: 'Video Call Error',
            message: errorMessage,
          });
        }
      } catch (err) {
        console.error('Error fetching interview:', err);
        setError(err instanceof Error ? err.message : 'Failed to fetch interview details');
      } finally {
        setLoading(false);
      }
    };

    fetchInterview();
  }, [interviewId, showToast]);

  if (loading) {
    return (
      <AppLayout>
        <div className="min-h-screen bg-gray-900 flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white mx-auto mb-4"></div>
            <span className="text-white">Setting up video call...</span>
          </div>
        </div>
      </AppLayout>
    );
  }

  if (error || !interview) {
    return (
      <AppLayout>
        <div className="min-h-screen bg-gray-900 flex items-center justify-center">
          <div className="text-center">
            <AlertCircle className="h-12 w-12 text-red-400 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-white mb-2">Cannot Start Video Call</h2>
            <p className="text-gray-300 mb-4">
              {error || 'Unable to initialize video call for this interview.'}
            </p>
            <Link
              href={interviewId ? `/interviews/${interviewId}` : '/interviews'}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg inline-flex items-center gap-2"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Interview
            </Link>
          </div>
        </div>
      </AppLayout>
    );
  }

  if (!videoCallId) {
    return (
      <AppLayout>
        <div className="min-h-screen bg-gray-900 flex items-center justify-center">
          <div className="text-center">
            <AlertCircle className="h-12 w-12 text-yellow-400 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-white mb-2">Video Call Not Ready</h2>
            <p className="text-gray-300 mb-4">The video call session is being prepared...</p>
            <Link
              href={`/interviews/${interviewId}`}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg inline-flex items-center gap-2"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Interview
            </Link>
          </div>
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout>
      <div className="h-screen bg-gray-900">
        {/* Header with interview context */}
        <div className="bg-gray-800 border-b border-gray-700 px-4 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link
                href={`/interviews/${interviewId}`}
                className="text-gray-400 hover:text-white p-1 rounded"
              >
                <ArrowLeft className="h-5 w-5" />
              </Link>
              <div>
                <h1 className="text-white font-semibold">{interview.title}</h1>
                <p className="text-gray-400 text-sm">
                  {interview.position_title && `${interview.position_title} • `}
                  Video Interview
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Video Call Room */}
        <div className="h-full">
          <VideoCallRoom callId={videoCallId} />
        </div>
      </div>
    </AppLayout>
  );
}

export default function VideoCallPage() {
  return (
    <ProtectedRoute>
      <VideoCallContent />
    </ProtectedRoute>
  );
}
