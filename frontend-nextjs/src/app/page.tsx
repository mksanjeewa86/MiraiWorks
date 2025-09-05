export default function Home() {
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <div className="card-gradient p-12 text-center">
        <h1 className="text-4xl font-bold mb-4">
          <span className="gradient-text">MiraiWorks</span>
        </h1>
        <p className="text-xl mb-8" style={{ color: 'var(--text-secondary)' }}>
          Your Future Career Starts Here
        </p>
        <div className="flex gap-4 justify-center">
          <button className="btn btn-primary">
            Get Started
          </button>
          <button className="btn btn-secondary">
            Learn More
          </button>
        </div>
      </div>

      {/* Features Section */}
      <div className="p-12">
        <h2 className="text-3xl font-bold text-center mb-12" style={{ color: 'var(--text-primary)' }}>
          Why Choose MiraiWorks?
        </h2>
        
        <div className="grid md:grid-cols-3 gap-8">
          <div className="card p-6 text-center">
            <div className="text-4xl mb-4">🎯</div>
            <h3 className="text-xl font-semibold mb-3 text-brand-primary">
              Smart Job Matching
            </h3>
            <p style={{ color: 'var(--text-secondary)' }}>
              AI-powered matching connects you with the perfect opportunities
            </p>
          </div>
          
          <div className="card p-6 text-center">
            <div className="text-4xl mb-4">💼</div>
            <h3 className="text-xl font-semibold mb-3 text-brand-accent">
              Professional Growth
            </h3>
            <p style={{ color: 'var(--text-secondary)' }}>
              Track your career progress and unlock new opportunities
            </p>
          </div>
          
          <div className="card p-6 text-center">
            <div className="text-4xl mb-4">🚀</div>
            <h3 className="text-xl font-semibold mb-3 text-brand-muted">
              Fast & Modern
            </h3>
            <p style={{ color: 'var(--text-secondary)' }}>
              Built with Next.js for lightning-fast performance
            </p>
          </div>
        </div>
      </div>

      {/* Stats Section */}
      <div className="p-12">
        <div className="card p-8">
          <div className="grid md:grid-cols-3 gap-8 text-center">
            <div>
              <div className="text-3xl font-bold text-brand-primary mb-2">10,000+</div>
              <div style={{ color: 'var(--text-secondary)' }}>Active Jobs</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-brand-accent mb-2">50,000+</div>
              <div style={{ color: 'var(--text-secondary)' }}>Registered Users</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-brand-muted mb-2">95%</div>
              <div style={{ color: 'var(--text-secondary)' }}>Success Rate</div>
            </div>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="card-gradient p-12 text-center">
        <h2 className="text-3xl font-bold mb-4">
          Ready to Start Your Journey?
        </h2>
        <p className="text-xl mb-8" style={{ color: 'var(--text-secondary)' }}>
          Join thousands of professionals who found their dream job with MiraiWorks
        </p>
        <button className="btn btn-accent text-lg px-8 py-4">
          Sign Up Now
        </button>
      </div>
    </div>
  );
}
