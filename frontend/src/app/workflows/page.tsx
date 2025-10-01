'use client';

import React, { useState, useEffect, useRef } from 'react';
import type { CSSProperties } from 'react';
import AppLayout from '@/components/layout/AppLayout';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import { useAuth } from '@/contexts/AuthContext';
import { recruitmentWorkflowsApi, workflowIntegrationService, type RecruitmentProcess, type ProcessNode, type CreateNodeData } from '@/api/workflows';
import { interviewsApi } from '@/api/interviews';
import { todosApi } from '@/api/todos';
import TaskModal from '@/components/todos/TaskModal';
import type { Todo } from '@/types/todo';
import type { Interview } from '@/types/interview';
import {
  GitBranch,
  Search,
  Filter,
  Plus,
  Eye,
  Edit,
  Trash2,
  Download,
  Users,
  PlayCircle,
  PauseCircle,
  Archive,
  Calendar,
  TrendingUp,
  Clock,
  CheckSquare,
  X,
  Video,
  Play,
  Square,
  Circle,
} from 'lucide-react';

// No more mock data - using real API integration

function RecruitmentWorkflowsPageContent() {
  const { user, isLoading: authLoading } = useAuth();
  const [processes, setProcesses] = useState<RecruitmentProcess[]>([]);
  const [filteredProcesses, setFilteredProcesses] = useState<RecruitmentProcess[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [sortBy, setSortBy] = useState<'name' | 'createdAt' | 'candidatesCount' | 'status'>('createdAt');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;
  const [isNewProcessOpen, setIsNewProcessOpen] = useState(false);
  const [selectedProcess, setSelectedProcess] = useState<RecruitmentProcess | null>(null);
  const [isViewModalOpen, setIsViewModalOpen] = useState(false);
  const [isWorkflowEditorOpen, setIsWorkflowEditorOpen] = useState(false);
  const [editingProcess, setEditingProcess] = useState<RecruitmentProcess | null>(null);

  // Load processes from API
  useEffect(() => {
    const loadProcesses = async () => {
      if (authLoading || !user) {
        return;
      }

      try {
        setLoading(true);
        setError(null);

        const response = await recruitmentWorkflowsApi.getProcesses();
        if (response.success && response.data && response.data.processes) {
          // Map API data to local format
          const mappedProcesses = response.data.processes.map((process: any) => ({
            id: process.id,
            name: process.name,
            description: process.description || '',
            status: process.status,
            employer_company_id: process.employer_company_id,
            position_id: process.position_id,
            created_by: process.created_by,
            nodes: process.nodes || [],
            candidate_processes: process.candidate_processes || [],
            created_at: process.created_at,
            updated_at: process.updated_at,
            is_template: process.is_template || false
          }));
          setProcesses(mappedProcesses);
        } else {
          // If no processes exist, start with empty array (not mock data)
          setProcesses([]);
        }
      } catch (err) {
        console.error('Error loading recruitment processes:', err);
        setError(err instanceof Error ? err.message : 'Failed to load recruitment processes');
        // Start with empty array on error
        setProcesses([]);
      } finally {
        setLoading(false);
      }
    };

    loadProcesses();
  }, [user, authLoading]);

  // Apply filters and search
  useEffect(() => {
    const filtered = processes.filter((process) => {
      const matchesSearch =
        process.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        process.description.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesStatus = statusFilter === 'all' || process.status === statusFilter;
      return matchesSearch && matchesStatus;
    });

    // Sort
    filtered.sort((a, b) => {
      let aValue, bValue;
      switch (sortBy) {
        case 'name':
          aValue = a.name.toLowerCase();
          bValue = b.name.toLowerCase();
          break;
        case 'createdAt':
          aValue = new Date(a.created_at).getTime();
          bValue = new Date(b.created_at).getTime();
          break;
        case 'candidatesCount':
          aValue = a.candidate_processes?.length || 0;
          bValue = b.candidate_processes?.length || 0;
          break;
        case 'status':
          aValue = a.status;
          bValue = b.status;
          break;
        default:
          return 0;
      }
      if (sortOrder === 'asc') {
        return aValue < bValue ? -1 : aValue > bValue ? 1 : 0;
      } else {
        return aValue > bValue ? -1 : aValue < bValue ? 1 : 0;
      }
    });

    setFilteredProcesses(filtered);
    setCurrentPage(1);
  }, [processes, searchTerm, statusFilter, sortBy, sortOrder]);

  // Pagination
  const totalPages = Math.ceil(filteredProcesses.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const currentProcesses = filteredProcesses.slice(startIndex, endIndex);

  // Statistics
  const stats = {
    total: processes.length,
    active: processes.filter((p) => p.status === 'active').length,
    totalCandidates: processes.reduce((sum, p) => sum + (p.candidate_processes?.length || 0), 0),
    avgNodes: Math.round(processes.reduce((sum, p) => sum + p.nodes.length, 0) / processes.length) || 0,
  };

  // Helper functions
  const getStatusBadge = (status: RecruitmentProcess['status']) => {
    const styles = {
      draft: 'bg-gray-100 text-gray-800 border-gray-200',
      active: 'bg-green-100 text-green-800 border-green-200',
      inactive: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      archived: 'bg-red-100 text-red-800 border-red-200',
    };
    return styles[status] || styles.draft;
  };

  const getNodeTypeIcon = (type: ProcessNode['node_type']) => {
    switch (type) {
      case 'interview': return <Video className="h-3 w-3" />;
      case 'todo': return <CheckSquare className="h-3 w-3" />;
      case 'assessment': return <TrendingUp className="h-3 w-3" />;
      case 'decision': return <GitBranch className="h-3 w-3" />;
      default: return <GitBranch className="h-3 w-3" />;
    }
  };

  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString);
      if (isNaN(date.getTime())) return 'Recently';
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
      });
    } catch {
      return 'Recently';
    }
  };

  const handleSort = (field: typeof sortBy) => {
    if (sortBy === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(field);
      setSortOrder('desc');
    }
  };

  const clearFilters = () => {
    setSearchTerm('');
    setStatusFilter('all');
  };

  // Action handlers
  const handleViewWorkflow = (process: RecruitmentProcess) => {
    setSelectedProcess(process);
    setIsViewModalOpen(true);
  };

  const handleEditWorkflow = (process: RecruitmentProcess) => {
    setEditingProcess(process);
    setIsWorkflowEditorOpen(true);
  };

  const handleToggleStatus = async (process: RecruitmentProcess) => {
    const newStatus = process.status === 'draft' ? 'active' :
                     process.status === 'active' ? 'inactive' : 'active';

    try {
      const response = await recruitmentWorkflowsApi.updateProcessStatus(process.id, newStatus);
      if (response.success) {
        // Update the process status locally
        setProcesses(prev => prev.map(p =>
          p.id === process.id ? { ...p, status: newStatus } : p
        ));
        alert(`Changed ${process.name} status to: ${newStatus}`);
      }
    } catch (err) {
      console.error('Failed to update process status:', err);
      alert('Failed to update workflow status');
    }
  };

  const handleArchiveWorkflow = async (process: RecruitmentProcess) => {
    if ((process.candidate_processes?.length || 0) > 0) {
      const confirmed = confirm(
        `This workflow has ${process.candidate_processes?.length || 0} active candidates. Are you sure you want to archive it?`
      );
      if (!confirmed) return;
    }

    try {
      const response = await recruitmentWorkflowsApi.archiveProcess(process.id);
      if (response.success) {
        // Remove the archived process from the list
        setProcesses(prev => prev.filter(p => p.id !== process.id));
        alert(`Archived workflow: ${process.name}`);
      }
    } catch (err) {
      console.error('Failed to archive process:', err);
      alert('Failed to archive workflow');
    }
  };

  const handleCreateWorkflow = async (formData: any) => {
    try {
      let response;
      let newProcess: RecruitmentProcess;

      // If template is selected, use integrated workflow creation
      if (formData.useTemplate && formData.templateSteps) {
        const workflowData = {
          name: formData.name,
          description: formData.description,
          position_id: formData.position_id,
          workflow_steps: formData.templateSteps
        };

        const integratedResponse = await workflowIntegrationService.createCompleteWorkflow(workflowData);
        if (integratedResponse.success && integratedResponse.data) {
          const processData = integratedResponse.data.process;
          newProcess = {
            id: processData.id,
            name: processData.name,
            description: processData.description || '',
            status: processData.status,
            employer_company_id: processData.employer_company_id,
            position_id: processData.position_id,
            created_by: processData.created_by,
            nodes: processData.nodes || [],
            candidate_processes: processData.candidate_processes || [],
            created_at: processData.created_at,
            updated_at: processData.updated_at,
            is_template: processData.is_template || false
          };

          // Show success message with integration details
          const interviewCount = integratedResponse.data.created_interviews.length;
          const todoCount = integratedResponse.data.created_todos.length;
          alert(
            `✅ Created workflow: ${formData.name}\n` +
            `📝 Created ${processData.nodes?.length || 0} workflow steps\n` +
            `🎙️ Created ${interviewCount} interview templates\n` +
            `📋 Created ${todoCount} todo assignments\n\n` +
            `The workflow is now linked to real interviews and todos!`
          );
        } else {
          throw new Error('Failed to create integrated workflow');
        }
      } else {
        // Regular workflow creation
        const createData = {
          name: formData.name,
          description: formData.description,
          is_template: formData.isTemplate || false
        };

        response = await recruitmentWorkflowsApi.createProcess(createData);
        if (response.success && response.data) {
          newProcess = {
            id: response.data.id,
            name: response.data.name,
            description: response.data.description || '',
            status: response.data.status,
            employer_company_id: response.data.employer_company_id,
            position_id: response.data.position_id,
            created_by: response.data.created_by,
            nodes: response.data.nodes || [],
            candidate_processes: response.data.candidate_processes || [],
            created_at: response.data.created_at,
            updated_at: response.data.updated_at,
            is_template: response.data.is_template || false
          };

          alert(`Created new workflow: ${formData.name}`);
        } else {
          throw new Error('Failed to create workflow');
        }
      }

      setProcesses(prev => [newProcess, ...prev]);
      setIsNewProcessOpen(false);
    } catch (err) {
      console.error('Failed to create workflow:', err);
      alert('Failed to create workflow: ' + (err instanceof Error ? err.message : 'Unknown error'));
    }
  };

  // Show loading spinner while auth is loading
  if (authLoading) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center min-h-64">
          <div
            className="loading-spinner border-gray-300 border-t-brand-primary h-8 w-8"
            aria-label="Loading"
          ></div>
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout>
      {/* Modals */}
      <NewWorkflowModal
        isOpen={isNewProcessOpen}
        onClose={() => setIsNewProcessOpen(false)}
        onSubmit={handleCreateWorkflow}
      />
      <ViewWorkflowModal
        isOpen={isViewModalOpen}
        onClose={() => setIsViewModalOpen(false)}
        process={selectedProcess}
        onEdit={handleEditWorkflow}
      />
      <WorkflowEditorModal
        isOpen={isWorkflowEditorOpen}
        onClose={() => {
          setIsWorkflowEditorOpen(false);
          setEditingProcess(null);
        }}
        process={editingProcess}
        onSave={(updatedProcess) => {
          setProcesses(prev => prev.map(p =>
            p.id === updatedProcess.id ? updatedProcess : p
          ));
          setIsWorkflowEditorOpen(false);
          setEditingProcess(null);
        }}
      />

      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
              <GitBranch className="h-6 w-6 text-violet-600" />
              Workflows
            </h1>
            <p className="text-gray-600 mt-1">
              Create and manage hiring workflows with interviews, tasks, and assessments
            </p>
          </div>
          <div className="flex items-center gap-3">
            <button className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
              <Download className="h-4 w-4" />
              Export
            </button>
            <button
              type="button"
              onClick={() => setIsNewProcessOpen(true)}
              className="flex items-center gap-2 px-4 py-2 bg-violet-600 text-white rounded-lg hover:bg-violet-700 transition-colors"
            >
              <Plus className="h-4 w-4" />
              New Workflow
            </button>
          </div>
        </div>

        {/* Statistics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-white p-6 rounded-lg border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Workflows</p>
                <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
              </div>
              <div className="p-3 bg-violet-100 rounded-full">
                <GitBranch className="h-6 w-6 text-violet-600" />
              </div>
            </div>
          </div>
          <div className="bg-white p-6 rounded-lg border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Active</p>
                <p className="text-2xl font-bold text-green-600">{stats.active}</p>
              </div>
              <div className="p-3 bg-green-100 rounded-full">
                <PlayCircle className="h-6 w-6 text-green-600" />
              </div>
            </div>
          </div>
          <div className="bg-white p-6 rounded-lg border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Candidates</p>
                <p className="text-2xl font-bold text-blue-600">{stats.totalCandidates}</p>
              </div>
              <div className="p-3 bg-blue-100 rounded-full">
                <Users className="h-6 w-6 text-blue-600" />
              </div>
            </div>
          </div>
          <div className="bg-white p-6 rounded-lg border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Avg. Steps</p>
                <p className="text-2xl font-bold text-purple-600">{stats.avgNodes}</p>
              </div>
              <div className="p-3 bg-purple-100 rounded-full">
                <TrendingUp className="h-6 w-6 text-purple-600" />
              </div>
            </div>
          </div>
        </div>

        {/* Filters and Search */}
        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <div className="flex flex-col lg:flex-row gap-4">
            {/* Search */}
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search workflows by name or description..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-violet-500 focus:border-transparent"
                />
              </div>
            </div>
            {/* Filters */}
            <div className="flex flex-wrap gap-3">
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="pl-4 pr-10 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-violet-500 appearance-none bg-white"
                style={{
                  backgroundImage: `url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M6 8l4 4 4-4'/%3e%3c/svg%3e")`,
                  backgroundPosition: 'right 12px center',
                  backgroundRepeat: 'no-repeat',
                  backgroundSize: '16px',
                } as CSSProperties}
              >
                <option value="all">All Status</option>
                <option value="draft">Draft</option>
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
                <option value="archived">Archived</option>
              </select>
              <button
                onClick={clearFilters}
                className="px-3 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              >
                <Filter className="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-center gap-2">
              <div className="text-red-600">
                <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                  <path
                    fillRule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                    clipRule="evenodd"
                  />
                </svg>
              </div>
              <p className="text-red-800 font-medium">{error}</p>
            </div>
          </div>
        )}

        {/* Workflows Table */}
        <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                    onClick={() => handleSort('name')}
                  >
                    <div className="flex items-center gap-1">
                      Workflow
                      {sortBy === 'name' && (
                        <span className="text-xs">{sortOrder === 'asc' ? '↑' : '↓'}</span>
                      )}
                    </div>
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status & Nodes
                  </th>
                  <th
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                    onClick={() => handleSort('candidatesCount')}
                  >
                    <div className="flex items-center gap-1">
                      Candidates
                      {sortBy === 'candidatesCount' && (
                        <span className="text-xs">{sortOrder === 'asc' ? '↑' : '↓'}</span>
                      )}
                    </div>
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Progress
                  </th>
                  <th
                    className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                    onClick={() => handleSort('createdAt')}
                  >
                    <div className="flex items-center gap-1">
                      Created
                      {sortBy === 'createdAt' && (
                        <span className="text-xs">{sortOrder === 'asc' ? '↑' : '↓'}</span>
                      )}
                    </div>
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {loading ? (
                  <tr>
                    <td colSpan={6} className="px-6 py-12 text-center">
                      <div className="flex flex-col items-center gap-3">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-violet-600"></div>
                        <p className="text-gray-500">Loading workflows...</p>
                      </div>
                    </td>
                  </tr>
                ) : currentProcesses.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="px-6 py-12 text-center">
                      <div className="flex flex-col items-center gap-3">
                        <GitBranch className="h-12 w-12 text-gray-400" />
                        <div>
                          <p className="text-gray-900 font-medium">No workflows found</p>
                          <p className="text-gray-500 text-sm">
                            Create your first recruitment workflow to get started
                          </p>
                        </div>
                      </div>
                    </td>
                  </tr>
                ) : (
                  currentProcesses.map((process) => (
                    <tr key={process.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4">
                        <div className="flex flex-col gap-1">
                          <h3 className="text-sm font-medium text-gray-900">{process.name}</h3>
                          <p className="text-sm text-gray-600 line-clamp-2">{process.description}</p>
                          {process.is_template && (
                            <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 w-fit">
                              Template
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex flex-col gap-2">
                          <span
                            className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border w-fit ${getStatusBadge(process.status)}`}
                          >
                            {process.status}
                          </span>
                          <div className="flex items-center gap-1 flex-wrap">
                            {process.nodes.slice(0, 4).map((node) => (
                              <div
                                key={node.id}
                                className="flex items-center gap-1 px-2 py-1 bg-gray-100 rounded text-xs text-gray-600"
                                title={node.title}
                              >
                                {getNodeTypeIcon(node.node_type)}
                                <span className="truncate max-w-20">{node.title}</span>
                              </div>
                            ))}
                            {process.nodes.length > 4 && (
                              <span className="text-xs text-gray-500">+{process.nodes.length - 4} more</span>
                            )}
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-1">
                          <Users className="h-3 w-3 text-gray-400" />
                          <span className="text-sm font-medium text-gray-900">
                            {process.candidate_processes?.length || 0}
                          </span>
                          <span className="text-sm text-gray-600">candidates</span>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex flex-col gap-1">
                          <div className="flex items-center gap-2">
                            <div className="flex-1 bg-gray-200 rounded-full h-1.5">
                              <div
                                className="bg-violet-600 h-1.5 rounded-full transition-all duration-300"
                                style={{
                                  width: (process.candidate_processes?.length || 0) > 0
                                    ? `${((process.candidate_processes?.filter((cp: any) => cp.status === 'completed').length || 0) / (process.candidate_processes?.length || 0)) * 100}%`
                                    : '0%'
                                }}
                              />
                            </div>
                            <span className="text-xs text-gray-600">
                              {process.candidate_processes?.filter((cp: any) => cp.status === 'completed').length || 0}/{process.candidate_processes?.length || 0}
                            </span>
                          </div>
                          <span className="text-xs text-gray-500">
                            {(process.candidate_processes?.length || 0) > 0
                              ? `${Math.round(((process.candidate_processes?.filter((cp: any) => cp.status === 'completed').length || 0) / (process.candidate_processes?.length || 0)) * 100)}% complete`
                              : 'No candidates'
                            }
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-1">
                          <Calendar className="h-3 w-3 text-gray-400" />
                          <span className="text-sm text-gray-600">
                            {formatDate(process.created_at)}
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2">
                          <button
                            onClick={() => handleViewWorkflow(process)}
                            className="p-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                            title="View Workflow"
                          >
                            <Eye className="h-4 w-4" />
                          </button>
                          <button
                            onClick={() => handleEditWorkflow(process)}
                            className="p-2 text-gray-600 hover:text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                            title="Edit Workflow"
                          >
                            <Edit className="h-4 w-4" />
                          </button>
                          {process.status === 'draft' ? (
                            <button
                              onClick={() => handleToggleStatus(process)}
                              className="p-2 text-gray-600 hover:text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                              title="Activate Workflow"
                            >
                              <PlayCircle className="h-4 w-4" />
                            </button>
                          ) : process.status === 'active' ? (
                            <button
                              onClick={() => handleToggleStatus(process)}
                              className="p-2 text-gray-600 hover:text-yellow-600 hover:bg-yellow-50 rounded-lg transition-colors"
                              title="Pause Workflow"
                            >
                              <PauseCircle className="h-4 w-4" />
                            </button>
                          ) : (
                            <button
                              onClick={() => handleToggleStatus(process)}
                              className="p-2 text-gray-600 hover:text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                              title="Reactivate Workflow"
                            >
                              <PlayCircle className="h-4 w-4" />
                            </button>
                          )}
                          <button
                            onClick={() => handleArchiveWorkflow(process)}
                            className="p-2 text-gray-600 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                            title="Archive Workflow"
                            disabled={process.status === 'archived'}
                          >
                            <Archive className="h-4 w-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="px-6 py-3 border-t border-gray-200">
              <div className="flex items-center justify-between">
                <div className="text-sm text-gray-700">
                  Showing {startIndex + 1} to {Math.min(endIndex, filteredProcesses.length)} of{' '}
                  {filteredProcesses.length} workflows
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setCurrentPage((prev) => Math.max(prev - 1, 1))}
                    disabled={currentPage === 1}
                    className="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Previous
                  </button>
                  <span className="text-sm text-gray-600">
                    Page {currentPage} of {totalPages}
                  </span>
                  <button
                    onClick={() => setCurrentPage((prev) => Math.min(prev + 1, totalPages))}
                    disabled={currentPage === totalPages}
                    className="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Next
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>

      </div>
    </AppLayout>
  );
}

// New Workflow Modal
interface NewWorkflowModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: any) => void;
}

function NewWorkflowModal({ isOpen, onClose, onSubmit }: NewWorkflowModalProps) {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    isTemplate: false,
    useTemplate: false,
    selectedTemplate: '',
    position_id: undefined as number | undefined
  });

  useEffect(() => {
    if (isOpen) {
      setFormData({
        name: '',
        description: '',
        isTemplate: false,
        useTemplate: false,
        selectedTemplate: '',
        position_id: undefined
      });
    }
  }, [isOpen]);

  // Pre-configured workflow templates with real integration
  const workflowTemplates = {
    software_engineer: {
      name: 'Software Engineer Hiring',
      description: 'Complete technical hiring with coding tests and multiple interview stages',
      steps: [
        {
          type: 'interview' as const,
          title: 'Initial HR Screening',
          description: 'Initial screening interview with HR team',
          interview_config: {
            duration: 30,
            interview_type: 'video',
            location: 'Video Call'
          }
        },
        {
          type: 'todo' as const,
          title: 'Coding Test',
          description: 'Technical coding assessment',
          todo_config: {
            category: 'coding_test',
            priority: 'high' as const,
            is_assignment: true,
            assignment_type: 'coding'
          }
        },
        {
          type: 'interview' as const,
          title: 'Technical Interview',
          description: 'Deep technical skills interview',
          interview_config: {
            duration: 60,
            interview_type: 'video',
            location: 'Conference Room A'
          }
        },
        {
          type: 'interview' as const,
          title: 'Team Culture Interview',
          description: 'Cultural fit and team dynamics interview',
          interview_config: {
            duration: 45,
            interview_type: 'in_person',
            location: 'Team Room'
          }
        },
        {
          type: 'assessment' as const,
          title: '適性検査 (Aptitude Test)',
          description: 'Personality and aptitude assessment'
        }
      ]
    },
    marketing_specialist: {
      name: 'Marketing Specialist Process',
      description: 'Marketing role recruitment with portfolio review and case studies',
      steps: [
        {
          type: 'interview' as const,
          title: 'Initial Interview',
          description: 'General background and motivation interview',
          interview_config: {
            duration: 45,
            interview_type: 'video',
            location: 'Video Call'
          }
        },
        {
          type: 'todo' as const,
          title: 'Portfolio Review',
          description: 'Marketing portfolio and case study assignment',
          todo_config: {
            category: 'portfolio',
            priority: 'medium' as const,
            is_assignment: true,
            assignment_type: 'portfolio'
          }
        },
        {
          type: 'interview' as const,
          title: 'Final Decision Interview',
          description: 'Final interview with marketing director',
          interview_config: {
            duration: 30,
            interview_type: 'in_person',
            location: 'Director Office'
          }
        }
      ]
    }
  };

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.name.trim()) {
      alert('Please enter a workflow name');
      return;
    }

    const submitData: any = { ...formData };

    if (formData.useTemplate && formData.selectedTemplate) {
      const template = workflowTemplates[formData.selectedTemplate as keyof typeof workflowTemplates];
      submitData.templateSteps = template.steps;
      if (!formData.name.trim() || formData.name === template.name) {
        submitData.name = template.name;
        submitData.description = template.description;
      }
    }

    onSubmit(submitData);
  };

  const handleTemplateSelect = (templateKey: string) => {
    const template = workflowTemplates[templateKey as keyof typeof workflowTemplates];
    if (template) {
      setFormData(prev => ({
        ...prev,
        selectedTemplate: templateKey,
        name: template.name,
        description: template.description
      }));
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4 py-8" onClick={onClose}>
      <div
        className="w-full max-w-lg rounded-xl bg-white shadow-xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between border-b border-gray-200 px-6 py-4">
          <h2 className="text-lg font-semibold text-gray-900">Create New Workflow</h2>
          <button onClick={onClose} className="rounded-full p-1 text-gray-400 hover:text-gray-600">
            <X className="h-5 w-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4 px-6 py-5">
          {/* Template Selection */}
          <div>
            <div className="flex items-center gap-2 mb-3">
              <input
                type="checkbox"
                id="useTemplate"
                checked={formData.useTemplate}
                onChange={(e) => setFormData(prev => ({
                  ...prev,
                  useTemplate: e.target.checked,
                  selectedTemplate: e.target.checked ? prev.selectedTemplate : ''
                }))}
                className="h-4 w-4 rounded border-gray-300 text-violet-600 focus:ring-violet-500"
              />
              <label htmlFor="useTemplate" className="text-sm font-medium text-gray-700">
                ✨ Use pre-configured template (with real interviews & todos)
              </label>
            </div>

            {formData.useTemplate && (
              <div className="space-y-3 p-3 bg-violet-50 rounded-lg border">
                <p className="text-sm text-violet-700 font-medium">
                  🚀 Choose a template that creates real interviews and todo assignments:
                </p>
                <div className="space-y-2">
                  <label className="flex items-center gap-3 p-3 border border-violet-200 rounded-lg hover:bg-violet-100 cursor-pointer">
                    <input
                      type="radio"
                      name="template"
                      value="software_engineer"
                      checked={formData.selectedTemplate === 'software_engineer'}
                      onChange={(e) => handleTemplateSelect(e.target.value)}
                      className="h-4 w-4 text-violet-600 focus:ring-violet-500"
                    />
                    <div className="flex-1">
                      <div className="font-medium text-gray-900">Software Engineer</div>
                      <div className="text-sm text-gray-600">
                        HR Screening → Coding Test → Technical Interview → Culture Interview → 適性検査
                      </div>
                      <div className="text-xs text-green-600 font-medium">
                        ✅ Creates 3 real interviews + 1 coding assignment
                      </div>
                    </div>
                  </label>
                  <label className="flex items-center gap-3 p-3 border border-violet-200 rounded-lg hover:bg-violet-100 cursor-pointer">
                    <input
                      type="radio"
                      name="template"
                      value="marketing_specialist"
                      checked={formData.selectedTemplate === 'marketing_specialist'}
                      onChange={(e) => handleTemplateSelect(e.target.value)}
                      className="h-4 w-4 text-violet-600 focus:ring-violet-500"
                    />
                    <div className="flex-1">
                      <div className="font-medium text-gray-900">Marketing Specialist</div>
                      <div className="text-sm text-gray-600">
                        Initial Interview → Portfolio Review → Final Interview
                      </div>
                      <div className="text-xs text-green-600 font-medium">
                        ✅ Creates 2 real interviews + 1 portfolio assignment
                      </div>
                    </div>
                  </label>
                </div>
              </div>
            )}
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">
              Workflow Name <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
              placeholder="e.g. Software Engineer Hiring"
              className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-violet-500 focus:ring-2 focus:ring-violet-500"
            />
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">
              Description
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
              placeholder="Describe the purpose of this recruitment workflow"
              rows={3}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-violet-500 focus:ring-2 focus:ring-violet-500"
            />
          </div>

          {!formData.useTemplate && (
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="isTemplate"
                checked={formData.isTemplate}
                onChange={(e) => setFormData(prev => ({ ...prev, isTemplate: e.target.checked }))}
                className="h-4 w-4 rounded border-gray-300 text-violet-600 focus:ring-violet-500"
              />
              <label htmlFor="isTemplate" className="text-sm text-gray-700">
                Save as template for reuse
              </label>
            </div>
          )}

          <div className="flex justify-end gap-3 border-t border-gray-200 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="rounded-lg bg-violet-600 px-4 py-2 text-sm font-semibold text-white hover:bg-violet-700"
            >
              Create Workflow
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// View Workflow Modal
interface ViewWorkflowModalProps {
  isOpen: boolean;
  onClose: () => void;
  process: RecruitmentProcess | null;
  onEdit?: (process: RecruitmentProcess) => void;
}

function ViewWorkflowModal({ isOpen, onClose, process, onEdit }: ViewWorkflowModalProps) {
  if (!isOpen || !process) return null;

  const getNodeTypeIcon = (type: ProcessNode['node_type']) => {
    switch (type) {
      case 'interview': return <Video className="h-4 w-4 text-blue-600" />;
      case 'todo': return <CheckSquare className="h-4 w-4 text-green-600" />;
      case 'assessment': return <TrendingUp className="h-4 w-4 text-purple-600" />;
      case 'decision': return <GitBranch className="h-4 w-4 text-orange-600" />;
      default: return <GitBranch className="h-4 w-4 text-gray-600" />;
    }
  };

  const getNodeTypeBadge = (type: ProcessNode['node_type']) => {
    const styles = {
      interview: 'bg-blue-50 text-blue-700 border-blue-200',
      todo: 'bg-green-50 text-green-700 border-green-200',
      assessment: 'bg-purple-50 text-purple-700 border-purple-200',
      decision: 'bg-orange-50 text-orange-700 border-orange-200',
    };
    return styles[type] || 'bg-gray-50 text-gray-700 border-gray-200';
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4 py-8" onClick={onClose}>
      <div
        className="w-full max-w-2xl rounded-xl bg-white shadow-xl max-h-[80vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between border-b border-gray-200 px-6 py-4">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">{process.name}</h2>
            <p className="text-sm text-gray-600">{process.description}</p>
          </div>
          <button onClick={onClose} className="rounded-full p-1 text-gray-400 hover:text-gray-600">
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="px-6 py-5 space-y-6">
          {/* Status and Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-900">{process.candidate_processes?.length || 0}</div>
              <div className="text-sm text-gray-600">Candidates</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{process.candidate_processes?.filter((cp: any) => cp.status === 'completed').length || 0}</div>
              <div className="text-sm text-gray-600">Completed</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-violet-600">{process.nodes.length}</div>
              <div className="text-sm text-gray-600">Steps</div>
            </div>
            <div className="text-center">
              <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium border ${
                process.status === 'active' ? 'bg-green-100 text-green-800 border-green-200' :
                process.status === 'draft' ? 'bg-gray-100 text-gray-800 border-gray-200' :
                process.status === 'inactive' ? 'bg-yellow-100 text-yellow-800 border-yellow-200' :
                'bg-red-100 text-red-800 border-red-200'
              }`}>
                {process.status}
              </div>
            </div>
          </div>

          {/* Workflow Steps */}
          <div>
            <h3 className="text-lg font-medium text-gray-900 mb-4">Workflow Steps</h3>
            {process.nodes.length > 0 ? (
              <div className="space-y-3">
                {process.nodes.map((node, index) => (
                  <div key={node.id} className="flex items-center gap-4 p-3 border border-gray-200 rounded-lg">
                    <div className="flex items-center justify-center w-8 h-8 bg-violet-100 text-violet-600 rounded-full text-sm font-medium">
                      {index + 1}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        {getNodeTypeIcon(node.node_type)}
                        <span className="font-medium text-gray-900">{node.title}</span>
                        <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium border ${getNodeTypeBadge(node.node_type)}`}>
                          {node.node_type}
                        </span>
                      </div>
                      <p className="text-sm text-gray-600">{node.description}</p>
                    </div>
                    {index < process.nodes.length - 1 && (
                      <div className="text-gray-400">
                        →
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <GitBranch className="h-12 w-12 mx-auto mb-3 text-gray-400" />
                <p>No workflow steps defined yet</p>
                <p className="text-sm">Add steps to create your recruitment process</p>
              </div>
            )}
          </div>

          {/* Actions */}
          <div className="flex justify-end gap-3 border-t border-gray-200 pt-4">
            <button
              onClick={onClose}
              className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              Close
            </button>
            <button
              onClick={() => {
                onClose();
                onEdit?.(process);
              }}
              className="rounded-lg bg-violet-600 px-4 py-2 text-sm font-semibold text-white hover:bg-violet-700"
            >
              Edit Workflow
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

// Linear Workflow Editor Modal
interface WorkflowEditorModalProps {
  isOpen: boolean;
  onClose: () => void;
  process: RecruitmentProcess | null;
  onSave: (process: RecruitmentProcess) => void;
}

interface LinearWorkflowStep {
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

interface WorkflowCandidate {
  id: number;
  name: string;
  email: string;
}

interface WorkflowViewer {
  id: number;
  name: string;
  email: string;
  role: 'viewer' | 'reviewer' | 'manager';
}

function WorkflowEditorModal({ isOpen, onClose, process, onSave }: WorkflowEditorModalProps) {
  const [steps, setSteps] = useState<LinearWorkflowStep[]>([]);
  const [selectedStep, setSelectedStep] = useState<LinearWorkflowStep | null>(null);
  const [showStepPanel, setShowStepPanel] = useState(false);
  const [processTitle, setProcessTitle] = useState('');
  const [processDescription, setProcessDescription] = useState('');
  const [isCreatingIntegratedRecords, setIsCreatingIntegratedRecords] = useState(true);

  // Candidate and viewer management
  const [assignedCandidates, setAssignedCandidates] = useState<WorkflowCandidate[]>([]);
  const [workflowViewers, setWorkflowViewers] = useState<WorkflowViewer[]>([]);
  const [candidateInput, setCandidateInput] = useState('');
  const [viewerInput, setViewerInput] = useState('');
  const [viewerRole, setViewerRole] = useState<'viewer' | 'reviewer' | 'manager'>('viewer');

  // Modal states for interview and todo editing
  const [isInterviewModalOpen, setIsInterviewModalOpen] = useState(false);
  const [isTodoModalOpen, setIsTodoModalOpen] = useState(false);
  const [editingInterview, setEditingInterview] = useState<Interview | null>(null);
  const [editingTodo, setEditingTodo] = useState<Todo | null>(null);

  // Drag and drop state
  const [draggedStep, setDraggedStep] = useState<LinearWorkflowStep | null>(null);
  const [dragOverIndex, setDragOverIndex] = useState<number | null>(null);

  // Initialize steps when process changes
  useEffect(() => {
    if (process && isOpen) {
      setProcessTitle(process.name);
      setProcessDescription(process.description || '');

      // Convert existing nodes to linear steps
      if (process.nodes && process.nodes.length > 0) {
        const linearSteps: LinearWorkflowStep[] = process.nodes
          .filter(node => node.node_type === 'interview' || node.node_type === 'todo')
          .sort((a, b) => a.sequence_order - b.sequence_order)
          .map((node, index) => ({
            id: `step-${node.id}`,
            type: node.node_type as 'interview' | 'todo',
            title: node.title,
            description: node.description,
            config: node.config || {},
            order: index + 1,
            realId: node.id,
            isIntegrated: !!(node.interview_id || node.todo_id),
            interview_id: node.interview_id,
            todo_id: node.todo_id
          }));
        setSteps(linearSteps);
      } else {
        // Start with empty workflow
        setSteps([]);
      }
    }
  }, [process, isOpen]);

  // Add new step to the workflow
  const addStep = (type: 'interview' | 'todo') => {
    const newStep: LinearWorkflowStep = {
      id: `step-${Date.now()}`,
      type,
      title: type === 'interview' ? 'New Interview' : 'New Todo',
      description: type === 'interview' ? 'Interview step description' : 'Todo assignment',
      config: type === 'interview' ? {
        duration: 60,
        interview_type: 'video',
        location: 'Video Call'
      } : {
        priority: 'medium',
        assignment_type: 'general',
        is_assignment: true
      },
      order: steps.length + 1,
      isIntegrated: isCreatingIntegratedRecords
    };
    setSteps(prev => [...prev, newStep]);
    setSelectedStep(newStep);
    setShowStepPanel(true);
  };

  // Update step properties
  const updateStep = (stepId: string, updates: Partial<LinearWorkflowStep>) => {
    setSteps(prev => prev.map(step =>
      step.id === stepId ? { ...step, ...updates } : step
    ));
    if (selectedStep?.id === stepId) {
      setSelectedStep(prev => prev ? { ...prev, ...updates } : null);
    }
  };

  // Delete step from workflow
  const deleteStep = (stepId: string) => {
    setSteps(prev => {
      const filtered = prev.filter(step => step.id !== stepId);
      // Reorder remaining steps
      return filtered.map((step, index) => ({ ...step, order: index + 1 }));
    });
    if (selectedStep?.id === stepId) {
      setSelectedStep(null);
      setShowStepPanel(false);
    }
  };

  // Move step up/down in the sequence
  const moveStep = (stepId: string, direction: 'up' | 'down') => {
    setSteps(prev => {
      const currentIndex = prev.findIndex(step => step.id === stepId);
      if (currentIndex === -1) return prev;

      const newIndex = direction === 'up' ? currentIndex - 1 : currentIndex + 1;
      if (newIndex < 0 || newIndex >= prev.length) return prev;

      const newSteps = [...prev];
      [newSteps[currentIndex], newSteps[newIndex]] = [newSteps[newIndex], newSteps[currentIndex]];

      // Update order numbers
      return newSteps.map((step, index) => ({ ...step, order: index + 1 }));
    });
  };

  // Handle editing the actual interview/todo record
  const handleEditStepRecord = async (step: LinearWorkflowStep) => {
    if (step.type === 'interview' && step.interview_id) {
      try {
        const response = await interviewsApi.getById(step.interview_id);
        if (response.success && response.data) {
          setEditingInterview(response.data);
          setIsInterviewModalOpen(true);
        }
      } catch (error) {
        console.error('Failed to load interview:', error);
        alert('Failed to load interview for editing');
      }
    } else if (step.type === 'todo' && step.todo_id) {
      try {
        const todo = await todosApi.getTodoWithAssignedUser(step.todo_id);
        setEditingTodo(todo);
        setIsTodoModalOpen(true);
      } catch (error) {
        console.error('Failed to load todo:', error);
        alert('Failed to load todo for editing');
      }
    } else {
      alert(`No linked ${step.type} found for this step. The integration may not have been completed.`);
    }
  };

  // Add candidate to workflow
  const handleAddCandidate = async () => {
    if (!candidateInput.trim()) return;

    try {
      // For demo purposes, we'll simulate finding a candidate
      // In real implementation, this would search users by email/ID
      const candidateId = parseInt(candidateInput) || Math.floor(Math.random() * 1000);
      const newCandidate: WorkflowCandidate = {
        id: candidateId,
        name: candidateInput.includes('@') ? candidateInput.split('@')[0] : `User ${candidateId}`,
        email: candidateInput.includes('@') ? candidateInput : `user${candidateId}@example.com`
      };

      setAssignedCandidates(prev => [...prev, newCandidate]);
      setCandidateInput('');

      // If process is already created, assign candidate via API
      if (process?.id) {
        await recruitmentWorkflowsApi.assignCandidates(process.id, [candidateId]);
      }
    } catch (error) {
      console.error('Failed to add candidate:', error);
      alert('Failed to add candidate');
    }
  };

  // Add viewer to workflow
  const handleAddViewer = async () => {
    if (!viewerInput.trim()) return;

    try {
      // For demo purposes, we'll simulate finding a user
      // In real implementation, this would search users by email/ID
      const viewerId = parseInt(viewerInput) || Math.floor(Math.random() * 1000);
      const newViewer: WorkflowViewer = {
        id: viewerId,
        name: viewerInput.includes('@') ? viewerInput.split('@')[0] : `User ${viewerId}`,
        email: viewerInput.includes('@') ? viewerInput : `user${viewerId}@example.com`,
        role: viewerRole
      };

      setWorkflowViewers(prev => [...prev, newViewer]);
      setViewerInput('');

      // Note: API call for adding viewers would go here
      // await recruitmentWorkflowsApi.addViewer(process.id, viewerId, viewerRole);
    } catch (error) {
      console.error('Failed to add viewer:', error);
      alert('Failed to add viewer');
    }
  };

  // Remove candidate from workflow
  const handleRemoveCandidate = (candidateId: number) => {
    setAssignedCandidates(prev => prev.filter(c => c.id !== candidateId));
  };

  // Remove viewer from workflow
  const handleRemoveViewer = (viewerId: number) => {
    setWorkflowViewers(prev => prev.filter(v => v.id !== viewerId));
  };

  // Drag and drop handlers
  const handleDragStart = (step: LinearWorkflowStep) => {
    setDraggedStep(step);
  };

  const handleDragOver = (e: React.DragEvent, index: number) => {
    e.preventDefault();
    setDragOverIndex(index);
  };

  const handleDragEnd = () => {
    setDraggedStep(null);
    setDragOverIndex(null);
  };

  const handleDrop = (e: React.DragEvent, targetIndex: number) => {
    e.preventDefault();

    if (!draggedStep) return;

    const currentIndex = steps.findIndex(s => s.id === draggedStep.id);
    if (currentIndex === -1 || currentIndex === targetIndex) {
      handleDragEnd();
      return;
    }

    // Reorder steps
    setSteps(prev => {
      const newSteps = [...prev];
      const [removed] = newSteps.splice(currentIndex, 1);
      newSteps.splice(targetIndex, 0, removed);
      // Update order numbers
      return newSteps.map((step, index) => ({ ...step, order: index + 1 }));
    });

    handleDragEnd();
  };

  const getStepIcon = (type: 'interview' | 'todo') => {
    switch (type) {
      case 'interview': return <Video className="h-5 w-5" />;
      case 'todo': return <CheckSquare className="h-5 w-5" />;
      default: return <Circle className="h-5 w-5" />;
    }
  };

  const getStepColor = (type: 'interview' | 'todo') => {
    switch (type) {
      case 'interview': return 'bg-blue-500 text-white border-blue-600';
      case 'todo': return 'bg-green-500 text-white border-green-600';
      default: return 'bg-gray-400 text-white border-gray-500';
    }
  };

  const handleSave = async () => {
    if (!process) return;

    try {
      // First, delete any existing nodes that are not in our current steps
      const existingNodeIds = process.nodes?.map(n => n.id) || [];
      const currentStepNodeIds = steps.filter(s => s.realId).map(s => s.realId!);
      const nodesToDelete = existingNodeIds.filter(id => !currentStepNodeIds.includes(id));

      for (const nodeId of nodesToDelete) {
        try {
          await recruitmentWorkflowsApi.deleteNode(process.id, nodeId);
        } catch (error) {
          console.warn(`Failed to delete node ${nodeId}:`, error);
        }
      }

      // Create or update steps
      const createdInterviews: any[] = [];
      const createdTodos: any[] = [];

      for (const step of steps) {
        const nodeData: CreateNodeData = {
          node_type: step.type,
          title: step.title,
          description: step.description,
          sequence_order: step.order,
          position: {
            x: 100 + (step.order * 200), // Linear horizontal layout
            y: 200
          },
          config: step.config
        };

        // Add integration data if creating real records
        if (step.isIntegrated && !step.realId) {
          if (step.type === 'interview') {
            nodeData.create_interview = {
              duration: step.config?.duration || 60,
              interview_type: step.config?.interview_type || 'video',
              location: step.config?.location || 'Video Call',
              notes: `Auto-generated for workflow: ${processTitle}`,
              // Use first candidate if available
              candidate_id: assignedCandidates.length > 0 ? assignedCandidates[0].id : undefined
            };
          }

          if (step.type === 'todo') {
            nodeData.create_todo = {
              title: step.title,
              description: step.description || 'Todo assignment',
              priority: step.config?.priority || 'medium',
              is_assignment: step.config?.is_assignment !== false,
              assignment_type: step.config?.assignment_type || 'general',
              // Use first candidate if available
              assigned_to: assignedCandidates.length > 0 ? assignedCandidates[0].id : undefined
            };
          }
        }

        if (step.realId) {
          // Update existing node
          await recruitmentWorkflowsApi.updateNode(process.id, step.realId, nodeData);
        } else {
          // Create new node with integration
          try {
            if (step.isIntegrated && (nodeData.create_interview || nodeData.create_todo)) {
              console.log('Creating node with integration:', { step: step.title, nodeData });
              const nodeResponse = await recruitmentWorkflowsApi.createNodeWithIntegration(process.id, nodeData);
              console.log('Node integration response:', nodeResponse);

              if (nodeResponse.success && nodeResponse.data) {
                // Update step with the actual linked IDs
                if (nodeResponse.data.interview) {
                  console.log('Interview created:', nodeResponse.data.interview);
                  createdInterviews.push(nodeResponse.data.interview);
                  step.interview_id = nodeResponse.data.interview.id;
                }
                if (nodeResponse.data.todo) {
                  console.log('Todo created:', nodeResponse.data.todo);
                  createdTodos.push(nodeResponse.data.todo);
                  step.todo_id = nodeResponse.data.todo.id;
                }
                // Update the step with the real node ID
                step.realId = nodeResponse.data.node.id;
              }
            } else {
              const nodeResponse = await recruitmentWorkflowsApi.createNode(process.id, nodeData);
              if (nodeResponse.success && nodeResponse.data) {
                step.realId = nodeResponse.data.id;
              }
            }
          } catch (error) {
            console.warn(`Failed to create integrated node for step ${step.title}:`, error);
            // Fallback to regular node creation
            await recruitmentWorkflowsApi.createNode(process.id, nodeData);
          }
        }
      }

      // Update process basic info if changed
      if (processTitle !== process.name || processDescription !== process.description) {
        await recruitmentWorkflowsApi.updateProcess(process.id, {
          name: processTitle,
          description: processDescription
        });
      }

      // Reload the process from the API to get the actual node IDs
      const reloadedProcessResponse = await recruitmentWorkflowsApi.getProcess(process.id);

      const updatedProcess: RecruitmentProcess = reloadedProcessResponse.data || {
        ...process,
        name: processTitle,
        description: processDescription,
        nodes: []
      };

      onSave(updatedProcess);

      console.log('Workflow saved!', { createdInterviews, createdTodos, reloadedNodes: updatedProcess.nodes.length });

      let successMessage = '✅ Workflow saved successfully!';

      // Show integration results
      if (createdInterviews.length > 0 || createdTodos.length > 0) {
        successMessage += `\n\n📊 Integration Results:`;
        if (createdInterviews.length > 0) {
          successMessage += `\n🎙️ Created ${createdInterviews.length} interview(s)`;
          createdInterviews.forEach((interview, i) => {
            successMessage += `\n   Interview ${i + 1}: ID ${interview.id}`;
          });
        }
        if (createdTodos.length > 0) {
          successMessage += `\n📋 Created ${createdTodos.length} todo(s)`;
          createdTodos.forEach((todo, i) => {
            successMessage += `\n   Todo ${i + 1}: ID ${todo.id}`;
          });
        }

        // Show assignment information
        if (assignedCandidates.length > 0) {
          successMessage += `\n\n👥 Assignments:`;
          successMessage += `\n• ${assignedCandidates.length} candidate${assignedCandidates.length !== 1 ? 's' : ''} assigned`;
        }
        if (workflowViewers.length > 0) {
          successMessage += `\n• ${workflowViewers.length} viewer${workflowViewers.length !== 1 ? 's' : ''} added`;
        }

        successMessage += `\n\n💡 Check /interviews and /todos pages to see them!`;
      }

      alert(successMessage);
    } catch (error) {
      console.error('Failed to save workflow:', error);
      alert('❌ Failed to save workflow: ' + (error instanceof Error ? error.message : 'Unknown error'));
    }
  };

  if (!isOpen || !process) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-black bg-opacity-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-6xl h-[90vh] flex flex-col">
        {/* Header */}
        <div className="border-b border-gray-200 p-6 flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
              <GitBranch className="h-5 w-5 text-violet-600" />
              Linear Workflow Editor
            </h2>
            <p className="text-sm text-gray-500 mt-1">Create a step-by-step recruitment process with interviews and coding tests</p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={onClose}
              className="p-2 text-gray-400 hover:text-gray-600"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1 flex overflow-hidden">
          {/* Left Sidebar - Step Controls */}
          <div className="w-80 border-r border-gray-200 p-6 bg-gray-50 overflow-y-auto">
            <h3 className="font-semibold text-gray-900 mb-4">Workflow Configuration</h3>

            {/* Process Info */}
            <div className="mb-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Process Name</label>
                <input
                  type="text"
                  value={processTitle}
                  onChange={(e) => setProcessTitle(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-violet-500 focus:border-violet-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
                <textarea
                  value={processDescription}
                  onChange={(e) => setProcessDescription(e.target.value)}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-violet-500 focus:border-violet-500"
                />
              </div>
            </div>

            {/* Add Step Buttons */}
            <div className="mb-6">
              <h4 className="font-medium text-gray-900 mb-3">Add Workflow Steps</h4>
              <div className="space-y-3">
                <button
                  onClick={() => addStep('interview')}
                  className="w-full flex items-center gap-3 p-4 text-left text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-blue-50 hover:border-blue-300 transition-colors"
                >
                  <Video className="h-5 w-5 text-blue-500" />
                  <div>
                    <div className="font-medium text-gray-900">Interview</div>
                    <div className="text-xs text-gray-500">Technical, HR, or cultural interview</div>
                  </div>
                </button>
                <button
                  onClick={() => addStep('todo')}
                  className="w-full flex items-center gap-3 p-4 text-left text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-green-50 hover:border-green-300 transition-colors"
                >
                  <CheckSquare className="h-5 w-5 text-green-500" />
                  <div>
                    <div className="font-medium text-gray-900">Todo</div>
                    <div className="text-xs text-gray-500">Assignment or task</div>
                  </div>
                </button>
              </div>
            </div>

            {/* Candidate Assignment */}
            <div className="mb-6">
              <h4 className="font-medium text-gray-900 mb-3">Candidate & Viewer Assignment</h4>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Assign Candidates</label>
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={candidateInput}
                      onChange={(e) => setCandidateInput(e.target.value)}
                      placeholder="Enter candidate ID or email"
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-violet-500 focus:border-violet-500"
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') {
                          handleAddCandidate();
                        }
                      }}
                    />
                    <button
                      type="button"
                      onClick={handleAddCandidate}
                      className="px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm"
                    >
                      Add
                    </button>
                  </div>

                  {/* Assigned Candidates List */}
                  {assignedCandidates.length > 0 && (
                    <div className="mt-2 space-y-1">
                      {assignedCandidates.map(candidate => (
                        <div key={candidate.id} className="flex items-center justify-between p-2 bg-blue-50 border border-blue-200 rounded text-sm">
                          <div>
                            <span className="font-medium text-blue-900">{candidate.name}</span>
                            <span className="text-blue-600 ml-2">({candidate.email})</span>
                          </div>
                          <button
                            onClick={() => handleRemoveCandidate(candidate.id)}
                            className="text-red-500 hover:text-red-700"
                            title="Remove candidate"
                          >
                            ×
                          </button>
                        </div>
                      ))}
                    </div>
                  )}

                  <p className="text-xs text-gray-500 mt-1">
                    Candidates will be automatically assigned to all interviews and todos in this workflow
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Add Viewers</label>
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={viewerInput}
                      onChange={(e) => setViewerInput(e.target.value)}
                      placeholder="Enter user ID or email"
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-violet-500 focus:border-violet-500"
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') {
                          handleAddViewer();
                        }
                      }}
                    />
                    <select
                      value={viewerRole}
                      onChange={(e) => setViewerRole(e.target.value as 'viewer' | 'reviewer' | 'manager')}
                      className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-violet-500 focus:border-violet-500"
                    >
                      <option value="viewer">Viewer</option>
                      <option value="reviewer">Reviewer</option>
                      <option value="manager">Manager</option>
                    </select>
                    <button
                      type="button"
                      onClick={handleAddViewer}
                      className="px-3 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm"
                    >
                      Add
                    </button>
                  </div>

                  {/* Workflow Viewers List */}
                  {workflowViewers.length > 0 && (
                    <div className="mt-2 space-y-1">
                      {workflowViewers.map(viewer => (
                        <div key={viewer.id} className="flex items-center justify-between p-2 bg-green-50 border border-green-200 rounded text-sm">
                          <div>
                            <span className="font-medium text-green-900">{viewer.name}</span>
                            <span className="text-green-600 ml-2">({viewer.email})</span>
                            <span className={`ml-2 px-2 py-1 rounded-full text-xs font-medium ${
                              viewer.role === 'manager' ? 'bg-purple-100 text-purple-800' :
                              viewer.role === 'reviewer' ? 'bg-orange-100 text-orange-800' :
                              'bg-gray-100 text-gray-800'
                            }`}>
                              {viewer.role}
                            </span>
                          </div>
                          <button
                            onClick={() => handleRemoveViewer(viewer.id)}
                            className="text-red-500 hover:text-red-700"
                            title="Remove viewer"
                          >
                            ×
                          </button>
                        </div>
                      ))}
                    </div>
                  )}

                  <p className="text-xs text-gray-500 mt-1">
                    Viewers will have access to all interviews and todos created by this workflow
                  </p>
                </div>
              </div>
            </div>

            {/* Integration Info */}
            <div className="p-4 bg-violet-50 border border-violet-200 rounded-lg">
              <div className="flex items-start gap-2">
                <GitBranch className="h-4 w-4 text-violet-600 mt-0.5" />
                <div className="text-xs text-violet-800">
                  <div className="font-medium mb-1">Smart Integration</div>
                  <p>
                    When enabled, interview steps create actual interview records and todo steps create real todo assignments.
                    Assigned candidates and viewers are automatically propagated to all created records.
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Center - Linear Workflow View */}
          <div className="flex-1 p-6 bg-white overflow-y-auto">
            <div className="max-w-4xl mx-auto">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-semibold text-gray-900">Workflow Steps</h3>
              </div>

              {steps.length === 0 ? (
                /* Empty State */
                <div className="text-center py-12">
                  <GitBranch className="h-16 w-16 mx-auto text-gray-400 mb-4" />
                  <h4 className="text-xl font-semibold text-gray-900 mb-2">No Steps Yet</h4>
                  <p className="text-gray-600 mb-6 max-w-md mx-auto">
                    Start building your recruitment workflow by adding interview and todo steps.
                    Use the buttons on the left to get started.
                  </p>
                  <div className="flex justify-center gap-3">
                    <button
                      onClick={() => addStep('interview')}
                      className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                    >
                      <Video className="h-4 w-4" />
                      Interview
                    </button>
                    <button
                      onClick={() => addStep('todo')}
                      className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                    >
                      <CheckSquare className="h-4 w-4" />
                      Todo
                    </button>
                  </div>
                </div>
              ) : (
                /* Linear Workflow Steps */
                <div className="space-y-4">
                  {steps.map((step, index) => {
                    console.log(`Step ${index}:`, { id: step.id, interview_id: step.interview_id, todo_id: step.todo_id, isIntegrated: step.isIntegrated, realId: step.realId });
                    return (
                    <div key={step.id} className="relative">
                      <div
                        draggable
                        onDragStart={() => handleDragStart(step)}
                        onDragOver={(e) => handleDragOver(e, index)}
                        onDragEnd={handleDragEnd}
                        onDrop={(e) => handleDrop(e, index)}
                        className={`relative border-2 rounded-xl p-5 cursor-move transition-all shadow-sm hover:shadow-md ${
                          draggedStep?.id === step.id
                            ? 'opacity-50 border-violet-500 bg-violet-100'
                            : selectedStep?.id === step.id
                            ? 'border-violet-500 bg-gradient-to-br from-violet-50 to-purple-50 shadow-lg ring-2 ring-violet-200'
                            : dragOverIndex === index && draggedStep?.id !== step.id
                            ? 'border-blue-500 bg-blue-50 ring-2 ring-blue-300'
                            : 'border-gray-200 bg-white hover:border-gray-300'
                        }`}
                        onClick={() => {
                          setSelectedStep(step);
                          setShowStepPanel(true);
                        }}
                      >
                        {/* Drop indicator line at top */}
                        {dragOverIndex === index && draggedStep?.id !== step.id && (
                          <div className="absolute -top-1 left-0 right-0 h-1 bg-blue-500 rounded-full shadow-lg animate-pulse" />
                        )}

                        <div className="flex items-center gap-4">
                          {/* Step Number */}
                          <div className="flex-shrink-0 w-11 h-11 bg-gradient-to-br from-violet-500 to-purple-600 text-white rounded-full flex items-center justify-center font-bold text-lg shadow-md">
                            {step.order}
                          </div>

                          {/* Step Icon and Type */}
                          <div className={`flex-shrink-0 w-14 h-14 rounded-xl border-2 ${getStepColor(step.type)} flex items-center justify-center shadow-sm`}>
                            {getStepIcon(step.type)}
                          </div>

                          {/* Step Content */}
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2 mb-1">
                              <h4 className="font-semibold text-gray-900 truncate">{step.title}</h4>
                              <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                                step.type === 'interview'
                                  ? 'bg-blue-100 text-blue-800'
                                  : 'bg-green-100 text-green-800'
                              }`}>
                                {step.type}
                              </span>
                              {step.isIntegrated && (
                                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-violet-100 text-violet-800">
                                  {(step.interview_id || step.todo_id) ? '🔗 Linked' : '✨ Integration Enabled'}
                                </span>
                              )}
                            </div>
                            <p className="text-sm text-gray-600 truncate">{step.description}</p>
                            <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
                              {step.type === 'interview' && (
                                <>
                                  <span>📅 {step.config?.duration || 60} minutes</span>
                                  <span>🎥 {step.config?.interview_type || 'video'}</span>
                                  <span>📍 {step.config?.location || 'Video Call'}</span>
                                </>
                              )}
                              {step.type === 'todo' && (
                                <>
                                  <span>📋 {step.config?.assignment_type || 'general'} assignment</span>
                                  <span>⭐ {step.config?.priority || 'medium'} priority</span>
                                </>
                              )}
                            </div>
                          </div>

                          {/* Step Controls */}
                          <div className="flex-shrink-0 flex items-center gap-2">
                            {/* Edit button - opens actual interview/todo for editing */}
                            {(step.interview_id || step.todo_id) && (
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleEditStepRecord(step);
                                }}
                                className="px-3 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg shadow-sm transition-colors flex items-center gap-1"
                                title={`Edit ${step.type === 'interview' ? 'interview' : 'todo'} record`}
                              >
                                <Edit className="h-4 w-4" />
                                Edit
                              </button>
                            )}
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                moveStep(step.id, 'up');
                              }}
                              disabled={index === 0}
                              className="p-1 text-gray-400 hover:text-gray-600 disabled:opacity-30 disabled:cursor-not-allowed"
                              title="Move up"
                            >
                              ↑
                            </button>
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                moveStep(step.id, 'down');
                              }}
                              disabled={index === steps.length - 1}
                              className="p-1 text-gray-400 hover:text-gray-600 disabled:opacity-30 disabled:cursor-not-allowed"
                              title="Move down"
                            >
                              ↓
                            </button>
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                deleteStep(step.id);
                              }}
                              className="p-1 text-red-400 hover:text-red-600"
                              title="Delete step"
                            >
                              <Trash2 className="h-4 w-4" />
                            </button>
                          </div>
                        </div>
                      </div>

                      {/* Connection Arrow */}
                      {index < steps.length - 1 && (
                        <div className="flex justify-center py-2">
                          <div className={`text-2xl font-bold ${
                            draggedStep && (dragOverIndex === index || dragOverIndex === index + 1)
                              ? 'text-blue-500 animate-pulse'
                              : 'text-gray-400'
                          }`}>
                            ↓
                          </div>
                        </div>
                      )}
                    </div>
                  );
                  })}
                </div>
              )}
            </div>
          </div>

          {/* Right Sidebar - Step Properties */}
          {showStepPanel && selectedStep && (
            <div className="w-80 border-l border-gray-200 p-6 bg-gray-50">
              <h3 className="font-semibold text-gray-900 mb-4">Step Properties</h3>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Title</label>
                  <input
                    type="text"
                    value={selectedStep.title}
                    onChange={(e) => updateStep(selectedStep.id, { title: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-violet-500 focus:border-violet-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
                  <textarea
                    value={selectedStep.description || ''}
                    onChange={(e) => updateStep(selectedStep.id, { description: e.target.value })}
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-violet-500 focus:border-violet-500"
                  />
                </div>

                <div>
                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={selectedStep.isIntegrated}
                      onChange={(e) => updateStep(selectedStep.id, { isIntegrated: e.target.checked })}
                      className="h-4 w-4 rounded border-gray-300 text-violet-600 focus:ring-violet-500"
                    />
                    <span className="text-sm font-medium text-gray-700">
                      Create real {selectedStep.type === 'interview' ? 'interview' : 'todo'} record
                    </span>
                  </label>
                  <p className="text-xs text-gray-500 mt-1">
                    When enabled, this step will create an actual {selectedStep.type === 'interview' ? 'interview' : 'todo assignment'} that you can view in the {selectedStep.type === 'interview' ? 'Interviews' : 'Todos'} section.
                  </p>
                </div>

                {/* Interview-specific settings */}
                {selectedStep.type === 'interview' && (
                  <div className="space-y-4 pt-4 border-t border-gray-200">
                    <h4 className="font-medium text-gray-900">Interview Settings</h4>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Duration (minutes)</label>
                      <input
                        type="number"
                        min="15"
                        max="480"
                        value={selectedStep.config?.duration || 60}
                        onChange={(e) => updateStep(selectedStep.id, {
                          config: { ...selectedStep.config, duration: parseInt(e.target.value) }
                        })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-violet-500 focus:border-violet-500"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Interview Type</label>
                      <select
                        value={selectedStep.config?.interview_type || 'video'}
                        onChange={(e) => updateStep(selectedStep.id, {
                          config: { ...selectedStep.config, interview_type: e.target.value }
                        })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-violet-500 focus:border-violet-500"
                      >
                        <option value="video">Video Interview</option>
                        <option value="phone">Phone Interview</option>
                        <option value="in_person">In-Person Interview</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Location</label>
                      <input
                        type="text"
                        value={selectedStep.config?.location || 'Video Call'}
                        onChange={(e) => updateStep(selectedStep.id, {
                          config: { ...selectedStep.config, location: e.target.value }
                        })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-violet-500 focus:border-violet-500"
                        placeholder="e.g., Video Call, Conference Room A"
                      />
                    </div>
                  </div>
                )}

                {/* Todo-specific settings */}
                {selectedStep.type === 'todo' && (
                  <div className="space-y-4 pt-4 border-t border-gray-200">
                    <h4 className="font-medium text-gray-900">Assignment Settings</h4>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Priority</label>
                      <select
                        value={selectedStep.config?.priority || 'medium'}
                        onChange={(e) => updateStep(selectedStep.id, {
                          config: { ...selectedStep.config, priority: e.target.value }
                        })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-violet-500 focus:border-violet-500"
                      >
                        <option value="low">Low</option>
                        <option value="medium">Medium</option>
                        <option value="high">High</option>
                        <option value="urgent">Urgent</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Assignment Type</label>
                      <select
                        value={selectedStep.config?.assignment_type || 'general'}
                        onChange={(e) => updateStep(selectedStep.id, {
                          config: { ...selectedStep.config, assignment_type: e.target.value }
                        })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-violet-500 focus:border-violet-500"
                      >
                        <option value="general">General Assignment</option>
                        <option value="coding">Coding Challenge</option>
                        <option value="research">Research Task</option>
                        <option value="presentation">Presentation</option>
                        <option value="analysis">Analysis Task</option>
                        <option value="design">Design Task</option>
                        <option value="writing">Writing Assignment</option>
                        <option value="review">Review Task</option>
                      </select>
                    </div>

                    <div>
                      <label className="flex items-center gap-2">
                        <input
                          type="checkbox"
                          checked={selectedStep.config?.is_assignment !== false}
                          onChange={(e) => updateStep(selectedStep.id, {
                            config: { ...selectedStep.config, is_assignment: e.target.checked }
                          })}
                          className="h-4 w-4 rounded border-gray-300 text-violet-600 focus:ring-violet-500"
                        />
                        <span className="text-sm font-medium text-gray-700">Is Assignment</span>
                      </label>
                      <p className="text-xs text-gray-500 mt-1">
                        Assignments are special todos that require completion and scoring.
                      </p>
                    </div>
                  </div>
                )}

                <div className="pt-4 border-t border-gray-200">
                  <div className="text-xs text-gray-500">
                    <div>Step #{selectedStep.order}</div>
                    <div>Type: {selectedStep.type}</div>
                    {selectedStep.realId && <div>Node ID: {selectedStep.realId}</div>}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="border-t border-gray-200 p-6 flex justify-between items-center">
          <div className="text-sm text-gray-600">
            {(steps.length > 0 || assignedCandidates.length > 0 || workflowViewers.length > 0) && (
              <div className="mt-1 text-xs text-gray-500 space-y-1">
                {steps.length > 0 && (
                  <div>{steps.filter(s => s.type === 'interview').length} interviews • {steps.filter(s => s.type === 'todo').length} todos</div>
                )}
                {assignedCandidates.length > 0 && (
                  <div className="flex items-center gap-1">
                    <Users className="h-3 w-3" />
                    {assignedCandidates.length} candidate{assignedCandidates.length !== 1 ? 's' : ''} assigned
                  </div>
                )}
                {workflowViewers.length > 0 && (
                  <div className="flex items-center gap-1">
                    <Eye className="h-3 w-3" />
                    {workflowViewers.length} viewer{workflowViewers.length !== 1 ? 's' : ''} added
                  </div>
                )}
              </div>
            )}
          </div>
          <div className="flex gap-3">
            <button
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              disabled={steps.length === 0}
              className="px-4 py-2 text-sm font-semibold text-white bg-violet-600 rounded-lg hover:bg-violet-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Save Linear Workflow
            </button>
          </div>
        </div>
      </div>

      {/* Modals for editing */}
      {isTodoModalOpen && (
        <TaskModal
          isOpen={isTodoModalOpen}
          onClose={() => {
            setIsTodoModalOpen(false);
            setEditingTodo(null);
          }}
          onSuccess={() => {
            setIsTodoModalOpen(false);
            setEditingTodo(null);
            alert('Todo updated successfully!');
          }}
          editingTodo={editingTodo}
        />
      )}

      {isInterviewModalOpen && editingInterview && (
        <div className="fixed inset-0 z-[60] overflow-y-auto bg-black bg-opacity-50 flex items-center justify-center p-4"
             onClick={() => {
               setIsInterviewModalOpen(false);
               setEditingInterview(null);
             }}>
          <div className="bg-white rounded-xl shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto"
               onClick={(e) => e.stopPropagation()}>
            <div className="border-b border-gray-200 p-6 flex items-center justify-between">
              <h2 className="text-xl font-bold text-gray-900">Edit Interview</h2>
              <button
                onClick={() => {
                  setIsInterviewModalOpen(false);
                  setEditingInterview(null);
                }}
                className="p-2 text-gray-400 hover:text-gray-600"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
            <div className="p-6">
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Title</label>
                  <input
                    type="text"
                    value={editingInterview.title || ''}
                    onChange={(e) => setEditingInterview({ ...editingInterview, title: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-violet-500 focus:border-violet-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Notes</label>
                  <textarea
                    value={editingInterview.notes || ''}
                    onChange={(e) => setEditingInterview({ ...editingInterview, notes: e.target.value })}
                    rows={4}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-violet-500 focus:border-violet-500"
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Duration (minutes)</label>
                    <input
                      type="number"
                      value={editingInterview.duration_minutes || 60}
                      onChange={(e) => setEditingInterview({ ...editingInterview, duration_minutes: parseInt(e.target.value) })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-violet-500 focus:border-violet-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Location</label>
                    <input
                      type="text"
                      value={editingInterview.location || ''}
                      onChange={(e) => setEditingInterview({ ...editingInterview, location: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-violet-500 focus:border-violet-500"
                    />
                  </div>
                </div>
              </div>
            </div>
            <div className="border-t border-gray-200 p-6 flex justify-end gap-3">
              <button
                onClick={() => {
                  setIsInterviewModalOpen(false);
                  setEditingInterview(null);
                }}
                className="px-4 py-2 text-sm font-medium text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={async () => {
                  try {
                    await interviewsApi.update(editingInterview.id, {
                      title: editingInterview.title,
                      notes: editingInterview.notes,
                      duration_minutes: editingInterview.duration_minutes,
                      location: editingInterview.location
                    });
                    alert('Interview updated successfully!');
                    setIsInterviewModalOpen(false);
                    setEditingInterview(null);
                  } catch (error) {
                    console.error('Failed to update interview:', error);
                    alert('Failed to update interview');
                  }
                }}
                className="px-4 py-2 text-sm font-semibold text-white bg-violet-600 rounded-lg hover:bg-violet-700"
              >
                Save Changes
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default function RecruitmentWorkflowsPage() {
  return (
    <ProtectedRoute>
      <RecruitmentWorkflowsPageContent />
    </ProtectedRoute>
  );
}