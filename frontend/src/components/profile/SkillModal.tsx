'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui';
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import type { Skill, SkillCreate, SkillUpdate } from '@/types/profile';
import { X, Zap } from 'lucide-react';

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

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent
        closeButton={false}
        className="flex flex-col max-h-[90vh] w-full max-w-4xl md:max-w-3xl overflow-hidden rounded-3xl border border-slate-200 bg-white text-slate-900 shadow-[0_30px_80px_-20px_rgba(15,23,42,0.2)]"
      >
        <DialogHeader className="flex-shrink-0 px-6 pt-6">
          <div className="flex items-start justify-between gap-4">
            <div className="space-y-3">
              <div className="flex items-center gap-3">
                <span className="inline-flex h-10 w-10 items-center justify-center rounded-full bg-teal-100 text-teal-600">
                  <Zap className="h-5 w-5" />
                </span>
                <div>
                  <DialogTitle className="text-xl font-semibold text-slate-900">
                    {mode === 'create' ? 'Add Skill' : 'Edit Skill'}
                  </DialogTitle>
                  <DialogDescription className="text-sm text-slate-500">
                    {mode === 'create'
                      ? 'Add your skills and expertise to showcase your capabilities.'
                      : 'Update your skill details and proficiency level.'}
                  </DialogDescription>
                </div>
              </div>
            </div>
            <DialogClose className="rounded-lg border border-slate-200 p-2 text-slate-500 transition hover:bg-slate-100 hover:text-slate-700">
              <X className="h-4 w-4" />
            </DialogClose>
          </div>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="flex flex-1 flex-col min-h-0">
          <div className="flex-1 overflow-y-auto px-6 py-4 min-h-0">
            <div className="space-y-4">
              {error && (
                <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm">
                  {error}
                </div>
              )}

              <div className="grid gap-6 rounded-2xl border border-slate-200 bg-slate-50 p-6">
                {/* Skill Name */}
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Skill Name *
                  </label>
                  <input
                    type="text"
                    required
                    className="w-full border-slate-300 bg-white text-slate-900 rounded-md px-3 py-2"
                    value={formData.skill_name}
                    onChange={(e) => handleChange('skill_name', e.target.value)}
                    placeholder="e.g., Python, React, Project Management"
                  />
                  <p className="text-xs text-slate-500 mt-1">
                    Enter a specific skill, technology, or competency
                  </p>
                </div>

                {/* Category & Proficiency Level */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">
                      Category
                    </label>
                    <select
                      className="w-full border-slate-300 bg-white text-slate-900 rounded-md px-3 py-2"
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
                    <p className="text-xs text-slate-500 mt-1">
                      Classify your skill type
                    </p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">
                      Proficiency Level
                    </label>
                    <select
                      className="w-full border-slate-300 bg-white text-slate-900 rounded-md px-3 py-2"
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
                    <p className="text-xs text-slate-500 mt-1">
                      Rate your current skill level
                    </p>
                  </div>
                </div>

                {/* Years of Experience */}
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Years of Experience
                  </label>
                  <input
                    type="number"
                    min="0"
                    max="50"
                    className="w-full border-slate-300 bg-white text-slate-900 rounded-md px-3 py-2"
                    value={formData.years_of_experience || ''}
                    onChange={(e) => handleChange('years_of_experience', e.target.value ? parseInt(e.target.value) : null)}
                    placeholder="e.g., 5"
                  />
                  <p className="text-xs text-slate-500 mt-1">
                    How many years have you worked with this skill?
                  </p>
                </div>
              </div>
            </div>
          </div>

          <DialogFooter className="flex-shrink-0 gap-3 border-t border-slate-200 bg-white px-6 py-4">
            <div className="flex w-full items-center justify-end gap-3">
              <Button
                type="button"
                variant="ghost"
                onClick={onClose}
                disabled={saving}
                className="min-w-[120px] border border-slate-300 bg-white text-slate-600 hover:bg-slate-100"
              >
                Cancel
              </Button>
              <Button
                type="submit"
                disabled={saving}
                className="min-w-[160px] bg-blue-600 text-white shadow-lg shadow-blue-500/30 hover:bg-blue-600/90"
              >
                {saving ? 'Saving...' : mode === 'create' ? 'Add Skill' : 'Save Changes'}
              </Button>
            </div>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
