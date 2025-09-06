'use client';

import { useState, useEffect } from 'react';
import AppLayout from '@/components/layout/AppLayout';
import Card from '@/components/ui/Card';
import Badge from '@/components/ui/Badge';
import Button from '@/components/ui/Button';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import { Calendar, Clock, MapPin, Video, Phone, Users, Plus, Filter } from 'lucide-react';
import type { Interview } from '@/types';

// Mock interview data - moved outside component to prevent re-creation
const mockInterviews: Interview[] = [
  {
    id: 1,
    candidate_id: 101,
    recruiter_id: 201,
    employer_company_id: 301,
    title: 'Senior Frontend Developer Interview',
    description: 'Technical interview for React/TypeScript position',
    position_title: 'Senior Frontend Developer',
    status: 'scheduled',
    interview_type: 'video',
    scheduled_start: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(),
    scheduled_end: new Date(Date.now() + 24 * 60 * 60 * 1000 + 60 * 60 * 1000).toISOString(), // 1 hour later
    scheduled_at: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(), // Tomorrow
    timezone: 'America/New_York',
    location: 'Zoom Meeting',
    meeting_url: 'https://zoom.us/j/123456789',
    duration_minutes: 60,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    candidate: {
      id: 101,
      email: 'john.doe@email.com',
      first_name: 'John',
      last_name: 'Doe',
      full_name: 'John Doe',
      company_id: 401,
      is_active: true,
      is_admin: false,
      require_2fa: false,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      roles: [],
      company: {
        id: 401,
        name: 'Candidate Corp',
        domain: 'candidatecorp.com',
        is_active: true,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      }
    },
    recruiter: {
      id: 201,
      email: 'jane.smith@techcorp.com',
      first_name: 'Jane',
      last_name: 'Smith',
      full_name: 'Jane Smith',
      company_id: 301,
      is_active: true,
      is_admin: false,
      require_2fa: false,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      roles: [],
      company: {
        id: 301,
        name: 'TechCorp Inc.',
        domain: 'techcorp.com',
        is_active: true,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      }
    },
    candidate_name: 'John Doe',
    company_name: 'TechCorp Inc.',
    proposals: [],
    active_proposal_count: 0
  },
  {
    id: 2,
    candidate_id: 102,
    recruiter_id: 202,
    employer_company_id: 302,
    title: 'Product Manager Discussion',
    description: 'Initial screening call for PM role',
    position_title: 'Product Manager',
    status: 'scheduled',
    interview_type: 'phone',
    scheduled_start: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000).toISOString(),
    scheduled_end: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000 + 45 * 60 * 1000).toISOString(), // 45 minutes later
    scheduled_at: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000).toISOString(), // Day after tomorrow
    timezone: 'America/Los_Angeles',
    location: 'Phone Call',
    duration_minutes: 45,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    candidate: {
      id: 102,
      email: 'sarah.wilson@email.com',
      first_name: 'Sarah',
      last_name: 'Wilson',
      full_name: 'Sarah Wilson',
      company_id: 402,
      is_active: true,
      is_admin: false,
      require_2fa: false,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      roles: [],
      company: {
        id: 402,
        name: 'Wilson Consulting',
        domain: 'wilsonconsulting.com',
        is_active: true,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      }
    },
    recruiter: {
      id: 202,
      email: 'mike.johnson@startupco.com',
      first_name: 'Mike',
      last_name: 'Johnson',
      full_name: 'Mike Johnson',
      company_id: 302,
      is_active: true,
      is_admin: false,
      require_2fa: false,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      roles: [],
      company: {
        id: 302,
        name: 'StartupCo',
        domain: 'startupco.com',
        is_active: true,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      }
    },
    candidate_name: 'Sarah Wilson',
    company_name: 'StartupCo',
    proposals: [],
    active_proposal_count: 0
  },
  {
    id: 3,
    candidate_id: 103,
    recruiter_id: 203,
    employer_company_id: 303,
    title: 'Final Round Interview',
    description: 'Final interview with leadership team',
    position_title: 'Senior Software Engineer',
    status: 'completed',
    interview_type: 'in_person',
    scheduled_start: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
    scheduled_end: new Date(Date.now() - 24 * 60 * 60 * 1000 + 90 * 60 * 1000).toISOString(), // 90 minutes later
    scheduled_at: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(), // Yesterday
    timezone: 'America/Chicago',
    location: 'Conference Room A, Main Office',
    duration_minutes: 90,
    notes: 'Great candidate, strong technical skills and cultural fit.',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    candidate: {
      id: 103,
      email: 'alex.brown@email.com',
      first_name: 'Alex',
      last_name: 'Brown',
      full_name: 'Alex Brown',
      company_id: 403,
      is_active: true,
      is_admin: false,
      require_2fa: false,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      roles: [],
      company: {
        id: 403,
        name: 'Brown Tech Solutions',
        domain: 'browntech.com',
        is_active: true,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      }
    },
    recruiter: {
      id: 203,
      email: 'david.lee@enterprise.com',
      first_name: 'David',
      last_name: 'Lee',
      full_name: 'David Lee',
      company_id: 303,
      is_active: true,
      is_admin: false,
      require_2fa: false,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      roles: [],
      company: {
        id: 303,
        name: 'Enterprise Corp',
        domain: 'enterprise.com',
        is_active: true,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      }
    },
    candidate_name: 'Alex Brown',
    company_name: 'Enterprise Corp',
    proposals: [],
    active_proposal_count: 0
  }
];

