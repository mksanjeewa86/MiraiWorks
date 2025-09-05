import React from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { publicApi } from '../../services/api';

interface PublicStats {
  total_companies: number;
  total_jobs: number;
  total_applications: number;
  featured_companies: Array<{
    id: number;
    name: string;
    domain: string;
    description: string;
    profile?: {
      logo_url?: string;
      tagline?: string;
      public_slug: string;
    };
  }>;
  latest_jobs: Array<{
    id: number;
    title: string;
    slug: string;
    summary: string;
    company_name: string;
    company_logo?: string;
    location: string;
    job_type: string;
    is_featured: boolean;
    published_at: string;
  }>;
  job_categories: Record<string, number>;
  location_stats: Record<string, number>;
}

const LandingPage: React.FC = () => {
  const { data: stats, isLoading } = useQuery({
    queryKey: ['public-stats'],
    queryFn: async (): Promise<PublicStats> => {
      const response = await publicApi.get('/public/stats');
      return response.data;
    }
  });

  const { data: featuredJobs } = useQuery({
    queryKey: ['featured-jobs'],
    queryFn: async () => {
      const response = await publicApi.get('/public/jobs?limit=6&featured_only=true');
      return response.data;
    }
  });

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white">
      {/* Hero Section */}
      <section className="relative bg-gradient-to-r from-blue-600 to-purple-700 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
          <div className="text-center">
            <h1 className="text-4xl md:text-6xl font-bold mb-6">
              Find Your Dream Job in Japan
            </h1>
            <p className="text-xl md:text-2xl mb-8 text-blue-100">
              Connect with top companies and build your future career
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                to="/jobs"
                className="bg-white text-blue-600 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors"
              >
                Browse Jobs
              </Link>
              <Link
                to="/companies"
                className="bg-transparent border-2 border-white text-white px-8 py-3 rounded-lg font-semibold hover:bg-white hover:text-blue-600 transition-colors"
              >
                Explore Companies
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-center">
            <div className="bg-white p-8 rounded-lg shadow-md">
              <div className="text-3xl font-bold text-blue-600 mb-2">
                {stats?.total_jobs.toLocaleString()}
              </div>
              <div className="text-gray-600">Active Jobs</div>
            </div>
            <div className="bg-white p-8 rounded-lg shadow-md">
              <div className="text-3xl font-bold text-blue-600 mb-2">
                {stats?.total_companies.toLocaleString()}
              </div>
              <div className="text-gray-600">Companies</div>
            </div>
            <div className="bg-white p-8 rounded-lg shadow-md">
              <div className="text-3xl font-bold text-blue-600 mb-2">
                {stats?.total_applications.toLocaleString()}
              </div>
              <div className="text-gray-600">Applications Submitted</div>
            </div>
          </div>
        </div>
      </section>

      {/* Featured Jobs */}
      <section className="py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Featured Jobs
            </h2>
            <p className="text-xl text-gray-600">
              Discover opportunities from top companies
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
            {featuredJobs?.slice(0, 6).map((job: any) => (
              <div key={job.id} className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h3 className="font-semibold text-lg text-gray-900 mb-2">
                      <Link
                        to={`/jobs/${job.slug}`}
                        className="hover:text-blue-600 transition-colors"
                      >
                        {job.title}
                      </Link>
                    </h3>
                    <p className="text-gray-600 mb-2">{job.company_name}</p>
                    <p className="text-sm text-gray-500">{job.location}</p>
                  </div>
                  {job.company_logo && (
                    <img
                      src={job.company_logo}
                      alt={job.company_name}
                      className="w-12 h-12 rounded-lg object-cover"
                    />
                  )}
                </div>
                
                {job.summary && (
                  <p className="text-gray-700 mb-4 text-sm line-clamp-2">
                    {job.summary}
                  </p>
                )}
                
                <div className="flex items-center justify-between">
                  <span className="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">
                    {job.job_type.replace('_', ' ')}
                  </span>
                  {job.is_featured && (
                    <span className="inline-block bg-yellow-100 text-yellow-800 text-xs px-2 py-1 rounded">
                      Featured
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
          
          <div className="text-center">
            <Link
              to="/jobs"
              className="bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
            >
              View All Jobs
            </Link>
          </div>
        </div>
      </section>

      {/* Featured Companies */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Featured Companies
            </h2>
            <p className="text-xl text-gray-600">
              Join innovative companies shaping the future
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
            {stats?.featured_companies?.slice(0, 6).map((company) => (
              <div key={company.id} className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow">
                <div className="flex items-center mb-4">
                  {company.profile?.logo_url ? (
                    <img
                      src={company.profile.logo_url}
                      alt={company.name}
                      className="w-16 h-16 rounded-lg object-cover mr-4"
                    />
                  ) : (
                    <div className="w-16 h-16 bg-gray-200 rounded-lg mr-4 flex items-center justify-center">
                      <span className="text-gray-500 font-semibold text-lg">
                        {company.name.charAt(0)}
                      </span>
                    </div>
                  )}
                  <div className="flex-1">
                    <h3 className="font-semibold text-lg text-gray-900">
                      <Link
                        to={`/companies/${company.profile?.public_slug || company.domain}`}
                        className="hover:text-blue-600 transition-colors"
                      >
                        {company.name}
                      </Link>
                    </h3>
                    {company.profile?.tagline && (
                      <p className="text-sm text-gray-600">{company.profile.tagline}</p>
                    )}
                  </div>
                </div>
                
                {company.description && (
                  <p className="text-gray-700 text-sm line-clamp-3">
                    {company.description}
                  </p>
                )}
              </div>
            ))}
          </div>
          
          <div className="text-center">
            <Link
              to="/companies"
              className="bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
            >
              View All Companies
            </Link>
          </div>
        </div>
      </section>

      {/* Job Categories */}
      <section className="py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Browse by Category
            </h2>
            <p className="text-xl text-gray-600">
              Find jobs in your field of expertise
            </p>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {Object.entries(stats?.job_categories || {}).map(([category, count]) => (
              <Link
                key={category}
                to={`/jobs?job_type=${category}`}
                className="bg-white p-4 rounded-lg shadow-md hover:shadow-lg transition-shadow text-center"
              >
                <div className="font-semibold text-gray-900 mb-1">
                  {category.replace('_', ' ').toUpperCase()}
                </div>
                <div className="text-sm text-gray-600">
                  {count} jobs
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
};

export default LandingPage;