'use client';

import { useState, useEffect } from 'react';
import { Clock, AlertTriangle } from 'lucide-react';
import { Badge } from '@/components/ui/badge';

interface ExamTimerProps {
  timeRemaining: number; // in seconds
  onTimeUp: () => void;
}

export function ExamTimer({ timeRemaining, onTimeUp }: ExamTimerProps) {
  const [showWarning, setShowWarning] = useState(false);

  useEffect(() => {
    // Show warning when less than 5 minutes remaining
    if (timeRemaining <= 300 && timeRemaining > 0) {
      setShowWarning(true);
    }

    // Auto-submit when time is up
    if (timeRemaining <= 0) {
      onTimeUp();
    }
  }, [timeRemaining, onTimeUp]);

  const formatTime = (seconds: number): string => {
    if (seconds <= 0) return '00:00:00';

    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;

    if (hours > 0) {
      return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }

    return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const getTimerColor = () => {
    if (timeRemaining <= 60) return 'bg-red-100 text-red-800 border-red-200'; // Last minute
    if (timeRemaining <= 300) return 'bg-orange-100 text-orange-800 border-orange-200'; // Last 5 minutes
    if (timeRemaining <= 900) return 'bg-yellow-100 text-yellow-800 border-yellow-200'; // Last 15 minutes
    return 'bg-blue-100 text-blue-800 border-blue-200';
  };

  const getProgressPercentage = (totalTime: number) => {
    return Math.max(0, (timeRemaining / totalTime) * 100);
  };

  return (
    <div className="flex items-center gap-3">
      {showWarning && timeRemaining > 60 && (
        <div className="flex items-center gap-1 text-orange-600">
          <AlertTriangle className="h-4 w-4" />
          <span className="text-sm font-medium">Less than 5 minutes remaining!</span>
        </div>
      )}

      {timeRemaining <= 60 && timeRemaining > 0 && (
        <div className="flex items-center gap-1 text-red-600 animate-pulse">
          <AlertTriangle className="h-4 w-4" />
          <span className="text-sm font-medium">Time almost up!</span>
        </div>
      )}

      <Badge
        variant="outline"
        className={`${getTimerColor()} px-3 py-1 font-mono text-base border ${
          timeRemaining <= 60 ? 'animate-pulse' : ''
        }`}
      >
        <Clock className="h-4 w-4 mr-2" />
        {formatTime(timeRemaining)}
      </Badge>

      {/* Mini progress bar for time remaining */}
      {timeRemaining <= 300 && (
        <div className="w-20 h-2 bg-gray-200 rounded-full overflow-hidden">
          <div
            className={`h-full transition-all duration-1000 ${
              timeRemaining <= 60
                ? 'bg-red-500'
                : timeRemaining <= 300
                  ? 'bg-orange-500'
                  : 'bg-yellow-500'
            }`}
            style={{ width: `${getProgressPercentage(300)}%` }}
          />
        </div>
      )}
    </div>
  );
}
