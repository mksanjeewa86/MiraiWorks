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
