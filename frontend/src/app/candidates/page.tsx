'use client';

import React, { useState, useEffect, useMemo } from 'react';
import { Plus, Search, Mail, Phone, MapPin, Edit, Trash2, Eye, User, Star, Calendar, Download, Upload } from 'lucide-react';
import Link from 'next/link';
import AppLayout from '@/components/layout/AppLayout';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import { candidatesApi } from '@/api/candidates';
import type { Candidate, CandidateApiFilters } from '@/types/candidate';


function CandidatesPageContent() {
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [sourceFilter, setSourceFilter] = useState<string>('all');
  const [experienceFilter, setExperienceFilter] = useState<string>('all');
  const [sortBy, setSortBy] = useState<string>('last_activity');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage] = useState(10);
  const [totalCandidates, setTotalCandidates] = useState(0);
  const [totalPages, setTotalPages] = useState(0);

  // Mock data for development
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const mockCandidates: Candidate[] = useMemo(() => [
    {
      id: 1,
      first_name: 'John',
      last_name: 'Smith',
      email: 'john.smith@email.com',
      phone: '+1-555-0123',
      location: 'San Francisco, CA',
      title: 'Senior Software Engineer',
      company: 'Tech Corp',
      experience_years: 8,
      skills: ['React', 'Node.js', 'TypeScript', 'Python', 'AWS'],
      status: 'interviewing',
      rating: 4.5,
      source: 'linkedin',
      applied_positions: 2,
      last_activity: '2025-01-20T10:00:00Z',
      resume_url: '/resumes/john-smith.pdf',
      notes: 'Strong technical background, good communication skills',
      created_at: '2025-01-15T09:00:00Z'
    },
    {
      id: 2,
      first_name: 'Emily',
      last_name: 'Chen',
      email: 'emily.chen@email.com',
      phone: '+1-555-0124',
      location: 'New York, NY',
      title: 'Product Manager',
      company: 'Innovation Ltd',
      experience_years: 6,
      skills: ['Product Strategy', 'Agile', 'Analytics', 'SQL', 'Figma'],
      status: 'active',
      rating: 4.8,
      source: 'website',
      applied_positions: 1,
      last_activity: '2025-01-21T14:30:00Z',
      resume_url: '/resumes/emily-chen.pdf',
      notes: 'Excellent product sense, proven track record',
      created_at: '2025-01-18T11:15:00Z'
    },
    {
      id: 3,
      first_name: 'David',
      last_name: 'Brown',
      email: 'david.brown@email.com',
      phone: '+1-555-0125',
      location: 'Austin, TX',
      title: 'DevOps Engineer',
      company: 'Cloud Solutions',
      experience_years: 5,
      skills: ['Docker', 'Kubernetes', 'AWS', 'Terraform', 'Jenkins'],
      status: 'hired',
      rating: 4.2,
      source: 'referral',
      applied_positions: 1,
      last_activity: '2025-01-19T16:45:00Z',
      resume_url: '/resumes/david-brown.pdf',
      notes: 'Recently hired for DevOps Engineer position',
      created_at: '2025-01-10T13:20:00Z'
    },
    {
      id: 4,
      first_name: 'Sarah',
      last_name: 'Wilson',
      email: 'sarah.wilson@email.com',
      phone: '+1-555-0126',
      location: 'Seattle, WA',
      title: 'UX Designer',
      company: 'Design Studio',
      experience_years: 4,
      skills: ['Figma', 'Sketch', 'User Research', 'Prototyping', 'CSS'],
      status: 'rejected',
      rating: 3.5,
      source: 'agency',
      applied_positions: 1,
      last_activity: '2025-01-17T12:10:00Z',
      resume_url: '/resumes/sarah-wilson.pdf',
      notes: 'Good design skills but not the right fit for this role',
      created_at: '2025-01-12T08:45:00Z'
    }
  ], []);

  // Fetch candidates from API
  useEffect(() => {
    const fetchCandidates = async () => {
      try {
        setLoading(true);
        setError('');

        const filters: CandidateApiFilters = {
          page: currentPage,
          size: itemsPerPage,
          search: searchTerm || undefined,
          role: 'candidate' as const
        };

        const response = await candidatesApi.getCandidates(filters);

        // Map users to candidates format
        const candidatesData = response.data?.users?.map(user => ({
          id: user.id,
          first_name: user.first_name,
          last_name: user.last_name,
          email: user.email,
          phone: user.phone || '',
          location: '', // Not available in User type
          title: 'Job Seeker', // Not available in User type
          company: user.company_name || '',
          experience_years: 0, // Not available in User type
          skills: [], // Not available in User type
          status: 'active' as const,
          rating: 0,
          source: 'website' as const,
          applied_positions: 0,
          last_activity: user.updated_at || user.created_at,
          resume_url: '',
          notes: '', // Not available in User type
          created_at: user.created_at
        })) || [];

        setCandidates(candidatesData);
        setTotalCandidates(response.data?.total || 0);
        setTotalPages(response.data?.pages || 0);
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to fetch candidates';
        setError(errorMessage);
        console.error('Error fetching candidates:', err);
        setCandidates([]);
      } finally {
        setLoading(false);
      }
    };

    fetchCandidates();
  }, [currentPage, itemsPerPage, searchTerm]);

  // Apply client-side filters (search is handled server-side)
  const filteredCandidates = candidates
    .filter(candidate => {
      const matchesStatus = statusFilter === 'all' || candidate.status === statusFilter;
      const matchesSource = sourceFilter === 'all' || candidate.source === sourceFilter;

      let matchesExperience = true;
      if (experienceFilter !== 'all' && candidate.experience_years) {
        switch (experienceFilter) {
          case 'entry':
            matchesExperience = candidate.experience_years <= 2;
            break;
          case 'mid':
            matchesExperience = candidate.experience_years >= 3 && candidate.experience_years <= 7;
            break;
          case 'senior':
            matchesExperience = candidate.experience_years >= 8;
            break;
        }
      }

      return matchesStatus && matchesSource && matchesExperience;
    })
    .sort((a, b) => {
      let aValue: string | number | Date = a[sortBy as keyof Candidate] as string;
      let bValue: string | number | Date = b[sortBy as keyof Candidate] as string;

      if (sortBy === 'last_activity' || sortBy === 'created_at') {
        aValue = new Date(aValue as string);
        bValue = new Date(bValue as string);
      }

      if (sortBy === 'name') {
        aValue = `${a.first_name} ${a.last_name}`;
        bValue = `${b.first_name} ${b.last_name}`;
      }

      if (sortOrder === 'asc') {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });

  // Calculate display range for results count
  const startIndex = (currentPage - 1) * itemsPerPage;

  // Use candidates from API directly (pagination handled server-side)
  const paginatedCandidates = filteredCandidates;

  const getStatusBadge = (status: string) => {
    const statusClasses = {
      active: 'bg-green-100 text-green-800',
      interviewing: 'bg-blue-100 text-blue-800',
      hired: 'bg-purple-100 text-purple-800',
      rejected: 'bg-red-100 text-red-800',
      withdrawn: 'bg-gray-100 text-gray-800'
    };

    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusClasses[status as keyof typeof statusClasses]}`}>
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </span>
    );
  };

  const getSourceBadge = (source: string) => {
    const sourceClasses = {
      website: 'bg-blue-100 text-blue-800',
      referral: 'bg-green-100 text-green-800',
      linkedin: 'bg-indigo-100 text-indigo-800',
      agency: 'bg-orange-100 text-orange-800',
      event: 'bg-purple-100 text-purple-800',
      other: 'bg-gray-100 text-gray-800'
    };

    const sourceLabels = {
      website: 'Website',
      referral: 'Referral',
      linkedin: 'LinkedIn',
      agency: 'Agency',
      event: 'Event',
      other: 'Other'
    };

    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${sourceClasses[source as keyof typeof sourceClasses]}`}>
        {sourceLabels[source as keyof typeof sourceLabels]}
      </span>
    );
  };

  const renderRating = (rating?: number) => {
    if (!rating) return null;

    return (
      <div className="flex items-center gap-1">
        {Array.from({ length: 5 }, (_, i) => (
          <Star
            key={i}
            size={12}
            className={`${
              i < Math.floor(rating) ? 'text-yellow-400 fill-current' : 'text-gray-300'
            }`}
          />
        ))}
        <span className="text-xs text-gray-600 ml-1">{rating.toFixed(1)}</span>
      </div>
    );
  };

  const handleDelete = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this candidate?')) {
      try {
        await candidatesApi.deleteCandidate(id);
        setCandidates(candidates.filter(candidate => candidate.id !== id));
        setTotalCandidates(prev => prev - 1);
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to delete candidate';
        setError(errorMessage);
        console.error('Error deleting candidate:', err);
      }
    }
  };

  const handleBulkExport = () => {
    // In a real app, this would trigger a CSV/PDF export
    alert('Export functionality would be implemented here');
  };

  if (loading) {
    return (
      <AppLayout>
        <div className="min-h-screen bg-gray-50 flex items-center justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-2 text-gray-600">Loading candidates...</span>
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
              <h1 className="text-3xl font-bold text-gray-900">Candidates</h1>
              <p className="text-gray-600 mt-1">Manage your talent pipeline and candidate relationships</p>
              {error && (
                <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg">
                  <p className="text-sm text-red-600">⚠️ {error}</p>
                </div>
              )}
            </div>
            <div className="flex gap-3">
              <button
                onClick={handleBulkExport}
                className="bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-lg flex items-center gap-2 transition-colors"
              >
                <Download size={20} />
                Export
              </button>
              <Link
                href="/candidates/new"
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors"
              >
                <Plus size={20} />
                Add Candidate
              </Link>
            </div>
          </div>

          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-lg shadow-sm p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <User className="h-8 w-8 text-blue-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Total Candidates</p>
                  <p className="text-2xl font-bold text-gray-900">{candidates.length}</p>
                </div>
              </div>
            </div>
            <div className="bg-white rounded-lg shadow-sm p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <Calendar className="h-8 w-8 text-green-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Interviewing</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {candidates.filter(c => c.status === 'interviewing').length}
                  </p>
                </div>
              </div>
            </div>
            <div className="bg-white rounded-lg shadow-sm p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <Star className="h-8 w-8 text-purple-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Hired</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {candidates.filter(c => c.status === 'hired').length}
                  </p>
                </div>
              </div>
            </div>
            <div className="bg-white rounded-lg shadow-sm p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <Upload className="h-8 w-8 text-orange-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">This Month</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {candidates.filter(c => {
                      const candidateDate = new Date(c.created_at);
                      const now = new Date();
                      return candidateDate.getMonth() === now.getMonth() &&
                             candidateDate.getFullYear() === now.getFullYear();
                    }).length}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Filters and Search */}
          <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
            <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
              {/* Search */}
              <div className="relative">
                <Search className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search candidates..."
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
                <option value="active">Active</option>
                <option value="interviewing">Interviewing</option>
                <option value="hired">Hired</option>
                <option value="rejected">Rejected</option>
                <option value="withdrawn">Withdrawn</option>
              </select>

              {/* Source Filter */}
              <select
                value={sourceFilter}
                onChange={(e) => setSourceFilter(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">All Sources</option>
                <option value="website">Website</option>
                <option value="referral">Referral</option>
                <option value="linkedin">LinkedIn</option>
                <option value="agency">Agency</option>
                <option value="event">Event</option>
                <option value="other">Other</option>
              </select>

              {/* Experience Filter */}
              <select
                value={experienceFilter}
                onChange={(e) => setExperienceFilter(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">All Experience</option>
                <option value="entry">Entry (0-2 years)</option>
                <option value="mid">Mid (3-7 years)</option>
                <option value="senior">Senior (8+ years)</option>
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
                <option value="last_activity_desc">Recent Activity</option>
                <option value="created_at_desc">Newest First</option>
                <option value="created_at_asc">Oldest First</option>
                <option value="name_asc">Name (A-Z)</option>
                <option value="name_desc">Name (Z-A)</option>
                <option value="rating_desc">Highest Rated</option>
              </select>
            </div>
          </div>

          {/* Results Count */}
          <div className="mb-4">
            <p className="text-gray-600">
              Showing {startIndex + 1}-{Math.min(startIndex + paginatedCandidates.length, startIndex + itemsPerPage)} of {totalCandidates} candidates
              {filteredCandidates.length !== candidates.length && (
                <span className="text-gray-500"> (filtered from {candidates.length})</span>
              )}
            </p>
          </div>

          {/* Candidates List */}
          <div className="bg-white rounded-lg shadow-sm">
            {paginatedCandidates.length === 0 ? (
              <div className="p-8 text-center">
                <User className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No candidates found</h3>
                <p className="text-gray-600 mb-4">
                  {searchTerm || statusFilter !== 'all' || sourceFilter !== 'all' || experienceFilter !== 'all'
                    ? 'Try adjusting your filters to see more results.'
                    : 'Get started by adding your first candidate.'
                  }
                </p>
                {(!searchTerm && statusFilter === 'all' && sourceFilter === 'all' && experienceFilter === 'all') && (
                  <Link
                    href="/candidates/new"
                    className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg inline-flex items-center gap-2 transition-colors"
                  >
                    <Plus size={20} />
                    Add Candidate
                  </Link>
                )}
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Candidate
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Contact & Location
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Experience & Skills
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Status & Rating
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Source & Activity
                      </th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {paginatedCandidates.map((candidate) => (
                      <tr key={candidate.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center">
                            <div className="flex-shrink-0 h-10 w-10">
                              <div className="h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center">
                                <span className="text-blue-600 font-medium text-sm">
                                  {candidate.first_name[0]}{candidate.last_name[0]}
                                </span>
                              </div>
                            </div>
                            <div className="ml-4">
                              <div className="text-sm font-medium text-gray-900">
                                {candidate.first_name} {candidate.last_name}
                              </div>
                              <div className="text-sm text-gray-500">
                                {candidate.title} {candidate.company && `at ${candidate.company}`}
                              </div>
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900 flex items-center gap-2">
                            <Mail size={14} />
                            {candidate.email}
                          </div>
                          {candidate.phone && (
                            <div className="text-sm text-gray-500 flex items-center gap-2 mt-1">
                              <Phone size={14} />
                              {candidate.phone}
                            </div>
                          )}
                          {candidate.location && (
                            <div className="text-sm text-gray-500 flex items-center gap-2 mt-1">
                              <MapPin size={14} />
                              {candidate.location}
                            </div>
                          )}
                        </td>
                        <td className="px-6 py-4">
                          <div className="text-sm text-gray-900">
                            {candidate.experience_years} years experience
                          </div>
                          <div className="flex flex-wrap gap-1 mt-2">
                            {candidate.skills.slice(0, 3).map((skill, index) => (
                              <span
                                key={index}
                                className="px-2 py-1 text-xs bg-gray-100 text-gray-800 rounded-full"
                              >
                                {skill}
                              </span>
                            ))}
                            {candidate.skills.length > 3 && (
                              <span className="px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded-full">
                                +{candidate.skills.length - 3} more
                              </span>
                            )}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="mb-2">
                            {getStatusBadge(candidate.status)}
                          </div>
                          {renderRating(candidate.rating)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="mb-2">
                            {getSourceBadge(candidate.source)}
                          </div>
                          <div className="text-sm text-gray-500">
                            {new Date(candidate.last_activity).toLocaleDateString()}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                          <div className="flex justify-end gap-2">
                            <Link
                              href={`/candidates/${candidate.id}`}
                              className="text-blue-600 hover:text-blue-900 p-1 rounded hover:bg-blue-50"
                              title="View Profile"
                            >
                              <Eye size={16} />
                            </Link>
                            <Link
                              href={`/candidates/${candidate.id}/edit`}
                              className="text-gray-600 hover:text-gray-900 p-1 rounded hover:bg-gray-50"
                              title="Edit Candidate"
                            >
                              <Edit size={16} />
                            </Link>
                            {candidate.resume_url && (
                              <a
                                href={candidate.resume_url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-green-600 hover:text-green-900 p-1 rounded hover:bg-green-50"
                                title="View Resume"
                              >
                                <Download size={16} />
                              </a>
                            )}
                            <button
                              onClick={() => handleDelete(candidate.id)}
                              className="text-red-600 hover:text-red-900 p-1 rounded hover:bg-red-50"
                              title="Delete Candidate"
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

export default function CandidatesPage() {
  return (
    <ProtectedRoute>
      <CandidatesPageContent />
    </ProtectedRoute>
  );
}
