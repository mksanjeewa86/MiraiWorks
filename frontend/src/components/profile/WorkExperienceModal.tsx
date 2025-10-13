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
import type { WorkExperience, WorkExperienceCreate, WorkExperienceUpdate } from '@/types/profile';
import { X, Briefcase } from 'lucide-react';

interface WorkExperienceModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (data: WorkExperienceCreate | WorkExperienceUpdate) => Promise<void>;
  onDelete?: (id: number) => Promise<void>;
  experience?: WorkExperience;
  mode: 'create' | 'edit';
}

export default function WorkExperienceModal({
  isOpen,
  onClose,
  onSave,
  onDelete,
  experience,
  mode,
}: WorkExperienceModalProps) {
  const [formData, setFormData] = useState<WorkExperienceCreate>({
    company_name: '',
    position_title: '',
    employment_type: 'Full-time',
    location: '',
    start_date: '',
    end_date: null,
    is_current: false,
    description: '',
    skills: '',
    company_logo_url: null,
    display_order: 0,
  });
  const [saving, setSaving] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (experience && mode === 'edit') {
      setFormData({
        company_name: experience.company_name,
        position_title: experience.position_title,
        employment_type: experience.employment_type,
        location: experience.location,
        start_date: experience.start_date,
        end_date: experience.end_date,
        is_current: experience.is_current,
        description: experience.description,
        skills: experience.skills,
        company_logo_url: experience.company_logo_url,
        display_order: experience.display_order,
      });
    } else {
      setFormData({
        company_name: '',
        position_title: '',
        employment_type: 'Full-time',
        location: '',
        start_date: '',
        end_date: null,
        is_current: false,
        description: '',
        skills: '',
        company_logo_url: null,
        display_order: 0,
      });
    }
  }, [experience, mode, isOpen]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSaving(true);

    try {
      await onSave(formData);
      onClose();
    } catch (err: any) {
      console.error('Failed to save work experience:', err);
      setError(err.message || 'Failed to save work experience');
    } finally {
      setSaving(false);
    }
  };

  const handleChange = (field: keyof WorkExperienceCreate, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleDelete = async () => {
    if (!experience?.id || !onDelete) return;

    const confirmed = confirm('Are you sure you want to delete this work experience? This action cannot be undone.');
    if (!confirmed) return;

    setDeleting(true);
    setError(null);

    try {
      await onDelete(experience.id);
      onClose();
    } catch (err: any) {
      console.error('Failed to delete work experience:', err);
      setError(err.message || 'Failed to delete work experience');
    } finally {
      setDeleting(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent
        closeButton={false}
        className="flex flex-col h-[90vh] max-h-[90vh] w-full max-w-4xl md:max-w-3xl overflow-hidden rounded-3xl border border-slate-200 bg-white text-slate-900 shadow-[0_30px_80px_-20px_rgba(15,23,42,0.2)]"
      >
        <DialogHeader className="flex-shrink-0 px-6 pt-6">
          <div className="flex items-start justify-between gap-4">
            <div className="space-y-3">
              <div className="flex items-center gap-3">
                <span className="inline-flex h-10 w-10 items-center justify-center rounded-full bg-blue-100 text-blue-600">
                  <Briefcase className="h-5 w-5" />
                </span>
                <div>
                  <DialogTitle className="text-xl font-semibold text-slate-900">
                    {mode === 'create' ? 'Add Work Experience' : 'Edit Work Experience'}
                  </DialogTitle>
                  <DialogDescription className="text-sm text-slate-500">
                    {mode === 'create'
                      ? 'Add your professional work experience to showcase your career journey.'
                      : 'Update your work experience details and responsibilities.'}
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
          <div className="flex-1 overflow-y-auto px-6 py-6 min-h-0">
            <div className="space-y-8">
              {error && (
                <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm">
                  {error}
                </div>
              )}

              <div className="grid gap-6 rounded-2xl border border-slate-200 bg-slate-50 p-6">
                {/* Company Name */}
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Company Name *
                  </label>
                  <input
                    type="text"
                    required
                    className="w-full border-slate-300 bg-white text-slate-900 rounded-md px-3 py-2"
                    value={formData.company_name}
                    onChange={(e) => handleChange('company_name', e.target.value)}
                  />
                </div>

                {/* Position Title */}
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Position Title *
                  </label>
                  <input
                    type="text"
                    required
                    className="w-full border-slate-300 bg-white text-slate-900 rounded-md px-3 py-2"
                    value={formData.position_title}
                    onChange={(e) => handleChange('position_title', e.target.value)}
                  />
                </div>

                {/* Employment Type & Location */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">
                      Employment Type
                    </label>
                    <select
                      className="w-full border-slate-300 bg-white text-slate-900 rounded-md px-3 py-2"
                      value={formData.employment_type || ''}
                      onChange={(e) => handleChange('employment_type', e.target.value)}
                    >
                      <option value="Full-time">Full-time</option>
                      <option value="Part-time">Part-time</option>
                      <option value="Contract">Contract</option>
                      <option value="Freelance">Freelance</option>
                      <option value="Internship">Internship</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">
                      Location
                    </label>
                    <input
                      type="text"
                      className="w-full border-slate-300 bg-white text-slate-900 rounded-md px-3 py-2"
                      value={formData.location || ''}
                      onChange={(e) => handleChange('location', e.target.value)}
                      placeholder="e.g., San Francisco, CA"
                    />
                  </div>
                </div>

                {/* Start Date & End Date */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">
                      Start Date *
                    </label>
                    <input
                      type="date"
                      required
                      className="w-full border-slate-300 bg-white text-slate-900 rounded-md px-3 py-2"
                      value={formData.start_date}
                      onChange={(e) => handleChange('start_date', e.target.value)}
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">
                      End Date
                    </label>
                    <input
                      type="date"
                      className="w-full border-slate-300 bg-white text-slate-900 rounded-md px-3 py-2"
                      value={formData.end_date || ''}
                      onChange={(e) => handleChange('end_date', e.target.value || null)}
                      disabled={formData.is_current}
                    />
                  </div>
                </div>

                {/* Currently Working */}
                <div>
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={formData.is_current}
                      onChange={(e) => {
                        handleChange('is_current', e.target.checked);
                        if (e.target.checked) {
                          handleChange('end_date', null);
                        }
                      }}
                      className="h-4 w-4 rounded border-slate-300"
                    />
                    <span className="text-sm font-medium text-slate-700">
                      I currently work here
                    </span>
                  </label>
                </div>

                {/* Description */}
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Description
                  </label>
                  <textarea
                    className="w-full border border-slate-300 bg-white text-slate-900 rounded-md px-3 py-2 focus-visible:ring-blue-500"
                    rows={4}
                    value={formData.description || ''}
                    onChange={(e) => handleChange('description', e.target.value)}
                    placeholder="Describe your responsibilities and achievements..."
                  />
                  <p className="text-xs text-slate-500 mt-1">
                    Highlight your key responsibilities and major achievements
                  </p>
                </div>

                {/* Skills */}
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Skills Used
                  </label>
                  <input
                    type="text"
                    className="w-full border-slate-300 bg-white text-slate-900 rounded-md px-3 py-2"
                    value={formData.skills || ''}
                    onChange={(e) => handleChange('skills', e.target.value)}
                    placeholder="Python, React, SQL"
                  />
                  <p className="text-xs text-slate-500 mt-1">
                    Separate skills with commas
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
                {saving ? 'Saving...' : mode === 'create' ? 'Add Experience' : 'Save Changes'}
              </Button>
            </div>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
