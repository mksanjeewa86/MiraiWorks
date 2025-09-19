'use client';

import React, { useState, useEffect } from 'react';
import { Plus, Search, Filter, Calendar, Clock, User, MapPin, Edit, Trash2, Eye } from 'lucide-react';
import Link from 'next/link';
import AppLayout from '@/components/layout/AppLayout';
import ProtectedRoute from '@/components/auth/ProtectedRoute';

interface Interview {
  id: number;
  title: string;
  candidate_name: string;
  recruiter_name: string;
  company_name: string;
  scheduled_date: string;
  start_time: string;
  end_time: string;
  location: string;
  type: 'phone' | 'video' | 'in_person';
  status: 'scheduled' | 'completed' | 'cancelled' | 'rescheduled';
  notes?: string;
  created_at: string;
}

function InterviewsPageContent() {
  const [interviews, setInterviews] = useState<Interview[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [typeFilter, setTypeFilter] = useState<string>('all');
  const [sortBy, setSortBy] = useState<string>('scheduled_date');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage] = useState(10);

  // Mock data for development
  const mockInterviews: Interview[] = [
    {
      id: 1,
      title: 'Senior Software Engineer Interview',
      candidate_name: 'John Smith',
      recruiter_name: 'Sarah Wilson',
      company_name: 'Tech Corp',
      scheduled_date: '2025-01-25',
      start_time: '10:00',
      end_time: '11:00',
      location: 'Conference Room A',
      type: 'in_person',
      status: 'scheduled',
      notes: 'Technical interview focusing on React and Node.js',
      created_at: '2025-01-20T10:00:00Z'
    },
    {
      id: 2,
      title: 'Product Manager Position',
      candidate_name: 'Emily Chen',
      recruiter_name: 'Michael Johnson',
      company_name: 'Innovation Ltd',
      scheduled_date: '2025-01-26',
      start_time: '14:00',
      end_time: '15:30',
      location: 'Zoom Meeting',
      type: 'video',
      status: 'scheduled',
      notes: 'Final round interview with CEO',
      created_at: '2025-01-21T09:30:00Z'
    },
    {
      id: 3,
      title: 'DevOps Engineer Role',
      candidate_name: 'David Brown',
      recruiter_name: 'Lisa Anderson',
      company_name: 'Cloud Solutions',
      scheduled_date: '2025-01-24',
      start_time: '09:00',
      end_time: '10:00',
      location: 'Phone Interview',
      type: 'phone',
      status: 'completed',
      notes: 'Initial screening completed successfully',
      created_at: '2025-01-19T15:00:00Z'
    }
  ];

  useEffect(() => {
    // Simulate API call
    const fetchInterviews = async () => {
      setLoading(true);
      try {
        // In a real app, this would be an API call:
        // const response = await fetch('/api/interviews');
        // const data = await response.json();

        // For now, use mock data
        setTimeout(() => {
          setInterviews(mockInterviews);
          setLoading(false);
        }, 1000);
      } catch (error) {
        console.error('Error fetching interviews:', error);
        setLoading(false);
      }
    };

    fetchInterviews();
  }, []);

  // Filter and sort interviews
  const filteredInterviews = interviews
    .filter(interview => {
      const matchesSearch =
        interview.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        interview.candidate_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        interview.company_name.toLowerCase().includes(searchTerm.toLowerCase());

      const matchesStatus = statusFilter === 'all' || interview.status === statusFilter;
      const matchesType = typeFilter === 'all' || interview.type === typeFilter;

      return matchesSearch && matchesStatus && matchesType;
    })
    .sort((a, b) => {
      let aValue: unknown = a[sortBy as keyof Interview];
      let bValue: unknown = b[sortBy as keyof Interview];

      if (sortBy === 'scheduled_date') {
        aValue = new Date(a.scheduled_date + ' ' + a.start_time);
        bValue = new Date(b.scheduled_date + ' ' + b.start_time);
      }

      if (sortOrder === 'asc') {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });

  // Pagination
  const totalPages = Math.ceil(filteredInterviews.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const paginatedInterviews = filteredInterviews.slice(startIndex, startIndex + itemsPerPage);

  const getStatusBadge = (status: string) => {
    const statusClasses = {
      scheduled: 'bg-blue-100 text-blue-800',
      completed: 'bg-green-100 text-green-800',
      cancelled: 'bg-red-100 text-red-800',
      rescheduled: 'bg-yellow-100 text-yellow-800'
    };

    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusClasses[status as keyof typeof statusClasses]}`}>
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </span>
    );
  };

  const getTypeBadge = (type: string) => {
    const typeClasses = {
      phone: 'bg-gray-100 text-gray-800',
      video: 'bg-purple-100 text-purple-800',
      in_person: 'bg-indigo-100 text-indigo-800'
    };

    const typeLabels = {
      phone: 'Phone',
      video: 'Video',
      in_person: 'In-Person'
    };

    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${typeClasses[type as keyof typeof typeClasses]}`}>
        {typeLabels[type as keyof typeof typeLabels]}
      </span>
    );
  };

  const handleDelete = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this interview?')) {
      try {
        // In a real app: await fetch(`/api/interviews/${id}`, { method: 'DELETE' });
        setInterviews(interviews.filter(interview => interview.id !== id));
      } catch (error) {
        console.error('Error deleting interview:', error);
      }
    }
  };

  if (loading) {
    return (
      <AppLayout>
        <div className="min-h-screen bg-gray-50 flex items-center justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-2 text-gray-600">Loading interviews...</span>
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout>
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Header */}
          <div className="flex justify-between items-center mb-8">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Interviews</h1>
              <p className="text-gray-600 mt-1">Manage and track all interview sessions</p>
            </div>
            <Link
              href="/interviews/new"
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors"
            >
              <Plus size={20} />
              Schedule Interview
            </Link>
          </div>

          {/* Filters and Search */}
          <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              {/* Search */}
              <div className="relative">
                <Search className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search interviews..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 pr-4 py-2 w-full border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              {/* Status Filter */}
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">All Statuses</option>
                <option value="scheduled">Scheduled</option>
                <option value="completed">Completed</option>
                <option value="cancelled">Cancelled</option>
                <option value="rescheduled">Rescheduled</option>
              </select>

              {/* Type Filter */}
              <select
                value={typeFilter}
                onChange={(e) => setTypeFilter(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">All Types</option>
                <option value="phone">Phone</option>
                <option value="video">Video</option>
                <option value="in_person">In-Person</option>
              </select>

              {/* Sort */}
              <select
                value={`${sortBy}_${sortOrder}`}
                onChange={(e) => {
                  const [field, order] = e.target.value.split('_');
                  setSortBy(field);
                  setSortOrder(order as 'asc' | 'desc');
                }}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="scheduled_date_asc">Date (Earliest)</option>
                <option value="scheduled_date_desc">Date (Latest)</option>
                <option value="candidate_name_asc">Candidate (A-Z)</option>
                <option value="candidate_name_desc">Candidate (Z-A)</option>
                <option value="status_asc">Status (A-Z)</option>
              </select>
            </div>
          </div>

          {/* Results Count */}
          <div className="mb-4">
            <p className="text-gray-600">
              Showing {startIndex + 1}-{Math.min(startIndex + itemsPerPage, filteredInterviews.length)} of {filteredInterviews.length} interviews
            </p>
          </div>

          {/* Interviews List */}
          <div className="bg-white rounded-lg shadow-sm">
            {paginatedInterviews.length === 0 ? (
              <div className="p-8 text-center">
                <Calendar className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No interviews found</h3>
                <p className="text-gray-600 mb-4">
                  {searchTerm || statusFilter !== 'all' || typeFilter !== 'all'
                    ? 'Try adjusting your filters to see more results.'
                    : 'Get started by scheduling your first interview.'
                  }
                </p>
                {(!searchTerm && statusFilter === 'all' && typeFilter === 'all') && (
                  <Link
                    href="/interviews/new"
                    className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg inline-flex items-center gap-2 transition-colors"
                  >
                    <Plus size={20} />
                    Schedule Interview
                  </Link>
                )}
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Interview Details
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Participants
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Schedule
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Status
                      </th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {paginatedInterviews.map((interview) => (
                      <tr key={interview.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div>
                            <div className="text-sm font-medium text-gray-900">{interview.title}</div>
                            <div className="text-sm text-gray-500 flex items-center gap-2 mt-1">
                              <MapPin size={14} />
                              {interview.location}
                            </div>
                            <div className="mt-1">
                              {getTypeBadge(interview.type)}
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div>
                            <div className="text-sm font-medium text-gray-900 flex items-center gap-2">
                              <User size={14} />
                              {interview.candidate_name}
                            </div>
                            <div className="text-sm text-gray-500">
                              Recruiter: {interview.recruiter_name}
                            </div>
                            <div className="text-sm text-gray-500">
                              {interview.company_name}
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900 flex items-center gap-2">
                            <Calendar size={14} />
                            {new Date(interview.scheduled_date).toLocaleDateString()}
                          </div>
                          <div className="text-sm text-gray-500 flex items-center gap-2 mt-1">
                            <Clock size={14} />
                            {interview.start_time} - {interview.end_time}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          {getStatusBadge(interview.status)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                          <div className="flex justify-end gap-2">
                            <Link
                              href={`/interviews/${interview.id}`}
                              className="text-blue-600 hover:text-blue-900 p-1 rounded hover:bg-blue-50"
                              title="View Details"
                            >
                              <Eye size={16} />
                            </Link>
                            <Link
                              href={`/interviews/${interview.id}/edit`}
                              className="text-gray-600 hover:text-gray-900 p-1 rounded hover:bg-gray-50"
                              title="Edit Interview"
                            >
                              <Edit size={16} />
                            </Link>
                            <button
                              onClick={() => handleDelete(interview.id)}
                              className="text-red-600 hover:text-red-900 p-1 rounded hover:bg-red-50"
                              title="Delete Interview"
                            >
                              <Trash2 size={16} />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="mt-6 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                  disabled={currentPage === 1}
                  className="px-3 py-2 border border-gray-300 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
                >
                  Previous
                </button>
                <span className="text-sm text-gray-600">
                  Page {currentPage} of {totalPages}
                </span>
                <button
                  onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                  disabled={currentPage === totalPages}
                  className="px-3 py-2 border border-gray-300 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
                >
                  Next
                </button>
              </div>
              <div className="flex gap-1">
                {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                  const pageNum = i + 1;
                  return (
                    <button
                      key={pageNum}
                      onClick={() => setCurrentPage(pageNum)}
                      className={`px-3 py-2 rounded-lg ${
                        currentPage === pageNum
                          ? 'bg-blue-600 text-white'
                          : 'border border-gray-300 hover:bg-gray-50'
                      }`}
                    >
                      {pageNum}
                    </button>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      </div>
    </AppLayout>
  );
}

export default function InterviewsPage() {
  return (
    <ProtectedRoute>
      <InterviewsPageContent />
    </ProtectedRoute>
  );
}
