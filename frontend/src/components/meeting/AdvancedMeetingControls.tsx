import React, { useState, useRef } from 'react';
import VirtualBackgroundPanel from './VirtualBackgroundPanel';
import ExpressionViewer from './ExpressionViewer';

interface AdvancedMeetingControlsProps {
  localStream?: MediaStream;
  isHost?: boolean;
  isRecording?: boolean;
  onStreamChange?: (stream: MediaStream | null) => void;
  onRecordingToggle?: () => void;
  onMeetingQualityChange?: (quality: 'auto' | 'high' | 'medium' | 'low') => void;
}

interface MeetingQuality {
  video: {
    resolution: string;
    frameRate: number;
    bitrate: number;
  };
  audio: {
    bitrate: number;
    echoCancellation: boolean;
    noiseSuppression: boolean;
  };
  connection: {
    type: string;
    rtt: number;
    bandwidth: number;
  };
}

const AdvancedMeetingControls: React.FC<AdvancedMeetingControlsProps> = ({
  localStream,
  isHost = false,
  isRecording = false,
  onStreamChange,
  onRecordingToggle,
  onMeetingQualityChange
}) => {
  const [showVirtualBg, setShowVirtualBg] = useState(false);
  const [showExpressions, setShowExpressions] = useState(false);
  const [showQualityPanel, setShowQualityPanel] = useState(false);
  const [showAdvancedSettings, setShowAdvancedSettings] = useState(false);
  
  const [meetingQuality, setMeetingQuality] = useState<MeetingQuality>({
    video: {
      resolution: '1280x720',
      frameRate: 30,
      bitrate: 1000
    },
    audio: {
      bitrate: 128,
      echoCancellation: true,
      noiseSuppression: true
    },
    connection: {
      type: 'P2P',
      rtt: 45,
      bandwidth: 2.5
    }
  });

  const [selectedQuality, setSelectedQuality] = useState<'auto' | 'high' | 'medium' | 'low'>('auto');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleQualityChange = (quality: 'auto' | 'high' | 'medium' | 'low') => {
    setSelectedQuality(quality);
    onMeetingQualityChange?.(quality);

    // Update local quality settings based on selection
    const qualitySettings = {
      high: { resolution: '1920x1080', frameRate: 30, bitrate: 2000 },
      medium: { resolution: '1280x720', frameRate: 30, bitrate: 1000 },
      low: { resolution: '640x480', frameRate: 15, bitrate: 500 },
      auto: { resolution: '1280x720', frameRate: 30, bitrate: 1000 }
    };

    setMeetingQuality(prev => ({
      ...prev,
      video: { ...prev.video, ...qualitySettings[quality] }
    }));
  };

  const handleFileShare = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // File size limit (10MB)
    if (file.size > 10 * 1024 * 1024) {
      alert('File size must be less than 10MB');
      return;
    }

    try {
      // In a real implementation, this would upload the file and share it
      // For now, we'll just log it
      console.log('Sharing file:', file.name, file.size, 'bytes');
      
      // Reset input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (error) {
      console.error('Error sharing file:', error);
      alert('Failed to share file');
    }
  };

  const getConnectionQualityColor = (rtt: number): string => {
    if (rtt < 50) return 'text-green-600';
    if (rtt < 150) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getConnectionQualityLabel = (rtt: number): string => {
    if (rtt < 50) return 'Excellent';
    if (rtt < 150) return 'Good';
    return 'Poor';
  };


  return (
    <div className="space-y-4">
      {/* Main Advanced Controls Bar */}
      <div className="bg-white rounded-lg shadow-sm border p-4">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Advanced Controls</h3>
          <button
            onClick={() => setShowAdvancedSettings(!showAdvancedSettings)}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </button>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {/* Virtual Backgrounds */}
          <button
            onClick={() => setShowVirtualBg(true)}
            className="flex flex-col items-center p-4 rounded-lg border hover:border-blue-300 hover:bg-blue-50 transition-colors group"
          >
            <div className="text-blue-600 group-hover:text-blue-700 mb-2">
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
            <span className="text-sm font-medium text-gray-700 group-hover:text-gray-900">
              Backgrounds
            </span>
          </button>

          {/* Expression Analysis */}
          <button
            onClick={() => setShowExpressions(true)}
            className="flex flex-col items-center p-4 rounded-lg border hover:border-purple-300 hover:bg-purple-50 transition-colors group"
          >
            <div className="text-purple-600 group-hover:text-purple-700 mb-2">
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <span className="text-sm font-medium text-gray-700 group-hover:text-gray-900">
              Expressions
            </span>
          </button>

          {/* Quality Settings */}
          <button
            onClick={() => setShowQualityPanel(true)}
            className="flex flex-col items-center p-4 rounded-lg border hover:border-green-300 hover:bg-green-50 transition-colors group"
          >
            <div className="text-green-600 group-hover:text-green-700 mb-2">
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <span className="text-sm font-medium text-gray-700 group-hover:text-gray-900">
              Quality
            </span>
          </button>

          {/* File Sharing */}
          <button
            onClick={() => fileInputRef.current?.click()}
            className="flex flex-col items-center p-4 rounded-lg border hover:border-orange-300 hover:bg-orange-50 transition-colors group"
          >
            <div className="text-orange-600 group-hover:text-orange-700 mb-2">
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
              </svg>
            </div>
            <span className="text-sm font-medium text-gray-700 group-hover:text-gray-900">
              Share File
            </span>
          </button>
        </div>

        {/* Connection Quality Indicator */}
        <div className="mt-4 pt-4 border-t">
          <div className="flex items-center justify-between text-sm">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-1">
                <div className={`w-2 h-2 rounded-full ${
                  meetingQuality.connection.rtt < 50 ? 'bg-green-500' :
                  meetingQuality.connection.rtt < 150 ? 'bg-yellow-500' : 'bg-red-500'
                }`}></div>
                <span className="text-gray-600">Connection:</span>
                <span className={getConnectionQualityColor(meetingQuality.connection.rtt)}>
                  {getConnectionQualityLabel(meetingQuality.connection.rtt)}
                </span>
              </div>

              <div className="flex items-center space-x-1">
                <span className="text-gray-600">Quality:</span>
                <span className="font-medium capitalize">{selectedQuality}</span>
              </div>

              <div className="flex items-center space-x-1">
                <span className="text-gray-600">Bandwidth:</span>
                <span>{meetingQuality.connection.bandwidth} Mbps</span>
              </div>
            </div>

            {isHost && (
              <div className="flex items-center space-x-2">
                <button
                  onClick={onRecordingToggle}
                  className={`flex items-center space-x-1 px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                    isRecording
                      ? 'bg-red-100 text-red-800 hover:bg-red-200'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  <div className={`w-2 h-2 rounded-full ${isRecording ? 'bg-red-500' : 'bg-gray-400'}`}></div>
                  <span>{isRecording ? 'Recording' : 'Record'}</span>
                </button>
              </div>
            )}
          </div>
        </div>

        <input
          ref={fileInputRef}
          type="file"
          onChange={handleFileShare}
          className="hidden"
          accept=".pdf,.doc,.docx,.txt,.png,.jpg,.jpeg"
        />
      </div>

      {/* Expression Viewer Panel */}
      {showExpressions && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-md w-full">
            <div className="flex justify-between items-center p-4 border-b">
              <h3 className="text-lg font-semibold">Expression Analysis</h3>
              <button
                onClick={() => setShowExpressions(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div className="p-4">
              <ExpressionViewer 
                videoStream={localStream} 
                isHost={isHost}
              />
            </div>
          </div>
        </div>
      )}

      {/* Virtual Background Panel */}
      {showVirtualBg && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <VirtualBackgroundPanel
            videoStream={localStream}
            onBackgroundChange={onStreamChange}
            onClose={() => setShowVirtualBg(false)}
          />
        </div>
      )}

      {/* Quality Settings Panel */}
      {showQualityPanel && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-lg w-full">
            <div className="flex justify-between items-center p-4 border-b">
              <h3 className="text-lg font-semibold">Video Quality Settings</h3>
              <button
                onClick={() => setShowQualityPanel(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            
            <div className="p-6 space-y-6">
              {/* Quality Selector */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  Video Quality
                </label>
                <div className="grid grid-cols-2 gap-3">
                  {(['auto', 'high', 'medium', 'low'] as const).map((quality) => (
                    <button
                      key={quality}
                      onClick={() => handleQualityChange(quality)}
                      className={`p-3 rounded-lg border text-left transition-colors ${
                        selectedQuality === quality
                          ? 'border-blue-500 bg-blue-50 text-blue-700'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <div className="font-medium capitalize">{quality}</div>
                      <div className="text-xs text-gray-500 mt-1">
                        {quality === 'auto' && 'Adaptive quality'}
                        {quality === 'high' && '1080p, 30fps'}
                        {quality === 'medium' && '720p, 30fps'}
                        {quality === 'low' && '480p, 15fps'}
                      </div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Current Quality Stats */}
              <div className="bg-gray-50 rounded-lg p-4">
                <h4 className="font-medium text-gray-900 mb-3">Current Stats</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Resolution:</span>
                    <span className="font-medium">{meetingQuality.video.resolution}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Frame Rate:</span>
                    <span className="font-medium">{meetingQuality.video.frameRate} fps</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Video Bitrate:</span>
                    <span className="font-medium">{meetingQuality.video.bitrate} kbps</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Audio Bitrate:</span>
                    <span className="font-medium">{meetingQuality.audio.bitrate} kbps</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Round Trip Time:</span>
                    <span className={`font-medium ${getConnectionQualityColor(meetingQuality.connection.rtt)}`}>
                      {meetingQuality.connection.rtt}ms
                    </span>
                  </div>
                </div>
              </div>

              {/* Audio Enhancement Settings */}
              <div>
                <h4 className="font-medium text-gray-900 mb-3">Audio Enhancements</h4>
                <div className="space-y-3">
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={meetingQuality.audio.echoCancellation}
                      onChange={(e) => setMeetingQuality(prev => ({
                        ...prev,
                        audio: { ...prev.audio, echoCancellation: e.target.checked }
                      }))}
                      className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                    <span className="ml-2 text-sm text-gray-700">Echo Cancellation</span>
                  </label>
                  
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={meetingQuality.audio.noiseSuppression}
                      onChange={(e) => setMeetingQuality(prev => ({
                        ...prev,
                        audio: { ...prev.audio, noiseSuppression: e.target.checked }
                      }))}
                      className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                    <span className="ml-2 text-sm text-gray-700">Noise Suppression</span>
                  </label>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdvancedMeetingControls;