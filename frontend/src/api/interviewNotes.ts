import { API_ENDPOINTS } from './config';
import { apiClient } from './apiClient';
import type { ApiResponse } from '@/types';
import type { InterviewNote, InterviewNoteUpdate } from '@/types/interviewNote';

export const interviewNotesApi = {
  async getNote(interviewId: number): Promise<ApiResponse<InterviewNote>> {
    const response = await apiClient.get<InterviewNote>(
      API_ENDPOINTS.INTERVIEWS.NOTES(interviewId)
    );
    return { data: response.data, success: true };
  },

  async updateNote(
    interviewId: number,
    noteData: InterviewNoteUpdate
  ): Promise<ApiResponse<InterviewNote>> {
    const response = await apiClient.put<InterviewNote>(
      API_ENDPOINTS.INTERVIEWS.NOTES(interviewId),
      noteData
    );
    return { data: response.data, success: true };
  },

  async deleteNote(interviewId: number): Promise<ApiResponse<void>> {
    await apiClient.delete<void>(API_ENDPOINTS.INTERVIEWS.NOTES(interviewId));
    return { data: undefined, success: true };
  },
};
