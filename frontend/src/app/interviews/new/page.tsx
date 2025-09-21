'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowLeft, Save, Calendar, Clock, MapPin, Video, Phone, Users, AlertCircle } from 'lucide-react';
import AppLayout from '@/components/layout/AppLayout';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import { useAuth } from '@/contexts/AuthContext';
import { useToast } from '@/contexts/ToastContext';
import { interviewsApi } from '@/api/interviews';
import type { Interview, InterviewFormData } from '@/types/interview';

function ScheduleInterviewContent() {
  const router = useRouter();
  const { user } = useAuth();
  const { showToast } = useToast();

  const [formData, setFormData] = useState<InterviewFormData>({
    title: '',
    description: '',
    candidate_id: '',
    position_title: '',
    interview_type: 'video',
    scheduled_start: '',
    scheduled_end: '',
    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC',
    location: '',
    meeting_url: '',
    notes: '',
    preparation_notes: ''
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);

  // Initialize form with default times
  useEffect(() => {
    const now = new Date();
    const startTime = new Date(now.getTime() + 60 * 60 * 1000); // 1 hour from now
    const endTime = new Date(startTime.getTime() + 60 * 60 * 1000); // 1 hour duration

    setFormData(prev => ({
      ...prev,
      scheduled_start: startTime.toISOString().slice(0, 16),
      scheduled_end: endTime.toISOString().slice(0, 16)
    }));
  }, []);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));

    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }

    // Auto-adjust end time when start time changes
    if (name === 'scheduled_start' && value) {
      const startTime = new Date(value);
      const endTime = new Date(startTime.getTime() + 60 * 60 * 1000); // 1 hour duration
      setFormData(prev => ({
        ...prev,
        scheduled_end: endTime.toISOString().slice(0, 16)
      }));
    }
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.title.trim()) {
      newErrors.title = 'Interview title is required';
    }

    if (!formData.candidate_id) {
      newErrors.candidate_id = 'Candidate is required';
    }

    if (!formData.scheduled_start) {
      newErrors.scheduled_start = 'Start time is required';
    }

    if (!formData.scheduled_end) {
      newErrors.scheduled_end = 'End time is required';
    }

    if (formData.scheduled_start && formData.scheduled_end) {
      const start = new Date(formData.scheduled_start);
      const end = new Date(formData.scheduled_end);
      if (end <= start) {
        newErrors.scheduled_end = 'End time must be after start time';
      }
    }

    if (formData.interview_type === 'video' && !formData.meeting_url.trim()) {
      newErrors.meeting_url = 'Meeting URL is required for video interviews';
    }

    if (formData.interview_type === 'in_person' && !formData.location.trim()) {
      newErrors.location = 'Location is required for in-person interviews';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    if (!user?.company_id) {
      showToast({
        type: 'error',
        title: 'Error',
        message: 'User company information is missing'
      });
      return;
    }

    setLoading(true);
    try {
      const interviewData: Partial<Interview> = {
        title: formData.title.trim(),
        description: formData.description.trim() || undefined,
        candidate_id: parseInt(formData.candidate_id),
        recruiter_id: user.id,
        employer_company_id: user.company_id,
        position_title: formData.position_title.trim() || undefined,
        interview_type: formData.interview_type,
        scheduled_start: formData.scheduled_start,
        scheduled_end: formData.scheduled_end,
        timezone: formData.timezone,
        location: formData.location.trim() || undefined,
        meeting_url: formData.meeting_url.trim() || undefined,
        notes: formData.notes.trim() || undefined,
        preparation_notes: formData.preparation_notes.trim() || undefined,
        status: 'scheduled'
      };

      await interviewsApi.create(interviewData);

      showToast({
        type: 'success',
        title: 'Interview Scheduled',
        message: 'The interview has been successfully scheduled'
      });

      router.push('/interviews');
    } catch (error) {
      console.error('Error creating interview:', error);
      showToast({
        type: 'error',
        title: 'Error',
        message: error instanceof Error ? error.message : 'Failed to schedule interview'
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <AppLayout>
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="flex items-center mb-8">
          <button
            onClick={() => router.back()}
            className="mr-4 p-2 text-gray-600 hover:text-gray-900 rounded-lg hover:bg-gray-100"
          >
            <ArrowLeft className="h-5 w-5" />
          </button>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Schedule Interview</h1>
            <p className="text-gray-600">Create a new interview session</p>
          </div>
        </div>

        {/* Form */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Basic Information */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Interview Title *
                </label>
                <input
                  type="text"
                  name="title"
                  value={formData.title}
                  onChange={handleInputChange}
                  className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                    errors.title ? 'border-red-300' : 'border-gray-300'
                  }`}
                  placeholder="e.g., Technical Interview - Frontend Developer"
                />
                {errors.title && (
                  <p className="mt-1 text-sm text-red-600 flex items-center">
                    <AlertCircle className="h-4 w-4 mr-1" />
                    {errors.title}
                  </p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Candidate ID *
                </label>
                <input
                  type="number"
                  name="candidate_id"
                  value={formData.candidate_id}
                  onChange={handleInputChange}
                  className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                    errors.candidate_id ? 'border-red-300' : 'border-gray-300'
                  }`}
                  placeholder="Enter candidate ID"
                />
                {errors.candidate_id && (
                  <p className="mt-1 text-sm text-red-600">{errors.candidate_id}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Position Title
                </label>
                <input
                  type="text"
                  name="position_title"
                  value={formData.position_title}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., Senior Frontend Developer"
                />
              </div>
            </div>

            {/* Interview Type */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-3">
                Interview Type *
              </label>
              <div className="grid grid-cols-3 gap-4">
                {[
                  { value: 'video', label: 'Video Call', icon: Video },
                  { value: 'phone', label: 'Phone Call', icon: Phone },
                  { value: 'in_person', label: 'In-Person', icon: Users }
                ].map((type) => (
                  <label key={type.value} className="relative">
                    <input
                      type="radio"
                      name="interview_type"
                      value={type.value}
                      checked={formData.interview_type === type.value}
                      onChange={handleInputChange}
                      className="sr-only"
                    />
                    <div className={`p-4 border-2 rounded-lg cursor-pointer transition-colors ${
                      formData.interview_type === type.value
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}>
                      <type.icon className="h-6 w-6 mx-auto mb-2 text-gray-600" />
                      <p className="text-sm font-medium text-center text-gray-900">{type.label}</p>
                    </div>
                  </label>
                ))}
              </div>
            </div>

            {/* Schedule */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Start Time *
                </label>
                <input
                  type="datetime-local"
                  name="scheduled_start"
                  value={formData.scheduled_start}
                  onChange={handleInputChange}
                  className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                    errors.scheduled_start ? 'border-red-300' : 'border-gray-300'
                  }`}
                />
                {errors.scheduled_start && (
                  <p className="mt-1 text-sm text-red-600">{errors.scheduled_start}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  End Time *
                </label>
                <input
                  type="datetime-local"
                  name="scheduled_end"
                  value={formData.scheduled_end}
                  onChange={handleInputChange}
                  className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                    errors.scheduled_end ? 'border-red-300' : 'border-gray-300'
                  }`}
                />
                {errors.scheduled_end && (
                  <p className="mt-1 text-sm text-red-600">{errors.scheduled_end}</p>
                )}
              </div>
            </div>

            {/* Location/Meeting Details */}
            {formData.interview_type === 'video' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Meeting URL *
                </label>
                <input
                  type="url"
                  name="meeting_url"
                  value={formData.meeting_url}
                  onChange={handleInputChange}
                  className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                    errors.meeting_url ? 'border-red-300' : 'border-gray-300'
                  }`}
                  placeholder="https://zoom.us/j/..."
                />
                {errors.meeting_url && (
                  <p className="mt-1 text-sm text-red-600">{errors.meeting_url}</p>
                )}
              </div>
            )}

            {formData.interview_type === 'in_person' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Location *
                </label>
                <input
                  type="text"
                  name="location"
                  value={formData.location}
                  onChange={handleInputChange}
                  className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                    errors.location ? 'border-red-300' : 'border-gray-300'
                  }`}
                  placeholder="Office address or meeting room"
                />
                {errors.location && (
                  <p className="mt-1 text-sm text-red-600">{errors.location}</p>
                )}
              </div>
            )}

            {formData.interview_type === 'phone' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Phone Details
                </label>
                <input
                  type="text"
                  name="location"
                  value={formData.location}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Phone number or instructions"
                />
              </div>
            )}

            {/* Description */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Description
              </label>
              <textarea
                name="description"
                value={formData.description}
                onChange={handleInputChange}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Brief description of the interview purpose and format"
              />
            </div>

            {/* Notes */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Interview Notes
                </label>
                <textarea
                  name="notes"
                  value={formData.notes}
                  onChange={handleInputChange}
                  rows={4}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Internal notes about the interview"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Preparation Notes
                </label>
                <textarea
                  name="preparation_notes"
                  value={formData.preparation_notes}
                  onChange={handleInputChange}
                  rows={4}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Notes for interview preparation"
                />
              </div>
            </div>

            {/* Submit Buttons */}
            <div className="flex items-center justify-end space-x-3 pt-6 border-t border-gray-200">
              <button
                type="button"
                onClick={() => router.back()}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={loading}
                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
              >
                {loading ? (
                  <div className="h-4 w-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                ) : (
                  <Save className="h-4 w-4" />
                )}
                <span>{loading ? 'Scheduling...' : 'Schedule Interview'}</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </AppLayout>
  );
}

export default function ScheduleInterviewPage() {
  return (
    <ProtectedRoute>
      <ScheduleInterviewContent />
    </ProtectedRoute>
  );
}