'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import WebsiteLayout from '@/components/website/WebsiteLayout';
import { positionsApi } from "@/api/positions";
import { PREFECTURES } from '@/utils/prefectures';
import type { Position } from '@/types';

function PositionsPageContent() {
  const [positions, setPositions] = useState<Position[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedType, setSelectedType] = useState('all');
  const [selectedPrefecture, setSelectedPrefecture] = useState('all');
  const [selectedSalaryRange, setSelectedSalaryRange] = useState('all');
  const [selectedDateFilter, setSelectedDateFilter] = useState('all');

  // Pagination state
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPositions, setTotalPositions] = useState(0);
  const [, setHasMore] = useState(false);
  const positionsPerPage = 12; // Show 12 positions per page for nice grid layout

  // Set page title
  useEffect(() => {
    document.title = 'Positions - MiraiWorks';
  }, []);

  // Fetch positions from API
  useEffect(() => {
    const fetchPositions = async () => {
      try {
        setLoading(true);
        setError('');

        // Parse salary range
        let salary_min, salary_max;
        if (selectedSalaryRange !== 'all') {
          if (selectedSalaryRange === '15000000+') {
            salary_min = 15000000;
          } else {
            const [min, max] = selectedSalaryRange.split('-').map(Number);
            salary_min = min;
            salary_max = max;
          }
        }

        const filters = {
          department: selectedCategory !== 'all' ? selectedCategory : undefined,
          job_type: selectedType !== 'all' ? selectedType : undefined,
          location: selectedPrefecture !== 'all' ? selectedPrefecture : undefined,
          salary_min: salary_min,
          salary_max: salary_max,
          days_since_posted: selectedDateFilter !== 'all' ? parseInt(selectedDateFilter) : undefined,
          search: searchQuery || undefined,
          limit: positionsPerPage,
          skip: (currentPage - 1) * positionsPerPage
        };

        const response = await positionsApi.getPublic(filters);
        setPositions(response.data?.positions || []);
        setTotalPositions(response.data?.total || 0);
        setHasMore(response.data?.has_more || false);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch positions');
        console.error('Failed to fetch positions:', err);
        // Fallback to empty array on error
        setPositions([]);
        setTotalPositions(0);
        setHasMore(false);
      } finally {
        setLoading(false);
      }
    };

    fetchPositions();
  }, [searchQuery, selectedCategory, selectedType, selectedPrefecture, selectedSalaryRange, selectedDateFilter, currentPage]);

  // Reset to first page when filters change
  useEffect(() => {
    setCurrentPage(1);
  }, [searchQuery, selectedCategory, selectedType, selectedPrefecture, selectedSalaryRange, selectedDateFilter]);

  const categories = [
    { value: 'all', label: 'All Categories' },
    { value: 'technology', label: 'Technology' },
    { value: 'marketing', label: 'Marketing' },
    { value: 'design', label: 'Design' },
    { value: 'sales', label: 'Sales' },
    { value: 'finance', label: 'Finance' },
    { value: 'healthcare', label: 'Healthcare' }
  ];

  const jobTypes = [
    { value: 'all', label: 'All Types' },
    { value: 'full_time', label: 'Full-time' },
    { value: 'part_time', label: 'Part-time' },
    { value: 'contract', label: 'Contract' },
    { value: 'temporary', label: 'Temporary' },
    { value: 'internship', label: 'Internship' },
    { value: 'freelance', label: 'Freelance' }
  ];

  const prefectureOptions = [
    { value: 'all', label: 'All Locations' },
    ...PREFECTURES.map(pref => ({
      value: pref.nameJa,
      label: `${pref.nameEn} (${pref.nameJa})`
    })),
    { value: 'リモート', label: 'Remote' }
  ];

  const salaryRanges = [
    { value: 'all', label: 'Any Salary' },
    { value: '3000000-5000000', label: '¥3M - ¥5M' },
    { value: '5000000-7000000', label: '¥5M - ¥7M' },
    { value: '7000000-10000000', label: '¥7M - ¥10M' },
    { value: '10000000-15000000', label: '¥10M - ¥15M' },
    { value: '15000000+', label: '¥15M+' }
  ];

  const dateFilters = [
    { value: 'all', label: 'Any Time' },
    { value: '1', label: 'Last 24 hours' },
    { value: '3', label: 'Last 3 days' },
    { value: '7', label: 'Last week' },
    { value: '30', label: 'Last month' }
  ];

  // Calculate pagination info
  const totalPages = Math.ceil(totalPositions / positionsPerPage);
  const startPosition = (currentPage - 1) * positionsPerPage + 1;
  const endPosition = Math.min(currentPage * positionsPerPage, totalPositions);

  const getPositionTypeColor = (type: string) => {
    switch (type) {
      case 'full_time': return 'bg-green-100 text-green-800';
      case 'part_time': return 'bg-blue-100 text-blue-800';
      case 'contract': return 'bg-purple-100 text-purple-800';
      case 'temporary': return 'bg-orange-100 text-orange-800';
      case 'internship': return 'bg-pink-100 text-pink-800';
      case 'freelance': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <WebsiteLayout>
      {/* Hero Section */}
      <section className="py-24 bg-gradient-to-br from-slate-900 via-indigo-900 to-slate-900 relative overflow-hidden">
        {/* Background Pattern */}
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiM5Q0EzQUYiIGZpbGwtb3BhY2l0eT0iMC4xIj48Y2lyY2xlIGN4PSIzMCIgY3k9IjMwIiByPSI0Ii8+PC9nPjwvZz48L3N2Zz4=')] opacity-30"></div>

        {/* Floating Elements */}
        <div className="absolute top-20 left-10 w-64 h-64 bg-indigo-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-float"></div>
        <div className="absolute bottom-20 right-10 w-64 h-64 bg-purple-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-float animation-delay-2000"></div>

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12 animate-fade-in-up">
            <span className="inline-block px-4 py-2 text-sm font-semibold text-indigo-300 bg-indigo-500/20 rounded-full mb-8">
              Browse Jobs
            </span>
            <h1 className="text-5xl md:text-6xl font-bold text-white mb-8">
              Find Your
              <span className="block bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
                Dream Job
              </span>
            </h1>
            <p className="text-xl md:text-2xl text-indigo-100 max-w-4xl mx-auto leading-relaxed">
              Discover thousands of opportunities from top companies in Japan.
              Filter by prefecture, salary range, posting date and more - no account required to explore!
            </p>
          </div>

          {/* Search and Filters */}
          <div className="group relative">
            <div className="absolute inset-0 bg-gradient-to-r from-indigo-400 to-purple-400 rounded-3xl blur-lg opacity-25 group-hover:opacity-40 transition duration-1000 group-hover:duration-200"></div>
            <div className="relative bg-white/10 backdrop-blur-sm rounded-3xl p-8 border border-white/20 shadow-2xl">
              {/* Main Search Bar */}
              <div className="mb-6">
                <input
                  type="text"
                  placeholder="Search jobs, companies, or skills..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full px-6 py-4 border-2 border-white/30 rounded-2xl focus:ring-2 focus:ring-indigo-400 focus:border-indigo-400 bg-white/20 backdrop-blur-sm text-white placeholder-white/70 font-medium transition-all duration-300"
                />
              </div>

              {/* Filter Dropdowns */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
                <div>
                  <select
                    value={selectedCategory}
                    onChange={(e) => setSelectedCategory(e.target.value)}
                    className="w-full px-4 py-3 border-2 border-white/30 rounded-xl focus:ring-2 focus:ring-indigo-400 focus:border-indigo-400 appearance-none bg-white/20 backdrop-blur-sm text-white font-medium transition-all duration-300 text-sm"
                    style={{
                      backgroundImage: `url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%23ffffff' stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M6 8l4 4 4-4'/%3e%3c/svg%3e")`,
                      backgroundPosition: 'right 12px center',
                      backgroundRepeat: 'no-repeat',
                      backgroundSize: '16px'
                    }}
                  >
                    {categories.map(category => (
                      <option key={category.value} value={category.value} className="text-gray-900">
                        {category.label}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <select
                    value={selectedType}
                    onChange={(e) => setSelectedType(e.target.value)}
                    className="w-full px-4 py-3 border-2 border-white/30 rounded-xl focus:ring-2 focus:ring-indigo-400 focus:border-indigo-400 appearance-none bg-white/20 backdrop-blur-sm text-white font-medium transition-all duration-300 text-sm"
                    style={{
                      backgroundImage: `url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%23ffffff' stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M6 8l4 4 4-4'/%3e%3c/svg%3e")`,
                      backgroundPosition: 'right 12px center',
                      backgroundRepeat: 'no-repeat',
                      backgroundSize: '16px'
                    }}
                  >
                    {jobTypes.map(type => (
                      <option key={type.value} value={type.value} className="text-gray-900">
                        {type.label}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <select
                    value={selectedPrefecture}
                    onChange={(e) => setSelectedPrefecture(e.target.value)}
                    className="w-full px-4 py-3 border-2 border-white/30 rounded-xl focus:ring-2 focus:ring-indigo-400 focus:border-indigo-400 appearance-none bg-white/20 backdrop-blur-sm text-white font-medium transition-all duration-300 text-sm"
                    style={{
                      backgroundImage: `url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%23ffffff' stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M6 8l4 4 4-4'/%3e%3c/svg%3e")`,
                      backgroundPosition: 'right 12px center',
                      backgroundRepeat: 'no-repeat',
                      backgroundSize: '16px'
                    }}
                  >
                    {prefectureOptions.map(prefecture => (
                      <option key={prefecture.value} value={prefecture.value} className="text-gray-900">
                        {prefecture.label}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <select
                    value={selectedSalaryRange}
                    onChange={(e) => setSelectedSalaryRange(e.target.value)}
                    className="w-full px-4 py-3 border-2 border-white/30 rounded-xl focus:ring-2 focus:ring-indigo-400 focus:border-indigo-400 appearance-none bg-white/20 backdrop-blur-sm text-white font-medium transition-all duration-300 text-sm"
                    style={{
                      backgroundImage: `url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%23ffffff' stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M6 8l4 4 4-4'/%3e%3c/svg%3e")`,
                      backgroundPosition: 'right 12px center',
                      backgroundRepeat: 'no-repeat',
                      backgroundSize: '16px'
                    }}
                  >
                    {salaryRanges.map(range => (
                      <option key={range.value} value={range.value} className="text-gray-900">
                        {range.label}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <select
                    value={selectedDateFilter}
                    onChange={(e) => setSelectedDateFilter(e.target.value)}
                    className="w-full px-4 py-3 border-2 border-white/30 rounded-xl focus:ring-2 focus:ring-indigo-400 focus:border-indigo-400 appearance-none bg-white/20 backdrop-blur-sm text-white font-medium transition-all duration-300 text-sm"
                    style={{
                      backgroundImage: `url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%23ffffff' stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M6 8l4 4 4-4'/%3e%3c/svg%3e")`,
                      backgroundPosition: 'right 12px center',
                      backgroundRepeat: 'no-repeat',
                      backgroundSize: '16px'
                    }}
                  >
                    {dateFilters.map(filter => (
                      <option key={filter.value} value={filter.value} className="text-gray-900">
                        {filter.label}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Positions List */}
      <section className="py-12 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Active Filters Summary */}
          {(selectedCategory !== 'all' || selectedType !== 'all' || selectedPrefecture !== 'all' || selectedSalaryRange !== 'all' || selectedDateFilter !== 'all' || searchQuery) && (
            <div className="mb-6 p-4 bg-indigo-50 rounded-xl border border-indigo-200">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-sm font-semibold text-indigo-900">Active Filters:</h3>
                <button
                  onClick={() => {
                    setSearchQuery('');
                    setSelectedCategory('all');
                    setSelectedType('all');
                    setSelectedPrefecture('all');
                    setSelectedSalaryRange('all');
                    setSelectedDateFilter('all');
                  }}
                  className="text-xs font-medium text-indigo-600 hover:text-indigo-800 transition-colors duration-200"
                >
                  Clear All
                </button>
              </div>
              <div className="flex flex-wrap gap-2">
                {searchQuery && (
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800">
                    Search: &ldquo;{searchQuery}&rdquo;
                    <button
                      onClick={() => setSearchQuery('')}
                      className="ml-1 text-indigo-600 hover:text-indigo-800"
                    >
                      ×
                    </button>
                  </span>
                )}
                {selectedCategory !== 'all' && (
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800">
                    Category: {categories.find(c => c.value === selectedCategory)?.label}
                    <button
                      onClick={() => setSelectedCategory('all')}
                      className="ml-1 text-indigo-600 hover:text-indigo-800"
                    >
                      ×
                    </button>
                  </span>
                )}
                {selectedType !== 'all' && (
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800">
                    Type: {jobTypes.find(t => t.value === selectedType)?.label}
                    <button
                      onClick={() => setSelectedType('all')}
                      className="ml-1 text-indigo-600 hover:text-indigo-800"
                    >
                      ×
                    </button>
                  </span>
                )}
                {selectedPrefecture !== 'all' && (
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800">
                    Location: {prefectureOptions.find(p => p.value === selectedPrefecture)?.label}
                    <button
                      onClick={() => setSelectedPrefecture('all')}
                      className="ml-1 text-indigo-600 hover:text-indigo-800"
                    >
                      ×
                    </button>
                  </span>
                )}
                {selectedSalaryRange !== 'all' && (
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800">
                    Salary: {salaryRanges.find(s => s.value === selectedSalaryRange)?.label}
                    <button
                      onClick={() => setSelectedSalaryRange('all')}
                      className="ml-1 text-indigo-600 hover:text-indigo-800"
                    >
                      ×
                    </button>
                  </span>
                )}
                {selectedDateFilter !== 'all' && (
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800">
                    Posted: {dateFilters.find(d => d.value === selectedDateFilter)?.label}
                    <button
                      onClick={() => setSelectedDateFilter('all')}
                      className="ml-1 text-indigo-600 hover:text-indigo-800"
                    >
                      ×
                    </button>
                  </span>
                )}
              </div>
            </div>
          )}

          {/* Results Header */}
          <div className="flex items-center justify-between mb-8">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">
                {loading ? 'Loading...' : `${totalPositions} Position${totalPositions !== 1 ? 's' : ''} Found`}
              </h2>
              {!loading && totalPositions > 0 && (
                <p className="text-gray-600 mt-1">
                  Showing {startPosition}-{endPosition} of {totalPositions} results
                </p>
              )}
            </div>

            {/* Page Info */}
            {!loading && totalPages > 1 && (
              <div className="text-sm text-gray-500">
                Page {currentPage} of {totalPages}
              </div>
            )}
          </div>

          {/* Loading State */}
          {loading && (
            <div className="text-center py-16">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
              <p className="text-gray-600">Loading positions...</p>
            </div>
          )}

          {/* Error State */}
          {error && (
            <div className="text-center py-16">
              <div className="text-6xl mb-4">❌</div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">Error Loading Positions</h3>
              <p className="text-red-600 mb-6">{error}</p>
              <button
                onClick={() => window.location.reload()}
                className="px-6 py-3 font-medium rounded-lg text-white transition-colors bg-indigo-600 hover:bg-indigo-700"
              >
                Try Again
              </button>
            </div>
          )}

          {/* Job Cards Grid */}
          {!loading && !error && positions.length > 0 && (
            <>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
                {positions.map(job => (
                  <div
                    key={job.id}
                    className={`bg-white rounded-xl shadow-sm border hover:shadow-lg transition-all duration-300 p-6 ${
                      job.is_featured ? 'ring-2 ring-indigo-500 border-indigo-200' : 'border-gray-200'
                    }`}
                  >
                    {/* Card Header */}
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex-1">
                        <h3 className="text-lg font-semibold text-gray-900 mb-2 overflow-hidden" style={{ display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical' }}>
                          {job.title}
                        </h3>
                        <p className="text-sm text-indigo-600 font-medium">
                          {job.company_name || 'Unknown Company'}
                        </p>
                      </div>
                      {job.is_featured && (
                        <span className="px-2 py-1 text-xs font-medium bg-yellow-100 text-yellow-800 rounded-full">
                          Featured
                        </span>
                      )}
                    </div>

                    {/* Location and Job Type */}
                    <div className="flex items-center gap-4 mb-3 text-sm text-gray-600">
                      <span className="flex items-center gap-1">
                        📍 {job.location || 'Remote'}
                      </span>
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${getPositionTypeColor(job.job_type)}`}>
                        {job.job_type.replace('_', ' ')}
                      </span>
                    </div>

                    {/* Salary */}
                    {job.salary_min && job.salary_max && job.show_salary && (
                      <div className="mb-3">
                        <span className="text-sm font-medium text-green-600">
                          $${(job.salary_min / 100).toLocaleString()} - $${(job.salary_max / 100).toLocaleString()}
                        </span>
                        <span className="text-xs text-gray-500 ml-1">/ year</span>
                      </div>
                    )}

                    {/* Description */}
                    <p className="text-sm text-gray-600 mb-4 overflow-hidden" style={{ display: '-webkit-box', WebkitLineClamp: 3, WebkitBoxOrient: 'vertical' }}>
                      {job.description}
                    </p>

                    {/* Skills */}
                    <div className="flex flex-wrap gap-1 mb-4">
                      {job.required_skills?.slice(0, 3).map((skill: string, index: number) => (
                        <span
                          key={index}
                          className="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded-md"
                        >
                          {skill}
                        </span>
                      ))}
                      {(job.required_skills?.length || 0) > 3 && (
                        <span className="px-2 py-1 text-xs bg-gray-100 text-gray-500 rounded-md">
                          +{(job.required_skills?.length || 0) - 3}
                        </span>
                      )}
                    </div>

                    {/* Actions */}
                    <div className="flex gap-2 pt-4 border-t border-gray-100">
                      <Link
                        href="/auth/register"
                        className="w-full px-3 py-2 text-sm font-medium text-center text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg transition-colors"
                      >
                        Apply
                      </Link>
                    </div>

                    {/* Posted Date */}
                    <div className="mt-3 pt-3 border-t border-gray-100">
                      <span className="text-xs text-gray-500">
                        Posted {(() => {
                          const dateStr = job.published_at || job.created_at;
                          if (!dateStr) return 'Recently';
                          try {
                            const date = new Date(dateStr);
                            return isNaN(date.getTime()) ? 'Recently' : date.toLocaleDateString();
                          } catch {
                            return 'Recently';
                          }
                        })()}
                      </span>
                    </div>
                  </div>
                ))}
              </div>

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="flex items-center justify-center gap-2">
                  <button
                    onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                    disabled={currentPage <= 1}
                    className="px-3 py-2 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Previous
                  </button>

                  {/* Page Numbers */}
                  {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                    let pageNum = i + 1;
                    if (totalPages > 5) {
                      if (currentPage <= 3) {
                        pageNum = i + 1;
                      } else if (currentPage >= totalPages - 2) {
                        pageNum = totalPages - 4 + i;
                      } else {
                        pageNum = currentPage - 2 + i;
                      }
                    }

                    return (
                      <button
                        key={pageNum}
                        onClick={() => setCurrentPage(pageNum)}
                        className={`px-3 py-2 text-sm font-medium rounded-md ${
                          currentPage === pageNum
                            ? 'text-white bg-indigo-600'
                            : 'text-gray-700 bg-white border border-gray-300 hover:bg-gray-50'
                        }`}
                      >
                        {pageNum}
                      </button>
                    );
                  })}

                  <button
                    onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                    disabled={currentPage >= totalPages}
                    className="px-3 py-2 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Next
                  </button>
                </div>
              )}
            </>
          )}

          {/* Empty State */}
          {!loading && !error && positions.length === 0 && (
            <div className="text-center py-16">
              <div className="text-6xl mb-4">🔍</div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">No positions found</h3>
              <p className="text-gray-600 mb-6">
                Try adjusting your search criteria or browse all categories
              </p>
              <button
                onClick={() => {
                  setSearchQuery('');
                  setSelectedCategory('all');
                  setSelectedType('all');
                }}
                className="px-6 py-3 font-medium rounded-lg text-white transition-colors bg-indigo-600 hover:bg-indigo-700"
              >
                Clear Filters
              </button>
            </div>
          )}
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 bg-gray-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold text-white mb-4">
            Don&apos;t See the Right Position?
          </h2>
          <p className="text-xl text-gray-300 mb-8">
            Create a profile and let employers find you, or set up job alerts to never miss an opportunity.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/auth/register"
              className="inline-flex items-center px-8 py-3 text-lg font-medium rounded-md text-white shadow-lg transition-colors"
              style={{ backgroundColor: 'var(--brand-primary)' }}
            >
              Create Profile
            </Link>
            <button className="inline-flex items-center px-8 py-3 text-lg font-medium rounded-md border border-gray-600 text-gray-300 bg-transparent hover:bg-gray-800 transition-colors">
              Set Up Position Alerts
            </button>
          </div>
        </div>
      </section>
    </WebsiteLayout>
  );
}

export default function PositionsPage() {
  return <PositionsPageContent />;
}