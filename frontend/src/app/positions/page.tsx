'use client';
import { useState, useEffect } from 'react';
import type { ChangeEvent, FormEvent, CSSProperties } from 'react';
import AppLayout from '@/components/layout/AppLayout';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import { useAuth } from '@/contexts/AuthContext';
import { PREFECTURES } from '@/utils/prefectures';
import { positionsApi } from '@/api/positions';
import type { Position as ApiPosition, PositionCreate } from '@/types';
import {
  BriefcaseBusiness,
  Search,
  Filter,
  Plus,
  Eye,
  Edit,
  Trash2,
  Download,
  MapPin,
  DollarSign,
  Clock,
  Users,
  Building,
  Calendar,
  TrendingUp,
  Briefcase,
  Globe,
  X
} from 'lucide-react';

// Types
interface Position extends Omit<ApiPosition, 'requirements'> {
  company: string;
  applications: number;
  views: number;
  postedDate: string;
  deadline: string;
  requirements: string[];
  remote: boolean;
  urgent: boolean;
  type: 'full-time' | 'part-time' | 'contract' | 'internship' | 'freelance' | 'temporary';
  level: 'entry' | 'mid' | 'senior' | 'executive';
  salaryMin: number;
  salaryMax: number;
}

interface NewPositionFormData {
  title: string;
  department: string;
  location: string;
  job_type: Position['job_type'];
  experience_level: Position['experience_level'];
  salaryMin: string;
  salaryMax: string;
  status: Position['status'];
  postedDate: string;
  deadline: string;
  description: string;
  requirements: string;
  benefits: string;
  remote_type: Position['remote_type'];
  is_urgent: boolean;
}

const formatDateInput = (date: Date) => date.toISOString().split('T')[0];

const getDefaultFormData = (): NewPositionFormData => {
  const today = new Date();
  const defaultDeadline = new Date(today);
  defaultDeadline.setDate(defaultDeadline.getDate() + 30);

  return {
    title: '',
    department: '',
    location: '',
    job_type: 'full_time',
    experience_level: 'entry_level',
    salaryMin: '',
    salaryMax: '',
    status: 'draft',
    postedDate: formatDateInput(today),
    deadline: formatDateInput(defaultDeadline),
    description: '',
    requirements: '',
    benefits: '',
    remote_type: 'on_site',
    is_urgent: false,
  };
};

const PREFECTURE_LOCATION_OPTIONS = PREFECTURES.map(prefecture => ({
  label: prefecture.nameEn,
  value: `${prefecture.nameEn}, Japan`,
}));

const LOCATION_OPTIONS = [
  ...PREFECTURE_LOCATION_OPTIONS,
  { label: 'Remote', value: 'Remote' },
];

const FILTER_LOCATION_OPTIONS = [
  { label: 'All Locations', value: 'all' },
  ...LOCATION_OPTIONS,
];
// Helper function to map API data to frontend format
const mapApiPositionToLocal = (apiPosition: ApiPosition): Position => {
  return {
    ...apiPosition,
    company: apiPosition.company_name || 'Unknown Company',
    applications: apiPosition.application_count || 0,
    views: apiPosition.view_count || 0,
    postedDate: apiPosition.published_at || apiPosition.created_at || new Date().toISOString(),
    deadline: apiPosition.application_deadline || '',
    requirements: apiPosition.required_skills || [],
    salaryMin: apiPosition.salary_min || 0,
    salaryMax: apiPosition.salary_max || 0,
    remote: apiPosition.remote_type === 'remote' || apiPosition.remote_type === 'hybrid',
    urgent: apiPosition.is_urgent || false,
    type: (apiPosition.job_type?.replace('_', '-') || 'full-time') as Position['type'],
    level: (apiPosition.experience_level?.replace('_level', '').replace('_', '') || 'mid') as Position['level'],
  };
};

