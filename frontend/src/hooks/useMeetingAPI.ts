import { useCallback } from 'react';
import { apiClient } from '../services/api';
import type { Meeting, MeetingJoinResponse } from '../types';

export function useMeetingAPI() {
  const joinMeeting = useCallback(async (roomId: string, accessCode?: string): Promise<MeetingJoinResponse> => {
    const response = await apiClient.post(`/meetings/join/${roomId}`, {
      access_code: accessCode
    });
    return response.data;
  }, []);

  const leaveMeeting = useCallback(async (roomId: string): Promise<void> => {
    await apiClient.post(`/meetings/leave/${roomId}`);
  }, []);

  const getMeeting = useCallback(async (meetingId: number): Promise<Meeting> => {
    const response = await apiClient.get(`/meetings/${meetingId}`);
    return response.data;
  }, []);

  const getMeetingByRoomId = useCallback(async (roomId: string): Promise<Meeting> => {
    const response = await apiClient.get(`/meetings/room/${roomId}`);
    return response.data;
  }, []);

  const listMeetings = useCallback(async (params: {
    status?: string;
    meeting_type?: string;
    page?: number;
    limit?: number;
  } = {}) => {
    const response = await apiClient.get('/meetings', { params });
    return response.data;
  }, []);

  const createMeeting = useCallback(async (meetingData: {
    title: string;
    description?: string;
    meeting_type: string;
    scheduled_start: string;
    scheduled_end: string;
    interview_id?: number;
    participants: Array<{
      user_id: number;
      role: string;
      can_record?: boolean;
    }>;
    recording_enabled?: boolean;
    transcription_enabled?: boolean;
    auto_summary?: boolean;
    access_code?: string;
  }): Promise<Meeting> => {
    const response = await apiClient.post('/meetings', meetingData);
    return response.data;
  }, []);

  const updateMeeting = useCallback(async (meetingId: number, updateData: {
    title?: string;
    description?: string;
    status?: string;
    scheduled_start?: string;
    scheduled_end?: string;
    recording_enabled?: boolean;
    transcription_enabled?: boolean;
    auto_summary?: boolean;
    access_code?: string;
  }): Promise<Meeting> => {
    const response = await apiClient.put(`/meetings/${meetingId}`, updateData);
    return response.data;
  }, []);

  const deleteMeeting = useCallback(async (meetingId: number): Promise<void> => {
    await apiClient.delete(`/meetings/${meetingId}`);
  }, []);

  const getMeetingRecordings = useCallback(async (meetingId: number) => {
    const response = await apiClient.get(`/meetings/${meetingId}/recordings`);
    return response.data;
  }, []);

  const getMeetingTranscripts = useCallback(async (meetingId: number) => {
    const response = await apiClient.get(`/meetings/${meetingId}/transcripts`);
    return response.data;
  }, []);

  const getMeetingTranscript = useCallback(async (meetingId: number, transcriptId: number) => {
    const response = await apiClient.get(`/meetings/${meetingId}/transcripts/${transcriptId}`);
    return response.data;
  }, []);

  const getMeetingSummaries = useCallback(async (meetingId: number) => {
    const response = await apiClient.get(`/meetings/${meetingId}/summaries`);
    return response.data;
  }, []);

  const getMeetingSummary = useCallback(async (meetingId: number, summaryId: number) => {
    const response = await apiClient.get(`/meetings/${meetingId}/summaries/${summaryId}`);
    return response.data;
  }, []);

  return {
    joinMeeting,
    leaveMeeting,
    getMeeting,
    getMeetingByRoomId,
    listMeetings,
    createMeeting,
    updateMeeting,
    deleteMeeting,
    getMeetingRecordings,
    getMeetingTranscripts,
    getMeetingTranscript,
    getMeetingSummaries,
    getMeetingSummary
  };
}