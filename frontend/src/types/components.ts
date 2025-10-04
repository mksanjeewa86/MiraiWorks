// Component Props - Centralized type definitions
import type {
  Resume,
  CalendarConnection,
  TodoWithAssignedUser,
  RecruitmentProcess,
  LinearWorkflowStep,
} from '@/types';
import type { ChatMessage, TranscriptionSegment } from '@/types/video';
import type { Interview, InterviewFormData, InterviewEditFormData } from '@/types/interview';
import type { SelectionRange } from '@/types/calendar';
import type { MBTITestProgress } from '@/types/mbti';
import type { UserManagement } from '@/types/user';
import type { Question, Answer, QuestionFormData } from '@/types/exam';
import type {
  LabelHTMLAttributes,
  InputHTMLAttributes,
  HTMLAttributes,
  SelectHTMLAttributes,
  TextareaHTMLAttributes,
} from 'react';

// ====================
// VIDEO COMPONENTS
// ====================

export interface VideoControlsProps {
  isMuted: boolean;
  isVideoOn: boolean;
  isScreenSharing: boolean;
  onToggleAudio: () => void;
  onToggleVideo: () => void;
  onStartScreenShare: () => void;
  onStopScreenShare: () => void;
  onEndCall: () => void;
  onToggleTranscription: () => void;
  showTranscription: boolean;
  onToggleChat: () => void;
  showChat: boolean;
  onToggleFullScreen: () => void;
  isFullScreen: boolean;
}

export interface VideoCallRoomProps {
  callId?: string;
  roomCode?: string;
}

export interface ParticipantVideoProps {
  stream: MediaStream | null;
  isLocal: boolean;
  participantName: string;
  isMuted: boolean;
  className?: string;
}

export interface ConnectionStatusProps {
  isConnected: boolean;
  quality: 'excellent' | 'good' | 'fair' | 'poor';
  participantCount: number;
}

export interface ChatPanelProps {
  messages: ChatMessage[];
  onSendMessage: (message: string, type?: string) => void;
  currentUserId: number;
  isVisible: boolean;
  onToggleVisibility: () => void;
}

export interface TranscriptionPanelProps {
  segments: TranscriptionSegment[];
  isTranscribing: boolean;
  language: string;
  onLanguageChange: (language: string) => void;
  callId?: string;
}

export interface LanguageSelectorProps {
  value: string;
  onChange: (language: string) => void;
}

export interface ScreenShareViewProps {
  stream: MediaStream | null;
  isSharing: boolean;
  onStopSharing: () => void;
  onToggleFullScreen: () => void;
  isFullScreen: boolean;
  sharerName: string;
}

export interface RecordingConsentProps {
  onSubmit: (consented: boolean) => void;
  onClose: () => void;
}

// ====================
// INTERVIEW COMPONENTS
// ====================

export interface InterviewModalProps {
  isOpen: boolean;
  mode: 'create' | 'edit';
  interviewId?: number;
  onClose: () => void;
  onSuccess: (interview: Interview | InterviewFormData) => void;
  defaultData?: Partial<InterviewFormData>;
  workflowContext?: boolean;
}

export interface InterviewEditModalProps {
  isOpen: boolean;
  onClose: () => void;
  interviewId: number;
  onSuccess: () => void;
}

export interface InterviewNotesProps {
  interviewId: number;
  className?: string;
}

// ====================
// PROFILE COMPONENTS
// ====================

export interface CandidateProfileProps {
  userId?: number;
  isPublic?: boolean;
}

// ====================
// MBTI COMPONENTS
// ====================

export interface MBTITypeAvatarProps {
  type: string;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  showLabel?: boolean;
}

export interface MBTITestButtonProps {
  onStartTest: () => void;
  className?: string;
  language?: 'en' | 'ja';
}

// ====================
// TODO COMPONENTS
// ====================

