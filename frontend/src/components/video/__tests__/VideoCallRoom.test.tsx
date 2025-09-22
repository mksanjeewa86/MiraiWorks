import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { VideoCallRoom } from '../VideoCallRoom';
import { useVideoCall } from '../../../hooks/useVideoCall';
import { useWebRTC } from '../../../hooks/useWebRTC';
import { useTranscription } from '../../../hooks/useTranscription';

// Mock the hooks
jest.mock('../../../hooks/useVideoCall');
jest.mock('../../../hooks/useWebRTC');
jest.mock('../../../hooks/useTranscription');

const mockUseVideoCall = useVideoCall as jest.MockedFunction<typeof useVideoCall>;
const mockUseWebRTC = useWebRTC as jest.MockedFunction<typeof useWebRTC>;
const mockUseTranscription = useTranscription as jest.MockedFunction<typeof useTranscription>;

const mockVideoCall = {
  id: 1,
  interviewer_id: 1,
  candidate_id: 2,
  scheduled_at: '2024-01-01T10:00:00Z',
  status: 'scheduled' as const,
  room_id: 'test-room-123',
  transcription_enabled: true,
  transcription_language: 'ja',
  created_at: '2024-01-01T09:00:00Z',
  updated_at: '2024-01-01T09:00:00Z',
};

const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
  useParams: () => ({ callId: '1' }),
}));

