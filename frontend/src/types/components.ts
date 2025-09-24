import { type ReactNode, type ButtonHTMLAttributes, type InputHTMLAttributes } from 'react';
import { LucideIcon } from 'lucide-react';
import type { CalendarEvent } from './interview';

// ====================
// UI COMPONENT INTERFACES
// ====================

// Card Component Types
export interface CardProps {
  children: ReactNode;
  className?: string;
  padding?: 'none' | 'sm' | 'md' | 'lg';
  shadow?: 'none' | 'sm' | 'md' | 'lg';
}

export interface CardContentProps {
  children: ReactNode;
  className?: string;
}

export interface CardHeaderProps {
  children: ReactNode;
  className?: string;
}

export interface CardTitleProps {
  children: ReactNode;
  className?: string;
}

export interface CardDescriptionProps {
  children: ReactNode;
  className?: string;
}

// Badge Component Types
export interface BadgeProps {
  children: ReactNode;
  variant?:
    | 'primary'
    | 'secondary'
    | 'success'
    | 'warning'
    | 'error'
    | 'destructive'
    | 'default'
    | 'outline';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

// Toggle Component Types
export interface ToggleProps {
  id?: string;
  checked: boolean;
  onChange: (checked: boolean) => void;
  disabled?: boolean;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

// Loading Spinner Component Types
export interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
}

// Button Component Types (already in ui.ts, kept here for completeness)
export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
  leftIcon?: ReactNode;
  rightIcon?: ReactNode;
  fullWidth?: boolean;
}

// Input Component Types (already in ui.ts, kept here for completeness)
export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  leftIcon?: ReactNode;
  rightIcon?: ReactNode;
  fullWidth?: boolean;
}

// ====================
// LAYOUT COMPONENT INTERFACES
// ====================

// App Layout Types
export interface AppLayoutProps {
  children: ReactNode;
  pageTitle?: string;
  pageDescription?: string;
}

// Sidebar Component Types
export interface SidebarProps {
  isOpen: boolean;
  isCollapsed: boolean;
  onClose: () => void;
  onToggleCollapse: () => void;
  isMobile: boolean;
}

export interface NavItem {
  name: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  roles: string[];
  color: string;
  lightColor: string;
}

// Topbar Component Types
export interface TopbarProps {
  onMenuClick?: () => void;
  pageTitle?: string;
  pageDescription?: string;
}

// ====================
// COMMON COMPONENT INTERFACES
// ====================

// Brand Component Types
export interface BrandProps {
  className?: string;
  showText?: boolean;
}

// Search Input Component Types
export interface SearchInputProps {
  placeholder?: string;
  onSearch?: (query: string) => void;
  className?: string;
}

// Stat Card Component Types
export interface StatCardProps {
  title: string;
  value: string | number;
  icon: LucideIcon;
  change?: {
    value: number;
    trend: 'up' | 'down';
    period: string;
  };
  color?: 'primary' | 'blue' | 'green' | 'orange' | 'red' | 'accent';
  loading?: boolean;
}

// ====================
// AUTH COMPONENT INTERFACES
// ====================

// Login Form Component Types
export interface LoginFormProps {
  onSuccess?: () => void;
  onForgotPassword?: () => void;
}

// Two Factor Form Component Types
export interface TwoFactorFormProps {
  onSubmit: (code: string) => Promise<void>;
  onResend?: () => Promise<void>;
  isLoading?: boolean;
  error?: string;
}

// ====================
// TESTING COMPONENT INTERFACES
// ====================

// API Test Runner Component Types
export interface TestResult {
  name: string;
  status: 'pass' | 'fail' | 'pending';
  details: string;
  duration?: number;
}

export interface TestSuite {
  name: string;
  tests: TestResult[];
  completed: boolean;
}

// ====================
// NOTIFICATION COMPONENT INTERFACES
// ====================

export interface NotificationDropdownProps {
  isOpen: boolean;
  onToggle: () => void;
}

// ====================
// COMPONENT PROP INTERFACES
// ====================

// Calendar Component Props
export interface CalendarViewProps {
  currentDate: Date;
  onDateChange: (date: Date) => void;
  viewType: 'month' | 'week' | 'day';
  events: CalendarEvent[];
  onDateSelect: (date: Date) => void;
  onEventClick: (event: CalendarEvent) => void;
  loading: boolean;
  canCreateEvents: boolean;
}

export interface CalendarSidebarProps {
  isOpen: boolean;
  onClose: () => void;
  events: CalendarEvent[];
  onEventClick: (event: CalendarEvent) => void;
  filters: {
    eventType: string;
    status: string;
    search: string;
  };
  onFiltersChange: (filters: { eventType: string; status: string; search: string }) => void;
  userRole: string;
}

export interface EventModalProps {
  isOpen: boolean;
  onClose: () => void;
  event: CalendarEvent | null;
  selectedDate: Date | null;
  isCreateMode: boolean;
  onSave: (eventData: Partial<CalendarEvent>) => void;
  onDelete: (event: CalendarEvent) => Promise<void> | void;
}

export interface EventFormData {
  title: string;
  description: string;
  location: string;
  startDatetime: string;
  endDatetime: string;
  timezone: string;
  isAllDay: boolean;
  attendees: string[];
  status: string;
}

// Auth Component Props
export interface ProtectedRouteProps {
  children: React.ReactNode;
  allowedRoles?: string[];
  fallback?: React.ReactNode;
  redirectTo?: string;
}

export interface ResetPasswordFormProps {
  onSubmit: (password: string) => Promise<void>;
  isLoading?: boolean;
  error?: string;
}

export interface ForgotPasswordFormProps {
  onSubmit: (email: string) => Promise<void>;
  isLoading?: boolean;
  error?: string;
}

// UI Component Props
export interface ConfirmationModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  message: string | React.ReactNode;
  confirmText?: string;
  cancelText?: string;
  variant?: 'danger' | 'warning' | 'info';
  confirmButtonClass?: string;
  icon?: React.ReactNode;
}

export interface WebsiteLayoutProps {
  children: React.ReactNode;
}

export interface PlaceholderPageProps {
  title: string;
  description: string;
  icon?: React.ReactNode;
  actions?: React.ReactNode;
  primaryAction?: {
    label: string;
    onClick: () => void;
  };
}
