# MiraiWorks Database Definition (DB定義書)

## Overview

MiraiWorks is a comprehensive HR management system with the following core modules:
- User & Company Management
- Position & Candidate Management
- Interview & Meeting Management
- Todo & Task Management
- Calendar Integration
- Video Call & Recording
- Resume Management
- Exam & Assessment System
- Notification System
- File Attachment System

## Database Technology Stack

- **Database Engine**: MySQL 8.0
- **ORM**: SQLAlchemy (Python)
- **Migration Tool**: Alembic
- **Character Set**: utf8mb4
- **Collation**: utf8mb4_unicode_ci

## Core Design Principles

1. **Soft Deletion**: Most entities support logical deletion with `is_deleted`, `deleted_at`, `deleted_by` fields
2. **Multi-tenancy**: Company-based data isolation using `company_id` foreign keys
3. **Audit Trail**: All entities have `created_at`, `updated_at` timestamps
4. **RBAC**: Role-based access control with `User`, `Role`, `UserRole` relationship
5. **Indexing**: Strategic indexes on foreign keys, status fields, and frequently queried columns

## Table Definitions

### 1. Core Authentication & User Management

#### users
**Purpose**: Core user entity with authentication and profile information

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique user identifier |
| company_id | INTEGER | FK(companies.id), INDEX, CASCADE DELETE | Company association |
| email | VARCHAR(255) | NOT NULL, UNIQUE, INDEX | User email (login) |
| hashed_password | VARCHAR(255) | NULL | Bcrypt hashed password (nullable for SSO) |
| first_name | VARCHAR(100) | NOT NULL | User first name |
| last_name | VARCHAR(100) | NOT NULL | User last name |
| phone | VARCHAR(50) | NULL | Contact phone number |
| is_active | BOOLEAN | NOT NULL, DEFAULT FALSE, INDEX | Account activation status |
| is_admin | BOOLEAN | NOT NULL, DEFAULT FALSE, INDEX | Admin privileges flag |
| require_2fa | BOOLEAN | NOT NULL, DEFAULT FALSE, INDEX | Two-factor auth requirement |
| last_login | DATETIME | NULL, TIMEZONE | Last successful login |
| is_deleted | BOOLEAN | NOT NULL, DEFAULT FALSE, INDEX | Soft deletion flag |
| deleted_at | DATETIME | NULL, TIMEZONE | Deletion timestamp |
| deleted_by | INTEGER | NULL | ID of deleting user |
| is_suspended | BOOLEAN | NOT NULL, DEFAULT FALSE, INDEX | Account suspension status |
| suspended_at | DATETIME | NULL, TIMEZONE | Suspension timestamp |
| suspended_by | INTEGER | NULL | ID of suspending user |
| created_at | DATETIME | NOT NULL, DEFAULT NOW(), TIMEZONE | Creation timestamp |
| updated_at | DATETIME | NOT NULL, DEFAULT NOW(), ON UPDATE NOW(), TIMEZONE | Last update timestamp |

**Relationships**:
- belongs_to Company
- has_many UserRole
- has_many RefreshToken
- has_many TwoFactorCode
- has_many UserSettings
- has_many Notification
- has_many TodoViewer
- has_many TodoAttachment

**Indexes**:
- PRIMARY: id
- UNIQUE: email
- INDEX: company_id, is_active, is_admin, require_2fa, is_deleted, is_suspended

#### companies
**Purpose**: Organization/tenant entity for multi-tenancy

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique company identifier |
| name | VARCHAR(255) | NOT NULL, INDEX | Company name |
| type | ENUM | NOT NULL, INDEX | CompanyType (RECRUITING_AGENCY, EMPLOYER) |
| email | VARCHAR(255) | NOT NULL, INDEX | Company contact email |
| phone | VARCHAR(50) | NOT NULL | Company phone number |
| website | VARCHAR(255) | NULL | Company website URL |
| postal_code | VARCHAR(10) | NULL | Postal code |
| prefecture | VARCHAR(50) | NULL | Prefecture/state |
| city | VARCHAR(100) | NULL | City |
| description | TEXT | NULL | Company description |
| is_active | VARCHAR(1) | NOT NULL, DEFAULT '1', INDEX | Active status ('1'/'0') |
| is_demo | BOOLEAN | NOT NULL, DEFAULT FALSE, INDEX | Demo account flag |
| demo_end_date | DATETIME | NULL, TIMEZONE | Demo expiration |
| demo_features | TEXT | NULL | Available demo features |
| demo_notes | TEXT | NULL | Demo-specific notes |
| is_deleted | BOOLEAN | NOT NULL, DEFAULT FALSE, INDEX | Soft deletion flag |
| deleted_at | DATETIME | NULL, TIMEZONE | Deletion timestamp |
| deleted_by | INTEGER | NULL | ID of deleting user |
| created_at | DATETIME | NOT NULL, DEFAULT NOW(), TIMEZONE | Creation timestamp |
| updated_at | DATETIME | NOT NULL, DEFAULT NOW(), ON UPDATE NOW(), TIMEZONE | Last update timestamp |

**Relationships**:
- has_many User
- has_many Position
- has_many Meeting

**Indexes**:
- PRIMARY: id
- INDEX: name, type, email, is_active, is_demo, is_deleted

#### roles
**Purpose**: System roles for RBAC

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique role identifier |
| name | VARCHAR(100) | NOT NULL, UNIQUE | Role name (ADMIN, RECRUITER, etc.) |
| description | TEXT | NULL | Role description |
| is_active | BOOLEAN | NOT NULL, DEFAULT TRUE | Role active status |
| created_at | DATETIME | NOT NULL, DEFAULT NOW(), TIMEZONE | Creation timestamp |
| updated_at | DATETIME | NOT NULL, DEFAULT NOW(), ON UPDATE NOW(), TIMEZONE | Last update timestamp |

**Relationships**:
- has_many UserRole