export interface AssignmentWorkflowProps {
  todo: TodoWithAssignedUser;
  onUpdate: () => void;
}

// ====================
// RESUME COMPONENTS
// ====================

export interface ResumePreviewProps {
  resume: Resume;
  previewHtml: string;
  loading?: boolean;
  showControls?: boolean;
  onPrint?: () => void;
  className?: string;
}

// ====================
// CALENDAR COMPONENTS
// ====================

export interface CalendarFilters {
  search: string;
}

export type CalendarViewMode = 'month' | 'week' | 'day' | 'list';

// Re-export SelectionRange for convenience
export type { SelectionRange };

export interface CalendarViewProps {
  currentDate: Date;
  onDateChange: (date: Date) => void;
  viewType: CalendarViewMode;
  onViewChange: (view: CalendarViewMode) => void;
  events: import('@/types/interview').CalendarEvent[];
  onRangeSelect?: (range: SelectionRange) => void;
  onEventClick: (event: import('@/types/interview').CalendarEvent) => void;
  loading?: boolean;
  canCreateEvents?: boolean;
}

export interface CalendarSidebarProps {
  isOpen: boolean;
  onClose: () => void;
  events: import('@/types/interview').CalendarEvent[];
  onEventClick: (event: import('@/types/interview').CalendarEvent) => void;
  filters: CalendarFilters;
  onFiltersChange: (filters: CalendarFilters) => void;
  onCreateEvent: () => void;
  connections: CalendarConnection[];
  onConnectProvider: (
    provider: import('@/types/calendar').CalendarProvider
  ) => void | Promise<void>;
  onDisconnect: (connectionId: number) => void | Promise<void>;
  onSync: (connectionId: number) => void | Promise<void>;
  loadingConnections: boolean;
  syncingConnectionId?: number | null;
}

export interface EventFormData {
  title: string;
  description: string;
  location: string;
  startDatetime: string;
  endDatetime: string;
  isAllDay: boolean;
  attendees: string[];
  status: string;
  timezone: string;
}

export interface EventModalProps {
  isOpen: boolean;
  onClose: () => void;
  event?: import('@/types/interview').CalendarEvent | null;
  selectedDate?: Date | null;
  selectedRange?: SelectionRange | null;
  isCreateMode: boolean;
  onSave: (event: Partial<import('@/types/interview').CalendarEvent>) => Promise<void>;
  onDelete: (event: import('@/types/interview').CalendarEvent) => Promise<void>;
}

export interface ConnectionListProps {
  connections: CalendarConnection[];
  onConnectProvider: CalendarSidebarProps['onConnectProvider'];
  onDisconnect: CalendarSidebarProps['onDisconnect'];
  onSync: CalendarSidebarProps['onSync'];
  loadingConnections: boolean;
  syncingConnectionId?: number | null;
}

// ====================
// EXAM COMPONENTS
// ====================

export interface ExamQuestionProps {
  question: Question;
  answer?: Answer;
  onAnswerChange: (answer: Partial<Answer>) => void;
}

export interface ExamQuestionFormProps {
  question: QuestionFormData;
  onSave: (question: QuestionFormData) => void;
  onCancel: () => void;
}

export interface ExamTimerProps {
  timeRemaining: number;
  onTimeUp: () => void;
}

export interface FaceVerificationProps {
  sessionId: number;
  onComplete: (success: boolean) => void;
}

export interface WebUsageMonitorProps {
  onWebUsageDetected: (eventType: string, eventData: any) => void;
  allowWebUsage: boolean;
}

// ====================
// COMMON COMPONENTS
// ====================

export interface BrandProps {
  className?: string;
  showText?: boolean;
}

export interface PlaceholderPageProps {
  title: string;
  description: string;
  icon?: string;
  actions?: React.ReactNode;
  primaryAction?: {
    label: string;
    onClick: () => void;
  };
}

