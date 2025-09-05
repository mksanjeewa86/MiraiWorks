'use client';

import { useState } from 'react';
import Link from 'next/link';
import WebsiteLayout from '@/components/website/WebsiteLayout';

interface Job {
  id: string;
  title: string;
  company: string;
  location: string;
  type: 'full-time' | 'part-time' | 'contract' | 'remote';
  salary: string;
  description: string;
  requirements: string[];
  category: string;
  postedDate: string;
  featured: boolean;
}

export default function JobsPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedType, setSelectedType] = useState('all');

  const mockJobs: Job[] = [
    {
      id: '1',
      title: 'Senior Frontend Developer',
      company: 'TechCorp Inc.',
      location: 'San Francisco, CA',
      type: 'full-time',
      salary: '$120k - $180k',
      description: 'We are looking for a Senior Frontend Developer to join our growing team. You will be responsible for building responsive web applications using React, TypeScript, and modern web technologies.',
      requirements: ['5+ years React experience', 'TypeScript proficiency', 'Experience with Next.js', 'Knowledge of CSS frameworks'],
      category: 'technology',
      postedDate: '2025-01-05',
      featured: true
    },
    {
      id: '2',
      title: 'Product Marketing Manager',
      company: 'StartupCo',
      location: 'New York, NY',
      type: 'full-time',
      salary: '$90k - $140k',
      description: 'Join our marketing team as a Product Marketing Manager. You will develop go-to-market strategies and work closely with product and sales teams.',
      requirements: ['3+ years marketing experience', 'Product marketing background', 'Strong communication skills', 'Analytics experience'],
      category: 'marketing',
      postedDate: '2025-01-04',
      featured: false
    },
    {
      id: '3',
      title: 'DevOps Engineer',
      company: 'CloudTech Solutions',
      location: 'Remote',
      type: 'remote',
      salary: '$100k - $160k',
      description: 'We need a DevOps Engineer to help us scale our cloud infrastructure. Experience with AWS, Docker, and Kubernetes required.',
      requirements: ['AWS certification preferred', 'Docker & Kubernetes', 'CI/CD pipeline experience', 'Infrastructure as Code'],
      category: 'technology',
      postedDate: '2025-01-03',
      featured: true
    },
    {
      id: '4',
      title: 'UX/UI Designer',
      company: 'DesignStudio',
      location: 'Los Angeles, CA',
      type: 'full-time',
      salary: '$80k - $120k',
      description: 'Creative UX/UI Designer wanted to join our design team. You will work on user experience design for web and mobile applications.',
      requirements: ['3+ years UX/UI experience', 'Figma proficiency', 'User research skills', 'Design system experience'],
      category: 'design',
      postedDate: '2025-01-02',
      featured: false
    },
    {
      id: '5',
      title: 'Sales Development Representative',
      company: 'SalesPro Inc.',
      location: 'Chicago, IL',
      type: 'full-time',
      salary: '$50k - $80k + Commission',
      description: 'High-energy Sales Development Representative needed to generate leads and qualify prospects for our sales team.',
      requirements: ['1+ years sales experience', 'CRM experience', 'Strong communication skills', 'Goal-oriented mindset'],
      category: 'sales',
      postedDate: '2025-01-01',
      featured: false
    },
    {
      id: '6',
      title: 'Data Scientist',
      company: 'DataCorp',
      location: 'Seattle, WA',
      type: 'full-time',
      salary: '$130k - $200k',
      description: 'Join our data science team to build machine learning models and analyze large datasets to drive business insights.',
      requirements: ['PhD in related field preferred', 'Python/R proficiency', 'Machine learning expertise', 'SQL skills'],
      category: 'technology',
      postedDate: '2024-12-30',
      featured: true
    }
  ];

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
    { value: 'full-time', label: 'Full-time' },
    { value: 'part-time', label: 'Part-time' },
    { value: 'contract', label: 'Contract' },
    { value: 'remote', label: 'Remote' }
  ];

  const filteredJobs = mockJobs.filter(job => {
    const matchesSearch = job.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         job.company.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         job.location.toLowerCase().includes(searchQuery.toLowerCase());
    
    const matchesCategory = selectedCategory === 'all' || job.category === selectedCategory;
    const matchesType = selectedType === 'all' || job.type === selectedType;

    return matchesSearch && matchesCategory && matchesType;
  });

  const getJobTypeColor = (type: string) => {
    switch (type) {
      case 'full-time': return 'bg-green-100 text-green-800';
      case 'part-time': return 'bg-blue-100 text-blue-800';
      case 'contract': return 'bg-purple-100 text-purple-800';
      case 'remote': return 'bg-orange-100 text-orange-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <WebsiteLayout>
      {/* Hero Section */}
      <section className="py-16 bg-gradient-to-br from-blue-50 via-white to-purple-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-8">
            <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
              Find Your Next Job
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
                  placeholder="Search jobs, companies, or locations..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div>
                <select
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
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
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
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

      {/* Jobs List */}
      <section className="py-12 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between mb-8">
            <h2 className="text-2xl font-bold text-gray-900">
              {filteredJobs.length} Job{filteredJobs.length !== 1 ? 's' : ''} Found
            </h2>
            <p className="text-gray-600">
              Showing results for your search criteria
            </p>
          </div>

          <div className="space-y-6">
            {filteredJobs.map(job => (
              <div 
                key={job.id} 
                className={`bg-white rounded-lg border shadow-sm hover:shadow-md transition-shadow p-6 ${
                  job.featured ? 'ring-2 ring-blue-200 border-blue-200' : 'border-gray-200'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-xl font-bold text-gray-900">
                        {job.title}
                      </h3>
                      {job.featured && (
                        <span className="px-2 py-1 text-xs font-medium bg-yellow-100 text-yellow-800 rounded-full">
                          Featured
                        </span>
                      )}
                    </div>
                    
                    <div className="flex flex-wrap items-center gap-4 mb-3 text-sm text-gray-600">
                      <span className="font-medium text-blue-600">{job.company}</span>
                      <span>📍 {job.location}</span>
                      <span>💰 {job.salary}</span>
                      <span>📅 Posted {new Date(job.postedDate).toLocaleDateString()}</span>
                    </div>

                    <p className="text-gray-600 mb-4">
                      {job.description}
                    </p>

                    <div className="flex flex-wrap gap-2 mb-4">
                      {job.requirements.slice(0, 3).map((req, index) => (
                        <span 
                          key={index}
                          className="px-3 py-1 text-xs font-medium bg-gray-100 text-gray-700 rounded-full"
                        >
                          {req}
                        </span>
                      ))}
                      {job.requirements.length > 3 && (
                        <span className="px-3 py-1 text-xs font-medium bg-gray-100 text-gray-700 rounded-full">
                          +{job.requirements.length - 3} more
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="flex flex-col items-end gap-3 ml-6">
                    <span className={`px-3 py-1 text-xs font-medium rounded-full ${getJobTypeColor(job.type)}`}>
                      {job.type.replace('-', ' ').toUpperCase()}
                    </span>
                    
                    <div className="flex flex-col sm:flex-row gap-2">
                      <button className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors">
                        Save Job
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

          {filteredJobs.length === 0 && (
            <div className="text-center py-12">
              <div className="text-6xl mb-4">🔍</div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">No jobs found</h3>
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
            Don&apos;t See the Right Job?
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
              Set Up Job Alerts
            </button>
          </div>
        </div>
      </section>
    </WebsiteLayout>
  );
}