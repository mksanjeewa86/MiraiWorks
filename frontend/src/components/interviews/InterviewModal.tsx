'use client';

import React, { useState, useEffect, useRef } from 'react';
import { useTranslations } from 'next-intl';
import { Save, Video, Phone, Users, AlertCircle, X, Search, ChevronDown, Calendar, Clock } from 'lucide-react';
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
import { userConnectionsApi } from '@/api/userConnections';
import type { Interview, InterviewFormData } from '@/types/interview';
import type { ConnectedUser } from '@/types/user';
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
  const t = useTranslations('interviews.schedule');

  // Form state
  const [formData, setFormData] = useState<InterviewFormData>({
    title: '',
    description: '',
    assignee_id: '',
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

  // Assignee selection state (connected users only)
  const [assignees, setAssignees] = useState<ConnectedUser[]>([]);
  const [assigneesLoading, setAssigneesLoading] = useState(true);
  const [assigneeSearch, setAssigneeSearch] = useState('');
  const [showAssigneeDropdown, setShowAssigneeDropdown] = useState(false);
  const assigneeDropdownRef = useRef<HTMLDivElement>(null);

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
          assignee_id: interview.assignee_id?.toString() || '',
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

        // Set assignee search display
        if (interview.assignee) {
          setAssigneeSearch(`${interview.assignee.full_name} (${interview.assignee.email})`);
        }
      } catch (error) {
        console.error('Error fetching interview:', error);
        showToast({
          type: 'error',
          title: t('error.message'),
        });
      } finally {
        setLoading(false);
      }
    };

    fetchInterview();
  }, [isOpen, mode, interviewId, showToast]);

  // Fetch connected users with candidate role only
  useEffect(() => {
    if (!isOpen) return;

    const fetchAssignees = async () => {
      try {
        setAssigneesLoading(true);
        const response = await userConnectionsApi.getMyConnections();

        if (response.success && response.data) {
          // Filter to only show active users with 'candidate' role
          const candidates = response.data.filter(
            (user) => user.is_active && user.roles?.includes('candidate')
          );
          setAssignees(candidates);
        }
      } catch (error) {
        console.error('Error fetching connected candidates:', error);
      } finally {
        setAssigneesLoading(false);
      }
    };

    fetchAssignees();
  }, [isOpen]);

  // Handle click outside to close assignee dropdown
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        assigneeDropdownRef.current &&
        !assigneeDropdownRef.current.contains(event.target as Node)
      ) {
        setShowAssigneeDropdown(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  // Filter assignees based on search
  const filteredAssignees = assignees.filter((assignee) => {
    const searchLower = assigneeSearch.toLowerCase();
    const fullName = `${assignee.first_name} ${assignee.last_name}`.toLowerCase();
    const email = assignee.email.toLowerCase();
    return fullName.includes(searchLower) || email.includes(searchLower);
  });

  // Handle assignee selection
  const handleAssigneeSelect = (assignee: ConnectedUser) => {
    setFormData((prev) => ({ ...prev, assignee_id: assignee.id.toString() }));
    setAssigneeSearch(`${assignee.first_name} ${assignee.last_name} (${assignee.email})`);
    setShowAssigneeDropdown(false);

    if (errors.assignee_id) {
      setErrors((prev) => ({ ...prev, assignee_id: '' }));
    }
  };

  // Handle clear assignee selection
  const handleClearAssignee = () => {
    setFormData((prev) => ({ ...prev, assignee_id: '' }));
    setAssigneeSearch('');
    setShowAssigneeDropdown(false);
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

  // Helper functions for date/time formatting (similar to todos)
  const formatDateForInput = (value: Date | string) => {
    const date = value instanceof Date ? value : new Date(value);
    if (Number.isNaN(date.getTime())) return '';
    const offset = date.getTimezoneOffset();
    const local = new Date(date.getTime() - offset * 60_000);
    return local.toISOString().slice(0, 10);
  };

  const formatTimeForInput = (value: Date | string) => {
    const date = value instanceof Date ? new Date(value) : new Date(value);
    if (Number.isNaN(date.getTime())) return '';
    const offset = date.getTimezoneOffset();
    const local = new Date(date.getTime() - offset * 60_000);
    return local.toISOString().slice(11, 16);
  };

  const handleDateChange = (value: string) => {
    if (!value) return;

    const currentStart = formData.scheduled_start ? new Date(formData.scheduled_start) : new Date();
    const [year, month, day] = value.split('-').map(Number);

    const newStart = new Date(currentStart);
    newStart.setFullYear(year, month - 1, day);

    const newEnd = new Date(newStart);
    newEnd.setHours(newEnd.getHours() + 1);

    setFormData((prev) => ({
      ...prev,
      scheduled_start: newStart.toISOString(),
      scheduled_end: newEnd.toISOString(),
    }));

    setErrors((prev) => ({ ...prev, scheduled_start: '', scheduled_end: '' }));
  };

  const handleStartTimeChange = (value: string) => {
    if (!value) return;

    const currentStart = formData.scheduled_start ? new Date(formData.scheduled_start) : new Date();
    const [hours, minutes] = value.split(':').map(Number);

    const newStart = new Date(currentStart);
    newStart.setHours(hours, minutes, 0, 0);

    const newEnd = new Date(newStart);
    newEnd.setHours(newEnd.getHours() + 1);

    setFormData((prev) => ({
      ...prev,
      scheduled_start: newStart.toISOString(),
      scheduled_end: newEnd.toISOString(),
    }));

    setErrors((prev) => ({ ...prev, scheduled_start: '', scheduled_end: '' }));
  };

  const handleEndTimeChange = (value: string) => {
    if (!value) return;

    const currentEnd = formData.scheduled_end ? new Date(formData.scheduled_end) : new Date();
    const [hours, minutes] = value.split(':').map(Number);

    const newEnd = new Date(currentEnd);
    newEnd.setHours(hours, minutes, 0, 0);

    setFormData((prev) => ({ ...prev, scheduled_end: newEnd.toISOString() }));
    setErrors((prev) => ({ ...prev, scheduled_end: '' }));
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.title.trim()) {
      newErrors.title = t('validation.titleRequired');
    }

    if (!formData.assignee_id) {
      newErrors.assignee_id = t('validation.assigneeRequired');
    }

    if (!formData.scheduled_start) {
      newErrors.scheduled_start = t('validation.startTimeRequired');
    }

    if (!formData.scheduled_end) {
      newErrors.scheduled_end = t('validation.endTimeRequired');
    }

    if (formData.scheduled_start && formData.scheduled_end) {
      const start = new Date(formData.scheduled_start);
      const end = new Date(formData.scheduled_end);
      if (end <= start) {
        newErrors.scheduled_end = t('validation.endAfterStart');
      }
    }

    if (
      formData.interview_type === 'video' &&
      formData.video_call_type === 'custom_url' &&
      !formData.meeting_url.trim()
    ) {
      newErrors.meeting_url = t('validation.meetingUrlRequired');
    }

    if (formData.interview_type === 'in_person' && !formData.location.trim()) {
      newErrors.location = t('validation.locationRequired');
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();

    if (!validateForm()) {
      showToast({
        type: 'error',
        title: t('error.title'),
        message: t('error.message'),
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
        title: t('error.title'),
        message: t('errors.sessionNotFound'),
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
        assignee_id: parseInt(formData.assignee_id),
        recruiter_id: user.id,
        employer_company_id: companyId,
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
        title: t('success.title'),
        message: t('success.message'),
      });

      if (result.data) {
        onSuccess(result.data);
      }
      onClose();
    } catch (error) {
      console.error('Error saving interview:', error);
      showToast({
        type: 'error',
        title: t('error.title'),
        message: error instanceof Error ? error.message : t('error.message'),
      });
    } finally {
      setSaving(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent
        closeButton={false}
        className="flex flex-col h-[90vh] max-h-[90vh] w-full max-w-4xl md:max-w-3xl overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-2xl"
      >
        <DialogHeader className="flex-shrink-0 px-6 pt-6 pb-4 border-b border-slate-100">
          <div className="flex items-start justify-between gap-4">
            <div className="flex items-start gap-4">
              <div className="flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-blue-500 to-blue-600 shadow-lg shadow-blue-500/30">
                <Video className="h-6 w-6 text-white" />
              </div>
              <div className="space-y-1">
                <DialogTitle className="text-xl font-semibold text-slate-900">
                  {mode === 'edit' ? t('editTitle') : t('title')}
                </DialogTitle>
                <DialogDescription className="text-sm text-slate-500">
                  {mode === 'edit' ? t('editSubtitle') : t('subtitle')}
                </DialogDescription>
              </div>
            </div>
            <DialogClose className="rounded-lg border border-slate-200 p-2 text-slate-400 transition hover:bg-slate-50 hover:text-slate-600 hover:border-slate-300">
              <X className="h-4 w-4" />
            </DialogClose>
          </div>
        </DialogHeader>

        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="flex flex-col items-center gap-3">
              <div className="h-10 w-10 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
              <p className="text-sm text-slate-500">Loading...</p>
            </div>
          </div>
        ) : (
          <div className="flex-1 overflow-y-auto px-6 py-6 min-h-0">
            <div className="space-y-6">
              {/* Single Column Layout */}
              <div className="space-y-6">
                {/* Interview Details Section */}
                <div className="space-y-4 rounded-xl border border-slate-200 bg-slate-50/50 p-5">
                  <div className="flex items-center gap-2 mb-2">
                    <div className="h-1.5 w-1.5 rounded-full bg-blue-500"></div>
                    <h3 className="text-sm font-semibold text-slate-900 uppercase tracking-wide">
                      Interview Details
                    </h3>
                  </div>

                  {/* Interview Title */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1.5">
                      {t('interviewTitle')} *
                    </label>
                    <Input
                      type="text"
                      name="title"
                      value={formData.title}
                      onChange={handleInputChange}
                      className={errors.title ? 'border-red-300' : ''}
                      placeholder={t('interviewTitlePlaceholder')}
                    />
                    {errors.title && (
                      <p className="mt-1 text-xs text-red-600 flex items-center">
                        <AlertCircle className="h-3 w-3 mr-1" />
                        {errors.title}
                      </p>
                    )}
                  </div>

                  {/* Select Assignee */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1.5">
                      {t('selectAssignee')} *
                    </label>
                    <div className="relative" ref={assigneeDropdownRef}>
                      <div className="relative">
                        <Input
                          type="text"
                          value={assigneeSearch}
                          onChange={(e) => {
                            setAssigneeSearch(e.target.value);
                            setShowAssigneeDropdown(true);
                          }}
                          onFocus={() => setShowAssigneeDropdown(true)}
                          placeholder={
                            assigneesLoading
                              ? t('assigneeLoadingPlaceholder')
                              : t('assigneeSearchPlaceholder')
                          }
                          disabled={assigneesLoading}
                          leftIcon={<Search className="h-4 w-4 text-gray-400" />}
                          className={`pr-16 ${errors.assignee_id ? 'border-red-300' : ''}`}
                        />
                        <div className="absolute right-3 top-1/2 transform -translate-y-1/2 flex items-center space-x-1 z-10">
                          {assigneeSearch && (
                            <button
                              type="button"
                              onClick={handleClearAssignee}
                              className="text-gray-400 hover:text-gray-600 transition"
                            >
                              <X className="h-4 w-4" />
                            </button>
                          )}
                          <ChevronDown
                            className={`text-gray-400 h-4 w-4 transition-transform ${
                              showAssigneeDropdown ? 'rotate-180' : ''
                            }`}
                          />
                        </div>
                      </div>

                      {/* Dropdown */}
                      {showAssigneeDropdown && !assigneesLoading && (
                        <div className="absolute z-20 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-48 overflow-y-auto">
                          {filteredAssignees.length === 0 ? (
                            <div className="px-4 py-3 text-sm text-gray-500">
                              {assigneeSearch
                                ? t('noAssigneesFound')
                                : t('noAssigneesAvailable')}
                            </div>
                          ) : (
                            filteredAssignees.map((assignee) => (
                              <div
                                key={assignee.id}
                                onClick={() => handleAssigneeSelect(assignee)}
                                className="px-4 py-2.5 hover:bg-blue-50 cursor-pointer border-b border-gray-100 last:border-b-0"
                              >
                                <div className="flex items-center">
                                  <div className="flex-shrink-0 w-7 h-7 bg-blue-100 rounded-full flex items-center justify-center">
                                    <span className="text-xs font-medium text-blue-600">
                                      {assignee.first_name.charAt(0)}
                                      {assignee.last_name.charAt(0)}
                                    </span>
                                  </div>
                                  <div className="ml-2.5">
                                    <div className="text-sm font-medium text-gray-900">
                                      {assignee.first_name} {assignee.last_name}
                                    </div>
                                    <div className="text-xs text-gray-500">{assignee.email}</div>
                                  </div>
                                </div>
                              </div>
                            ))
                          )}
                        </div>
                      )}
                    </div>
                    {errors.assignee_id && (
                      <p className="mt-1 text-xs text-red-600 flex items-center">
                        <AlertCircle className="h-3 w-3 mr-1" />
                        {errors.assignee_id}
                      </p>
                    )}
                  </div>

                  {/* Description */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1.5">
                      {t('description')}
                    </label>
                    <Textarea
                      name="description"
                      value={formData.description}
                      onChange={handleInputChange}
                      rows={3}
                      placeholder={t('descriptionPlaceholder')}
                    />
                  </div>
                </div>

                {/* Schedule & Settings Section */}
                <div className="space-y-4 rounded-xl border border-slate-200 bg-slate-50/50 p-5">
                  <div className="flex items-center gap-2 mb-2">
                    <div className="h-1.5 w-1.5 rounded-full bg-purple-500"></div>
                    <h3 className="text-sm font-semibold text-slate-900 uppercase tracking-wide">
                      Schedule & Settings
                    </h3>
                  </div>

                  {/* Interview Type */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-3">
                      {t('interviewTypeLabel')} *
                    </label>
                    <div className="grid grid-cols-3 gap-3">
                      {[
                        { value: 'video', label: t('typeVideoCall'), icon: Video, color: 'blue' },
                        { value: 'phone', label: t('typePhoneCall'), icon: Phone, color: 'green' },
                        { value: 'in_person', label: t('typeInPerson'), icon: Users, color: 'purple' },
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
                            className={`relative p-4 border-2 rounded-xl cursor-pointer transition-all duration-200 ${
                              formData.interview_type === type.value
                                ? `border-${type.color}-500 bg-${type.color}-50 shadow-md`
                                : 'border-slate-200 bg-white hover:border-slate-300 hover:shadow-sm'
                            }`}
                          >
                            {formData.interview_type === type.value && (
                              <div className={`absolute top-2 right-2 h-2 w-2 rounded-full bg-${type.color}-500`}></div>
                            )}
                            <type.icon className={`h-5 w-5 mx-auto mb-2 ${
                              formData.interview_type === type.value ? `text-${type.color}-600` : 'text-slate-400'
                            }`} />
                            <p className={`text-xs font-medium text-center ${
                              formData.interview_type === type.value ? `text-${type.color}-900` : 'text-slate-600'
                            }`}>
                              {type.label}
                            </p>
                          </div>
                        </label>
                      ))}
                    </div>
                  </div>

                  {/* Video Call Options */}
                  {formData.interview_type === 'video' && (
                    <div className="bg-gradient-to-br from-blue-50 to-indigo-50 border border-blue-200 rounded-xl p-4">
                      <h4 className="text-sm font-semibold text-slate-900 mb-3 flex items-center gap-2">
                        <div className="h-8 w-8 rounded-lg bg-blue-500 flex items-center justify-center">
                          <Video className="h-4 w-4 text-white" />
                        </div>
                        {t('videoCallSetup')}
                      </h4>
                      <div className="space-y-3">
                        <label className="flex items-start cursor-pointer group">
                          <input
                            type="radio"
                            name="video_call_type"
                            value="system_generated"
                            checked={formData.video_call_type === 'system_generated'}
                            onChange={handleInputChange}
                            className="mt-1 h-4 w-4 text-blue-600"
                          />
                          <div className="ml-3">
                            <div className="text-sm font-medium text-slate-900 group-hover:text-blue-600 transition">
                              {t('systemGenerated')}
                            </div>
                            <div className="text-xs text-slate-600 mt-0.5">{t('systemGeneratedDesc')}</div>
                          </div>
                        </label>
                        <label className="flex items-start cursor-pointer group">
                          <input
                            type="radio"
                            name="video_call_type"
                            value="custom_url"
                            checked={formData.video_call_type === 'custom_url'}
                            onChange={handleInputChange}
                            className="mt-1 h-4 w-4 text-blue-600"
                          />
                          <div className="ml-3 flex-1">
                            <div className="text-sm font-medium text-slate-900 group-hover:text-blue-600 transition">
                              {t('customUrl')}
                            </div>
                            <div className="text-xs text-slate-600 mt-0.5">{t('customUrlDesc')}</div>
                          </div>
                        </label>

                        {formData.video_call_type === 'custom_url' && (
                          <div className="mt-3 pl-7">
                            <Input
                              type="url"
                              name="meeting_url"
                              value={formData.meeting_url}
                              onChange={handleInputChange}
                              className={`text-sm bg-white ${errors.meeting_url ? 'border-red-300' : 'border-blue-200'}`}
                              placeholder={t('meetingUrlPlaceholder')}
                            />
                            {errors.meeting_url && (
                              <p className="mt-1.5 text-xs text-red-600 flex items-center">
                                <AlertCircle className="h-3 w-3 mr-1" />
                                {errors.meeting_url}
                              </p>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Date & Time - Modern Design with Icons */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Date & Time *
                    </label>
                    <div className="grid grid-cols-[1.5fr_1fr_1fr] gap-3">
                      {/* Date */}
                      <div>
                        <label className="block text-xs font-medium text-gray-600 mb-1.5">
                          Date
                        </label>
                        <Input
                          type="date"
                          value={formData.scheduled_start ? formatDateForInput(formData.scheduled_start) : ''}
                          onChange={(e) => handleDateChange(e.target.value)}
                          required
                          leftIcon={<Calendar className="h-4 w-4 text-gray-400" />}
                          className={errors.scheduled_start ? 'border-red-300' : ''}
                        />
                        {errors.scheduled_start && (
                          <p className="mt-1 text-xs text-red-600 flex items-center">
                            <AlertCircle className="h-3 w-3 mr-1" />
                            {errors.scheduled_start}
                          </p>
                        )}
                      </div>

                      {/* Start Time */}
                      <div>
                        <label className="block text-xs font-medium text-gray-600 mb-1.5">
                          Start Time
                        </label>
                        <Input
                          type="time"
                          value={formData.scheduled_start ? formatTimeForInput(formData.scheduled_start) : ''}
                          onChange={(e) => handleStartTimeChange(e.target.value)}
                          required
                          leftIcon={<Clock className="h-4 w-4 text-gray-400" />}
                          className={errors.scheduled_start ? 'border-red-300' : ''}
                        />
                      </div>

                      {/* End Time */}
                      <div>
                        <label className="block text-xs font-medium text-gray-600 mb-1.5">
                          End Time
                        </label>
                        <Input
                          type="time"
                          value={formData.scheduled_end ? formatTimeForInput(formData.scheduled_end) : ''}
                          onChange={(e) => handleEndTimeChange(e.target.value)}
                          required
                          leftIcon={<Clock className="h-4 w-4 text-gray-400" />}
                          className={errors.scheduled_end ? 'border-red-300' : ''}
                        />
                        {errors.scheduled_end && (
                          <p className="mt-1 text-xs text-red-600 flex items-center">
                            <AlertCircle className="h-3 w-3 mr-1" />
                            {errors.scheduled_end}
                          </p>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Location/Meeting Details */}
                  {formData.interview_type === 'in_person' && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1.5">
                        {t('locationRequired')} *
                      </label>
                      <Input
                        type="text"
                        name="location"
                        value={formData.location}
                        onChange={handleInputChange}
                        className={errors.location ? 'border-red-300' : ''}
                        placeholder={t('locationPlaceholder')}
                      />
                      {errors.location && (
                        <p className="mt-1 text-xs text-red-600">{errors.location}</p>
                      )}
                    </div>
                  )}

                  {formData.interview_type === 'phone' && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1.5">
                        {t('phoneDetails')}
                      </label>
                      <Input
                        type="text"
                        name="location"
                        value={formData.location}
                        onChange={handleInputChange}
                        placeholder={t('phoneDetailsPlaceholder')}
                      />
                    </div>
                  )}
                </div>

                {/* Additional Notes - Always Visible */}
                <div className="space-y-4 rounded-xl border border-slate-200 bg-slate-50/50 p-5">
                  <div className="flex items-center gap-2 mb-2">
                    <div className="h-1.5 w-1.5 rounded-full bg-green-500"></div>
                    <h3 className="text-sm font-semibold text-slate-900 uppercase tracking-wide">
                      Additional Notes
                    </h3>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1.5">
                      {t('interviewNotes')}
                    </label>
                    <Textarea
                      name="notes"
                      value={formData.notes}
                      onChange={handleInputChange}
                      rows={3}
                      placeholder={t('interviewNotesPlaceholder')}
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1.5">
                      {t('preparationNotes')}
                    </label>
                    <Textarea
                      name="preparation_notes"
                      value={formData.preparation_notes}
                      onChange={handleInputChange}
                      rows={3}
                      placeholder={t('preparationNotesPlaceholder')}
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        <DialogFooter className="flex-shrink-0 gap-3 border-t border-slate-100 bg-slate-50 px-6 py-4">
          <Button
            type="button"
            variant="ghost"
            disabled={saving}
            onClick={onClose}
            className="min-w-[120px] border border-slate-200 bg-white hover:bg-slate-50 text-slate-700 font-medium"
          >
            {t('cancel')}
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
            className="min-w-[160px] bg-gradient-to-r from-blue-600 to-blue-700 text-white hover:from-blue-700 hover:to-blue-800 shadow-lg shadow-blue-500/30 font-medium"
          >
            {workflowContext
              ? 'Save & Return to Workflow'
              : saving
                ? (mode === 'edit' ? t('editSubmitting') : t('submitting'))
                : (mode === 'edit' ? t('editSubmit') : t('submit'))}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
