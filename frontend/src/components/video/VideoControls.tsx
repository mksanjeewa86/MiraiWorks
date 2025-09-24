import React from 'react';
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
    <div className="flex items-center justify-center gap-3 bg-gray-900/90 backdrop-blur-md rounded-2xl px-8 py-4 shadow-2xl border border-gray-700/50">
      {/* Audio Control */}
      <button
        onClick={onToggleAudio}
        className={`
          relative w-14 h-14 rounded-full transition-all duration-200 ease-in-out
          flex items-center justify-center group
          ${
            isMuted
              ? 'bg-red-500 hover:bg-red-600 shadow-lg shadow-red-500/25'
              : 'bg-gray-700 hover:bg-gray-600 shadow-lg shadow-black/25'
          }
          hover:scale-105 active:scale-95
        `}
        title={isMuted ? 'Unmute' : 'Mute'}
      >
        {isMuted ? (
          <MicrophoneIcon className="h-6 w-6 text-white drop-shadow-sm" />
        ) : (
          <MicrophoneIconSolid className="h-6 w-6 text-white drop-shadow-sm" />
        )}
        {isMuted && (
          <div className="absolute -top-1 -right-1 w-3 h-3 bg-red-400 rounded-full animate-pulse" />
        )}
      </button>

      {/* Video Control */}
      <button
        onClick={onToggleVideo}
        className={`
          relative w-14 h-14 rounded-full transition-all duration-200 ease-in-out
          flex items-center justify-center group
          ${
            !isVideoOn
              ? 'bg-red-500 hover:bg-red-600 shadow-lg shadow-red-500/25'
              : 'bg-gray-700 hover:bg-gray-600 shadow-lg shadow-black/25'
          }
          hover:scale-105 active:scale-95
        `}
        title={isVideoOn ? 'Turn off camera' : 'Turn on camera'}
      >
        {isVideoOn ? (
          <VideoCameraIconSolid className="h-6 w-6 text-white drop-shadow-sm" />
        ) : (
          <VideoCameraIcon className="h-6 w-6 text-white drop-shadow-sm" />
        )}
        {!isVideoOn && (
          <div className="absolute -top-1 -right-1 w-3 h-3 bg-red-400 rounded-full animate-pulse" />
        )}
      </button>

      {/* Screen Share Control */}
      <button
        onClick={isScreenSharing ? onStopScreenShare : onStartScreenShare}
        className={`
          w-14 h-14 rounded-full transition-all duration-200 ease-in-out
          flex items-center justify-center group
          ${
            isScreenSharing
              ? 'bg-blue-500 hover:bg-blue-600 shadow-lg shadow-blue-500/25'
              : 'bg-gray-700 hover:bg-gray-600 shadow-lg shadow-black/25'
          }
          hover:scale-105 active:scale-95
        `}
        title={isScreenSharing ? 'Stop sharing' : 'Share screen'}
      >
        <ComputerDesktopIcon className="h-6 w-6 text-white drop-shadow-sm" />
      </button>

      {/* Divider */}
      <div className="h-8 w-px bg-gray-600 mx-2" />

      {/* Transcription Toggle */}
      <button
        onClick={onToggleTranscription}
        className={`
          w-12 h-12 rounded-xl transition-all duration-200 ease-in-out
          flex items-center justify-center group
          ${
            showTranscription
              ? 'bg-purple-500 hover:bg-purple-600 shadow-lg shadow-purple-500/25'
              : 'bg-gray-700/80 hover:bg-gray-600 shadow-md'
          }
          hover:scale-105 active:scale-95
        `}
        title={showTranscription ? 'Hide transcription' : 'Show transcription'}
      >
        <DocumentTextIcon className="h-5 w-5 text-white drop-shadow-sm" />
      </button>

      {/* Chat Toggle */}
      <button
        onClick={onToggleChat}
        className={`
          w-12 h-12 rounded-xl transition-all duration-200 ease-in-out
          flex items-center justify-center group
          ${
            showChat
              ? 'bg-green-500 hover:bg-green-600 shadow-lg shadow-green-500/25'
              : 'bg-gray-700/80 hover:bg-gray-600 shadow-md'
          }
          hover:scale-105 active:scale-95
        `}
        title={showChat ? 'Hide chat' : 'Show chat'}
      >
        <ChatBubbleLeftRightIcon className="h-5 w-5 text-white drop-shadow-sm" />
      </button>

      {/* Fullscreen Toggle */}
      <button
        onClick={onToggleFullScreen}
        className="
          w-12 h-12 rounded-xl transition-all duration-200 ease-in-out
          flex items-center justify-center group
          bg-gray-700/80 hover:bg-gray-600 shadow-md
          hover:scale-105 active:scale-95
        "
        title={isFullScreen ? 'Exit fullscreen' : 'Enter fullscreen'}
      >
        {isFullScreen ? (
          <ArrowsPointingInIcon className="h-5 w-5 text-white drop-shadow-sm" />
        ) : (
          <ArrowsPointingOutIcon className="h-5 w-5 text-white drop-shadow-sm" />
        )}
      </button>

      {/* Divider */}
      <div className="h-8 w-px bg-gray-600 mx-2" />

      {/* End Call */}
      <button
        onClick={onEndCall}
        className="
          w-14 h-14 rounded-full transition-all duration-200 ease-in-out
          flex items-center justify-center group
          bg-red-500 hover:bg-red-600 shadow-lg shadow-red-500/30
          hover:scale-105 active:scale-95
          ring-2 ring-red-500/20 hover:ring-red-400/40
        "
        title="End call"
      >
        <PhoneXMarkIcon className="h-6 w-6 text-white drop-shadow-sm" />
      </button>
    </div>
  );
};
