'use client';

import React, { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowLeft, Save, Video, Phone, Users, AlertCircle, Search, ChevronDown, X } from 'lucide-react';
import AppLayout from '@/components/layout/AppLayout';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import { useAuth } from '@/contexts/AuthContext';
import { useToast } from '@/contexts/ToastContext';
import { interviewsApi } from '@/api/interviews';
import { candidatesApi } from '@/api/candidates';
import type { Interview, InterviewFormData } from '@/types/interview';
import type { UserManagement } from '@/types/user';

function ScheduleInterviewContent() {
  const router = useRouter();
  const { user } = useAuth();
  const { showToast } = useToast();

  // Check if user can create interviews (not a candidate)
  const canCreateInterviews = () => {
    if (!user || !user.roles) return false;
    const isCandidate = user.roles.some(userRole => userRole.role.name === 'candidate');
    return !isCandidate && user.roles.length > 0;
  };

  // Redirect if user cannot create interviews
  useEffect(() => {
    if (user && !canCreateInterviews()) {
      router.push('/interviews');
    }
   
  }, [user, router]);

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
    preparation_notes: ''
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const [candidates, setCandidates] = useState<UserManagement[]>([]);
  const [candidatesLoading, setCandidatesLoading] = useState(true);
  const [candidateSearch, setCandidateSearch] = useState('');
  const [showCandidateDropdown, setShowCandidateDropdown] = useState(false);
  const candidateDropdownRef = useRef<HTMLDivElement>(null);

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

  // Fetch candidates list
  useEffect(() => {
    const fetchCandidates = async () => {
      try {
        setCandidatesLoading(true);
        const response = await candidatesApi.getCandidates({
          is_active: true,
          size: 100 // Get up to 100 candidates
        });

        if (response.success && response.data) {
          setCandidates(response.data.users || []);
        }
      } catch (error) {
        console.error('Error fetching candidates:', error);
        showToast({
          type: 'error',
          title: 'Error',
          message: 'Failed to load candidates list'
        });
      } finally {
        setCandidatesLoading(false);
      }
    };

    fetchCandidates();
   
  }, []);

  // Handle click outside to close dropdown
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (candidateDropdownRef.current && !candidateDropdownRef.current.contains(event.target as Node)) {
        setShowCandidateDropdown(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  // Filter candidates based on search
  const filteredCandidates = candidates.filter(candidate => {
    const searchLower = candidateSearch.toLowerCase();
    const fullName = `${candidate.first_name} ${candidate.last_name}`.toLowerCase();
    const email = candidate.email.toLowerCase();
    return fullName.includes(searchLower) || email.includes(searchLower);
  });

  // Handle candidate selection
  const handleCandidateSelect = (candidate: UserManagement) => {
    setFormData(prev => ({ ...prev, candidate_id: candidate.id.toString() }));
    setCandidateSearch(`${candidate.first_name} ${candidate.last_name} (${candidate.email})`);
    setShowCandidateDropdown(false);

    // Clear error when user selects
    if (errors.candidate_id) {
      setErrors(prev => ({ ...prev, candidate_id: '' }));
    }
  };

  // Handle clear selection
  const handleClearCandidate = () => {
    setFormData(prev => ({ ...prev, candidate_id: '' }));
    setCandidateSearch('');
    setShowCandidateDropdown(false);
  };

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

    // Clear meeting URL when switching to system generated
    if (name === 'video_call_type' && value === 'system_generated') {
      setFormData(prev => ({ ...prev, meeting_url: '' }));
      if (errors.meeting_url) {
        setErrors(prev => ({ ...prev, meeting_url: '' }));
      }
    }

    // Reset video call type when changing from video to other interview types
    if (name === 'interview_type' && value !== 'video') {
      setFormData(prev => ({
        ...prev,
        video_call_type: 'system_generated',
        meeting_url: ''
      }));
      if (errors.meeting_url) {
        setErrors(prev => ({ ...prev, meeting_url: '' }));
      }
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

    if (formData.interview_type === 'video' && formData.video_call_type === 'custom_url' && !formData.meeting_url.trim()) {
      newErrors.meeting_url = 'Meeting URL is required when using custom URL option';
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

    // Ensure user exists before proceeding
    if (!user) {
      showToast({
        type: 'error',
        title: 'Error',
        message: 'User session not found. Please refresh and try again.'
      });
      return;
    }

    // Handle case where user doesn't have company_id (temporary fix for test accounts)
    const companyId = user.company_id || 1;

    setLoading(true);
    try {
      // Handle video call URL generation
      let meetingUrl = formData.meeting_url.trim() || undefined;

      if (formData.interview_type === 'video' && formData.video_call_type === 'system_generated') {
        // Generate system meeting URL - this will be handled by the backend
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
                  Select Candidate *
                </label>
                <div className="relative" ref={candidateDropdownRef}>
                  {/* Search Input */}
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4 z-10" />
                    <input
                      type="text"
                      value={candidateSearch}
                      onChange={(e) => {
                        setCandidateSearch(e.target.value);
                        setShowCandidateDropdown(true);
                      }}
                      onFocus={() => setShowCandidateDropdown(true)}
                      placeholder={candidatesLoading ? 'Loading candidates...' : 'Search candidates...'}
                      disabled={candidatesLoading}
                      className={`w-full pl-10 pr-16 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                        errors.candidate_id ? 'border-red-300' : 'border-gray-300'
                      } ${candidatesLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
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
                      <ChevronDown className={`text-gray-400 h-4 w-4 transition-transform ${showCandidateDropdown ? 'rotate-180' : ''}`} />
                    </div>
                  </div>

                  {/* Dropdown */}
                  {showCandidateDropdown && !candidatesLoading && (
                    <div className="absolute z-20 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-y-auto">
                      {filteredCandidates.length === 0 ? (
                        <div className="px-4 py-3 text-sm text-gray-500">
                          {candidateSearch ? 'No candidates found matching your search' : 'No candidates available'}
                        </div>
                      ) : (
                        filteredCandidates.map((candidate) => (
                          <div
                            key={candidate.id}
                            onClick={() => handleCandidateSelect(candidate)}
                            className="px-4 py-3 hover:bg-blue-50 cursor-pointer border-b border-gray-100 last:border-b-0"
                          >
                            <div className="flex items-center">
                              <div className="flex-shrink-0 w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                                <span className="text-sm font-medium text-blue-600">
                                  {candidate.first_name.charAt(0)}{candidate.last_name.charAt(0)}
                                </span>
                              </div>
                              <div className="ml-3">
                                <div className="text-sm font-medium text-gray-900">
                                  {candidate.first_name} {candidate.last_name}
                                </div>
                                <div className="text-sm text-gray-500">{candidate.email}</div>
                              </div>
                            </div>
                          </div>
                        ))
                      )}
                    </div>
                  )}
                </div>

                {errors.candidate_id && (
                  <p className="mt-1 text-sm text-red-600 flex items-center">
                    <AlertCircle className="h-4 w-4 mr-1" />
                    {errors.candidate_id}
                  </p>
                )}

                {candidates.length === 0 && !candidatesLoading && (
                  <p className="mt-1 text-sm text-yellow-600">
                    No active candidates found. Make sure candidates are registered in the system.
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

            {/* Video Call Options - Show only when video type is selected */}
            {formData.interview_type === 'video' && (
              <div className="bg-purple-50 border border-purple-200 rounded-lg p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
                  <Video className="h-5 w-5 mr-2 text-purple-600" />
                  Video Call Configuration
                </h3>

                <div className="space-y-4">
                  {/* Meeting URL Option */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-3">
                      Video Call Setup
                    </label>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <label className="relative">
                        <input
                          type="radio"
                          name="video_call_type"
                          value="system_generated"
                          checked={formData.video_call_type === 'system_generated'}
                          onChange={handleInputChange}
                          className="sr-only"
                        />
                        <div className={`p-4 border-2 rounded-lg cursor-pointer transition-colors ${
                          formData.video_call_type === 'system_generated'
                            ? 'border-purple-500 bg-purple-50'
                            : 'border-gray-200 hover:border-gray-300'
                        }`}>
                          <div className="flex items-center">
                            <div className="flex-shrink-0">
                              <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
                                <Video className="h-4 w-4 text-purple-600" />
                              </div>
                            </div>
                            <div className="ml-3">
                              <p className="text-sm font-medium text-gray-900">System Generated</p>
                              <p className="text-xs text-gray-500">Auto-create video call room</p>
                            </div>
                          </div>
                        </div>
                      </label>

                      <label className="relative">
                        <input
                          type="radio"
                          name="video_call_type"
                          value="custom_url"
                          checked={formData.video_call_type === 'custom_url'}
                          onChange={handleInputChange}
                          className="sr-only"
                        />
                        <div className={`p-4 border-2 rounded-lg cursor-pointer transition-colors ${
                          formData.video_call_type === 'custom_url'
                            ? 'border-purple-500 bg-purple-50'
                            : 'border-gray-200 hover:border-gray-300'
                        }`}>
                          <div className="flex items-center">
                            <div className="flex-shrink-0">
                              <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                                <svg className="h-4 w-4 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                                  <path d="M12.586 4.586a2 2 0 112.828 2.828l-3 3a2 2 0 01-2.828 0 1 1 0 00-1.414 1.414 4 4 0 005.656 0l3-3a4 4 0 00-5.656-5.656l-1.5 1.5a1 1 0 101.414 1.414l1.5-1.5z" />
                                  <path d="M7.414 15.414a2 2 0 01-2.828-2.828l3-3a2 2 0 012.828 0 1 1 0 001.414-1.414 4 4 0 00-5.656 0l-3 3a4 4 0 105.656 5.656l1.5-1.5a1 1 0 10-1.414-1.414l-1.5 1.5z" />
                                </svg>
                              </div>
                            </div>
                            <div className="ml-3">
                              <p className="text-sm font-medium text-gray-900">Custom URL</p>
                              <p className="text-xs text-gray-500">Use Zoom, Google Meet, etc.</p>
                            </div>
                          </div>
                        </div>
                      </label>
                    </div>
                  </div>

                  {/* Custom URL Input - Show only when custom URL is selected */}
                  {formData.video_call_type === 'custom_url' && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Meeting URL
                      </label>
                      <input
                        type="url"
                        name="meeting_url"
                        value={formData.meeting_url}
                        onChange={handleInputChange}
                        className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent ${
                          errors.meeting_url ? 'border-red-300' : 'border-gray-300'
                        }`}
                        placeholder="https://zoom.us/j/123456789 or https://meet.google.com/xxx-yyyy-zzz"
                      />
                      {errors.meeting_url && (
                        <p className="mt-1 text-sm text-red-600 flex items-center">
                          <AlertCircle className="h-4 w-4 mr-1" />
                          {errors.meeting_url}
                        </p>
                      )}
                      <p className="mt-1 text-xs text-gray-500">
                        Enter your Zoom, Google Meet, Teams, or other video call URL
                      </p>
                    </div>
                  )}

                  {/* System Generated Info */}
                  {formData.video_call_type === 'system_generated' && (
                    <div className="bg-white border border-gray-200 rounded-lg p-4">
                      <div className="flex items-start">
                        <div className="flex-shrink-0">
                          <svg className="h-5 w-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                          </svg>
                        </div>
                        <div className="ml-3">
                          <h4 className="text-sm font-medium text-gray-900">Auto-Generated Meeting Room</h4>
                          <p className="text-sm text-gray-600 mt-1">
                            A secure video call room will be automatically created. Both interviewer and candidate will receive the meeting link.
                          </p>
                          <div className="mt-2 text-xs text-gray-500">
                            Features: Screen sharing, Recording, Real-time transcription
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

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