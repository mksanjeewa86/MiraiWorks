'use client';

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
import StatCard from '@/components/common/StatCard';
import { SimpleLineChart, SimpleBarChart } from './Charts';
import { CandidateStats, ApplicationActivity, RecentActivity } from '@/types/dashboard';
import { dashboardApi } from '@/api/dashboard';

export default function CandidateOverview() {
  const [stats, setStats] = useState<CandidateStats | null>(null);
  const [activityData, setActivityData] = useState<ApplicationActivity[]>([]);
  const [recentActivity, setRecentActivity] = useState<RecentActivity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError('');

        // Fetch dashboard stats from API
        const [statsResponse, activityResponse] = await Promise.all([
          dashboardApi.getStats(),
          dashboardApi.getRecentActivity(10)
        ]);

        // Map API response to CandidateStats interface
        const dashboardStats = statsResponse.data;
        setStats({
          activeApplications: dashboardStats?.totalUsers || 0,
          upcomingInterviews: dashboardStats?.totalInterviews || 0,
          unreadMessages: dashboardStats?.activeConversations || 0,
          resumeCompleteness: 85, // This might come from user profile
          totalApplications: dashboardStats?.totalUsers || 0,
          interviewsCompleted: dashboardStats?.totalInterviews || 0,
          offersReceived: 0 // This needs to be added to backend
        });

        // Generate activity chart data from recent activity
        const currentDate = new Date();
        const months = [];
        for (let i = 5; i >= 0; i--) {
          const date = new Date(currentDate.getFullYear(), currentDate.getMonth() - i, 1);
          const monthName = date.toLocaleDateString('en', { month: 'short' });
          months.push({
            name: monthName,
            applications: Math.floor(Math.random() * 20) + 5, // TODO: Get real data from API
            interviews: Math.floor(Math.random() * 10) + 1
          });
        }
        setActivityData(months);

        // Map API activity to RecentActivity format
        const activities = activityResponse.data?.map((item, index) => {
          // Map API activity types to UI activity types
          let mappedType: 'application' | 'interview' | 'message' | 'offer';
          switch (item.type) {
            case 'interview':
              mappedType = 'interview';
              break;
            case 'message':
              mappedType = 'message';
              break;
            case 'user':
            case 'resume':
              mappedType = 'application';
              break;
            case 'company':
              mappedType = 'offer';
              break;
            default:
              mappedType = 'application';
          }

          return {
            id: parseInt(item.id) || index + 1,
            type: mappedType,
            title: item.title,
            description: item.description,
            time: new Date(item.timestamp).toLocaleDateString(),
            status: 'pending' as const
          };
        }) || [];

        setRecentActivity(activities);
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to fetch dashboard data';
        setError(errorMessage);
        console.error('Error fetching candidate dashboard data:', err);

        // Set empty data on error
        setStats({
          activeApplications: 0,
          upcomingInterviews: 0,
          unreadMessages: 0,
          resumeCompleteness: 0,
          totalApplications: 0,
          interviewsCompleted: 0,
          offersReceived: 0
        });
        setActivityData([]);
        setRecentActivity([]);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const getActivityIcon = (type: string) => {
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


  return (
    <div className="space-y-6">
      {/* Welcome Header */}
      <div className="card-gradient rounded-2xl p-6">
        <h1 className="text-2xl font-bold mb-2" style={{ color: 'var(--text-primary)' }}>
          Welcome back! 👋
        </h1>
        <p style={{ color: 'var(--text-secondary)' }}>
          Here&apos;s what&apos;s happening with your job search today.
        </p>
        {error && (
          <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-600">
              ⚠️ {error}
            </p>
          </div>
        )}
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
              data={activityData.map(item => ({ ...item, value: item.applications }))}
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
                  {getActivityIcon(activity.type)}
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