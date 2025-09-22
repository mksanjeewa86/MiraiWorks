import React from 'react';
import { 
  SignalIcon, 
  WifiIcon,
  ExclamationTriangleIcon,
  UserGroupIcon,
} from '@heroicons/react/24/outline';

interface ConnectionStatusProps {
  isConnected: boolean;
  quality: 'excellent' | 'good' | 'fair' | 'poor';
  participantCount: number;
}

export const ConnectionStatus: React.FC<ConnectionStatusProps> = ({
  isConnected,
  quality,
  participantCount,
}) => {
  const getQualityColor = () => {
    switch (quality) {
      case 'excellent':
        return 'text-green-500';
      case 'good':
        return 'text-green-400';
      case 'fair':
        return 'text-yellow-500';
      case 'poor':
        return 'text-red-500';
      default:
        return 'text-gray-500';
    }
  };

  const getQualityIcon = () => {
    if (!isConnected) {
      return <ExclamationTriangleIcon className="h-5 w-5 text-red-500" />;
    }

    switch (quality) {
      case 'excellent':
      case 'good':
        return <SignalIcon className={`h-5 w-5 ${getQualityColor()}`} />;
      case 'fair':
      case 'poor':
        return <WifiIcon className={`h-5 w-5 ${getQualityColor()}`} />;
      default:
        return <WifiIcon className="h-5 w-5 text-gray-500" />;
    }
  };

  const getStatusText = () => {
    if (!isConnected) {
      return '接続中...';
    }

    switch (quality) {
      case 'excellent':
        return '優秀';
      case 'good':
        return '良好';
      case 'fair':
        return '普通';
      case 'poor':
        return '不安定';
      default:
        return '不明';
    }
  };

  return (
    <div className="absolute top-4 left-4 z-50">
      <div className="bg-black bg-opacity-75 text-white rounded-lg px-3 py-2 flex items-center space-x-3">
        {/* Connection Quality */}
        <div className="flex items-center space-x-2">
          {getQualityIcon()}
          <span className="text-sm font-medium">
            {getStatusText()}
          </span>
        </div>

        {/* Divider */}
        <div className="w-px h-4 bg-gray-400"></div>

        {/* Participant Count */}
        <div className="flex items-center space-x-1">
          <UserGroupIcon className="h-4 w-4" />
          <span className="text-sm">{participantCount}</span>
        </div>

        {/* Recording Indicator */}
        <div className="flex items-center space-x-1">
          <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
          <span className="text-sm">REC</span>
        </div>
      </div>
    </div>
  );
};