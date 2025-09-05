import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { publicApi } from '../../services/api';

interface CompanyDetail {
  id: number;
  name: string;
  domain?: string;
  website?: string;
  description?: string;
  profile?: {
    id: number;
    tagline?: string;
    mission?: string;
    values?: string[];
    culture?: string;
    logo_url?: string;
    banner_url?: string;
    gallery_images?: string[];
    company_video_url?: string;
    contact_email?: string;
    phone?: string;
    address?: string;
    linkedin_url?: string;
    twitter_url?: string;
    facebook_url?: string;
    instagram_url?: string;
    youtube_url?: string;
    founded_year?: number;
    employee_count?: string;
    headquarters?: string;
    funding_stage?: string;
    benefits_summary?: string;
    perks_highlights?: string[];
    public_slug: string;
    profile_views: number;
  };
}

interface Job {
  id: number;
  title: string;
  slug: string;
  summary?: string;
  location?: string;
  job_type: string;
  experience_level: string;
  remote_type: string;
  salary_range_display?: string;
  is_featured: boolean;
  published_at: string;
  days_since_published?: number;
}

const CompanyDetailPage: React.FC = () => {
  const { slug } = useParams<{ slug: string }>();

  const { data: company, isLoading, error } = useQuery({
    queryKey: ['company', slug],
    queryFn: async (): Promise<CompanyDetail> => {
      const response = await publicApi.get(`/public/companies/${slug}`);
      return response.data;
    },
    enabled: !!slug
  });

  const { data: jobs } = useQuery({
    queryKey: ['company-jobs', slug],
    queryFn: async (): Promise<Job[]> => {
      const response = await publicApi.get(`/public/companies/${slug}/jobs`);
      return response.data;
    },
    enabled: !!slug
  });

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error || !company) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Company Not Found</h1>
          <p className="text-gray-600 mb-4">The company you're looking for doesn't exist or is not publicly available.</p>
          <Link
            to="/companies"
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Browse All Companies
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Banner Section */}
      {company.profile?.banner_url && (
        <div className="relative h-64 bg-gradient-to-r from-blue-600 to-purple-700">
          <img
            src={company.profile.banner_url}
            alt={`${company.name} banner`}
            className="w-full h-full object-cover"
          />
          <div className="absolute inset-0 bg-black bg-opacity-30"></div>
        </div>
      )}

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Company Header */}
        <div className="bg-white rounded-lg shadow-md -mt-16 relative z-10 p-8 mb-8">
          <div className="flex items-start justify-between">
            <div className="flex items-start gap-6">
              {company.profile?.logo_url ? (
                <img
                  src={company.profile.logo_url}
                  alt={company.name}
                  className="w-24 h-24 rounded-lg object-cover border-4 border-white shadow-lg"
                />
              ) : (
                <div className="w-24 h-24 bg-gray-200 rounded-lg border-4 border-white shadow-lg flex items-center justify-center">
                  <span className="text-gray-500 font-semibold text-3xl">
                    {company.name.charAt(0)}
                  </span>
                </div>
              )}
              
              <div className="flex-1">
                <h1 className="text-3xl font-bold text-gray-900 mb-2">{company.name}</h1>
                
                {company.profile?.tagline && (
                  <p className="text-xl text-gray-600 mb-4">{company.profile.tagline}</p>
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
                  
                  {company.profile?.founded_year && (
                    <span className="flex items-center">
                      📅 Founded {company.profile.founded_year}
                    </span>
                  )}
                  
                  {company.profile?.funding_stage && (
                    <span className="flex items-center">
                      💰 {company.profile.funding_stage.replace('_', ' ')}
                    </span>
                  )}
                  
                  {company.profile?.profile_views && (
                    <span className="flex items-center">
                      👁️ {company.profile.profile_views.toLocaleString()} views
                    </span>
                  )}
                </div>
              </div>
            </div>
            
            <div className="flex flex-col gap-3">
              {company.website && (
                <a
                  href={company.website}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors text-center"
                >
                  Visit Website
                </a>
              )}
              
              {jobs && jobs.length > 0 && (
                <Link
                  to="#jobs"
                  className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 transition-colors text-center"
                >
                  View Jobs ({jobs.length})
                </Link>
              )}
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 pb-12">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-8">
            {/* About */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">About {company.name}</h2>
              
              {company.description && (
                <div className="mb-6">
                  <p className="text-gray-700 leading-relaxed">
                    {company.description}
                  </p>
                </div>
              )}
              
              {company.profile?.mission && (
                <div className="mb-6">
                  <h3 className="font-semibold text-gray-900 mb-2">Mission</h3>
                  <p className="text-gray-700">{company.profile.mission}</p>
                </div>
              )}
              
              {company.profile?.culture && (
                <div className="mb-6">
                  <h3 className="font-semibold text-gray-900 mb-2">Culture</h3>
                  <p className="text-gray-700">{company.profile.culture}</p>
                </div>
              )}
              
              {company.profile?.values && company.profile.values.length > 0 && (
                <div>
                  <h3 className="font-semibold text-gray-900 mb-2">Values</h3>
                  <ul className="space-y-2">
                    {company.profile.values.map((value, index) => (
                      <li key={index} className="flex items-start">
                        <span className="text-blue-600 mr-2">•</span>
                        <span className="text-gray-700">{value}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            {/* Benefits & Perks */}
            {(company.profile?.benefits_summary || company.profile?.perks_highlights) && (
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Benefits & Perks</h2>
                
                {company.profile.benefits_summary && (
                  <div className="mb-6">
                    <p className="text-gray-700">{company.profile.benefits_summary}</p>
                  </div>
                )}
                
                {company.profile.perks_highlights && company.profile.perks_highlights.length > 0 && (
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-3">Highlights</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {company.profile.perks_highlights.map((perk, index) => (
                        <div key={index} className="flex items-center bg-green-50 p-3 rounded-lg">
                          <span className="text-green-600 mr-2">✓</span>
                          <span className="text-gray-700">{perk}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Photo Gallery */}
            {company.profile?.gallery_images && company.profile.gallery_images.length > 0 && (
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Gallery</h2>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                  {company.profile.gallery_images.map((image, index) => (
                    <img
                      key={index}
                      src={image}
                      alt={`${company.name} gallery ${index + 1}`}
                      className="w-full h-32 object-cover rounded-lg"
                    />
                  ))}
                </div>
              </div>
            )}

            {/* Video */}
            {company.profile?.company_video_url && (
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Company Video</h2>
                <div className="aspect-w-16 aspect-h-9">
                  <iframe
                    src={company.profile.company_video_url}
                    title={`${company.name} video`}
                    className="w-full h-64 rounded-lg"
                    allowFullScreen
                  />
                </div>
              </div>
            )}

            {/* Jobs */}
            <div id="jobs" className="bg-white rounded-lg shadow-md p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-xl font-semibold text-gray-900">
                  Open Positions {jobs && `(${jobs.length})`}
                </h2>
                {jobs && jobs.length > 5 && (
                  <Link
                    to={`/jobs?company_id=${company.id}`}
                    className="text-blue-600 hover:text-blue-800"
                  >
                    View All →
                  </Link>
                )}
              </div>
              
              {jobs && jobs.length > 0 ? (
                <div className="space-y-4">
                  {jobs.slice(0, 5).map(job => (
                    <div key={job.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                      <div className="flex justify-between items-start mb-2">
                        <h3 className="text-lg font-semibold text-gray-900">
                          <Link
                            to={`/jobs/${job.slug}`}
                            className="hover:text-blue-600 transition-colors"
                          >
                            {job.title}
                          </Link>
                        </h3>
                        {job.is_featured && (
                          <span className="bg-yellow-100 text-yellow-800 text-xs px-2 py-1 rounded">
                            Featured
                          </span>
                        )}
                      </div>
                      
                      {job.summary && (
                        <p className="text-gray-700 mb-3 text-sm">{job.summary}</p>
                      )}
                      
                      <div className="flex items-center justify-between">
                        <div className="flex gap-3 text-sm">
                          <span className="bg-gray-100 px-2 py-1 rounded">
                            {job.job_type.replace('_', ' ')}
                          </span>
                          <span className="bg-gray-100 px-2 py-1 rounded">
                            {job.experience_level.replace('_', ' ')}
                          </span>
                          <span className="bg-gray-100 px-2 py-1 rounded">
                            {job.remote_type.replace('_', ' ')}
                          </span>
                          {job.location && (
                            <span className="text-gray-500">📍 {job.location}</span>
                          )}
                        </div>
                        
                        <div className="text-sm text-gray-500">
                          {job.days_since_published} days ago
                        </div>
                      </div>
                      
                      {job.salary_range_display && (
                        <div className="mt-2 text-green-600 font-medium">
                          {job.salary_range_display}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500 text-center py-8">
                  No open positions at the moment. Check back later!
                </p>
              )}
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Contact Info */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Contact Information</h3>
              
              <div className="space-y-3 text-sm">
                {company.profile?.contact_email && (
                  <div>
                    <span className="font-medium text-gray-700">Email:</span>
                    <a
                      href={`mailto:${company.profile.contact_email}`}
                      className="ml-2 text-blue-600 hover:text-blue-800"
                    >
                      {company.profile.contact_email}
                    </a>
                  </div>
                )}
                
                {company.profile?.phone && (
                  <div>
                    <span className="font-medium text-gray-700">Phone:</span>
                    <span className="ml-2 text-gray-600">{company.profile.phone}</span>
                  </div>
                )}
                
                {company.profile?.address && (
                  <div>
                    <span className="font-medium text-gray-700">Address:</span>
                    <span className="ml-2 text-gray-600">{company.profile.address}</span>
                  </div>
                )}
              </div>
            </div>

            {/* Social Links */}
            {(company.profile?.linkedin_url || company.profile?.twitter_url || company.profile?.facebook_url) && (
              <div className="bg-white rounded-lg shadow-md p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Follow Us</h3>
                
                <div className="flex gap-3">
                  {company.profile.linkedin_url && (
                    <a
                      href={company.profile.linkedin_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="bg-blue-600 text-white p-2 rounded-lg hover:bg-blue-700 transition-colors"
                    >
                      LinkedIn
                    </a>
                  )}
                  
                  {company.profile.twitter_url && (
                    <a
                      href={company.profile.twitter_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="bg-black text-white p-2 rounded-lg hover:bg-gray-800 transition-colors"
                    >
                      Twitter
                    </a>
                  )}
                  
                  {company.profile.facebook_url && (
                    <a
                      href={company.profile.facebook_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="bg-blue-800 text-white p-2 rounded-lg hover:bg-blue-900 transition-colors"
                    >
                      Facebook
                    </a>
                  )}
                  
                  {company.profile.instagram_url && (
                    <a
                      href={company.profile.instagram_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="bg-pink-600 text-white p-2 rounded-lg hover:bg-pink-700 transition-colors"
                    >
                      Instagram
                    </a>
                  )}
                  
                  {company.profile.youtube_url && (
                    <a
                      href={company.profile.youtube_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="bg-red-600 text-white p-2 rounded-lg hover:bg-red-700 transition-colors"
                    >
                      YouTube
                    </a>
                  )}
                </div>
              </div>
            )}

            {/* Quick Stats */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Stats</h3>
              
              <div className="space-y-3">
                {company.profile?.founded_year && (
                  <div className="flex justify-between">
                    <span className="text-gray-600">Founded:</span>
                    <span className="font-medium">{company.profile.founded_year}</span>
                  </div>
                )}
                
                {company.profile?.employee_count && (
                  <div className="flex justify-between">
                    <span className="text-gray-600">Size:</span>
                    <span className="font-medium">{company.profile.employee_count} employees</span>
                  </div>
                )}
                
                {company.profile?.funding_stage && (
                  <div className="flex justify-between">
                    <span className="text-gray-600">Stage:</span>
                    <span className="font-medium">{company.profile.funding_stage.replace('_', ' ')}</span>
                  </div>
                )}
                
                {jobs && (
                  <div className="flex justify-between">
                    <span className="text-gray-600">Open Jobs:</span>
                    <span className="font-medium">{jobs.length}</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CompanyDetailPage;