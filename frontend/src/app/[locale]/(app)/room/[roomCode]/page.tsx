'use client';

import React, { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { ArrowLeft, AlertCircle, UserCircle } from 'lucide-react';
import Link from 'next/link';
import AppLayout from '@/components/layout/AppLayout';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import { VideoCallRoom } from '@/components/video/VideoCallRoom';
import { useVideoCall } from '@/hooks/useVideoCall';
import { useAuth } from '@/contexts/AuthContext';
import { ROUTES } from '@/routes/config';

function VideoCallRoomContent() {
  const params = useParams();
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');

  const roomCode = typeof params.roomCode === 'string' ? params.roomCode : null;

  // Use the updated hook with room code support
  const {
    videoCall,
    loading: callLoading,
    error: callError,
  } = useVideoCall(roomCode || '', { type: 'roomCode' });

  useEffect(() => {
    if (!roomCode) {
      setError('Invalid room code');
      setLoading(false);
      return;
    }

    // The loading and error handling is managed by the useVideoCall hook
    if (!callLoading) {
      setLoading(false);
      if (callError) {
        setError(callError);
      }
    }
  }, [roomCode, callLoading, callError]);

  if (loading || callLoading) {
    return (
      <AppLayout>
        <div className="min-h-screen bg-gray-900 flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white mx-auto mb-4"></div>
            <span className="text-white">Joining room {roomCode}...</span>
          </div>
        </div>
      </AppLayout>
    );
  }

  if (error || callError || !videoCall) {
    return (
      <AppLayout>
        <div className="min-h-screen bg-gray-900 flex items-center justify-center">
          <div className="text-center">
            <AlertCircle className="h-12 w-12 text-red-400 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-white mb-2">Room Not Found</h2>
            <p className="text-gray-300 mb-4">
              {error ||
                callError ||
                'The room code you entered is invalid or the meeting has ended.'}
            </p>
            <p className="text-gray-400 text-sm mb-4">Room Code: {roomCode}</p>
            <Link
              href={ROUTES.DASHBOARD}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg inline-flex items-center gap-2"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Dashboard
            </Link>
          </div>
        </div>
      </AppLayout>
    );
  }

  // Get participant info
  const isInterviewer = videoCall.interviewer_id === user?.id;
  const participantRole = isInterviewer ? 'Interviewer' : 'Candidate';

  return (
    <AppLayout>
      <div className="h-screen bg-gray-900">
        {/* Header with room context */}
        <div className="bg-gray-800 border-b border-gray-700 px-4 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link href={ROUTES.DASHBOARD} className="text-gray-400 hover:text-white p-1 rounded">
                <ArrowLeft className="h-5 w-5" />
              </Link>
              <div>
                <div className="flex items-center gap-2">
                  <h1 className="text-white font-semibold">Video Interview</h1>
                  <div className="bg-gray-700 px-2 py-1 rounded text-xs text-gray-300">
                    {roomCode}
                  </div>
                </div>
                <p className="text-gray-400 text-sm flex items-center gap-1">
                  <UserCircle className="h-4 w-4" />
                  Joining as {participantRole}
                </p>
              </div>
            </div>
            <div className="text-gray-400 text-sm">Room: {roomCode}</div>
          </div>
        </div>

        {/* Video Call Room */}
        <div className="h-full">
          <VideoCallRoom callId={videoCall.id.toString()} roomCode={roomCode || undefined} />
        </div>
      </div>
    </AppLayout>
  );
}

export default function VideoCallRoomPage() {
  return (
    <ProtectedRoute>
      <VideoCallRoomContent />
    </ProtectedRoute>
  );
}
