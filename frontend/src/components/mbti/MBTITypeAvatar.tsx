import React from 'react';
import { MBTI_TYPE_COLORS } from '@/types/mbti';

interface MBTITypeAvatarProps {
  type: string;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  showLabel?: boolean;
}

const MBTITypeAvatar: React.FC<MBTITypeAvatarProps> = ({
  type,
  size = 'md',
  showLabel = false,
}) => {
  const sizeClasses = {
    sm: 'w-12 h-12 text-sm',
    md: 'w-16 h-16 text-base',
    lg: 'w-24 h-24 text-lg',
    xl: 'w-32 h-32 text-xl',
  };

  const iconSizes = {
    sm: 24,
    md: 32,
    lg: 48,
    xl: 64,
  };

  const color = MBTI_TYPE_COLORS[type] || '#6B7280';
  const iconSize = iconSizes[size];

  // Unique icons for each MBTI type
  const getTypeIcon = () => {
    switch (type) {
      // Analysts (NT)
      case 'INTJ':
        return (
          <svg viewBox="0 0 100 100" width={iconSize} height={iconSize} fill="currentColor">
            <path d="M50 10 L80 30 L80 70 L50 90 L20 70 L20 30 Z" opacity="0.2" />
            <path d="M50 5 C30 5 15 20 15 40 C15 60 30 75 50 75 C70 75 85 60 85 40 C85 20 70 5 50 5 Z M50 20 L60 35 L50 50 L40 35 Z" />
            <circle cx="50" cy="65" r="5" />
          </svg>
        );
      case 'INTP':
        return (
          <svg viewBox="0 0 100 100" width={iconSize} height={iconSize} fill="currentColor">
            <circle cx="50" cy="50" r="35" fill="none" stroke="currentColor" strokeWidth="3" />
            <path
              d="M30 50 Q50 20 70 50 Q50 80 30 50"
              strokeWidth="2"
              stroke="currentColor"
              fill="none"
            />
            <circle cx="50" cy="50" r="8" />
          </svg>
        );
      case 'ENTJ':
        return (
          <svg viewBox="0 0 100 100" width={iconSize} height={iconSize} fill="currentColor">
            <polygon points="50,15 75,35 75,65 50,85 25,65 25,35" />
            <polygon points="50,30 65,40 65,60 50,70 35,60 35,40" fill="white" />
            <circle cx="50" cy="50" r="10" fill="currentColor" />
          </svg>
        );
      case 'ENTP':
        return (
          <svg viewBox="0 0 100 100" width={iconSize} height={iconSize} fill="currentColor">
            <path d="M50 20 L70 40 L60 50 L70 60 L50 80 L30 60 L40 50 L30 40 Z" />
            <circle cx="50" cy="50" r="5" fill="white" />
          </svg>
        );

      // Diplomats (NF)
      case 'INFJ':
        return (
          <svg viewBox="0 0 100 100" width={iconSize} height={iconSize} fill="currentColor">
            <path
              d="M50 15 C30 15 20 35 20 50 C20 65 30 85 50 85 C70 85 80 65 80 50 C80 35 70 15 50 15 Z"
              opacity="0.3"
            />
            <path d="M50 25 L60 45 L50 65 L40 45 Z" />
            <circle cx="50" cy="50" r="8" fill="white" />
            <circle cx="50" cy="50" r="4" />
          </svg>
        );
      case 'INFP':
        return (
          <svg viewBox="0 0 100 100" width={iconSize} height={iconSize} fill="currentColor">
            <path d="M50 20 Q30 30 25 50 T50 80 Q70 70 75 50 T50 20" />
            <circle cx="50" cy="50" r="12" fill="white" />
            <path d="M45 45 Q50 40 55 45 Q50 55 45 45" fill="currentColor" />
          </svg>
        );
      case 'ENFJ':
        return (
          <svg viewBox="0 0 100 100" width={iconSize} height={iconSize} fill="currentColor">
            <circle cx="50" cy="50" r="30" opacity="0.3" />
            <path d="M35 40 Q50 25 65 40 L65 60 Q50 75 35 60 Z" />
            <circle cx="40" cy="45" r="3" fill="white" />
            <circle cx="60" cy="45" r="3" fill="white" />
          </svg>
        );
      case 'ENFP':
        return (
          <svg viewBox="0 0 100 100" width={iconSize} height={iconSize} fill="currentColor">
            <path d="M50 20 L55 40 L75 40 L60 52 L65 72 L50 60 L35 72 L40 52 L25 40 L45 40 Z" />
            <circle cx="50" cy="50" r="8" fill="white" />
          </svg>
        );

      // Sentinels (SJ)
      case 'ISTJ':
        return (
          <svg viewBox="0 0 100 100" width={iconSize} height={iconSize} fill="currentColor">
            <rect x="20" y="20" width="60" height="60" />
            <rect x="30" y="30" width="40" height="40" fill="white" />
            <rect x="40" y="40" width="20" height="20" />
          </svg>
        );
      case 'ISFJ':
        return (
          <svg viewBox="0 0 100 100" width={iconSize} height={iconSize} fill="currentColor">
            <path d="M50 15 L70 35 L70 65 L50 85 L30 65 L30 35 Z" />
            <path d="M50 30 L60 40 L60 60 L50 70 L40 60 L40 40 Z" fill="white" />
            <circle cx="50" cy="50" r="8" />
          </svg>
        );
      case 'ESTJ':
        return (
          <svg viewBox="0 0 100 100" width={iconSize} height={iconSize} fill="currentColor">
            <polygon points="50,20 70,30 70,50 80,60 60,80 40,80 20,60 30,50 30,30" />
            <polygon points="50,35 60,40 60,55 50,65 40,55 40,40" fill="white" />
          </svg>
        );
      case 'ESFJ':
        return (
          <svg viewBox="0 0 100 100" width={iconSize} height={iconSize} fill="currentColor">
            <circle cx="50" cy="35" r="20" />
            <circle cx="35" cy="65" r="15" />
            <circle cx="65" cy="65" r="15" />
            <circle cx="50" cy="35" r="8" fill="white" />
          </svg>
        );

      // Explorers (SP)
      case 'ISTP':
        return (
          <svg viewBox="0 0 100 100" width={iconSize} height={iconSize} fill="currentColor">
            <path d="M30 30 L70 30 L60 50 L70 70 L30 70 L40 50 Z" />
            <rect x="45" y="25" width="10" height="50" fill="white" />
            <rect x="48" y="40" width="4" height="20" />
          </svg>
        );
      case 'ISFP':
        return (
          <svg viewBox="0 0 100 100" width={iconSize} height={iconSize} fill="currentColor">
            <path d="M50 20 Q70 30 70 50 T50 80 Q30 70 30 50 T50 20" />
            <circle cx="40" cy="40" r="5" fill="white" />
            <circle cx="60" cy="40" r="5" fill="white" />
            <path d="M40 60 Q50 65 60 60" fill="none" stroke="white" strokeWidth="2" />
          </svg>
        );
      case 'ESTP':
        return (
          <svg viewBox="0 0 100 100" width={iconSize} height={iconSize} fill="currentColor">
            <path d="M50 15 L80 50 L50 85 L20 50 Z" />
            <path d="M50 30 L65 50 L50 70 L35 50 Z" fill="white" />
            <circle cx="50" cy="50" r="10" />
          </svg>
        );
      case 'ESFP':
        return (
          <svg viewBox="0 0 100 100" width={iconSize} height={iconSize} fill="currentColor">
            <circle cx="50" cy="50" r="35" />
            <path d="M30 40 Q50 20 70 40" fill="none" stroke="white" strokeWidth="3" />
            <circle cx="35" cy="40" r="5" fill="white" />
            <circle cx="65" cy="40" r="5" fill="white" />
            <path d="M35 60 Q50 70 65 60" fill="none" stroke="white" strokeWidth="3" />
          </svg>
        );

      default:
        return (
          <svg viewBox="0 0 100 100" width={iconSize} height={iconSize} fill="currentColor">
            <circle cx="50" cy="50" r="35" />
            <text x="50" y="55" textAnchor="middle" fontSize="20" fill="white" fontWeight="bold">
              {type.charAt(0)}
            </text>
          </svg>
        );
    }
  };

  return (
    <div className="inline-flex flex-col items-center">
      <div
        className={`${sizeClasses[size]} rounded-full flex items-center justify-center`}
        style={{ backgroundColor: `${color}20`, color }}
      >
        {getTypeIcon()}
      </div>
      {showLabel && (
        <span className="mt-2 font-semibold" style={{ color }}>
          {type}
        </span>
      )}
    </div>
  );
};

export default MBTITypeAvatar;