#### user_roles
**Purpose**: Many-to-many relationship between users and roles

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique assignment identifier |
| user_id | INTEGER | NOT NULL, FK(users.id), CASCADE DELETE | User reference |
| role_id | INTEGER | NOT NULL, FK(roles.id), CASCADE DELETE | Role reference |
| assigned_at | DATETIME | NOT NULL, DEFAULT NOW(), TIMEZONE | Assignment timestamp |
| assigned_by | INTEGER | NULL, FK(users.id) | Assigning user |

**Relationships**:
- belongs_to User
- belongs_to Role

**Constraints**:
- UNIQUE: (user_id, role_id)

### 2. Position & Candidate Management

#### positions
**Purpose**: Job positions/vacancies

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique position identifier |
| company_id | INTEGER | NOT NULL, FK(companies.id), CASCADE DELETE, INDEX | Company association |
| title | VARCHAR(255) | NOT NULL, INDEX | Position title |
| description | LONGTEXT | NULL | Position description |
| requirements | LONGTEXT | NULL | Position requirements |
| location | VARCHAR(255) | NULL | Work location |
| employment_type | VARCHAR(50) | NULL | Employment type |
| salary_range | VARCHAR(100) | NULL | Salary range |
| experience_level | VARCHAR(50) | NULL | Required experience level |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'draft', INDEX | Position status |
| posted_date | DATE | NULL | Publication date |
| application_deadline | DATE | NULL | Application deadline |
| is_remote | BOOLEAN | NOT NULL, DEFAULT FALSE | Remote work flag |
| benefits | TEXT | NULL | Benefits description |
| skills_required | TEXT | NULL | Required skills (JSON) |
| skills_preferred | TEXT | NULL | Preferred skills (JSON) |
| created_by | INTEGER | NOT NULL, FK(users.id) | Creating user |
| is_deleted | BOOLEAN | NOT NULL, DEFAULT FALSE, INDEX | Soft deletion flag |
| deleted_at | DATETIME | NULL, TIMEZONE | Deletion timestamp |
| deleted_by | INTEGER | NULL | ID of deleting user |
| created_at | DATETIME | NOT NULL, DEFAULT NOW(), TIMEZONE | Creation timestamp |
| updated_at | DATETIME | NOT NULL, DEFAULT NOW(), ON UPDATE NOW(), TIMEZONE | Last update timestamp |

**Relationships**:
- belongs_to Company
- belongs_to User (creator)
- has_many Interview

**Indexes**:
- PRIMARY: id
- INDEX: company_id, title, status, is_deleted

### 3. Interview & Meeting System

#### interviews
**Purpose**: Interview scheduling and management

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique interview identifier |
| position_id | INTEGER | NULL, FK(positions.id), SET NULL | Associated position |
| candidate_id | INTEGER | NULL, FK(users.id), SET NULL | Candidate user |
| recruiter_id | INTEGER | NULL, FK(users.id), SET NULL | Recruiter user |
| title | VARCHAR(255) | NOT NULL | Interview title |
| description | TEXT | NULL | Interview description |
| scheduled_start | DATETIME | NULL, TIMEZONE | Scheduled start time |
| scheduled_end | DATETIME | NULL, TIMEZONE | Scheduled end time |
| actual_start | DATETIME | NULL, TIMEZONE | Actual start time |
| actual_end | DATETIME | NULL, TIMEZONE | Actual end time |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'pending_schedule', INDEX | Interview status |
| interview_type | VARCHAR(20) | NOT NULL, DEFAULT 'online' | Interview type |
| location | VARCHAR(255) | NULL | Interview location |
| meeting_url | VARCHAR(500) | NULL | Online meeting URL |
| timezone | VARCHAR(50) | NULL, DEFAULT 'Asia/Tokyo' | Timezone |
| duration_minutes | INTEGER | NULL, DEFAULT 60 | Planned duration |
| notes | TEXT | NULL | Interview notes |
| feedback | TEXT | NULL | Interview feedback |
| rating | INTEGER | NULL | Interview rating (1-5) |
| decision | VARCHAR(20) | NULL | Interview decision |
| company_id | INTEGER | NOT NULL, FK(companies.id), CASCADE DELETE, INDEX | Company association |
| created_by | INTEGER | NOT NULL, FK(users.id) | Creating user |
| is_deleted | BOOLEAN | NOT NULL, DEFAULT FALSE, INDEX | Soft deletion flag |
| deleted_at | DATETIME | NULL, TIMEZONE | Deletion timestamp |
| deleted_by | INTEGER | NULL | ID of deleting user |
| created_at | DATETIME | NOT NULL, DEFAULT NOW(), TIMEZONE | Creation timestamp |
| updated_at | DATETIME | NOT NULL, DEFAULT NOW(), ON UPDATE NOW(), TIMEZONE | Last update timestamp |

**Relationships**:
- belongs_to Position
- belongs_to User (candidate)
- belongs_to User (recruiter)
- belongs_to Company
- belongs_to User (creator)
- has_many Meeting
- has_many InterviewNote

**Indexes**:
- PRIMARY: id
- INDEX: position_id, candidate_id, recruiter_id, company_id, status, scheduled_start, is_deleted

#### meetings
**Purpose**: Video conference meetings for interviews

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique meeting identifier |
| interview_id | INTEGER | NULL, FK(interviews.id), SET NULL | Associated interview |
| title | VARCHAR(255) | NOT NULL | Meeting title |
| description | TEXT | NULL | Meeting description |
| meeting_type | VARCHAR(20) | NOT NULL | Meeting type |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'scheduled' | Meeting status |
| scheduled_start | DATETIME | NOT NULL, TIMEZONE | Scheduled start time |
| scheduled_end | DATETIME | NOT NULL, TIMEZONE | Scheduled end time |
| actual_start | DATETIME | NULL, TIMEZONE | Actual start time |
| actual_end | DATETIME | NULL, TIMEZONE | Actual end time |
| room_id | VARCHAR(255) | NOT NULL, UNIQUE | WebRTC room identifier |
| access_code | VARCHAR(50) | NULL | Meeting PIN code |
| recording_enabled | BOOLEAN | NOT NULL, DEFAULT FALSE | Recording enabled flag |
| recording_status | VARCHAR(20) | NOT NULL, DEFAULT 'not_started' | Recording status |
| recording_consent_required | BOOLEAN | NOT NULL, DEFAULT TRUE | Consent requirement |
| transcription_enabled | BOOLEAN | NOT NULL, DEFAULT FALSE | Transcription enabled |
| auto_summary | BOOLEAN | NOT NULL, DEFAULT FALSE | Auto-summary enabled |
| company_id | INTEGER | NOT NULL, FK(companies.id), CASCADE DELETE | Company association |
| created_by | INTEGER | NOT NULL, FK(users.id) | Creating user |
| created_at | DATETIME | NOT NULL, DEFAULT NOW(), TIMEZONE | Creation timestamp |
| updated_at | DATETIME | NOT NULL, DEFAULT NOW(), ON UPDATE NOW(), TIMEZONE | Last update timestamp |

