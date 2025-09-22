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
  Clock4
} from 'lucide-react';
import Link from 'next/link';
import AppLayout from '@/components/layout/AppLayout';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import { useToast } from '@/contexts/ToastContext';
import { interviewsApi } from '@/api/interviews';
import type { Interview } from '@/types/interview';

function InterviewDetailsContent() {
  const params = useParams();
  const router = useRouter();
  const { showToast } = useToast();
  const [interview, setInterview] = useState<Interview | null>(null);
  const [loading, setLoading] = useState(true);
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

        setInterview(interview);
      } catch (err) {
        console.error('Error fetching interview:', err);
        setError(err instanceof Error ? err.message : 'Failed to fetch interview details');
      } finally {
        setLoading(false);
      }
    };

    fetchInterview();
  }, [interviewId]);

  const handleDelete = async () => {
    if (!interview || !window.confirm('Are you sure you want to delete this interview? This action cannot be undone.')) {
      return;
    }

    try {
      await interviewsApi.delete(interview.id);
      showToast({
        type: 'success',
        title: 'Interview Deleted',
        message: 'The interview has been successfully deleted'
      });
      router.push('/interviews');
    } catch (err) {
      console.error('Error deleting interview:', err);
      showToast({
        type: 'error',
        title: 'Error',
        message: err instanceof Error ? err.message : 'Failed to delete interview'
      });
    }
  };

  const getStatusBadge = (status: Interview['status']) => {
    const statusConfig = {
      pending_schedule: { icon: Clock4, color: 'bg-yellow-100 text-yellow-800', label: 'Pending Schedule' },
      scheduled: { icon: Calendar, color: 'bg-blue-100 text-blue-800', label: 'Scheduled' },
      confirmed: { icon: CheckCircle, color: 'bg-green-100 text-green-800', label: 'Confirmed' },
      in_progress: { icon: Clock, color: 'bg-purple-100 text-purple-800', label: 'In Progress' },
      completed: { icon: CheckCircle, color: 'bg-green-100 text-green-800', label: 'Completed' },
      cancelled: { icon: XCircle, color: 'bg-red-100 text-red-800', label: 'Cancelled' }
    };

    const config = statusConfig[status] || statusConfig.pending_schedule;
    const IconComponent = config.icon;

    return (
      <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${config.color}`}>
        <IconComponent className="h-4 w-4 mr-1" />
        {config.label}
      </span>
    );
  };

  const getTypeBadge = (type: Interview['interview_type']) => {
    const typeConfig = {
      video: { icon: Video, color: 'bg-purple-100 text-purple-800', label: 'Video Call' },
      phone: { icon: Phone, color: 'bg-green-100 text-green-800', label: 'Phone Call' },
      in_person: { icon: Users, color: 'bg-indigo-100 text-indigo-800', label: 'In-Person' }
    };

    const config = typeConfig[type];
    const IconComponent = config.icon;

    return (
      <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${config.color}`}>
        <IconComponent className="h-4 w-4 mr-1" />
        {config.label}
      </span>
    );
  };

  const formatDateTime = (dateTime: string) => {
    const date = new Date(dateTime);
    return {
      date: date.toLocaleDateString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      }),
      time: date.toLocaleTimeString('en-US', {
        hour: 'numeric',
        minute: '2-digit',
        hour12: true
      })
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
            <p className="text-gray-600 mb-4">{error || 'The interview you are looking for could not be found.'}</p>
            <Link
              href="/interviews"
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
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center">
            <button
              onClick={() => router.back()}
              className="mr-4 p-2 text-gray-600 hover:text-gray-900 rounded-lg hover:bg-gray-100"
            >
              <ArrowLeft className="h-5 w-5" />
            </button>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{interview.title}</h1>
              <p className="text-gray-600">Interview Details</p>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            {/* Show video call button for video interviews */}
            {interview.interview_type === 'video' && (
              <Link
                href={`/video-call/${interview.id}`}
                className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg flex items-center gap-2"
              >
                <Video className="h-4 w-4" />
                Start Video Call
              </Link>
            )}
            <Link
              href={`/interviews/${interview.id}/edit`}
              className="bg-white hover:bg-gray-50 text-gray-700 border border-gray-300 px-4 py-2 rounded-lg flex items-center gap-2"
            >
              <Edit className="h-4 w-4" />
              Edit
            </Link>
            <button
              onClick={handleDelete}
              className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg flex items-center gap-2"
            >
              <Trash2 className="h-4 w-4" />
              Delete
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Basic Information */}
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Interview Information</h2>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Status</label>
                  {getStatusBadge(interview.status)}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Type</label>
                  {getTypeBadge(interview.interview_type)}
                </div>

                {interview.position_title && (
                  <div className="md:col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-2">Position</label>
                    <p className="text-gray-900">{interview.position_title}</p>
                  </div>
                )}

                {interview.description && (
                  <div className="md:col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
                    <p className="text-gray-900">{interview.description}</p>
                  </div>
                )}
              </div>
            </div>

            {/* Schedule Information */}
            {(interview.scheduled_start || interview.scheduled_end) && (
              <div className="bg-white rounded-lg border border-gray-200 p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <Calendar className="h-5 w-5 mr-2" />
                  Schedule
                </h2>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {startTime && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Start Time</label>
                      <div>
                        <p className="text-gray-900 font-medium">{startTime.date}</p>
                        <p className="text-gray-600">{startTime.time}</p>
                      </div>
                    </div>
                  )}

                  {endTime && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">End Time</label>
                      <div>
                        <p className="text-gray-900 font-medium">{endTime.date}</p>
                        <p className="text-gray-600">{endTime.time}</p>
                      </div>
                    </div>
                  )}

                  {interview.timezone && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Timezone</label>
                      <p className="text-gray-900">{interview.timezone}</p>
                    </div>
                  )}

                  {(interview.duration_minutes) && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Duration</label>
                      <p className="text-gray-900">{interview.duration_minutes} minutes</p>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Location/Meeting Details */}
            {(interview.location || interview.meeting_url) && (
              <div className="bg-white rounded-lg border border-gray-200 p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <MapPin className="h-5 w-5 mr-2" />
                  Location & Meeting Details
                </h2>

                <div className="space-y-4">
                  {interview.location && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Location</label>
                      <p className="text-gray-900">{interview.location}</p>
                    </div>
                  )}

                  {interview.meeting_url && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Meeting URL</label>
                      <a
                        href={interview.meeting_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:text-blue-800 hover:underline break-all"
                      >
                        {interview.meeting_url}
                      </a>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Notes */}
            {(interview.notes || interview.preparation_notes) && (
              <div className="bg-white rounded-lg border border-gray-200 p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <FileText className="h-5 w-5 mr-2" />
                  Notes
                </h2>

                <div className="space-y-6">
                  {interview.notes && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Interview Notes</label>
                      <div className="bg-gray-50 rounded-lg p-4">
                        <p className="text-gray-900 whitespace-pre-wrap">{interview.notes}</p>
                      </div>
                    </div>
                  )}

                  {interview.preparation_notes && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Preparation Notes</label>
                      <div className="bg-gray-50 rounded-lg p-4">
                        <p className="text-gray-900 whitespace-pre-wrap">{interview.preparation_notes}</p>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Participants */}
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <User className="h-5 w-5 mr-2" />
                Participants
              </h3>

              <div className="space-y-4">
                {interview.candidate && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Candidate</label>
                    <div className="flex items-center space-x-3">
                      <div className="h-8 w-8 bg-blue-100 rounded-full flex items-center justify-center">
                        <User className="h-4 w-4 text-blue-600" />
                      </div>
                      <div>
                        <p className="text-sm font-medium text-gray-900">
                          {interview.candidate.first_name} {interview.candidate.last_name}
                        </p>
                        <p className="text-sm text-gray-500">{interview.candidate.email}</p>
                      </div>
                    </div>
                  </div>
                )}

                {interview.recruiter && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Recruiter</label>
                    <div className="flex items-center space-x-3">
                      <div className="h-8 w-8 bg-green-100 rounded-full flex items-center justify-center">
                        <User className="h-4 w-4 text-green-600" />
                      </div>
                      <div>
                        <p className="text-sm font-medium text-gray-900">
                          {interview.recruiter.first_name} {interview.recruiter.last_name}
                        </p>
                        <p className="text-sm text-gray-500">{interview.recruiter.email}</p>
                      </div>
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
                      minute: '2-digit'
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
                      minute: '2-digit'
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
                        minute: '2-digit'
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
                        minute: '2-digit'
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
                        <span className="text-sm font-medium text-gray-900">{proposal.proposer_name}</span>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                          proposal.status === 'accepted' ? 'bg-green-100 text-green-800' :
                          proposal.status === 'declined' ? 'bg-red-100 text-red-800' :
                          proposal.status === 'expired' ? 'bg-gray-100 text-gray-800' :
                          'bg-yellow-100 text-yellow-800'
                        }`}>
                          {proposal.status.charAt(0).toUpperCase() + proposal.status.slice(1)}
                        </span>
                      </div>
                      <p className="text-sm text-gray-600">
                        {new Date(proposal.start_datetime).toLocaleDateString()} at{' '}
                        {new Date(proposal.start_datetime).toLocaleTimeString('en-US', {
                          hour: 'numeric',
                          minute: '2-digit'
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