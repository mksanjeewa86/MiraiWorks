'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import AppLayout from '@/components/layout/AppLayout';
import { positionsApi } from "@/api/positions";
import type { Position } from '@/types';
import ProtectedRoute from '@/components/auth/ProtectedRoute';

function PositionsPageContent() {
  const [positions, setPositions] = useState<Position[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedType, setSelectedType] = useState('all');

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
        
        const filters = {
          department: selectedCategory !== 'all' ? selectedCategory : undefined,
          job_type: selectedType !== 'all' ? selectedType : undefined,
          search: searchQuery || undefined,
          limit: 50
        };
        
        const response = await positionsApi.getPublic(filters);
        setPositions(response.data?.positions || response.data?.positions || []);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch positions');
        console.error('Failed to fetch positions:', err);
        // Fallback to empty array on error
        setPositions([]);
      } finally {
        setLoading(false);
      }
    };

    fetchPositions();
  }, [searchQuery, selectedCategory, selectedType]);

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

  // Positions are already filtered by the API based on search, category, and type
  const filteredPositions = positions;

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
    <AppLayout>
      {/* Hero Section */}
      <section className="py-16 bg-gradient-to-br from-blue-50 via-white to-purple-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-8">
            <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
              Find Your Next Position
            </h1>
            <p className="text-xl text-gray-600">
              Discover thousands of job opportunities from top companies
            </p>
          </div>

          {/* Search and Filters */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="md:col-span-2">
                <input
                  type="text"
                  placeholder="Search positions, companies, or locations..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full px-4 py-3 pr-8 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div>
                <select
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  className="w-full px-4 py-3 pr-8 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  {categories.map(category => (
                    <option key={category.value} value={category.value}>
                      {category.label}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <select
                  value={selectedType}
                  onChange={(e) => setSelectedType(e.target.value)}
                  className="w-full px-4 py-3 pr-8 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  {jobTypes.map(type => (
                    <option key={type.value} value={type.value}>
                      {type.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Positions List */}
      <section className="py-12 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between mb-8">
            <h2 className="text-2xl font-bold text-gray-900">
              {filteredPositions.length} Position{filteredPositions.length !== 1 ? 's' : ''} Found
            </h2>
            <p className="text-gray-600">
              Showing results for your search criteria
            </p>
          </div>

          {loading && (
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-gray-600">Loading positions...</p>
            </div>
          )}

          {error && (
            <div className="text-center py-12">
              <div className="text-6xl mb-4">❌</div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">Error Loading Positions</h3>
              <p className="text-red-600 mb-6">{error}</p>
              <button
                onClick={() => window.location.reload()}
                className="px-6 py-3 font-medium rounded-lg text-white transition-colors"
                style={{ backgroundColor: 'var(--brand-primary)' }}
              >
                Try Again
              </button>
            </div>
          )}

          {!loading && !error && (
            <div className="space-y-6">
              {filteredPositions.map(job => (
              <div 
                key={job.id} 
                className={`bg-white rounded-lg border shadow-sm hover:shadow-md transition-shadow p-6 ${
                  job.is_featured ? 'ring-2 ring-blue-200 border-blue-200' : 'border-gray-200'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-xl font-bold text-gray-900">
                        {job.title}
                      </h3>
                      {job.is_featured && (
                        <span className="px-2 py-1 text-xs font-medium bg-yellow-100 text-yellow-800 rounded-full">
                          Featured
                        </span>
                      )}
                    </div>
                    
                    <div className="flex flex-wrap items-center gap-4 mb-3 text-sm text-gray-600">
                      <span className="font-medium text-blue-600">{job.company_name || 'Unknown Company'}</span>
                      <span>📍 {job.location || 'Location not specified'}</span>
                      {job.salary_min && job.salary_max && (
                        <span>💰 ¥{(job.salary_min / 10000).toFixed(0)}万 - ¥{(job.salary_max / 10000).toFixed(0)}万</span>
                      )}
                      <span>📅 Posted {new Date(job.published_at || job.created_at || '').toLocaleDateString()}</span>
                    </div>

                    <p className="text-gray-600 mb-4">
                      {job.description}
                    </p>

                    <div className="flex flex-wrap gap-2 mb-4">
                      {job.required_skills?.slice(0, 3).map((req: string, index: number) => (
                        <span
                          key={index}
                          className="px-3 py-1 text-xs font-medium bg-gray-100 text-gray-700 rounded-full"
                        >
                          {req}
                        </span>
                      ))}
                      {(job.required_skills?.length || 0) > 3 && (
                        <span className="px-3 py-1 text-xs font-medium bg-gray-100 text-gray-700 rounded-full">
                          +{(job.required_skills?.length || 0) - 3} more
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="flex flex-col items-end gap-3 ml-6">
                    <span className={`px-3 py-1 text-xs font-medium rounded-full ${getPositionTypeColor(job.job_type)}`}>
                      {job.job_type.replace('_', ' ').toUpperCase()}
                    </span>
                    
                    <div className="flex flex-col sm:flex-row gap-2">
                      <button className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors">
                        Save Position
                      </button>
                      <Link
                        href="/auth/login"
                        className="px-4 py-2 text-sm font-medium text-white rounded-lg transition-colors"
                        style={{ backgroundColor: 'var(--brand-primary)' }}
                      >
                        Apply Now
                      </Link>
                    </div>
                  </div>
                </div>
              </div>
            ))}
            </div>
          )}

          {!loading && !error && filteredPositions.length === 0 && (
            <div className="text-center py-12">
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
                className="px-6 py-3 font-medium rounded-lg text-white transition-colors"
                style={{ backgroundColor: 'var(--brand-primary)' }}
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
    </AppLayout>
  );
}

export default function PositionsPage() {
  return (
    <ProtectedRoute>
      <PositionsPageContent />
    </ProtectedRoute>
  );
}