**Relationships**:
- belongs_to Interview
- belongs_to Company
- belongs_to User (creator)
- has_many_through meeting_participants (User)
- has_many MeetingRecording
- has_many MeetingTranscript
- has_many MeetingSummary

**Indexes**:
- PRIMARY: id
- UNIQUE: room_id
- INDEX: interview_id, company_id, status, scheduled_start

#### meeting_participants
**Purpose**: Meeting participants with roles and permissions

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique participant identifier |
| meeting_id | INTEGER | NOT NULL, FK(meetings.id), CASCADE DELETE | Meeting reference |
| user_id | INTEGER | NOT NULL, FK(users.id), CASCADE DELETE | User reference |
| role | VARCHAR(20) | NOT NULL | Participant role |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'invited' | Participation status |
| joined_at | DATETIME | NULL, TIMEZONE | Join timestamp |
| left_at | DATETIME | NULL, TIMEZONE | Leave timestamp |
| can_record | BOOLEAN | NOT NULL, DEFAULT FALSE | Recording permission |
| recording_consent | BOOLEAN | NULL | Recording consent (TRUE/FALSE/NULL) |
| created_at | DATETIME | NOT NULL, DEFAULT NOW(), TIMEZONE | Creation timestamp |
| updated_at | DATETIME | NOT NULL, DEFAULT NOW(), ON UPDATE NOW(), TIMEZONE | Last update timestamp |

**Relationships**:
- belongs_to Meeting
- belongs_to User

**Constraints**:
- UNIQUE: (meeting_id, user_id)

**Indexes**:
- PRIMARY: id
- INDEX: meeting_id, user_id

### 4. Todo & Task Management

#### todos
**Purpose**: Task and todo item management

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique todo identifier |
| title | VARCHAR(255) | NOT NULL, INDEX | Todo title |
| description | TEXT | NULL | Todo description |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'pending', INDEX | Todo status |
| priority | VARCHAR(10) | NOT NULL, DEFAULT 'medium', INDEX | Priority level |
| due_date | DATETIME | NULL, TIMEZONE, INDEX | Due date |
| assigned_user_id | INTEGER | NULL, FK(users.id), SET NULL, INDEX | Assigned user |
| created_by | INTEGER | NOT NULL, FK(users.id) | Creating user |
| completed_at | DATETIME | NULL, TIMEZONE | Completion timestamp |
| completed_by | INTEGER | NULL, FK(users.id) | Completing user |
| category | VARCHAR(50) | NULL, INDEX | Todo category |
| tags | TEXT | NULL | Tags (JSON array) |
| estimated_hours | DECIMAL(5,2) | NULL | Estimated effort hours |
| actual_hours | DECIMAL(5,2) | NULL | Actual effort hours |
| visibility | VARCHAR(20) | NOT NULL, DEFAULT 'private' | Visibility setting |
| company_id | INTEGER | NOT NULL, FK(companies.id), CASCADE DELETE, INDEX | Company association |
| is_deleted | BOOLEAN | NOT NULL, DEFAULT FALSE, INDEX | Soft deletion flag |
| deleted_at | DATETIME | NULL, TIMEZONE | Deletion timestamp |
| deleted_by | INTEGER | NULL | ID of deleting user |
| created_at | DATETIME | NOT NULL, DEFAULT NOW(), TIMEZONE | Creation timestamp |
| updated_at | DATETIME | NOT NULL, DEFAULT NOW(), ON UPDATE NOW(), TIMEZONE | Last update timestamp |

**Relationships**:
- belongs_to User (assigned_user)
- belongs_to User (created_by)
- belongs_to User (completed_by)
- belongs_to Company
- has_many TodoViewer
- has_many TodoAttachment
- has_many TodoExtensionRequest

**Indexes**:
- PRIMARY: id
- INDEX: title, status, priority, due_date, assigned_user_id, category, company_id, is_deleted

#### todo_viewers
**Purpose**: Access control for todo items

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique viewer assignment identifier |
| todo_id | INTEGER | NOT NULL, FK(todos.id), CASCADE DELETE | Todo reference |
| user_id | INTEGER | NOT NULL, FK(users.id), CASCADE DELETE | User reference |
| permission | VARCHAR(20) | NOT NULL, DEFAULT 'read' | Permission level |
| added_by | INTEGER | NOT NULL, FK(users.id) | User who granted access |
| added_at | DATETIME | NOT NULL, DEFAULT NOW(), TIMEZONE | Access grant timestamp |

**Relationships**:
- belongs_to Todo
- belongs_to User
- belongs_to User (added_by)

**Constraints**:
- UNIQUE: (todo_id, user_id)

#### todo_attachments
**Purpose**: File attachments for todo items

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique attachment identifier |
| todo_id | INTEGER | NOT NULL, FK(todos.id), CASCADE DELETE | Todo reference |
| filename | VARCHAR(255) | NOT NULL | Original filename |
| stored_filename | VARCHAR(255) | NOT NULL, UNIQUE | Stored filename |
| file_path | VARCHAR(500) | NOT NULL | File storage path |
| file_size | INTEGER | NOT NULL | File size in bytes |
| mime_type | VARCHAR(100) | NOT NULL | MIME type |
| description | TEXT | NULL | Attachment description |
| uploaded_by | INTEGER | NOT NULL, FK(users.id) | Uploading user |
| is_deleted | BOOLEAN | NOT NULL, DEFAULT FALSE | Soft deletion flag |
| deleted_at | DATETIME | NULL, TIMEZONE | Deletion timestamp |
| deleted_by | INTEGER | NULL | ID of deleting user |
| created_at | DATETIME | NOT NULL, DEFAULT NOW(), TIMEZONE | Creation timestamp |
| updated_at | DATETIME | NOT NULL, DEFAULT NOW(), ON UPDATE NOW(), TIMEZONE | Last update timestamp |

