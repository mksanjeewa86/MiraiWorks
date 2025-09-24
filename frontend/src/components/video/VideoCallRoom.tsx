import React, { useEffect, useRef, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Card from '../ui/card';
import Button from '../ui/button';
import { VideoControls } from './VideoControls';
import { ParticipantVideo } from './ParticipantVideo';
import { TranscriptionPanel } from './TranscriptionPanel';
import { ConnectionStatus } from './ConnectionStatus';
import { RecordingConsent } from './RecordingConsent';
import { ChatPanel } from './ChatPanel';
import { ScreenShareView } from './ScreenShareView';
import { useVideoCall } from '../../hooks/useVideoCall';
import { useWebRTC } from '../../hooks/useWebRTC';
import { useTranscription } from '../../hooks/useTranscription';
import { ChatMessage } from '../../types/video';
import { useAuth } from '../../contexts/AuthContext';

interface VideoCallRoomProps {
  callId?: string;
  roomCode?: string;
}

export const VideoCallRoom: React.FC<VideoCallRoomProps> = ({ callId: propCallId, roomCode }) => {
  const { callId: paramCallId } = useParams<{ callId: string }>();
  const router = useRouter();
  const { user } = useAuth();
  const callId = propCallId || paramCallId;

  const [showTranscription, setShowTranscription] = useState(true);
  const [showChat, setShowChat] = useState(false);
  const [showConsentModal, setShowConsentModal] = useState(false);
  const [isFullScreen, setIsFullScreen] = useState(false);
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [hasJoinedCall, setHasJoinedCall] = useState(false);
  const [consentCompleted, setConsentCompleted] = useState(false);

  const localVideoRef = useRef<HTMLVideoElement>(null);
  const remoteVideoRef = useRef<HTMLVideoElement>(null);

  // Custom hooks for video call functionality
  const {
    videoCall,
    loading: callLoading,
    error: callError,
    joinCall,
    endCall,
    recordConsent,
  } = useVideoCall(roomCode || callId, { type: roomCode ? 'roomCode' : 'id' });

  const {
    localStream,
    remoteStream,
    isConnected,
    connectionQuality,
    isMuted,
    isVideoOn,
    isScreenSharing,
    toggleAudio,
    toggleVideo,
    startScreenShare,
    stopScreenShare,
    connect,
    disconnect,
  } = useWebRTC(videoCall?.room_id, user?.id);

  const {
    segments: transcriptionSegments,
    isTranscribing,
    language: transcriptionLanguage,
    setTranscriptionLanguage,
    // startTranscription,
    // stopTranscription,
  } = useTranscription(callId, videoCall?.transcription_enabled);

  // Chat functionality
  const handleSendMessage = (message: string, type: string = 'text') => {
    const newMessage: ChatMessage = {
      id: Date.now().toString(),
      senderId: 1, // Replace with actual current user ID
      senderName: 'You',
      message,
      timestamp: new Date(),
      type: type as 'text' | 'link' | 'code' | 'file',
    };
    setChatMessages((prev) => [...prev, newMessage]);
  };

  // Set up local video stream
  useEffect(() => {
    if (localStream && localVideoRef.current) {
      localVideoRef.current.srcObject = localStream;
    }
  }, [localStream]);

  // Set up remote video stream
  useEffect(() => {
    if (remoteStream && remoteVideoRef.current) {
      remoteVideoRef.current.srcObject = remoteStream;
    }
  }, [remoteStream]);

  // Auto-join call when component mounts
  useEffect(() => {
    if (videoCall && !hasJoinedCall && !isConnected) {
      handleJoinCall();
    }
  }, [videoCall, hasJoinedCall, isConnected]);

  // Show consent modal when call starts
  useEffect(() => {
    if (videoCall && videoCall.status === 'in_progress' && !consentCompleted && !showConsentModal) {
      setShowConsentModal(true);
    }
  }, [videoCall?.status, consentCompleted, showConsentModal]);

  const handleJoinCall = async () => {
    try {
      setHasJoinedCall(true);
      await joinCall();
      await connect();
    } catch (error) {
      console.error('Failed to join call:', error);
      setHasJoinedCall(false);
    }
  };

  const handleEndCall = async () => {
    try {
      await disconnect();
      await endCall();
      router.push('/interviews');
    } catch (error) {
      console.error('Failed to end call:', error);
    }
  };

  const handleConsentSubmit = async (consented: boolean) => {
    try {
      await recordConsent(consented);
      setConsentCompleted(true);
      setShowConsentModal(false);
    } catch (error) {
      console.error('Failed to record consent:', error);
    }
  };

  const toggleFullScreen = () => {
    if (!isFullScreen) {
      document.documentElement.requestFullscreen();
    } else {
      document.exitFullscreen();
    }
    setIsFullScreen(!isFullScreen);
  };

  if (callLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (callError || !videoCall) {
    return (
      <div className="flex items-center justify-center h-screen">
        <Card className="p-8 text-center">
          <h2 className="text-xl font-semibold text-red-600 mb-4">
            {callError || 'Video call not found'}
          </h2>
          <Button onClick={() => router.push('/interviews')}>Return to Interviews</Button>
        </Card>
      </div>
    );
  }

  return (
    <div className={`video-call-room ${isFullScreen ? 'fullscreen' : ''} h-screen bg-gray-900`}>
      {/* Connection Status */}
      <ConnectionStatus
        isConnected={isConnected}
        quality={connectionQuality}
        participantCount={remoteStream ? 2 : 1}
      />

      {/* Main Video Area */}
      <div className="flex h-full">
        {/* Video Grid */}
        <div className={`flex-1 relative ${showTranscription ? 'mr-80' : ''}`}>
          {/* Remote Video (Full Screen) */}
          <div className="w-full h-full relative">
            <ParticipantVideo
              ref={remoteVideoRef}
              stream={remoteStream}
              isLocal={false}
              participantName={videoCall.candidate_id ? 'Candidate' : 'Interviewer'}
              isMuted={false}
              className="w-full h-full object-cover"
            />

            {/* Local Video (Picture-in-Picture) */}
            <div className="absolute top-4 right-4 w-64 h-48 rounded-lg overflow-hidden shadow-lg">
              <ParticipantVideo
                ref={localVideoRef}
                stream={localStream}
                isLocal={true}
                participantName="You"
                isMuted={isMuted}
                className="w-full h-full object-cover"
              />
            </div>

            {/* Screen Share Indicator */}
            {isScreenSharing && (
              <div className="absolute top-4 left-4 bg-red-600 text-white px-3 py-1 rounded-md text-sm">
                Sharing Screen
              </div>
            )}
          </div>

          {/* Video Controls */}
          <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2">
            <VideoControls
              isMuted={isMuted}
              isVideoOn={isVideoOn}
              isScreenSharing={isScreenSharing}
              onToggleAudio={toggleAudio}
              onToggleVideo={toggleVideo}
              onStartScreenShare={startScreenShare}
              onStopScreenShare={stopScreenShare}
              onEndCall={handleEndCall}
              onToggleTranscription={() => setShowTranscription(!showTranscription)}
              showTranscription={showTranscription}
              onToggleChat={() => setShowChat(!showChat)}
              showChat={showChat}
              onToggleFullScreen={toggleFullScreen}
              isFullScreen={isFullScreen}
            />
          </div>
        </div>

        {/* Side Panels */}
        {(showTranscription || showChat) && (
          <div className="w-80 bg-white border-l border-gray-200 flex flex-col">
            {/* Panel Tabs */}
            <div className="flex border-b border-gray-200">
              {videoCall.transcription_enabled && (
                <button
                  onClick={() => {
                    setShowTranscription(true);
                    setShowChat(false);
                  }}
                  className={`flex-1 py-2 px-4 text-sm font-medium ${
                    showTranscription && !showChat
                      ? 'text-blue-600 border-b-2 border-blue-600'
                      : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  転写
                </button>
              )}
              <button
                onClick={() => {
                  setShowChat(true);
                  setShowTranscription(false);
                }}
                className={`flex-1 py-2 px-4 text-sm font-medium ${
                  showChat && !showTranscription
                    ? 'text-blue-600 border-b-2 border-blue-600'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                チャット
              </button>
            </div>

            {/* Panel Content */}
            <div className="flex-1 overflow-hidden">
              {showTranscription && !showChat && videoCall.transcription_enabled && (
                <TranscriptionPanel
                  segments={transcriptionSegments}
                  isTranscribing={isTranscribing}
                  language={transcriptionLanguage}
                  onLanguageChange={setTranscriptionLanguage}
                  callId={callId}
                />
              )}

              {showChat && !showTranscription && (
                <ChatPanel
                  messages={chatMessages}
                  onSendMessage={handleSendMessage}
                  currentUserId={1} // Replace with actual current user ID
                  isVisible={showChat}
                  onToggleVisibility={() => setShowChat(false)}
                />
              )}
            </div>
          </div>
        )}

        {/* Screen Share Overlay */}
        {isScreenSharing && (
          <ScreenShareView
            stream={localStream}
            isSharing={isScreenSharing}
            onStopSharing={stopScreenShare}
            onToggleFullScreen={toggleFullScreen}
            isFullScreen={isFullScreen}
            sharerName="You"
          />
        )}
      </div>

      {/* Recording Consent Modal */}
      {showConsentModal && (
        <RecordingConsent
          onSubmit={handleConsentSubmit}
          onClose={() => setShowConsentModal(false)}
        />
      )}
    </div>
  );
};
