'use client';

import React, { useState, useEffect, useRef } from 'react';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';
import '@/styles/datepicker.css';

import { Save, Video, Phone, Users, AlertCircle, X, Search, ChevronDown } from 'lucide-react';
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui';
import { Button } from '@/components/ui';
import { Input } from '@/components/ui';
import { Textarea } from '@/components/ui';
import { useAuth } from '@/contexts/AuthContext';
import { useToast } from '@/contexts/ToastContext';
import { interviewsApi } from '@/api/interviews';
import { candidatesApi } from '@/api/candidates';
import type { Interview, InterviewFormData } from '@/types/interview';
import type { UserManagement } from '@/types/user';
import type { InterviewModalProps } from '@/types/components';

export default function InterviewModal({
  isOpen,
  mode,
  interviewId,
  onClose,
  onSuccess,
  defaultData,
  workflowContext = false,
}: InterviewModalProps) {
  const { user } = useAuth();
  const { showToast } = useToast();

  // Form state
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
    video_call_type: 'system_generated',
    notes: '',
    preparation_notes: '',
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);

  // Candidate selection state
  const [candidates, setCandidates] = useState<UserManagement[]>([]);
  const [candidatesLoading, setCandidatesLoading] = useState(true);
  const [candidateSearch, setCandidateSearch] = useState('');
  const [showCandidateDropdown, setShowCandidateDropdown] = useState(false);
  const candidateDropdownRef = useRef<HTMLDivElement>(null);

  // Initialize form with default times
  useEffect(() => {
    if (!isOpen) return;

    const now = new Date();
    const startTime = new Date(now.getTime() + 60 * 60 * 1000); // 1 hour from now
    const endTime = new Date(startTime.getTime() + 60 * 60 * 1000); // 1 hour duration

    if (mode === 'create') {
      setFormData((prev) => ({
        ...prev,
        ...defaultData,
        scheduled_start: defaultData?.scheduled_start || startTime.toISOString().slice(0, 16),
        scheduled_end: defaultData?.scheduled_end || endTime.toISOString().slice(0, 16),
      }));
    }
  }, [isOpen, mode, defaultData]);

  // Fetch interview data in edit mode
  useEffect(() => {
    if (!isOpen || mode !== 'edit' || !interviewId) return;

    const fetchInterview = async () => {
      try {
        setLoading(true);
        const response = await interviewsApi.getById(interviewId);
        const interview = response.data;

        if (!interview) {
          throw new Error('Interview not found');
        }

        // Convert ISO strings to datetime-local format
        const formatDateTimeLocal = (dateTime?: string) => {
          if (!dateTime) return '';
          return new Date(dateTime).toISOString().slice(0, 16);
        };

        setFormData({
          title: interview.title || '',
          description: interview.description || '',
          candidate_id: interview.candidate_id?.toString() || '',
          position_title: interview.position_title || '',
          interview_type: interview.interview_type || 'video',
          scheduled_start: formatDateTimeLocal(interview.scheduled_start),
          scheduled_end: formatDateTimeLocal(interview.scheduled_end),
          timezone: interview.timezone || Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC',
          location: interview.location || '',
          meeting_url: interview.meeting_url || '',
          video_call_type: interview.video_call_type || 'system_generated',
          notes: interview.notes || '',
          preparation_notes: interview.preparation_notes || '',
        });

        // Set candidate search display
        if (interview.candidate) {
          setCandidateSearch(`${interview.candidate.full_name} (${interview.candidate.email})`);
        }
      } catch (error) {
        console.error('Error fetching interview:', error);
        showToast({
          type: 'error',
          title: 'Failed to load interview details',
        });
      } finally {
        setLoading(false);
      }
    };

    fetchInterview();
  }, [isOpen, mode, interviewId, showToast]);

  // Fetch candidates list
  useEffect(() => {
    if (!isOpen) return;

    const fetchCandidates = async () => {
      try {
        setCandidatesLoading(true);
        const response = await candidatesApi.getCandidates({
          is_active: true,
          size: 100,
        });

        if (response.success && response.data) {
          setCandidates(response.data.users || []);
        }
      } catch (error) {
        console.error('Error fetching candidates:', error);
      } finally {
        setCandidatesLoading(false);
      }
    };

    fetchCandidates();
  }, [isOpen]);

  // Handle click outside to close candidate dropdown
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        candidateDropdownRef.current &&
        !candidateDropdownRef.current.contains(event.target as Node)
      ) {
        setShowCandidateDropdown(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  // Filter candidates based on search
  const filteredCandidates = candidates.filter((candidate) => {
    const searchLower = candidateSearch.toLowerCase();
    const fullName = `${candidate.first_name} ${candidate.last_name}`.toLowerCase();
    const email = candidate.email.toLowerCase();
    return fullName.includes(searchLower) || email.includes(searchLower);
  });

  // Handle candidate selection
  const handleCandidateSelect = (candidate: UserManagement) => {
    setFormData((prev) => ({ ...prev, candidate_id: candidate.id.toString() }));
    setCandidateSearch(`${candidate.first_name} ${candidate.last_name} (${candidate.email})`);
    setShowCandidateDropdown(false);

    if (errors.candidate_id) {
      setErrors((prev) => ({ ...prev, candidate_id: '' }));
    }
  };

  // Handle clear candidate selection
  const handleClearCandidate = () => {
    setFormData((prev) => ({ ...prev, candidate_id: '' }));
    setCandidateSearch('');
    setShowCandidateDropdown(false);
  };

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));

    // Clear error when user starts typing
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: '' }));
    }

    // Auto-adjust end time when start time changes
    if (name === 'scheduled_start' && value) {
      const startTime = new Date(value);
      const endTime = new Date(startTime.getTime() + 60 * 60 * 1000);
      setFormData((prev) => ({
        ...prev,
        scheduled_end: endTime.toISOString().slice(0, 16),
      }));
    }

    // Clear meeting URL when switching to system generated
    if (name === 'video_call_type' && value === 'system_generated') {
      setFormData((prev) => ({ ...prev, meeting_url: '' }));
      if (errors.meeting_url) {
        setErrors((prev) => ({ ...prev, meeting_url: '' }));
      }
    }

    // Reset video call type when changing from video to other interview types
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

  const handleScheduleChange =
    (field: 'scheduled_start' | 'scheduled_end') => (date: Date | null) => {
      if (!date) {
        setFormData((prev) => ({ ...prev, [field]: '' }));
        return;
      }

      // Use local time without timezone conversion
      const formatted = date.toISOString();
      setFormData((prev) => {
        const next = { ...prev, [field]: formatted };
        if (field === 'scheduled_start') {
          const newEnd = new Date(date.getTime() + 60 * 60 * 1000);
          next.scheduled_end = newEnd.toISOString();
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

    if (
      formData.interview_type === 'video' &&
      formData.video_call_type === 'custom_url' &&
      !formData.meeting_url.trim()
    ) {
      newErrors.meeting_url = 'Meeting URL is required when using custom URL option';
    }

    if (formData.interview_type === 'in_person' && !formData.location.trim()) {
      newErrors.location = 'Location is required for in-person interviews';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();

    if (!validateForm()) {
      showToast({
        type: 'error',
        title: 'Please fill in all required fields',
      });
      return;
    }

    // If in workflow context, just return the form data without saving to DB
    if (workflowContext) {
      onSuccess(formData);
      onClose();
      return;
    }

    if (!user) {
      showToast({
        type: 'error',
        title: 'User session not found. Please refresh and try again.',
      });
      return;
    }

    const companyId = user.company_id || 1;

    setSaving(true);
    try {
      let meetingUrl = formData.meeting_url.trim() || undefined;

      if (formData.interview_type === 'video' && formData.video_call_type === 'system_generated') {
        meetingUrl = `${window.location.origin}/video-call/PLACEHOLDER_ID`;
      }

      const interviewData: Partial<Interview> = {
        title: formData.title.trim(),
        description: formData.description.trim() || undefined,
        candidate_id: parseInt(formData.candidate_id),
        recruiter_id: user.id,
        employer_company_id: companyId,
        position_title: formData.position_title.trim() || undefined,
        interview_type: formData.interview_type,
        scheduled_start: formData.scheduled_start,
        scheduled_end: formData.scheduled_end,
        timezone: formData.timezone,
        location: formData.location.trim() || undefined,
        meeting_url: meetingUrl,
        video_call_type: formData.interview_type === 'video' ? formData.video_call_type : undefined,
        notes: formData.notes.trim() || undefined,
        preparation_notes: formData.preparation_notes.trim() || undefined,
        status: 'scheduled',
      };

      let result;
      if (mode === 'edit' && interviewId) {
        result = await interviewsApi.update(interviewId, interviewData);
      } else {
        result = await interviewsApi.create(interviewData);
      }

      showToast({
        type: 'success',
        title:
          mode === 'edit' ? 'Interview updated successfully' : 'Interview scheduled successfully',
      });

      if (result.data) {
        onSuccess(result.data);
      }
      onClose();
    } catch (error) {
      console.error('Error saving interview:', error);
      showToast({
        type: 'error',
        title: error instanceof Error ? error.message : 'Failed to save interview',
      });
    } finally {
      setSaving(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent
        closeButton={false}
        className="flex flex-col h-[90vh] max-h-[90vh] w-full max-w-4xl md:max-w-3xl overflow-hidden"
      >
        <DialogHeader className="flex-shrink-0 px-6 pt-6">
          <div className="flex items-start justify-between gap-4">
            <div className="space-y-1">
              <DialogTitle className="flex items-center gap-2 text-xl font-semibold">
                <Video className="h-5 w-5 text-blue-600" />
                {mode === 'edit' ? 'Edit Interview' : 'Schedule Interview'}
              </DialogTitle>
              <DialogDescription className="text-sm">
                {mode === 'edit' ? 'Update interview details' : 'Create a new interview session'}
              </DialogDescription>
            </div>
            <DialogClose className="rounded-lg border border-slate-200 p-2 text-slate-500 transition hover:bg-slate-100 hover:text-slate-700">
              <X className="h-4 w-4" />
            </DialogClose>
          </div>
        </DialogHeader>

        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="h-8 w-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
          </div>
        ) : (
          <div className="flex-1 overflow-y-auto px-6 py-6 min-h-0">
            <div className="space-y-6">
              {/* Single Column Layout */}
              <div className="space-y-6">
                {/* Interview Details Section */}
                <div className="space-y-4">
                  <div>
                    <h3 className="text-base font-semibold text-gray-900 mb-3">
                      Interview Details
                    </h3>
                  </div>

                  {/* Interview Title */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1.5">
                      Interview Title *
                    </label>
                    <Input
                      type="text"
                      name="title"
                      value={formData.title}
                      onChange={handleInputChange}
                      className={errors.title ? 'border-red-300' : ''}
                      placeholder="e.g., Technical Interview"
                    />
                    {errors.title && (
                      <p className="mt-1 text-xs text-red-600 flex items-center">
                        <AlertCircle className="h-3 w-3 mr-1" />
                        {errors.title}
                      </p>
                    )}
                  </div>

                  {/* Select Candidate */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1.5">
                      Select Candidate *
                    </label>
                    <div className="relative" ref={candidateDropdownRef}>
                      <div className="relative">
                        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4 z-10" />
                        <Input
                          type="text"
                          value={candidateSearch}
                          onChange={(e) => {
                            setCandidateSearch(e.target.value);
                            setShowCandidateDropdown(true);
                          }}
                          onFocus={() => setShowCandidateDropdown(true)}
                          placeholder={candidatesLoading ? 'Loading...' : 'Search candidates...'}
                          disabled={candidatesLoading}
                          className={`pl-10 pr-16 ${errors.candidate_id ? 'border-red-300' : ''}`}
                        />
                        <div className="absolute right-3 top-1/2 transform -translate-y-1/2 flex items-center space-x-1">
                          {candidateSearch && (
                            <button
                              type="button"
                              onClick={handleClearCandidate}
                              className="text-gray-400 hover:text-gray-600"
                            >
                              <X className="h-4 w-4" />
                            </button>
                          )}
                          <ChevronDown
                            className={`text-gray-400 h-4 w-4 transition-transform ${
                              showCandidateDropdown ? 'rotate-180' : ''
                            }`}
                          />
                        </div>
                      </div>

                      {/* Dropdown */}
                      {showCandidateDropdown && !candidatesLoading && (
                        <div className="absolute z-20 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-48 overflow-y-auto">
                          {filteredCandidates.length === 0 ? (
                            <div className="px-4 py-3 text-sm text-gray-500">
                              {candidateSearch ? 'No candidates found' : 'No candidates available'}
                            </div>
                          ) : (
                            filteredCandidates.map((candidate) => (
                              <div
                                key={candidate.id}
                                onClick={() => handleCandidateSelect(candidate)}
                                className="px-4 py-2.5 hover:bg-blue-50 cursor-pointer border-b border-gray-100 last:border-b-0"
                              >
                                <div className="flex items-center">
                                  <div className="flex-shrink-0 w-7 h-7 bg-blue-100 rounded-full flex items-center justify-center">
                                    <span className="text-xs font-medium text-blue-600">
                                      {candidate.first_name.charAt(0)}
                                      {candidate.last_name.charAt(0)}
                                    </span>
                                  </div>
                                  <div className="ml-2.5">
                                    <div className="text-sm font-medium text-gray-900">
                                      {candidate.first_name} {candidate.last_name}
                                    </div>
                                    <div className="text-xs text-gray-500">{candidate.email}</div>
                                  </div>
                                </div>
                              </div>
                            ))
                          )}
                        </div>
                      )}
                    </div>
                    {errors.candidate_id && (
                      <p className="mt-1 text-xs text-red-600 flex items-center">
                        <AlertCircle className="h-3 w-3 mr-1" />
                        {errors.candidate_id}
                      </p>
                    )}
                  </div>

                  {/* Position Title */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1.5">
                      Position Title
                    </label>
                    <Input
                      type="text"
                      name="position_title"
                      value={formData.position_title}
                      onChange={handleInputChange}
                      placeholder="e.g., Senior Frontend Developer"
                    />
                  </div>

                  {/* Description */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1.5">
                      Description
                    </label>
                    <Textarea
                      name="description"
                      value={formData.description}
                      onChange={handleInputChange}
                      rows={3}
                      placeholder="Brief description of the interview purpose"
                    />
                  </div>
                </div>

                {/* Schedule & Settings Section */}
                <div className="space-y-4">
                  <div>
                    <h3 className="text-base font-semibold text-gray-900 mb-3">
                      Schedule & Settings
                    </h3>
                  </div>

                  {/* Interview Type */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Interview Type *
                    </label>
                    <div className="grid grid-cols-3 gap-2">
                      {[
                        { value: 'video', label: 'Video', icon: Video },
                        { value: 'phone', label: 'Phone', icon: Phone },
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
                            className={`p-2.5 border-2 rounded-lg cursor-pointer transition-colors ${
                              formData.interview_type === type.value
                                ? 'border-blue-500 bg-blue-50'
                                : 'border-gray-200 hover:border-gray-300'
                            }`}
                          >
                            <type.icon className="h-4 w-4 mx-auto mb-1 text-gray-600" />
                            <p className="text-xs font-medium text-center text-gray-900">
                              {type.label}
                            </p>
                          </div>
                        </label>
                      ))}
                    </div>
                  </div>

                  {/* Video Call Options */}
                  {formData.interview_type === 'video' && (
                    <div className="bg-purple-50 border border-purple-200 rounded-lg p-3">
                      <h4 className="text-sm font-medium text-gray-900 mb-2.5 flex items-center">
                        <Video className="h-4 w-4 mr-1.5 text-purple-600" />
                        Video Call Setup
                      </h4>
                      <div className="space-y-2.5">
                        <label className="flex items-start cursor-pointer">
                          <input
                            type="radio"
                            name="video_call_type"
                            value="system_generated"
                            checked={formData.video_call_type === 'system_generated'}
                            onChange={handleInputChange}
                            className="mt-0.5"
                          />
                          <div className="ml-2.5">
                            <div className="text-sm font-medium text-gray-900">
                              System Generated
                            </div>
                            <div className="text-xs text-gray-600">Auto-create video call room</div>
                          </div>
                        </label>
                        <label className="flex items-start cursor-pointer">
                          <input
                            type="radio"
                            name="video_call_type"
                            value="custom_url"
                            checked={formData.video_call_type === 'custom_url'}
                            onChange={handleInputChange}
                            className="mt-0.5"
                          />
                          <div className="ml-2.5">
                            <div className="text-sm font-medium text-gray-900">Custom URL</div>
                            <div className="text-xs text-gray-600">Use Zoom, Google Meet, etc.</div>
                          </div>
                        </label>

                        {formData.video_call_type === 'custom_url' && (
                          <div className="mt-2.5">
                            <Input
                              type="url"
                              name="meeting_url"
                              value={formData.meeting_url}
                              onChange={handleInputChange}
                              className={`text-sm ${errors.meeting_url ? 'border-red-300' : ''}`}
                              placeholder="https://zoom.us/j/123456789"
                            />
                            {errors.meeting_url && (
                              <p className="mt-1 text-xs text-red-600">{errors.meeting_url}</p>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Date & Time - Grid with wider date field */}
                  <div className="grid grid-cols-[1.5fr_1fr_1fr] gap-3 items-start">
                    {/* Date */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1.5">
                        Date *
                      </label>
                      <DatePicker
                        selected={
                          formData.scheduled_start ? new Date(formData.scheduled_start) : null
                        }
                        onChange={(date) => {
                          if (date) {
                            const newDate = new Date(date);
                            // Keep existing time or set to default
                            if (formData.scheduled_start) {
                              const existingStart = new Date(formData.scheduled_start);
                              newDate.setHours(
                                existingStart.getHours(),
                                existingStart.getMinutes()
                              );
                            } else {
                              newDate.setHours(10, 0); // Default 10:00
                            }

                            const startISO = newDate.toISOString();

                            // Update end time to be 1 hour later
                            const endDate = new Date(newDate);
                            if (formData.scheduled_end) {
                              const existingEnd = new Date(formData.scheduled_end);
                              endDate.setHours(existingEnd.getHours(), existingEnd.getMinutes());
                            } else {
                              endDate.setHours(11, 0); // Default 11:00
                            }
                            const endISO = endDate.toISOString();

                            setFormData({
                              ...formData,
                              scheduled_start: startISO,
                              scheduled_end: endISO,
                            });
                          }
                        }}
                        dateFormat="yyyy-MM-dd"
                        placeholderText="Select date"
                        className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm text-left ${
                          errors.scheduled_start ? 'border-red-300' : 'border-gray-300'
                        }`}
                      />
                      {errors.scheduled_start && (
                        <p className="mt-1 text-xs text-red-600">{errors.scheduled_start}</p>
                      )}
                    </div>

                    {/* Start Time */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1.5">
                        Start Time *
                      </label>
                      <DatePicker
                        selected={
                          formData.scheduled_start ? new Date(formData.scheduled_start) : null
                        }
                        onChange={(time) => {
                          if (time && formData.scheduled_start) {
                            // Get the current date from scheduled_start
                            const baseDate = new Date(formData.scheduled_start);
                            // Update only the time portion
                            baseDate.setHours(time.getHours(), time.getMinutes(), 0, 0);
                            const startISO = baseDate.toISOString();

                            // Update end time to be 1 hour later
                            const endDate = new Date(baseDate);
                            endDate.setHours(endDate.getHours() + 1);
                            const endISO = endDate.toISOString();

                            setFormData({
                              ...formData,
                              scheduled_start: startISO,
                              scheduled_end: endISO,
                            });
                          }
                        }}
                        showTimeSelect
                        showTimeSelectOnly
                        timeFormat="HH:mm"
                        timeIntervals={15}
                        dateFormat="HH:mm"
                        placeholderText="HH:mm"
                        className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm text-left ${
                          errors.scheduled_start ? 'border-red-300' : 'border-gray-300'
                        }`}
                      />
                    </div>

                    {/* End Time */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1.5">
                        End Time *
                      </label>
                      <DatePicker
                        selected={formData.scheduled_end ? new Date(formData.scheduled_end) : null}
                        onChange={(time) => {
                          if (time && formData.scheduled_end) {
                            // Get the current date from scheduled_end
                            const baseDate = new Date(formData.scheduled_end);
                            // Update only the time portion
                            baseDate.setHours(time.getHours(), time.getMinutes(), 0, 0);
                            const endISO = baseDate.toISOString();

                            setFormData({
                              ...formData,
                              scheduled_end: endISO,
                            });

                            setErrors((prev) => ({
                              ...prev,
                              scheduled_end: '',
                            }));
                          }
                        }}
                        showTimeSelect
                        showTimeSelectOnly
                        timeFormat="HH:mm"
                        timeIntervals={15}
                        dateFormat="HH:mm"
                        placeholderText="HH:mm"
                        className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm text-left ${
                          errors.scheduled_end ? 'border-red-300' : 'border-gray-300'
                        }`}
                      />
                      {errors.scheduled_end && (
                        <p className="mt-1 text-xs text-red-600">{errors.scheduled_end}</p>
                      )}
                    </div>
                  </div>

                  {/* Location/Meeting Details */}
                  {formData.interview_type === 'in_person' && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1.5">
                        Location *
                      </label>
                      <Input
                        type="text"
                        name="location"
                        value={formData.location}
                        onChange={handleInputChange}
                        className={errors.location ? 'border-red-300' : ''}
                        placeholder="Office address or meeting room"
                      />
                      {errors.location && (
                        <p className="mt-1 text-xs text-red-600">{errors.location}</p>
                      )}
                    </div>
                  )}

                  {formData.interview_type === 'phone' && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1.5">
                        Phone Details
                      </label>
                      <Input
                        type="text"
                        name="location"
                        value={formData.location}
                        onChange={handleInputChange}
                        placeholder="Phone number or instructions"
                      />
                    </div>
                  )}
                </div>

                {/* Additional Notes - Always Visible */}
                <div className="space-y-4">
                  <div>
                    <h3 className="text-base font-semibold text-gray-900 mb-3">Additional Notes</h3>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1.5">
                      Interview Notes
                    </label>
                    <Textarea
                      name="notes"
                      value={formData.notes}
                      onChange={handleInputChange}
                      rows={3}
                      placeholder="Internal notes about the interview"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1.5">
                      Preparation Notes
                    </label>
                    <Textarea
                      name="preparation_notes"
                      value={formData.preparation_notes}
                      onChange={handleInputChange}
                      rows={3}
                      placeholder="Notes for interview preparation"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        <DialogFooter className="flex-shrink-0 gap-3 border-t border-slate-200 bg-white px-6 py-4">
          <Button
            type="button"
            variant="ghost"
            disabled={saving}
            onClick={onClose}
            className="min-w-[120px]"
          >
            Cancel
          </Button>
          <Button
            type="button"
            onClick={handleSubmit}
            disabled={saving || loading}
            leftIcon={
              saving ? (
                <div className="h-4 w-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <Save className="h-4 w-4" />
              )
            }
            className="min-w-[160px] bg-blue-600 text-white hover:bg-blue-600/90"
          >
            {workflowContext
              ? 'Save & Return to Workflow'
              : saving
                ? 'Saving...'
                : mode === 'edit'
                  ? 'Save Changes'
                  : 'Schedule Interview'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