**Relationships**:
- belongs_to Todo
- belongs_to User (uploaded_by)

**Indexes**:
- PRIMARY: id
- UNIQUE: stored_filename
- INDEX: todo_id, uploaded_by, is_deleted

#### todo_extension_requests
**Purpose**: Deadline extension requests for todos

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique request identifier |
| todo_id | INTEGER | NOT NULL, FK(todos.id), CASCADE DELETE | Todo reference |
| requested_by | INTEGER | NOT NULL, FK(users.id) | Requesting user |
| original_due_date | DATETIME | NULL, TIMEZONE | Original due date |
| requested_due_date | DATETIME | NOT NULL, TIMEZONE | Requested new due date |
| reason | TEXT | NOT NULL | Extension reason |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'pending' | Request status |
| reviewed_by | INTEGER | NULL, FK(users.id) | Reviewing user |
| reviewed_at | DATETIME | NULL, TIMEZONE | Review timestamp |
| review_notes | TEXT | NULL | Review notes |
| approved_due_date | DATETIME | NULL, TIMEZONE | Approved due date |
| created_at | DATETIME | NOT NULL, DEFAULT NOW(), TIMEZONE | Creation timestamp |
| updated_at | DATETIME | NOT NULL, DEFAULT NOW(), ON UPDATE NOW(), TIMEZONE | Last update timestamp |

**Relationships**:
- belongs_to Todo
- belongs_to User (requested_by)
- belongs_to User (reviewed_by)

**Indexes**:
- PRIMARY: id
- INDEX: todo_id, requested_by, status

### 5. Calendar Integration

#### calendar_connections
**Purpose**: External calendar service connections

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique connection identifier |
| user_id | INTEGER | NOT NULL, FK(users.id), CASCADE DELETE | User reference |
| provider | VARCHAR(20) | NOT NULL | Provider (google, outlook) |
| external_account_id | VARCHAR(255) | NOT NULL | External account ID |
| external_account_email | VARCHAR(255) | NOT NULL | External account email |
| display_name | VARCHAR(255) | NULL | Display name |
| access_token | TEXT | NOT NULL | Encrypted access token |
| refresh_token | TEXT | NULL | Encrypted refresh token |
| token_expires_at | DATETIME | NULL, TIMEZONE | Token expiration |
| is_active | BOOLEAN | NOT NULL, DEFAULT TRUE | Connection active status |
| last_sync | DATETIME | NULL, TIMEZONE | Last sync timestamp |
| sync_enabled | BOOLEAN | NOT NULL, DEFAULT TRUE | Sync enabled flag |
| created_at | DATETIME | NOT NULL, DEFAULT NOW(), TIMEZONE | Creation timestamp |
| updated_at | DATETIME | NOT NULL, DEFAULT NOW(), ON UPDATE NOW(), TIMEZONE | Last update timestamp |

**Relationships**:
- belongs_to User
- has_many CalendarIntegration

**Constraints**:
- UNIQUE: (user_id, provider, external_account_id)

**Indexes**:
- PRIMARY: id
- INDEX: user_id, provider, is_active

#### calendar_integrations
**Purpose**: Synchronized calendar events

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique integration identifier |
| connection_id | INTEGER | NOT NULL, FK(calendar_connections.id), CASCADE DELETE | Connection reference |
| external_event_id | VARCHAR(255) | NOT NULL | External event ID |
| title | VARCHAR(255) | NOT NULL | Event title |
| description | TEXT | NULL | Event description |
| start_datetime | DATETIME | NOT NULL, TIMEZONE | Start date/time |
| end_datetime | DATETIME | NOT NULL, TIMEZONE | End date/time |
| timezone | VARCHAR(50) | NULL | Event timezone |
| location | VARCHAR(255) | NULL | Event location |
| is_all_day | BOOLEAN | NOT NULL, DEFAULT FALSE | All-day event flag |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'confirmed' | Event status |
| organizer_email | VARCHAR(255) | NULL | Organizer email |
| attendees | TEXT | NULL | Attendees (JSON) |
| meeting_url | VARCHAR(500) | NULL | Meeting URL |
| is_recurring | BOOLEAN | NOT NULL, DEFAULT FALSE | Recurring event flag |
| recurrence_rule | TEXT | NULL | Recurrence rule |
| sync_status | VARCHAR(20) | NOT NULL, DEFAULT 'synced' | Sync status |
| last_modified | DATETIME | NULL, TIMEZONE | Last modification in external calendar |
| created_at | DATETIME | NOT NULL, DEFAULT NOW(), TIMEZONE | Creation timestamp |
| updated_at | DATETIME | NOT NULL, DEFAULT NOW(), ON UPDATE NOW(), TIMEZONE | Last update timestamp |

**Relationships**:
- belongs_to CalendarConnection

**Constraints**:
- UNIQUE: (connection_id, external_event_id)

**Indexes**:
- PRIMARY: id
- INDEX: connection_id, start_datetime, end_datetime, sync_status

### 6. File & Attachment System

