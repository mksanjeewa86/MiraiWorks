import React, { forwardRef } from 'react';
import { MicrophoneIcon } from '@heroicons/react/24/solid';

interface ParticipantVideoProps {
  stream: MediaStream | null;
  isLocal: boolean;
  participantName: string;
  isMuted: boolean;
  className?: string;
}

const ParticipantVideo = forwardRef<HTMLVideoElement, ParticipantVideoProps>(
  ({ stream, isLocal, participantName, isMuted, className = '' }, ref) => {
    return (
      <div className={`relative ${className}`}>
        {/* Video Element */}
        <video
          ref={ref}
          autoPlay
          playsInline
          muted={isLocal} // Always mute local video to prevent feedback
          className="w-full h-full object-cover bg-gray-800"
        />

        {/* No Video Placeholder */}
        {!stream && (
          <div className="absolute inset-0 flex items-center justify-center bg-gray-800">
            <div className="text-center text-white">
              <div className="w-16 h-16 bg-gray-600 rounded-full flex items-center justify-center mx-auto mb-2">
                <span className="text-xl font-semibold">
                  {participantName.charAt(0).toUpperCase()}
                </span>
              </div>
              <p className="text-sm">{participantName}</p>
            </div>
          </div>
        )}

        {/* Participant Info Overlay */}
        <div className="absolute bottom-2 left-2 bg-black bg-opacity-50 text-white px-2 py-1 rounded text-sm flex items-center space-x-1">
          <span>{participantName}</span>
          {isMuted && <MicrophoneIcon className="h-4 w-4 text-red-400" />}
        </div>

        {/* Connection Quality Indicator */}
        <div className="absolute top-2 right-2">
          <div className="flex space-x-1">
            <div className="w-1 h-3 bg-green-400 rounded"></div>
            <div className="w-1 h-3 bg-green-400 rounded"></div>
            <div className="w-1 h-3 bg-yellow-400 rounded"></div>
            <div className="w-1 h-3 bg-gray-400 rounded"></div>
          </div>
        </div>
      </div>
    );
  }
);

ParticipantVideo.displayName = 'ParticipantVideo';

export { ParticipantVideo };
