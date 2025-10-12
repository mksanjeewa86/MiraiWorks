'use client';

import { useTranslations } from 'next-intl';
import { Card, CardHeader, CardContent, CardTitle } from '@/components/ui/card';
import { useProfileCompleteness } from '@/hooks/useProfileCompleteness';
import {
  CheckCircle2,
  Circle,
  AlertCircle,
  Trophy,
  Target,
  Sparkles,
  TrendingUp,
  Award
} from 'lucide-react';

interface ProfileCompletenessCardProps {
  className?: string;
  showSuggestions?: boolean;
}

export default function ProfileCompletenessCard({
  className,
  showSuggestions = true,
}: ProfileCompletenessCardProps) {
  const t = useTranslations('profile');
  const { completeness, loading, error } = useProfileCompleteness();

  // Function to scroll to section
  const scrollToSection = (sectionId: string) => {
    const element = document.getElementById(`section-${sectionId}`);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' });
      // Add a highlight effect
      element.classList.add('ring-2', 'ring-orange-500', 'ring-offset-2');
      setTimeout(() => {
        element.classList.remove('ring-2', 'ring-orange-500', 'ring-offset-2');
      }, 2000);
    }
  };

  if (loading) {
    return (
      <Card className={className}>
        <CardContent className="pt-6">
          <div className="flex flex-col lg:flex-row gap-8">
            {/* Circular progress skeleton */}
            <div className="flex justify-center lg:justify-start">
              <div className="loading-skeleton rounded-full" style={{ width: '180px', height: '180px' }} />
            </div>
            {/* Content skeleton */}
            <div className="flex-1 space-y-4">
              <div className="loading-skeleton" style={{ width: '60%', height: '32px' }} />
              <div className="loading-skeleton" style={{ width: '100%', height: '80px' }} />
              <div className="loading-skeleton" style={{ width: '100%', height: '100px' }} />
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error || !completeness) {
    return (
      <Card className={className}>
        <CardContent className="pt-6">
          <div className="flex items-center gap-2 text-red-600">
            <AlertCircle className="h-5 w-5" />
            <span className="text-sm">{error || t('errors.failedToLoad')}</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  const { percentage, missing_sections, completed_sections } = completeness;

  // Get gradient and color based on completion
  const getGradientClass = (percent: number) => {
    if (percent === 100) return 'from-green-500 via-emerald-500 to-teal-500';
    if (percent >= 75) return 'from-blue-500 via-indigo-500 to-purple-500';
    if (percent >= 50) return 'from-yellow-500 via-orange-500 to-amber-500';
    if (percent >= 25) return 'from-orange-500 via-red-500 to-pink-500';
    return 'from-gray-400 via-gray-500 to-gray-600';
  };

  const getStatusInfo = (percent: number) => {
    if (percent === 100) return {
      icon: Trophy,
      text: 'Profile Complete!',
      subtext: 'You\'re ready to shine'
    };
    if (percent >= 75) return {
      icon: Award,
      text: 'Almost There!',
      subtext: 'Just a few more details'
    };
    if (percent >= 50) return {
      icon: TrendingUp,
      text: 'Great Progress!',
      subtext: 'Keep going to stand out'
    };
    if (percent >= 25) return {
      icon: Target,
      text: 'Getting Started',
      subtext: 'Add more to boost visibility'
    };
    return {
      icon: Sparkles,
      text: 'Just Started',
      subtext: 'Complete your profile to get noticed'
    };
  };

  const statusInfo = getStatusInfo(percentage);
  const StatusIcon = statusInfo.icon;
  const gradientClass = getGradientClass(percentage);

  // Calculate circle properties
  const circleRadius = 70;
  const circleCircumference = 2 * Math.PI * circleRadius;
  const strokeDashoffset = circleCircumference - (circleCircumference * percentage) / 100;

  return (
    <Card className={`${className} overflow-hidden relative`}>
      {/* Gradient background effect */}
      <div
        className={`absolute inset-0 bg-gradient-to-br ${gradientClass} opacity-5`}
        aria-hidden="true"
      />

      <CardContent className="pt-6 pb-6 relative">
        <div className="flex flex-col lg:flex-row gap-8 items-center lg:items-start">
          {/* Circular Progress Indicator */}
          <div className="flex-shrink-0">
            <div className="relative w-44 h-44">
              {/* Background Circle */}
              <svg className="w-full h-full transform -rotate-90">
                <circle
                  cx="88"
                  cy="88"
                  r={circleRadius}
                  stroke="currentColor"
                  strokeWidth="12"
                  fill="none"
                  className="text-gray-200 dark:text-gray-700"
                />
                {/* Progress Circle */}
                <circle
                  cx="88"
                  cy="88"
                  r={circleRadius}
                  stroke="url(#gradient)"
                  strokeWidth="12"
                  fill="none"
                  strokeLinecap="round"
                  strokeDasharray={circleCircumference}
                  strokeDashoffset={strokeDashoffset}
                  className="transition-all duration-1000 ease-out"
                />
                {/* Gradient Definition */}
                <defs>
                  <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" className={`${percentage === 100 ? 'text-green-500' : percentage >= 75 ? 'text-blue-500' : percentage >= 50 ? 'text-yellow-500' : percentage >= 25 ? 'text-orange-500' : 'text-gray-400'}`} stopColor="currentColor" />
                    <stop offset="100%" className={`${percentage === 100 ? 'text-teal-500' : percentage >= 75 ? 'text-purple-500' : percentage >= 50 ? 'text-amber-500' : percentage >= 25 ? 'text-pink-500' : 'text-gray-600'}`} stopColor="currentColor" />
                  </linearGradient>
                </defs>
              </svg>

              {/* Center Content */}
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <div className={`text-5xl font-bold bg-gradient-to-br ${gradientClass} bg-clip-text text-transparent`}>
                  {percentage}%
                </div>
                <div className="text-xs font-medium text-gray-500 dark:text-gray-400 mt-1">
                  Complete
                </div>
              </div>
            </div>
          </div>

          {/* Content Section */}
          <div className="flex-1 space-y-6 w-full">
            {/* Status Header */}
            <div className="space-y-2">
              <div className="flex items-center gap-3">
                <div className={`p-2 rounded-lg bg-gradient-to-br ${gradientClass}`}>
                  <StatusIcon className="h-6 w-6 text-white" />
                </div>
                <div>
                  <h3 className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>
                    {statusInfo.text}
                  </h3>
                  <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                    {statusInfo.subtext}
                  </p>
                </div>
              </div>
            </div>

            {/* Milestones */}
            <div className="flex gap-2 flex-wrap">
              {[25, 50, 75, 100].map((milestone) => (
                <div
                  key={milestone}
                  className={`px-3 py-1 rounded-full text-xs font-medium transition-all ${
                    percentage >= milestone
                      ? 'bg-gradient-to-r ' + gradientClass + ' text-white shadow-md'
                      : 'bg-gray-100 dark:bg-gray-800 text-gray-400 dark:text-gray-500'
                  }`}
                >
                  {milestone}%
                </div>
              ))}
            </div>

            {/* Two Column Layout for Sections - Compact Design */}
            {(completed_sections.length > 0 || (showSuggestions && missing_sections.length > 0)) && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Completed Sections */}
                {completed_sections.length > 0 && (
                  <div className="space-y-2">
                    <h4 className="text-xs font-semibold flex items-center gap-1.5 uppercase tracking-wide" style={{ color: 'var(--text-secondary)' }}>
                      <CheckCircle2 className="h-3.5 w-3.5 text-green-600" />
                      Completed ({completed_sections.length})
                    </h4>
                    <div className="flex flex-wrap gap-1.5">
                      {completed_sections.map((section) => (
                        <div
                          key={section}
                          className="inline-flex items-center gap-1.5 text-xs bg-green-50 dark:bg-green-900/20 px-2 py-1 rounded-md border border-green-200/50 dark:border-green-800/50"
                        >
                          <CheckCircle2 className="h-3 w-3 text-green-600 flex-shrink-0" />
                          <span className="text-green-900 dark:text-green-100 font-medium">
                            {t(`completeness.sections.${section}`)}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Missing Sections */}
                {showSuggestions && missing_sections.length > 0 && (
                  <div className="space-y-2">
                    <h4 className="text-xs font-semibold flex items-center gap-1.5 uppercase tracking-wide" style={{ color: 'var(--text-secondary)' }}>
                      <Circle className="h-3.5 w-3.5 text-orange-600" />
                      To Complete ({missing_sections.length})
                    </h4>
                    <div className="flex flex-wrap gap-1.5">
                      {missing_sections.map((section) => (
                        <button
                          key={section}
                          onClick={() => scrollToSection(section)}
                          className="inline-flex items-center gap-1.5 text-xs bg-orange-50 dark:bg-orange-900/20 px-2 py-1 rounded-md border border-orange-200/50 dark:border-orange-800/50 hover:bg-orange-100 dark:hover:bg-orange-900/30 hover:scale-105 active:scale-95 transition-all cursor-pointer"
                          title={`Jump to ${t(`completeness.sections.${section}`)} section`}
                        >
                          <Circle className="h-3 w-3 text-orange-600 flex-shrink-0" />
                          <span className="text-orange-900 dark:text-orange-100 font-medium">
                            {t(`completeness.sections.${section}`)}
                          </span>
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* 100% Completion Celebration */}
            {percentage === 100 && (
              <div className="relative overflow-hidden rounded-xl bg-gradient-to-r from-green-500 via-emerald-500 to-teal-500 p-4 shadow-lg">
                <div className="relative z-10 flex items-center gap-3">
                  <Trophy className="h-8 w-8 text-white" />
                  <div>
                    <p className="text-white font-bold text-lg">
                      Congratulations!
                    </p>
                    <p className="text-white/90 text-sm">
                      Your profile is 100% complete and ready to impress!
                    </p>
                  </div>
                </div>
                {/* Decorative elements */}
                <div className="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full -mr-16 -mt-16" />
                <div className="absolute bottom-0 left-0 w-24 h-24 bg-white/10 rounded-full -ml-12 -mb-12" />
              </div>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
