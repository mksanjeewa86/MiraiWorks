import Layout from '../../components/Layout';

export default function Services() {
  return (
    <Layout>
      <div>
        <section className="bg-gradient-to-br from-primary-50 to-primary-100 py-20">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center">
              <h1 className="text-4xl md:text-5xl font-bold text-secondary-900 mb-6">
                Our Services
              </h1>
              <p className="text-xl text-secondary-700 max-w-3xl mx-auto">
                Comprehensive recruitment solutions tailored to meet the unique needs of modern businesses and talented professionals.
              </p>
            </div>
          </div>
        </section>

        <section className="py-16 bg-white">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
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
      </div>
    </Layout>
  );
}