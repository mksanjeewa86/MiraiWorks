import type { AttendeeInfo } from './interview';

export interface CalendarConnection {
  id: number;
  provider: 'google' | 'outlook';
  provider_email: string;
  display_name?: string;
  is_enabled: boolean;
  sync_events: boolean;
  sync_reminders: boolean;
  auto_create_meetings: boolean;
  status: 'connected' | 'error' | 'expired' | 'disabled';
  last_sync_at?: string;
  sync_error?: string;
  created_at: string;
  updated_at: string;
}

export interface CalendarConnectionUpdate {
  display_name?: string;
  is_enabled?: boolean;
  sync_events?: boolean;
  sync_reminders?: boolean;
  auto_create_meetings?: boolean;
  calendar_ids?: string[];
  default_calendar_id?: string;
}

export interface CalendarConnectionResponse {
  message: string;
  connection: CalendarConnection;
}

export interface CalendarListResponse {
  connections: CalendarConnection[];
}

export interface CalendarAuthResponse {
  auth_url: string;
}

export type CalendarProvider = 'google' | 'outlook';

// ==================== INTERNAL CALENDAR EVENTS ====================

export enum EventType {
  EVENT = 'event',
  MEETING = 'meeting',
  TASK = 'task',
  APPOINTMENT = 'appointment',
  REMINDER = 'reminder',
  BIRTHDAY = 'birthday',
  DEADLINE = 'deadline',
}

export enum EventStatus {
  CONFIRMED = 'confirmed',
  TENTATIVE = 'tentative',
  CANCELLED = 'cancelled',
  POSTPONED = 'postponed',
}

export interface CalendarEventBase {
  title: string;
  description?: string;
  start_datetime: string;
  end_datetime?: string;
  is_all_day?: boolean;
  location?: string;
  event_type?: EventType;
  status?: EventStatus;
  recurrence_rule?: string;
  timezone?: string;
  attendees?: string[];
}

export type CalendarEventCreate = CalendarEventBase;

export interface CalendarEventUpdate {
  title?: string;
  description?: string;
  start_datetime?: string;
  end_datetime?: string;
  is_all_day?: boolean;
  location?: string;
  event_type?: EventType;
  status?: EventStatus;
  recurrence_rule?: string;
  timezone?: string;
  attendees?: string[];
}

export interface CalendarEventInfo extends Omit<CalendarEventBase, 'attendees'> {
  id: number;
  creator_id?: number;
  created_at: string;
  updated_at: string;
  parent_event_id?: number;
  is_recurring: boolean;
  is_instance: boolean;
  attendees?: AttendeeInfo[];
}

export interface CalendarEventListResponse {
  events: CalendarEventInfo[];
  total: number;
  start_date?: string;
  end_date?: string;
}

export interface CalendarEventQueryParams {
  start_date?: string;
  end_date?: string;
  event_type?: EventType;
  status?: EventStatus;
  creator_id?: number;
  include_all_day?: boolean;
  include_recurring?: boolean;
  timezone?: string;
}

export interface CalendarEventBulkCreate {
  events: CalendarEventCreate[];
}

export interface CalendarEventBulkResponse {
  created_events: CalendarEventInfo[];
  failed_events: any[];
  total_created: number;
  total_failed: number;
}

// ==================== CONSOLIDATED CALENDAR VIEW ====================

export interface ConsolidatedCalendarEvent {
  id: string;
  title: string;
  description?: string;
  start: string;
  end?: string;
  allDay: boolean;
  location?: string;
  type?: string;
  status?: string;
  source: 'internal' | 'external' | 'holiday';
  country?: string; // For holidays
}

export interface ConsolidatedCalendarData {
  internal_events: ConsolidatedCalendarEvent[];
  external_events: ConsolidatedCalendarEvent[];
  holidays: ConsolidatedCalendarEvent[];
}

// ==================== LEGACY COMPATIBILITY ====================

// Calendar Event Input type for creating/updating events (legacy)
export interface CalendarEventInput {
  title: string;
  description?: string;
  location?: string;
  startDatetime: string;
  endDatetime: string;
  timezone?: string;
  isAllDay?: boolean;
  attendees?: string[];
  status?: string;
}

// ============================================================================
// CALENDAR UI TYPES
// ============================================================================

// Selection Range (from app/calendar/page.tsx)
export interface SelectionRange {
  start: Date;
  end: Date;
  allDay: boolean;
}
