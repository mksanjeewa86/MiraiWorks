# MiraiWorks API Reference

Welcome to the MiraiWorks API documentation. This comprehensive reference covers all available endpoints, authentication methods, and usage examples.

## Base URL

```
https://api.miraiworks.com
```

For development:
```
http://localhost:8000
```

## Authentication

MiraiWorks API uses JWT (JSON Web Tokens) for authentication. Most endpoints require a valid access token.

### Getting an Access Token

```bash
POST /api/auth/login
```

```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 3600,
  "user": {
    "id": 123,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe"
  }
}
```

### Using the Access Token

Include the token in the Authorization header:

```
Authorization: Bearer <access_token>
```

## API Endpoints

### Authentication
- [Authentication & Authorization](auth.md) - Login, logout, token refresh, 2FA

### User Management
- [Users Management](users.md) - Create, read, update, delete users with role-based permissions

### Company Management
- [Companies](companies.md) - Manage company accounts and settings

### Job Management
- [Jobs](jobs.md) - Create and manage job postings

### Application Management
- [Applications](applications.md) - Handle job applications and candidate management

### Calendar & Interviews
- [Calendar](calendar.md) - Schedule and manage interviews
- [Interviews](interviews.md) - Interview management and feedback

### File Management
- [Files](files.md) - Upload and manage resumes and documents

### Messages
- [Messages](messages.md) - Direct messaging between users

### Notifications
- [Notifications](notifications.md) - Real-time notifications and alerts

## Rate Limiting

The API implements rate limiting to ensure fair usage:

- **Standard endpoints**: 100 requests per minute per user
- **Bulk operations**: 10 requests per minute per user
- **File uploads**: 20 requests per minute per user

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

## Error Handling

### Standard Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad Request - Invalid input data |
| 401 | Unauthorized - Authentication required |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource does not exist |
| 422 | Unprocessable Entity - Validation error |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error - Server error |

### Error Response Format

```json
{
  "detail": "Error description"
}
```

For validation errors:
```json
{
  "detail": [
    {
      "loc": ["field_name"],
      "msg": "Field is required",
      "type": "missing"
    }
  ]
}
```

## Permission System

MiraiWorks uses a role-based access control (RBAC) system with the following roles:

### Super Admin
- Full system access
- Can manage all companies and users
- Can assign any role including super_admin
- Platform-wide administrative capabilities

### Company Admin
- Full access within their company
- Can manage company users and settings
- Cannot access other companies' data
- Cannot assign super_admin role

### Recruiter
- Can manage job postings and applications
- Can schedule interviews
- Can view candidate profiles
- Company-scoped access

### Employer
- Similar to recruiter with additional hiring permissions
- Can make final hiring decisions
- Can access advanced reporting

### Candidate
- Can apply to jobs
- Can manage their profile and resume
- Can participate in interviews
- Read-only access to job listings

## Pagination

List endpoints support pagination using query parameters:

```
GET /api/admin/users?page=1&size=20
```

Response includes pagination metadata:
```json
{
  "data": [...],
  "total": 150,
  "pages": 8,
  "page": 1,
  "per_page": 20
}
```

## Filtering and Search

Most list endpoints support filtering and search:

```
GET /api/admin/users?search=john&is_active=true&role=recruiter
```

Common filter parameters:
- `search` - Text search across relevant fields
- `is_active` - Filter by active status
- `company_id` - Filter by company (super admin only)
- `role` - Filter by user role
- `created_after` - Filter by creation date
- `updated_after` - Filter by last update

## Data Formats

### Dates and Times
All timestamps are in ISO 8601 format with UTC timezone:
```
2024-01-01T12:30:45Z
```

### Phone Numbers
Phone numbers should include country code:
```
+1-555-123-4567
```

### Email Addresses
Must be valid email format:
```
user@example.com
```

## File Uploads

File uploads use multipart/form-data:

```bash
curl -X POST "https://api.miraiworks.com/api/files/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@resume.pdf" \
  -F "type=resume"
```

Supported file types:
- **Documents**: PDF, DOC, DOCX (max 10MB)
- **Images**: JPG, PNG, GIF (max 5MB)

## Webhooks

MiraiWorks supports webhooks for real-time event notifications:

- User creation/updates
- Job application submissions
- Interview scheduling
- Status changes

Webhook configuration is available in the admin panel.

## SDK and Libraries

Official SDKs are available for:
- JavaScript/TypeScript
- Python
- PHP
- Ruby

Community libraries are available for other languages.

## Support

For API support:
- Documentation: [https://docs.miraiworks.com](https://docs.miraiworks.com)
- Support: [support@miraiworks.com](mailto:support@miraiworks.com)
- Status Page: [https://status.miraiworks.com](https://status.miraiworks.com)

## Changelog

### v1.2.0 (2024-01-15)
- Added enhanced role-based permissions for company admins
- Improved user creation validation
- Added bulk operations support
- Enhanced security measures

### v1.1.0 (2024-01-01)
- Added 2FA support
- Improved error handling
- Added rate limiting
- Enhanced file upload capabilities

### v1.0.0 (2023-12-01)
- Initial API release
- Core user and company management
- Authentication and authorization
- Basic job and application management