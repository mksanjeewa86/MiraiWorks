import React, { useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { publicApi } from '../../services/api';

interface Company {
  id: number;
  name: string;
  domain?: string;
  website?: string;
  description?: string;
  profile?: {
    id: number;
    tagline?: string;
    logo_url?: string;
    headquarters?: string;
    employee_count?: string;
    funding_stage?: string;
    founded_year?: number;
    public_slug: string;
  };
}

interface CompanySearchResponse {
  companies: Company[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

const CompaniesPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [localFilters, setLocalFilters] = useState({
    q: searchParams.get('q') || '',
    industry: searchParams.get('industry') || '',
    location: searchParams.get('location') || '',
    employee_count: searchParams.get('employee_count') || '',
    funding_stage: searchParams.get('funding_stage') || '',
    sort_by: searchParams.get('sort_by') || 'name',
    sort_order: searchParams.get('sort_order') || 'asc'
  });

  const page = parseInt(searchParams.get('page') || '1');

  const { data: companyData, isLoading } = useQuery({
    queryKey: ['companies', searchParams.toString()],
    queryFn: async (): Promise<CompanySearchResponse> => {
      const response = await publicApi.get('/public/companies/search', {
        params: Object.fromEntries(searchParams)
      });
      return response.data;
    }
  });

  const handleFilterChange = (key: string, value: string) => {
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
      industry: '',
      location: '',
      employee_count: '',
      funding_stage: '',
      sort_by: 'name',
      sort_order: 'asc'
    });
    setSearchParams(new URLSearchParams());
  };

  const handlePageChange = (newPage: number) => {
    const newParams = new URLSearchParams(searchParams);
    newParams.set('page', newPage.toString());
    setSearchParams(newParams);
  };

  const employeeCountOptions = [
    { value: '1-10', label: '1-10 employees' },
    { value: '11-50', label: '11-50 employees' },
    { value: '51-200', label: '51-200 employees' },
    { value: '201-500', label: '201-500 employees' },
    { value: '501-1000', label: '501-1000 employees' },
    { value: '1000+', label: '1000+ employees' }
  ];

  const fundingStageOptions = [
    { value: 'pre_seed', label: 'Pre-seed' },
    { value: 'seed', label: 'Seed' },
    { value: 'series_a', label: 'Series A' },
    { value: 'series_b', label: 'Series B' },
    { value: 'series_c', label: 'Series C' },
    { value: 'public', label: 'Public' },
    { value: 'acquired', label: 'Acquired' }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">Companies</h1>
          <p className="text-xl text-gray-600">
            {companyData ? `${companyData.total} companies found` : 'Discover innovative companies'}
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
                    placeholder="Company name, description..."
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

                {/* Industry */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Industry
                  </label>
                  <input
                    type="text"
                    value={localFilters.industry}
                    onChange={(e) => handleFilterChange('industry', e.target.value)}
                    placeholder="Technology, Finance..."
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                {/* Employee Count */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Company Size
                  </label>
                  <select
                    value={localFilters.employee_count}
                    onChange={(e) => handleFilterChange('employee_count', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">All Sizes</option>
                    {employeeCountOptions.map(option => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Funding Stage */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Funding Stage
                  </label>
                  <select
                    value={localFilters.funding_stage}
                    onChange={(e) => handleFilterChange('funding_stage', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">All Stages</option>
                    {fundingStageOptions.map(option => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
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
                    <option value="name-asc">Name A-Z</option>
                    <option value="name-desc">Name Z-A</option>
                    <option value="founded_year-desc">Newest First</option>
                    <option value="founded_year-asc">Oldest First</option>
                    <option value="employee_count-desc">Largest First</option>
                    <option value="employee_count-asc">Smallest First</option>
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

          {/* Company Results */}
          <div className="lg:w-3/4">
            {isLoading ? (
              <div className="flex justify-center items-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
              </div>
            ) : (
              <div className="space-y-4">
                {companyData?.companies.map(company => (
                  <div key={company.id} className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow">
                    <div className="flex items-start gap-6">
                      {/* Company Logo */}
                      <div className="flex-shrink-0">
                        {company.profile?.logo_url ? (
                          <img
                            src={company.profile.logo_url}
                            alt={company.name}
                            className="w-20 h-20 rounded-lg object-cover"
                          />
                        ) : (
                          <div className="w-20 h-20 bg-gray-200 rounded-lg flex items-center justify-center">
                            <span className="text-gray-500 font-semibold text-2xl">
                              {company.name.charAt(0)}
                            </span>
                          </div>
                        )}
                      </div>
                      
                      {/* Company Info */}
                      <div className="flex-1">
                        <div className="flex items-start justify-between mb-2">
                          <h3 className="text-xl font-semibold text-gray-900">
                            <Link
                              to={`/companies/${company.profile?.public_slug || company.domain}`}
                              className="hover:text-blue-600 transition-colors"
                            >
                              {company.name}
                            </Link>
                          </h3>
                          
                          {company.website && (
                            <a
                              href={company.website}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-blue-600 hover:text-blue-800 text-sm"
                            >
                              Visit Website →
                            </a>
                          )}
                        </div>
                        
                        {company.profile?.tagline && (
                          <p className="text-gray-600 mb-3 font-medium">
                            {company.profile.tagline}
                          </p>
                        )}
                        
                        {company.description && (
                          <p className="text-gray-700 mb-4 line-clamp-2">
                            {company.description}
                          </p>
                        )}
                        
                        <div className="flex flex-wrap gap-4 text-sm text-gray-500">
                          {company.profile?.headquarters && (
                            <span className="flex items-center">
                              📍 {company.profile.headquarters}
                            </span>
                          )}
                          
                          {company.profile?.employee_count && (
                            <span className="flex items-center">
                              👥 {company.profile.employee_count} employees
                            </span>
                          )}
                          
                          {company.profile?.funding_stage && (
                            <span className="flex items-center">
                              💰 {company.profile.funding_stage.replace('_', ' ')}
                            </span>
                          )}
                          
                          {company.profile?.founded_year && (
                            <span className="flex items-center">
                              📅 Founded {company.profile.founded_year}
                            </span>
                          )}
                        </div>
                        
                        <div className="mt-4 pt-4 border-t border-gray-200 flex justify-between items-center">
                          <Link
                            to={`/companies/${company.profile?.public_slug || company.domain}`}
                            className="text-blue-600 hover:text-blue-800 font-medium"
                          >
                            View Company Profile
                          </Link>
                          
                          <Link
                            to={`/companies/${company.profile?.public_slug || company.domain}/jobs`}
                            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors text-sm"
                          >
                            View Jobs
                          </Link>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}

                {companyData?.companies.length === 0 && (
                  <div className="text-center py-12">
                    <div className="text-gray-500 mb-4">No companies found matching your criteria.</div>
                    <button
                      onClick={clearFilters}
                      className="text-blue-600 hover:text-blue-800"
                    >
                      Clear filters to see all companies
                    </button>
                  </div>
                )}

                {/* Pagination */}
                {companyData && companyData.total_pages > 1 && (
                  <div className="flex justify-center items-center space-x-2 mt-8">
                    <button
                      onClick={() => handlePageChange(page - 1)}
                      disabled={page <= 1}
                      className="px-3 py-2 rounded-md bg-white border border-gray-300 text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Previous
                    </button>
                    
                    {Array.from({ length: Math.min(5, companyData.total_pages) }, (_, i) => {
                      const pageNum = Math.max(1, Math.min(companyData.total_pages - 4, page - 2)) + i;
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
                      disabled={page >= companyData.total_pages}
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

export default CompaniesPage;