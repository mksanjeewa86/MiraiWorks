// Recruitment Workflow Types

export interface RecruitmentProcess {
  id: number;
  name: string;
  description: string;
  status: 'draft' | 'active' | 'inactive' | 'archived';
  employer_company_id: number;
  position_id?: number;
  created_by: number;
  nodes: ProcessNode[];
  candidate_processes: CandidateProcess[];
  created_at: string;
  updated_at: string;
  is_template: boolean;
}

export interface ProcessNode {
  id: number;
  process_id: number;
  node_type: 'interview' | 'todo' | 'assessment' | 'decision';
  title: string;
  description?: string;
  sequence_order: number;
  position_x: number;
  position_y: number;
  config?: any;
  status: 'draft' | 'active' | 'inactive';
  interview_id?: number;
  todo_id?: number;
}

export interface CandidateProcess {
  id: number;
  candidate_id: number;
  process_id: number;
  current_node_id?: number;
  status: 'not_started' | 'in_progress' | 'completed' | 'failed' | 'withdrawn';
  assigned_recruiter_id?: number;
  overall_score?: number;
  final_result?: string;
}

export interface CreateProcessData {
  name: string;
  description?: string;
  position_id?: number;
  is_template?: boolean;
}

export interface CreateNodeData {
  node_type: 'interview' | 'todo' | 'assessment' | 'decision';
  title: string;
  description?: string;
  sequence_order: number;
  position?: {
    x: number;
    y: number;
  };
  // Legacy fields (deprecated, use position instead)
  position_x?: number;
  position_y?: number;
  config?: any;
  // For linking to existing interviews/todos
  interview_id?: number;
  todo_id?: number;
  // For creating new interviews/todos with the node
  create_interview?: {
    candidate_id?: number;
    position_id?: number;
    scheduled_at?: string;
    duration?: number;
    location?: string;
    meeting_link?: string;
    interview_type?: string;
    notes?: string;
  };
  create_todo?: {
    title: string;
    description?: string;
    category?: string;
    priority?: 'low' | 'medium' | 'high';
    due_date?: string;
    assigned_to?: number;
    is_assignment?: boolean;
    assignment_type?: string;
  };
}

// ============================================================================
// LINEAR WORKFLOW EDITOR
// ============================================================================

// Linear Workflow Step (from app/workflows/page.tsx)
export interface LinearWorkflowStep {
  id: string;
  type: 'interview' | 'todo';
  title: string;
  description?: string;
  config?: any;
  order: number;
  realId?: number; // Actual backend node ID
  isIntegrated?: boolean; // Whether this step creates a real interview/todo
  interview_id?: number; // Linked interview ID (for interview steps)
  todo_id?: number; // Linked todo ID (for todo steps)
}

// Workflow Candidate (from app/workflows/page.tsx)
export interface WorkflowCandidate {
  id: number;
  name: string;
  email: string;
}

// Workflow Viewer (from app/workflows/page.tsx)
export interface WorkflowViewer {
  id: number;
  name: string;
  email: string;
  role: 'viewer' | 'reviewer' | 'manager';
}
