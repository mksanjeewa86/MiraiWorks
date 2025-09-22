import { useState, useEffect, useRef, useCallback } from 'react';
import { WebRTCState, ConnectionQuality } from '../types/video';

interface UseWebRTCResult extends WebRTCState {
  connect: () => Promise<void>;
  disconnect: () => Promise<void>;
  toggleAudio: () => void;
  toggleVideo: () => void;
  startScreenShare: () => Promise<void>;
  stopScreenShare: () => void;
}

export const useWebRTC = (roomId?: string): UseWebRTCResult => {
  const [state, setState] = useState<WebRTCState>({
    localStream: null,
    remoteStream: null,
    isConnected: false,
    connectionQuality: 'good' as ConnectionQuality,
    isMuted: false,
    isVideoOn: true,
    isScreenSharing: false,
  });

  const peerConnection = useRef<RTCPeerConnection | null>(null);
  const localStreamRef = useRef<MediaStream | null>(null);
  const screenStreamRef = useRef<MediaStream | null>(null);
  const websocket = useRef<WebSocket | null>(null);

  const iceServers = [
    { urls: 'stun:stun.l.google.com:19302' },
    { urls: 'stun:stun1.l.google.com:19302' },
    // Add TURN servers in production
  ];

  const initializePeerConnection = useCallback(() => {
    if (peerConnection.current) return;

    peerConnection.current = new RTCPeerConnection({ iceServers });

    // Handle remote stream
    peerConnection.current.ontrack = (event) => {
      setState(prev => ({
        ...prev,
        remoteStream: event.streams[0]
      }));
    };

    // Handle ICE candidates
    peerConnection.current.onicecandidate = (event) => {
      if (event.candidate && websocket.current?.readyState === WebSocket.OPEN) {
        websocket.current.send(JSON.stringify({
          type: 'ice-candidate',
          candidate: event.candidate,
          roomId
        }));
      }
    };

    // Monitor connection state
    peerConnection.current.onconnectionstatechange = () => {
      const connectionState = peerConnection.current?.connectionState;
      setState(prev => ({
        ...prev,
        isConnected: connectionState === 'connected',
        connectionQuality: getQualityFromState(connectionState)
      }));
    };
  }, [roomId]);

  const getQualityFromState = (state: string | undefined): ConnectionQuality => {
    switch (state) {
      case 'connected': return 'excellent';
      case 'connecting': return 'good';
      case 'disconnected': return 'poor';
      default: return 'fair';
    }
  };

  const getUserMedia = async (video: boolean = true): Promise<MediaStream> => {
    try {
      return await navigator.mediaDevices.getUserMedia({
        video: video ? {
          width: { ideal: 1280 },
          height: { ideal: 720 },
          facingMode: 'user'
        } : false,
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        }
      });
    } catch (error) {
      console.error('Error accessing media devices:', error);
      throw error;
    }
  };

  const connect = async () => {
    try {
      if (!roomId) throw new Error('Room ID is required');

      // Get user media
      const stream = await getUserMedia();
      localStreamRef.current = stream;
      
      setState(prev => ({
        ...prev,
        localStream: stream
      }));

      // Initialize peer connection
      initializePeerConnection();

      // Add local stream to peer connection
      stream.getTracks().forEach(track => {
        peerConnection.current?.addTrack(track, stream);
      });

      // Connect to signaling server
      await connectSignaling();

    } catch (error) {
      console.error('Failed to connect:', error);
      throw error;
    }
  };

  const connectSignaling = async (): Promise<void> => {
    return new Promise((resolve, reject) => {
      const wsUrl = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws/video/${roomId}`;
      websocket.current = new WebSocket(wsUrl);

      websocket.current.onopen = () => {
        console.log('Connected to signaling server');
        resolve();
      };

      websocket.current.onmessage = async (event) => {
        const data = JSON.parse(event.data);
        await handleSignalingMessage(data);
      };

      websocket.current.onerror = (error) => {
        console.error('WebSocket error:', error);
        reject(error);
      };

      websocket.current.onclose = () => {
        console.log('Disconnected from signaling server');
        setState(prev => ({ ...prev, isConnected: false }));
      };
    });
  };

  const handleSignalingMessage = async (data: any) => {
    if (!peerConnection.current) return;

    switch (data.type) {
      case 'offer':
        await peerConnection.current.setRemoteDescription(new RTCSessionDescription(data.offer));
        const answer = await peerConnection.current.createAnswer();
        await peerConnection.current.setLocalDescription(answer);
        websocket.current?.send(JSON.stringify({
          type: 'answer',
          answer,
          roomId
        }));
        break;

      case 'answer':
        await peerConnection.current.setRemoteDescription(new RTCSessionDescription(data.answer));
        break;

      case 'ice-candidate':
        await peerConnection.current.addIceCandidate(new RTCIceCandidate(data.candidate));
        break;

      case 'user-joined':
        // Create offer for new user
        const offer = await peerConnection.current.createOffer();
        await peerConnection.current.setLocalDescription(offer);
        websocket.current?.send(JSON.stringify({
          type: 'offer',
          offer,
          roomId
        }));
        break;
    }
  };

  const disconnect = async () => {
    // Close peer connection
    peerConnection.current?.close();
    peerConnection.current = null;

    // Stop local streams
    localStreamRef.current?.getTracks().forEach(track => track.stop());
    screenStreamRef.current?.getTracks().forEach(track => track.stop());

    // Close websocket
    websocket.current?.close();

    setState({
      localStream: null,
      remoteStream: null,
      isConnected: false,
      connectionQuality: 'good',
      isMuted: false,
      isVideoOn: true,
      isScreenSharing: false,
    });
  };

  const toggleAudio = () => {
    if (localStreamRef.current) {
      const audioTrack = localStreamRef.current.getAudioTracks()[0];
      if (audioTrack) {
        audioTrack.enabled = !audioTrack.enabled;
        setState(prev => ({ ...prev, isMuted: !audioTrack.enabled }));
      }
    }
  };

  const toggleVideo = () => {
    if (localStreamRef.current) {
      const videoTrack = localStreamRef.current.getVideoTracks()[0];
      if (videoTrack) {
        videoTrack.enabled = !videoTrack.enabled;
        setState(prev => ({ ...prev, isVideoOn: videoTrack.enabled }));
      }
    }
  };

  const startScreenShare = async () => {
    try {
      const screenStream = await navigator.mediaDevices.getDisplayMedia({
        video: true,
        audio: true
      });

      screenStreamRef.current = screenStream;

      // Replace video track in peer connection
      if (peerConnection.current) {
        const sender = peerConnection.current.getSenders().find(s => 
          s.track?.kind === 'video'
        );
        
        if (sender) {
          await sender.replaceTrack(screenStream.getVideoTracks()[0]);
        }
      }

      // Handle screen share end
      screenStream.getVideoTracks()[0].onended = () => {
        stopScreenShare();
      };

      setState(prev => ({ 
        ...prev, 
        isScreenSharing: true,
        localStream: screenStream
      }));

    } catch (error) {
      console.error('Failed to start screen share:', error);
      throw error;
    }
  };

  const stopScreenShare = async () => {
    if (screenStreamRef.current) {
      screenStreamRef.current.getTracks().forEach(track => track.stop());
      screenStreamRef.current = null;
    }

    // Restore camera stream
    try {
      const cameraStream = await getUserMedia();
      localStreamRef.current = cameraStream;

      // Replace track in peer connection
      if (peerConnection.current) {
        const sender = peerConnection.current.getSenders().find(s => 
          s.track?.kind === 'video'
        );
        
        if (sender) {
          await sender.replaceTrack(cameraStream.getVideoTracks()[0]);
        }
      }

      setState(prev => ({ 
        ...prev, 
        isScreenSharing: false,
        localStream: cameraStream
      }));

    } catch (error) {
      console.error('Failed to restore camera:', error);
    }
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      disconnect();
    };
  }, []);

  return {
    ...state,
    connect,
    disconnect,
    toggleAudio,
    toggleVideo,
    startScreenShare,
    stopScreenShare,
  };
};