import React from 'react';
import { UserIcon, CalendarIcon } from '@heroicons/react/24/outline';
import type { MBTIResultCardProps } from '@/types/mbti';
import { MBTI_TYPE_COLORS, MBTI_TEMPERAMENTS } from '@/types/mbti';
import MBTITypeAvatar from './MBTITypeAvatar';

const MBTIResultCard: React.FC<MBTIResultCardProps> = ({
  summary,
  language = 'ja',
  showDetails = true
}) => {
  const typeColor = MBTI_TYPE_COLORS[summary.mbti_type] || '#6B7280';
  const temperamentInfo = MBTI_TEMPERAMENTS[summary.temperament];
  
  const typeName = language === 'ja' ? summary.type_name_ja : summary.type_name_en;
  const typeDescription = language === 'ja' ? summary.type_description_ja : summary.type_description_en;
  const temperamentName = language === 'ja' ? temperamentInfo?.name_ja : temperamentInfo?.name_en;

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString(language === 'ja' ? 'ja-JP' : 'en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const getDimensionLabel = (dimension: string) => {
    const labels = {
      'E_I': language === 'ja' ? { 'E': '外向性', 'I': '内向性' } : { 'E': 'Extraversion', 'I': 'Introversion' },
      'S_N': language === 'ja' ? { 'S': '感覚', 'N': '直感' } : { 'S': 'Sensing', 'N': 'Intuition' },
      'T_F': language === 'ja' ? { 'T': '思考', 'F': '感情' } : { 'T': 'Thinking', 'F': 'Feeling' },
      'J_P': language === 'ja' ? { 'J': '判断', 'P': '知覚' } : { 'J': 'Judging', 'P': 'Perceiving' }
    };
    return labels[dimension as keyof typeof labels] || {};
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 border-l-4" style={{ borderLeftColor: typeColor }}>
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div 
            className="w-12 h-12 rounded-full flex items-center justify-center text-white font-bold text-lg"
            style={{ backgroundColor: typeColor }}
          >
            {summary.mbti_type}
          </div>
          <div>
            <h3 className="text-xl font-bold text-gray-900">{typeName}</h3>
            <p className="text-sm text-gray-600">{temperamentName}</p>
          </div>
        </div>
        
        <div className="flex items-center text-sm text-gray-500">
          <CalendarIcon className="h-4 w-4 mr-1" />
          {formatDate(summary.completed_at)}
        </div>
      </div>

      {/* Description */}
      <p className="text-gray-700 mb-6 leading-relaxed">
        {typeDescription}
      </p>

      {/* Dimensions */}
      {showDetails && (
        <div className="space-y-4">
          <h4 className="font-semibold text-gray-900 text-lg">
            {language === 'ja' ? '性格特性' : 'Personality Dimensions'}
          </h4>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {Object.entries(summary.dimension_preferences).map(([dimension, preference]) => {
              const strength = summary.strength_scores[dimension] || 0;
              const labels = getDimensionLabel(dimension);
              const preferenceLabel = labels[preference as keyof typeof labels] || preference;
              
              return (
                <div key={dimension} className="bg-gray-50 rounded-lg p-4">
                  <div className="flex justify-between items-center mb-2">
                    <span className="font-medium text-gray-900">{preferenceLabel}</span>
                    <span className="text-sm text-gray-600">{strength}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="h-2 rounded-full transition-all duration-300"
                      style={{ 
                        width: `${strength}%`, 
                        backgroundColor: typeColor 
                      }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* MBTI Type Avatar */}
      <div className="mt-6 p-6 bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-800 dark:to-gray-900 rounded-lg">
        <div className="text-center">
          <MBTITypeAvatar type={summary.mbti_type} size="xl" showLabel={false} />
          <p className="mt-4 text-sm text-gray-600 dark:text-gray-400">
            {language === 'ja' 
              ? 'あなたの性格タイプ' 
              : 'Your Personality Type'
            }
          </p>
        </div>
      </div>
    </div>
  );
};

export default MBTIResultCard;