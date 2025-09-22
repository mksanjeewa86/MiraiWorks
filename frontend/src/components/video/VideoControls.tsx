import React from 'react';
import { Button } from '../ui/Button';
import {
  MicrophoneIcon,
  VideoCameraIcon,
  ComputerDesktopIcon,
  PhoneXMarkIcon,
  DocumentTextIcon,
  ChatBubbleLeftRightIcon,
  ArrowsPointingOutIcon,
  ArrowsPointingInIcon,
} from '@heroicons/react/24/outline';
import {
  MicrophoneIcon as MicrophoneIconSolid,
  VideoCameraIcon as VideoCameraIconSolid,
} from '@heroicons/react/24/solid';

interface VideoControlsProps {
  isMuted: boolean;
  isVideoOn: boolean;
  isScreenSharing: boolean;
  onToggleAudio: () => void;
  onToggleVideo: () => void;
  onStartScreenShare: () => void;
  onStopScreenShare: () => void;
  onEndCall: () => void;
  onToggleTranscription: () => void;
  showTranscription: boolean;
  onToggleChat: () => void;
  showChat: boolean;
  onToggleFullScreen: () => void;
  isFullScreen: boolean;
}

export const VideoControls: React.FC<VideoControlsProps> = ({
  isMuted,
  isVideoOn,
  isScreenSharing,
  onToggleAudio,
  onToggleVideo,
  onStartScreenShare,
  onStopScreenShare,
  onEndCall,
  onToggleTranscription,
  showTranscription,
  onToggleChat,
  showChat,
  onToggleFullScreen,
  isFullScreen,
}) => {
  return (
    <div className="flex items-center space-x-4 bg-gray-800 rounded-lg px-6 py-4 shadow-lg">
      {/* Audio Control */}
      <Button
        variant={isMuted ? 'destructive' : 'secondary'}
        size="sm"
        onClick={onToggleAudio}
        className="p-3 rounded-full"
        title={isMuted ? 'Unmute' : 'Mute'}
      >
        {isMuted ? (
          <MicrophoneIcon className="h-5 w-5 text-white" />
        ) : (
          <MicrophoneIconSolid className="h-5 w-5 text-white" />
        )}
      </Button>

      {/* Video Control */}
      <Button
        variant={isVideoOn ? 'secondary' : 'destructive'}
        size="sm"
        onClick={onToggleVideo}
        className="p-3 rounded-full"
        title={isVideoOn ? 'Turn off camera' : 'Turn on camera'}
      >
        {isVideoOn ? (
          <VideoCameraIconSolid className="h-5 w-5 text-white" />
        ) : (
          <VideoCameraIcon className="h-5 w-5 text-white" />
        )}
      </Button>

      {/* Screen Share Control */}
      <Button
        variant={isScreenSharing ? 'primary' : 'secondary'}
        size="sm"
        onClick={isScreenSharing ? onStopScreenShare : onStartScreenShare}
        className="p-3 rounded-full"
        title={isScreenSharing ? 'Stop sharing' : 'Share screen'}
      >
        <ComputerDesktopIcon className="h-5 w-5 text-white" />
      </Button>

      {/* Transcription Toggle */}
      <Button
        variant={showTranscription ? 'primary' : 'secondary'}
        size="sm"
        onClick={onToggleTranscription}
        className="p-3 rounded-full"
        title={showTranscription ? 'Hide transcription' : 'Show transcription'}
      >
        <DocumentTextIcon className="h-5 w-5 text-white" />
      </Button>

      {/* Chat Toggle */}
      <Button
        variant={showChat ? 'primary' : 'secondary'}
        size="sm"
        onClick={onToggleChat}
        className="p-3 rounded-full"
        title={showChat ? 'Hide chat' : 'Show chat'}
      >
        <ChatBubbleLeftRightIcon className="h-5 w-5 text-white" />
      </Button>

      {/* Fullscreen Toggle */}
      <Button
        variant="secondary"
        size="sm"
        onClick={onToggleFullScreen}
        className="p-3 rounded-full"
        title={isFullScreen ? 'Exit fullscreen' : 'Enter fullscreen'}
      >
        {isFullScreen ? (
          <ArrowsPointingInIcon className="h-5 w-5 text-white" />
        ) : (
          <ArrowsPointingOutIcon className="h-5 w-5 text-white" />
        )}
      </Button>

      {/* End Call */}
      <Button
        variant="destructive"
        size="sm"
        onClick={onEndCall}
        className="p-3 rounded-full bg-red-600 hover:bg-red-700"
        title="End call"
      >
        <PhoneXMarkIcon className="h-5 w-5 text-white" />
      </Button>
    </div>
  );
};