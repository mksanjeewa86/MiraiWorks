import React, { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { publicApi } from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';

interface JobDetail {
  id: number;
  title: string;
  slug: string;
  summary?: string;
  description: string;
  department?: string;
  location?: string;
  country?: string;
  city?: string;
  job_type: string;
  experience_level: string;
  remote_type: string;
  requirements?: string;
  required_skills?: string[];
  preferred_skills?: string[];
  salary_min?: number;
  salary_max?: number;
  salary_type: string;
  salary_currency: string;
  show_salary: boolean;
  benefits?: string[];
  perks?: string[];
  application_deadline?: string;
  external_apply_url?: string;
  application_questions?: Array<{
    id: string;
    question: string;
    type: string;
    required: boolean;
  }>;
  status: string;
  is_featured: boolean;
  is_urgent: boolean;
  view_count: number;
  application_count: number;
  published_at: string;
  expires_at?: string;
  created_at: string;
  updated_at: string;
  is_active: boolean;
  days_since_published?: number;
  salary_range_display?: string;
  can_apply: boolean;
  company: {
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
      public_slug: string;
    };
  };
}

interface ApplicationData {
  cover_letter?: string;
  resume_id?: number;
  application_answers?: Record<string, any>;
  source?: string;
}

const JobDetailPage: React.FC = () => {
  const { slug } = useParams<{ slug: string }>();
  const { isAuthenticated } = useAuth();
  const queryClient = useQueryClient();
  const [showApplicationForm, setShowApplicationForm] = useState(false);
  const [applicationData, setApplicationData] = useState<ApplicationData>({
    cover_letter: '',
    source: 'website'
  });

  const { data: job, isLoading, error } = useQuery({
    queryKey: ['job', slug],
    queryFn: async (): Promise<JobDetail> => {
      const response = await publicApi.get(`/public/jobs/${slug}`);
      return response.data;
    },
    enabled: !!slug
  });

  const applyMutation = useMutation({
    mutationFn: async (data: ApplicationData) => {
      if (!job) throw new Error('Job not found');
      const response = await publicApi.post(`/public/jobs/${job.id}/apply`, data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['job', slug] });
      setShowApplicationForm(false);
      alert('Application submitted successfully!');
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || 'Failed to submit application';
      alert(message);
    }
  });

  const handleApply = () => {
    if (!isAuthenticated) {
      // Redirect to login with return URL
      window.location.href = `/auth/login?redirect=/jobs/${slug}`;
      return;
    }
    setShowApplicationForm(true);
  };

  const handleSubmitApplication = (e: React.FormEvent) => {
    e.preventDefault();
    applyMutation.mutate(applicationData);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error || !job) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Job Not Found</h1>
          <p className="text-gray-600 mb-4">The job you're looking for doesn't exist or has been removed.</p>
          <Link
            to="/jobs"
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Browse All Jobs
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Job Header */}
        <div className="bg-white rounded-lg shadow-md p-8 mb-6">
          <div className="flex items-start justify-between mb-6">
            <div className="flex-1">
              <div className="flex items-center mb-3">
                <h1 className="text-3xl font-bold text-gray-900 mr-4">{job.title}</h1>
                <div className="flex gap-2">
                  {job.is_featured && (
                    <span className="bg-yellow-100 text-yellow-800 text-sm px-3 py-1 rounded-full">
                      Featured
                    </span>
                  )}
                  {job.is_urgent && (
                    <span className="bg-red-100 text-red-800 text-sm px-3 py-1 rounded-full">
                      Urgent
                    </span>
                  )}
                </div>
              </div>
              
              <div className="flex items-center text-lg text-gray-600 mb-4">
                <Link
                  to={`/companies/${job.company.profile?.public_slug || job.company.domain}`}
                  className="font-semibold hover:text-blue-600 transition-colors"
                >
                  {job.company.name}
                </Link>
                {job.location && (
                  <>
                    <span className="mx-3">•</span>
                    <span>{job.location}</span>
                  </>
                )}
              </div>
              
              <div className="flex flex-wrap gap-3 mb-4">
                <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm">
                  {job.job_type.replace('_', ' ')}
                </span>
                <span className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm">
                  {job.experience_level.replace('_', ' ')}
                </span>
                <span className="bg-purple-100 text-purple-800 px-3 py-1 rounded-full text-sm">
                  {job.remote_type.replace('_', ' ')}
                </span>
              </div>
              
              {job.show_salary && job.salary_range_display && (
                <div className="text-xl font-semibold text-green-600 mb-4">
                  {job.salary_range_display}
                </div>
              )}
              
              <div className="flex items-center text-sm text-gray-500">
                <span>Posted {job.days_since_published} days ago</span>
                <span className="mx-3">•</span>
                <span>{job.view_count} views</span>
                <span className="mx-3">•</span>
                <span>{job.application_count} applications</span>
              </div>
            </div>
            
            {job.company.profile?.logo_url && (
              <img
                src={job.company.profile.logo_url}
                alt={job.company.name}
                className="w-20 h-20 rounded-lg object-cover ml-8"
              />
            )}
          </div>
          
          {/* Apply Button */}
          <div className="border-t pt-6">
            {job.external_apply_url ? (
              <a
                href={job.external_apply_url}
                target="_blank"
                rel="noopener noreferrer"
                className="bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors inline-block"
              >
                Apply on Company Website
              </a>
            ) : job.can_apply ? (
              <button
                onClick={handleApply}
                disabled={applyMutation.isPending}
                className="bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors disabled:opacity-50"
              >
                {applyMutation.isPending ? 'Submitting...' : 'Apply Now'}
              </button>
            ) : (
              <div className="text-gray-500">Applications are closed for this position</div>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Job Description */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Job Description</h2>
              {job.summary && (
                <div className="mb-4 p-4 bg-blue-50 rounded-lg">
                  <p className="text-gray-700">{job.summary}</p>
                </div>
              )}
              <div 
                className="prose prose-sm max-w-none text-gray-700"
                dangerouslySetInnerHTML={{ __html: job.description.replace(/\n/g, '<br/>') }}
              />
            </div>

            {/* Requirements */}
            {(job.requirements || job.required_skills || job.preferred_skills) && (
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Requirements</h2>
                
                {job.requirements && (
                  <div className="mb-4">
                    <div 
                      className="text-gray-700"
                      dangerouslySetInnerHTML={{ __html: job.requirements.replace(/\n/g, '<br/>') }}
                    />
                  </div>
                )}
                
                {job.required_skills && job.required_skills.length > 0 && (
                  <div className="mb-4">
                    <h3 className="font-medium text-gray-900 mb-2">Required Skills:</h3>
                    <div className="flex flex-wrap gap-2">
                      {job.required_skills.map((skill, index) => (
                        <span key={index} className="bg-red-100 text-red-800 px-2 py-1 rounded text-sm">
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                
                {job.preferred_skills && job.preferred_skills.length > 0 && (
                  <div>
                    <h3 className="font-medium text-gray-900 mb-2">Preferred Skills:</h3>
                    <div className="flex flex-wrap gap-2">
                      {job.preferred_skills.map((skill, index) => (
                        <span key={index} className="bg-green-100 text-green-800 px-2 py-1 rounded text-sm">
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Benefits & Perks */}
            {(job.benefits || job.perks) && (
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Benefits & Perks</h2>
                
                {job.benefits && job.benefits.length > 0 && (
                  <div className="mb-4">
                    <h3 className="font-medium text-gray-900 mb-2">Benefits:</h3>
                    <ul className="list-disc list-inside space-y-1 text-gray-700">
                      {job.benefits.map((benefit, index) => (
                        <li key={index}>{benefit}</li>
                      ))}
                    </ul>
                  </div>
                )}
                
                {job.perks && job.perks.length > 0 && (
                  <div>
                    <h3 className="font-medium text-gray-900 mb-2">Perks:</h3>
                    <ul className="list-disc list-inside space-y-1 text-gray-700">
                      {job.perks.map((perk, index) => (
                        <li key={index}>{perk}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Company Info */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">About the Company</h3>
              
              <div className="flex items-center mb-4">
                {job.company.profile?.logo_url ? (
                  <img
                    src={job.company.profile.logo_url}
                    alt={job.company.name}
                    className="w-12 h-12 rounded-lg object-cover mr-3"
                  />
                ) : (
                  <div className="w-12 h-12 bg-gray-200 rounded-lg mr-3 flex items-center justify-center">
                    <span className="text-gray-500 font-semibold">
                      {job.company.name.charAt(0)}
                    </span>
                  </div>
                )}
                <div>
                  <h4 className="font-semibold text-gray-900">{job.company.name}</h4>
                  {job.company.profile?.tagline && (
                    <p className="text-sm text-gray-600">{job.company.profile.tagline}</p>
                  )}
                </div>
              </div>
              
              {job.company.description && (
                <p className="text-gray-700 mb-4 text-sm line-clamp-4">
                  {job.company.description}
                </p>
              )}
              
              {job.company.profile && (
                <div className="space-y-2 text-sm text-gray-600 mb-4">
                  {job.company.profile.headquarters && (
                    <div>📍 {job.company.profile.headquarters}</div>
                  )}
                  {job.company.profile.employee_count && (
                    <div>👥 {job.company.profile.employee_count} employees</div>
                  )}
                </div>
              )}
              
              <Link
                to={`/companies/${job.company.profile?.public_slug || job.company.domain}`}
                className="block w-full text-center bg-gray-100 text-gray-700 py-2 px-4 rounded-lg hover:bg-gray-200 transition-colors"
              >
                View Company Profile
              </Link>
            </div>

            {/* Job Details */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Job Details</h3>
              
              <div className="space-y-3 text-sm">
                {job.department && (
                  <div>
                    <span className="font-medium text-gray-700">Department:</span>
                    <span className="ml-2 text-gray-600">{job.department}</span>
                  </div>
                )}
                
                <div>
                  <span className="font-medium text-gray-700">Job Type:</span>
                  <span className="ml-2 text-gray-600">{job.job_type.replace('_', ' ')}</span>
                </div>
                
                <div>
                  <span className="font-medium text-gray-700">Experience:</span>
                  <span className="ml-2 text-gray-600">{job.experience_level.replace('_', ' ')}</span>
                </div>
                
                <div>
                  <span className="font-medium text-gray-700">Work Type:</span>
                  <span className="ml-2 text-gray-600">{job.remote_type.replace('_', ' ')}</span>
                </div>
                
                {job.application_deadline && (
                  <div>
                    <span className="font-medium text-gray-700">Deadline:</span>
                    <span className="ml-2 text-gray-600">
                      {new Date(job.application_deadline).toLocaleDateString()}
                    </span>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Application Form Modal */}
        {showApplicationForm && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg p-6 max-w-md w-full max-h-[90vh] overflow-y-auto">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Apply to {job.title}</h3>
              
              <form onSubmit={handleSubmitApplication}>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Cover Letter (Optional)
                  </label>
                  <textarea
                    value={applicationData.cover_letter}
                    onChange={(e) => setApplicationData(prev => ({ ...prev, cover_letter: e.target.value }))}
                    placeholder="Tell us why you're interested in this position..."
                    rows={6}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                
                <div className="flex gap-3">
                  <button
                    type="submit"
                    disabled={applyMutation.isPending}
                    className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
                  >
                    {applyMutation.isPending ? 'Submitting...' : 'Submit Application'}
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowApplicationForm(false)}
                    className="flex-1 bg-gray-300 text-gray-700 py-2 px-4 rounded-lg hover:bg-gray-400 transition-colors"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default JobDetailPage;