# Users Management API

The Users Management API provides endpoints for managing user accounts, roles, and permissions within the MiraiWorks platform.

## Overview

This API allows administrators to:
- Create, read, update, and delete user accounts
- Manage user roles and permissions
- Handle user suspension and activation
- Reset passwords and resend activation emails
- Perform bulk operations on multiple users

## Authentication

All endpoints require authentication using a Bearer token in the Authorization header:

```
Authorization: Bearer <access_token>
```

## Permission Levels

### Super Admin
- Full access to all user management operations
- Can manage users across all companies
- Can assign any role including `super_admin`
- Can create and manage company admin accounts

### Company Admin
- Can manage users within their own company only
- Cannot assign `super_admin` role
- Cannot create users for other companies
- Cannot move users between companies
- Can assign roles: `candidate`, `recruiter`, `employer`, `company_admin`

### Regular Users
- Cannot access user management endpoints
- Can only view/update their own profile

## Endpoints

### Create User

**POST** `/api/admin/users`

Creates a new user account.

#### Permission Requirements
- **Super Admin**: Can create users for any company with any role
- **Company Admin**: Can only create users for their own company, limited role assignments

#### Request Body

```json
{
  "email": "string",
  "first_name": "string",
  "last_name": "string",
  "phone": "string (optional)",
  "company_id": "integer (optional for super admin, auto-set for company admin)",
  "roles": ["candidate", "recruiter", "employer", "company_admin"],
  "is_admin": "boolean (optional)",
  "require_2fa": "boolean (optional)"
}
```

#### Company Admin Restrictions
- `company_id` is automatically set to the admin's company
- Cannot assign `super_admin` role
- Cannot specify a different `company_id`

#### Response

