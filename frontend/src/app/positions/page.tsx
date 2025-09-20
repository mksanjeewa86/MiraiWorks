'use client';
import { useState, useEffect } from 'react';
import type { ChangeEvent, FormEvent, CSSProperties } from 'react';
import AppLayout from '@/components/layout/AppLayout';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import { PREFECTURES } from '@/utils/prefectures';
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

interface Position {
  id: number;
  title: string;
  company: string;
  department: string;
  location: string;
  type: 'full-time' | 'part-time' | 'contract' | 'internship';
  level: 'entry' | 'mid' | 'senior' | 'executive';
  salaryMin: number;
  salaryMax: number;
  status: 'draft' | 'published' | 'paused' | 'closed' | 'filled';
  applications: number;
  views: number;
  postedDate: string;
  deadline: string;
  description: string;
  requirements: string[];
  benefits: string[];
  remote: boolean;
  urgent: boolean;
}

interface NewPositionFormData {
  title: string;
  department: string;
  location: string;
  type: Position['type'];
  level: Position['level'];
  salaryMin: string;
  salaryMax: string;
  status: Position['status'];
  postedDate: string;
  deadline: string;
  description: string;
  requirements: string;
  benefits: string;
  remote: boolean;
  urgent: boolean;
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
    type: 'full-time',
    level: 'entry',
    salaryMin: '',
    salaryMax: '',
    status: 'draft',
    postedDate: formatDateInput(today),
    deadline: formatDateInput(defaultDeadline),
    description: '',
    requirements: '',
    benefits: '',
    remote: false,
    urgent: false,
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
// Mock data
const mockPositions: Position[] = [
  {
    id: 1,
    title: 'Senior Full Stack Developer',
    company: 'TechCorp Inc.',
    department: 'Engineering',
    location: 'Tokyo, Japan',
    type: 'full-time',
    level: 'senior',
    salaryMin: 8000000,
    salaryMax: 12000000,
    status: 'published',
    applications: 42,
    views: 156,
    postedDate: '2024-01-15',
    deadline: '2024-02-15',
    description: 'We are looking for a senior full stack developer to join our growing team...',
    requirements: ['React', 'Node.js', 'TypeScript', '5+ years experience'],
    benefits: ['Health Insurance', 'Remote Work', 'Stock Options'],
    remote: true,
    urgent: false
  },
  {
    id: 2,
    title: 'Product Manager',
    company: 'StartupXYZ',
    department: 'Product',
    location: 'Osaka, Japan',
    type: 'full-time',
    level: 'mid',
    salaryMin: 6000000,
    salaryMax: 9000000,
    status: 'published',
    applications: 28,
    views: 89,
    postedDate: '2024-01-18',
    deadline: '2024-02-18',
    description: 'Join our product team to drive innovation and user experience...',
    requirements: ['Product Management', 'Agile', 'Data Analysis', '3+ years experience'],
    benefits: ['Flexible Hours', 'Learning Budget', 'Team Events'],
    remote: false,
    urgent: true
  },
  {
    id: 3,
    title: 'UX/UI Designer',
    company: 'Design Studio Co.',
    department: 'Design',
    location: 'Remote',
    type: 'contract',
    level: 'mid',
    salaryMin: 4000000,
    salaryMax: 6000000,
    status: 'paused',
    applications: 15,
    views: 67,
    postedDate: '2024-01-10',
    deadline: '2024-02-10',
    description: 'Create beautiful and intuitive user experiences for our digital products...',
    requirements: ['Figma', 'Adobe Creative Suite', 'User Research', '2+ years experience'],
    benefits: ['Remote Work', 'Creative Freedom', 'Portfolio Projects'],
    remote: true,
    urgent: false
  },
  {
    id: 4,
    title: 'Data Scientist',
    company: 'Analytics Pro',
    department: 'Data Science',
    location: 'Tokyo, Japan',
    type: 'full-time',
    level: 'senior',
    salaryMin: 7000000,
    salaryMax: 10000000,
    status: 'filled',
    applications: 67,
    views: 203,
    postedDate: '2024-01-05',
    deadline: '2024-02-05',
    description: 'Lead data science initiatives and build predictive models...',
    requirements: ['Python', 'Machine Learning', 'SQL', 'PhD preferred'],
    benefits: ['Research Time', 'Conference Budget', 'Publication Support'],
    remote: true,
    urgent: false
  },
  {
    id: 5,
    title: 'Marketing Coordinator',
    company: 'Growth Marketing Inc.',
    department: 'Marketing',
    location: 'Nagoya, Japan',
    type: 'full-time',
    level: 'entry',
    salaryMin: 3000000,
    salaryMax: 4500000,
    status: 'draft',
    applications: 0,
    views: 0,
    postedDate: '2024-01-20',
    deadline: '2024-02-20',
    description: 'Support marketing campaigns and content creation efforts...',
    requirements: ['Marketing Basics', 'Content Creation', 'Social Media', 'Fresh Graduate OK'],
    benefits: ['Training Program', 'Mentorship', 'Career Growth'],
    remote: false,
    urgent: false
  }

];

function PositionsPageContent() {
  const [positions, setPositions] = useState<Position[]>(mockPositions);
  const [filteredPositions, setFilteredPositions] = useState<Position[]>(mockPositions);
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

  // Apply filters and search
  useEffect(() => {
    const filtered = positions.filter(position => {
      const matchesSearch = position.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          position.company.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          position.department.toLowerCase().includes(searchTerm.toLowerCase());
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
  const handleCreatePosition = (formData: NewPositionFormData) => {
    const parseMultiline = (value: string) => (
      value
        .split('\n')
        .map(item => item.trim())
        .filter(Boolean)
    );
    const salaryMin = Number(formData.salaryMin);
    const salaryMax = Number(formData.salaryMax);
    const nextId = positions.reduce((maxId, position) => Math.max(maxId, position.id), 0) + 1;
    const companyName = positions[0]?.company ?? 'Not specified';
    const newPosition: Position = {
      id: nextId,
      title: formData.title.trim(),
      company: companyName,
      department: formData.department.trim(),
      location: formData.location,
      type: formData.type,
      level: formData.level,
      salaryMin,
      salaryMax,
      status: formData.status,
      applications: 0,
      views: 0,
      postedDate: formData.postedDate,
      deadline: formData.deadline,
      description: formData.description.trim(),
      requirements: parseMultiline(formData.requirements),
      benefits: parseMultiline(formData.benefits),
      remote: formData.remote,
      urgent: formData.urgent,
    };
    setPositions(prev => [newPosition, ...prev]);
    setIsNewPositionOpen(false);
    setCurrentPage(1);
  };
  // Helper functions
  const getStatusBadge = (status: Position['status']) => {
    const styles = {
      draft: 'bg-gray-100 text-gray-800 border-gray-200',
      published: 'bg-green-100 text-green-800 border-green-200',
      paused: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      closed: 'bg-red-100 text-red-800 border-red-200',
      filled: 'bg-blue-100 text-blue-800 border-blue-200'
    };
    return styles[status];
  };
  const getTypeBadge = (type: Position['type']) => {
    const styles = {
      'full-time': 'bg-blue-50 text-blue-700 border-blue-200',
      'part-time': 'bg-purple-50 text-purple-700 border-purple-200',
      'contract': 'bg-orange-50 text-orange-700 border-orange-200',
      'internship': 'bg-pink-50 text-pink-700 border-pink-200'
    };
    return styles[type];
  };
  const getLevelBadge = (level: Position['level']) => {
    const styles = {
      'entry': 'bg-green-50 text-green-700 border-green-200',
      'mid': 'bg-blue-50 text-blue-700 border-blue-200',
      'senior': 'bg-purple-50 text-purple-700 border-purple-200',
      'executive': 'bg-red-50 text-red-700 border-red-200'
    };
    return styles[level];
  };
  const formatSalary = (min: number, max: number) => {
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
                <option value="filled">Filled</option>
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
                {currentPositions.length === 0 ? (
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
              <label className="mb-1 block text-sm font-medium text-gray-700" htmlFor="type">Type</label>
              <select
                id="type"
                name="type"
                value={formData.type}
                onChange={handleInputChange}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-transparent focus:outline-none focus:ring-2 focus:ring-[var(--brand-primary)]"
              >
                <option value="full-time">Full-time</option>
                <option value="part-time">Part-time</option>
                <option value="contract">Contract</option>
                <option value="internship">Internship</option>
              </select>
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700" htmlFor="level">Level</label>
              <select
                id="level"
                name="level"
                value={formData.level}
                onChange={handleInputChange}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-transparent focus:outline-none focus:ring-2 focus:ring-[var(--brand-primary)]"
              >
                <option value="entry">Entry</option>
                <option value="mid">Mid</option>
                <option value="senior">Senior</option>
                <option value="executive">Executive</option>
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
                <option value="filled">Filled</option>
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
                name="remote"
                checked={formData.remote}
                onChange={handleCheckboxChange}
                className="h-4 w-4 rounded border-gray-300 text-[var(--brand-primary)] focus:ring-[var(--brand-primary)]"
              />
              Remote friendly role
            </label>
            <label className="flex items-center gap-2 text-sm font-medium text-gray-700">
              <input
                type="checkbox"
                name="urgent"
                checked={formData.urgent}
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