export interface SearchInputProps {
  placeholder?: string;
  onSearch?: (query: string) => void;
  className?: string;
}

export interface StatCardProps {
  title: string;
  value: string | number;
  icon: React.ComponentType<{ style?: React.CSSProperties }>;
  change?: {
    trend: 'up' | 'down';
    value: number;
    period: string;
  };
  color?: 'primary' | 'blue' | 'green' | 'accent' | 'orange' | 'red';
  loading?: boolean;
}

// ====================
// LAYOUT COMPONENTS
// ====================

export interface AppLayoutProps {
  children: React.ReactNode;
  pageTitle?: string;
  pageDescription?: string;
}

export interface NavItem {
  name: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  roles: string[];
  color: string;
  lightColor: string;
}

export interface SidebarProps {
  isOpen: boolean;
  isCollapsed: boolean;
  onClose: () => void;
  onToggleCollapse: () => void;
  isMobile: boolean;
}

export interface TopbarProps {
  pageTitle?: string;
  pageDescription?: string;
}

export interface WebsiteLayoutProps {
  children: React.ReactNode;
}

// ====================
// UI COMPONENTS
// ====================

export interface AlertProps {
  variant?: 'default' | 'destructive' | 'success' | 'warning';
  children: React.ReactNode;
  className?: string;
}

export interface BadgeProps {
  children: React.ReactNode;
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

export interface CardProps {
  children: React.ReactNode;
  className?: string;
  padding?: 'none' | 'sm' | 'md' | 'lg';
  shadow?: 'none' | 'sm' | 'md' | 'lg';
}

export interface CardHeaderProps {
  children: React.ReactNode;
  className?: string;
}

export interface CardContentProps {
  children: React.ReactNode;
  className?: string;
}

export interface CardTitleProps {
  children: React.ReactNode;
  className?: string;
}

export interface CardDescriptionProps {
  children: React.ReactNode;
  className?: string;
}

export interface ConfirmationModalProps {
  isOpen: boolean;
  title: string;
  message: string;
  confirmLabel?: string;
  cancelLabel?: string;
  onConfirm: () => void;
  onCancel: () => void;
  variant?: 'danger' | 'warning' | 'info';
}

export interface CheckboxProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'type'> {
  className?: string;
  onCheckedChange?: (checked: boolean) => void;
}

export interface DialogProps {
  open?: boolean;
  defaultOpen?: boolean;
  onOpenChange?: (open: boolean) => void;
  modal?: boolean;
  children?: React.ReactNode;
}

export interface DialogTriggerProps {
  asChild?: boolean;
  children?: React.ReactNode;
  className?: string;
}

export interface DialogPortalProps {
  children: React.ReactNode;
  container?: HTMLElement;
}

export interface DialogOverlayProps {
  className?: string;
}

export interface DialogContentProps {
  children: React.ReactNode;
  className?: string;
  closeButton?: boolean;
  onEscapeKeyDown?: (event: KeyboardEvent) => void;
  onPointerDownOutside?: (event: PointerEvent) => void;
}

export interface DialogHeaderProps {
  className?: string;
  children?: React.ReactNode;
}

export interface DialogFooterProps {
  className?: string;
  children?: React.ReactNode;
}

export interface DialogTitleProps {
  className?: string;
  children?: React.ReactNode;
}

export interface DialogDescriptionProps {
  className?: string;
  children?: React.ReactNode;
}

export interface DialogCloseProps {
  asChild?: boolean;
  children?: React.ReactNode;
  className?: string;
}

export interface DropdownMenuProps {
  children: React.ReactNode;
  className?: string;
}

export interface DropdownMenuTriggerProps {
  asChild?: boolean;
  children: React.ReactNode;
  className?: string;
}

export interface DropdownMenuContentProps {
  children: React.ReactNode;
  className?: string;
  align?: 'start' | 'center' | 'end';
  side?: 'top' | 'right' | 'bottom' | 'left';
}

export interface DropdownMenuItemProps {
  children: React.ReactNode;
  className?: string;
  asChild?: boolean;
  disabled?: boolean;
  onClick?: () => void;
}

export interface DropdownMenuSeparatorProps {
  className?: string;
}

export interface DropdownMenuLabelProps {
  children: React.ReactNode;
  className?: string;
}

export interface LabelProps extends LabelHTMLAttributes<HTMLLabelElement> {
  error?: boolean;
}

export interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export interface ProgressProps {
  value: number;
  max?: number;
  className?: string;
  size?: 'sm' | 'md' | 'lg';
}

export interface RadioGroupProps {
  children: React.ReactNode;
  className?: string;
  value?: string;
  onValueChange?: (value: string) => void;
}

export interface RadioGroupItemProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'type'> {
  value: string;
  id?: string;
  className?: string;
}

export interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  className?: string;
  onValueChange?: (value: string) => void;
}

