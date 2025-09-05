import React, { useState, useRef } from 'react';
import { useVirtualBackground } from '../../hooks/useVirtualBackground';

interface VirtualBackgroundPanelProps {
  videoStream?: MediaStream;
  onBackgroundChange?: (stream: MediaStream | null) => void;
  onClose?: () => void;
}

const VirtualBackgroundPanel: React.FC<VirtualBackgroundPanelProps> = ({
  videoStream,
  onBackgroundChange,
  onClose
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [selectedBackground, setSelectedBackground] = useState<string>('none');

  const {
    isSupported,
    isEnabled,
    isProcessing,
    availableBackgrounds,
    error,
    enableBackground,
    disableBackground,
    getProcessedStream,
    uploadCustomBackground
  } = useVirtualBackground(videoStream);

  const handleBackgroundSelect = async (backgroundIndex: number) => {
    const background = availableBackgrounds[backgroundIndex];
    setSelectedBackground(backgroundIndex.toString());

    try {
      if (background.type === 'none') {
        disableBackground();
        onBackgroundChange?.(videoStream || null);
      } else {
        await enableBackground(background);
        const processedStream = getProcessedStream();
        onBackgroundChange?.(processedStream);
      }
    } catch (error) {
      console.error('Error applying background:', error);
    }
  };

  const handleCustomUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    try {
      const customBackground = await uploadCustomBackground(file);
      const newIndex = availableBackgrounds.length;
      setSelectedBackground(newIndex.toString());
      
      await enableBackground(customBackground);
      const processedStream = getProcessedStream();
      onBackgroundChange?.(processedStream);
    } catch (error) {
      console.error('Error uploading custom background:', error);
    }

    // Reset input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  if (!isSupported) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6 max-w-md mx-auto">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Virtual Backgrounds</h3>
          {onClose && (
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
            >
              ✕
            </button>
          )}
        </div>
        
        <div className="text-center py-8">
          <div className="text-gray-500 mb-4">
            <svg className="w-16 h-16 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
          <p className="text-gray-600 mb-2">Virtual backgrounds are not supported</p>
          <p className="text-sm text-gray-500">
            Your browser doesn't support the required features for virtual backgrounds.
            Please try using Chrome, Edge, or Firefox.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 max-w-2xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-lg font-semibold text-gray-900">Virtual Backgrounds</h3>
        {onClose && (
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        )}
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-md p-3 mb-4">
          <div className="flex">
            <div className="text-red-400 mr-2">
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="text-sm text-red-700">{error}</div>
          </div>
        </div>
      )}

      {isProcessing && (
        <div className="bg-blue-50 border border-blue-200 rounded-md p-3 mb-4">
          <div className="flex items-center">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
            <div className="text-sm text-blue-700">Processing background...</div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-3 gap-4 mb-6">
        {availableBackgrounds.map((background, index) => (
          <div
            key={index}
            className={`relative cursor-pointer rounded-lg overflow-hidden border-2 transition-all ${
              selectedBackground === index.toString()
                ? 'border-blue-500 shadow-md'
                : 'border-gray-200 hover:border-gray-300'
            }`}
            onClick={() => handleBackgroundSelect(index)}
          >
            <div className="aspect-video bg-gray-100 flex items-center justify-center">
              {background.type === 'none' ? (
                <div className="text-center">
                  <div className="text-gray-400 mb-1">
                    <svg className="w-8 h-8 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728L5.636 5.636m12.728 12.728L5.636 5.636" />
                    </svg>
                  </div>
                  <span className="text-xs text-gray-600">None</span>
                </div>
              ) : background.type === 'blur' ? (
                <div className="text-center">
                  <div className="text-gray-400 mb-1">
                    <svg className="w-8 h-8 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                  </div>
                  <span className="text-xs text-gray-600">Blur {background.blurAmount}px</span>
                </div>
              ) : background.source ? (
                <img
                  src={background.source}
                  alt="Background"
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="text-gray-400">Image</div>
              )}
            </div>

            {selectedBackground === index.toString() && isEnabled && (
              <div className="absolute top-2 right-2">
                <div className="bg-blue-500 text-white rounded-full p-1">
                  <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                </div>
              </div>
            )}
          </div>
        ))}

        {/* Upload Custom Background Button */}
        <div
          className="relative cursor-pointer rounded-lg overflow-hidden border-2 border-dashed border-gray-300 hover:border-gray-400 transition-colors"
          onClick={() => fileInputRef.current?.click()}
        >
          <div className="aspect-video bg-gray-50 flex items-center justify-center">
            <div className="text-center">
              <div className="text-gray-400 mb-1">
                <svg className="w-8 h-8 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
              </div>
              <span className="text-xs text-gray-600">Upload</span>
            </div>
          </div>
        </div>
      </div>

      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        onChange={handleCustomUpload}
        className="hidden"
      />

      <div className="flex justify-between items-center">
        <div className="text-sm text-gray-600">
          {isEnabled ? (
            <span className="text-green-600">✓ Virtual background active</span>
          ) : (
            <span>Select a background to get started</span>
          )}
        </div>

        <div className="flex gap-2">
          {onClose && (
            <button
              onClick={onClose}
              className="px-4 py-2 text-sm text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors"
            >
              Close
            </button>
          )}
        </div>
      </div>

      <div className="mt-4 text-xs text-gray-500">
        <p>
          • Virtual backgrounds use AI to detect and replace your background
        </p>
        <p>
          • For best results, use good lighting and sit against a solid background
        </p>
        <p>
          • Custom backgrounds should be 16:9 aspect ratio for best fit
        </p>
      </div>
    </div>
  );
};

export default VirtualBackgroundPanel;