'use client';

import React, { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import DatePicker from 'react-datepicker';
import "react-datepicker/dist/react-datepicker.css";
import '@/styles/datepicker.css';

import { ArrowLeft, Save, Video, Phone, Users, AlertCircle } from 'lucide-react';
import AppLayout from '@/components/layout/AppLayout';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import { useAuth } from '@/contexts/AuthContext';
import { useToast } from '@/contexts/ToastContext';
import { interviewsApi } from '@/api/interviews';
import type { Interview, InterviewEditFormData } from '@/types/interview';

function EditInterviewContent() {
  const params = useParams();
  const router = useRouter();
  const { showToast } = useToast();
  const { user } = useAuth();

  // Check if user can edit interviews (not a candidate)
  const canEditInterviews = () => {
    if (!user || !user.roles) return false;
    const isCandidate = user.roles.some((userRole) => userRole.role.name === 'candidate');
    return !isCandidate && user.roles.length > 0;
  };

  // Redirect if user cannot edit interviews
  useEffect(() => {
    if (user && !canEditInterviews()) {
      router.push('/interviews');
    }
  }, [user, router]);

  const [originalInterview, setOriginalInterview] = useState<Interview | null>(null);
  const [formData, setFormData] = useState<InterviewEditFormData>({
    title: '',
    description: '',
    position_title: '',
    interview_type: 'video',
    scheduled_start: '',
    scheduled_end: '',
    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC',
    location: '',
    meeting_url: '',
    notes: '',
    preparation_notes: '',
    status: 'scheduled',
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string>('');

  const interviewId = typeof params.id === 'string' ? parseInt(params.id) : null;

  useEffect(() => {
    if (!interviewId) {
      setError('Invalid interview ID');
      setLoading(false);
      return;
    }

    const fetchInterview = async () => {
      try {
        setLoading(true);
        const response = await interviewsApi.getById(interviewId);
        const interview = response.data;

        if (!interview) {
          throw new Error('Interview not found');
        }

        setOriginalInterview(interview);

        // Convert ISO strings to datetime-local format
        const formatDateTimeLocal = (dateTime?: string) => {
          if (!dateTime) return '';
          return new Date(dateTime).toISOString().slice(0, 16);
        };

        setFormData({
          title: interview.title || '',
          description: interview.description || '',
          position_title: interview.position_title || '',
          interview_type: interview.interview_type || 'video',
          scheduled_start: formatDateTimeLocal(interview.scheduled_start),
          scheduled_end: formatDateTimeLocal(interview.scheduled_end),
          timezone: interview.timezone || Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC',
          location: interview.location || '',
          meeting_url: interview.meeting_url || '',
          notes: interview.notes || '',
          preparation_notes: interview.preparation_notes || '',
          status: interview.status || 'scheduled',
        });
      } catch (err) {
        console.error('Error fetching interview:', err);
        setError(err instanceof Error ? err.message : 'Failed to fetch interview details');
      } finally {
        setLoading(false);
      }
    };

    fetchInterview();
  }, [interviewId]);

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));

    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: '' }));
    }

    if (name === 'video_call_type' && value === 'system_generated') {
      setFormData((prev) => ({ ...prev, meeting_url: '' }));
      if (errors.meeting_url) {
        setErrors((prev) => ({ ...prev, meeting_url: '' }));
      }
    }

    if (name === 'interview_type' && value !== 'video') {
      setFormData((prev) => ({
        ...prev,
        video_call_type: 'system_generated',
        meeting_url: '',
      }));
      if (errors.meeting_url) {
        setErrors((prev) => ({ ...prev, meeting_url: '' }));
      }
    }
  };

  const handleScheduleChange = (field: 'scheduled_start' | 'scheduled_end') => (value: string | null) => {
    const normalized = value ?? '';
    setFormData((prev) => {
      const next = { ...prev, [field]: normalized };

      if (field === 'scheduled_start' && normalized) {
        const startTime = new Date(normalized);
        if (!Number.isNaN(startTime.getTime())) {
          const previousStart = prev.scheduled_start ? new Date(prev.scheduled_start) : null;
          const previousEnd = prev.scheduled_end ? new Date(prev.scheduled_end) : null;

          let duration = 60 * 60 * 1000;
          if (previousStart && !Number.isNaN(previousStart.getTime()) && previousEnd && !Number.isNaN(previousEnd.getTime())) {
            const diff = previousEnd.getTime() - previousStart.getTime();
            if (diff > 0) {
              duration = diff;
            }
          }

          const newEnd = new Date(startTime.getTime() + duration);
          next.scheduled_end = newEnd.toISOString().slice(0, 16);
        }
      }

      return next;
    });

    setErrors((prev) => ({
      ...prev,
      [field]: '',
      ...(field === 'scheduled_start' ? { scheduled_end: '' } : {}),
    }));
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.title.trim()) {
      newErrors.title = 'Interview title is required';
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

    if (!validateForm() || !originalInterview) {
      return;
    }

    setSaving(true);
    try {
      const updateData: Partial<Interview> = {
        title: formData.title.trim(),
        description: formData.description.trim() || undefined,
        position_title: formData.position_title.trim() || undefined,
        interview_type: formData.interview_type,
        scheduled_start: formData.scheduled_start,
        scheduled_end: formData.scheduled_end,
        timezone: formData.timezone,
        location: formData.location.trim() || undefined,
        meeting_url: formData.meeting_url.trim() || undefined,
        notes: formData.notes.trim() || undefined,
        preparation_notes: formData.preparation_notes.trim() || undefined,
        status: formData.status,
      };

      await interviewsApi.update(originalInterview.id, updateData);

      showToast({
        type: 'success',
        title: 'Interview Updated',
        message: 'The interview has been successfully updated',
      });

      router.push(`/interviews/${originalInterview.id}`);
    } catch (error) {
      console.error('Error updating interview:', error);
      showToast({
        type: 'error',
        title: 'Error',
        message: error instanceof Error ? error.message : 'Failed to update interview',
      });
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <AppLayout>
        <div className="min-h-screen bg-gray-50 flex items-center justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-2 text-gray-600">Loading interview...</span>
        </div>
      </AppLayout>
    );
  }

  if (error || !originalInterview) {
    return (
      <AppLayout>
        <div className="min-h-screen bg-gray-50 flex items-center justify-center">
          <div className="text-center">
            <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-gray-900 mb-2">Interview Not Found</h2>
            <p className="text-gray-600 mb-4">
              {error || 'The interview you are trying to edit could not be found.'}
            </p>
            <button
              onClick={() => router.back()}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg inline-flex items-center gap-2"
            >
              <ArrowLeft className="h-4 w-4" />
              Go Back
            </button>
          </div>
        </div>
      </AppLayout>
    );
  }

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
            <h1 className="text-2xl font-bold text-gray-900">Edit Interview</h1>
            <p className="text-gray-600">Update interview details</p>
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

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Status</label>
                <select
                  name="status"
                  value={formData.status}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 pr-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent appearance-none bg-white"
                  style={{
                    backgroundImage: `url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M6 8l4 4 4-4'/%3e%3c/svg%3e")`,
                    backgroundPosition: 'right 12px center',
                    backgroundRepeat: 'no-repeat',
                    backgroundSize: '16px',
                  }}
                >
                  <option value="pending_schedule">Pending Schedule</option>
                  <option value="scheduled">Scheduled</option>
                  <option value="confirmed">Confirmed</option>
                  <option value="in_progress">In Progress</option>
                  <option value="completed">Completed</option>
                  <option value="cancelled">Cancelled</option>
                </select>
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
                  { value: 'in_person', label: 'In-Person', icon: Users },
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
                    <div
                      className={`p-4 border-2 rounded-lg cursor-pointer transition-colors ${
                        formData.interview_type === type.value
                          ? 'border-blue-500 bg-blue-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <type.icon className="h-6 w-6 mx-auto mb-2 text-gray-600" />
                      <p className="text-sm font-medium text-center text-gray-900">{type.label}</p>
                    </div>
                  </label>
                ))}
              </div>
            </div>

            {/* Schedule */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <label className={`block text-sm font-medium ${errors.scheduled_start ? 'text-red-700' : 'text-gray-700'}`}>
                  Start Time *
                </label>
                <DatePicker
                  selected={formData.scheduled_start ? new Date(formData.scheduled_start) : null}
                  onChange={(date) => {
                    if (date) {
                      const formatted = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}T${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`;
                      handleScheduleChange('scheduled_start')(formatted);
                    }
                  }}
                  showTimeSelect
                  timeFormat="HH:mm"
                  timeIntervals={15}
                  dateFormat="yyyy-MM-dd HH:mm"
                  placeholderText="Select start time"
                  className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                    errors.scheduled_start ? 'border-red-300' : 'border-gray-300'
                  }`}
                />
                {errors.scheduled_start && (
                  <p className="mt-1 text-sm text-red-600 flex items-center">
                    <AlertCircle className="h-4 w-4 mr-1" />
                    {errors.scheduled_start}
                  </p>
                )}
              </div>
              <div className="space-y-2">
                <label className={`block text-sm font-medium ${errors.scheduled_end ? 'text-red-700' : 'text-gray-700'}`}>
                  End Time *
                </label>
                <DatePicker
                  selected={formData.scheduled_end ? new Date(formData.scheduled_end) : null}
                  onChange={(date) => {
                    if (date) {
                      const formatted = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}T${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`;
                      handleScheduleChange('scheduled_end')(formatted);
                    }
                  }}
                  showTimeSelect
                  timeFormat="HH:mm"
                  timeIntervals={15}
                  dateFormat="yyyy-MM-dd HH:mm"
                  placeholderText="Select end time"
                  className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                    errors.scheduled_end ? 'border-red-300' : 'border-gray-300'
                  }`}
                />
                {errors.scheduled_end && (
                  <p className="mt-1 text-sm text-red-600 flex items-center">
                    <AlertCircle className="h-4 w-4 mr-1" />
                    {errors.scheduled_end}
                  </p>
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
                <label className="block text-sm font-medium text-gray-700 mb-2">Location *</label>
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
                {errors.location && <p className="mt-1 text-sm text-red-600">{errors.location}</p>}
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
              <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
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
                disabled={saving}
                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
              >
                {saving ? (
                  <div className="h-4 w-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                ) : (
                  <Save className="h-4 w-4" />
                )}
                <span>{saving ? 'Saving...' : 'Save Changes'}</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </AppLayout>
  );
}

export default function EditInterviewPage() {
  return (
    <ProtectedRoute>
      <EditInterviewContent />
    </ProtectedRoute>
  );
}


