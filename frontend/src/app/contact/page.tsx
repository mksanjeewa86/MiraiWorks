'use client';

import { useState } from 'react';
import WebsiteLayout from '@/components/website/WebsiteLayout';

export default function ContactPage() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    subject: '',
    message: '',
    type: 'general'
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Handle form submission
    alert('Thank you for your message! We\'ll get back to you soon.');
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  return (
    <WebsiteLayout>
      {/* Hero Section */}
      <section className="py-24 bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 relative overflow-hidden">
        {/* Background Pattern */}
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiM5Q0EzQUYiIGZpbGwtb3BhY2l0eT0iMC4xIj48Y2lyY2xlIGN4PSIzMCIgY3k9IjMwIiByPSI0Ii8+PC9nPjwvZz48L3N2Zz4=')] opacity-30"></div>

        {/* Floating Elements */}
        <div className="absolute top-20 left-10 w-64 h-64 bg-blue-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-float"></div>
        <div className="absolute bottom-20 right-10 w-64 h-64 bg-cyan-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-float animation-delay-2000"></div>

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="animate-fade-in-up">
            <span className="inline-block px-4 py-2 text-sm font-semibold text-blue-300 bg-blue-500/20 rounded-full mb-8">
              Get In Touch
            </span>
            <h1 className="text-5xl md:text-6xl font-bold text-white mb-8">
              Contact
              <span className="block bg-gradient-to-r from-blue-400 via-cyan-400 to-teal-400 bg-clip-text text-transparent">
                Our Team
              </span>
            </h1>
            <p className="text-xl md:text-2xl text-blue-100 max-w-4xl mx-auto leading-relaxed">
              Have questions? We&apos;d love to hear from you. Get in touch and we&apos;ll respond
              as soon as possible with personalized assistance.
            </p>
          </div>
        </div>
      </section>

      <section className="py-24 bg-gradient-to-b from-white to-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-16">
            {/* Contact Information */}
            <div className="animate-slide-in-left">
              <div className="mb-12">
                <span className="inline-block px-4 py-2 text-sm font-semibold text-cyan-600 bg-cyan-100 rounded-full mb-6">
                  Contact Information
                </span>
                <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
                  Let&apos;s Start a
                  <span className="block bg-gradient-to-r from-cyan-600 to-blue-600 bg-clip-text text-transparent">
                    Conversation
                  </span>
                </h2>
                <p className="text-xl text-gray-600">
                  We&apos;re here to help you succeed. Reach out through any of these channels.
                </p>
              </div>
              
              <div className="space-y-6">
                <div className="group relative">
                  <div className="absolute inset-0 bg-gradient-to-r from-green-400 to-blue-400 rounded-3xl blur-lg opacity-25 group-hover:opacity-40 transition duration-300"></div>
                  <div className="relative bg-white rounded-3xl p-6 shadow-xl border border-gray-100 hover:shadow-2xl transition-all duration-300 transform group-hover:-translate-y-1">
                    <div className="flex items-start gap-4">
                      <div className="flex-shrink-0 w-16 h-16 rounded-2xl bg-gradient-to-r from-green-500 to-blue-500 flex items-center justify-center shadow-lg">
                        <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                        </svg>
                      </div>
                      <div>
                        <h3 className="text-xl font-bold text-gray-900 mb-2">Phone</h3>
                        <p className="text-lg text-gray-700 font-semibold">+1 (555) 123-4567</p>
                        <p className="text-sm text-gray-500 mt-1">Mon-Fri 9am-6pm PST</p>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="group relative">
                  <div className="absolute inset-0 bg-gradient-to-r from-purple-400 to-pink-400 rounded-3xl blur-lg opacity-25 group-hover:opacity-40 transition duration-300"></div>
                  <div className="relative bg-white rounded-3xl p-6 shadow-xl border border-gray-100 hover:shadow-2xl transition-all duration-300 transform group-hover:-translate-y-1">
                    <div className="flex items-start gap-4">
                      <div className="flex-shrink-0 w-16 h-16 rounded-2xl bg-gradient-to-r from-purple-500 to-pink-500 flex items-center justify-center shadow-lg">
                        <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                        </svg>
                      </div>
                      <div>
                        <h3 className="text-xl font-bold text-gray-900 mb-2">Email</h3>
                        <p className="text-lg text-gray-700 font-semibold">hello@miraiworks.com</p>
                        <p className="text-sm text-gray-500 mt-1">We&apos;ll respond within 24 hours</p>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="group relative">
                  <div className="absolute inset-0 bg-gradient-to-r from-cyan-400 to-blue-400 rounded-3xl blur-lg opacity-25 group-hover:opacity-40 transition duration-300"></div>
                  <div className="relative bg-white rounded-3xl p-6 shadow-xl border border-gray-100 hover:shadow-2xl transition-all duration-300 transform group-hover:-translate-y-1">
                    <div className="flex items-start gap-4">
                      <div className="flex-shrink-0 w-16 h-16 rounded-2xl bg-gradient-to-r from-cyan-500 to-blue-500 flex items-center justify-center shadow-lg">
                        <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                        </svg>
                      </div>
                      <div>
                        <h3 className="text-xl font-bold text-gray-900 mb-2">Office</h3>
                        <p className="text-lg text-gray-700 font-semibold">
                          123 Innovation Drive<br />
                          San Francisco, CA 94105
                        </p>
                        <p className="text-sm text-gray-500 mt-1">Visitors by appointment only</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* FAQ Section */}
              <div className="mt-16">
                <h3 className="text-3xl font-bold text-gray-900 mb-8 bg-gradient-to-r from-gray-900 to-gray-600 bg-clip-text text-transparent">Frequently Asked Questions</h3>
                <div className="space-y-4">
                  <details className="group">
                    <summary className="flex justify-between items-center font-semibold cursor-pointer list-none p-6 bg-gradient-to-r from-blue-50 to-cyan-50 rounded-2xl border border-blue-100 hover:from-blue-100 hover:to-cyan-100 transition-all duration-300">
                      <span className="text-gray-900">How do I post a job?</span>
                      <span className="transition-transform duration-300 group-open:rotate-180 text-blue-600">
                        <svg fill="none" height="24" shapeRendering="geometricPrecision" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" width="24">
                          <path d="m6 9 6 6 6-6"></path>
                        </svg>
                      </span>
                    </summary>
                    <div className="mt-4 p-6 bg-white rounded-2xl border border-gray-100 shadow-sm">
                      <p className="text-gray-600 leading-relaxed">
                        Simply create an employer account, fill out your job details, and publish. Your job will be visible to thousands of qualified candidates immediately.
                      </p>
                    </div>
                  </details>

                  <details className="group">
                    <summary className="flex justify-between items-center font-semibold cursor-pointer list-none p-6 bg-gradient-to-r from-purple-50 to-pink-50 rounded-2xl border border-purple-100 hover:from-purple-100 hover:to-pink-100 transition-all duration-300">
                      <span className="text-gray-900">Is MiraiWorks free for job seekers?</span>
                      <span className="transition-transform duration-300 group-open:rotate-180 text-purple-600">
                        <svg fill="none" height="24" shapeRendering="geometricPrecision" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" width="24">
                          <path d="m6 9 6 6 6-6"></path>
                        </svg>
                      </span>
                    </summary>
                    <div className="mt-4 p-6 bg-white rounded-2xl border border-gray-100 shadow-sm">
                      <p className="text-gray-600 leading-relaxed">
                        Yes! Creating a profile, browsing jobs, and applying is completely free for job seekers. We make money from employers who post jobs.
                      </p>
                    </div>
                  </details>

                  <details className="group">
                    <summary className="flex justify-between items-center font-semibold cursor-pointer list-none p-6 bg-gradient-to-r from-green-50 to-teal-50 rounded-2xl border border-green-100 hover:from-green-100 hover:to-teal-100 transition-all duration-300">
                      <span className="text-gray-900">How does the matching algorithm work?</span>
                      <span className="transition-transform duration-300 group-open:rotate-180 text-green-600">
                        <svg fill="none" height="24" shapeRendering="geometricPrecision" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" width="24">
                          <path d="m6 9 6 6 6-6"></path>
                        </svg>
                      </span>
                    </summary>
                    <div className="mt-4 p-6 bg-white rounded-2xl border border-gray-100 shadow-sm">
                      <p className="text-gray-600 leading-relaxed">
                        Our AI analyzes your skills, experience, preferences, and career goals to match you with relevant opportunities. The more complete your profile, the better the matches.
                      </p>
                    </div>
                  </details>
                </div>
              </div>
            </div>

            {/* Contact Form */}
            <div className="animate-slide-in-right">
              <div className="group relative">
                <div className="absolute inset-0 bg-gradient-to-r from-blue-400 to-purple-400 rounded-3xl blur-lg opacity-25 group-hover:opacity-40 transition duration-1000 group-hover:duration-200"></div>
                <div className="relative bg-white rounded-3xl shadow-2xl border border-gray-100 p-8 lg:p-10">
                  <div className="mb-8">
                    <span className="inline-block px-4 py-2 text-sm font-semibold text-blue-600 bg-blue-100 rounded-full mb-4">
                      Contact Form
                    </span>
                    <h2 className="text-3xl font-bold text-gray-900 mb-4">
                      Send us a
                      <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                        Message
                      </span>
                    </h2>
                    <p className="text-gray-600">
                      Fill out the form below and we&apos;ll get back to you as soon as possible.
                    </p>
                  </div>
                
                <form onSubmit={handleSubmit} className="space-y-8">
                  <div>
                    <label htmlFor="type" className="block text-sm font-bold text-gray-700 mb-3">
                      What can we help you with?
                    </label>
                    <select
                      id="type"
                      name="type"
                      value={formData.type}
                      onChange={handleChange}
                      className="w-full px-4 py-4 pr-8 border-2 border-gray-200 rounded-2xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 appearance-none bg-white text-gray-900 font-medium transition-all duration-300 hover:border-gray-300"
                      style={{
                        backgroundImage: `url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%233b82f6' stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M6 8l4 4 4-4'/%3e%3c/svg%3e")`,
                        backgroundPosition: 'right 16px center',
                        backgroundRepeat: 'no-repeat',
                        backgroundSize: '20px'
                      }}
                    >
                      <option value="general">General Inquiry</option>
                      <option value="support">Technical Support</option>
                      <option value="sales">Sales Question</option>
                      <option value="partnership">Partnership Opportunity</option>
                      <option value="press">Press Inquiry</option>
                    </select>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label htmlFor="name" className="block text-sm font-bold text-gray-700 mb-3">
                        Name *
                      </label>
                      <input
                        type="text"
                        id="name"
                        name="name"
                        value={formData.name}
                        onChange={handleChange}
                        required
                        className="w-full px-4 py-4 border-2 border-gray-200 rounded-2xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-300 hover:border-gray-300 font-medium"
                        placeholder="Your full name"
                      />
                    </div>

                    <div>
                      <label htmlFor="email" className="block text-sm font-bold text-gray-700 mb-3">
                        Email *
                      </label>
                      <input
                        type="email"
                        id="email"
                        name="email"
                        value={formData.email}
                        onChange={handleChange}
                        required
                        className="w-full px-4 py-4 border-2 border-gray-200 rounded-2xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-300 hover:border-gray-300 font-medium"
                        placeholder="your.email@example.com"
                      />
                    </div>
                  </div>

                  <div>
                    <label htmlFor="subject" className="block text-sm font-bold text-gray-700 mb-3">
                      Subject *
                    </label>
                    <input
                      type="text"
                      id="subject"
                      name="subject"
                      value={formData.subject}
                      onChange={handleChange}
                      required
                      className="w-full px-4 py-4 border-2 border-gray-200 rounded-2xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-300 hover:border-gray-300 font-medium"
                      placeholder="What is this regarding?"
                    />
                  </div>

                  <div>
                    <label htmlFor="message" className="block text-sm font-bold text-gray-700 mb-3">
                      Message *
                    </label>
                    <textarea
                      id="message"
                      name="message"
                      rows={6}
                      value={formData.message}
                      onChange={handleChange}
                      required
                      className="w-full px-4 py-4 border-2 border-gray-200 rounded-2xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-300 hover:border-gray-300 resize-none font-medium"
                      placeholder="Tell us more about your inquiry... We'd love to hear from you!"
                    />
                  </div>

                  <button
                    type="submit"
                    className="group w-full px-8 py-5 text-xl font-bold rounded-2xl text-white bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 transition-all duration-300 transform hover:scale-105 shadow-xl"
                  >
                    Send Message
                    <svg className="inline-block ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                    </svg>
                  </button>

                  <p className="text-sm text-gray-500 text-center leading-relaxed">
                    By submitting this form, you agree to our privacy policy. We&apos;ll never share your information with third parties.
                  </p>
                </form>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </WebsiteLayout>
  );
}