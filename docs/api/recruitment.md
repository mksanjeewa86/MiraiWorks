# Recruitment API Documentation

## Overview

The MiraiWorks Recruitment API provides comprehensive endpoints for managing the complete recruitment process, including job postings, candidate management, and interview scheduling.

## Base URL

```
http://localhost:8000/api
```

## Authentication

All recruitment endpoints require JWT authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

## Jobs API

### Create Job Posting

**POST** `/jobs/`

Creates a new job posting.

```json
{
  "title": "Senior Full Stack Developer",
  "description": "We are looking for an experienced full stack developer to join our team",
  "location": "Tokyo, Japan",
  "job_type": "full_time",
  "experience_level": "senior_level",
  "remote_type": "hybrid",
  "salary_min": 8000000,
  "salary_max": 12000000,
  "company_id": 1,
  "requirements": "5+ years experience with React and Node.js",
  "application_deadline": "2024-12-31T23:59:59"
}
```

**Response:**
```json
{
  "id": 1,
  "title": "Senior Full Stack Developer",
  "status": "draft",
  "slug": "senior-full-stack-developer-1",
  "created_at": "2024-01-15T10:00:00Z",
  "updated_at": "2024-01-15T10:00:00Z"
}
```

### List Jobs

**GET** `/jobs/`

Retrieves jobs with optional filtering.

**Query Parameters:**
- `skip` (int): Number of jobs to skip (default: 0)
- `limit` (int): Number of jobs to return (default: 100, max: 500)
- `location` (string): Filter by location
- `job_type` (string): Filter by job type
- `salary_min` (int): Minimum salary filter
- `salary_max` (int): Maximum salary filter
- `company_id` (int): Filter by company
- `search` (string): Search in title, description, requirements
- `status` (string): Job status filter (default: "published")

**Example:**
```
GET /jobs/?location=Tokyo&job_type=full_time&salary_min=5000000
```

**Response:**
```json
{
  "jobs": [
    {
      "id": 1,
      "title": "Senior Full Stack Developer",
      "company": "TechCorp Inc.",
      "location": "Tokyo, Japan",
      "job_type": "full_time",
      "salary_min": 8000000,
      "salary_max": 12000000,
      "status": "published"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 100
}
```

### Search Jobs

**GET** `/jobs/search`

Advanced job search with multiple criteria.

**Query Parameters:**
- `query` (string): Search query
- `location` (string): Location filter
- `job_type` (string): Job type filter
- `salary_min` (int): Minimum salary
- `salary_max` (int): Maximum salary
- `company_id` (int): Company ID filter

### Get Popular Jobs

**GET** `/jobs/popular`

Get most popular jobs by view count.

**Query Parameters:**
- `limit` (int): Number of popular jobs to return (default: 10, max: 50)

### Get Recent Jobs

**GET** `/jobs/recent`

Get recently posted jobs.

**Query Parameters:**
- `days` (int): Jobs posted in the last N days (default: 7, max: 30)
- `limit` (int): Number of jobs to return (default: 100, max: 500)

### Get Expiring Jobs

**GET** `/jobs/expiring`

Get jobs expiring soon (admin/employer only).

**Query Parameters:**
- `days` (int): Jobs expiring in the next N days (default: 7, max: 30)
- `limit` (int): Number of jobs to return (default: 100, max: 500)

### Get Job Statistics

**GET** `/jobs/statistics`

Get job posting statistics (admin only).

**Response:**
```json
{
  "total_jobs": 150,
  "published_jobs": 120,
  "draft_jobs": 20,
  "closed_jobs": 10,
  "avg_applications_per_job": 15.5,
  "top_locations": ["Tokyo", "Osaka", "Remote"],
  "top_job_types": ["full_time", "contract", "part_time"]
}
```

### Get Company Jobs

**GET** `/jobs/company/{company_id}`

Get jobs for a specific company.

**Query Parameters:**
- `skip` (int): Number of jobs to skip
- `limit` (int): Number of jobs to return

### Get Job by ID

**GET** `/jobs/{job_id}`

Get job by ID and increment view count.

### Get Job by Slug

**GET** `/jobs/slug/{slug}`

Get job by slug and increment view count.

### Update Job

**PUT** `/jobs/{job_id}`

Update job posting.

```json
{
  "title": "Updated Job Title",
  "status": "published",
  "salary_max": 15000000
}
```

### Delete Job

**DELETE** `/jobs/{job_id}`

Delete job posting (admin only).

## Interviews API

### Create Interview

**POST** `/interviews/`

Schedule a new interview.

