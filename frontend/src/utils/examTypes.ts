import { ExamType } from '@/types/exam';

// Exam Type Labels (Japanese and English)
export const examTypeLabels: Record<string, { ja: string; en: string; category: string }> = {
  // General Categories
  [ExamType.APTITUDE]: {
    ja: '適性検査',
    en: 'Aptitude Test',
    category: 'General',
  },
  [ExamType.SKILL]: {
    ja: 'スキルテスト',
    en: 'Skill Test',
    category: 'General',
  },
  [ExamType.KNOWLEDGE]: {
    ja: '知識テスト',
    en: 'Knowledge Test',
    category: 'General',
  },
  [ExamType.PERSONALITY]: {
    ja: '性格テスト',
    en: 'Personality Test',
    category: 'General',
  },
  [ExamType.CUSTOM]: {
    ja: 'カスタムテスト',
    en: 'Custom Test',
    category: 'General',
  },

  // Japanese Aptitude Tests
  [ExamType.SPI]: {
    ja: 'SPI（総合適性検査）',
    en: 'SPI - Synthetic Personality Inventory',
    category: 'Japanese Aptitude',
  },
  [ExamType.TAMATEBAKO]: {
    ja: '玉手箱（Web適性検査）',
    en: 'Tamatebako - Web Aptitude Test',
    category: 'Japanese Aptitude',
  },
  [ExamType.CAB]: {
    ja: 'CAB（IT適性検査）',
    en: 'CAB - Computer Aptitude Battery',
    category: 'Japanese Aptitude',
  },
  [ExamType.GAB]: {
    ja: 'GAB（総合適性検査）',
    en: 'GAB - General Aptitude Battery',
    category: 'Japanese Aptitude',
  },
  [ExamType.TG_WEB]: {
    ja: 'TG-WEB（適性検査）',
    en: 'TG-WEB Aptitude Test',
    category: 'Japanese Aptitude',
  },
  [ExamType.CUBIC]: {
    ja: 'CUBIC（適性検査）',
    en: 'CUBIC Aptitude & Personality Test',
    category: 'Japanese Aptitude',
  },
  [ExamType.NTT]: {
    ja: 'NTT適性検査',
    en: 'NTT Aptitude Test',
    category: 'Japanese Aptitude',
  },
  [ExamType.KRAEPELIN]: {
    ja: 'クレペリン検査（計算式適性検査）',
    en: 'Kraepelin Test - Psychological Test',
    category: 'Japanese Aptitude',
  },
  [ExamType.SJT]: {
    ja: '状況判断テスト',
    en: 'SJT - Situational Judgment Test',
    category: 'Japanese Aptitude',
  },

  // Technical/Industry-Specific
  [ExamType.PROGRAMMING_APTITUDE]: {
    ja: 'プログラミング適性検査',
    en: 'Programming Aptitude Test',
    category: 'Technical',
  },
  [ExamType.NUMERICAL_ABILITY]: {
    ja: '数理能力検査',
    en: 'Numerical Ability Test',
    category: 'Technical',
  },
  [ExamType.VERBAL_ABILITY]: {
    ja: '言語能力検査',
    en: 'Verbal Ability Test',
    category: 'Technical',
  },
  [ExamType.LOGICAL_THINKING]: {
    ja: '論理思考テスト',
    en: 'Logical Thinking Test',
    category: 'Technical',
  },
};

/**
 * Get exam type label in specified language
 */
export function getExamTypeLabel(type: string, lang: 'ja' | 'en' = 'ja'): string {
  return examTypeLabels[type]?.[lang] || type;
}

/**
 * Get exam type category
 */
export function getExamTypeCategory(type: string): string {
  return examTypeLabels[type]?.category || 'General';
}

/**
 * Get all exam types grouped by category
 */
export function getExamTypesByCategory() {
  const categories: Record<string, Array<{ value: string; label: string }>> = {
    General: [],
    'Japanese Aptitude': [],
    Technical: [],
  };

  Object.entries(examTypeLabels).forEach(([value, { ja, category }]) => {
    if (categories[category]) {
      categories[category].push({ value, label: ja });
    }
  });

  return categories;
}

/**
 * Get all exam types as flat list
 */
export function getAllExamTypes(): Array<{ value: string; label: string; category: string }> {
  return Object.entries(examTypeLabels).map(([value, { ja, category }]) => ({
    value,
    label: ja,
    category,
  }));
}
