import React, { useState, useEffect } from 'react';
import { useExpressionAnalysis } from '../../hooks/useExpressionAnalysis';

interface ExpressionViewerProps {
  videoStream?: MediaStream;
  isHost?: boolean;
  onEngagementChange?: (engagement: number) => void;
}

const ExpressionViewer: React.FC<ExpressionViewerProps> = ({
  videoStream,
  isHost = false,
  onEngagementChange
}) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const {
    isSupported,
    isEnabled,
    isAnalyzing,
    hasConsent,
    currentEmotion,
    dominantEmotion,
    engagementLevel,
    error,
    enableAnalysis,
    disableAnalysis,
    getAverageEngagement,
    getEngagementTrend
  } = useExpressionAnalysis(videoStream);

  // Notify parent of engagement changes
  useEffect(() => {
    if (onEngagementChange && isEnabled) {
      onEngagementChange(engagementLevel);
    }
  }, [engagementLevel, isEnabled, onEngagementChange]);

  const handleToggleAnalysis = async () => {
    if (isEnabled) {
      disableAnalysis();
    } else {
      await enableAnalysis();
    }
  };

  const getEmotionColor = (emotion: string): string => {
    const colors: Record<string, string> = {
      happy: 'text-green-600',
      sad: 'text-blue-600',
      angry: 'text-red-600',
      fearful: 'text-purple-600',
      disgusted: 'text-yellow-600',
      surprised: 'text-orange-600',
      neutral: 'text-gray-600'
    };
    return colors[emotion] || 'text-gray-600';
  };

  const getEmotionIcon = (emotion: string): string => {
    const icons: Record<string, string> = {
      happy: '😊',
      sad: '😢',
      angry: '😠',
      fearful: '😨',
      disgusted: '🤢',
      surprised: '😮',
      neutral: '😐'
    };
    return icons[emotion] || '😐';
  };

  const getEngagementColor = (level: number): string => {
    if (level >= 0.7) return 'text-green-600';
    if (level >= 0.4) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getEngagementLabel = (level: number): string => {
    if (level >= 0.8) return 'Highly Engaged';
    if (level >= 0.6) return 'Engaged';
    if (level >= 0.4) return 'Moderately Engaged';
    if (level >= 0.2) return 'Low Engagement';
    return 'Very Low Engagement';
  };

  const getTrendIcon = (trend: string): string => {
    switch (trend) {
      case 'increasing': return '📈';
      case 'decreasing': return '📉';
      default: return '➡️';
    }
  };

  if (!isSupported) {
    return (
      <div className="bg-gray-50 rounded-lg p-3 text-center">
        <div className="text-gray-400 text-sm">
          Expression analysis not supported
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border">
      {/* Header */}
      <div className="flex items-center justify-between p-3 border-b">
        <div className="flex items-center space-x-2">
          <div className="text-sm font-medium text-gray-700">
            Expression Insights
          </div>
          {isHost && (
            <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
              Host View
            </span>
          )}
        </div>
        
        <div className="flex items-center space-x-2">
          {error && (
            <div className="text-red-500 text-xs" title={error}>
              ⚠️
            </div>
          )}
          
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <svg
              className={`w-4 h-4 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>
        </div>
      </div>

      {/* Quick Status Bar */}
      <div className="p-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            {isEnabled && currentEmotion && dominantEmotion ? (
              <>
                <div className="flex items-center space-x-1">
                  <span className="text-lg">{getEmotionIcon(dominantEmotion)}</span>
                  <span className={`text-sm font-medium ${getEmotionColor(dominantEmotion)}`}>
                    {dominantEmotion.charAt(0).toUpperCase() + dominantEmotion.slice(1)}
                  </span>
                </div>
                
                <div className="w-px h-4 bg-gray-300"></div>
                
                <div className="flex items-center space-x-1">
                  <div className={`w-2 h-2 rounded-full ${
                    engagementLevel >= 0.7 ? 'bg-green-500' :
                    engagementLevel >= 0.4 ? 'bg-yellow-500' : 'bg-red-500'
                  }`}></div>
                  <span className={`text-sm ${getEngagementColor(engagementLevel)}`}>
                    {Math.round(engagementLevel * 100)}%
                  </span>
                </div>
              </>
            ) : isAnalyzing ? (
              <div className="flex items-center space-x-2">
                <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-blue-600"></div>
                <span className="text-sm text-gray-600">Analyzing...</span>
              </div>
            ) : (
              <span className="text-sm text-gray-500">
                {hasConsent ? 'Ready to analyze' : 'Analysis disabled'}
              </span>
            )}
          </div>

          <button
            onClick={handleToggleAnalysis}
            disabled={isAnalyzing}
            className={`px-3 py-1 text-xs rounded transition-colors ${
              isEnabled
                ? 'bg-red-100 text-red-800 hover:bg-red-200'
                : 'bg-green-100 text-green-800 hover:bg-green-200'
            } disabled:opacity-50`}
          >
            {isEnabled ? 'Disable' : 'Enable'}
          </button>
        </div>
      </div>

      {/* Expanded Details */}
      {isExpanded && isEnabled && currentEmotion && (
        <div className="border-t">
          <div className="p-4 space-y-4">
            {/* Emotion Breakdown */}
            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-2">Current Emotions</h4>
              <div className="grid grid-cols-2 gap-2">
                {Object.entries(currentEmotion).map(([emotion, value]) => (
                  <div key={emotion} className="flex items-center justify-between">
                    <div className="flex items-center space-x-1">
                      <span className="text-xs">{getEmotionIcon(emotion)}</span>
                      <span className="text-xs text-gray-600 capitalize">{emotion}</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <div className="w-16 h-1 bg-gray-200 rounded-full overflow-hidden">
                        <div 
                          className={`h-full transition-all duration-300 ${getEmotionColor(emotion).replace('text-', 'bg-')}`}
                          style={{ width: `${value * 100}%` }}
                        />
                      </div>
                      <span className="text-xs text-gray-500 w-8 text-right">
                        {Math.round(value * 100)}%
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Engagement Metrics */}
            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-2">Engagement Metrics</h4>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Current Level</span>
                  <span className={`text-sm font-medium ${getEngagementColor(engagementLevel)}`}>
                    {getEngagementLabel(engagementLevel)}
                  </span>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">5-min Average</span>
                  <span className="text-sm font-medium">
                    {Math.round(getAverageEngagement(5) * 100)}%
                  </span>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Trend</span>
                  <div className="flex items-center space-x-1">
                    <span>{getTrendIcon(getEngagementTrend())}</span>
                    <span className="text-sm capitalize">{getEngagementTrend()}</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Privacy Notice */}
            <div className="bg-blue-50 rounded-md p-3">
              <div className="flex items-start space-x-2">
                <div className="text-blue-500 mt-0.5">
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                  </svg>
                </div>
                <div>
                  <div className="text-xs font-medium text-blue-800">Privacy Protected</div>
                  <div className="text-xs text-blue-700 mt-1">
                    Expression analysis is processed locally. No facial data is stored or transmitted.
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

    </div>
  );
};

export default ExpressionViewer;