```json
{
  "title": "Technical Interview - John Doe",
  "description": "Technical assessment for Senior Developer position",
  "interview_type": "technical",
  "status": "scheduled",
  "scheduled_start": "2024-01-20T10:00:00Z",
  "scheduled_end": "2024-01-20T11:30:00Z",
  "interviewer_id": 1,
  "candidate_id": 2,
  "location": "Conference Room A"
}
```

**Response:**
```json
{
  "id": 1,
  "title": "Technical Interview - John Doe",
  "status": "scheduled",
  "interview_type": "technical",
  "scheduled_start": "2024-01-20T10:00:00Z",
  "scheduled_end": "2024-01-20T11:30:00Z",
  "created_at": "2024-01-15T10:00:00Z"
}
```

### List Interviews

**GET** `/interviews/`

Retrieve interviews with optional filtering.

**Query Parameters:**
- `skip` (int): Number of interviews to skip
- `limit` (int): Number of interviews to return
- `status` (string): Filter by status
- `interview_type` (string): Filter by interview type
- `interviewer_id` (int): Filter by interviewer
- `candidate_id` (int): Filter by candidate

### Get Interview

**GET** `/interviews/{interview_id}`

Get interview by ID.

### Update Interview

**PUT** `/interviews/{interview_id}`

Update interview details.

```json
{
  "status": "completed",
  "notes": "Candidate showed strong technical skills",
  "scheduled_start": "2024-01-21T14:00:00Z",
  "scheduled_end": "2024-01-21T15:30:00Z"
}
```

### Delete Interview

**DELETE** `/interviews/{interview_id}`

Cancel/delete interview.

## User Management API

### List Users

**GET** `/admin/users`

List all users with role-based filtering.

**Query Parameters:**
- `skip` (int): Number of users to skip
- `limit` (int): Number of users to return
- `role` (string): Filter by role (candidate, recruiter, company_admin, super_admin)
- `company_id` (int): Filter by company
- `is_active` (bool): Filter by active status

### Create User

**POST** `/admin/users`

Create a new user.

```json
{
  "email": "john.doe@email.com",
  "first_name": "John",
  "last_name": "Doe",
  "company_id": 1,
  "roles": ["candidate"]
}
```

### Get User

**GET** `/admin/users/{user_id}`

Get user by ID.

### Update User

**PUT** `/admin/users/{user_id}`

Update user information.

### Delete User

**DELETE** `/admin/users/{user_id}`

Delete user (admin only).

## Data Types

### Job Types
- `full_time`
- `part_time`
- `contract`
- `temporary`
- `internship`
- `freelance`

### Experience Levels
- `entry_level`
- `mid_level`
- `senior_level`
- `executive`
- `internship`

### Remote Types
- `on_site`
- `remote`
- `hybrid`

### Job Status
- `draft`
- `published`
- `paused`
- `closed`
- `archived`

### Interview Types
- `phone_screen`
- `technical`
- `system_design`
- `behavioral`
- `final`
- `hr_screening`

### Interview Status
- `scheduled`
- `in_progress`
- `completed`
- `cancelled`
- `rescheduled`

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid request data"
}
```

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

### 403 Forbidden
```json
{
  "detail": "Not enough permissions"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

## Rate Limiting

API endpoints are rate-limited to prevent abuse:
- 100 requests per minute for authenticated users
- 20 requests per minute for unauthenticated users

## Testing

Use the interactive API documentation at `/docs` to test endpoints.

Test credentials:
- **Candidate**: `john.doe@email.com` (any password)
- **Recruiter**: `recruiter1@techcorp.jp` (any password)
- **Admin**: `admin@techcorp.jp` (any password)

## Code Examples

### Python (using requests)

```python
import requests

# Login
response = requests.post('http://localhost:8000/api/auth/login', json={
    'email': 'john.doe@email.com',
    'password': 'password'
})
token = response.json()['access_token']

# Create job posting
headers = {'Authorization': f'Bearer {token}'}
job_data = {
    'title': 'Software Engineer',
    'description': 'Great opportunity for software engineers',
    'location': 'Tokyo, Japan',
    'job_type': 'full_time',
    'company_id': 1
}
response = requests.post('http://localhost:8000/api/jobs/',
                        json=job_data, headers=headers)
print(response.json())
```

### JavaScript (using fetch)

```javascript
// Login
const loginResponse = await fetch('http://localhost:8000/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'john.doe@email.com',
    password: 'password'
  })
});
const { access_token } = await loginResponse.json();

// List jobs
const jobsResponse = await fetch('http://localhost:8000/api/jobs/', {
  headers: { 'Authorization': `Bearer ${access_token}` }
});
const jobs = await jobsResponse.json();
console.log(jobs);
```

## Support

For additional support or questions about the API, please refer to:
- Interactive API docs: `/docs`
- OpenAPI specification: `/openapi.json`
- Project documentation: `docs/`