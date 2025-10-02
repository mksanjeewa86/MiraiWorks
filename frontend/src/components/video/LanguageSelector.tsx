import React from 'react';
import type { LanguageSelectorProps } from '@/types/components';

export const LanguageSelector: React.FC<LanguageSelectorProps> = ({ value, onChange }) => {
  const languages = [
    { code: 'ja', label: '日本語', flag: '🇯🇵' },
    { code: 'en', label: 'English', flag: '🇺🇸' },
  ];

  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-1">転写言語</label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
      >
        {languages.map((lang) => (
          <option key={lang.code} value={lang.code}>
            {lang.flag} {lang.label}
          </option>
        ))}
      </select>
    </div>
  );
};
