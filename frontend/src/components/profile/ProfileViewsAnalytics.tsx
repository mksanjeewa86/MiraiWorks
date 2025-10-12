'use client';

import { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import { Card } from '@/components/ui';
import { Eye, Users, Building2, TrendingUp, Calendar } from 'lucide-react';
import { profileViewsApi } from '@/api/profileViews';
import type {
  ProfileViewStats,
  RecentViewer,
} from '@/api/profileViews';

interface ProfileViewsAnalyticsProps {
  userId?: number;
  days?: number;
}

export default function ProfileViewsAnalytics({
  userId,
  days = 30,
}: ProfileViewsAnalyticsProps) {
  const t = useTranslations('profile');
  const [stats, setStats] = useState<ProfileViewStats | null>(null);
  const [recentViewers, setRecentViewers] = useState<RecentViewer[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchAnalytics = async () => {
      setLoading(true);
      setError(null);

      try {
        // Fetch stats
        const statsResponse = await profileViewsApi.getStats(days);
        if (statsResponse.success && statsResponse.data) {
          setStats(statsResponse.data);
        }

        // Fetch recent viewers
        const viewersResponse = await profileViewsApi.getRecentViewers({
          limit: 10,
          days,
        });
        if (viewersResponse.success && viewersResponse.data) {
          setRecentViewers(viewersResponse.data);
        }
      } catch (err: any) {
        console.error('Error fetching profile analytics:', err);
        setError('Failed to load analytics data');
      } finally {
        setLoading(false);
      }
    };

    fetchAnalytics();
  }, [days]);

  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
      });
    } catch {
      return dateString;
    }
  };

  const getInitials = (firstName: string, lastName: string) => {
    return `${firstName?.[0] || ''}${lastName?.[0] || ''}`.toUpperCase();
  };

  if (loading) {
    return (
      <Card className="p-6">
        <div className="flex items-center justify-center py-12">
          <div className="loading-spinner" />
        </div>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="p-6">
        <div className="text-center py-12">
          <p className="text-red-600 dark:text-red-400">{error}</p>
        </div>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Stats Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Views */}
        <Card className="p-6 bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 border-blue-200 dark:border-blue-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-blue-700 dark:text-blue-300 mb-1">
                Total Views
              </p>
              <p className="text-3xl font-bold text-blue-900 dark:text-blue-100">
                {stats?.total_views || 0}
              </p>
            </div>
            <div className="p-3 bg-blue-200 dark:bg-blue-700 rounded-full">
              <Eye className="h-6 w-6 text-blue-700 dark:text-blue-200" />
            </div>
          </div>
        </Card>

        {/* Unique Viewers */}
        <Card className="p-6 bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/20 border-purple-200 dark:border-purple-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-purple-700 dark:text-purple-300 mb-1">
                Unique Viewers
              </p>
              <p className="text-3xl font-bold text-purple-900 dark:text-purple-100">
                {stats?.unique_viewers || 0}
              </p>
            </div>
            <div className="p-3 bg-purple-200 dark:bg-purple-700 rounded-full">
              <Users className="h-6 w-6 text-purple-700 dark:text-purple-200" />
            </div>
          </div>
        </Card>

        {/* Companies */}
        <Card className="p-6 bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 border-green-200 dark:border-green-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-green-700 dark:text-green-300 mb-1">
                Companies
              </p>
              <p className="text-3xl font-bold text-green-900 dark:text-green-100">
                {stats?.views_by_company?.length || 0}
              </p>
            </div>
            <div className="p-3 bg-green-200 dark:bg-green-700 rounded-full">
              <Building2 className="h-6 w-6 text-green-700 dark:text-green-200" />
            </div>
          </div>
        </Card>

        {/* Time Period */}
        <Card className="p-6 bg-gradient-to-br from-orange-50 to-orange-100 dark:from-orange-900/20 dark:to-orange-800/20 border-orange-200 dark:border-orange-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-orange-700 dark:text-orange-300 mb-1">
                Time Period
              </p>
              <p className="text-3xl font-bold text-orange-900 dark:text-orange-100">
                {days} Days
              </p>
            </div>
            <div className="p-3 bg-orange-200 dark:bg-orange-700 rounded-full">
              <Calendar className="h-6 w-6 text-orange-700 dark:text-orange-200" />
            </div>
          </div>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Companies */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2" style={{ color: 'var(--text-primary)' }}>
            <Building2 className="h-5 w-5" />
            Top Companies Viewing Your Profile
          </h3>

          {stats?.views_by_company && stats.views_by_company.length > 0 ? (
            <div className="space-y-3">
              {stats.views_by_company.map((company, index) => (
                <div
                  key={company.company_id}
                  className="flex items-center justify-between p-3 rounded-lg bg-gray-50 dark:bg-gray-800"
                >
                  <div className="flex items-center gap-3">
                    <div className="flex items-center justify-center w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 text-white text-sm font-bold">
                      {index + 1}
                    </div>
                    <div>
                      <p className="font-medium" style={{ color: 'var(--text-primary)' }}>
                        {company.company_name}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-semibold text-blue-600 dark:text-blue-400">
                      {company.view_count} {company.view_count === 1 ? 'view' : 'views'}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <Building2 className="h-12 w-12 mx-auto mb-3 text-gray-400" />
              <p className="text-sm text-gray-500 dark:text-gray-400">
                No company views yet
              </p>
            </div>
          )}
        </Card>

        {/* Recent Viewers */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2" style={{ color: 'var(--text-primary)' }}>
            <Users className="h-5 w-5" />
            Recent Profile Viewers
          </h3>

          {recentViewers && recentViewers.length > 0 ? (
            <div className="space-y-3">
              {recentViewers.map((viewer) => (
                <div
                  key={viewer.viewer_user_id}
                  className="flex items-center justify-between p-3 rounded-lg bg-gray-50 dark:bg-gray-800"
                >
                  <div className="flex items-center gap-3">
                    <div className="flex items-center justify-center w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 text-white text-sm font-bold">
                      {getInitials(viewer.first_name, viewer.last_name)}
                    </div>
                    <div>
                      <p className="font-medium" style={{ color: 'var(--text-primary)' }}>
                        {viewer.first_name} {viewer.last_name}
                      </p>
                      {viewer.company_name && (
                        <p className="text-xs text-gray-500 dark:text-gray-400">
                          {viewer.company_name}
                        </p>
                      )}
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-xs font-medium text-gray-600 dark:text-gray-400">
                      {formatDate(viewer.last_viewed)}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-500">
                      {viewer.view_count} {viewer.view_count === 1 ? 'view' : 'views'}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <Users className="h-12 w-12 mx-auto mb-3 text-gray-400" />
              <p className="text-sm text-gray-500 dark:text-gray-400">
                No recent viewers yet
              </p>
            </div>
          )}
        </Card>
      </div>

      {/* Views Over Time Chart */}
      {stats?.views_over_time && stats.views_over_time.length > 0 && (
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2" style={{ color: 'var(--text-primary)' }}>
            <TrendingUp className="h-5 w-5" />
            Views Over Time
          </h3>

          <div className="space-y-2">
            {stats.views_over_time.map((data) => (
              <div key={data.date} className="flex items-center gap-3">
                <p className="text-sm w-24 text-gray-600 dark:text-gray-400">
                  {formatDate(data.date)}
                </p>
                <div className="flex-1 bg-gray-100 dark:bg-gray-800 rounded-full h-6 overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-blue-500 to-indigo-600 rounded-full flex items-center justify-end px-2"
                    style={{
                      width: `${Math.max((data.count / (stats.total_views || 1)) * 100, 5)}%`,
                    }}
                  >
                    <span className="text-xs font-medium text-white">{data.count}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
}
