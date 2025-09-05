import Layout from '../../components/Layout';

export default function About() {
  return (
    <Layout>
      <div>
        <section className="bg-gradient-to-br from-primary-50 to-primary-100 py-20">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center">
              <h1 className="text-4xl md:text-5xl font-bold text-secondary-900 mb-6">
                About MiraiWorks
              </h1>
              <p className="text-xl text-secondary-700 max-w-3xl mx-auto">
                We're on a mission to connect talented individuals with their dream careers 
                and help companies build exceptional teams.
              </p>
            </div>
          </div>
        </section>

        <section className="py-16 bg-white">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
              <div>
                <h2 className="text-3xl font-bold text-secondary-900 mb-6">Our Story</h2>
                <p className="text-secondary-600 mb-4">
                  Founded in 2020, MiraiWorks began with a simple vision: to make job searching 
                  and hiring more efficient, transparent, and rewarding for everyone involved.
                </p>
                <p className="text-secondary-600 mb-4">
                  We understand that finding the right job or the perfect candidate can be 
                  challenging. That's why we've built a platform that uses cutting-edge technology 
                  to match skills with opportunities, while maintaining the human touch that makes 
                  all the difference.
                </p>
                <p className="text-secondary-600">
                  Today, we're proud to serve thousands of job seekers and hundreds of companies 
                  across Japan and beyond, helping them achieve their goals and build successful futures.
                </p>
              </div>
              <div className="bg-primary-100 rounded-lg p-8 text-center">
                <div className="grid grid-cols-2 gap-8">
                  <div>
                    <div className="text-3xl font-bold text-primary-600 mb-2">10,000+</div>
                    <div className="text-secondary-600">Jobs Posted</div>
                  </div>
                  <div>
                    <div className="text-3xl font-bold text-primary-600 mb-2">5,000+</div>
                    <div className="text-secondary-600">Successful Hires</div>
                  </div>
                  <div>
                    <div className="text-3xl font-bold text-primary-600 mb-2">500+</div>
                    <div className="text-secondary-600">Partner Companies</div>
                  </div>
                  <div>
                    <div className="text-3xl font-bold text-primary-600 mb-2">98%</div>
                    <div className="text-secondary-600">Satisfaction Rate</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className="py-16 bg-secondary-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-12">
              <h2 className="text-3xl font-bold text-secondary-900 mb-4">Our Values</h2>
              <p className="text-xl text-secondary-600">
                The principles that guide everything we do
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div className="text-center p-6">
                <div className="w-16 h-16 bg-primary-600 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold text-secondary-900 mb-2">Passion</h3>
                <p className="text-secondary-600">
                  We're passionate about helping people find work they love and companies find the talent they need.
                </p>
              </div>

              <div className="text-center p-6">
                <div className="w-16 h-16 bg-primary-600 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold text-secondary-900 mb-2">Integrity</h3>
                <p className="text-secondary-600">
                  We believe in transparency, honesty, and doing the right thing for our users and partners.
                </p>
              </div>

              <div className="text-center p-6">
                <div className="w-16 h-16 bg-primary-600 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold text-secondary-900 mb-2">Innovation</h3>
                <p className="text-secondary-600">
                  We continuously improve our platform with the latest technology and user feedback.
                </p>
              </div>
            </div>
          </div>
        </section>

        <section className="py-16 bg-white">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-12">
              <h2 className="text-3xl font-bold text-secondary-900 mb-4">Our Services</h2>
              <p className="text-xl text-secondary-600">
                Comprehensive recruitment solutions for modern businesses
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
              <div className="border border-secondary-200 rounded-lg p-6 hover:shadow-lg transition-shadow">
                <h3 className="text-xl font-semibold text-secondary-900 mb-3">Talent Sourcing</h3>
                <p className="text-secondary-600 mb-4">
                  Find the right candidates from our extensive database of qualified professionals.
                </p>
                <ul className="text-secondary-600 text-sm space-y-1">
                  <li>• AI-powered candidate matching</li>
                  <li>• Skills-based search filters</li>
                  <li>• Real-time candidate availability</li>
                </ul>
              </div>

              <div className="border border-secondary-200 rounded-lg p-6 hover:shadow-lg transition-shadow">
                <h3 className="text-xl font-semibold text-secondary-900 mb-3">Recruitment Consulting</h3>
                <p className="text-secondary-600 mb-4">
                  Expert guidance to optimize your hiring process and attract top talent.
                </p>
                <ul className="text-secondary-600 text-sm space-y-1">
                  <li>• Hiring strategy development</li>
                  <li>• Job description optimization</li>
                  <li>• Interview process design</li>
                </ul>
              </div>

              <div className="border border-secondary-200 rounded-lg p-6 hover:shadow-lg transition-shadow">
                <h3 className="text-xl font-semibold text-secondary-900 mb-3">Executive Search</h3>
                <p className="text-secondary-600 mb-4">
                  Specialized recruitment for senior-level and executive positions.
                </p>
                <ul className="text-secondary-600 text-sm space-y-1">
                  <li>• C-level and VP positions</li>
                  <li>• Confidential searches</li>
                  <li>• Leadership assessment</li>
                </ul>
              </div>
            </div>
          </div>
        </section>

        <section className="py-16 bg-primary-600">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <h2 className="text-3xl font-bold text-white mb-4">Ready to Get Started?</h2>
            <p className="text-xl text-primary-100 mb-8 max-w-2xl mx-auto">
              Whether you're looking for your next career opportunity or searching for top talent, 
              we're here to help you succeed.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button className="bg-white text-primary-600 hover:bg-primary-50 px-8 py-3 rounded-lg font-medium transition-colors">
                Find Jobs
              </button>
              <button className="border-2 border-white text-white hover:bg-white hover:text-primary-600 px-8 py-3 rounded-lg font-medium transition-colors">
                Hire Talent
              </button>
            </div>
          </div>
        </section>
      </div>
    </Layout>
  );
}