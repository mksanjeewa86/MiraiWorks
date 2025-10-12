'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui';
import type { Project, ProjectCreate, ProjectUpdate } from '@/types/profile';
import { X } from 'lucide-react';

interface ProjectModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (data: ProjectCreate | ProjectUpdate) => Promise<void>;
  project?: Project;
  mode: 'create' | 'edit';
}

export default function ProjectModal({
  isOpen,
  onClose,
  onSave,
  project,
  mode,
}: ProjectModalProps) {
  const [formData, setFormData] = useState<ProjectCreate>({
    project_name: '',
    description: null,
    role: null,
    technologies: null,
    project_url: null,
    github_url: null,
    image_urls: null,
    start_date: null,
    end_date: null,
    display_order: 0,
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (project && mode === 'edit') {
      setFormData({
        project_name: project.project_name,
        description: project.description,
        role: project.role,
        technologies: project.technologies,
        project_url: project.project_url,
        github_url: project.github_url,
        image_urls: project.image_urls,
        start_date: project.start_date,
        end_date: project.end_date,
        display_order: project.display_order,
      });
    } else {
      setFormData({
        project_name: '',
        description: null,
        role: null,
        technologies: null,
        project_url: null,
        github_url: null,
        image_urls: null,
        start_date: null,
        end_date: null,
        display_order: 0,
      });
    }
  }, [project, mode, isOpen]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSaving(true);

    try {
      await onSave(formData);
      onClose();
    } catch (err: any) {
      console.error('Failed to save project:', err);
      setError(err.message || 'Failed to save project');
    } finally {
      setSaving(false);
    }
  };

  const handleChange = (field: keyof ProjectCreate, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
            <h2 className="text-xl font-semibold" style={{ color: 'var(--text-primary)' }}>
              {mode === 'create' ? 'Add Project' : 'Edit Project'}
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

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Project Name */}
              <div className="md:col-span-2">
                <label className="block text-sm font-medium mb-1" style={{ color: 'var(--text-primary)' }}>
                  Project Name *
                </label>
                <input
                  type="text"
                  required
                  className="input w-full"
                  value={formData.project_name}
                  onChange={(e) => handleChange('project_name', e.target.value)}
                  placeholder="e.g., E-commerce Platform"
                />
              </div>

              {/* Role */}
              <div className="md:col-span-2">
                <label className="block text-sm font-medium mb-1" style={{ color: 'var(--text-primary)' }}>
                  Your Role
                </label>
                <input
                  type="text"
                  className="input w-full"
                  value={formData.role || ''}
                  onChange={(e) => handleChange('role', e.target.value || null)}
                  placeholder="e.g., Lead Developer, Designer"
                />
              </div>

              {/* Description */}
              <div className="md:col-span-2">
                <label className="block text-sm font-medium mb-1" style={{ color: 'var(--text-primary)' }}>
                  Description
                </label>
                <textarea
                  className="input w-full"
                  rows={4}
                  value={formData.description || ''}
                  onChange={(e) => handleChange('description', e.target.value || null)}
                  placeholder="Describe the project, your contributions, and achievements..."
                />
              </div>

              {/* Technologies */}
              <div className="md:col-span-2">
                <label className="block text-sm font-medium mb-1" style={{ color: 'var(--text-primary)' }}>
                  Technologies Used
                </label>
                <input
                  type="text"
                  className="input w-full"
                  value={formData.technologies || ''}
                  onChange={(e) => handleChange('technologies', e.target.value || null)}
                  placeholder="Separate with commas (e.g., React, Node.js, MongoDB)"
                />
              </div>

              {/* Project URL */}
              <div>
                <label className="block text-sm font-medium mb-1" style={{ color: 'var(--text-primary)' }}>
                  Project URL
                </label>
                <input
                  type="url"
                  className="input w-full"
                  value={formData.project_url || ''}
                  onChange={(e) => handleChange('project_url', e.target.value || null)}
                  placeholder="https://project-demo.com"
                />
              </div>

              {/* GitHub URL */}
              <div>
                <label className="block text-sm font-medium mb-1" style={{ color: 'var(--text-primary)' }}>
                  GitHub URL
                </label>
                <input
                  type="url"
                  className="input w-full"
                  value={formData.github_url || ''}
                  onChange={(e) => handleChange('github_url', e.target.value || null)}
                  placeholder="https://github.com/username/project"
                />
              </div>

              {/* Start Date */}
              <div>
                <label className="block text-sm font-medium mb-1" style={{ color: 'var(--text-primary)' }}>
                  Start Date
                </label>
                <input
                  type="date"
                  className="input w-full"
                  value={formData.start_date || ''}
                  onChange={(e) => handleChange('start_date', e.target.value || null)}
                />
              </div>

              {/* End Date */}
              <div>
                <label className="block text-sm font-medium mb-1" style={{ color: 'var(--text-primary)' }}>
                  End Date
                </label>
                <input
                  type="date"
                  className="input w-full"
                  value={formData.end_date || ''}
                  onChange={(e) => handleChange('end_date', e.target.value || null)}
                />
                <p className="text-xs text-gray-500 mt-1">Leave blank if ongoing</p>
              </div>
            </div>

            {/* Actions */}
            <div className="flex justify-end gap-3 pt-4 border-t border-gray-200 dark:border-gray-700">
              <Button type="button" variant="outline" onClick={onClose} disabled={saving}>
                Cancel
              </Button>
              <Button type="submit" disabled={saving}>
                {saving ? 'Saving...' : mode === 'create' ? 'Add Project' : 'Save Changes'}
              </Button>
            </div>
          </form>
        </div>
      </div>
  );
}
