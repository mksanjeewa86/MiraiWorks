import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import Button from '../ui/Button';
import Card from '../ui/Card';
import LoadingSpinner from '../ui/LoadingSpinner';
import { useWebRTCConnection } from '../../hooks/useWebRTCConnection';
import { useMeetingAPI } from '../../hooks/useMeetingAPI';
import type { Meeting, MeetingJoinResponse, MeetingParticipant } from '../../types';
import { ParticipantStatus } from '../../types';

interface VideoCallComponentProps {
  roomId?: string;
  accessCode?: string;
  onLeave?: () => void;
}

export default function VideoCallComponent({ roomId: propRoomId, accessCode, onLeave }: VideoCallComponentProps) {
  const { roomId: paramRoomId } = useParams<{ roomId: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();
  
  const roomId = propRoomId || paramRoomId;
  
  // State management
  const [meeting, setMeeting] = useState<Meeting | null>(null);
  const [participants, setParticipants] = useState<MeetingParticipant[]>([]);
  const [isJoined, setIsJoined] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [chatMessages, setChatMessages] = useState<Array<{
    sender_id: number;
    message: string;
    timestamp: string;
    sender_name: string;
  }>>([]);
  const [newChatMessage, setNewChatMessage] = useState('');
  const [showChat, setShowChat] = useState(false);
  const [isRecording, setIsRecording] = useState(false);

  // Media state
  const [isAudioMuted, setIsAudioMuted] = useState(false);
  const [isVideoMuted, setIsVideoMuted] = useState(false);
  const [isScreenSharing, setIsScreenSharing] = useState(false);

  // Refs for video elements
  const localVideoRef = useRef<HTMLVideoElement>(null);
  const remoteVideosRef = useRef<Map<number, HTMLVideoElement>>(new Map());

  // Custom hooks
  const { joinMeeting, leaveMeeting } = useMeetingAPI();
  const {
    localStream,
    remoteStreams,
    connectionState,
    connect,
    disconnect,
    toggleAudio,
    toggleVideo,
    startScreenShare,
    stopScreenShare,
    sendChatMessage
  } = useWebRTCConnection({
    roomId: roomId || '',
    onParticipantJoined: handleParticipantJoined,
    onParticipantLeft: handleParticipantLeft,
    onChatMessage: handleChatMessage,
    onRecordingStatusChange: handleRecordingStatusChange
  });

  // Join meeting on mount
  useEffect(() => {
    if (!roomId || !user) return;

    const joinMeetingRoom = async () => {
      try {
        setIsLoading(true);
        const response: MeetingJoinResponse = await joinMeeting(roomId, accessCode);
        
        if (response.success) {
          setMeeting(response.meeting);
          setParticipants(response.meeting.participants);
          
          // Connect to WebRTC
          await connect(response.turn_servers);
          setIsJoined(true);
        } else {
          setError(response.error || 'Failed to join meeting');
        }
      } catch (err: any) {
        setError(err.message || 'Failed to join meeting');
      } finally {
        setIsLoading(false);
      }
    };

    joinMeetingRoom();

    // Cleanup on unmount
    return () => {
      handleLeave();
    };
  }, [roomId, accessCode, user]);

  // Update local video when stream changes
  useEffect(() => {
    if (localVideoRef.current && localStream) {
      localVideoRef.current.srcObject = localStream;
    }
  }, [localStream]);

  // Handle remote stream changes
  useEffect(() => {
    remoteStreams.forEach((stream, userId) => {
      const videoElement = remoteVideosRef.current.get(userId);
      if (videoElement) {
        videoElement.srcObject = stream;
      }
    });
  }, [remoteStreams]);

  // Event handlers
  function handleParticipantJoined(userId: number) {
    // Update participants list
    setParticipants(prev => 
      prev.map(p => 
        p.user_id === userId 
          ? { ...p, status: ParticipantStatus.JOINED }
          : p
      )
    );
  }

  function handleParticipantLeft(userId: number) {
    setParticipants(prev => 
      prev.map(p => 
        p.user_id === userId 
          ? { ...p, status: ParticipantStatus.LEFT }
          : p
      )
    );
  }

  function handleChatMessage(message: { sender_id: number; message: string; timestamp: string }) {
    const participant = participants.find(p => p.user_id === message.sender_id);
    setChatMessages(prev => [...prev, {
      ...message,
      sender_name: participant?.user?.full_name || 'Unknown'
    }]);
  }

  function handleRecordingStatusChange(isRecording: boolean) {
    setIsRecording(isRecording);
  }

  const handleLeave = useCallback(async () => {
    if (!roomId) return;

    try {
      // Disconnect WebRTC
      await disconnect();
      
      // Leave meeting via API
      if (isJoined) {
        await leaveMeeting(roomId);
      }
      
      setIsJoined(false);
      
      // Navigate away or call onLeave callback
      if (onLeave) {
        onLeave();
      } else {
        navigate('/dashboard');
      }
    } catch (err) {
      console.error('Error leaving meeting:', err);
      // Still navigate away even if API call fails
      if (onLeave) {
        onLeave();
      } else {
        navigate('/dashboard');
      }
    }
  }, [roomId, isJoined, disconnect, leaveMeeting, navigate, onLeave]);

  const handleToggleAudio = async () => {
    const newState = await toggleAudio();
    setIsAudioMuted(!newState);
  };

  const handleToggleVideo = async () => {
    const newState = await toggleVideo();
    setIsVideoMuted(!newState);
  };

  const handleToggleScreenShare = async () => {
    if (isScreenSharing) {
      await stopScreenShare();
      setIsScreenSharing(false);
    } else {
      const success = await startScreenShare();
      setIsScreenSharing(success);
    }
  };

  const handleSendChatMessage = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newChatMessage.trim()) return;
    
    sendChatMessage(newChatMessage.trim());
    setNewChatMessage('');
  };

  const getParticipantName = (userId: number) => {
    const participant = participants.find(p => p.user_id === userId);
    return participant?.user?.full_name || 'Unknown';
  };

  const createVideoElement = useCallback((userId: number) => (
    <video
      key={userId}
      ref={(el) => {
        if (el) {
          remoteVideosRef.current.set(userId, el);
        } else {
          remoteVideosRef.current.delete(userId);
        }
      }}
      autoPlay
      playsInline
      className="w-full h-full object-cover rounded-lg"
    />
  ), []);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-900">
        <Card className="p-8 text-center">
          <LoadingSpinner className="w-8 h-8 mb-4 mx-auto" />
          <p className="text-gray-600">Joining meeting...</p>
        </Card>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-900">
        <Card className="p-8 text-center max-w-md">
          <div className="text-red-500 text-4xl mb-4">⚠️</div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Unable to Join Meeting</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <Button onClick={() => navigate('/dashboard')}>
            Return to Dashboard
          </Button>
        </Card>
      </div>
    );
  }

  return (
    <div className="h-screen bg-gray-900 flex flex-col">
      {/* Header */}
      <div className="bg-gray-800 text-white p-4 flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <h1 className="text-xl font-semibold">{meeting?.title}</h1>
          <div className="flex items-center space-x-2">
            <div className={`w-2 h-2 rounded-full ${
              connectionState === 'connected' ? 'bg-green-500' : 'bg-red-500'
            }`} />
            <span className="text-sm text-gray-300">
              {connectionState === 'connected' ? 'Connected' : 'Connecting...'}
            </span>
          </div>
          {isRecording && (
            <div className="flex items-center space-x-1 text-red-400">
              <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse" />
              <span className="text-sm">Recording</span>
            </div>
          )}
        </div>
        
        <div className="flex items-center space-x-2">
          <span className="text-sm text-gray-300">
            {participants.filter(p => p.status === ParticipantStatus.JOINED).length} participants
          </span>
          <Button 
            variant="outline" 
            size="sm" 
            onClick={() => setShowChat(!showChat)}
            className="text-white border-gray-600 hover:bg-gray-700"
          >
            💬 Chat
          </Button>
        </div>
      </div>

      {/* Video Area */}
      <div className="flex-1 flex">
        {/* Main video area */}
        <div className="flex-1 p-4">
          <div className="grid grid-cols-2 gap-4 h-full">
            {/* Local video */}
            <div className="relative bg-gray-800 rounded-lg overflow-hidden">
              <video
                ref={localVideoRef}
                autoPlay
                playsInline
                muted
                className="w-full h-full object-cover"
              />
              <div className="absolute bottom-2 left-2 bg-black bg-opacity-50 text-white px-2 py-1 rounded text-sm">
                You {isVideoMuted && '(Video Off)'}
              </div>
              {isVideoMuted && (
                <div className="absolute inset-0 bg-gray-700 flex items-center justify-center">
                  <div className="w-16 h-16 bg-gray-600 rounded-full flex items-center justify-center">
                    <span className="text-white text-xl">{user?.full_name?.charAt(0)}</span>
                  </div>
                </div>
              )}
            </div>

            {/* Remote videos */}
            {Array.from(remoteStreams.keys()).map(userId => (
              <div key={userId} className="relative bg-gray-800 rounded-lg overflow-hidden">
                {createVideoElement(userId)}
                <div className="absolute bottom-2 left-2 bg-black bg-opacity-50 text-white px-2 py-1 rounded text-sm">
                  {getParticipantName(userId)}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Chat panel */}
        {showChat && (
          <div className="w-80 bg-white border-l border-gray-300 flex flex-col">
            <div className="p-4 border-b border-gray-200">
              <h3 className="font-semibold text-gray-900">Meeting Chat</h3>
            </div>
            
            {/* Chat messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-3">
              {chatMessages.map((msg, index) => (
                <div key={index} className="break-words">
                  <div className="flex items-center space-x-2 mb-1">
                    <span className="text-sm font-medium text-gray-900">{msg.sender_name}</span>
                    <span className="text-xs text-gray-500">
                      {new Date(msg.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                  <p className="text-sm text-gray-700 pl-2 border-l-2 border-gray-200">
                    {msg.message}
                  </p>
                </div>
              ))}
            </div>

            {/* Chat input */}
            <form onSubmit={handleSendChatMessage} className="p-4 border-t border-gray-200">
              <div className="flex space-x-2">
                <input
                  type="text"
                  value={newChatMessage}
                  onChange={(e) => setNewChatMessage(e.target.value)}
                  placeholder="Type a message..."
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <Button type="submit" size="sm" disabled={!newChatMessage.trim()}>
                  Send
                </Button>
              </div>
            </form>
          </div>
        )}
      </div>

      {/* Controls */}
      <div className="bg-gray-800 p-4">
        <div className="flex items-center justify-center space-x-4">
          <Button
            onClick={handleToggleAudio}
            variant={isAudioMuted ? "primary" : "outline"}
            size="lg"
            className={`w-12 h-12 rounded-full ${
              isAudioMuted ? 'bg-red-500 hover:bg-red-600 text-white' : 'text-white border-gray-600 hover:bg-gray-700'
            }`}
          >
            {isAudioMuted ? '🔇' : '🔊'}
          </Button>

          <Button
            onClick={handleToggleVideo}
            variant={isVideoMuted ? "primary" : "outline"}
            size="lg"
            className={`w-12 h-12 rounded-full ${
              isVideoMuted ? 'bg-red-500 hover:bg-red-600 text-white' : 'text-white border-gray-600 hover:bg-gray-700'
            }`}
          >
            {isVideoMuted ? '📷' : '📹'}
          </Button>

          <Button
            onClick={handleToggleScreenShare}
            variant={isScreenSharing ? "primary" : "outline"}
            size="lg"
            className={`w-12 h-12 rounded-full ${
              isScreenSharing ? 'bg-blue-500 hover:bg-blue-600 text-white' : 'text-white border-gray-600 hover:bg-gray-700'
            }`}
          >
            🖥️
          </Button>

          <Button
            onClick={handleLeave}
            variant="primary"
            size="lg"
            className="w-12 h-12 rounded-full bg-red-500 hover:bg-red-600 text-white"
          >
            📞
          </Button>
        </div>
      </div>
    </div>
  );
}