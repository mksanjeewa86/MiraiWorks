import { API_ENDPOINTS } from './config';
import { apiClient } from './apiClient';
import type { ApiResponse } from '@/types';
import { interviewsApi } from './interviews';
import { todosApi } from './todos';

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

export const recruitmentWorkflowsApi = {
  // Get all recruitment processes for current user's company
  async getProcesses(params?: {
    status?: string;
    is_template?: boolean;
  }): Promise<ApiResponse<{ processes: RecruitmentProcess[]; total: number }>> {
    let url = '/api/recruitment-processes/';

    if (params) {
      const searchParams = new URLSearchParams();
      if (params.status) searchParams.append('status', params.status);
      if (params.is_template !== undefined) searchParams.append('is_template', params.is_template.toString());

      if (searchParams.toString()) {
        url += `?${searchParams.toString()}`;
      }
    }

    const response = await apiClient.get<RecruitmentProcess[]>(url);
    // Backend returns array directly, wrap it in expected format
    return {
      data: {
        processes: response.data || [],
        total: (response.data || []).length
      },
      success: true
    };
  },

  // Create new recruitment process
  async createProcess(data: CreateProcessData): Promise<ApiResponse<RecruitmentProcess>> {
    const response = await apiClient.post<RecruitmentProcess>('/api/recruitment-processes/', data);
    return { data: response.data, success: true };
  },

  // Get specific process with details
  async getProcess(id: number): Promise<ApiResponse<RecruitmentProcess>> {
    const response = await apiClient.get<RecruitmentProcess>(`/api/recruitment-processes/${id}`);
    return { data: response.data, success: true };
  },

  // Update process
  async updateProcess(id: number, data: Partial<CreateProcessData>): Promise<ApiResponse<RecruitmentProcess>> {
    const response = await apiClient.put<RecruitmentProcess>(`/api/recruitment-processes/${id}`, data);
    return { data: response.data, success: true };
  },

  // Change process status (draft -> active -> inactive -> archived)
  async updateProcessStatus(id: number, status: string): Promise<ApiResponse<RecruitmentProcess>> {
    const response = await apiClient.put<RecruitmentProcess>(`/api/recruitment-processes/${id}/status`, { status });
    return { data: response.data, success: true };
  },

  // Archive process
  async archiveProcess(id: number): Promise<ApiResponse<RecruitmentProcess>> {
    const response = await apiClient.post(`/api/recruitment-processes/${id}/archive`, {});
    return { data: response.data, success: true };
  },

  // Node management
  async createNode(processId: number, data: CreateNodeData): Promise<ApiResponse<ProcessNode>> {
    const response = await apiClient.post<ProcessNode>(`/api/recruitment-processes/${processId}/nodes`, data);
    return { data: response.data, success: true };
  },

  // Create node with integrated interview/todo creation
  async createNodeWithIntegration(processId: number, data: CreateNodeData): Promise<ApiResponse<{
    node: ProcessNode;
    interview?: any;
    todo?: any;
  }>> {
    const response = await apiClient.post<{
      node: ProcessNode;
      interview?: any;
      todo?: any;
    }>(`/api/recruitment-processes/${processId}/nodes/create-with-integration`, data);
    return { data: response.data, success: true };
  },

  async updateNode(processId: number, nodeId: number, data: Partial<CreateNodeData>): Promise<ApiResponse<ProcessNode>> {
    const response = await apiClient.put<ProcessNode>(`/api/recruitment-processes/${processId}/nodes/${nodeId}`, data);
    return { data: response.data, success: true };
  },

  async deleteNode(processId: number, nodeId: number): Promise<ApiResponse<void>> {
    await apiClient.delete(`/api/recruitment-processes/${processId}/nodes/${nodeId}`);
    return { data: undefined, success: true };
  },

  // Candidate management
  async assignCandidates(processId: number, candidateIds: number[]): Promise<ApiResponse<CandidateProcess[]>> {
    const response = await apiClient.post<CandidateProcess[]>(
      `/api/recruitment-processes/${processId}/candidates/assign`,
      { candidate_ids: candidateIds }
    );
    return { data: response.data, success: true };
  },

  async getCandidateProcess(processId: number, candidateId: number): Promise<ApiResponse<CandidateProcess>> {
    const response = await apiClient.get<CandidateProcess>(
      `/api/recruitment-processes/${processId}/candidates/${candidateId}`
    );
    return { data: response.data, success: true };
  },

  // Progress candidate to next node and trigger interview/todo creation
  async progressCandidate(processId: number, candidateId: number, nodeId: number): Promise<ApiResponse<{
    candidate_process: CandidateProcess;
    created_interview?: any;
    created_todo?: any;
  }>> {
    const response = await apiClient.post<{
      candidate_process: CandidateProcess;
      created_interview?: any;
      created_todo?: any;
    }>(
      `/api/recruitment-processes/${processId}/candidates/${candidateId}/progress`,
      { next_node_id: nodeId }
    );
    return { data: response.data, success: true };
  },

  // Statistics and analytics
  async getProcessStats(processId: number): Promise<ApiResponse<{
    total_candidates: number;
    completed_candidates: number;
    in_progress_candidates: number;
    failed_candidates: number;
    average_completion_time: number;
    node_completion_rates: { node_id: number; completion_rate: number }[];
  }>> {
    const response = await apiClient.get<{
      total_candidates: number;
      completed_candidates: number;
      in_progress_candidates: number;
      failed_candidates: number;
      average_completion_time: number;
      node_completion_rates: { node_id: number; completion_rate: number }[];
    }>(`/api/recruitment-processes/${processId}/stats`);
    return { data: response.data, success: true };
  },

  // Get linked interviews and todos for a process
  async getProcessIntegrations(processId: number): Promise<ApiResponse<{
    interviews: any[];
    todos: any[];
    nodes_with_links: { node_id: number; interview_id?: number; todo_id?: number; }[];
  }>> {
    const response = await apiClient.get<{
      interviews: any[];
      todos: any[];
      nodes_with_links: { node_id: number; interview_id?: number; todo_id?: number; }[];
    }>(`/api/recruitment-processes/${processId}/integrations`);
    return { data: response.data, success: true };
  }
};