```json
{
  "id": 123,
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "full_name": "John Doe",
  "phone": "+1-555-0123",
  "company_id": 1,
  "company_name": "Example Corp",
  "roles": ["recruiter"],
  "is_active": false,
  "is_admin": false,
  "require_2fa": false,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### Error Responses

- `400 Bad Request`: Invalid input data or duplicate email
- `403 Forbidden`: Insufficient permissions or role assignment restrictions
- `404 Not Found`: Specified company does not exist

### Get Users

**GET** `/api/admin/users`

Retrieves a paginated list of users with optional filtering.

#### Permission Requirements
- **Super Admin**: Can view all users
- **Company Admin**: Can only view users from their own company

#### Query Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `page` | integer | Page number (≥1) | 1 |
| `size` | integer | Page size (1-100) | 20 |
| `search` | string | Search by name or email | - |
| `company_id` | integer | Filter by company | - |
| `is_active` | boolean | Filter by active status | - |
| `is_admin` | boolean | Filter by admin status | - |
| `is_suspended` | boolean | Filter by suspension status | - |
| `require_2fa` | boolean | Filter by 2FA requirement | - |
| `role` | string | Filter by role | - |
| `include_deleted` | boolean | Include deleted users | false |

#### Company Admin Filtering
- `company_id` parameter is automatically set to admin's company
- Cannot view users from other companies

#### Response

```json
{
  "users": [
    {
      "id": 123,
      "email": "user@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "full_name": "John Doe",
      "phone": "+1-555-0123",
      "company_id": 1,
      "company_name": "Example Corp",
      "roles": ["recruiter"],
      "is_active": true,
      "is_admin": false,
      "require_2fa": false,
      "last_login": "2024-01-01T12:00:00Z",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z",
      "is_deleted": false,
      "is_suspended": false
    }
  ],
  "total": 150,
  "pages": 8,
  "page": 1,
  "per_page": 20
}
```

### Get User by ID

**GET** `/api/admin/users/{user_id}`

Retrieves details for a specific user.

#### Permission Requirements
- **Super Admin**: Can view any user
- **Company Admin**: Can only view users from their own company
- **Regular User**: Can only view their own profile

#### Response

Same as user object in the list response.

### Update User

**PUT** `/api/admin/users/{user_id}`

Updates an existing user account.

#### Permission Requirements
- **Super Admin**: Can update any user
- **Company Admin**: Can only update users from their own company with restrictions

#### Request Body

```json
{
  "first_name": "string (optional)",
  "last_name": "string (optional)",
  "phone": "string (optional)",
  "is_active": "boolean (optional)",
  "is_admin": "boolean (optional)",
  "require_2fa": "boolean (optional)",
  "company_id": "integer (optional)",
  "roles": ["role1", "role2"] // optional
}
```

#### Company Admin Restrictions
- Cannot assign `super_admin` role
- Cannot change `company_id` to a different company
- Cannot update users from other companies

#### Response

Same as user object in the create response.

### Delete User

**DELETE** `/api/admin/users/{user_id}`

Soft deletes a user account (logical deletion).

#### Permission Requirements
- **Super Admin**: Can delete any user except themselves
- **Company Admin**: Can delete users from their own company except themselves

#### Response

```json
{
  "message": "User deleted successfully"
}
```

#### Restrictions
- Users cannot delete their own account
- Company admins cannot delete users from other companies

### Suspend User

**POST** `/api/admin/users/{user_id}/suspend`

Suspends a user account, preventing login.

#### Permission Requirements
- **Super Admin**: Can suspend any user except themselves
- **Company Admin**: Can suspend users from their own company except themselves

#### Response

```json
{
  "message": "User suspended successfully",
  "is_suspended": true
}
```

### Unsuspend User

**POST** `/api/admin/users/{user_id}/unsuspend`

Reactivates a suspended user account.

#### Permission Requirements
- **Super Admin**: Can unsuspend any user
- **Company Admin**: Can unsuspend users from their own company

#### Response

```json
{
  "message": "User unsuspended successfully",
  "is_suspended": false
}
```

### Reset Password

**POST** `/api/admin/users/{user_id}/reset-password`

Resets a user's password and optionally sends an email.

#### Request Body

```json
{
  "send_email": true
}
```

#### Permission Requirements
- **Super Admin**: Can reset password for any user
- **Company Admin**: Can reset passwords for users in their own company

#### Response

```json
{
  "message": "Password reset successfully",
  "temporary_password": "abc123def456" // Only included if send_email is false
}
```

### Resend Activation Email

**POST** `/api/admin/users/{user_id}/resend-activation`

Resends activation email to an inactive user.

#### Permission Requirements
- **Super Admin**: Can resend activation for any user
- **Company Admin**: Can resend activation for users in their own company

#### Response

```json
{
  "message": "Activation email sent successfully"
}
```

## Bulk Operations

### Bulk Suspend

**POST** `/api/admin/users/bulk/suspend`

Suspends multiple users at once.

#### Request Body

```json
{
  "user_ids": [1, 2, 3, 4],
  "reason": "Policy violation"
}
```

#### Response

```json
{
  "message": "Successfully suspended 3 user(s)",
  "suspended_count": 3,
  "errors": ["Cannot suspend user 1 from other company"]
}
```

### Bulk Unsuspend

**POST** `/api/admin/users/bulk/unsuspend`

Unsuspends multiple users at once.

#### Request Body

```json
{
  "user_ids": [1, 2, 3, 4]
}
```

### Bulk Delete

**POST** `/api/admin/users/bulk/delete`

Soft deletes multiple users at once.

#### Request Body

```json
{
  "user_ids": [1, 2, 3, 4]
}
```

### Bulk Password Reset

**POST** `/api/admin/users/bulk/reset-password`

Resets passwords for multiple users at once.

#### Request Body

```json
{
  "user_ids": [1, 2, 3, 4],
  "send_email": true
}
```

#### Response

```json
{
  "message": "Successfully reset passwords for 3 user(s)",
  "reset_count": 3,
  "errors": [],
  "temporary_passwords": {
    "1": "abc123",
    "2": "def456",
    "3": "ghi789"
  }
}
```

### Bulk Resend Activation

**POST** `/api/admin/users/bulk/resend-activation`

Resends activation emails to multiple inactive users.

#### Request Body

```json
{
  "user_ids": [1, 2, 3, 4]
}
```

## Error Handling

### Common Error Codes

- `400 Bad Request`: Invalid input data, validation errors
- `401 Unauthorized`: Missing or invalid authentication token
- `403 Forbidden`: Insufficient permissions for the requested operation
- `404 Not Found`: User or resource not found
- `422 Unprocessable Entity`: Request validation failed

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

## Role-Based Access Control Summary

| Operation | Super Admin | Company Admin | Regular User |
|-----------|-------------|---------------|--------------|
| Create user | ✅ Any company | ✅ Own company only | ❌ |
| View users | ✅ All users | ✅ Own company only | ❌ |
| Update user | ✅ Any user | ✅ Own company only | ❌ |
| Delete user | ✅ Any user (not self) | ✅ Own company only (not self) | ❌ |
| Assign super_admin role | ✅ | ❌ | ❌ |
| Move users between companies | ✅ | ❌ | ❌ |
| Bulk operations | ✅ Any users | ✅ Own company only | ❌ |

## Security Considerations

1. **Company Isolation**: Company admins can only access users within their own company
2. **Role Restrictions**: Company admins cannot assign super_admin roles
3. **Self-Protection**: Users cannot delete or suspend their own accounts
4. **Audit Trail**: All user operations are logged for compliance
5. **Password Security**: Temporary passwords are securely generated and can be sent via email
6. **2FA Enforcement**: Admin users automatically require 2FA for enhanced security

## Examples

### Creating a User as Company Admin

```bash
curl -X POST "https://api.miraiworks.com/api/admin/users" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "first_name": "Jane",
    "last_name": "Smith",
    "phone": "+1-555-0199",
    "roles": ["recruiter"]
  }'
```

### Filtering Users by Role

```bash
curl -X GET "https://api.miraiworks.com/api/admin/users?role=recruiter&is_active=true&page=1&size=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Bulk Password Reset

```bash
curl -X POST "https://api.miraiworks.com/api/admin/users/bulk/reset-password" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_ids": [123, 456, 789],
    "send_email": true
  }'
```