import { useState, useEffect } from 'react';
import { 
  Briefcase, 
  Calendar, 
  MessageSquare, 
  FileText, 
  TrendingUp,
  Clock,
  CheckCircle,
  AlertCircle
} from 'lucide-react';
import StatCard from '../common/StatCard';
import { SimpleLineChart, SimpleBarChart } from './Charts';

interface CandidateStats {
  activeApplications: number;
  upcomingInterviews: number;
  unreadMessages: number;
  resumeCompleteness: number;
  totalApplications: number;
  interviewsCompleted: number;
  offersReceived: number;
}

interface ApplicationActivity {
  name: string;
  applications: number;
  interviews: number;
}

interface RecentActivity {
  id: number;
  type: 'application' | 'interview' | 'message' | 'offer';
  title: string;
  description: string;
  time: string;
  status?: 'pending' | 'completed' | 'scheduled';
}

export default function CandidateOverview() {
  const [stats, setStats] = useState<CandidateStats | null>(null);
  const [activityData, setActivityData] = useState<ApplicationActivity[]>([]);
  const [recentActivity, setRecentActivity] = useState<RecentActivity[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulate API call
    const fetchData = async () => {
      try {
        // Mock data - replace with real API calls
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        setStats({
          activeApplications: 12,
          upcomingInterviews: 3,
          unreadMessages: 5,
          resumeCompleteness: 85,
          totalApplications: 47,
          interviewsCompleted: 8,
          offersReceived: 2
        });

        setActivityData([
          { name: 'Jan', applications: 4, interviews: 1 },
          { name: 'Feb', applications: 8, interviews: 2 },
          { name: 'Mar', applications: 12, interviews: 4 },
          { name: 'Apr', applications: 15, interviews: 6 },
          { name: 'May', applications: 18, interviews: 8 },
          { name: 'Jun', applications: 22, interviews: 10 }
        ]);

        setRecentActivity([
          {
            id: 1,
            type: 'interview',
            title: 'Technical Interview',
            description: 'Senior React Developer at TechCorp',
            time: '2 hours ago',
            status: 'scheduled'
          },
          {
            id: 2,
            type: 'application',
            title: 'Application Submitted',
            description: 'Full Stack Engineer at StartupXYZ',
            time: '1 day ago',
            status: 'pending'
          },
          {
            id: 3,
            type: 'message',
            title: 'New Message',
            description: 'From Sarah (Recruiter) at InnovateInc',
            time: '2 days ago',
            status: 'pending'
          },
          {
            id: 4,
            type: 'offer',
            title: 'Job Offer Received',
            description: 'Frontend Developer at DesignStudio',
            time: '3 days ago',
            status: 'pending'
          }
        ]);
      } catch (error) {
        console.error('Error fetching candidate data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const getActivityIcon = (type: string, status?: string) => {
    switch (type) {
      case 'application':
        return <Briefcase className="h-5 w-5" />;
      case 'interview':
        return <Calendar className="h-5 w-5" />;
      case 'message':
        return <MessageSquare className="h-5 w-5" />;
      case 'offer':
        return <CheckCircle className="h-5 w-5" />;
      default:
        return <AlertCircle className="h-5 w-5" />;
    }
  };

  const getStatusColor = (status?: string) => {
    switch (status) {
      case 'completed':
        return 'text-accent-600 dark:text-accent-400';
      case 'scheduled':
        return 'text-blue-600 dark:text-blue-400';
      case 'pending':
        return 'text-orange-600 dark:text-orange-400';
      default:
        return 'text-muted-600 dark:text-muted-400';
    }
  };

  return (
    <div className="space-y-6">
      {/* Welcome Header */}
      <div className="card-gradient rounded-2xl p-6">
        <h1 className="text-2xl font-bold mb-2" style={{ color: 'var(--text-primary)' }}>
          Welcome back! 👋
        </h1>
        <p style={{ color: 'var(--text-secondary)' }}>
          Here's what's happening with your job search today.
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Active Applications"
          value={stats?.activeApplications || 0}
          icon={Briefcase}
          change={{ value: 15, trend: 'up', period: 'last week' }}
          color="primary"
          loading={loading}
        />
        <StatCard
          title="Upcoming Interviews"
          value={stats?.upcomingInterviews || 0}
          icon={Calendar}
          change={{ value: 2, trend: 'up', period: 'this week' }}
          color="blue"
          loading={loading}
        />
        <StatCard
          title="Unread Messages"
          value={stats?.unreadMessages || 0}
          icon={MessageSquare}
          color="orange"
          loading={loading}
        />
        <StatCard
          title="Resume Completeness"
          value={stats ? `${stats.resumeCompleteness}%` : '0%'}
          icon={FileText}
          change={{ value: 10, trend: 'up', period: 'last update' }}
          color="accent"
          loading={loading}
        />
      </div>

      {/* Charts Section */}
      <div className="grid lg:grid-cols-2" style={{ gap: '24px' }}>
        {/* Application Activity Chart */}
        <div className="card p-6">
          <div className="flex items-center justify-between" style={{ marginBottom: '24px' }}>
            <div>
              <h3 className="text-lg font-semibold" style={{ color: 'var(--text-primary)' }}>
                Application Activity
              </h3>
              <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                Applications and interviews over time
              </p>
            </div>
            <TrendingUp className="text-brand-primary" style={{ width: '20px', height: '20px' }} />
          </div>
          
          {loading ? (
            <div className="loading-skeleton" style={{ height: '250px' }} />
          ) : (
            <SimpleLineChart
              data={activityData}
              dataKey="applications"
              height={250}
              color="var(--brand-primary)"
            />
          )}
        </div>

        {/* Interview Pipeline */}
        <div className="card p-6">
          <div className="flex items-center justify-between" style={{ marginBottom: '24px' }}>
            <div>
              <h3 className="text-lg font-semibold" style={{ color: 'var(--text-primary)' }}>
                Interview Pipeline
              </h3>
              <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                Current interview stages
              </p>
            </div>
            <Calendar style={{ color: '#3B82F6', width: '20px', height: '20px' }} />
          </div>
          
          {loading ? (
            <div className="loading-skeleton" style={{ height: '250px' }} />
          ) : (
            <SimpleBarChart
              data={[
                { name: 'Applied', value: 12 },
                { name: 'Screening', value: 8 },
                { name: 'Interview', value: 5 },
                { name: 'Final', value: 3 },
                { name: 'Offer', value: 2 }
              ]}
              height={250}
              color="#3B82F6"
            />
          )}
        </div>
      </div>

      {/* Recent Activity */}
      <div className="card p-6">
        <div className="flex items-center justify-between" style={{ marginBottom: '24px' }}>
          <div>
            <h3 className="text-lg font-semibold" style={{ color: 'var(--text-primary)' }}>
              Recent Activity
            </h3>
            <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
              Your latest job search updates
            </p>
          </div>
          <Clock style={{ width: '20px', height: '20px', color: 'var(--text-muted)' }} />
        </div>

        {loading ? (
          <div className="space-y-4">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="flex items-center p-4 rounded-xl" style={{ gap: '16px', backgroundColor: 'var(--bg-secondary)' }}>
                <div className="loading-skeleton" style={{ width: '40px', height: '40px', borderRadius: '50%' }} />
                <div className="flex-1 space-y-2">
                  <div className="loading-skeleton" style={{ height: '16px', width: '75%' }} />
                  <div className="loading-skeleton" style={{ height: '12px', width: '50%' }} />
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="space-y-4">
            {recentActivity.map((activity) => (
              <div 
                key={activity.id} 
                className="flex items-center p-4 rounded-xl transition-all cursor-pointer"
                style={{ gap: '16px' }}
                onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'var(--bg-secondary)'}
                onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
              >
                <div 
                  className="flex items-center justify-center rounded-full"
                  style={{ 
                    width: '40px', 
                    height: '40px',
                    backgroundColor: activity.status === 'completed' ? 'rgba(34, 197, 94, 0.1)' :
                                    activity.status === 'scheduled' ? 'rgba(59, 130, 246, 0.1)' :
                                    'rgba(245, 158, 11, 0.1)',
                    color: activity.status === 'completed' ? 'var(--brand-accent)' :
                           activity.status === 'scheduled' ? '#3B82F6' :
                           '#F59E0B'
                  }}
                >
                  {getActivityIcon(activity.type, activity.status)}
                </div>
                <div className="flex-1" style={{ minWidth: 0 }}>
                  <p className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>
                    {activity.title}
                  </p>
                  <p className="text-sm" style={{ color: 'var(--text-secondary)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {activity.description}
                  </p>
                </div>
                <div className="text-xs" style={{ color: 'var(--text-muted)' }}>
                  {activity.time}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}