#### attachments
**Purpose**: General file attachment system

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique attachment identifier |
| entity_type | VARCHAR(50) | NOT NULL, INDEX | Entity type (resume, interview, etc.) |
| entity_id | INTEGER | NOT NULL, INDEX | Entity ID |
| filename | VARCHAR(255) | NOT NULL | Original filename |
| stored_filename | VARCHAR(255) | NOT NULL, UNIQUE | Stored filename |
| file_path | VARCHAR(500) | NOT NULL | File storage path |
| file_size | INTEGER | NOT NULL | File size in bytes |
| mime_type | VARCHAR(100) | NOT NULL | MIME type |
| file_hash | VARCHAR(64) | NULL | File hash for deduplication |
| description | TEXT | NULL | Attachment description |
| upload_status | VARCHAR(20) | NOT NULL, DEFAULT 'completed' | Upload status |
| uploaded_by | INTEGER | NOT NULL, FK(users.id) | Uploading user |
| company_id | INTEGER | NOT NULL, FK(companies.id), CASCADE DELETE | Company association |
| is_deleted | BOOLEAN | NOT NULL, DEFAULT FALSE | Soft deletion flag |
| deleted_at | DATETIME | NULL, TIMEZONE | Deletion timestamp |
| deleted_by | INTEGER | NULL | ID of deleting user |
| created_at | DATETIME | NOT NULL, DEFAULT NOW(), TIMEZONE | Creation timestamp |
| updated_at | DATETIME | NOT NULL, DEFAULT NOW(), ON UPDATE NOW(), TIMEZONE | Last update timestamp |

**Relationships**:
- belongs_to User (uploaded_by)
- belongs_to Company

**Indexes**:
- PRIMARY: id
- UNIQUE: stored_filename
- INDEX: entity_type, entity_id, uploaded_by, company_id, is_deleted

### 7. Resume Management

#### resumes
**Purpose**: Resume/CV management system

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique resume identifier |
| user_id | INTEGER | NOT NULL, FK(users.id), CASCADE DELETE | Owner user |
| title | VARCHAR(255) | NOT NULL | Resume title |
| template_id | INTEGER | NULL | Template identifier |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'draft' | Resume status |
| visibility | VARCHAR(20) | NOT NULL, DEFAULT 'private' | Visibility setting |
| content | LONGTEXT | NULL | Resume content (JSON) |
| summary | TEXT | NULL | Professional summary |
| skills | TEXT | NULL | Skills list (JSON) |
| languages | TEXT | NULL | Languages (JSON) |
| certifications | TEXT | NULL | Certifications (JSON) |
| education | TEXT | NULL | Education history (JSON) |
| experience | TEXT | NULL | Work experience (JSON) |
| projects | TEXT | NULL | Projects (JSON) |
| references | TEXT | NULL | References (JSON) |
| is_public | BOOLEAN | NOT NULL, DEFAULT FALSE | Public visibility flag |
| public_slug | VARCHAR(100) | NULL, UNIQUE | Public access slug |
| download_count | INTEGER | NOT NULL, DEFAULT 0 | Download counter |
| view_count | INTEGER | NOT NULL, DEFAULT 0 | View counter |
| company_id | INTEGER | NOT NULL, FK(companies.id), CASCADE DELETE | Company association |
| is_deleted | BOOLEAN | NOT NULL, DEFAULT FALSE | Soft deletion flag |
| deleted_at | DATETIME | NULL, TIMEZONE | Deletion timestamp |
| deleted_by | INTEGER | NULL | ID of deleting user |
| created_at | DATETIME | NOT NULL, DEFAULT NOW(), TIMEZONE | Creation timestamp |
| updated_at | DATETIME | NOT NULL, DEFAULT NOW(), ON UPDATE NOW(), TIMEZONE | Last update timestamp |

**Relationships**:
- belongs_to User
- belongs_to Company

**Indexes**:
- PRIMARY: id
- UNIQUE: public_slug
- INDEX: user_id, company_id, status, visibility, is_public, is_deleted

### 8. Exam & Assessment System

#### exams
**Purpose**: Assessment and examination system

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique exam identifier |
| title | VARCHAR(255) | NOT NULL, INDEX | Exam title |
| description | TEXT | NULL | Exam description |
| instructions | TEXT | NULL | Exam instructions |
| category | VARCHAR(50) | NULL, INDEX | Exam category |
| difficulty | VARCHAR(20) | NOT NULL, DEFAULT 'medium' | Difficulty level |
| duration_minutes | INTEGER | NOT NULL, DEFAULT 60 | Time limit in minutes |
| total_questions | INTEGER | NOT NULL, DEFAULT 0 | Total question count |
| passing_score | INTEGER | NOT NULL, DEFAULT 70 | Passing score percentage |
| max_attempts | INTEGER | NOT NULL, DEFAULT 1 | Maximum attempts allowed |
| is_randomized | BOOLEAN | NOT NULL, DEFAULT FALSE | Question randomization |
| show_results | BOOLEAN | NOT NULL, DEFAULT TRUE | Show results to candidate |
| show_correct_answers | BOOLEAN | NOT NULL, DEFAULT FALSE | Show correct answers |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'draft', INDEX | Exam status |
| questions | LONGTEXT | NOT NULL | Questions data (JSON) |
| settings | TEXT | NULL | Exam settings (JSON) |
| company_id | INTEGER | NOT NULL, FK(companies.id), CASCADE DELETE | Company association |
| created_by | INTEGER | NOT NULL, FK(users.id) | Creating user |
| is_deleted | BOOLEAN | NOT NULL, DEFAULT FALSE | Soft deletion flag |
| deleted_at | DATETIME | NULL, TIMEZONE | Deletion timestamp |
| deleted_by | INTEGER | NULL | ID of deleting user |
| created_at | DATETIME | NOT NULL, DEFAULT NOW(), TIMEZONE | Creation timestamp |
| updated_at | DATETIME | NOT NULL, DEFAULT NOW(), ON UPDATE NOW(), TIMEZONE | Last update timestamp |

**Relationships**:
- belongs_to Company
- belongs_to User (created_by)
- has_many ExamSession

**Indexes**:
- PRIMARY: id
- INDEX: title, category, status, company_id, is_deleted

