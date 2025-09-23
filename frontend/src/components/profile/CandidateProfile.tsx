import React, { useState, useEffect } from 'react';
import { UserCircleIcon, EnvelopeIcon, PhoneIcon, MapPinIcon, CalendarIcon } from '@heroicons/react/24/outline';
import Card from '@/components/ui/card';
import Badge from '@/components/ui/badge';
import Button from '@/components/ui/button';
import LoadingSpinner from '@/components/ui/loading-spinner';
import MBTIResultCard from '@/components/mbti/MBTIResultCard';
import { mbtiApi } from '@/api/mbti';
import { useAuth } from '@/contexts/AuthContext';
import type { MBTITestSummary } from '@/types/mbti';

interface CandidateProfileProps {
  userId?: number;
  isPublic?: boolean;
}

const CandidateProfile: React.FC<CandidateProfileProps> = ({ userId, isPublic = false }) => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [mbtiSummary, setMbtiSummary] = useState<MBTITestSummary | null>(null);
  const [language, setLanguage] = useState<'en' | 'ja'>('ja');

  useEffect(() => {
    loadProfileData();
  }, [userId]);

  const loadProfileData = async () => {
    try {
      setLoading(true);
      
      // Load MBTI results if it's the user's own profile or public
      if (!userId || userId === user?.id) {
        try {
          const summary = await mbtiApi.getSummary(language);
          setMbtiSummary(summary);
        } catch (err) {
          console.log('No MBTI results available');
        }
      }
    } catch (error) {
      console.error('Failed to load profile data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <LoadingSpinner className="w-8 h-8" />
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Profile Info */}
        <div className="lg:col-span-2 space-y-6">
          {/* Basic Info Card */}
          <Card className="p-6">
            <div className="flex items-start space-x-4">
              <div className="flex-shrink-0">
                <UserCircleIcon className="h-24 w-24 text-gray-400" />
              </div>
              <div className="flex-1">
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                  {user?.full_name || 'Candidate Name'}
                </h1>
                <p className="text-lg text-gray-600 dark:text-gray-400 mt-1">
                  Software Developer
                </p>
                <div className="flex flex-wrap gap-2 mt-4">
                  <Badge variant="primary">Active</Badge>
                  <Badge variant="secondary">Available</Badge>
                  {mbtiSummary && (
                    <Badge variant="outline">{mbtiSummary.mbti_type}</Badge>
                  )}
                </div>
              </div>
            </div>

            {/* Contact Information */}
            <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="flex items-center space-x-2 text-gray-600 dark:text-gray-400">
                <EnvelopeIcon className="h-5 w-5" />
                <span>{user?.email || 'email@example.com'}</span>
              </div>
              <div className="flex items-center space-x-2 text-gray-600 dark:text-gray-400">
                <PhoneIcon className="h-5 w-5" />
                <span>+81 90-1234-5678</span>
              </div>
              <div className="flex items-center space-x-2 text-gray-600 dark:text-gray-400">
                <MapPinIcon className="h-5 w-5" />
                <span>Tokyo, Japan</span>
              </div>
              <div className="flex items-center space-x-2 text-gray-600 dark:text-gray-400">
                <CalendarIcon className="h-5 w-5" />
                <span>Member since 2024</span>
              </div>
            </div>
          </Card>

          {/* Skills Section */}
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4">Skills</h2>
            <div className="flex flex-wrap gap-2">
              {['JavaScript', 'React', 'Node.js', 'Python', 'SQL', 'AWS'].map((skill) => (
                <span
                  key={skill}
                  className="px-3 py-1 bg-blue-100 dark:bg-blue-900/50 text-blue-700 dark:text-blue-300 rounded-full text-sm"
                >
                  {skill}
                </span>
              ))}
            </div>
          </Card>

          {/* Experience Section */}
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4">Experience</h2>
            <div className="space-y-4">
              <div className="border-l-4 border-blue-500 pl-4">
                <h3 className="font-semibold">Senior Software Developer</h3>
                <p className="text-gray-600 dark:text-gray-400">Tech Company Inc.</p>
                <p className="text-sm text-gray-500">2021 - Present</p>
                <p className="mt-2 text-gray-700 dark:text-gray-300">
                  Leading development of cloud-based applications using modern tech stack.
                </p>
              </div>
              <div className="border-l-4 border-gray-300 pl-4">
                <h3 className="font-semibold">Software Developer</h3>
                <p className="text-gray-600 dark:text-gray-400">Startup Ltd.</p>
                <p className="text-sm text-gray-500">2019 - 2021</p>
                <p className="mt-2 text-gray-700 dark:text-gray-300">
                  Developed and maintained multiple web applications.
                </p>
              </div>
            </div>
          </Card>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* MBTI Results */}
          {mbtiSummary && (
            <div>
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold">MBTI性格タイプ</h2>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => setLanguage('ja')}
                    className={`px-2 py-1 text-xs rounded ${
                      language === 'ja'
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-200 text-gray-700 dark:bg-gray-700 dark:text-gray-300'
                    }`}
                  >
                    JP
                  </button>
                  <button
                    onClick={() => setLanguage('en')}
                    className={`px-2 py-1 text-xs rounded ${
                      language === 'en'
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-200 text-gray-700 dark:bg-gray-700 dark:text-gray-300'
                    }`}
                  >
                    EN
                  </button>
                </div>
              </div>
              <MBTIResultCard
                summary={mbtiSummary}
                language={language}
                showDetails={true}
              />
            </div>
          )}

          {/* Quick Stats */}
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4">Quick Stats</h2>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-600 dark:text-gray-400">Applications</span>
                <span className="font-semibold">15</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600 dark:text-gray-400">Interviews</span>
                <span className="font-semibold">8</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600 dark:text-gray-400">Profile Views</span>
                <span className="font-semibold">234</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600 dark:text-gray-400">Response Rate</span>
                <span className="font-semibold">85%</span>
              </div>
            </div>
          </Card>

          {/* Actions */}
          {!isPublic && (
            <Card className="p-6">
              <h2 className="text-xl font-semibold mb-4">Actions</h2>
              <div className="space-y-3">
                <Button className="w-full">Edit Profile</Button>
                <Button variant="outline" className="w-full">Update Resume</Button>
                <Button variant="outline" className="w-full">Privacy Settings</Button>
              </div>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
};

export default CandidateProfile;