// Workflow service for managing integrated workflows
export const workflowIntegrationService = {
  // Create a complete workflow with interview and todo nodes
  async createCompleteWorkflow(data: {
    name: string;
    description?: string;
    position_id?: number;
    workflow_steps: Array<{
      type: 'interview' | 'todo' | 'assessment' | 'decision';
      title: string;
      description?: string;
      interview_config?: {
        duration?: number;
        interview_type?: string;
        location?: string;
      };
      todo_config?: {
        category?: string;
        priority?: 'low' | 'medium' | 'high';
        is_assignment?: boolean;
        assignment_type?: string;
      };
    }>;
  }): Promise<ApiResponse<{
    process: RecruitmentProcess;
    created_interviews: any[];
    created_todos: any[];
  }>> {
    // Create the process first
    const processResponse = await recruitmentWorkflowsApi.createProcess({
      name: data.name,
      description: data.description,
      position_id: data.position_id
    });

    if (!processResponse.success || !processResponse.data) {
      throw new Error('Failed to create recruitment process');
    }

    const process = processResponse.data;
    const createdInterviews: any[] = [];
    const createdTodos: any[] = [];

    // Create nodes with integrations
    for (let i = 0; i < data.workflow_steps.length; i++) {
      const step = data.workflow_steps[i];

      const nodeData: CreateNodeData = {
        node_type: step.type,
        title: step.title,
        description: step.description,
        sequence_order: i + 1,
        position: {
          x: 100 + (i * 200), // Simple horizontal layout
          y: 100
        }
      };

      // Add interview/todo creation data
      if (step.type === 'interview' && step.interview_config) {
        nodeData.create_interview = {
          position_id: data.position_id,
          duration: step.interview_config.duration || 60,
          interview_type: step.interview_config.interview_type || 'video',
          location: step.interview_config.location,
          notes: `Auto-generated for workflow: ${data.name}`
        };
      }

      if (step.type === 'todo' && step.todo_config) {
        nodeData.create_todo = {
          title: step.title,
          description: step.description || `Assignment for workflow: ${data.name}`,
          category: step.todo_config.category || 'coding_test',
          priority: step.todo_config.priority || 'medium',
          is_assignment: step.todo_config.is_assignment !== false,
          assignment_type: step.todo_config.assignment_type || 'coding'
        };
      }

      // Create node with integration
      try {
        const nodeResponse = await recruitmentWorkflowsApi.createNodeWithIntegration(process.id, nodeData);
        if (nodeResponse.success && nodeResponse.data) {
          if (nodeResponse.data.interview) {
            createdInterviews.push(nodeResponse.data.interview);
          }
          if (nodeResponse.data.todo) {
            createdTodos.push(nodeResponse.data.todo);
          }
        }
      } catch (error) {
        console.warn(`Failed to create integrated node ${i + 1}:`, error);
        // Fallback to regular node creation
        await recruitmentWorkflowsApi.createNode(process.id, nodeData);
      }
    }

    return {
      data: {
        process,
        created_interviews: createdInterviews,
        created_todos: createdTodos
      },
      success: true
    };
  }
};