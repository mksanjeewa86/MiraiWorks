export interface InterviewNote {
  id: number;
  interview_id: number;
  participant_id: number;
  content?: string;
  created_at: string;
  updated_at: string;
}

export interface InterviewNoteUpdate {
  content?: string;
}
