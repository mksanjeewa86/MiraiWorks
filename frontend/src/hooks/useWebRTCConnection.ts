import { useState, useEffect, useRef, useCallback } from 'react';
import { useAuth } from '../contexts/AuthContext';
import type { RTCIceServer, WebRTCSignal } from '../types';

interface UseWebRTCConnectionOptions {
  roomId: string;
  onParticipantJoined?: (userId: number) => void;
  onParticipantLeft?: (userId: number) => void;
  onChatMessage?: (message: { sender_id: number; message: string; timestamp: string }) => void;
  onRecordingStatusChange?: (isRecording: boolean) => void;
}

interface PeerConnection {
  connection: RTCPeerConnection;
  userId: number;
}

export function useWebRTCConnection(options: UseWebRTCConnectionOptions) {
  const { user } = useAuth();
  const {
    roomId,
    onParticipantJoined,
    onParticipantLeft, 
    onChatMessage,
    onRecordingStatusChange
  } = options;

  // State
  const [localStream, setLocalStream] = useState<MediaStream | null>(null);
  const [remoteStreams, setRemoteStreams] = useState<Map<number, MediaStream>>(new Map());
  const [connectionState, setConnectionState] = useState<'disconnected' | 'connecting' | 'connected'>('disconnected');
  const [isAudioEnabled, setIsAudioEnabled] = useState(true);
  const [isVideoEnabled, setIsVideoEnabled] = useState(true);

  // Refs
  const wsRef = useRef<WebSocket | null>(null);
  const peerConnections = useRef<Map<number, PeerConnection>>(new Map());
  const localStreamRef = useRef<MediaStream | null>(null);
  const turnServersRef = useRef<RTCIceServer[]>([]);

  // WebRTC configuration
  const rtcConfig: RTCConfiguration = {
    iceServers: [
      { urls: 'stun:stun.l.google.com:19302' },
      // TURN servers will be added dynamically
    ]
  };

  // Initialize media stream
  const initializeLocalStream = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 1280 },
          height: { ideal: 720 },
          facingMode: 'user'
        },
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        }
      });

      setLocalStream(stream);
      localStreamRef.current = stream;
      return stream;
    } catch (error) {
      console.error('Failed to get user media:', error);
      throw error;
    }
  }, []);

  // Create peer connection for a user
  const createPeerConnection = useCallback((userId: number): RTCPeerConnection => {
    const config = {
      ...rtcConfig,
      iceServers: [...rtcConfig.iceServers!, ...turnServersRef.current]
    };

    const pc = new RTCPeerConnection(config);

    // Add local stream tracks
    if (localStreamRef.current) {
      localStreamRef.current.getTracks().forEach(track => {
        pc.addTrack(track, localStreamRef.current!);
      });
    }

    // Handle remote stream
    pc.ontrack = (event) => {
      const [remoteStream] = event.streams;
      setRemoteStreams(prev => {
        const newMap = new Map(prev);
        newMap.set(userId, remoteStream);
        return newMap;
      });
    };

    // Handle ICE candidates
    pc.onicecandidate = (event) => {
      if (event.candidate && wsRef.current) {
        sendSignal({
          type: 'ice-candidate',
          data: event.candidate,
          target_user_id: userId,
          room_id: roomId
        });
      }
    };

    // Handle connection state changes
    pc.onconnectionstatechange = () => {
      console.log(`Peer connection state with ${userId}:`, pc.connectionState);
      
      if (pc.connectionState === 'failed') {
        // Try to restart ICE
        pc.restartIce();
      }
    };

    // Store peer connection
    peerConnections.current.set(userId, { connection: pc, userId });

    return pc;
  }, [roomId]);

  // Send WebRTC signal
  const sendSignal = useCallback((signal: WebRTCSignal) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(signal));
    }
  }, []);

  // Handle WebSocket messages
  const handleWebSocketMessage = useCallback(async (event: MessageEvent) => {
    try {
      const message = JSON.parse(event.data);
      const { type, data, sender_id } = message;

      switch (type) {
        case 'meeting_joined':
          setConnectionState('connected');
          if (data.participants) {
            // Create peer connections for existing participants
            data.participants.forEach((participantId: number) => {
              if (participantId !== user?.id) {
                createPeerConnection(participantId);
              }
            });
          }
          break;

        case 'user_joined':
          if (data.user_id !== user?.id) {
            // Create offer for new participant
            const pc = createPeerConnection(data.user_id);
            try {
              const offer = await pc.createOffer();
              await pc.setLocalDescription(offer);
              
              sendSignal({
                type: 'offer',
                data: offer,
                target_user_id: data.user_id,
                room_id: roomId
              });
            } catch (error) {
              console.error('Failed to create offer:', error);
            }
            
            onParticipantJoined?.(data.user_id);
          }
          break;

        case 'user_left':
          if (data.user_id !== user?.id) {
            // Clean up peer connection
            const peerData = peerConnections.current.get(data.user_id);
            if (peerData) {
              peerData.connection.close();
              peerConnections.current.delete(data.user_id);
            }
            
            // Remove remote stream
            setRemoteStreams(prev => {
              const newMap = new Map(prev);
              newMap.delete(data.user_id);
              return newMap;
            });
            
            onParticipantLeft?.(data.user_id);
          }
          break;

        case 'offer':
          if (sender_id !== user?.id) {
            const pc = peerConnections.current.get(sender_id)?.connection || createPeerConnection(sender_id);
            try {
              await pc.setRemoteDescription(new RTCSessionDescription(data));
              const answer = await pc.createAnswer();
              await pc.setLocalDescription(answer);
              
              sendSignal({
                type: 'answer',
                data: answer,
                target_user_id: sender_id,
                room_id: roomId
              });
            } catch (error) {
              console.error('Failed to handle offer:', error);
            }
          }
          break;

        case 'answer':
          if (sender_id !== user?.id) {
            const peerData = peerConnections.current.get(sender_id);
            if (peerData) {
              try {
                await peerData.connection.setRemoteDescription(new RTCSessionDescription(data));
              } catch (error) {
                console.error('Failed to handle answer:', error);
              }
            }
          }
          break;

        case 'ice-candidate':
          if (sender_id !== user?.id) {
            const peerData = peerConnections.current.get(sender_id);
            if (peerData && peerData.connection.remoteDescription) {
              try {
                await peerData.connection.addIceCandidate(new RTCIceCandidate(data));
              } catch (error) {
                console.error('Failed to add ICE candidate:', error);
              }
            }
          }
          break;

        case 'chat_message':
          onChatMessage?.(data);
          break;

        case 'recording_started':
          onRecordingStatusChange?.(true);
          break;

        case 'recording_stopped':
          onRecordingStatusChange?.(false);
          break;

        case 'participant_muted':
        case 'participant_unmuted':
          // Handle participant mute/unmute status
          console.log(`Participant ${data.user_id} ${type}:`, data);
          break;

        case 'screen_share_start':
        case 'screen_share_stop':
          // Handle screen sharing events
          console.log(`Screen share ${type} by ${data.user_id}`);
          break;

        case 'error':
          console.error('WebSocket error:', data.message);
          break;

        default:
          console.log('Unknown WebSocket message type:', type);
      }
    } catch (error) {
      console.error('Failed to handle WebSocket message:', error);
    }
  }, [user?.id, roomId, createPeerConnection, sendSignal, onParticipantJoined, onParticipantLeft, onChatMessage, onRecordingStatusChange]);

  // Connect to meeting
  const connect = useCallback(async (turnServers: RTCIceServer[] = []) => {
    if (!user || !roomId) return;

    try {
      setConnectionState('connecting');
      turnServersRef.current = turnServers;

      // Initialize local stream
      await initializeLocalStream();

      // Connect WebSocket
      const token = localStorage.getItem('accessToken');
      const wsUrl = `${import.meta.env.VITE_MEETINGS_WS_URL}/ws/meetings/${roomId}?token=${token}`;
      
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('WebSocket connected');
      };

      ws.onmessage = handleWebSocketMessage;

      ws.onclose = () => {
        console.log('WebSocket disconnected');
        setConnectionState('disconnected');
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setConnectionState('disconnected');
      };

    } catch (error) {
      console.error('Failed to connect:', error);
      setConnectionState('disconnected');
      throw error;
    }
  }, [user, roomId, initializeLocalStream, handleWebSocketMessage]);

  // Disconnect from meeting
  const disconnect = useCallback(async () => {
    // Close WebSocket
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    // Close all peer connections
    peerConnections.current.forEach(({ connection }) => {
      connection.close();
    });
    peerConnections.current.clear();

    // Stop local stream
    if (localStreamRef.current) {
      localStreamRef.current.getTracks().forEach(track => track.stop());
      localStreamRef.current = null;
    }

    // Reset state
    setLocalStream(null);
    setRemoteStreams(new Map());
    setConnectionState('disconnected');
  }, []);

  // Toggle audio
  const toggleAudio = useCallback(async (): Promise<boolean> => {
    if (localStreamRef.current) {
      const audioTrack = localStreamRef.current.getAudioTracks()[0];
      if (audioTrack) {
        audioTrack.enabled = !audioTrack.enabled;
        setIsAudioEnabled(audioTrack.enabled);
        
        // Notify other participants
        sendSignal({
          type: audioTrack.enabled ? 'unmute_audio' : 'mute_audio',
          data: {},
          room_id: roomId
        });
        
        return audioTrack.enabled;
      }
    }
    return false;
  }, [roomId, sendSignal]);

  // Toggle video
  const toggleVideo = useCallback(async (): Promise<boolean> => {
    if (localStreamRef.current) {
      const videoTrack = localStreamRef.current.getVideoTracks()[0];
      if (videoTrack) {
        videoTrack.enabled = !videoTrack.enabled;
        setIsVideoEnabled(videoTrack.enabled);
        
        // Notify other participants
        sendSignal({
          type: videoTrack.enabled ? 'unmute_video' : 'mute_video',
          data: {},
          room_id: roomId
        });
        
        return videoTrack.enabled;
      }
    }
    return false;
  }, [roomId, sendSignal]);

  // Start screen sharing
  const startScreenShare = useCallback(async (): Promise<boolean> => {
    try {
      const screenStream = await navigator.mediaDevices.getDisplayMedia({
        video: true,
        audio: true
      });

      // Replace video track in all peer connections
      const videoTrack = screenStream.getVideoTracks()[0];
      peerConnections.current.forEach(({ connection }) => {
        const sender = connection.getSenders().find(s => 
          s.track && s.track.kind === 'video'
        );
        if (sender) {
          sender.replaceTrack(videoTrack);
        }
      });

      // Notify participants
      sendSignal({
        type: 'screen_share_start',
        data: {},
        room_id: roomId
      });

      // Handle screen share ending
      videoTrack.onended = () => {
        stopScreenShare();
      };

      return true;
    } catch (error) {
      console.error('Failed to start screen sharing:', error);
      return false;
    }
  }, [roomId, sendSignal]);

  // Stop screen sharing
  const stopScreenShare = useCallback(async () => {
    try {
      // Get camera stream back
      const cameraStream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: false
      });

      // Replace screen share track with camera track
      const videoTrack = cameraStream.getVideoTracks()[0];
      peerConnections.current.forEach(({ connection }) => {
        const sender = connection.getSenders().find(s => 
          s.track && s.track.kind === 'video'
        );
        if (sender) {
          sender.replaceTrack(videoTrack);
        }
      });

      // Update local stream
      if (localStreamRef.current) {
        const audioTrack = localStreamRef.current.getAudioTracks()[0];
        const newStream = new MediaStream([videoTrack]);
        if (audioTrack) {
          newStream.addTrack(audioTrack);
        }
        localStreamRef.current = newStream;
        setLocalStream(newStream);
      }

      // Notify participants
      sendSignal({
        type: 'screen_share_stop',
        data: {},
        room_id: roomId
      });

    } catch (error) {
      console.error('Failed to stop screen sharing:', error);
    }
  }, [roomId, sendSignal]);

  // Send chat message
  const sendChatMessage = useCallback((message: string) => {
    sendSignal({
      type: 'chat_message',
      data: { message },
      room_id: roomId
    });
  }, [roomId, sendSignal]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  return {
    localStream,
    remoteStreams,
    connectionState,
    isAudioEnabled,
    isVideoEnabled,
    connect,
    disconnect,
    toggleAudio,
    toggleVideo,
    startScreenShare,
    stopScreenShare,
    sendChatMessage
  };
}