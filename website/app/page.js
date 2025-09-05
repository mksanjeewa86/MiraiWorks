import Layout from '../components/Layout';

export default function Home() {
  return (
    <Layout>
      <div>
        <section className="bg-gradient py-20">
          <div className="container">
            <div className="text-center">
              <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
                Find Your Dream Job
                <span className="text-primary block">With MiraiWorks</span>
              </h1>
              <p className="text-xl text-secondary mb-8 max-w-3xl mx-auto">
                Connect with top companies and discover opportunities that match your skills and ambitions. 
                Your career journey starts here.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
                <button className="btn btn-primary px-8 py-3 text-lg shadow-lg">
                  Browse Jobs
                </button>
                <button className="btn btn-secondary px-8 py-3 text-lg">
                  Post a Job
                </button>
              </div>
            </div>
          </div>
        </section>

        <section className="py-16 bg-white">
          <div className="container">
            <div className="text-center mb-12">
              <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
                Why Choose MiraiWorks?
              </h2>
              <p className="text-xl text-secondary max-w-2xl mx-auto">
                We make job searching and hiring simple, efficient, and effective.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div className="text-center p-6 rounded-lg bg-primary-lightest card">
                <div className="icon-container">
                  <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">Smart Job Matching</h3>
                <p className="text-secondary">
                  Our AI-powered system matches you with jobs that fit your skills, experience, and preferences.
                </p>
              </div>

              <div className="text-center p-6 rounded-lg bg-primary-lightest card">
                <div className="icon-container">
                  <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">Top Companies</h3>
                <p className="text-secondary">
                  Connect with leading companies across various industries looking for talented professionals like you.
                </p>
              </div>

              <div className="text-center p-6 rounded-lg bg-primary-lightest card">
                <div className="icon-container">
                  <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">Fast & Easy</h3>
                <p className="text-secondary">
                  Apply to multiple jobs with one click. Our streamlined process saves you time and effort.
                </p>
              </div>
            </div>
          </div>
        </section>

        <section className="py-16 bg-secondary-light">
          <div className="container">
            <div className="text-center mb-12">
              <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
                Popular Job Categories
              </h2>
              <p className="text-xl text-secondary">
                Explore opportunities in trending fields
              </p>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
              {[
                { name: 'Technology', count: '1,234', icon: '💻' },
                { name: 'Marketing', count: '856', icon: '📈' },
                { name: 'Finance', count: '492', icon: '💰' },
                { name: 'Healthcare', count: '678', icon: '🏥' },
                { name: 'Design', count: '324', icon: '🎨' },
                { name: 'Sales', count: '789', icon: '💼' },
                { name: 'Education', count: '234', icon: '📚' },
                { name: 'Engineering', count: '567', icon: '⚙️' }
              ].map((category, index) => (
                <div key={index} className="bg-white p-6 rounded-lg shadow-sm card cursor-pointer">
                  <div className="text-3xl mb-3">{category.icon}</div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-1">{category.name}</h3>
                  <p className="text-primary font-medium">{category.count} jobs</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="py-16 bg-white">
          <div className="container">
            <div className="text-center mb-12">
              <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
                Ready to Get Started?
              </h2>
              <p className="text-xl text-secondary mb-8">
                Join thousands of job seekers who have found their perfect match
              </p>
              <button className="btn btn-primary px-8 py-3 text-lg shadow-lg">
                Start Your Journey
              </button>
            </div>
          </div>
        </section>
      </div>
    </Layout>
  );
}