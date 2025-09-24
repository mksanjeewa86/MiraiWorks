import React, { useEffect, useRef } from 'react';
import Button from '../ui/button';
import {
  XMarkIcon,
  ArrowsPointingOutIcon,
  ArrowsPointingInIcon,
} from '@heroicons/react/24/outline';

interface ScreenShareViewProps {
  stream: MediaStream | null;
  isSharing: boolean;
  onStopSharing: () => void;
  onToggleFullScreen: () => void;
  isFullScreen: boolean;
  sharerName: string;
}

export const ScreenShareView: React.FC<ScreenShareViewProps> = ({
  stream,
  isSharing,
  onStopSharing,
  onToggleFullScreen,
  isFullScreen,
  sharerName,
}) => {
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    if (stream && videoRef.current) {
      videoRef.current.srcObject = stream;
    }
  }, [stream]);

  if (!isSharing || !stream) {
    return null;
  }

  return (
    <div className={`screen-share-view ${isFullScreen ? 'fullscreen' : ''}`}>
      <div className="relative w-full h-full bg-black">
        {/* Screen Share Video */}
        <video ref={videoRef} autoPlay playsInline className="w-full h-full object-contain" />

        {/* Controls Overlay */}
        <div className="absolute top-4 left-4 right-4 flex justify-between items-center">
          {/* Screen Share Info */}
          <div className="bg-black bg-opacity-75 text-white px-4 py-2 rounded-lg flex items-center space-x-2">
            <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
            <span className="text-sm font-medium">{sharerName}が画面を共有中</span>
          </div>

          {/* Control Buttons */}
          <div className="flex space-x-2">
            {/* Fullscreen Toggle */}
            <Button
              variant="secondary"
              size="sm"
              onClick={onToggleFullScreen}
              className="bg-black bg-opacity-75 hover:bg-opacity-90 text-white"
              title={isFullScreen ? 'フルスクリーン終了' : 'フルスクリーン'}
            >
              {isFullScreen ? (
                <ArrowsPointingInIcon className="h-5 w-5" />
              ) : (
                <ArrowsPointingOutIcon className="h-5 w-5" />
              )}
            </Button>

            {/* Stop Sharing (only for sharer) */}
            <Button
              variant="ghost"
              size="sm"
              onClick={onStopSharing}
              className="bg-red-600 hover:bg-red-700 text-white"
              title="画面共有を停止"
            >
              <XMarkIcon className="h-5 w-5" />
            </Button>
          </div>
        </div>

        {/* Instructions */}
        <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2">
          <div className="bg-black bg-opacity-75 text-white px-4 py-2 rounded-lg text-center">
            <p className="text-sm">画面共有中です。ESCキーでフルスクリーンを終了できます。</p>
          </div>
        </div>
      </div>
    </div>
  );
};
