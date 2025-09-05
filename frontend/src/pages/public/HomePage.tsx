import { Link } from 'react-router-dom'
import { ArrowRight, Users, Briefcase, TrendingUp } from 'lucide-react'

export default function HomePage() {
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative py-20" style={{ background: 'linear-gradient(to bottom right, rgba(108, 99, 255, 0.05), rgba(108, 99, 255, 0.1))' }}>
        <div className="container mx-auto px-4">
          <div className="text-center max-w-4xl mx-auto">
            <h1 className="text-5xl md:text-6xl font-bold text-gray-900 dark:text-white mb-6">
              Your Future <span className="text-brand-primary">Starts Here</span>
            </h1>
            <p className="text-xl text-muted-600 dark:text-muted-300 mb-8 leading-relaxed">
              Connect talented professionals with innovative companies. 
              MiraiWorks is the modern platform for recruiting, interviewing, and hiring.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                to="/register"
                className="btn-primary px-8 py-4 text-lg inline-flex items-center justify-center"
              >
                Get Started
                <ArrowRight className="ml-2 h-5 w-5" />
              </Link>
              <Link
                to="/jobs"
                className="btn-secondary text-brand-primary px-8 py-4 text-lg inline-flex items-center justify-center"
              >
                Browse Jobs
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20" style={{ backgroundColor: 'var(--bg-primary)' }}>
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
            <div className="text-center p-8 card">
              <div className="w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-6" style={{ backgroundColor: 'rgba(108, 99, 255, 0.1)' }}>
                <Users className="h-8 w-8 text-brand-primary" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                Smart Matching
              </h3>
              <p className="text-muted-600 dark:text-muted-300">
                Our AI-powered platform matches candidates with the perfect opportunities based on skills, experience, and preferences.
              </p>
            </div>
            
            <div className="text-center p-8 card">
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
            
            <div className="text-center p-8 card">
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
      <section className="py-20" style={{ backgroundColor: 'var(--brand-primary)' }}>
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-4xl font-bold text-white mb-4">
            Ready to Transform Your Hiring?
          </h2>
          <p className="text-xl mb-8 max-w-2xl mx-auto" style={{ color: 'rgba(255, 255, 255, 0.8)' }}>
            Join thousands of companies and candidates who trust MiraiWorks for their career journey.
          </p>
          <Link
            to="/register"
            className="px-8 py-4 text-lg inline-flex items-center font-medium transition-colors rounded-2xl" style={{ backgroundColor: 'white', color: 'var(--brand-primary)' }}
          >
            Start Your Journey
            <ArrowRight className="ml-2 h-5 w-5" />
          </Link>
        </div>
      </section>
    </div>
  )
}
