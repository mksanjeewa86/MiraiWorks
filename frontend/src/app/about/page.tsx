import Link from 'next/link';
import WebsiteLayout from '@/components/website/WebsiteLayout';

export default function AboutPage() {
  const teamMembers = [
    {
      name: 'Alex Thompson',
      role: 'CEO & Founder',
      image: '👨‍💼',
      bio: 'Passionate about connecting talent with opportunities. Former VP at top tech companies.'
    },
    {
      name: 'Sarah Chen',
      role: 'CTO',
      image: '👩‍💻',
      bio: 'Full-stack engineer with 10+ years building scalable platforms. AI and ML enthusiast.'
    },
    {
      name: 'Michael Rodriguez',
      role: 'Head of Product',
      image: '👨‍🎯',
      bio: 'Product strategist focused on user experience and market-driven solutions.'
    },
    {
      name: 'Emily Johnson',
      role: 'VP of Marketing',
      image: '👩‍📊',
      bio: 'Growth marketing expert helping companies and candidates find each other.'
    }
  ];

  return (
    <WebsiteLayout>
      {/* Hero Section */}
      <section className="py-20 bg-gradient-to-br from-blue-50 via-white to-purple-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
              About MiraiWorks
            </h1>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              We&apos;re building the future of work by connecting talented individuals with 
              innovative companies through our comprehensive HR and recruitment platform.
            </p>
          </div>
        </div>
      </section>

      {/* Mission Section */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl font-bold text-gray-900 mb-6">Our Mission</h2>
              <p className="text-lg text-gray-600 mb-6 leading-relaxed">
                At MiraiWorks, we believe that finding the right job or the perfect candidate 
                shouldn&apos;t be left to chance. Our mission is to revolutionize the recruitment 
                process by leveraging cutting-edge technology and human insights.
              </p>
              <p className="text-lg text-gray-600 mb-8 leading-relaxed">
                We&apos;re committed to creating meaningful connections between job seekers and 
                employers, fostering career growth, and building stronger teams that drive 
                innovation and success.
              </p>
              <Link
                href="/contact"
                className="inline-flex items-center px-6 py-3 font-medium rounded-md text-white shadow-lg transition-colors"
                style={{ backgroundColor: 'var(--brand-primary)' }}
              >
                Get in Touch
              </Link>
            </div>
            <div className="bg-gray-100 rounded-lg p-8">
              <div className="text-6xl mb-4 text-center">🎯</div>
              <h3 className="text-2xl font-bold text-gray-900 mb-4 text-center">Our Vision</h3>
              <p className="text-gray-600 text-center">
                To become the world&apos;s most trusted platform for career development and 
                talent acquisition, where every professional finds their perfect match.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Values Section */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">Our Values</h2>
            <p className="text-xl text-gray-600">
              The principles that guide everything we do
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="bg-white p-8 rounded-lg shadow-sm">
              <div className="text-4xl mb-4">🤝</div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">Trust & Transparency</h3>
              <p className="text-gray-600">
                We build trust through honest communication, transparent processes, 
                and reliable service that both job seekers and employers can count on.
              </p>
            </div>

            <div className="bg-white p-8 rounded-lg shadow-sm">
              <div className="text-4xl mb-4">🚀</div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">Innovation</h3>
              <p className="text-gray-600">
                We continuously evolve our platform with the latest technology, 
                from AI-powered matching to seamless user experiences.
              </p>
            </div>

            <div className="bg-white p-8 rounded-lg shadow-sm">
              <div className="text-4xl mb-4">🎯</div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">Quality Matches</h3>
              <p className="text-gray-600">
                We focus on quality over quantity, ensuring that every connection 
                we facilitate has the potential for long-term success.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Team Section */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">Meet Our Team</h2>
            <p className="text-xl text-gray-600">
              The passionate individuals behind MiraiWorks
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {teamMembers.map((member, index) => (
              <div key={index} className="text-center">
                <div className="bg-gray-100 rounded-full w-32 h-32 flex items-center justify-center mx-auto mb-4">
                  <span className="text-6xl">{member.image}</span>
                </div>
                <h3 className="text-xl font-bold text-gray-900 mb-2">{member.name}</h3>
                <p className="text-gray-600 font-medium mb-3">{member.role}</p>
                <p className="text-sm text-gray-500">{member.bio}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 bg-gray-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-white mb-4">Our Impact</h2>
            <p className="text-xl text-gray-300">
              Numbers that showcase our success
            </p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            <div className="text-center">
              <div className="text-4xl font-bold text-white mb-2">10,000+</div>
              <div className="text-gray-400">Active Jobs</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-white mb-2">50,000+</div>
              <div className="text-gray-400">Job Seekers</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-white mb-2">2,500+</div>
              <div className="text-gray-400">Companies</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-white mb-2">95%</div>
              <div className="text-gray-400">Success Rate</div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 bg-blue-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Ready to Join the MiraiWorks Community?
          </h2>
          <p className="text-xl text-gray-600 mb-8">
            Whether you&apos;re looking for your next opportunity or searching for top talent, 
            we&apos;re here to help.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
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
              Sign Up Today
            </Link>
          </div>
        </div>
      </section>
    </WebsiteLayout>
  );
}