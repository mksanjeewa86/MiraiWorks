import Link from 'next/link';
import WebsiteLayout from '@/components/website/WebsiteLayout';

export default function ServicesPage() {
  const services = [
    {
      title: 'Job Matching Platform',
      description: 'Our AI-powered platform connects job seekers with relevant opportunities based on skills, experience, and preferences.',
      features: [
        'Smart job recommendations',
        'Skills-based matching',
        'Preference filtering',
        'Real-time notifications'
      ],
      icon: '🎯',
      category: 'For Job Seekers'
    },
    {
      title: 'Talent Acquisition',
      description: 'Help companies find, attract, and hire the best talent with our comprehensive recruitment solutions.',
      features: [
        'Candidate sourcing',
        'Advanced filtering',
        'Interview scheduling',
        'Applicant tracking'
      ],
      icon: '🏢',
      category: 'For Employers'
    },
    {
      title: 'Resume Builder',
      description: 'Create professional resumes with our intuitive builder featuring multiple templates and industry-specific guidance.',
      features: [
        'Multiple templates',
        'ATS-friendly formats',
        'Industry recommendations',
        'Real-time preview'
      ],
      icon: '📄',
      category: 'For Job Seekers'
    },
    {
      title: 'Interview Management',
      description: 'Streamline your interview process with scheduling tools, video interviews, and candidate evaluation features.',
      features: [
        'Calendar integration',
        'Video interviewing',
        'Candidate scoring',
        'Interview feedback'
      ],
      icon: '🎤',
      category: 'For Employers'
    },
    {
      title: 'Career Coaching',
      description: 'Professional career guidance to help job seekers navigate their career path and achieve their goals.',
      features: [
        '1-on-1 coaching sessions',
        'Career path planning',
        'Skill development',
        'Interview preparation'
      ],
      icon: '🎓',
      category: 'Premium Service'
    },
    {
      title: 'Company Branding',
      description: 'Build your employer brand and attract top talent with our comprehensive branding and recruitment marketing services.',
      features: [
        'Company profile optimization',
        'Recruitment marketing',
        'Employee testimonials',
        'Social media presence'
      ],
      icon: '🚀',
      category: 'For Employers'
    }
  ];

  const pricingPlans = [
    {
      name: 'Job Seeker',
      price: 'Free',
      description: 'Everything you need to find your next opportunity',
      features: [
        'Unlimited job applications',
        'Resume builder',
        'Job alerts',
        'Basic profile',
        'Mobile app access'
      ],
      cta: 'Get Started',
      popular: false
    },
    {
      name: 'Professional',
      price: '$19/month',
      description: 'Advanced features for serious job seekers',
      features: [
        'Everything in Free',
        'Priority job matching',
        'Advanced analytics',
        'Career coaching session',
        'Premium templates'
      ],
      cta: 'Upgrade Now',
      popular: true
    },
    {
      name: 'Enterprise',
      price: 'Custom',
      description: 'Tailored solutions for large organizations',
      features: [
        'Custom integration',
        'Dedicated support',
        'Advanced analytics',
        'Custom branding',
        'API access'
      ],
      cta: 'Contact Sales',
      popular: false
    }
  ];

  return (
    <WebsiteLayout>
      {/* Hero Section */}
      <section className="py-20 bg-gradient-to-br from-blue-50 via-white to-purple-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
              Our Services
            </h1>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Comprehensive HR and recruitment solutions designed to connect talent with opportunity 
              and help organizations build exceptional teams.
            </p>
          </div>
        </div>
      </section>

      {/* Services Grid */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Everything You Need for Successful Hiring
            </h2>
            <p className="text-xl text-gray-600">
              From job posting to onboarding, we&apos;ve got you covered
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {services.map((service, index) => (
              <div key={index} className="bg-white rounded-lg shadow-lg p-8 hover:shadow-xl transition-shadow">
                <div className="text-center mb-6">
                  <div className="text-5xl mb-4">{service.icon}</div>
                  <span className="inline-block px-3 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800 mb-3">
                    {service.category}
                  </span>
                  <h3 className="text-xl font-bold text-gray-900 mb-2">{service.title}</h3>
                  <p className="text-gray-600">{service.description}</p>
                </div>

                <ul className="space-y-2 mb-6">
                  {service.features.map((feature, featureIndex) => (
                    <li key={featureIndex} className="flex items-center text-sm text-gray-600">
                      <svg className="w-4 h-4 mr-2 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                      {feature}
                    </li>
                  ))}
                </ul>

                <Link
                  href="/auth/register"
                  className="block w-full text-center px-4 py-2 font-medium rounded-lg text-white transition-colors"
                  style={{ backgroundColor: 'var(--brand-primary)' }}
                >
                  Learn More
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              How MiraiWorks Works
            </h2>
            <p className="text-xl text-gray-600">
              Simple steps to find talent or your next opportunity
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
            {/* For Job Seekers */}
            <div>
              <h3 className="text-2xl font-bold text-gray-900 mb-8 text-center">For Job Seekers</h3>
              <div className="space-y-6">
                <div className="flex items-start gap-4">
                  <div 
                    className="flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center text-white font-bold"
                    style={{ backgroundColor: 'var(--brand-primary)' }}
                  >
                    1
                  </div>
                  <div>
                    <h4 className="text-lg font-semibold text-gray-900 mb-1">Create Your Profile</h4>
                    <p className="text-gray-600">Build a comprehensive profile showcasing your skills, experience, and career goals.</p>
                  </div>
                </div>

                <div className="flex items-start gap-4">
                  <div 
                    className="flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center text-white font-bold"
                    style={{ backgroundColor: 'var(--brand-primary)' }}
                  >
                    2
                  </div>
                  <div>
                    <h4 className="text-lg font-semibold text-gray-900 mb-1">Get Matched</h4>
                    <p className="text-gray-600">Our AI analyzes your profile and matches you with relevant job opportunities.</p>
                  </div>
                </div>

                <div className="flex items-start gap-4">
                  <div 
                    className="flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center text-white font-bold"
                    style={{ backgroundColor: 'var(--brand-primary)' }}
                  >
                    3
                  </div>
                  <div>
                    <h4 className="text-lg font-semibold text-gray-900 mb-1">Apply & Interview</h4>
                    <p className="text-gray-600">Apply to jobs with one click and schedule interviews through our platform.</p>
                  </div>
                </div>

                <div className="flex items-start gap-4">
                  <div 
                    className="flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center text-white font-bold"
                    style={{ backgroundColor: 'var(--brand-primary)' }}
                  >
                    4
                  </div>
                  <div>
                    <h4 className="text-lg font-semibold text-gray-900 mb-1">Land Your Dream Job</h4>
                    <p className="text-gray-600">Get hired and start your new career journey with ongoing support.</p>
                  </div>
                </div>
              </div>
            </div>

            {/* For Employers */}
            <div>
              <h3 className="text-2xl font-bold text-gray-900 mb-8 text-center">For Employers</h3>
              <div className="space-y-6">
                <div className="flex items-start gap-4">
                  <div 
                    className="flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center text-white font-bold"
                    style={{ backgroundColor: 'var(--brand-primary)' }}
                  >
                    1
                  </div>
                  <div>
                    <h4 className="text-lg font-semibold text-gray-900 mb-1">Post Your Job</h4>
                    <p className="text-gray-600">Create detailed job postings with requirements, benefits, and company culture.</p>
                  </div>
                </div>

                <div className="flex items-start gap-4">
                  <div 
                    className="flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center text-white font-bold"
                    style={{ backgroundColor: 'var(--brand-primary)' }}
                  >
                    2
                  </div>
                  <div>
                    <h4 className="text-lg font-semibold text-gray-900 mb-1">Review Applications</h4>
                    <p className="text-gray-600">Use our filtering tools to find candidates that match your requirements.</p>
                  </div>
                </div>

                <div className="flex items-start gap-4">
                  <div 
                    className="flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center text-white font-bold"
                    style={{ backgroundColor: 'var(--brand-primary)' }}
                  >
                    3
                  </div>
                  <div>
                    <h4 className="text-lg font-semibold text-gray-900 mb-1">Schedule Interviews</h4>
                    <p className="text-gray-600">Coordinate interviews with integrated calendar and video conferencing tools.</p>
                  </div>
                </div>

                <div className="flex items-start gap-4">
                  <div 
                    className="flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center text-white font-bold"
                    style={{ backgroundColor: 'var(--brand-primary)' }}
                  >
                    4
                  </div>
                  <div>
                    <h4 className="text-lg font-semibold text-gray-900 mb-1">Make Great Hires</h4>
                    <p className="text-gray-600">Extend offers and onboard your new team members seamlessly.</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Simple, Transparent Pricing
            </h2>
            <p className="text-xl text-gray-600">
              Choose the plan that&apos;s right for you
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {pricingPlans.map((plan, index) => (
              <div 
                key={index} 
                className={`relative rounded-lg shadow-lg overflow-hidden ${
                  plan.popular ? 'ring-2 ring-blue-500' : ''
                }`}
              >
                {plan.popular && (
                  <div className="absolute top-0 right-0 bg-blue-500 text-white px-4 py-1 text-sm font-medium">
                    Most Popular
                  </div>
                )}
                
                <div className="bg-white p-8">
                  <h3 className="text-2xl font-bold text-gray-900 mb-2">{plan.name}</h3>
                  <div className="mb-4">
                    <span className="text-4xl font-bold text-gray-900">{plan.price}</span>
                    {plan.price !== 'Free' && plan.price !== 'Custom' && (
                      <span className="text-gray-600 ml-1">/month</span>
                    )}
                  </div>
                  <p className="text-gray-600 mb-6">{plan.description}</p>

                  <ul className="space-y-3 mb-8">
                    {plan.features.map((feature, featureIndex) => (
                      <li key={featureIndex} className="flex items-center text-sm text-gray-600">
                        <svg className="w-4 h-4 mr-2 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                        </svg>
                        {feature}
                      </li>
                    ))}
                  </ul>

                  <Link
                    href={plan.name === 'Enterprise' ? '/contact' : '/auth/register'}
                    className={`block w-full text-center px-4 py-3 font-medium rounded-lg transition-colors ${
                      plan.popular
                        ? 'text-white'
                        : 'border border-gray-300 text-gray-700 bg-white hover:bg-gray-50'
                    }`}
                    style={plan.popular ? { backgroundColor: 'var(--brand-primary)' } : {}}
                  >
                    {plan.cta}
                  </Link>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-16 bg-gray-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold text-white mb-4">
            Ready to Transform Your Hiring Process?
          </h2>
          <p className="text-xl text-gray-300 mb-8">
            Join thousands of companies and job seekers who trust MiraiWorks for their career success.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/auth/register"
              className="inline-flex items-center px-8 py-3 text-lg font-medium rounded-md text-white shadow-lg transition-colors"
              style={{ backgroundColor: 'var(--brand-primary)' }}
            >
              Get Started Today
            </Link>
            <Link
              href="/contact"
              className="inline-flex items-center px-8 py-3 text-lg font-medium rounded-md border border-gray-600 text-gray-300 bg-transparent hover:bg-gray-800 transition-colors"
            >
              Schedule Demo
            </Link>
          </div>
        </div>
      </section>
    </WebsiteLayout>
  );
}