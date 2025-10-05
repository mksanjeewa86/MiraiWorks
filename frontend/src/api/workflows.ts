import { API_ENDPOINTS } from './config';
import { apiClient } from './apiClient';
import type { ApiResponse } from '@/types';
import { interviewsApi } from './interviews';
import { todosApi } from './todos';
import type {
  RecruitmentProcess,
  ProcessNode,
  CandidateProcess,
  CreateProcessData,
  CreateNodeData,
} from '@/types/workflow';

export const recruitmentWorkflowsApi = {
  // Get all recruitment workflows for current user's company
  async getProcesses(params?: {
    status?: string;
    is_template?: boolean;
  }): Promise<ApiResponse<{ processes: RecruitmentProcess[]; total: number }>> {
    let url = API_ENDPOINTS.WORKFLOWS.BASE;

    if (params) {
      const searchParams = new URLSearchParams();
      if (params.status) searchParams.append('status', params.status);
      if (params.is_template !== undefined)
        searchParams.append('is_template', params.is_template.toString());

      if (searchParams.toString()) {
        url += `?${searchParams.toString()}`;
      }
    }

    const response = await apiClient.get<RecruitmentProcess[]>(url);
    // Backend returns array directly, wrap it in expected format
    return {
      data: {
        processes: response.data || [],
        total: (response.data || []).length,
      },
      success: true,
    };
  },

  // Create new recruitment workflow
  async createProcess(data: CreateProcessData): Promise<ApiResponse<RecruitmentProcess>> {
    const response = await apiClient.post<RecruitmentProcess>(API_ENDPOINTS.WORKFLOWS.BASE, data);
    return { data: response.data, success: true };
  },

  // Get specific workflow with details
  async getProcess(workflowId: number): Promise<ApiResponse<RecruitmentProcess>> {
    const response = await apiClient.get<RecruitmentProcess>(
      `${API_ENDPOINTS.WORKFLOWS.BASE}${workflowId}`
    );
    return { data: response.data, success: true };
  },

  // Update workflow
  async updateProcess(
    workflowId: number,
    data: Partial<CreateProcessData>
  ): Promise<ApiResponse<RecruitmentProcess>> {
    const response = await apiClient.put<RecruitmentProcess>(
      `${API_ENDPOINTS.WORKFLOWS.BASE}${workflowId}`,
      data
    );
    return { data: response.data, success: true };
  },

  // Change workflow status (draft -> active -> inactive -> archived)
  async updateProcessStatus(workflowId: number, status: string): Promise<ApiResponse<RecruitmentProcess>> {
    const response = await apiClient.put<RecruitmentProcess>(
      `${API_ENDPOINTS.WORKFLOWS.BASE}${workflowId}/status`,
      { status }
    );
    return { data: response.data, success: true };
  },

  // Archive workflow
  async archiveProcess(workflowId: number): Promise<ApiResponse<RecruitmentProcess>> {
    const response = await apiClient.post<RecruitmentProcess>(
      `${API_ENDPOINTS.WORKFLOWS.BASE}${workflowId}/archive`,
      {}
    );
    return { data: response.data, success: true };
  },

  // Node management
  async createNode(workflowId: number, data: CreateNodeData): Promise<ApiResponse<ProcessNode>> {
    const response = await apiClient.post<ProcessNode>(
      `${API_ENDPOINTS.WORKFLOWS.BASE}${workflowId}/nodes`,
      data
    );
    return { data: response.data, success: true };
  },

  // Create node with integrated interview/todo creation
  async createNodeWithIntegration(
    workflowId: number,
    data: CreateNodeData
  ): Promise<
    ApiResponse<{
      node: ProcessNode;
      interview?: any;
      todo?: any;
    }>
  > {
    const response = await apiClient.post<{
      node: ProcessNode;
      interview?: any;
      todo?: any;
    }>(`${API_ENDPOINTS.WORKFLOWS.BASE}${workflowId}/nodes/create-with-integration`, data);
    return { data: response.data, success: true };
  },

  async updateNode(
    workflowId: number,
    nodeId: number,
    data: Partial<CreateNodeData>
  ): Promise<ApiResponse<ProcessNode>> {
    const response = await apiClient.put<ProcessNode>(
      `${API_ENDPOINTS.WORKFLOWS.BASE}${workflowId}/nodes/${nodeId}`,
      data
    );
    return { data: response.data, success: true };
  },

  async deleteNode(workflowId: number, nodeId: number): Promise<ApiResponse<void>> {
    await apiClient.delete(`${API_ENDPOINTS.WORKFLOWS.BASE}${workflowId}/nodes/${nodeId}`);
    return { data: undefined, success: true };
  },

  // Candidate management
  async assignCandidates(
    workflowId: number,
    candidateIds: number[]
  ): Promise<ApiResponse<CandidateProcess[]>> {
    const response = await apiClient.post<CandidateProcess[]>(
      `${API_ENDPOINTS.WORKFLOWS.BASE}${workflowId}/candidates/assign`,
      { candidate_ids: candidateIds }
    );
    return { data: response.data, success: true };
  },

  async getCandidateProcess(
    workflowId: number,
    candidateId: number
  ): Promise<ApiResponse<CandidateProcess>> {
    const response = await apiClient.get<CandidateProcess>(
      `${API_ENDPOINTS.WORKFLOWS.BASE}${workflowId}/candidates/${candidateId}`
    );
    return { data: response.data, success: true };
  },

  // Progress candidate to next node and trigger interview/todo creation
  async progressCandidate(
    workflowId: number,
    candidateId: number,
    nodeId: number
  ): Promise<
    ApiResponse<{
      candidate_process: CandidateProcess;
      created_interview?: any;
      created_todo?: any;
    }>
  > {
    const response = await apiClient.post<{
      candidate_process: CandidateProcess;
      created_interview?: any;
      created_todo?: any;
    }>(`${API_ENDPOINTS.WORKFLOWS.BASE}${workflowId}/candidates/${candidateId}/progress`, {
      next_node_id: nodeId,
    });
    return { data: response.data, success: true };
  },

  // Statistics and analytics
  async getProcessStats(workflowId: number): Promise<
    ApiResponse<{
      total_candidates: number;
      completed_candidates: number;
      in_progress_candidates: number;
      failed_candidates: number;
      average_completion_time: number;
      node_completion_rates: { node_id: number; completion_rate: number }[];
    }>
  > {
    const response = await apiClient.get<{
      total_candidates: number;
      completed_candidates: number;
      in_progress_candidates: number;
      failed_candidates: number;
      average_completion_time: number;
      node_completion_rates: { node_id: number; completion_rate: number }[];
    }>(`${API_ENDPOINTS.WORKFLOWS.BASE}${workflowId}/stats`);
    return { data: response.data, success: true };
  },

  // Get linked interviews and todos for a workflow
  async getProcessIntegrations(workflowId: number): Promise<
    ApiResponse<{
      interviews: any[];
      todos: any[];
      nodes_with_links: { node_id: number; interview_id?: number; todo_id?: number }[];
    }>
  > {
    const response = await apiClient.get<{
      interviews: any[];
      todos: any[];
      nodes_with_links: { node_id: number; interview_id?: number; todo_id?: number }[];
    }>(`${API_ENDPOINTS.WORKFLOWS.BASE}${workflowId}/integrations`);
    return { data: response.data, success: true };
  },
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
  }): Promise<
    ApiResponse<{
      process: RecruitmentProcess;
      created_interviews: any[];
      created_todos: any[];
    }>
  > {
    // Create the workflow first
    const processResponse = await recruitmentWorkflowsApi.createProcess({
      name: data.name,
      description: data.description,
      position_id: data.position_id,
    });

    if (!processResponse.success || !processResponse.data) {
      throw new Error('Failed to create recruitment workflow');
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
          x: 100 + i * 200, // Simple horizontal layout
          y: 100,
        },
      };

      // Add interview/todo creation data
      if (step.type === 'interview' && step.interview_config) {
        nodeData.create_interview = {
          position_id: data.position_id,
          duration: step.interview_config.duration || 60,
          interview_type: step.interview_config.interview_type || 'video',
          location: step.interview_config.location,
          notes: `Auto-generated for workflow: ${data.name}`,
        };
      }

      if (step.type === 'todo' && step.todo_config) {
        nodeData.create_todo = {
          title: step.title,
          description: step.description || `Assignment for workflow: ${data.name}`,
          category: step.todo_config.category || 'coding_test',
          priority: step.todo_config.priority || 'medium',
          is_assignment: step.todo_config.is_assignment !== false,
          assignment_type: step.todo_config.assignment_type || 'coding',
        };
      }

      // Create node with integration
      try {
        const nodeResponse = await recruitmentWorkflowsApi.createNodeWithIntegration(
          process.id,
          nodeData
        );
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
        created_todos: createdTodos,
      },
      success: true,
    };
  },
};
