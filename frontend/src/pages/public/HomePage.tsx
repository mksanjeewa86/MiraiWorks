import { Link } from 'react-router-dom'
import { ArrowRight, Users, Briefcase, TrendingUp } from 'lucide-react'

export default function HomePage() {
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative bg-gradient-to-br from-primary-50 to-primary-100 dark:from-primary-950 dark:to-primary-900 py-20">
        <div className="container mx-auto px-4">
          <div className="text-center max-w-4xl mx-auto">
            <h1 className="text-5xl md:text-6xl font-bold text-gray-900 dark:text-white mb-6">
              Your Future <span className="text-primary-600 dark:text-primary-400">Starts Here</span>
            </h1>
            <p className="text-xl text-muted-600 dark:text-muted-300 mb-8 leading-relaxed">
              Connect talented professionals with innovative companies. 
              MiraiWorks is the modern platform for recruiting, interviewing, and hiring.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                to="/register"
                className="bg-primary-600 hover:bg-primary-700 text-white px-8 py-4 rounded-2xl font-medium text-lg transition-colors inline-flex items-center justify-center"
              >
                Get Started
                <ArrowRight className="ml-2 h-5 w-5" />
              </Link>
              <Link
                to="/jobs"
                className="border border-primary-600 text-primary-600 hover:bg-primary-50 dark:hover:bg-primary-900/20 px-8 py-4 rounded-2xl font-medium text-lg transition-colors inline-flex items-center justify-center"
              >
                Browse Jobs
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-white dark:bg-gray-900">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
              Why Choose MiraiWorks?
            </h2>
            <p className="text-xl text-muted-600 dark:text-muted-300 max-w-2xl mx-auto">
              We make hiring simple, efficient, and effective for everyone involved.
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center p-8 bg-gray-50 dark:bg-gray-800 rounded-2xl">
              <div className="w-16 h-16 bg-primary-100 dark:bg-primary-900/20 rounded-2xl flex items-center justify-center mx-auto mb-6">
                <Users className="h-8 w-8 text-primary-600 dark:text-primary-400" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                Smart Matching
              </h3>
              <p className="text-muted-600 dark:text-muted-300">
                Our AI-powered platform matches candidates with the perfect opportunities based on skills, experience, and preferences.
              </p>
            </div>
            
            <div className="text-center p-8 bg-gray-50 dark:bg-gray-800 rounded-2xl">
              <div className="w-16 h-16 bg-accent-100 dark:bg-accent-900/20 rounded-2xl flex items-center justify-center mx-auto mb-6">
                <Briefcase className="h-8 w-8 text-accent-600 dark:text-accent-400" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                Streamlined Process
              </h3>
              <p className="text-muted-600 dark:text-muted-300">
                From application to hire, our platform streamlines every step of the recruitment process for faster results.
              </p>
            </div>
            
            <div className="text-center p-8 bg-gray-50 dark:bg-gray-800 rounded-2xl">
              <div className="w-16 h-16 bg-orange-100 dark:bg-orange-900/20 rounded-2xl flex items-center justify-center mx-auto mb-6">
                <TrendingUp className="h-8 w-8 text-orange-600 dark:text-orange-400" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                Data-Driven Insights
              </h3>
              <p className="text-muted-600 dark:text-muted-300">
                Make informed decisions with comprehensive analytics and reporting on your hiring performance.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-primary-600 dark:bg-primary-800">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-4xl font-bold text-white mb-4">
            Ready to Transform Your Hiring?
          </h2>
          <p className="text-xl text-primary-100 mb-8 max-w-2xl mx-auto">
            Join thousands of companies and candidates who trust MiraiWorks for their career journey.
          </p>
          <Link
            to="/register"
            className="bg-white text-primary-600 hover:bg-gray-100 px-8 py-4 rounded-2xl font-medium text-lg transition-colors inline-flex items-center"
          >
            Start Your Journey
            <ArrowRight className="ml-2 h-5 w-5" />
          </Link>
        </div>
      </section>
    </div>
  )
}
