'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui';
import type { Skill, SkillCreate, SkillUpdate } from '@/types/profile';
import { X } from 'lucide-react';

interface SkillModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (data: SkillCreate | SkillUpdate) => Promise<void>;
  skill?: Skill;
  mode: 'create' | 'edit';
}

export default function SkillModal({
  isOpen,
  onClose,
  onSave,
  skill,
  mode,
}: SkillModalProps) {
  const [formData, setFormData] = useState<SkillCreate>({
    skill_name: '',
    category: null,
    proficiency_level: null,
    years_of_experience: null,
    endorsement_count: 0,
    display_order: 0,
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (skill && mode === 'edit') {
      setFormData({
        skill_name: skill.skill_name,
        category: skill.category,
        proficiency_level: skill.proficiency_level,
        years_of_experience: skill.years_of_experience,
        endorsement_count: skill.endorsement_count,
        display_order: skill.display_order,
      });
    } else {
      setFormData({
        skill_name: '',
        category: null,
        proficiency_level: null,
        years_of_experience: null,
        endorsement_count: 0,
        display_order: 0,
      });
    }
  }, [skill, mode, isOpen]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSaving(true);

    try {
      await onSave(formData);
      onClose();
    } catch (err: any) {
      console.error('Failed to save skill:', err);
      setError(err.message || 'Failed to save skill');
    } finally {
      setSaving(false);
    }
  };

  const handleChange = (field: keyof SkillCreate, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
            <h2 className="text-xl font-semibold" style={{ color: 'var(--text-primary)' }}>
              {mode === 'create' ? 'Add Skill' : 'Edit Skill'}
            </h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            >
              <X className="h-6 w-6" />
            </button>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="p-6 space-y-4">
            {error && (
              <div className="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded text-red-600 dark:text-red-400 text-sm">
                {error}
              </div>
            )}

            {/* Skill Name */}
            <div>
              <label className="block text-sm font-medium mb-1" style={{ color: 'var(--text-primary)' }}>
                Skill Name *
              </label>
              <input
                type="text"
                required
                className="input w-full"
                value={formData.skill_name}
                onChange={(e) => handleChange('skill_name', e.target.value)}
                placeholder="e.g., Python, React, Project Management"
              />
            </div>

            {/* Category */}
            <div>
              <label className="block text-sm font-medium mb-1" style={{ color: 'var(--text-primary)' }}>
                Category
              </label>
              <select
                className="input w-full"
                value={formData.category || ''}
                onChange={(e) => handleChange('category', e.target.value || null)}
              >
                <option value="">Select Category</option>
                <option value="Technical">Technical</option>
                <option value="Soft Skill">Soft Skill</option>
                <option value="Language">Language</option>
                <option value="Tool">Tool</option>
                <option value="Framework">Framework</option>
                <option value="Other">Other</option>
              </select>
            </div>

            {/* Proficiency Level */}
            <div>
              <label className="block text-sm font-medium mb-1" style={{ color: 'var(--text-primary)' }}>
                Proficiency Level
              </label>
              <select
                className="input w-full"
                value={formData.proficiency_level || ''}
                onChange={(e) => handleChange('proficiency_level', e.target.value || null)}
              >
                <option value="">Select Level</option>
                <option value="Beginner">Beginner</option>
                <option value="Intermediate">Intermediate</option>
                <option value="Advanced">Advanced</option>
                <option value="Expert">Expert</option>
                <option value="Native">Native (for languages)</option>
              </select>
            </div>

            {/* Years of Experience */}
            <div>
              <label className="block text-sm font-medium mb-1" style={{ color: 'var(--text-primary)' }}>
                Years of Experience
              </label>
              <input
                type="number"
                min="0"
                max="50"
                className="input w-full"
                value={formData.years_of_experience || ''}
                onChange={(e) => handleChange('years_of_experience', e.target.value ? parseInt(e.target.value) : null)}
                placeholder="e.g., 5"
              />
            </div>

            {/* Actions */}
            <div className="flex justify-end gap-3 pt-4 border-t border-gray-200 dark:border-gray-700">
              <Button type="button" variant="outline" onClick={onClose} disabled={saving}>
                Cancel
              </Button>
              <Button type="submit" disabled={saving}>
                {saving ? 'Saving...' : mode === 'create' ? 'Add Skill' : 'Save Changes'}
              </Button>
            </div>
          </form>
        </div>
      </div>
  );
}
