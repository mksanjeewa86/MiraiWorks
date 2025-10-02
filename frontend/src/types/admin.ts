// Admin Security Types
export interface FileSecurityInfo {
  id: number;
  filename: string;
  file_path: string;
  file_size: number;
  uploaded_by: {
    id: number;
    full_name: string;
    email: string;
  };
  virus_status: 'pending' | 'clean' | 'infected' | 'error';
  virus_scan_result?: string;
  scanned_at?: string;
  is_quarantined: boolean;
  uploaded_at: string;
}

export interface SecurityStats {
  total_files: number;
  clean_files: number;
  infected_files: number;
  pending_scans: number;
  error_scans: number;
  quarantined_files: number;
  scan_success_rate: number;
}

export interface VirusScanResult {
  file_id: number;
  status: 'clean' | 'infected' | 'error';
  result_message: string;
  scanned_at: string;
}

export interface BulkSecurityAction {
  file_ids: number[];
  action: 'scan' | 'quarantine' | 'delete' | 'restore';
  reason?: string;
}

export interface SecurityLog {
  id: number;
  action: string;
  file_id: number;
  filename: string;
  performed_by: {
    id: number;
    full_name: string;
    email: string;
  };
  details: string;
  timestamp: string;
}

// Audit Log Types
export interface AuditLogEntry {
  id: number;
  actor_id?: number;
  action: string;
  entity_type: string;
  entity_id?: number;
  entity_data?: Record<string, any>;
  changes?: Record<string, any>;
  ip_address?: string;
  user_agent?: string;
  timestamp: string;
  actor?: {
    id: number;
    full_name: string;
    email: string;
  };
}

export interface AuditLogFilters {
  actor_id?: number;
  action?: string;
  entity_type?: string;
  entity_id?: number;
  start_date?: string;
  end_date?: string;
  ip_address?: string;
  search?: string;
}

export interface AuditLogStats {
  total_entries: number;
  unique_actors: number;
  actions_today: number;
  top_actions: Array<{
    action: string;
    count: number;
  }>;
  top_entity_types: Array<{
    entity_type: string;
    count: number;
  }>;
  recent_activity_trend: Array<{
    date: string;
    count: number;
  }>;
}

export interface SystemActivity {
  login_attempts: {
    successful: number;
    failed: number;
    unique_users: number;
  };
  data_changes: {
    creates: number;
    updates: number;
    deletes: number;
  };
  security_events: {
    suspicious_activities: number;
    blocked_attempts: number;
    admin_actions: number;
  };
}

// Bulk Operations Types
export interface BulkOperation {
  id: string;
  type: 'import' | 'export' | 'delete' | 'update' | 'migrate';
  entity_type: string;
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled';
  progress: number;
  total_items: number;
  processed_items: number;
  success_count: number;
  error_count: number;
  created_by: {
    id: number;
    full_name: string;
    email: string;
  };
  created_at: string;
  started_at?: string;
  completed_at?: string;
  file_url?: string;
  error_details?: string[];
}

export interface BulkImportRequest {
  entity_type: 'users' | 'companies' | 'positions' | 'interviews' | 'candidates';
  file: File;
  options: {
    skip_duplicates?: boolean;
    update_existing?: boolean;
    validate_only?: boolean;
    batch_size?: number;
  };
}

export interface BulkExportRequest {
  entity_type: 'users' | 'companies' | 'positions' | 'interviews' | 'audit_logs' | 'messages';
  filters?: Record<string, any>;
  format: 'csv' | 'excel' | 'json';
  include_deleted?: boolean;
  date_range?: {
    start_date: string;
    end_date: string;
  };
}

export interface BulkUpdateRequest {
  entity_type: string;
  entity_ids: number[];
  updates: Record<string, any>;
  options: {
    validate_before_update?: boolean;
    send_notifications?: boolean;
  };
}

export interface BulkDeleteRequest {
  entity_type: string;
  entity_ids: number[];
  options: {
    hard_delete?: boolean;
    cascade?: boolean;
    backup_before_delete?: boolean;
  };
}

export interface ImportValidationResult {
  valid_rows: number;
  invalid_rows: number;
  warnings: Array<{
    row: number;
    field: string;
    message: string;
    severity: 'warning' | 'error';
  }>;
  preview: Array<Record<string, any>>;
}

export interface DataMigrationJob {
  id: string;
  name: string;
  description: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress: number;
  log_entries: Array<{
    timestamp: string;
    level: 'info' | 'warning' | 'error';
    message: string;
  }>;
  created_at: string;
  started_at?: string;
  completed_at?: string;
}

// System Monitoring Types
export interface SystemHealth {
  overall_status: 'healthy' | 'warning' | 'critical';
  services: {
    database: ServiceStatus;
    redis: ServiceStatus;
    storage: ServiceStatus;
    email: ServiceStatus;
    antivirus?: ServiceStatus;
    external_apis: Record<string, ServiceStatus>;
  };
  system_metrics: {
    uptime: number;
    memory_usage: number;
    cpu_usage: number;
    disk_usage: number;
    active_connections: number;
  };
  last_check: string;
}

export interface ServiceStatus {
  status: 'healthy' | 'degraded' | 'down';
  response_time?: number;
  last_check: string;
  error_message?: string;
  metadata?: Record<string, any>;
}

export interface PerformanceMetrics {
  response_times: {
    average: number;
    p50: number;
    p95: number;
    p99: number;
  };
  request_rates: {
    current: number;
    average_1h: number;
    average_24h: number;
  };
  error_rates: {
    current: number;
    average_1h: number;
    average_24h: number;
  };
  database_metrics: {
    active_connections: number;
    query_time_avg: number;
    slow_queries_count: number;
  };
}

export interface SystemConfiguration {
  features: {
    two_factor_auth: boolean;
    file_virus_scanning: boolean;
    audit_logging: boolean;
    rate_limiting: boolean;
    email_notifications: boolean;
    real_time_updates: boolean;
  };
  limits: {
    max_file_size: number;
    max_files_per_user: number;
    session_timeout: number;
    max_login_attempts: number;
    password_min_length: number;
  };
  security: {
    require_https: boolean;
    strict_transport_security: boolean;
    content_security_policy: boolean;
    cors_origins: string[];
  };
}

export interface SystemAlert {
  id: number;
  type: 'info' | 'warning' | 'error' | 'critical';
  title: string;
  message: string;
  component: string;
  created_at: string;
  resolved_at?: string;
  resolved_by?: {
    id: number;
    full_name: string;
  };
}

export interface ResourceUsage {
  timestamp: string;
  memory_usage: number;
  cpu_usage: number;
  disk_usage: number;
  network_io: {
    bytes_in: number;
    bytes_out: number;
  };
  active_users: number;
  database_connections: number;
}
