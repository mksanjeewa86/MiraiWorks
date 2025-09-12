import Link from 'next/link';
import WebsiteLayout from '@/components/website/WebsiteLayout';

export default function Home() {
  const jobCategories = [
    { name: 'Technology', count: '1,234', icon: '💻' },
    { name: 'Marketing', count: '856', icon: '📈' },
    { name: 'Finance', count: '492', icon: '💰' },
    { name: 'Healthcare', count: '678', icon: '🏥' },
    { name: 'Design', count: '324', icon: '🎨' },
    { name: 'Sales', count: '789', icon: '💼' },
    { name: 'Education', count: '234', icon: '📚' },
    { name: 'Engineering', count: '567', icon: '⚙️' }
  ];

  return (
    <WebsiteLayout>
      {/* Hero Section */}
      <section className="relative bg-gradient-to-br from-blue-50 via-white to-purple-50 py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
              Find Your Dream Job
              <span className="block" style={{ color: 'var(--brand-primary)' }}>
                With MiraiWorks
              </span>
            </h1>
            <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
              Connect with top companies and discover opportunities that match your skills and ambitions. 
              Your career journey starts here.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Link
                href="/jobs"
                className="inline-flex items-center px-8 py-3 text-lg font-medium rounded-md text-white shadow-lg transition-colors"
                style={{ backgroundColor: 'var(--brand-primary)' }}
              >
                Browse Jobs
              </Link>
              <Link
                href="/auth/register"
                className="inline-flex items-center px-8 py-3 text-lg font-medium rounded-md border border-gray-300 text-gray-700 bg-white hover:bg-gray-50 transition-colors"
              >
                Post a Job
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Why Choose MiraiWorks?
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              We make job searching and hiring simple, efficient, and effective.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center p-6 rounded-lg bg-blue-50 hover:bg-blue-100 transition-colors">
              <div 
                className="inline-flex items-center justify-center w-16 h-16 rounded-full mb-4"
                style={{ backgroundColor: 'var(--brand-primary)' }}
              >
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Smart Job Matching</h3>
              <p className="text-gray-600">
                Our AI-powered system matches you with jobs that fit your skills, experience, and preferences.
              </p>
            </div>

            <div className="text-center p-6 rounded-lg bg-blue-50 hover:bg-blue-100 transition-colors">
              <div 
                className="inline-flex items-center justify-center w-16 h-16 rounded-full mb-4"
                style={{ backgroundColor: 'var(--brand-primary)' }}
              >
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Top Companies</h3>
              <p className="text-gray-600">
                Connect with leading companies across various industries looking for talented professionals like you.
              </p>
            </div>

            <div className="text-center p-6 rounded-lg bg-blue-50 hover:bg-blue-100 transition-colors">
              <div 
                className="inline-flex items-center justify-center w-16 h-16 rounded-full mb-4"
                style={{ backgroundColor: 'var(--brand-primary)' }}
              >
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Fast & Easy</h3>
              <p className="text-gray-600">
                Apply to multiple jobs with one click. Our streamlined process saves you time and effort.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Job Categories Section */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Popular Job Categories
            </h2>
            <p className="text-xl text-gray-600">
              Explore opportunities in trending fields
            </p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {jobCategories.map((category, index) => (
              <Link
                key={index}
                href={`/jobs?category=${category.name.toLowerCase()}`}
                className="bg-white p-6 rounded-lg shadow-sm hover:shadow-md transition-shadow cursor-pointer"
              >
                <div className="text-3xl mb-3">{category.icon}</div>
                <h3 className="text-lg font-semibold text-gray-900 mb-1">{category.name}</h3>
                <p className="font-medium" style={{ color: 'var(--brand-primary)' }}>
                  {category.count} jobs
                </p>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
            <div>
              <div className="text-4xl font-bold mb-2" style={{ color: 'var(--brand-primary)' }}>
                10,000+
              </div>
              <div className="text-gray-600">Active Jobs</div>
            </div>
            <div>
              <div className="text-4xl font-bold mb-2" style={{ color: 'var(--brand-primary)' }}>
                50,000+
              </div>
              <div className="text-gray-600">Job Seekers</div>
            </div>
            <div>
              <div className="text-4xl font-bold mb-2" style={{ color: 'var(--brand-primary)' }}>
                2,500+
              </div>
              <div className="text-gray-600">Companies</div>
            </div>
            <div>
              <div className="text-4xl font-bold mb-2" style={{ color: 'var(--brand-primary)' }}>
                95%
              </div>
              <div className="text-gray-600">Success Rate</div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 bg-gray-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              Ready to Get Started?
            </h2>
            <p className="text-xl text-gray-300 mb-8">
              Join thousands of job seekers who have found their perfect match
            </p>
            <Link
              href="/auth/register"
              className="inline-flex items-center px-8 py-3 text-lg font-medium rounded-md text-white shadow-lg transition-colors"
              style={{ backgroundColor: 'var(--brand-primary)' }}
            >
              Start Your Journey
            </Link>
          </div>
        </div>
      </section>
    </WebsiteLayout>
  );
}