export interface SelectContentProps {
  children?: React.ReactNode;
  className?: string;
}

export interface SelectItemProps {
  value: string;
  children?: React.ReactNode;
  className?: string;
}

export interface SelectTriggerProps {
  className?: string;
  children?: React.ReactNode;
}

export interface SelectValueProps {
  placeholder?: string;
  className?: string;
}

export interface SeparatorProps extends HTMLAttributes<HTMLDivElement> {
  orientation?: 'horizontal' | 'vertical';
  decorative?: boolean;
}

export interface SwitchProps
  extends Omit<InputHTMLAttributes<HTMLInputElement>, 'type' | 'onCheckedChange'> {
  className?: string;
  checked?: boolean;
  onCheckedChange?: (checked: boolean) => void;
}

// ====================
// ADDITIONAL UI COMPONENTS
// ====================

export interface AlertDescriptionProps {
  children: React.ReactNode;
  className?: string;
}

export interface ConfirmationModalPropsExtended {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  message: string | React.ReactNode;
  confirmText?: string;
  cancelText?: string;
  confirmButtonClass?: string;
  icon?: React.ReactNode;
  dangerous?: boolean;
}

export interface DialogContextValue {
  open: boolean;
  setOpen: (open: boolean) => void;
}

export interface DropdownMenuContextValue {
  open: boolean;
  setOpen: (open: boolean) => void;
}

export interface ToggleProps {
  id?: string;
  checked: boolean;
  onChange: (checked: boolean) => void;
  disabled?: boolean;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

// ====================
// AUTH COMPONENTS
// ====================

export interface LoginFormProps {
  onSuccess: () => void;
  onForgotPassword: () => void;
}

export interface ForgotPasswordFormProps {
  onSubmit: (email: string) => Promise<void>;
  isLoading?: boolean;
  error?: string | null;
}

export interface ResetPasswordFormProps {
  onSubmit: (password: string) => Promise<void>;
  isLoading?: boolean;
  error?: string | null;
}

export interface ProtectedRouteProps {
  children: React.ReactNode;
  allowedRoles?: string[];
  fallback?: React.ReactNode;
  redirectTo?: string;
}

export interface TwoFactorFormProps {
  onSubmit: (code: string) => Promise<void>;
  onResend?: () => Promise<void>;
  isLoading?: boolean;
  error?: string | null;
}

// ====================
// API TEST COMPONENTS
// ====================

export interface TestResult {
  name: string;
  status: 'pending' | 'pass' | 'fail';
  details: string;
  duration?: number;
}

export interface TestSuite {
  name: string;
  tests: TestResult[];
  completed: boolean;
}

export interface TextareaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  className?: string;
}

export interface SliderProps {
  value?: number[];
  defaultValue?: number[];
  onValueChange?: (value: number[]) => void;
  min?: number;
  max?: number;
  step?: number;
  disabled?: boolean;
  className?: string;
  orientation?: 'horizontal' | 'vertical';
}