#### exam_sessions
**Purpose**: Individual exam attempt sessions

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique session identifier |
| exam_id | INTEGER | NOT NULL, FK(exams.id), CASCADE DELETE | Exam reference |
| candidate_id | INTEGER | NOT NULL, FK(users.id), CASCADE DELETE | Candidate user |
| session_token | VARCHAR(255) | NOT NULL, UNIQUE | Unique session token |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'not_started' | Session status |
| started_at | DATETIME | NULL, TIMEZONE | Start timestamp |
| submitted_at | DATETIME | NULL, TIMEZONE | Submission timestamp |
| time_remaining | INTEGER | NULL | Remaining time in seconds |
| current_question | INTEGER | NOT NULL, DEFAULT 0 | Current question index |
| answers | LONGTEXT | NULL | Candidate answers (JSON) |
| score | INTEGER | NULL | Final score |
| passed | BOOLEAN | NULL | Pass/fail result |
| feedback | TEXT | NULL | Examiner feedback |
| ip_address | VARCHAR(45) | NULL | Client IP address |
| user_agent | TEXT | NULL | Client user agent |
| browser_info | TEXT | NULL | Browser information (JSON) |
| attempt_number | INTEGER | NOT NULL, DEFAULT 1 | Attempt number |
| proctoring_enabled | BOOLEAN | NOT NULL, DEFAULT FALSE | Proctoring enabled |
| proctoring_data | TEXT | NULL | Proctoring data (JSON) |
| violations | TEXT | NULL | Detected violations (JSON) |
| company_id | INTEGER | NOT NULL, FK(companies.id), CASCADE DELETE | Company association |
| created_at | DATETIME | NOT NULL, DEFAULT NOW(), TIMEZONE | Creation timestamp |
| updated_at | DATETIME | NOT NULL, DEFAULT NOW(), ON UPDATE NOW(), TIMEZONE | Last update timestamp |

**Relationships**:
- belongs_to Exam
- belongs_to User (candidate)
- belongs_to Company

**Indexes**:
- PRIMARY: id
- UNIQUE: session_token
- INDEX: exam_id, candidate_id, status, company_id

### 9. MBTI Personality Assessment

#### mbti_test_sessions
**Purpose**: MBTI personality test sessions

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique session identifier |
| user_id | INTEGER | NOT NULL, FK(users.id), CASCADE DELETE | Test taker |
| session_token | VARCHAR(255) | NOT NULL, UNIQUE | Unique session token |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'in_progress' | Session status |
| current_question | INTEGER | NOT NULL, DEFAULT 1 | Current question number |
| answers | TEXT | NULL | User answers (JSON) |
| e_score | INTEGER | NOT NULL, DEFAULT 0 | Extraversion score |
| i_score | INTEGER | NOT NULL, DEFAULT 0 | Introversion score |
| s_score | INTEGER | NOT NULL, DEFAULT 0 | Sensing score |
| n_score | INTEGER | NOT NULL, DEFAULT 0 | Intuition score |
| t_score | INTEGER | NOT NULL, DEFAULT 0 | Thinking score |
| f_score | INTEGER | NOT NULL, DEFAULT 0 | Feeling score |
| j_score | INTEGER | NOT NULL, DEFAULT 0 | Judging score |
| p_score | INTEGER | NOT NULL, DEFAULT 0 | Perceiving score |
| result_type | VARCHAR(4) | NULL | MBTI type result |
| started_at | DATETIME | NOT NULL, DEFAULT NOW(), TIMEZONE | Start timestamp |
| completed_at | DATETIME | NULL, TIMEZONE | Completion timestamp |
| company_id | INTEGER | NOT NULL, FK(companies.id), CASCADE DELETE | Company association |
| created_at | DATETIME | NOT NULL, DEFAULT NOW(), TIMEZONE | Creation timestamp |
| updated_at | DATETIME | NOT NULL, DEFAULT NOW(), ON UPDATE NOW(), TIMEZONE | Last update timestamp |

**Relationships**:
- belongs_to User
- belongs_to Company

**Indexes**:
- PRIMARY: id
- UNIQUE: session_token
- INDEX: user_id, status, result_type, company_id

### 10. Notification System

#### notifications
**Purpose**: System notifications and alerts

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique notification identifier |
| user_id | INTEGER | NOT NULL, FK(users.id), CASCADE DELETE | Target user |
| type | VARCHAR(50) | NOT NULL, INDEX | Notification type |
| title | VARCHAR(255) | NOT NULL | Notification title |
| message | TEXT | NOT NULL | Notification message |
| data | TEXT | NULL | Additional data (JSON) |
| is_read | BOOLEAN | NOT NULL, DEFAULT FALSE, INDEX | Read status |
| read_at | DATETIME | NULL, TIMEZONE | Read timestamp |
| priority | VARCHAR(10) | NOT NULL, DEFAULT 'normal' | Priority level |
| category | VARCHAR(50) | NULL, INDEX | Notification category |
| action_url | VARCHAR(500) | NULL | Action URL |
| expires_at | DATETIME | NULL, TIMEZONE | Expiration timestamp |
| created_at | DATETIME | NOT NULL, DEFAULT NOW(), TIMEZONE | Creation timestamp |
| updated_at | DATETIME | NOT NULL, DEFAULT NOW(), ON UPDATE NOW(), TIMEZONE | Last update timestamp |

**Relationships**:
- belongs_to User

**Indexes**:
- PRIMARY: id
- INDEX: user_id, type, is_read, category, created_at

### 11. Authentication Support

#### refresh_tokens
**Purpose**: JWT refresh token management

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique token identifier |
| user_id | INTEGER | NOT NULL, FK(users.id), CASCADE DELETE | Token owner |
| token | VARCHAR(255) | NOT NULL, UNIQUE | Refresh token |
| expires_at | DATETIME | NOT NULL, TIMEZONE | Token expiration |
| is_active | BOOLEAN | NOT NULL, DEFAULT TRUE | Token active status |
| created_at | DATETIME | NOT NULL, DEFAULT NOW(), TIMEZONE | Creation timestamp |
| updated_at | DATETIME | NOT NULL, DEFAULT NOW(), ON UPDATE NOW(), TIMEZONE | Last update timestamp |

**Relationships**:
- belongs_to User

**Indexes**:
- PRIMARY: id
- UNIQUE: token
- INDEX: user_id, expires_at, is_active