describe('VideoCallRoom', () => {
  beforeEach(() => {
    jest.clearAllMocks();

    mockUseVideoCall.mockReturnValue({
      videoCall: mockVideoCall,
      loading: false,
      error: null,
      joinCall: jest.fn(),
      endCall: jest.fn(),
      recordConsent: jest.fn(),
      refreshCall: jest.fn(),
    });

    mockUseWebRTC.mockReturnValue({
      localStream: null,
      remoteStream: null,
      isConnected: false,
      connectionQuality: 'good',
      isMuted: false,
      isVideoOn: true,
      isScreenSharing: false,
      connect: jest.fn(),
      disconnect: jest.fn(),
      toggleAudio: jest.fn(),
      toggleVideo: jest.fn(),
      startScreenShare: jest.fn(),
      stopScreenShare: jest.fn(),
    });

    mockUseTranscription.mockReturnValue({
      segments: [],
      isTranscribing: false,
      language: 'ja',
      searchQuery: '',
      highlightedSegments: [],
      setTranscriptionLanguage: jest.fn(),
      startTranscription: jest.fn(),
      stopTranscription: jest.fn(),
      addSegment: jest.fn(),
      searchTranscript: jest.fn(),
      exportTranscript: jest.fn(),
    });
  });

  it('renders video call room correctly', () => {
    render(
      <MemoryRouter>
        <VideoCallRoom callId="1" />
      </MemoryRouter>
    );

    // Should show connection status
    expect(screen.getByText(/転写/)).toBeInTheDocument();
  });

  it('shows loading state', () => {
    mockUseVideoCall.mockReturnValue({
      videoCall: null,
      loading: true,
      error: null,
      joinCall: jest.fn(),
      endCall: jest.fn(),
      recordConsent: jest.fn(),
      refreshCall: jest.fn(),
    });

    render(
      <MemoryRouter>
        <VideoCallRoom callId="1" />
      </MemoryRouter>
    );

    // Should show loading spinner
    expect(screen.getByRole('status', { hidden: true })).toBeInTheDocument();
  });

  it('shows error state when video call not found', () => {
    mockUseVideoCall.mockReturnValue({
      videoCall: null,
      loading: false,
      error: 'Video call not found',
      joinCall: jest.fn(),
      endCall: jest.fn(),
      recordConsent: jest.fn(),
      refreshCall: jest.fn(),
    });

    render(
      <MemoryRouter>
        <VideoCallRoom callId="1" />
      </MemoryRouter>
    );

    expect(screen.getByText('Video call not found')).toBeInTheDocument();
    expect(screen.getByText('Return to Interviews')).toBeInTheDocument();
  });

  it('handles video controls interactions', async () => {
    const mockToggleAudio = jest.fn();
    const mockToggleVideo = jest.fn();
    const mockStartScreenShare = jest.fn();

    mockUseWebRTC.mockReturnValue({
      localStream: null,
      remoteStream: null,
      isConnected: true,
      connectionQuality: 'good',
      isMuted: false,
      isVideoOn: true,
      isScreenSharing: false,
      connect: jest.fn(),
      disconnect: jest.fn(),
      toggleAudio: mockToggleAudio,
      toggleVideo: mockToggleVideo,
      startScreenShare: mockStartScreenShare,
      stopScreenShare: jest.fn(),
    });

    render(
      <MemoryRouter>
        <VideoCallRoom callId="1" />
      </MemoryRouter>
    );

    // Test audio toggle
    const audioButton = screen.getByTitle('Mute');
    fireEvent.click(audioButton);
    expect(mockToggleAudio).toHaveBeenCalled();

    // Test video toggle
    const videoButton = screen.getByTitle('Turn off camera');
    fireEvent.click(videoButton);
    expect(mockToggleVideo).toHaveBeenCalled();

    // Test screen share
    const screenShareButton = screen.getByTitle('Share screen');
    fireEvent.click(screenShareButton);
    expect(mockStartScreenShare).toHaveBeenCalled();
  });

  it('handles transcription panel toggle', () => {
    render(
      <MemoryRouter>
        <VideoCallRoom callId="1" />
      </MemoryRouter>
    );

    // Initially should show transcription panel
    expect(screen.getByText('転写')).toBeInTheDocument();

    // Toggle transcription off
    const transcriptionButton = screen.getByTitle('Hide transcription');
    fireEvent.click(transcriptionButton);

    // Should hide transcription panel
    // (Note: actual implementation may vary based on component structure)
  });

  it('handles chat panel toggle', () => {
    render(
      <MemoryRouter>
        <VideoCallRoom callId="1" />
      </MemoryRouter>
    );

    // Toggle chat on
    const chatButton = screen.getByTitle('Show chat');
    fireEvent.click(chatButton);

    // Should show chat panel
    expect(screen.getByText('チャット')).toBeInTheDocument();
  });

  it('handles fullscreen toggle', () => {
    const mockRequestFullscreen = jest.fn();
    const mockExitFullscreen = jest.fn();

    Object.defineProperty(document.documentElement, 'requestFullscreen', {
      value: mockRequestFullscreen,
      writable: true,
    });

    Object.defineProperty(document, 'exitFullscreen', {
      value: mockExitFullscreen,
      writable: true,
    });

    render(
      <MemoryRouter>
        <VideoCallRoom callId="1" />
      </MemoryRouter>
    );

    const fullscreenButton = screen.getByTitle('Enter fullscreen');
    fireEvent.click(fullscreenButton);

    expect(mockRequestFullscreen).toHaveBeenCalled();
  });

  it('handles end call action', async () => {
    const mockEndCall = jest.fn();
    const mockDisconnect = jest.fn();

    mockUseVideoCall.mockReturnValue({
      videoCall: mockVideoCall,
      loading: false,
      error: null,
      joinCall: jest.fn(),
      endCall: mockEndCall,
      recordConsent: jest.fn(),
      refreshCall: jest.fn(),
    });

    mockUseWebRTC.mockReturnValue({
      localStream: null,
      remoteStream: null,
      isConnected: true,
      connectionQuality: 'good',
      isMuted: false,
      isVideoOn: true,
      isScreenSharing: false,
      connect: jest.fn(),
      disconnect: mockDisconnect,
      toggleAudio: jest.fn(),
      toggleVideo: jest.fn(),
      startScreenShare: jest.fn(),
      stopScreenShare: jest.fn(),
    });

    render(
      <MemoryRouter>
        <VideoCallRoom callId="1" />
      </MemoryRouter>
    );

    const endCallButton = screen.getByTitle('End call');
    fireEvent.click(endCallButton);

    await waitFor(() => {
      expect(mockDisconnect).toHaveBeenCalled();
      expect(mockEndCall).toHaveBeenCalled();
      expect(mockNavigate).toHaveBeenCalledWith('/interviews');
    });
  });

  it('shows recording consent modal when call starts', () => {
    mockUseVideoCall.mockReturnValue({
      videoCall: { ...mockVideoCall, status: 'in_progress' },
      loading: false,
      error: null,
      joinCall: jest.fn(),
      endCall: jest.fn(),
      recordConsent: jest.fn(),
      refreshCall: jest.fn(),
    });

    render(
      <MemoryRouter>
        <VideoCallRoom callId="1" />
      </MemoryRouter>
    );

    expect(screen.getByText('録画と転写の同意')).toBeInTheDocument();
  });

  it('handles consent submission', async () => {
    const mockRecordConsent = jest.fn();

    mockUseVideoCall.mockReturnValue({
      videoCall: { ...mockVideoCall, status: 'in_progress' },
      loading: false,
      error: null,
      joinCall: jest.fn(),
      endCall: jest.fn(),
      recordConsent: mockRecordConsent,
      refreshCall: jest.fn(),
    });

    render(
      <MemoryRouter>
        <VideoCallRoom callId="1" />
      </MemoryRouter>
    );

    // Check the consent checkbox
    const consentCheckbox = screen.getByRole('checkbox');
    fireEvent.click(consentCheckbox);

    // Click consent button
    const consentButton = screen.getByText('同意する');
    fireEvent.click(consentButton);

    await waitFor(() => {
      expect(mockRecordConsent).toHaveBeenCalledWith(true);
    });
  });

  it('handles sending chat messages', () => {
    render(
      <MemoryRouter>
        <VideoCallRoom callId="1" />
      </MemoryRouter>
    );

    // Open chat panel
    const chatButton = screen.getByTitle('Show chat');
    fireEvent.click(chatButton);

    // Type message
    const messageInput = screen.getByPlaceholderText('メッセージを入力...');
    fireEvent.change(messageInput, { target: { value: 'Hello there!' } });

    // Send message
    const sendButton = screen.getByRole('button', { name: /send/i });
    fireEvent.click(sendButton);

    // Should show the message in chat
    expect(screen.getByText('Hello there!')).toBeInTheDocument();
  });

  it('displays transcription segments', () => {
    const mockSegments = [
      {
        id: 1,
        video_call_id: 1,
        speaker_id: 1,
        speaker_name: 'Interviewer',
        segment_text: 'Hello, how are you today?',
        start_time: 10.5,
        end_time: 13.2,
        confidence: 0.95,
        created_at: '2024-01-01T10:00:10Z',
      },
    ];

    mockUseTranscription.mockReturnValue({
      segments: mockSegments,
      isTranscribing: true,
      language: 'ja',
      searchQuery: '',
      highlightedSegments: [],
      setTranscriptionLanguage: jest.fn(),
      startTranscription: jest.fn(),
      stopTranscription: jest.fn(),
      addSegment: jest.fn(),
      searchTranscript: jest.fn(),
      exportTranscript: jest.fn(),
    });

    render(
      <MemoryRouter>
        <VideoCallRoom callId="1" />
      </MemoryRouter>
    );

    expect(screen.getByText('Hello, how are you today?')).toBeInTheDocument();
    expect(screen.getByText('Interviewer')).toBeInTheDocument();
  });

  it('shows screen sharing overlay when active', () => {
    mockUseWebRTC.mockReturnValue({
      localStream: new MediaStream(),
      remoteStream: null,
      isConnected: true,
      connectionQuality: 'good',
      isMuted: false,
      isVideoOn: true,
      isScreenSharing: true,
      connect: jest.fn(),
      disconnect: jest.fn(),
      toggleAudio: jest.fn(),
      toggleVideo: jest.fn(),
      startScreenShare: jest.fn(),
      stopScreenShare: jest.fn(),
    });

    render(
      <MemoryRouter>
        <VideoCallRoom callId="1" />
      </MemoryRouter>
    );

    expect(screen.getByText('Youが画面を共有中')).toBeInTheDocument();
  });
});