export default function InterviewsPage() {
  const [interviews, setInterviews] = useState<Interview[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<'all' | 'upcoming' | 'completed' | 'cancelled'>('all');

  useEffect(() => {
    // Simulate loading interviews
    setTimeout(() => {
      setInterviews(mockInterviews);
      setLoading(false);
    }, 1000);
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'scheduled':
        return 'primary';
      case 'completed':
        return 'success';
      case 'cancelled':
        return 'error';
      default:
        return 'secondary';
    }
  };

  const getInterviewTypeIcon = (type: string) => {
    switch (type) {
      case 'video':
        return <Video className="h-4 w-4" />;
      case 'phone':
        return <Phone className="h-4 w-4" />;
      case 'in_person':
        return <Users className="h-4 w-4" />;
      default:
        return <Calendar className="h-4 w-4" />;
    }
  };

  const formatDateTime = (dateString: string) => {
    const date = new Date(dateString);
    return {
      date: date.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' }),
      time: date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
    };
  };

  const filteredInterviews = interviews.filter(interview => {
    if (filter === 'all') return true;
    if (filter === 'upcoming') return interview.scheduled_at && new Date(interview.scheduled_at) > new Date();
    if (filter === 'completed') return interview.status === 'completed';
    if (filter === 'cancelled') return interview.status === 'cancelled';
    return true;
  });

  if (loading) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center h-64">
          <LoadingSpinner className="w-8 h-8" />
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout>
      <div className="p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold" style={{ color: 'var(--text-primary)' }}>Interviews</h1>
            <p className="mt-1" style={{ color: 'var(--text-secondary)' }}>
              Manage your interview schedule and track progress
            </p>
          </div>
          <Button className="flex items-center gap-2">
            <Plus className="h-4 w-4" />
            Schedule Interview
          </Button>
        </div>

        {/* Filters */}
        <div className="flex items-center gap-4 mb-6">
          <div className="flex items-center gap-2">
            <Filter className="h-4 w-4" style={{ color: 'var(--text-muted)' }} />
            <span className="text-sm" style={{ color: 'var(--text-secondary)' }}>Filter:</span>
          </div>
          {['all', 'upcoming', 'completed', 'cancelled'].map((filterOption) => (
            <Button
              key={filterOption}
              variant={filter === filterOption ? 'primary' : 'outline'}
              size="sm"
              onClick={() => setFilter(filterOption as 'all' | 'upcoming' | 'completed' | 'cancelled')}
            >
              {filterOption.charAt(0).toUpperCase() + filterOption.slice(1)}
            </Button>
          ))}
        </div>

        {/* Interviews Grid */}
        {filteredInterviews.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredInterviews.map(interview => {
              const { date, time } = interview.scheduled_at ? formatDateTime(interview.scheduled_at) : { date: 'TBD', time: 'TBD' };
              const isUpcoming = interview.scheduled_at ? new Date(interview.scheduled_at) > new Date() : false;
              
              return (
                <Card key={interview.id} className="p-6 hover:shadow-md transition-shadow cursor-pointer">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-2">
                      {getInterviewTypeIcon(interview.interview_type)}
                      <Badge variant={getStatusColor(interview.status)}>
                        {interview.status}
                      </Badge>
                    </div>
                    <div className="text-right text-sm" style={{ color: 'var(--text-muted)' }}>
                      <div>{date}</div>
                      <div className="font-medium">{time}</div>
                    </div>
                  </div>

                  <div className="space-y-3">
                    <div>
                      <h3 className="font-semibold text-lg" style={{ color: 'var(--text-primary)' }}>
                        {interview.title}
                      </h3>
                      <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                        {interview.description}
                      </p>
                    </div>

                    <div className="space-y-2 text-sm">
                      <div className="flex items-center gap-2" style={{ color: 'var(--text-secondary)' }}>
                        <Users className="h-4 w-4" />
                        <span>{interview.company_name}</span>
                      </div>
                      
                      <div className="flex items-center gap-2" style={{ color: 'var(--text-secondary)' }}>
                        <Clock className="h-4 w-4" />
                        <span>{interview.duration_minutes} minutes</span>
                      </div>

                      <div className="flex items-center gap-2" style={{ color: 'var(--text-secondary)' }}>
                        <MapPin className="h-4 w-4" />
                        <span className="truncate">{interview.location}</span>
                      </div>
                    </div>

                    <div className="pt-3 border-t border-gray-200 dark:border-gray-700">
                      <div className="flex items-center justify-between text-sm">
                        <div style={{ color: 'var(--text-secondary)' }}>
                          <span className="font-medium">Recruiter:</span> {interview.recruiter.full_name}
                        </div>
                      </div>
                      <div className="flex items-center justify-between text-sm mt-1">
                        <div style={{ color: 'var(--text-secondary)' }}>
                          <span className="font-medium">Candidate:</span> {interview.candidate_name}
                        </div>
                      </div>
                    </div>

                    {/* Action Buttons */}
                    <div className="flex gap-2 pt-2">
                      {isUpcoming ? (
                        <>
                          <Button size="sm" className="flex-1">
                            Join
                          </Button>
                          <Button variant="outline" size="sm" className="flex-1">
                            Reschedule
                          </Button>
                        </>
                      ) : (
                        <>
                          <Button variant="outline" size="sm" className="flex-1">
                            View Details
                          </Button>
                          {interview.status === 'completed' && (
                            <Button variant="outline" size="sm" className="flex-1">
                              Add Notes
                            </Button>
                          )}
                        </>
                      )}
                    </div>

                    {interview.notes && (
                      <div className="pt-2 border-t border-gray-200 dark:border-gray-700">
                        <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                          <span className="font-medium">Notes:</span> {interview.notes}
                        </p>
                      </div>
                    )}
                  </div>
                </Card>
              );
            })}
          </div>
        ) : (
          <Card className="p-12 text-center">
            <Calendar className="h-16 w-16 mx-auto mb-4" style={{ color: 'var(--text-muted)' }} />
            <h3 className="text-lg font-semibold mb-2" style={{ color: 'var(--text-primary)' }}>
              No interviews found
            </h3>
            <p className="mb-6" style={{ color: 'var(--text-secondary)' }}>
              {filter === 'all' 
                ? "You don't have any interviews scheduled yet."
                : `No ${filter} interviews found.`
              }
            </p>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Schedule Your First Interview
            </Button>
          </Card>
        )}
      </div>
    </AppLayout>
  );
}