#### two_factor_codes
**Purpose**: Two-factor authentication codes

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique code identifier |
| user_id | INTEGER | NOT NULL, FK(users.id), CASCADE DELETE | User reference |
| code | VARCHAR(10) | NOT NULL | 2FA code |
| method | VARCHAR(20) | NOT NULL | Delivery method (email, sms) |
| expires_at | DATETIME | NOT NULL, TIMEZONE | Code expiration |
| is_used | BOOLEAN | NOT NULL, DEFAULT FALSE | Usage status |
| used_at | DATETIME | NULL, TIMEZONE | Usage timestamp |
| attempts | INTEGER | NOT NULL, DEFAULT 0 | Verification attempts |
| created_at | DATETIME | NOT NULL, DEFAULT NOW(), TIMEZONE | Creation timestamp |

**Relationships**:
- belongs_to User

**Indexes**:
- PRIMARY: id
- INDEX: user_id, code, expires_at, is_used

### 12. User Settings

#### user_settings
**Purpose**: User-specific configuration settings

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique setting identifier |
| user_id | INTEGER | NOT NULL, FK(users.id), CASCADE DELETE | User reference |
| setting_key | VARCHAR(100) | NOT NULL | Setting key name |
| setting_value | TEXT | NULL | Setting value (JSON) |
| data_type | VARCHAR(20) | NOT NULL, DEFAULT 'string' | Value data type |
| is_encrypted | BOOLEAN | NOT NULL, DEFAULT FALSE | Encryption flag |
| category | VARCHAR(50) | NULL | Setting category |
| description | TEXT | NULL | Setting description |
| created_at | DATETIME | NOT NULL, DEFAULT NOW(), TIMEZONE | Creation timestamp |
| updated_at | DATETIME | NOT NULL, DEFAULT NOW(), ON UPDATE NOW(), TIMEZONE | Last update timestamp |

**Relationships**:
- belongs_to User

**Constraints**:
- UNIQUE: (user_id, setting_key)

**Indexes**:
- PRIMARY: id
- INDEX: user_id, setting_key, category

### 13. Video Call Management

#### video_calls
**Purpose**: Video call session management

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique call identifier |
| room_code | VARCHAR(50) | NOT NULL, UNIQUE | Room access code |
| title | VARCHAR(255) | NOT NULL | Call title |
| description | TEXT | NULL | Call description |
| host_id | INTEGER | NOT NULL, FK(users.id) | Host user |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'scheduled' | Call status |
| scheduled_start | DATETIME | NOT NULL, TIMEZONE | Scheduled start time |
| scheduled_end | DATETIME | NOT NULL, TIMEZONE | Scheduled end time |
| actual_start | DATETIME | NULL, TIMEZONE | Actual start time |
| actual_end | DATETIME | NULL, TIMEZONE | Actual end time |
| max_participants | INTEGER | NOT NULL, DEFAULT 10 | Maximum participants |
| recording_enabled | BOOLEAN | NOT NULL, DEFAULT FALSE | Recording enabled |
| password_required | BOOLEAN | NOT NULL, DEFAULT FALSE | Password requirement |
| room_password | VARCHAR(100) | NULL | Room password |
| waiting_room | BOOLEAN | NOT NULL, DEFAULT FALSE | Waiting room enabled |
| settings | TEXT | NULL | Call settings (JSON) |
| company_id | INTEGER | NOT NULL, FK(companies.id), CASCADE DELETE | Company association |
| created_at | DATETIME | NOT NULL, DEFAULT NOW(), TIMEZONE | Creation timestamp |
| updated_at | DATETIME | NOT NULL, DEFAULT NOW(), ON UPDATE NOW(), TIMEZONE | Last update timestamp |

**Relationships**:
- belongs_to User (host)
- belongs_to Company
- has_many VideoCallParticipant

**Indexes**:
- PRIMARY: id
- UNIQUE: room_code
- INDEX: host_id, status, company_id, scheduled_start

#### video_call_participants
**Purpose**: Video call participants tracking

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique participant identifier |
| video_call_id | INTEGER | NOT NULL, FK(video_calls.id), CASCADE DELETE | Call reference |
| user_id | INTEGER | NULL, FK(users.id), SET NULL | User reference |
| display_name | VARCHAR(100) | NOT NULL | Display name |
| role | VARCHAR(20) | NOT NULL, DEFAULT 'participant' | Participant role |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'invited' | Participation status |
| joined_at | DATETIME | NULL, TIMEZONE | Join timestamp |
| left_at | DATETIME | NULL, TIMEZONE | Leave timestamp |
| duration_minutes | INTEGER | NULL | Participation duration |
| is_muted | BOOLEAN | NOT NULL, DEFAULT FALSE | Mute status |
| is_video_enabled | BOOLEAN | NOT NULL, DEFAULT TRUE | Video status |
| connection_quality | VARCHAR(20) | NULL | Connection quality |
| created_at | DATETIME | NOT NULL, DEFAULT NOW(), TIMEZONE | Creation timestamp |
| updated_at | DATETIME | NOT NULL, DEFAULT NOW(), ON UPDATE NOW(), TIMEZONE | Last update timestamp |

**Relationships**:
- belongs_to VideoCall
- belongs_to User

**Indexes**:
- PRIMARY: id
- INDEX: video_call_id, user_id, status

### 14. Message System

#### messages
**Purpose**: Internal messaging system

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique message identifier |
| sender_id | INTEGER | NOT NULL, FK(users.id) | Sender user |
| recipient_id | INTEGER | NOT NULL, FK(users.id) | Recipient user |
| subject | VARCHAR(255) | NULL | Message subject |
| content | TEXT | NOT NULL | Message content |
| message_type | VARCHAR(20) | NOT NULL, DEFAULT 'direct' | Message type |
| priority | VARCHAR(10) | NOT NULL, DEFAULT 'normal' | Message priority |
| is_read | BOOLEAN | NOT NULL, DEFAULT FALSE | Read status |
| read_at | DATETIME | NULL, TIMEZONE | Read timestamp |
| parent_message_id | INTEGER | NULL, FK(messages.id) | Reply parent |
| thread_id | VARCHAR(50) | NULL, INDEX | Conversation thread |
| attachments | TEXT | NULL | Attachment references (JSON) |
| metadata | TEXT | NULL | Additional metadata (JSON) |
| company_id | INTEGER | NOT NULL, FK(companies.id), CASCADE DELETE | Company association |
| is_deleted | BOOLEAN | NOT NULL, DEFAULT FALSE | Soft deletion flag |
| deleted_at | DATETIME | NULL, TIMEZONE | Deletion timestamp |
| deleted_by | INTEGER | NULL | ID of deleting user |
| created_at | DATETIME | NOT NULL, DEFAULT NOW(), TIMEZONE | Creation timestamp |
| updated_at | DATETIME | NOT NULL, DEFAULT NOW(), ON UPDATE NOW(), TIMEZONE | Last update timestamp |

