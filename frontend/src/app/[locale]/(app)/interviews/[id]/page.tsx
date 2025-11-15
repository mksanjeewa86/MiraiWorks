'use client';

import React, { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import {
  ArrowLeft,
  Edit,
  Trash2,
  Calendar,
  Clock,
  MapPin,
  User,
  Video,
  Phone,
  Users,
  FileText,
  AlertCircle,
  CheckCircle,
  XCircle,
  Clock4,
  Copy,
} from 'lucide-react';
import Link from 'next/link';
import AppLayout from '@/components/layout/AppLayout';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import { useAuth } from '@/contexts/AuthContext';
import { useToast } from '@/contexts/ToastContext';
import { interviewsApi } from '@/api/interviews';
import { apiClient } from '@/api/apiClient';
import { API_ENDPOINTS } from '@/api/config';
import InterviewNotes from '@/components/interview/InterviewNotes';
import InterviewDeleteModal from '@/components/interviews/InterviewDeleteModal';
import type { Interview } from '@/types/interview';
import type { VideoCall } from '@/types/video';
import { ROUTES } from '@/routes/config';

// Helper functions for styling
const getStatusStyle = (status: string) => {
  switch (status) {
    case 'scheduled':
      return 'bg-blue-100 text-blue-800 border border-blue-200';
    case 'completed':
      return 'bg-green-100 text-green-800 border border-green-200';
    case 'cancelled':
      return 'bg-red-100 text-red-800 border border-red-200';
    case 'in_progress':
      return 'bg-yellow-100 text-yellow-800 border border-yellow-200';
    default:
      return 'bg-gray-100 text-gray-800 border border-gray-200';
  }
};

const getStatusIcon = (status: string) => {
  switch (status) {
    case 'scheduled':
      return <Clock className="h-3 w-3 mr-1" />;
    case 'completed':
      return <CheckCircle className="h-3 w-3 mr-1" />;
    case 'cancelled':
      return <XCircle className="h-3 w-3 mr-1" />;
    case 'in_progress':
      return <Clock4 className="h-3 w-3 mr-1" />;
    default:
      return <AlertCircle className="h-3 w-3 mr-1" />;
  }
};

const getTypeIcon = (type: string) => {
  switch (type) {
    case 'video':
      return <Video className="h-3 w-3 mr-1" />;
    case 'phone':
      return <Phone className="h-3 w-3 mr-1" />;
    case 'in_person':
      return <Users className="h-3 w-3 mr-1" />;
    default:
      return <Users className="h-3 w-3 mr-1" />;
  }
};

function InterviewDetailsContent() {
  const params = useParams();
  const router = useRouter();
  const { user } = useAuth();
  const { showToast } = useToast();
  const [interview, setInterview] = useState<Interview | null>(null);
  const [videoCall, setVideoCall] = useState<VideoCall | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');

  const interviewId = typeof params.id === 'string' ? parseInt(params.id) : null;

  // Helper function to check if user has a specific permission
  const hasPermission = (permission: string): boolean => {
    if (!user || !user.roles) return false;

    return user.roles.some((userRole) =>
      userRole.role.permissions?.some((p) => p.name === permission)
    );
  };

  // Helper function to check if user can modify interviews
  const canModifyInterview = () => {
    return hasPermission('interviews.update');
  };

  // Helper function to check if user can delete interviews
  const canDeleteInterview = () => {
    if (!hasPermission('interviews.delete')) {
      return false;
    }

    // Check if current user is the creator of the interview
    if (!user || !interview || interview.created_by !== user.id) {
      return false;
    }

    return true;
  };

  // Delete modal state
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

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

        setInterview(interview);

        // If it's a video interview, fetch or create the video call
        if (interview.interview_type === 'video') {
          try {
            // Try to get existing video call
            const videoCallResponse = await apiClient.get<VideoCall>(
              API_ENDPOINTS.INTERVIEWS.VIDEO_CALL(interviewId)
            );
            setVideoCall(videoCallResponse.data);
          } catch (videoCallError: unknown) {
            const errorMessage =
              videoCallError instanceof Error ? videoCallError.message : 'Unknown error';

            // If video call doesn't exist (404), create one
            if (
              errorMessage.includes('404') ||
              errorMessage.toLowerCase().includes('not found') ||
              errorMessage.includes('No video call found')
            ) {
              const videoCallData = {
                candidate_id: interview.assignee?.id || interview.assignee_id,
                scheduled_at: interview.scheduled_start || new Date().toISOString(),
                transcription_enabled: true,
                transcription_language: 'ja',
              };

              const newVideoCall = await apiClient.post<VideoCall>(
                API_ENDPOINTS.INTERVIEWS.VIDEO_CALL(interviewId),
                videoCallData
              );
              setVideoCall(newVideoCall.data);
            } else {
              console.error('Video call error:', videoCallError);
            }
          }
        }
      } catch (err) {
        console.error('Error fetching interview:', err);
        setError(err instanceof Error ? err.message : 'Failed to fetch interview details');
      } finally {
        setLoading(false);
      }
    };

    fetchInterview();
  }, [interviewId]);

  const handleOpenDeleteModal = () => {
    setIsDeleteModalOpen(true);
  };

  const handleCloseDeleteModal = () => {
    if (!isDeleting) {
      setIsDeleteModalOpen(false);
    }
  };

  const handleConfirmDelete = async () => {
    if (!interview) return;

    setIsDeleting(true);
    try {
      await interviewsApi.delete(interview.id);
      showToast({
        type: 'success',
        title: 'Interview Deleted',
        message: 'The interview has been successfully deleted',
      });
      router.push(ROUTES.INTERVIEWS.BASE);
    } catch (err) {
      console.error('Error deleting interview:', err);
      showToast({
        type: 'error',
        title: 'Error',
        message: err instanceof Error ? err.message : 'Failed to delete interview',
      });
      setIsDeleting(false);
    }
  };

  const formatDateTime = (dateTime: string) => {
    const date = new Date(dateTime);
    return {
      date: date.toLocaleDateString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      }),
      time: date.toLocaleTimeString('en-US', {
        hour: 'numeric',
        minute: '2-digit',
        hour12: true,
      }),
    };
  };

  if (loading) {
    return (
      <AppLayout>
        <div className="min-h-screen bg-gray-50 flex items-center justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-2 text-gray-600">Loading interview details...</span>
        </div>
      </AppLayout>
    );
  }

  if (error || !interview) {
    return (
      <AppLayout>
        <div className="min-h-screen bg-gray-50 flex items-center justify-center">
          <div className="text-center">
            <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-gray-900 mb-2">Interview Not Found</h2>
            <p className="text-gray-600 mb-4">
              {error || 'The interview you are looking for could not be found.'}
            </p>
            <Link
              href={ROUTES.INTERVIEWS.BASE}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg inline-flex items-center gap-2"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Interviews
            </Link>
          </div>
        </div>
      </AppLayout>
    );
  }

  const startTime = interview.scheduled_start ? formatDateTime(interview.scheduled_start) : null;
  const endTime = interview.scheduled_end ? formatDateTime(interview.scheduled_end) : null;

  return (
    <AppLayout>
      {/* Hero Section with Gradient Background */}
      <div className="relative bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 min-h-[40vh]">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-600/5 to-purple-600/5"></div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Navigation */}
          <div className="flex items-center mb-8">
            <button
              onClick={() => router.back()}
              className="group mr-4 p-3 text-gray-500 hover:text-gray-900 bg-white/80 backdrop-blur-sm rounded-xl hover:bg-white shadow-sm hover:shadow-md transition-all duration-200"
            >
              <ArrowLeft className="h-5 w-5 group-hover:-translate-x-0.5 transition-transform duration-200" />
            </button>
            <div className="flex-1">
              <h1 className="text-3xl lg:text-4xl font-bold bg-gradient-to-r from-gray-900 via-gray-800 to-gray-700 bg-clip-text text-transparent mb-2">
                {interview.title}
              </h1>
              <p className="text-gray-600 text-lg">
                Interview with {interview.assignee?.full_name || 'Unknown Assignee'}
              </p>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex flex-wrap items-center gap-3">
            {interview.interview_type === 'video' &&
              (videoCall ? (
                <Link
                  href={ROUTES.ROOM.BY_CODE(videoCall.room_id)}
                  className="group bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white px-6 py-3 rounded-xl flex items-center gap-2 shadow-lg hover:shadow-xl transition-all duration-200 transform hover:-translate-y-0.5"
                >
                  <Video className="h-5 w-5 group-hover:scale-110 transition-transform duration-200" />
                  <span className="font-medium">Join Video Call</span>
                </Link>
              ) : (
                <div className="bg-gray-600 text-gray-300 px-6 py-3 rounded-xl flex items-center gap-2">
                  <Video className="h-5 w-5" />
                  <span className="font-medium">Setting up video call...</span>
                </div>
              ))}
            {canModifyInterview() && (
              <Link
                href={ROUTES.INTERVIEWS.EDIT(interview.id)}
                className="group bg-white/80 backdrop-blur-sm hover:bg-white text-gray-700 hover:text-gray-900 border border-gray-200 hover:border-gray-300 px-6 py-3 rounded-xl flex items-center gap-2 shadow-sm hover:shadow-md transition-all duration-200"
              >
                <Edit className="h-5 w-5 group-hover:scale-110 transition-transform duration-200" />
                <span className="font-medium">Edit Interview</span>
              </Link>
            )}
            {canDeleteInterview() && (
              <button
                onClick={handleOpenDeleteModal}
                className="group bg-red-500/10 hover:bg-red-500 text-red-600 hover:text-white border border-red-200 hover:border-red-500 px-6 py-3 rounded-xl flex items-center gap-2 backdrop-blur-sm transition-all duration-200"
              >
                <Trash2 className="h-5 w-5 group-hover:scale-110 transition-transform duration-200" />
                <span className="font-medium">Delete</span>
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 -mt-16 relative z-10 pb-16">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Basic Information */}
            <div className="group bg-white/70 backdrop-blur-xl border border-white/20 rounded-2xl p-8 shadow-xl hover:shadow-2xl transition-all duration-300 hover:-translate-y-1">
              <div className="flex items-center gap-3 mb-6">
                <div className="p-3 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl">
                  <FileText className="h-6 w-6 text-white" />
                </div>
                <h2 className="text-2xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent">
                  Interview Information
                </h2>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div className="space-y-2">
                  <label className="block text-sm font-semibold text-gray-600 uppercase tracking-wide">
                    Status
                  </label>
                  <div
                    className={`inline-flex items-center px-4 py-2 rounded-xl text-sm font-medium ${getStatusStyle(interview.status)} shadow-sm`}
                  >
                    {getStatusIcon(interview.status)}
                    {interview.status.replace('_', ' ').toUpperCase()}
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="block text-sm font-semibold text-gray-600 uppercase tracking-wide">
                    Type
                  </label>
                  <div className="inline-flex items-center px-4 py-2 bg-gradient-to-r from-indigo-50 to-purple-50 border border-indigo-200 text-indigo-800 rounded-xl text-sm font-medium shadow-sm">
                    {getTypeIcon(interview.interview_type)}
                    {interview.interview_type.replace('_', ' ').toUpperCase()}
                  </div>
                </div>

                {interview.description && (
                  <div className="md:col-span-2 space-y-2">
                    <label className="block text-sm font-semibold text-gray-600 uppercase tracking-wide">
                      Description
                    </label>
                    <div className="bg-gradient-to-br from-gray-50 to-gray-100/50 rounded-xl p-4 border border-gray-200">
                      <p className="text-gray-900 whitespace-pre-wrap leading-relaxed">
                        {interview.description}
                      </p>
                    </div>
                  </div>
                )}

                {interview.interview_type === 'video' && videoCall && (
                  <div className="md:col-span-2 space-y-2">
                    <label className="block text-sm font-semibold text-gray-600 uppercase tracking-wide">
                      Video Room Code
                    </label>
                    <div className="bg-gradient-to-br from-purple-50 to-indigo-50 rounded-xl p-4 border border-purple-200">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-2xl font-mono font-bold text-purple-800 tracking-wider">
                            {videoCall.room_id}
                          </p>
                          <p className="text-sm text-purple-600 mt-1">
                            Share this code with participants to join the video call
                          </p>
                        </div>
                        <button
                          onClick={() => {
                            navigator.clipboard.writeText(videoCall.room_id);
                            showToast({
                              type: 'success',
                              title: 'Copied!',
                              message: 'Room code copied to clipboard',
                            });
                          }}
                          className="bg-purple-100 hover:bg-purple-200 text-purple-700 px-3 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-2"
                        >
                          <Copy className="h-4 w-4" />
                          Copy Code
                        </button>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Schedule Information */}
            {(interview.scheduled_start || interview.scheduled_end) && (
              <div className="group bg-white/70 backdrop-blur-xl border border-white/20 rounded-2xl p-8 shadow-xl hover:shadow-2xl transition-all duration-300 hover:-translate-y-1">
                <div className="flex items-center gap-3 mb-6">
                  <div className="p-3 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-xl">
                    <Calendar className="h-6 w-6 text-white" />
                  </div>
                  <h2 className="text-2xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent">
                    Schedule Details
                  </h2>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                  {startTime && (
                    <div className="space-y-2">
                      <label className="block text-sm font-semibold text-gray-600 uppercase tracking-wide">
                        Start Time
                      </label>
                      <div className="bg-gradient-to-br from-emerald-50 to-teal-50 rounded-xl p-4 border border-emerald-200">
                        <p className="text-lg font-bold text-gray-900">{startTime.date}</p>
                        <p className="text-emerald-700 font-medium">{startTime.time}</p>
                      </div>
                    </div>
                  )}

                  {endTime && (
                    <div className="space-y-2">
                      <label className="block text-sm font-semibold text-gray-600 uppercase tracking-wide">
                        End Time
                      </label>
                      <div className="bg-gradient-to-br from-orange-50 to-red-50 rounded-xl p-4 border border-orange-200">
                        <p className="text-lg font-bold text-gray-900">{endTime.date}</p>
                        <p className="text-orange-700 font-medium">{endTime.time}</p>
                      </div>
                    </div>
                  )}

                  {interview.timezone && (
                    <div className="space-y-2">
                      <label className="block text-sm font-semibold text-gray-600 uppercase tracking-wide">
                        Timezone
                      </label>
                      <p className="text-lg font-medium text-gray-900 bg-gradient-to-r from-gray-50 to-gray-100/50 px-4 py-3 rounded-xl border border-gray-200">
                        {interview.timezone}
                      </p>
                    </div>
                  )}

                  {interview.duration_minutes && (
                    <div className="space-y-2">
                      <label className="block text-sm font-semibold text-gray-600 uppercase tracking-wide">
                        Duration
                      </label>
                      <div className="flex items-center gap-2 bg-gradient-to-r from-blue-50 to-indigo-50 px-4 py-3 rounded-xl border border-blue-200">
                        <Clock className="h-5 w-5 text-blue-600" />
                        <span className="text-lg font-medium text-gray-900">
                          {interview.duration_minutes} minutes
                        </span>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Location/Meeting Details */}
            {(interview.location || interview.meeting_url) && (
              <div className="group bg-white/70 backdrop-blur-xl border border-white/20 rounded-2xl p-8 shadow-xl hover:shadow-2xl transition-all duration-300 hover:-translate-y-1">
                <div className="flex items-center gap-3 mb-6">
                  <div className="p-3 bg-gradient-to-br from-orange-500 to-red-600 rounded-xl">
                    <MapPin className="h-6 w-6 text-white" />
                  </div>
                  <h2 className="text-2xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent">
                    Location & Meeting
                  </h2>
                </div>

                <div className="space-y-6">
                  {interview.location && (
                    <div className="space-y-2">
                      <label className="block text-sm font-semibold text-gray-600 uppercase tracking-wide">
                        Location
                      </label>
                      <div className="flex items-center gap-3 bg-gradient-to-r from-orange-50 to-red-50 px-4 py-3 rounded-xl border border-orange-200">
                        <MapPin className="h-5 w-5 text-orange-600" />
                        <p className="text-lg font-medium text-gray-900">{interview.location}</p>
                      </div>
                    </div>
                  )}

                  {interview.meeting_url && (
                    <div className="space-y-2">
                      <label className="block text-sm font-semibold text-gray-600 uppercase tracking-wide">
                        Meeting URL
                      </label>
                      <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-4 border border-blue-200">
                        <a
                          href={interview.meeting_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="group inline-flex items-center gap-2 text-blue-600 hover:text-blue-800 transition-colors duration-200"
                        >
                          <Video className="h-5 w-5 group-hover:scale-110 transition-transform duration-200" />
                          <span className="font-medium break-all group-hover:underline">
                            {interview.meeting_url.length > 50
                              ? `${interview.meeting_url.substring(0, 50)}...`
                              : interview.meeting_url}
                          </span>
                        </a>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Notes */}
            {(interview.notes || interview.preparation_notes) && (
              <div className="group bg-white/70 backdrop-blur-xl border border-white/20 rounded-2xl p-8 shadow-xl hover:shadow-2xl transition-all duration-300 hover:-translate-y-1">
                <div className="flex items-center gap-3 mb-6">
                  <div className="p-3 bg-gradient-to-br from-purple-500 to-pink-600 rounded-xl">
                    <FileText className="h-6 w-6 text-white" />
                  </div>
                  <h2 className="text-2xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent">
                    Interview Notes
                  </h2>
                </div>

                <div className="space-y-6">
                  {interview.notes && (
                    <div className="space-y-2">
                      <label className="block text-sm font-semibold text-gray-600 uppercase tracking-wide">
                        General Notes
                      </label>
                      <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl p-6 border border-purple-200">
                        <p className="text-gray-900 whitespace-pre-wrap leading-relaxed font-medium">
                          {interview.notes}
                        </p>
                      </div>
                    </div>
                  )}

                  {interview.preparation_notes && (
                    <div className="space-y-2">
                      <label className="block text-sm font-semibold text-gray-600 uppercase tracking-wide">
                        Preparation Notes
                      </label>
                      <div className="bg-gradient-to-br from-amber-50 to-yellow-50 rounded-xl p-6 border border-amber-200">
                        <p className="text-gray-900 whitespace-pre-wrap leading-relaxed font-medium">
                          {interview.preparation_notes}
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Private Notes */}
            <InterviewNotes interviewId={interview.id} className="mt-6" />
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Participants */}
            <div className="bg-white/70 backdrop-blur-xl border border-white/20 rounded-2xl p-6 shadow-xl hover:shadow-2xl transition-all duration-300">
              <div className="flex items-center gap-3 mb-6">
                <div className="p-2 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-lg">
                  <Users className="h-5 w-5 text-white" />
                </div>
                <h3 className="text-xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent">
                  Participants
                </h3>
              </div>

              <div className="space-y-4">
                {interview.assignee && (
                  <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-4 border border-blue-200">
                    <label className="block text-xs font-bold text-blue-600 uppercase tracking-wide mb-2">
                      Candidate
                    </label>
                    <div className="flex items-center space-x-3">
                      <div className="h-10 w-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center shadow-md">
                        <User className="h-5 w-5 text-white" />
                      </div>
                      <div>
                        <p className="text-sm font-bold text-gray-900">
                          {interview.assignee.full_name || interview.assignee.email}
                        </p>
                        <p className="text-sm text-gray-600 font-medium">
                          {interview.assignee.email}
                        </p>
                      </div>
                    </div>
                  </div>
                )}

                {interview.recruiter && (
                  <div className="bg-gradient-to-r from-emerald-50 to-teal-50 rounded-xl p-4 border border-emerald-200">
                    <label className="block text-xs font-bold text-emerald-600 uppercase tracking-wide mb-2">
                      Recruiter
                    </label>
                    <div className="flex items-center space-x-3">
                      <div className="h-10 w-10 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-xl flex items-center justify-center shadow-md">
                        <User className="h-5 w-5 text-white" />
                      </div>
                      <div>
                        <p className="text-sm font-bold text-gray-900">
                          {interview.recruiter.full_name || interview.recruiter.email}
                        </p>
                        <p className="text-sm text-gray-600 font-medium">
                          {interview.recruiter.email}
                        </p>
                      </div>
                    </div>
                  </div>
                )}

                {interview.employer_company_name && (
                  <div className="bg-gradient-to-r from-amber-50 to-orange-50 rounded-xl p-4 border border-amber-200">
                    <label className="block text-xs font-bold text-amber-600 uppercase tracking-wide mb-2">
                      Company
                    </label>
                    <div className="flex items-center space-x-3">
                      <div className="h-10 w-10 bg-gradient-to-br from-amber-500 to-orange-600 rounded-xl flex items-center justify-center shadow-md">
                        <Users className="h-5 w-5 text-white" />
                      </div>
                      <p className="text-sm font-bold text-gray-900">
                        {interview.employer_company_name}
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Metadata */}
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Details</h3>

              <div className="space-y-4 text-sm">
                <div>
                  <label className="block font-medium text-gray-700 mb-1">Created</label>
                  <p className="text-gray-600">
                    {new Date(interview.created_at).toLocaleDateString('en-US', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric',
                      hour: 'numeric',
                      minute: '2-digit',
                    })}
                  </p>
                </div>

                <div>
                  <label className="block font-medium text-gray-700 mb-1">Last Updated</label>
                  <p className="text-gray-600">
                    {new Date(interview.updated_at).toLocaleDateString('en-US', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric',
                      hour: 'numeric',
                      minute: '2-digit',
                    })}
                  </p>
                </div>

                {interview.confirmed_at && (
                  <div>
                    <label className="block font-medium text-gray-700 mb-1">Confirmed</label>
                    <p className="text-gray-600">
                      {new Date(interview.confirmed_at).toLocaleDateString('en-US', {
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric',
                        hour: 'numeric',
                        minute: '2-digit',
                      })}
                    </p>
                  </div>
                )}

                {interview.cancelled_at && (
                  <div>
                    <label className="block font-medium text-gray-700 mb-1">Cancelled</label>
                    <p className="text-gray-600">
                      {new Date(interview.cancelled_at).toLocaleDateString('en-US', {
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric',
                        hour: 'numeric',
                        minute: '2-digit',
                      })}
                    </p>
                    {interview.cancellation_reason && (
                      <p className="text-gray-600 mt-1 italic">{interview.cancellation_reason}</p>
                    )}
                  </div>
                )}
              </div>
            </div>

            {/* Interview Proposals */}
            {interview.proposals && interview.proposals.length > 0 && (
              <div className="bg-white rounded-lg border border-gray-200 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Proposals</h3>
                <div className="space-y-3">
                  {interview.proposals.map((proposal) => (
                    <div key={proposal.id} className="p-3 bg-gray-50 rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium text-gray-900">
                          {proposal.proposer_name}
                        </span>
                        <span
                          className={`px-2 py-1 rounded-full text-xs font-medium ${
                            proposal.status === 'accepted'
                              ? 'bg-green-100 text-green-800'
                              : proposal.status === 'declined'
                                ? 'bg-red-100 text-red-800'
                                : proposal.status === 'expired'
                                  ? 'bg-gray-100 text-gray-800'
                                  : 'bg-yellow-100 text-yellow-800'
                          }`}
                        >
                          {proposal.status.charAt(0).toUpperCase() + proposal.status.slice(1)}
                        </span>
                      </div>
                      <p className="text-sm text-gray-600">
                        {new Date(proposal.start_datetime).toLocaleDateString()} at{' '}
                        {new Date(proposal.start_datetime).toLocaleTimeString('en-US', {
                          hour: 'numeric',
                          minute: '2-digit',
                        })}
                      </p>
                      {proposal.notes && (
                        <p className="text-sm text-gray-600 mt-1">{proposal.notes}</p>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Delete Confirmation Modal */}
      <InterviewDeleteModal
        isOpen={isDeleteModalOpen}
        onClose={handleCloseDeleteModal}
        onConfirm={handleConfirmDelete}
        interviewTitle={interview?.title || ''}
        isDeleting={isDeleting}
      />
    </AppLayout>
  );
}

export default function InterviewDetailsPage() {
  return (
    <ProtectedRoute>
      <InterviewDetailsContent />
    </ProtectedRoute>
  );
}
