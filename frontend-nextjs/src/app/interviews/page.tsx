'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import AppLayout from '@/components/layout/AppLayout';
import Card from '@/components/ui/Card';
import Badge from '@/components/ui/Badge';
import Button from '@/components/ui/Button';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import { Calendar, Clock, MapPin, Video, Phone, Users, Plus, Filter } from 'lucide-react';
import type { Interview } from '@/types';

export default function InterviewsPage() {
  const { user } = useAuth();
  const [interviews, setInterviews] = useState<Interview[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<'all' | 'upcoming' | 'completed' | 'cancelled'>('all');

  // Mock interview data
  const mockInterviews: Interview[] = [
    {
      id: '1',
      title: 'Senior Frontend Developer Interview',
      description: 'Technical interview for React/TypeScript position',
      scheduled_at: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(), // Tomorrow
      duration: 60,
      status: 'scheduled',
      interview_type: 'video',
      location: 'Zoom Meeting',
      meeting_url: 'https://zoom.us/j/123456789',
      company_name: 'TechCorp Inc.',
      candidate_name: 'John Doe',
      interviewer_name: 'Jane Smith',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    },
    {
      id: '2',
      title: 'Product Manager Discussion',
      description: 'Initial screening call for PM role',
      scheduled_at: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000).toISOString(), // Day after tomorrow
      duration: 45,
      status: 'scheduled',
      interview_type: 'phone',
      location: 'Phone Call',
      company_name: 'StartupCo',
      candidate_name: 'Sarah Wilson',
      interviewer_name: 'Mike Johnson',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    },
    {
      id: '3',
      title: 'Final Round Interview',
      description: 'Final interview with leadership team',
      scheduled_at: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(), // Yesterday
      duration: 90,
      status: 'completed',
      interview_type: 'in_person',
      location: 'Conference Room A, Main Office',
      company_name: 'Enterprise Corp',
      candidate_name: 'Alex Brown',
      interviewer_name: 'David Lee',
      notes: 'Great candidate, strong technical skills and cultural fit.',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    }
  ];

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
    if (filter === 'upcoming') return new Date(interview.scheduled_at) > new Date();
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
              onClick={() => setFilter(filterOption as any)}
            >
              {filterOption.charAt(0).toUpperCase() + filterOption.slice(1)}
            </Button>
          ))}
        </div>

        {/* Interviews Grid */}
        {filteredInterviews.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredInterviews.map(interview => {
              const { date, time } = formatDateTime(interview.scheduled_at);
              const isUpcoming = new Date(interview.scheduled_at) > new Date();
              
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
                        <span>{interview.duration} minutes</span>
                      </div>

                      <div className="flex items-center gap-2" style={{ color: 'var(--text-secondary)' }}>
                        <MapPin className="h-4 w-4" />
                        <span className="truncate">{interview.location}</span>
                      </div>
                    </div>

                    <div className="pt-3 border-t border-gray-200 dark:border-gray-700">
                      <div className="flex items-center justify-between text-sm">
                        <div style={{ color: 'var(--text-secondary)' }}>
                          <span className="font-medium">Interviewer:</span> {interview.interviewer_name}
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