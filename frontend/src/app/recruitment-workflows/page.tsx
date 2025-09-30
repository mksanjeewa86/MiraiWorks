'use client';

import React, { useState, useEffect } from 'react';
import type { CSSProperties } from 'react';
import AppLayout from '@/components/layout/AppLayout';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import { useAuth } from '@/contexts/AuthContext';
import { recruitmentWorkflowsApi, workflowIntegrationService, type RecruitmentProcess, type ProcessNode } from '@/api/recruitment-workflows';
import { interviewsApi } from '@/api/interviews';
import { todosApi } from '@/api/todos';
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

// Use types from API
import type { Interview } from '@/types/interview';
import type { Todo } from '@/types/todo';

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
            `📋 Created ${todoCount} coding test assignments\n\n` +
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
              Recruitment Workflows
            </h1>
            <p className="text-gray-600 mt-1">
              Create and manage recruitment processes with multiple interview stages, coding tests, and assessments
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

        {/* Coming Soon Banner */}
        <div className="bg-gradient-to-r from-violet-50 to-purple-50 border border-violet-200 rounded-lg p-6">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-violet-100 rounded-full">
              <GitBranch className="h-6 w-6 text-violet-600" />
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-gray-900">Visual Workflow Designer Coming Soon!</h3>
              <p className="text-gray-600 mt-1">
                We're building a drag-and-drop interface for creating complex recruitment workflows.
                Create processes with conditional paths, score-based routing, and visual node editing.
              </p>
              <div className="mt-3 flex items-center gap-4 text-sm text-gray-600">
                <span className="flex items-center gap-1">
                  <Video className="h-4 w-4" /> Interview Nodes
                </span>
                <span className="flex items-center gap-1">
                  <CheckSquare className="h-4 w-4" /> Coding Tests
                </span>
                <span className="flex items-center gap-1">
                  <TrendingUp className="h-4 w-4" /> 適性検査 (Aptitude Tests)
                </span>
                <span className="flex items-center gap-1">
                  <GitBranch className="h-4 w-4" /> Decision Points
                </span>
              </div>
            </div>
          </div>
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
      name: 'Software Engineer Recruitment',
      description: 'Complete technical recruitment with coding tests and multiple interview stages',
      steps: [
        {
          type: 'interview' as const,
          title: 'Initial HR Screening',
          description: 'Initial screening interview with HR team',
          interview_config: {
            duration: 30,
            interview_type: 'hr_screening',
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
            interview_type: 'technical',
            location: 'Conference Room A'
          }
        },
        {
          type: 'interview' as const,
          title: 'Team Culture Interview',
          description: 'Cultural fit and team dynamics interview',
          interview_config: {
            duration: 45,
            interview_type: 'culture',
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
            interview_type: 'general',
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
            interview_type: 'final',
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
              placeholder="e.g. Software Engineer Recruitment"
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

// Visual Workflow Editor Modal
interface WorkflowEditorModalProps {
  isOpen: boolean;
  onClose: () => void;
  process: RecruitmentProcess | null;
  onSave: (process: RecruitmentProcess) => void;
}

interface WorkflowNode {
  id: string;
  type: 'interview' | 'todo' | 'assessment' | 'decision' | 'start' | 'end';
  title: string;
  description?: string;
  x: number;
  y: number;
  config?: any;
  connections?: string[];
}

function WorkflowEditorModal({ isOpen, onClose, process, onSave }: WorkflowEditorModalProps) {
  const [nodes, setNodes] = useState<WorkflowNode[]>([]);
  const [selectedNode, setSelectedNode] = useState<WorkflowNode | null>(null);
  const [dragNode, setDragNode] = useState<{ id: string; startX: number; startY: number } | null>(null);
  const [showNodePanel, setShowNodePanel] = useState(false);
  const [processTitle, setProcessTitle] = useState('');
  const [processDescription, setProcessDescription] = useState('');

  // Initialize nodes when process changes
  useEffect(() => {
    if (process && isOpen) {
      setProcessTitle(process.name);
      setProcessDescription(process.description || '');

      // Convert existing nodes or create default workflow
      if (process.nodes && process.nodes.length > 0) {
        const workflowNodes: WorkflowNode[] = [
          { id: 'start', type: 'start', title: 'Start', x: 100, y: 200 },
          ...process.nodes.map((node, index) => ({
            id: `node-${node.id}`,
            type: node.node_type,
            title: node.title,
            description: node.description,
            x: node.position_x || 300 + (index * 200),
            y: node.position_y || 200,
            config: node.config
          })),
          { id: 'end', type: 'end', title: 'End', x: 700, y: 200 }
        ];
        setNodes(workflowNodes);
      } else {
        // Default workflow template
        setNodes([
          { id: 'start', type: 'start', title: 'Start', x: 100, y: 200 },
          { id: 'end', type: 'end', title: 'End', x: 700, y: 200 }
        ]);
      }
    }
  }, [process, isOpen]);

  const handleNodeDragStart = (nodeId: string, e: React.MouseEvent) => {
    const rect = e.currentTarget.getBoundingClientRect();
    setDragNode({
      id: nodeId,
      startX: e.clientX - rect.left,
      startY: e.clientY - rect.top
    });
  };

  const handleNodeDrag = (e: React.MouseEvent) => {
    if (!dragNode) return;

    const canvas = e.currentTarget as HTMLElement;
    const rect = canvas.getBoundingClientRect();
    const newX = e.clientX - rect.left - dragNode.startX;
    const newY = e.clientY - rect.top - dragNode.startY;

    setNodes(prev => prev.map(node =>
      node.id === dragNode.id ? { ...node, x: Math.max(0, newX), y: Math.max(0, newY) } : node
    ));
  };

  const handleNodeDragEnd = () => {
    setDragNode(null);
  };

  const addNode = (type: WorkflowNode['type']) => {
    const newNode: WorkflowNode = {
      id: `node-${Date.now()}`,
      type,
      title: type === 'interview' ? 'New Interview' :
             type === 'todo' ? 'New Coding Test' :
             type === 'assessment' ? 'New 適性検査' :
             'New Decision Point',
      x: 400,
      y: 250,
      config: {}
    };
    setNodes(prev => [...prev, newNode]);
    setSelectedNode(newNode);
    setShowNodePanel(true);
  };

  const updateNode = (nodeId: string, updates: Partial<WorkflowNode>) => {
    setNodes(prev => prev.map(node =>
      node.id === nodeId ? { ...node, ...updates } : node
    ));
    if (selectedNode?.id === nodeId) {
      setSelectedNode(prev => prev ? { ...prev, ...updates } : null);
    }
  };

  const deleteNode = (nodeId: string) => {
    if (nodeId === 'start' || nodeId === 'end') return;
    setNodes(prev => prev.filter(node => node.id !== nodeId));
    if (selectedNode?.id === nodeId) {
      setSelectedNode(null);
      setShowNodePanel(false);
    }
  };

  const getNodeIcon = (type: WorkflowNode['type']) => {
    switch (type) {
      case 'interview': return <Video className="h-4 w-4" />;
      case 'todo': return <CheckSquare className="h-4 w-4" />;
      case 'assessment': return <TrendingUp className="h-4 w-4" />;
      case 'decision': return <GitBranch className="h-4 w-4" />;
      case 'start': return <Play className="h-4 w-4" />;
      case 'end': return <Square className="h-4 w-4" />;
      default: return <Circle className="h-4 w-4" />;
    }
  };

  const getNodeColor = (type: WorkflowNode['type']) => {
    switch (type) {
      case 'interview': return 'bg-blue-500 border-blue-600';
      case 'todo': return 'bg-green-500 border-green-600';
      case 'assessment': return 'bg-purple-500 border-purple-600';
      case 'decision': return 'bg-orange-500 border-orange-600';
      case 'start': return 'bg-gray-500 border-gray-600';
      case 'end': return 'bg-red-500 border-red-600';
      default: return 'bg-gray-400 border-gray-500';
    }
  };

  const handleSave = async () => {
    if (!process) return;

    try {
      // Convert workflow nodes back to ProcessNode format
      const processNodes = nodes
        .filter(node => node.type !== 'start' && node.type !== 'end')
        .map((node, index) => ({
          id: parseInt(node.id.replace('node-', '')) || 0,
          process_id: process.id,
          node_type: node.type,
          title: node.title,
          description: node.description,
          sequence_order: index + 1,
          position_x: node.x,
          position_y: node.y,
          config: node.config,
          status: 'active' as const
        }));

      // Update process nodes via API
      for (const node of processNodes) {
        if (node.id > 0) {
          // Update existing node
          await recruitmentWorkflowsApi.updateNode(process.id, node.id, {
            node_type: node.node_type as 'interview' | 'todo' | 'assessment' | 'decision',
            title: node.title,
            description: node.description,
            sequence_order: node.sequence_order,
            position_x: node.position_x,
            position_y: node.position_y,
            config: node.config
          });
        } else {
          // Create new node
          await recruitmentWorkflowsApi.createNode(process.id, {
            node_type: node.node_type as 'interview' | 'todo' | 'assessment' | 'decision',
            title: node.title,
            description: node.description,
            sequence_order: node.sequence_order,
            position_x: node.position_x,
            position_y: node.position_y,
            config: node.config
          });
        }
      }

      // Update process basic info if changed
      if (processTitle !== process.name || processDescription !== process.description) {
        await recruitmentWorkflowsApi.updateProcess(process.id, {
          name: processTitle,
          description: processDescription
        });
      }

      // Create updated process object
      const updatedProcess: RecruitmentProcess = {
        ...process,
        name: processTitle,
        description: processDescription,
        nodes: processNodes as ProcessNode[]
      };

      onSave(updatedProcess);
      alert('✅ Workflow saved successfully!');
    } catch (error) {
      console.error('Failed to save workflow:', error);
      alert('❌ Failed to save workflow');
    }
  };

  if (!isOpen || !process) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-black bg-opacity-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-7xl h-[90vh] flex flex-col">
        {/* Header */}
        <div className="border-b border-gray-200 p-6 flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
              <GitBranch className="h-5 w-5 text-violet-600" />
              Visual Workflow Editor
            </h2>
            <p className="text-sm text-gray-500 mt-1">Drag and drop to design your recruitment workflow</p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => setShowNodePanel(!showNodePanel)}
              className="px-3 py-2 text-sm font-medium text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              {showNodePanel ? 'Hide' : 'Show'} Properties
            </button>
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
          {/* Left Sidebar - Node Palette */}
          <div className="w-64 border-r border-gray-200 p-4 bg-gray-50">
            <h3 className="font-semibold text-gray-900 mb-4">Node Types</h3>

            {/* Process Info */}
            <div className="mb-6 space-y-3">
              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">Process Name</label>
                <input
                  type="text"
                  value={processTitle}
                  onChange={(e) => setProcessTitle(e.target.value)}
                  className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-violet-500 focus:border-violet-500"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">Description</label>
                <textarea
                  value={processDescription}
                  onChange={(e) => setProcessDescription(e.target.value)}
                  rows={2}
                  className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-violet-500 focus:border-violet-500"
                />
              </div>
            </div>

            {/* Node Palette */}
            <div className="space-y-2">
              <button
                onClick={() => addNode('interview')}
                className="w-full flex items-center gap-3 p-3 text-left text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-blue-50 hover:border-blue-300"
              >
                <Video className="h-4 w-4 text-blue-500" />
                Interview Node
              </button>
              <button
                onClick={() => addNode('todo')}
                className="w-full flex items-center gap-3 p-3 text-left text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-green-50 hover:border-green-300"
              >
                <CheckSquare className="h-4 w-4 text-green-500" />
                Coding Test
              </button>
              <button
                onClick={() => addNode('assessment')}
                className="w-full flex items-center gap-3 p-3 text-left text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-purple-50 hover:border-purple-300"
              >
                <TrendingUp className="h-4 w-4 text-purple-500" />
                適性検査 (Aptitude)
              </button>
              <button
                onClick={() => addNode('decision')}
                className="w-full flex items-center gap-3 p-3 text-left text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-orange-50 hover:border-orange-300"
              >
                <GitBranch className="h-4 w-4 text-orange-500" />
                Decision Point
              </button>
            </div>

            <div className="mt-6 p-3 bg-blue-50 border border-blue-200 rounded-lg">
              <p className="text-xs text-blue-800">
                💡 <strong>Tip:</strong> Click and drag nodes to reposition them. Click a node to edit its properties.
              </p>
            </div>
          </div>

          {/* Center Canvas */}
          <div className="flex-1 relative overflow-auto bg-gray-100">
            <div
              className="relative w-full h-full min-w-[1000px] min-h-[600px]"
              onMouseMove={handleNodeDrag}
              onMouseUp={handleNodeDragEnd}
              style={{ cursor: dragNode ? 'grabbing' : 'default' }}
            >
              {/* Grid Background */}
              <div
                className="absolute inset-0 opacity-20"
                style={{
                  backgroundImage: `radial-gradient(circle, #6b7280 1px, transparent 1px)`,
                  backgroundSize: '20px 20px'
                }}
              />

              {/* Connection Lines */}
              <svg className="absolute inset-0 w-full h-full pointer-events-none">
                {nodes.map((node, index) => {
                  const nextNode = nodes[index + 1];
                  if (!nextNode) return null;
                  return (
                    <line
                      key={`line-${node.id}-${nextNode.id}`}
                      x1={node.x + 60}
                      y1={node.y + 30}
                      x2={nextNode.x + 60}
                      y2={nextNode.y + 30}
                      stroke="#9ca3af"
                      strokeWidth="2"
                      strokeDasharray="5,5"
                    />
                  );
                })}
              </svg>

              {/* Workflow Nodes */}
              {nodes.map((node) => (
                <div
                  key={node.id}
                  className={`absolute cursor-move select-none ${
                    selectedNode?.id === node.id ? 'ring-2 ring-violet-500' : ''
                  }`}
                  style={{ left: node.x, top: node.y }}
                  onMouseDown={(e) => handleNodeDragStart(node.id, e)}
                  onClick={() => {
                    setSelectedNode(node);
                    setShowNodePanel(true);
                  }}
                >
                  <div className={`w-32 h-16 rounded-lg border-2 ${getNodeColor(node.type)} text-white shadow-lg flex flex-col items-center justify-center p-2 hover:shadow-xl transition-shadow`}>
                    {getNodeIcon(node.type)}
                    <span className="text-xs font-semibold text-center leading-tight">
                      {node.title}
                    </span>
                  </div>
                  {node.type !== 'start' && node.type !== 'end' && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        deleteNode(node.id);
                      }}
                      className="absolute -top-2 -right-2 w-6 h-6 bg-red-500 text-white rounded-full flex items-center justify-center text-xs hover:bg-red-600"
                    >
                      ×
                    </button>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Right Sidebar - Node Properties */}
          {showNodePanel && selectedNode && (
            <div className="w-80 border-l border-gray-200 p-4 bg-gray-50">
              <h3 className="font-semibold text-gray-900 mb-4">Node Properties</h3>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Title</label>
                  <input
                    type="text"
                    value={selectedNode.title}
                    onChange={(e) => updateNode(selectedNode.id, { title: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-violet-500 focus:border-violet-500"
                    disabled={selectedNode.type === 'start' || selectedNode.type === 'end'}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
                  <textarea
                    value={selectedNode.description || ''}
                    onChange={(e) => updateNode(selectedNode.id, { description: e.target.value })}
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-violet-500 focus:border-violet-500"
                    disabled={selectedNode.type === 'start' || selectedNode.type === 'end'}
                  />
                </div>

                {/* Type-specific configuration */}
                {selectedNode.type === 'interview' && (
                  <div className="space-y-3">
                    <h4 className="font-medium text-gray-900">Interview Settings</h4>
                    <div>
                      <label className="block text-sm text-gray-700 mb-1">Duration (minutes)</label>
                      <input
                        type="number"
                        value={selectedNode.config?.duration || 60}
                        onChange={(e) => updateNode(selectedNode.id, {
                          config: { ...selectedNode.config, duration: parseInt(e.target.value) }
                        })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                      />
                    </div>
                    <div>
                      <label className="block text-sm text-gray-700 mb-1">Interview Type</label>
                      <select
                        value={selectedNode.config?.interview_type || 'technical'}
                        onChange={(e) => updateNode(selectedNode.id, {
                          config: { ...selectedNode.config, interview_type: e.target.value }
                        })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                      >
                        <option value="hr_screening">HR Screening</option>
                        <option value="technical">Technical</option>
                        <option value="culture">Culture Fit</option>
                        <option value="final">Final Interview</option>
                      </select>
                    </div>
                  </div>
                )}

                {selectedNode.type === 'todo' && (
                  <div className="space-y-3">
                    <h4 className="font-medium text-gray-900">Assignment Settings</h4>
                    <div>
                      <label className="block text-sm text-gray-700 mb-1">Priority</label>
                      <select
                        value={selectedNode.config?.priority || 'medium'}
                        onChange={(e) => updateNode(selectedNode.id, {
                          config: { ...selectedNode.config, priority: e.target.value }
                        })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                      >
                        <option value="low">Low</option>
                        <option value="medium">Medium</option>
                        <option value="high">High</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm text-gray-700 mb-1">Assignment Type</label>
                      <select
                        value={selectedNode.config?.assignment_type || 'coding'}
                        onChange={(e) => updateNode(selectedNode.id, {
                          config: { ...selectedNode.config, assignment_type: e.target.value }
                        })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                      >
                        <option value="coding">Coding Challenge</option>
                        <option value="design">Design Task</option>
                        <option value="analysis">Data Analysis</option>
                        <option value="presentation">Presentation</option>
                      </select>
                    </div>
                  </div>
                )}

                {selectedNode.type === 'assessment' && (
                  <div className="space-y-3">
                    <h4 className="font-medium text-gray-900">適性検査 Settings</h4>
                    <div>
                      <label className="block text-sm text-gray-700 mb-1">Assessment Type</label>
                      <select
                        value={selectedNode.config?.assessment_type || 'personality'}
                        onChange={(e) => updateNode(selectedNode.id, {
                          config: { ...selectedNode.config, assessment_type: e.target.value }
                        })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                      >
                        <option value="personality">Personality Test</option>
                        <option value="aptitude">Aptitude Test</option>
                        <option value="cognitive">Cognitive Assessment</option>
                        <option value="skills">Skills Assessment</option>
                      </select>
                    </div>
                  </div>
                )}

                <div className="text-xs text-gray-500 mt-4">
                  Position: ({selectedNode.x}, {selectedNode.y})
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="border-t border-gray-200 p-6 flex justify-between items-center">
          <div className="text-sm text-gray-600">
            {nodes.length - 2} workflow steps configured
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
              className="px-4 py-2 text-sm font-semibold text-white bg-violet-600 rounded-lg hover:bg-violet-700"
            >
              Save Workflow
            </button>
          </div>
        </div>
      </div>
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