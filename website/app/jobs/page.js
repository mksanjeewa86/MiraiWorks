'use client'
import { useState } from 'react';
import Layout from '../../components/Layout';

export default function Jobs() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedLocation, setSelectedLocation] = useState('all');

  const jobs = [
    {
      id: 1,
      title: 'Senior React Developer',
      company: 'TechCorp Inc.',
      location: 'Tokyo, Japan',
      type: 'Full-time',
      category: 'Technology',
      salary: '¥8M - ¥12M',
      description: 'We are looking for an experienced React developer to join our growing team.',
      posted: '2 days ago'
    },
    {
      id: 2,
      title: 'Marketing Manager',
      company: 'Growth Solutions',
      location: 'Osaka, Japan',
      type: 'Full-time',
      category: 'Marketing',
      salary: '¥6M - ¥9M',
      description: 'Lead marketing campaigns and drive growth for our innovative products.',
      posted: '1 week ago'
    },
    {
      id: 3,
      title: 'UX Designer',
      company: 'Design Studio Pro',
      location: 'Remote',
      type: 'Contract',
      category: 'Design',
      salary: '¥5M - ¥7M',
      description: 'Create amazing user experiences for our digital products.',
      posted: '3 days ago'
    },
    {
      id: 4,
      title: 'Data Analyst',
      company: 'Analytics Co.',
      location: 'Kyoto, Japan',
      type: 'Part-time',
      category: 'Technology',
      salary: '¥4M - ¥6M',
      description: 'Analyze data to provide insights and drive business decisions.',
      posted: '5 days ago'
    },
    {
      id: 5,
      title: 'Sales Representative',
      company: 'Sales Pro Ltd.',
      location: 'Nagoya, Japan',
      type: 'Full-time',
      category: 'Sales',
      salary: '¥4M - ¥8M',
      description: 'Build relationships with clients and drive revenue growth.',
      posted: '1 day ago'
    },
    {
      id: 6,
      title: 'Financial Analyst',
      company: 'Finance Corp',
      location: 'Tokyo, Japan',
      type: 'Full-time',
      category: 'Finance',
      salary: '¥6M - ¥10M',
      description: 'Analyze financial data and provide strategic recommendations.',
      posted: '4 days ago'
    }
  ];

  const categories = ['all', 'Technology', 'Marketing', 'Design', 'Sales', 'Finance', 'Healthcare', 'Education'];
  const locations = ['all', 'Tokyo, Japan', 'Osaka, Japan', 'Kyoto, Japan', 'Nagoya, Japan', 'Remote'];

  const filteredJobs = jobs.filter(job => {
    const matchesSearch = job.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         job.company.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || job.category === selectedCategory;
    const matchesLocation = selectedLocation === 'all' || job.location === selectedLocation;
    
    return matchesSearch && matchesCategory && matchesLocation;
  });

  return (
    <Layout>
      <div className="min-h-screen bg-secondary-50">
        <div className="bg-white shadow-sm">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <h1 className="text-3xl font-bold text-secondary-900 mb-6">Find Your Perfect Job</h1>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              <div>
                <input
                  type="text"
                  placeholder="Search jobs, companies..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full px-4 py-2 border border-secondary-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>
              
              <div>
                <select
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  className="w-full px-4 py-2 border border-secondary-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                >
                  {categories.map(category => (
                    <option key={category} value={category}>
                      {category === 'all' ? 'All Categories' : category}
                    </option>
                  ))}
                </select>
              </div>
              
              <div>
                <select
                  value={selectedLocation}
                  onChange={(e) => setSelectedLocation(e.target.value)}
                  className="w-full px-4 py-2 border border-secondary-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                >
                  {locations.map(location => (
                    <option key={location} value={location}>
                      {location === 'all' ? 'All Locations' : location}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            
            <div className="text-secondary-600">
              Showing {filteredJobs.length} jobs
            </div>
          </div>
        </div>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="space-y-6">
            {filteredJobs.map(job => (
              <div key={job.id} className="bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow p-6">
                <div className="flex flex-col md:flex-row md:items-center md:justify-between">
                  <div className="flex-1">
                    <div className="flex items-start justify-between">
                      <div>
                        <h2 className="text-xl font-semibold text-secondary-900 mb-2">{job.title}</h2>
                        <p className="text-primary-600 font-medium mb-1">{job.company}</p>
                        <div className="flex flex-wrap items-center gap-4 text-secondary-600 text-sm mb-3">
                          <span className="flex items-center">
                            <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                            </svg>
                            {job.location}
                          </span>
                          <span className="flex items-center">
                            <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                            {job.type}
                          </span>
                          <span className="flex items-center">
                            <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
                            </svg>
                            {job.salary}
                          </span>
                        </div>
                        <p className="text-secondary-700 mb-3">{job.description}</p>
                        <div className="flex items-center gap-2">
                          <span className="bg-primary-100 text-primary-700 px-2 py-1 rounded text-xs font-medium">
                            {job.category}
                          </span>
                          <span className="text-secondary-500 text-sm">{job.posted}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <div className="mt-4 md:mt-0 md:ml-6 flex-shrink-0">
                    <div className="flex flex-col gap-2">
                      <button className="bg-primary-600 hover:bg-primary-700 text-white px-6 py-2 rounded-lg font-medium transition-colors">
                        Apply Now
                      </button>
                      <button className="border border-secondary-300 hover:border-secondary-400 text-secondary-700 px-6 py-2 rounded-lg font-medium transition-colors">
                        Save Job
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {filteredJobs.length === 0 && (
            <div className="text-center py-12">
              <div className="text-secondary-400 mb-4">
                <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              <h3 className="text-xl font-medium text-secondary-900 mb-2">No jobs found</h3>
              <p className="text-secondary-600">Try adjusting your search criteria or browse all available positions.</p>
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
}