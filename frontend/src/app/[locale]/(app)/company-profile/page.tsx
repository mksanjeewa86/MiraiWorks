'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import AppLayout from '@/components/layout/AppLayout';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import {
  Building2,
  Mail,
  Phone,
  Globe,
  MapPin,
  Users,
  Edit,
  Save,
  X,
  BarChart3,
  TrendingUp,
  UserPlus,
  Briefcase,
} from 'lucide-react';
import type { Company } from '@/types';
import { companiesApi } from '@/api/companies';

export default function CompanyProfilePage() {
  const { user } = useAuth();
  const [company, setCompany] = useState<Company | null>(null);
  const [loading, setLoading] = useState(true);
  const [isEditing, setIsEditing] = useState(false);
  const [editedCompany, setEditedCompany] = useState<Company | null>(null);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Check if user is admin (can edit) or member (can only view)
  const isAdmin = user?.roles?.some((userRole) => userRole.role.name === 'admin' || userRole.role.name === 'system_admin');
  const isCompanyUser = user?.roles?.some((userRole) =>
    userRole.role.name === 'member' || userRole.role.name === 'admin' || userRole.role.name === 'system_admin'
  );

  useEffect(() => {
    const fetchCompanyProfile = async () => {
      if (!user?.company_id) {
        setLoading(false);
        return;
      }

      try {
        const response = await companiesApi.getMyCompany();
        if (response.success && response.data) {
          setCompany(response.data);
          setError(null);
        } else {
          setError(response.errors?.[0] || 'Failed to load company profile');
        }
      } catch (error) {
        console.error('Failed to fetch company profile:', error);
        setError('Failed to load company profile');
      } finally {
        setLoading(false);
      }
    };

    fetchCompanyProfile();
  }, [user]);

  const handleEdit = () => {
    setEditedCompany(company);
    setIsEditing(true);
  };

  const handleCancel = () => {
    setEditedCompany(null);
    setIsEditing(false);
    setError(null);
  };

  const handleSave = async () => {
    if (!editedCompany) return;

    setSaving(true);
    setError(null);
    try {
      const response = await companiesApi.updateMyCompany(editedCompany);
      if (response.success && response.data) {
        setCompany(response.data);
        setIsEditing(false);
      } else {
        setError(response.errors?.[0] || 'Failed to update company profile');
      }
    } catch (error) {
      console.error('Failed to save company profile:', error);
      setError('Failed to save company profile');
    } finally {
      setSaving(false);
    }
  };

  const handleInputChange = (field: keyof Company, value: string) => {
    if (!editedCompany) return;
    setEditedCompany({ ...editedCompany, [field]: value });
  };

  if (!isCompanyUser) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center min-h-[60vh]">
          <Card className="p-8 text-center max-w-md">
            <Building2 className="h-16 w-16 mx-auto text-gray-400 mb-4" />
            <h2 className="text-xl font-semibold mb-2">Access Denied</h2>
            <p className="text-gray-600 dark:text-gray-400">
              Company profile is only available for company users.
            </p>
          </Card>
        </div>
      </AppLayout>
    );
  }

  if (loading) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center min-h-[60vh]">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600 dark:text-gray-400">Loading company profile...</p>
          </div>
        </div>
      </AppLayout>
    );
  }

  if (!company) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center min-h-[60vh]">
          <Card className="p-8 text-center max-w-md">
            <Building2 className="h-16 w-16 mx-auto text-gray-400 mb-4" />
            <h2 className="text-xl font-semibold mb-2">No Company Found</h2>
            <p className="text-gray-600 dark:text-gray-400">
              You are not associated with any company.
            </p>
          </Card>
        </div>
      </AppLayout>
    );
  }

  const displayCompany = isEditing ? editedCompany! : company;

  return (
    <AppLayout pageTitle="Company Profile" pageDescription="Manage your company information">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header Card */}
        <Card className="p-6">
          <div className="flex items-start justify-between">
            <div className="flex items-start gap-4">
              <div className="w-16 h-16 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-xl flex items-center justify-center">
                <Building2 className="h-8 w-8 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">{displayCompany.name}</h1>
                <p className="text-gray-600 dark:text-gray-400 capitalize">{displayCompany.type}</p>
              </div>
            </div>
            {isAdmin && !isEditing && (
              <Button onClick={handleEdit} variant="outline">
                <Edit className="h-4 w-4 mr-2" />
                Edit Profile
              </Button>
            )}
            {isAdmin && isEditing && (
              <div className="flex gap-2">
                <Button onClick={handleSave} disabled={saving}>
                  <Save className="h-4 w-4 mr-2" />
                  {saving ? 'Saving...' : 'Save'}
                </Button>
                <Button onClick={handleCancel} variant="outline" disabled={saving}>
                  <X className="h-4 w-4 mr-2" />
                  Cancel
                </Button>
              </div>
            )}
          </div>
        </Card>

        {/* Error Message */}
        {error && (
          <Card className="p-4 bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800">
            <div className="flex items-center gap-3">
              <X className="h-5 w-5 text-red-600 dark:text-red-400" />
              <p className="text-red-600 dark:text-red-400 font-medium">{error}</p>
              <button
                onClick={() => setError(null)}
                className="ml-auto text-red-600 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
          </Card>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Info */}
          <div className="lg:col-span-2 space-y-6">
            {/* Company Information */}
            <Card className="p-6">
              <h2 className="text-xl font-semibold mb-6 flex items-center gap-2">
                <Building2 className="h-5 w-5" />
                Company Information
              </h2>

              <div className="space-y-6">
                {/* Description */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Description
                  </label>
                  {isEditing ? (
                    <textarea
                      value={displayCompany.description || ''}
                      onChange={(e) => handleInputChange('description', e.target.value)}
                      className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      rows={4}
                      placeholder="Enter company description..."
                    />
                  ) : (
                    <p className="text-gray-900 dark:text-white">
                      {displayCompany.description || 'No description provided'}
                    </p>
                  )}
                </div>

                {/* Contact Information */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Email */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      <Mail className="h-4 w-4 inline mr-2" />
                      Email
                    </label>
                    {isEditing ? (
                      <input
                        type="email"
                        value={displayCompany.email || ''}
                        onChange={(e) => handleInputChange('email', e.target.value)}
                        className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="contact@company.com"
                      />
                    ) : (
                      <p className="text-gray-900 dark:text-white">{displayCompany.email}</p>
                    )}
                  </div>

                  {/* Phone */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      <Phone className="h-4 w-4 inline mr-2" />
                      Phone
                    </label>
                    {isEditing ? (
                      <input
                        type="tel"
                        value={displayCompany.phone || ''}
                        onChange={(e) => handleInputChange('phone', e.target.value)}
                        className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="+1-234-567-8900"
                      />
                    ) : (
                      <p className="text-gray-900 dark:text-white">{displayCompany.phone || 'Not provided'}</p>
                    )}
                  </div>

                  {/* Website */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      <Globe className="h-4 w-4 inline mr-2" />
                      Website
                    </label>
                    {isEditing ? (
                      <input
                        type="url"
                        value={displayCompany.website || ''}
                        onChange={(e) => handleInputChange('website', e.target.value)}
                        className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="https://company.com"
                      />
                    ) : (
                      <p className="text-gray-900 dark:text-white">
                        {displayCompany.website ? (
                          <a
                            href={displayCompany.website}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-blue-600 hover:underline"
                          >
                            {displayCompany.website}
                          </a>
                        ) : (
                          'Not provided'
                        )}
                      </p>
                    )}
                  </div>

                  {/* City */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      <MapPin className="h-4 w-4 inline mr-2" />
                      City
                    </label>
                    {isEditing ? (
                      <input
                        type="text"
                        value={displayCompany.city || ''}
                        onChange={(e) => handleInputChange('city', e.target.value)}
                        className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="Tokyo"
                      />
                    ) : (
                      <p className="text-gray-900 dark:text-white">{displayCompany.city || 'Not provided'}</p>
                    )}
                  </div>
                </div>
              </div>
            </Card>
          </div>

          {/* Sidebar - Analytics */}
          <div className="space-y-6">
            {/* Analytics Overview */}
            <Card className="p-6">
              <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <BarChart3 className="h-5 w-5" />
                Analytics
              </h2>

              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                  <div className="flex items-center gap-3">
                    <Users className="h-5 w-5 text-blue-600" />
                    <div>
                      <p className="text-sm text-gray-600 dark:text-gray-400">Team Members</p>
                      <p className="text-2xl font-bold text-gray-900 dark:text-white">24</p>
                    </div>
                  </div>
                  <TrendingUp className="h-5 w-5 text-green-500" />
                </div>

                <div className="flex items-center justify-between p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                  <div className="flex items-center gap-3">
                    <Briefcase className="h-5 w-5 text-green-600" />
                    <div>
                      <p className="text-sm text-gray-600 dark:text-gray-400">Active Positions</p>
                      <p className="text-2xl font-bold text-gray-900 dark:text-white">12</p>
                    </div>
                  </div>
                  <TrendingUp className="h-5 w-5 text-green-500" />
                </div>

                <div className="flex items-center justify-between p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                  <div className="flex items-center gap-3">
                    <UserPlus className="h-5 w-5 text-purple-600" />
                    <div>
                      <p className="text-sm text-gray-600 dark:text-gray-400">New Hires (Month)</p>
                      <p className="text-2xl font-bold text-gray-900 dark:text-white">5</p>
                    </div>
                  </div>
                  <TrendingUp className="h-5 w-5 text-green-500" />
                </div>
              </div>

              <p className="mt-4 text-xs text-gray-500 dark:text-gray-400 text-center">
                Analytics visible to all company members
              </p>
            </Card>

            {/* Quick Info */}
            <Card className="p-6">
              <h2 className="text-lg font-semibold mb-4">Quick Info</h2>
              <div className="space-y-3 text-sm">
                <div>
                  <p className="text-gray-600 dark:text-gray-400">Member since</p>
                  <p className="font-medium text-gray-900 dark:text-white">
                    {new Date(displayCompany.created_at).toLocaleDateString()}
                  </p>
                </div>
                <div>
                  <p className="text-gray-600 dark:text-gray-400">Last updated</p>
                  <p className="font-medium text-gray-900 dark:text-white">
                    {new Date(displayCompany.updated_at).toLocaleDateString()}
                  </p>
                </div>
                <div>
                  <p className="text-gray-600 dark:text-gray-400">Company Type</p>
                  <p className="font-medium text-gray-900 dark:text-white capitalize">{displayCompany.type}</p>
                </div>
              </div>
            </Card>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
