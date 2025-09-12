import {
  Company,
  CompanyType,
  CompanyCreate,
  CompanyUpdate,
  CompanyListResponse,
  CompanyFilters
} from '../types/company';

const API_BASE_URL = 'http://localhost:8000';

// Helper function to get auth token from localStorage
const getAuthToken = (): string | null => {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('accessToken');
  }
  return null;
};

// Helper function to make authenticated requests
const makeAuthenticatedRequest = async <T>(
  url: string,
  options: RequestInit = {}
): Promise<{ data: T }> => {
  const token = getAuthToken();
  
  const response = await fetch(`${API_BASE_URL}${url}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
      ...options.headers,
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(errorData.detail || `API request failed: ${response.status} ${response.statusText}`);
  }

  const data = await response.json();
  return { data };
};

export const companiesApi = {
  // Get companies with filters and pagination
  getCompanies: (filters: CompanyFilters = {}) => {
    const params = new URLSearchParams();
    
    if (filters.page) params.append('page', filters.page.toString());
    if (filters.size) params.append('size', filters.size.toString());
    if (filters.search) params.append('search', filters.search);
    if (filters.company_type) params.append('company_type', filters.company_type);
    if (filters.is_active !== undefined) params.append('is_active', filters.is_active.toString());
    
    const queryString = params.toString();
    const url = `/api/admin/companies${queryString ? `?${queryString}` : ''}`;
    
    return makeAuthenticatedRequest<CompanyListResponse>(url);
  },

  // Get single company by ID
  getCompany: (companyId: number) =>
    makeAuthenticatedRequest<Company>(`/api/admin/companies/${companyId}`),

  // Create new company
  createCompany: (companyData: CompanyCreate) =>
    makeAuthenticatedRequest<Company>('/api/admin/companies', {
      method: 'POST',
      body: JSON.stringify(companyData),
    }),

  // Update company
  updateCompany: (companyId: number, companyData: CompanyUpdate) =>
    makeAuthenticatedRequest<Company>(`/api/admin/companies/${companyId}`, {
      method: 'PUT',
      body: JSON.stringify(companyData),
    }),

  // Delete company
  deleteCompany: (companyId: number) =>
    makeAuthenticatedRequest<{ message: string }>(`/api/admin/companies/${companyId}`, {
      method: 'DELETE',
    }),
};