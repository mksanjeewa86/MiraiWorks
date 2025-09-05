import React, { useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { publicApi } from '../../services/api';

interface Job {
  id: number;
  title: string;
  slug: string;
  summary?: string;
  company_name: string;
  company_logo?: string;
  location?: string;
  job_type: string;
  experience_level: string;
  remote_type: string;
  salary_range_display?: string;
  is_featured: boolean;
  is_urgent: boolean;
  published_at: string;
  days_since_published?: number;
}

interface JobSearchResponse {
  jobs: Job[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
  filters: {
    countries: string[];
    cities: string[];
    companies: Array<{ id: number; name: string }>;
    job_types: string[];
    experience_levels: string[];
    remote_types: string[];
  };
}

const JobsPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [localFilters, setLocalFilters] = useState({
    q: searchParams.get('q') || '',
    location: searchParams.get('location') || '',
    country: searchParams.get('country') || '',
    job_type: searchParams.get('job_type') || '',
    experience_level: searchParams.get('experience_level') || '',
    remote_type: searchParams.get('remote_type') || '',
    company_id: searchParams.get('company_id') || '',
    featured_only: searchParams.get('featured_only') === 'true',
    sort_by: searchParams.get('sort_by') || 'published_date',
    sort_order: searchParams.get('sort_order') || 'desc'
  });

  const page = parseInt(searchParams.get('page') || '1');

  const { data: jobData, isLoading } = useQuery({
    queryKey: ['jobs', searchParams.toString()],
    queryFn: async (): Promise<JobSearchResponse> => {
      const response = await publicApi.get('/public/jobs/search', {
        params: Object.fromEntries(searchParams)
      });
      return response.data;
    }
  });

  const handleFilterChange = (key: string, value: string | boolean) => {
    setLocalFilters(prev => ({ ...prev, [key]: value }));
  };

  const applyFilters = () => {
    const newParams = new URLSearchParams();
    Object.entries(localFilters).forEach(([key, value]) => {
      if (value && value !== '') {
        newParams.set(key, value.toString());
      }
    });
    newParams.set('page', '1');
    setSearchParams(newParams);
  };

  const clearFilters = () => {
    setLocalFilters({
      q: '',
      location: '',
      country: '',
      job_type: '',
      experience_level: '',
      remote_type: '',
      company_id: '',
      featured_only: false,
      sort_by: 'published_date',
      sort_order: 'desc'
    });
    setSearchParams(new URLSearchParams());
  };

  const handlePageChange = (newPage: number) => {
    const newParams = new URLSearchParams(searchParams);
    newParams.set('page', newPage.toString());
    setSearchParams(newParams);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">Job Search</h1>
          <p className="text-xl text-gray-600">
            {jobData ? `${jobData.total} jobs found` : 'Find your next opportunity'}
          </p>
        </div>

        <div className="flex flex-col lg:flex-row gap-8">
          {/* Filters Sidebar */}
          <div className="lg:w-1/4">
            <div className="bg-white p-6 rounded-lg shadow-md sticky top-8">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-lg font-semibold text-gray-900">Filters</h2>
                <button
                  onClick={clearFilters}
                  className="text-sm text-blue-600 hover:text-blue-800"
                >
                  Clear all
                </button>
              </div>

              <div className="space-y-4">
                {/* Search Query */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Search
                  </label>
                  <input
                    type="text"
                    value={localFilters.q}
                    onChange={(e) => handleFilterChange('q', e.target.value)}
                    placeholder="Job title, company, keywords..."
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                {/* Location */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Location
                  </label>
                  <input
                    type="text"
                    value={localFilters.location}
                    onChange={(e) => handleFilterChange('location', e.target.value)}
                    placeholder="City, country..."
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                {/* Country */}
                {jobData?.filters.countries && jobData.filters.countries.length > 0 && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Country
                    </label>
                    <select
                      value={localFilters.country}
                      onChange={(e) => handleFilterChange('country', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="">All Countries</option>
                      {jobData?.filters.countries.map(country => (
                        <option key={country} value={country}>{country}</option>
                      ))}
                    </select>
                  </div>
                )}

                {/* Job Type */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Job Type
                  </label>
                  <select
                    value={localFilters.job_type}
                    onChange={(e) => handleFilterChange('job_type', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">All Types</option>
                    {jobData?.filters.job_types.map(type => (
                      <option key={type} value={type}>
                        {type.replace('_', ' ').toUpperCase()}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Experience Level */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Experience Level
                  </label>
                  <select
                    value={localFilters.experience_level}
                    onChange={(e) => handleFilterChange('experience_level', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">All Levels</option>
                    {jobData?.filters.experience_levels.map(level => (
                      <option key={level} value={level}>
                        {level.replace('_', ' ').toUpperCase()}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Remote Type */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Work Type
                  </label>
                  <select
                    value={localFilters.remote_type}
                    onChange={(e) => handleFilterChange('remote_type', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">All Types</option>
                    {jobData?.filters.remote_types.map(type => (
                      <option key={type} value={type}>
                        {type.replace('_', ' ').toUpperCase()}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Featured Only */}
                <div>
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={localFilters.featured_only}
                      onChange={(e) => handleFilterChange('featured_only', e.target.checked)}
                      className="mr-2"
                    />
                    <span className="text-sm text-gray-700">Featured jobs only</span>
                  </label>
                </div>

                {/* Sort */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Sort by
                  </label>
                  <select
                    value={`${localFilters.sort_by}-${localFilters.sort_order}`}
                    onChange={(e) => {
                      const [sortBy, sortOrder] = e.target.value.split('-');
                      handleFilterChange('sort_by', sortBy);
                      handleFilterChange('sort_order', sortOrder);
                    }}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="published_date-desc">Newest First</option>
                    <option value="published_date-asc">Oldest First</option>
                    <option value="salary-desc">Highest Salary</option>
                    <option value="salary-asc">Lowest Salary</option>
                    <option value="company-asc">Company A-Z</option>
                  </select>
                </div>

                <button
                  onClick={applyFilters}
                  className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors"
                >
                  Apply Filters
                </button>
              </div>
            </div>
          </div>

          {/* Job Results */}
          <div className="lg:w-3/4">
            {isLoading ? (
              <div className="flex justify-center items-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
              </div>
            ) : (
              <div className="space-y-4">
                {jobData?.jobs.map(job => (
                  <div key={job.id} className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex-1">
                        <div className="flex items-center mb-2">
                          <h3 className="text-xl font-semibold text-gray-900 mr-3">
                            <Link
                              to={`/jobs/${job.slug}`}
                              className="hover:text-blue-600 transition-colors"
                            >
                              {job.title}
                            </Link>
                          </h3>
                          <div className="flex gap-2">
                            {job.is_featured && (
                              <span className="bg-yellow-100 text-yellow-800 text-xs px-2 py-1 rounded">
                                Featured
                              </span>
                            )}
                            {job.is_urgent && (
                              <span className="bg-red-100 text-red-800 text-xs px-2 py-1 rounded">
                                Urgent
                              </span>
                            )}
                          </div>
                        </div>
                        
                        <div className="flex items-center text-gray-600 mb-2">
                          <span className="font-medium">{job.company_name}</span>
                          {job.location && (
                            <>
                              <span className="mx-2">•</span>
                              <span>{job.location}</span>
                            </>
                          )}
                        </div>
                        
                        <div className="flex gap-3 text-sm text-gray-500 mb-3">
                          <span className="bg-gray-100 px-2 py-1 rounded">
                            {job.job_type.replace('_', ' ')}
                          </span>
                          <span className="bg-gray-100 px-2 py-1 rounded">
                            {job.experience_level.replace('_', ' ')}
                          </span>
                          <span className="bg-gray-100 px-2 py-1 rounded">
                            {job.remote_type.replace('_', ' ')}
                          </span>
                        </div>
                        
                        {job.summary && (
                          <p className="text-gray-700 mb-3 line-clamp-2">
                            {job.summary}
                          </p>
                        )}
                        
                        <div className="flex items-center justify-between">
                          {job.salary_range_display && (
                            <span className="text-green-600 font-medium">
                              {job.salary_range_display}
                            </span>
                          )}
                          <span className="text-sm text-gray-500">
                            {job.days_since_published !== undefined
                              ? `${job.days_since_published} days ago`
                              : new Date(job.published_at).toLocaleDateString()
                            }
                          </span>
                        </div>
                      </div>
                      
                      {job.company_logo && (
                        <img
                          src={job.company_logo}
                          alt={job.company_name}
                          className="w-16 h-16 rounded-lg object-cover ml-4"
                        />
                      )}
                    </div>
                  </div>
                ))}

                {jobData?.jobs.length === 0 && (
                  <div className="text-center py-12">
                    <div className="text-gray-500 mb-4">No jobs found matching your criteria.</div>
                    <button
                      onClick={clearFilters}
                      className="text-blue-600 hover:text-blue-800"
                    >
                      Clear filters to see all jobs
                    </button>
                  </div>
                )}

                {/* Pagination */}
                {jobData && jobData.total_pages > 1 && (
                  <div className="flex justify-center items-center space-x-2 mt-8">
                    <button
                      onClick={() => handlePageChange(page - 1)}
                      disabled={page <= 1}
                      className="px-3 py-2 rounded-md bg-white border border-gray-300 text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Previous
                    </button>
                    
                    {Array.from({ length: Math.min(5, jobData.total_pages) }, (_, i) => {
                      const pageNum = Math.max(1, Math.min(jobData.total_pages - 4, page - 2)) + i;
                      return (
                        <button
                          key={pageNum}
                          onClick={() => handlePageChange(pageNum)}
                          className={`px-3 py-2 rounded-md ${
                            pageNum === page
                              ? 'bg-blue-600 text-white'
                              : 'bg-white border border-gray-300 text-gray-700 hover:bg-gray-50'
                          }`}
                        >
                          {pageNum}
                        </button>
                      );
                    })}
                    
                    <button
                      onClick={() => handlePageChange(page + 1)}
                      disabled={page >= jobData.total_pages}
                      className="px-3 py-2 rounded-md bg-white border border-gray-300 text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Next
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default JobsPage;