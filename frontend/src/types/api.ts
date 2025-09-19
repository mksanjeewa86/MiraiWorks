// API Response Types
export interface ApiResponse<T = unknown> {
  data?: T;
  message?: string;
  success: boolean;
  errors?: string[];
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  hasMore: boolean;
}

// Specific backend response types that match actual API schemas
export interface EventsListResponse<T = unknown> {
  events: T[];
  next_sync_token?: string;
  has_more: boolean;
}

export interface InterviewsListResponse<T = unknown> {
  interviews: T[];
  total: number;
  has_more: boolean;
}

// Form Types
export interface FormError {
  field: string;
  message: string;
}

export interface SelectOption {
  value: string | number;
  label: string;
  disabled?: boolean;
}