**Relationships**:
- belongs_to User (sender)
- belongs_to User (recipient)
- belongs_to Message (parent)
- belongs_to Company

**Indexes**:
- PRIMARY: id
- INDEX: sender_id, recipient_id, thread_id, is_read, company_id, is_deleted

### 15. Audit & Logging

#### audit_logs
**Purpose**: System audit trail

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique log identifier |
| user_id | INTEGER | NULL, FK(users.id), SET NULL | Acting user |
| action | VARCHAR(50) | NOT NULL, INDEX | Action performed |
| entity_type | VARCHAR(50) | NOT NULL, INDEX | Target entity type |
| entity_id | INTEGER | NULL | Target entity ID |
| old_values | TEXT | NULL | Previous values (JSON) |
| new_values | TEXT | NULL | New values (JSON) |
| ip_address | VARCHAR(45) | NULL | Client IP address |
| user_agent | TEXT | NULL | Client user agent |
| session_id | VARCHAR(255) | NULL | Session identifier |
| company_id | INTEGER | NULL, FK(companies.id), CASCADE DELETE | Company context |
| metadata | TEXT | NULL | Additional metadata (JSON) |
| created_at | DATETIME | NOT NULL, DEFAULT NOW(), TIMEZONE | Action timestamp |

**Relationships**:
- belongs_to User
- belongs_to Company

**Indexes**:
- PRIMARY: id
- INDEX: user_id, action, entity_type, company_id, created_at

## Relationships Summary

### Primary Relationships

1. **Company → Users**: One-to-many (company_id)
2. **User → UserRoles → Roles**: Many-to-many through user_roles
3. **Company → Positions**: One-to-many (company_id)
4. **Position → Interviews**: One-to-many (position_id)
5. **User → Interviews**: Many-to-many (candidate_id, recruiter_id)
6. **Interview → Meetings**: One-to-many (interview_id)
7. **Meeting → Users**: Many-to-many through meeting_participants
8. **User → Todos**: Many-to-many (assigned_user_id, created_by)
9. **Todo → Users**: Many-to-many through todo_viewers
10. **Todo → Attachments**: One-to-many (todo_id)
11. **User → CalendarConnections**: One-to-many (user_id)
12. **CalendarConnection → CalendarIntegrations**: One-to-many (connection_id)

### Cascade Rules

- **CASCADE DELETE**: When parent is deleted, children are automatically deleted
  - Company deletion removes all associated users, positions, meetings, etc.
  - User deletion removes their roles, tokens, settings, etc.
  - Todo deletion removes viewers and attachments

- **SET NULL**: When parent is deleted, foreign key is set to NULL
  - Interview deletion doesn't remove associated meetings
  - Position deletion doesn't remove associated interviews

## Indexes Strategy

### Primary Indexes
- All tables have PRIMARY KEY on `id` column with AUTO_INCREMENT

### Foreign Key Indexes
- All foreign key columns have indexes for join performance

### Query Optimization Indexes
- **Status fields**: Most entities have status indexes for filtering
- **Date fields**: created_at, updated_at, due_date for time-based queries
- **Soft deletion**: is_deleted indexes for filtering active records
- **Company isolation**: company_id indexes for multi-tenant queries
- **User activity**: user-specific indexes for dashboard queries

### Unique Constraints
- **Business logic**: email uniqueness, room_code uniqueness
- **Data integrity**: (user_id, setting_key), (meeting_id, user_id)
- **Security**: token uniqueness, session_token uniqueness

## Performance Considerations

### Query Patterns
1. **Company-scoped queries**: Most queries filter by company_id
2. **User-specific data**: Dashboard and profile queries by user_id
3. **Time-based queries**: Interviews, meetings, todos by date ranges
4. **Status filtering**: Active/inactive records, completed/pending tasks
5. **Search queries**: Title/name/email pattern matching

### Optimization Strategies
1. **Composite indexes** on frequently combined filters (company_id + status)
2. **Partial indexes** on soft-deleted records (WHERE is_deleted = FALSE)
3. **Covering indexes** for read-heavy queries
4. **Partitioning** by company_id for large datasets
5. **Archive strategy** for historical data (completed interviews, old logs)

## Security Features

### Data Protection
1. **Soft deletion**: Prevents accidental data loss
2. **Audit logging**: Tracks all data modifications
3. **Company isolation**: Multi-tenant data separation
4. **Token management**: Secure session handling
5. **Password encryption**: Bcrypt hashing
6. **File security**: Controlled file access

### Access Control
1. **RBAC**: Role-based permissions
2. **Resource-level**: Todo viewers, meeting participants
3. **Company boundaries**: Cross-tenant access prevention
4. **API authentication**: JWT tokens with refresh
5. **2FA support**: Optional two-factor authentication

## Backup & Recovery

### Strategy
1. **Daily backups**: Full database backup
2. **Point-in-time recovery**: Binary log retention
3. **Cross-region replication**: Disaster recovery
4. **Data validation**: Referential integrity checks
5. **Recovery testing**: Regular backup validation

### Retention Policies
1. **Audit logs**: 7 years retention
2. **File attachments**: Linked to entity lifecycle
3. **Soft deleted records**: 90 days before hard delete
4. **Session data**: 30 days retention
5. **Backup archives**: 1 year retention

This database definition provides a comprehensive foundation for the MiraiWorks HR management system with proper relationships, constraints, and optimization strategies.