function PositionsPageContent() {
  const { user, isLoading: authLoading } = useAuth();
  const [positions, setPositions] = useState<Position[]>([]);
  const [filteredPositions, setFilteredPositions] = useState<Position[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [typeFilter, setTypeFilter] = useState<string>('all');
  const [levelFilter, setLevelFilter] = useState<string>('all');
  const [locationFilter, setLocationFilter] = useState<string>('all');
  const [sortBy, setSortBy] = useState<'title' | 'postedDate' | 'applications' | 'deadline'>('postedDate');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;
  const [isNewPositionOpen, setIsNewPositionOpen] = useState(false);

  // Load positions from API
  useEffect(() => {
    const loadPositions = async () => {
      // Wait for user to be available and auth to finish loading
      if (authLoading || !user) {
        return;
      }

      try {
        setLoading(true);
        setError(null);
        // Pass user's company_id as a filter to only show positions from their company
        const response = await positionsApi.getAll({
          company_id: user.company_id
        });
        if (response.success && response.data) {
          const mappedPositions = response.data.positions.map(mapApiPositionToLocal);
          setPositions(mappedPositions);
        } else {
          setError('Failed to load positions');
        }
      } catch (err) {
        console.error('Error loading positions:', err);
        setError(err instanceof Error ? err.message : 'Failed to load positions');
      } finally {
        setLoading(false);
      }
    };

    loadPositions();
  }, [user, authLoading]);

  // Apply filters and search
  useEffect(() => {
    const filtered = positions.filter(position => {
      const matchesSearch = position.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          position.company.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          (position.department || '').toLowerCase().includes(searchTerm.toLowerCase());
      const matchesStatus = statusFilter === 'all' || position.status === statusFilter;
      const matchesType = typeFilter === 'all' || position.type === typeFilter;
      const matchesLevel = levelFilter === 'all' || position.level === levelFilter;
      const matchesLocation =
        locationFilter === 'all' ||
        (locationFilter.toLowerCase() === 'remote'
          ? position.remote
          : position.location === locationFilter);
      return matchesSearch && matchesStatus && matchesType && matchesLevel && matchesLocation;
    });
    // Sort
    filtered.sort((a, b) => {
      let aValue, bValue;
      switch (sortBy) {
        case 'title':
          aValue = a.title.toLowerCase();
          bValue = b.title.toLowerCase();
          break;
        case 'postedDate':
          aValue = new Date(a.postedDate).getTime();
          bValue = new Date(b.postedDate).getTime();
          break;
        case 'applications':
          aValue = a.applications;
          bValue = b.applications;
          break;
        case 'deadline':
          aValue = new Date(a.deadline).getTime();
          bValue = new Date(b.deadline).getTime();
          break;
        default:
          return 0;
      }
      if (sortOrder === 'asc') {
        return aValue < bValue ? -1 : aValue > bValue ? 1 : 0;
      } else {
        return aValue > bValue ? -1 : aValue < bValue ? 1 : 0;
      }
    });
    setFilteredPositions(filtered);
    setCurrentPage(1);
  }, [positions, searchTerm, statusFilter, typeFilter, levelFilter, locationFilter, sortBy, sortOrder]);
  // Pagination
  const totalPages = Math.ceil(filteredPositions.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const currentPositions = filteredPositions.slice(startIndex, endIndex);
  // Statistics
  const stats = {
    total: positions.length,
    published: positions.filter(p => p.status === 'published').length,
    applications: positions.reduce((sum, p) => sum + p.applications, 0),
    avgViews: Math.round(positions.reduce((sum, p) => sum + p.views, 0) / positions.length) || 0
  };
  const handleCreatePosition = async (formData: NewPositionFormData) => {
    try {
      const parseMultiline = (value: string) => (
        value
          .split('\n')
          .map(item => item.trim())
          .filter(Boolean)
      );

      const positionData: PositionCreate = {
        title: formData.title.trim(),
        description: formData.description.trim(),
        department: formData.department.trim(),
        location: formData.location,
        job_type: formData.job_type,
        experience_level: formData.experience_level,
        remote_type: formData.remote_type,
        salary_min: formData.salaryMin ? Number(formData.salaryMin) * 100 : undefined, // Convert to cents
        salary_max: formData.salaryMax ? Number(formData.salaryMax) * 100 : undefined, // Convert to cents
        required_skills: parseMultiline(formData.requirements),
        benefits: parseMultiline(formData.benefits),
        application_deadline: formData.deadline || undefined,
        is_urgent: formData.is_urgent,
        company_id: user?.company_id || 1, // Use current user's company
      };

      const response = await positionsApi.create(positionData);
      if (response.success && response.data) {
        const newPosition = mapApiPositionToLocal(response.data);
        setPositions(prev => [newPosition, ...prev]);
        setIsNewPositionOpen(false);
        setCurrentPage(1);
      } else {
        setError('Failed to create position');
      }
    } catch (err) {
      console.error('Error creating position:', err);
      setError(err instanceof Error ? err.message : 'Failed to create position');
    }
  };
  // Helper functions
  const getStatusBadge = (status: Position['status']) => {
    const styles = {
      draft: 'bg-gray-100 text-gray-800 border-gray-200',
      published: 'bg-green-100 text-green-800 border-green-200',
      paused: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      closed: 'bg-red-100 text-red-800 border-red-200',
      archived: 'bg-gray-100 text-gray-800 border-gray-200'
    };
    return styles[status] || styles.draft;
  };
  const getTypeBadge = (type: Position['type']) => {
    const styles = {
      'full-time': 'bg-blue-50 text-blue-700 border-blue-200',
      'part-time': 'bg-purple-50 text-purple-700 border-purple-200',
      'contract': 'bg-orange-50 text-orange-700 border-orange-200',
      'internship': 'bg-pink-50 text-pink-700 border-pink-200',
      'freelance': 'bg-green-50 text-green-700 border-green-200',
      'temporary': 'bg-yellow-50 text-yellow-700 border-yellow-200'
    };
    return styles[type] || styles['full-time'];
  };
  const getLevelBadge = (level: Position['level']) => {
    const styles = {
      'entry': 'bg-green-50 text-green-700 border-green-200',
      'mid': 'bg-blue-50 text-blue-700 border-blue-200',
      'senior': 'bg-purple-50 text-purple-700 border-purple-200',
      'executive': 'bg-red-50 text-red-700 border-red-200'
    };
    return styles[level] || styles['mid'];
  };
  const formatSalary = (min: number, max: number) => {
    if (!min || !max) return 'Salary not specified';
    return `¥${(min / 1000000).toFixed(1)}M - ¥${(max / 1000000).toFixed(1)}M`;
  };
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };
  const handleSort = (field: typeof sortBy) => {
    if (sortBy === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(field);
      setSortOrder('desc');
    }
  };
  const clearFilters = () => {
    setSearchTerm('');
    setStatusFilter('all');
    setTypeFilter('all');
    setLevelFilter('all');
    setLocationFilter('all');
  };
  // Show loading spinner while auth is loading
  if (authLoading) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center min-h-64">
          <div className="loading-spinner border-gray-300 border-t-brand-primary h-8 w-8" aria-label="Loading"></div>
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout>
      <NewPositionModal
        isOpen={isNewPositionOpen}
        onClose={() => setIsNewPositionOpen(false)}
        onSubmit={handleCreatePosition}
      />
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
              <BriefcaseBusiness className="h-6 w-6" style={{ color: 'var(--brand-primary)' }} />
              Positions Management
            </h1>
            <p className="text-gray-600 mt-1">Manage job postings, track applications, and oversee hiring workflows</p>
          </div>
          <div className="flex items-center gap-3">
            <button className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
              <Download className="h-4 w-4" />
              Export
            </button>
            <button
              type="button"
              onClick={() => setIsNewPositionOpen(true)}
              className="flex items-center gap-2 px-4 py-2 text-white rounded-lg hover:opacity-90 transition-opacity"
              style={{ backgroundColor: 'var(--brand-primary)' }}
            >
              <Plus className="h-4 w-4" />
              New Position
            </button>
          </div>
        </div>
        {/* Statistics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-white p-6 rounded-lg border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Positions</p>
                <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
              </div>
              <div className="p-3 rounded-full" style={{ backgroundColor: 'var(--brand-primary-light)' }}>
                <Briefcase className="h-6 w-6" style={{ color: 'var(--brand-primary)' }} />
              </div>
            </div>
          </div>
          <div className="bg-white p-6 rounded-lg border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Published</p>
                <p className="text-2xl font-bold text-green-600">{stats.published}</p>
              </div>
              <div className="p-3 bg-green-100 rounded-full">
                <Globe className="h-6 w-6 text-green-600" />
              </div>
            </div>
          </div>
          <div className="bg-white p-6 rounded-lg border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Applications</p>
                <p className="text-2xl font-bold text-blue-600">{stats.applications}</p>
              </div>
              <div className="p-3 bg-blue-100 rounded-full">
                <Users className="h-6 w-6 text-blue-600" />
              </div>
            </div>
          </div>
          <div className="bg-white p-6 rounded-lg border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Avg. Views</p>
                <p className="text-2xl font-bold text-purple-600">{stats.avgViews}</p>
              </div>
              <div className="p-3 bg-purple-100 rounded-full">
                <TrendingUp className="h-6 w-6 text-purple-600" />
              </div>
            </div>
          </div>
        </div>
        {/* Filters and Search */}
        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <div className="flex flex-col lg:flex-row gap-4">
            {/* Search */}
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search positions, companies, or departments..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:border-transparent"
                  style={{ '--tw-ring-color': 'var(--brand-primary)' } as CSSProperties}
                />
              </div>
            </div>
            {/* Filters */}
            <div className="flex flex-wrap gap-3">
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:border-transparent"
                style={{ '--tw-ring-color': 'var(--brand-primary)' } as CSSProperties}
              >
                <option value="all">All Status</option>
                <option value="draft">Draft</option>
                <option value="published">Published</option>
                <option value="paused">Paused</option>
                <option value="closed">Closed</option>
                <option value="archived">Archived</option>
              </select>
              <select
                value={typeFilter}
                onChange={(e) => setTypeFilter(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:border-transparent"
                style={{ '--tw-ring-color': 'var(--brand-primary)' } as CSSProperties}
              >
                <option value="all">All Types</option>
                <option value="full-time">Full-time</option>
                <option value="part-time">Part-time</option>
                <option value="contract">Contract</option>
                <option value="internship">Internship</option>
              </select>
              <select
                value={levelFilter}
                onChange={(e) => setLevelFilter(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:border-transparent"
                style={{ '--tw-ring-color': 'var(--brand-primary)' } as CSSProperties}
              >
                <option value="all">All Levels</option>
                <option value="entry">Entry</option>
                <option value="mid">Mid</option>
                <option value="senior">Senior</option>
                <option value="executive">Executive</option>
              </select>
              <select
                value={locationFilter}
                onChange={(e) => setLocationFilter(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:border-transparent"
                style={{ '--tw-ring-color': 'var(--brand-primary)' } as CSSProperties}
              >
                {FILTER_LOCATION_OPTIONS.map(({ label, value }) => (
                  <option key={value} value={value}>
                    {label}
                  </option>
                ))}
              </select>
              <button
                onClick={clearFilters}
                className="px-3 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              >
                <Filter className="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>
        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-center gap-2">
              <div className="text-red-600">
                <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <p className="text-red-800 font-medium">{error}</p>
            </div>
          </div>
        )}

        {/* Positions Table */}
        <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                      onClick={() => handleSort('title')}>
                    <div className="flex items-center gap-1">
                      Position
                      {sortBy === 'title' && (
                        <span className="text-xs">{sortOrder === 'asc' ? '↑' : '↓'}</span>
                      )}
                    </div>
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Company & Dept
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Details
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Salary
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                      onClick={() => handleSort('applications')}>
                    <div className="flex items-center gap-1">
                      Applications
                      {sortBy === 'applications' && (
                        <span className="text-xs">{sortOrder === 'asc' ? '↑' : '↓'}</span>
                      )}
                    </div>
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                      onClick={() => handleSort('deadline')}>
                    <div className="flex items-center gap-1">
                      Timeline
                      {sortBy === 'deadline' && (
                        <span className="text-xs">{sortOrder === 'asc' ? '↑' : '↓'}</span>
                      )}
                    </div>
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {loading ? (
                  <tr>
                    <td colSpan={7} className="px-6 py-12 text-center">
                      <div className="flex flex-col items-center gap-3">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                        <p className="text-gray-500">Loading positions...</p>
                      </div>
                    </td>
                  </tr>
                ) : currentPositions.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="px-6 py-12 text-center">
                      <div className="flex flex-col items-center gap-3">
                        <BriefcaseBusiness className="h-12 w-12 text-gray-400" />
                        <div>
                          <p className="text-gray-900 font-medium">No positions found</p>
                          <p className="text-gray-500 text-sm">Try adjusting your search or filters</p>
                        </div>
                      </div>
                    </td>
                  </tr>
                ) : (
                  currentPositions.map((position) => (
                    <tr key={position.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4">
                        <div className="flex flex-col gap-1">
                          <div className="flex items-center gap-2">
                            <h3 className="text-sm font-medium text-gray-900">{position.title}</h3>
                            {position.urgent && (
                              <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                                Urgent
                              </span>
                            )}
                          </div>
                          <div className="flex items-center gap-2">
                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${getStatusBadge(position.status)}`}>
                              {position.status}
                            </span>
                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${getTypeBadge(position.type)}`}>
                              {position.type}
                            </span>
                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${getLevelBadge(position.level)}`}>
                              {position.level}
                            </span>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex flex-col gap-1">
                          <div className="flex items-center gap-1">
                            <Building className="h-3 w-3 text-gray-400" />
                            <span className="text-sm font-medium text-gray-900">{position.company}</span>
                          </div>
                          <span className="text-sm text-gray-600">{position.department}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex flex-col gap-1">
                          <div className="flex items-center gap-1">
                            <MapPin className="h-3 w-3 text-gray-400" />
                            <span className="text-sm text-gray-600">{position.location}</span>
                            {position.remote && (
                              <span className="inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">
                                Remote
                              </span>
                            )}
                          </div>
                          <div className="flex items-center gap-1">
                            <Eye className="h-3 w-3 text-gray-400" />
                            <span className="text-sm text-gray-600">{position.views} views</span>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-1">
                          <DollarSign className="h-3 w-3 text-gray-400" />
                          <span className="text-sm text-gray-900">{formatSalary(position.salaryMin, position.salaryMax)}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-1">
                          <Users className="h-3 w-3 text-gray-400" />
                          <span className="text-sm font-medium text-gray-900">{position.applications}</span>
                          <span className="text-sm text-gray-600">applicants</span>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex flex-col gap-1">
                          <div className="flex items-center gap-1">
                            <Calendar className="h-3 w-3 text-gray-400" />
                            <span className="text-sm text-gray-600">Posted {formatDate(position.postedDate)}</span>
                          </div>
                          <div className="flex items-center gap-1">
                            <Clock className="h-3 w-3 text-gray-400" />
                            <span className="text-sm text-gray-600">Ends {formatDate(position.deadline)}</span>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2">
                          <button
                            className="p-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                            title="View Details"
                          >
                            <Eye className="h-4 w-4" />
                          </button>
                          <button
                            className="p-2 text-gray-600 hover:text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                            title="Edit Position"
                          >
                            <Edit className="h-4 w-4" />
                          </button>
                          <button
                            className="p-2 text-gray-600 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                            title="Delete Position"
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
          {/* Pagination */}
          {totalPages > 1 && (
            <div className="px-6 py-3 border-t border-gray-200">
              <div className="flex items-center justify-between">
                <div className="text-sm text-gray-700">
                  Showing {startIndex + 1} to {Math.min(endIndex, filteredPositions.length)} of {filteredPositions.length} positions
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
                    disabled={currentPage === 1}
                    className="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Previous
                  </button>
                  <span className="text-sm text-gray-600">
                    Page {currentPage} of {totalPages}
                  </span>
                  <button
                    onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
                    disabled={currentPage === totalPages}
                    className="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Next
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </AppLayout>
  );

}

interface NewPositionModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: NewPositionFormData) => void;

}

function NewPositionModal({ isOpen, onClose, onSubmit }: NewPositionModalProps) {
  const [formData, setFormData] = useState<NewPositionFormData>(getDefaultFormData());
  const [formError, setFormError] = useState<string | null>(null);
  useEffect(() => {
    if (isOpen) {
      setFormData(getDefaultFormData());
      setFormError(null);
    }
  }, [isOpen]);
  useEffect(() => {
    if (!isOpen) {
      return;
    }
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        onClose();
      }
    };
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    window.addEventListener('keydown', handleKeyDown);
    return () => {
      document.body.style.overflow = previousOverflow;
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [isOpen, onClose]);
  if (!isOpen) return null;
  const handleInputChange = (event: ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = event.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };
  const handleCheckboxChange = (event: ChangeEvent<HTMLInputElement>) => {
    const { name, checked } = event.target;
    setFormData(prev => ({ ...prev, [name]: checked }));
  };
  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!formData.title.trim() || !formData.department.trim() || !formData.location) {
      setFormError('Please select a location and complete the required fields.');
      return;
    }
    const salaryMin = Number(formData.salaryMin);
    const salaryMax = Number(formData.salaryMax);
    if (Number.isNaN(salaryMin) || Number.isNaN(salaryMax)) {
      setFormError('Salary fields must be valid numbers.');
      return;
    }
    if (salaryMin > salaryMax) {
      setFormError('Minimum salary cannot be greater than maximum salary.');
      return;
    }
    setFormError(null);
    onSubmit(formData);
  };
  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4 py-8"
      onClick={onClose}
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="new-position-modal-title"
        tabIndex={-1}
        className="w-full max-w-3xl rounded-xl bg-white shadow-xl max-h-[calc(100vh-4rem)] overflow-y-auto"
        onClick={(event) => event.stopPropagation()}
      >
        <div className="flex items-center justify-between border-b border-gray-200 px-6 py-4">
          <div>
            <h2 id="new-position-modal-title" className="text-lg font-semibold text-gray-900">Create New Position</h2>
            <p className="text-sm text-gray-500">Add a new job posting to your positions list.</p>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="rounded-full p-1 text-gray-400 transition-colors hover:text-gray-600"
          >
            <X className="h-5 w-5" />
          </button>
        </div>
        <form onSubmit={handleSubmit} className="space-y-5 px-6 py-5">
          {formError && (
            <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-2 text-sm text-red-600">
              {formError}
            </div>
          )}
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700" htmlFor="title">
                Title <span className="text-red-500">*</span>
              </label>
              <input
                id="title"
                name="title"
                value={formData.title}
                onChange={handleInputChange}
                placeholder="e.g. Senior Software Engineer"
                className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-transparent focus:outline-none focus:ring-2 focus:ring-[var(--brand-primary)]"
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700" htmlFor="department">
                Department <span className="text-red-500">*</span>
              </label>
              <input
                id="department"
                name="department"
                value={formData.department}
                onChange={handleInputChange}
                placeholder="e.g. Engineering"
                className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-transparent focus:outline-none focus:ring-2 focus:ring-[var(--brand-primary)]"
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700" htmlFor="location">
                Location <span className="text-red-500">*</span>
              </label>
              <select
                id="location"
                name="location"
                value={formData.location}
                onChange={handleInputChange}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-transparent focus:outline-none focus:ring-2 focus:ring-[var(--brand-primary)]"
              >
                <option value="" disabled>Select location</option>
                {LOCATION_OPTIONS.map(({ label, value }) => (
                  <option key={value} value={value}>
                    {label}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700" htmlFor="job_type">Type</label>
              <select
                id="job_type"
                name="job_type"
                value={formData.job_type}
                onChange={handleInputChange}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-transparent focus:outline-none focus:ring-2 focus:ring-[var(--brand-primary)]"
              >
                <option value="full_time">Full-time</option>
                <option value="part_time">Part-time</option>
                <option value="contract">Contract</option>
                <option value="internship">Internship</option>
                <option value="freelance">Freelance</option>
                <option value="temporary">Temporary</option>
              </select>
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700" htmlFor="experience_level">Level</label>
              <select
                id="experience_level"
                name="experience_level"
                value={formData.experience_level}
                onChange={handleInputChange}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-transparent focus:outline-none focus:ring-2 focus:ring-[var(--brand-primary)]"
              >
                <option value="entry_level">Entry Level</option>
                <option value="mid_level">Mid Level</option>
                <option value="senior_level">Senior Level</option>
                <option value="executive">Executive</option>
                <option value="internship">Internship</option>
              </select>
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700" htmlFor="status">Status</label>
              <select
                id="status"
                name="status"
                value={formData.status}
                onChange={handleInputChange}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-transparent focus:outline-none focus:ring-2 focus:ring-[var(--brand-primary)]"
              >
                <option value="draft">Draft</option>
                <option value="published">Published</option>
                <option value="paused">Paused</option>
                <option value="closed">Closed</option>
                <option value="archived">Archived</option>
              </select>
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700" htmlFor="remote_type">Remote Work</label>
              <select
                id="remote_type"
                name="remote_type"
                value={formData.remote_type}
                onChange={handleInputChange}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-transparent focus:outline-none focus:ring-2 focus:ring-[var(--brand-primary)]"
              >
                <option value="on_site">On-site</option>
                <option value="remote">Remote</option>
                <option value="hybrid">Hybrid</option>
              </select>
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700" htmlFor="postedDate">Posted Date</label>
              <input
                id="postedDate"
                name="postedDate"
                type="date"
                value={formData.postedDate}
                onChange={handleInputChange}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-transparent focus:outline-none focus:ring-2 focus:ring-[var(--brand-primary)]"
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700" htmlFor="deadline">Application Deadline</label>
              <input
                id="deadline"
                name="deadline"
                type="date"
                value={formData.deadline}
                onChange={handleInputChange}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-transparent focus:outline-none focus:ring-2 focus:ring-[var(--brand-primary)]"
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700" htmlFor="salaryMin">Salary Min (¥)</label>
              <input
                id="salaryMin"
                name="salaryMin"
                type="number"
                min="0"
                step="100000"
                value={formData.salaryMin}
                onChange={handleInputChange}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-transparent focus:outline-none focus:ring-2 focus:ring-[var(--brand-primary)]"
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700" htmlFor="salaryMax">Salary Max (¥)</label>
              <input
                id="salaryMax"
                name="salaryMax"
                type="number"
                min="0"
                step="100000"
                value={formData.salaryMax}
                onChange={handleInputChange}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-transparent focus:outline-none focus:ring-2 focus:ring-[var(--brand-primary)]"
              />
            </div>
          </div>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <div className="md:col-span-2">
              <label className="mb-1 block text-sm font-medium text-gray-700" htmlFor="description">Position Description</label>
              <textarea
                id="description"
                name="description"
                rows={4}
                value={formData.description}
                onChange={handleInputChange}
                placeholder="Outline the responsibilities and expectations for this role."
                className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-transparent focus:outline-none focus:ring-2 focus:ring-[var(--brand-primary)]"
              ></textarea>
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700" htmlFor="requirements">Requirements</label>
              <textarea
                id="requirements"
                name="requirements"
                rows={4}
                value={formData.requirements}
                onChange={handleInputChange}
                placeholder="List each requirement on a new line."
                className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-transparent focus:outline-none focus:ring-2 focus:ring-[var(--brand-primary)]"
              ></textarea>
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700" htmlFor="benefits">Benefits</label>
              <textarea
                id="benefits"
                name="benefits"
                rows={4}
                value={formData.benefits}
                onChange={handleInputChange}
                placeholder="List each benefit on a new line."
                className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-transparent focus:outline-none focus:ring-2 focus:ring-[var(--brand-primary)]"
              ></textarea>
            </div>
          </div>
          <div className="flex flex-wrap gap-6">
            <label className="flex items-center gap-2 text-sm font-medium text-gray-700">
              <input
                type="checkbox"
                name="is_urgent"
                checked={formData.is_urgent}
                onChange={handleCheckboxChange}
                className="h-4 w-4 rounded border-gray-300 text-[var(--brand-primary)] focus:ring-[var(--brand-primary)]"
              />
              Mark as urgent
            </label>
          </div>
          <div className="flex justify-end gap-3 border-t border-gray-200 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="rounded-lg px-4 py-2 text-sm font-semibold text-white transition-colors"
              style={{ backgroundColor: 'var(--brand-primary)' }}
            >
              Create Position
            </button>
          </div>
        </form>
      </div>
    </div>
  );

}

export default function PositionsPage() {
  return (
    <ProtectedRoute>
      <PositionsPageContent />
    </ProtectedRoute>
  );

}
