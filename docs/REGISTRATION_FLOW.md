# MiraiWorks User Registration Flow

## Overview
This document outlines the complete registration flow for all three user types in the MiraiWorks platform.

---

## 🎯 User Types

1. **Candidate** - Job seekers looking for employment opportunities
2. **Employer** - Companies/organizations looking to hire talent
3. **Recruiter** - Recruitment agencies connecting candidates with opportunities
4. **Admin/Super Admin** - Platform administrators with elevated privileges

---

## 📝 User Creation Methods

### **Method 1: Self-Registration**
Users register themselves through the public registration pages (documented below)

### **Method 2: Admin-Created Users**
Super admin creates user accounts through the admin panel (see Admin User Creation section)

---

## 📋 Registration Flow Comparison

### Self-Registration Flow

| Step | Candidate | Employer | Recruiter |
|------|-----------|----------|-----------|
| **Account Type** | Free Account | Trial Account | Trial Account |
| **Landing Page** | `/candidate` | `/employer` | `/recruiter` |
| **Registration URL** | `/auth/register?role=candidate` | `/auth/register?role=employer` | `/auth/register?role=recruiter` |
| **Button Text** | "Create Free Account" | "Start Free Trial" | "Start Free Trial" |
| **Color Scheme** | Green-Teal | Purple-Pink | Blue-Cyan |
| **Success Redirect** | `/dashboard` | `/dashboard` | `/dashboard` |
| **Password Set By** | User | User | User |
| **Email Verification** | Required | Required | Required |

### Admin-Created User Flow

| Feature | Candidate | Employer | Recruiter | Admin |
|---------|-----------|----------|-----------|-------|
| **Created Via** | Admin Panel | Admin Panel | Admin Panel | Admin Panel |
| **API Endpoint** | `POST /api/admin/users` | `POST /api/admin/users` | `POST /api/admin/users` | `POST /api/admin/users` |
| **Password Set By** | Admin (temp) | Admin (temp) | Admin (temp) | Admin (temp) |
| **Email Verification** | Optional | Optional | Optional | Optional |
| **Force Password Reset** | Optional | Optional | Optional | Optional |
| **Welcome Email** | Optional | Optional | Optional | Optional |
| **Account Status** | Admin choice | Admin choice | Admin choice | Admin choice |
| **Trial Period** | N/A | Admin configurable | Admin configurable | N/A |

---

## 🚀 Detailed Registration Flows

### 1️⃣ CANDIDATE REGISTRATION FLOW

#### **Step 1: Home Page Entry**
```
URL: /
User Action: Clicks "I'm a Candidate" card
Destination: /candidate
```

#### **Step 2: Candidate Landing Page**
```
URL: /candidate
Page Features:
- Hero section: "Find Your Dream Career Today"
- Features showcase (Job Search, Resume Builder, Application Tracking)
- CTA Buttons:
  - "Create Free Account" (Primary)
  - "Browse Jobs" (Secondary)

User Action: Clicks "Create Free Account" or "Create Your Profile"
Destination: /auth/register?role=candidate
```

#### **Step 3: Registration Form**
```
URL: /auth/register?role=candidate
Page Title: "Create Candidate Account"
Subtitle: "Find your dream job and advance your career"
Color Scheme: Green-Teal gradient
Button: "Create Account"

Required Fields:
✓ Role: candidate (pre-filled, hidden)
✓ First Name
✓ Last Name
✓ Email
✓ Password (min 12 chars, with strength requirements)
✓ Confirm Password
○ Phone (Optional)

Form Features:
- Password strength indicator (4-level)
- Password match validator
- Real-time validation
- Glass-morphism design
```

#### **Step 4: Form Submission**
```
API Endpoint: POST /api/auth/register
Request Payload:
{
  "email": "user@example.com",
  "password": "SecurePass123!@#",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+81 90 1234 5678",
  "role": "candidate",
  "company_name": "Default Company",
  "company_domain": "default.com"
}

Loading State: "Creating account..."
```

#### **Step 5: Success & Redirect**
```
Success Message: "Account created successfully! Redirecting..."
Wait: 2 seconds
Redirect: /dashboard
Account Status: Active (Free)
```

---

### 2️⃣ EMPLOYER REGISTRATION FLOW

#### **Step 1: Home Page Entry**
```
URL: /
User Action: Clicks "I'm an Employer" card
Destination: /employer
```

#### **Step 2: Employer Landing Page**
```
URL: /employer
Page Features:
- Hero section: "Find Top Talent For Your Company"
- Features showcase:
  - Easy Job Posting
  - Applicant Tracking
  - Analytics & Insights
- CTA Buttons:
  - "Start Free Trial" (Primary)
  - "View Pricing" (Secondary)

User Action: Clicks "Start Free Trial" or "Start Hiring Now"
Destination: /auth/register?role=employer
```

#### **Step 3: Registration Form**
```
URL: /auth/register?role=employer
Page Title: "Start Your Free Trial"
Subtitle: "Find and hire top talent for your company"
Color Scheme: Purple-Pink gradient
Button: "Start Free Trial"

Required Fields:
✓ Role: employer (pre-filled, hidden)
✓ First Name
✓ Last Name
✓ Email
✓ Password (min 12 chars, with strength requirements)
✓ Confirm Password
○ Phone (Optional)

Form Features:
- Password strength indicator (4-level)
- Password match validator
- Real-time validation
- Glass-morphism design
- Trial account messaging
```

#### **Step 4: Form Submission**
```
API Endpoint: POST /api/auth/register
Request Payload:
{
  "email": "hiring@company.com",
  "password": "SecurePass123!@#",
  "first_name": "Jane",
  "last_name": "Smith",
  "phone": "+81 90 1234 5678",
  "role": "employer",
  "company_name": "Default Company",
  "company_domain": "default.com"
}

Loading State: "Starting trial..."
```

#### **Step 5: Success & Redirect**
```
Success Message: "Account created successfully! Redirecting..."
Wait: 2 seconds
Redirect: /dashboard
Account Status: Trial (Free Trial Period)
```

---

### 3️⃣ RECRUITER REGISTRATION FLOW

#### **Step 1: Home Page Entry**
```
URL: /
User Action: Clicks "I'm a Recruiter" card
Destination: /recruiter
```

#### **Step 2: Recruiter Landing Page**
```
URL: /recruiter
Page Features:
- Hero section: "Connect Talent With Opportunity"
- Features showcase:
  - Candidate Management
  - Client Relations
  - Placement Tracking
- CTA Buttons:
  - "Start Free Trial" (Primary)
  - "View Pricing" (Secondary)

User Action: Clicks "Start Free Trial"
Destination: /auth/register?role=recruiter
```

#### **Step 3: Registration Form**
```
URL: /auth/register?role=recruiter
Page Title: "Start Your Free Trial"
Subtitle: "Connect candidates with opportunities"
Color Scheme: Blue-Cyan gradient
Button: "Start Free Trial"

Required Fields:
✓ Role: recruiter (pre-filled, hidden)
✓ First Name
✓ Last Name
✓ Email
✓ Password (min 12 chars, with strength requirements)
✓ Confirm Password
○ Phone (Optional)

Form Features:
- Password strength indicator (4-level)
- Password match validator
- Real-time validation
- Glass-morphism design
- Trial account messaging
```

#### **Step 4: Form Submission**
```
API Endpoint: POST /api/auth/register
Request Payload:
{
  "email": "recruiter@agency.com",
  "password": "SecurePass123!@#",
  "first_name": "Mike",
  "last_name": "Johnson",
  "phone": "+81 90 1234 5678",
  "role": "recruiter",
  "company_name": "Default Company",
  "company_domain": "default.com"
}

Loading State: "Starting trial..."
```

#### **Step 5: Success & Redirect**
```
Success Message: "Account created successfully! Redirecting..."
Wait: 2 seconds
Redirect: /dashboard
Account Status: Trial (Free Trial Period)
```

---

## 🔄 Alternative Registration Flows

### Direct Registration (No Role Pre-selected)

```
URL: /auth/register
User sees: Role dropdown selector

Dropdown Options:
- "Select your role"
- "Candidate - Looking for jobs"
- "Employer - Hiring talent"
- "Recruiter - Connecting talent"

User must select role before proceeding
Form adapts to selected role (colors, titles, button text)
```

---

## 🔐 Password Requirements

All user types have the same password requirements:

```
Minimum Requirements:
✓ At least 12 characters
✓ Uppercase letters (A-Z)
✓ Lowercase letters (a-z)
✓ Numbers (0-9)
✓ Special characters (@$!%*?&^#())
✓ Not a common password (blacklist check)
✓ Password strength score ≥ 3 (using zxcvbn)

Password Strength Levels:
0-1: Very Weak (Red)
2:   Weak (Orange)
3:   Good (Yellow)
4:   Strong (Green)

Real-time Indicators:
- 4-bar strength meter
- Color-coded feedback
- Text description (Very Weak, Weak, Good, Strong)
- Password match indicator for confirmation field
```

---

## 📧 Email Validation

```
Format: RFC 5322 compliant email
Validation: Client-side (Zod) + Server-side
Error Messages:
- "Invalid email address"
- "Email already exists" (from server)
```

---

## ⚠️ Error Handling

### Client-Side Validation Errors
```
Display: Red text below field
Examples:
- "First name is required"
- "Password must be at least 12 characters"
- "Passwords don't match"
- "Invalid email address"
- "This password is too common"
- "Password is too weak"
```

### Server-Side Errors
```
Display: Red banner at top of form
Examples:
- "Email already registered"
- "Unable to create account. Please try again"
- Network/API errors
```

---

## 🎨 Visual Design Elements

### Common Design Features (All Roles)
```
Background:
- Gradient: slate-900 → purple-900 → slate-900
- Animated floating blobs (purple, yellow, pink)
- Background pattern overlay

Form Container:
- Glass-morphism effect (white/10 backdrop-blur)
- Rounded corners (3xl)
- 2px white/20 border
- 2xl shadow

Input Fields:
- Glass-morphism (white/10 bg)
- White/20 border
- Rounded xl corners
- White text, gray-400 placeholders
- Purple-400 focus ring
- Icon prefixes (User, Mail, Lock, Phone)
```

### Role-Specific Colors

**Candidate (Green-Teal)**
```
Primary Button: from-green-600 to-teal-600
Hover: from-green-700 to-teal-700
Focus Ring: ring-green-400
```

**Employer (Purple-Pink)**
```
Primary Button: from-purple-600 to-pink-600
Hover: from-purple-700 to-pink-700
Focus Ring: ring-purple-400
```

**Recruiter (Blue-Cyan)**
```
Primary Button: from-blue-600 to-cyan-600
Hover: from-blue-700 to-cyan-700
Focus Ring: ring-blue-400
```

---

## 🔄 Post-Registration Flow

### All User Types
```
1. JWT token stored in cookies/local storage
2. User authenticated state updated
3. Redirect to /dashboard (2 second delay)
4. Welcome message displayed
5. Onboarding flow begins (if implemented)
```

### Account Status by Role

**Candidate**
```
Status: Active
Plan: Free (Unlimited)
Features:
- Job search
- Resume builder
- Application tracking
- Profile management
```

**Employer**
```
Status: Trial
Plan: Free Trial (30 days typical)
Features:
- Post jobs (limited)
- Review applications
- Interview scheduling
- Basic analytics
Note: Will prompt for paid plan after trial
```

**Recruiter**
```
Status: Trial
Plan: Free Trial (30 days typical)
Features:
- Candidate database (limited)
- Client management
- Placement tracking
- Basic commission tracking
Note: Will prompt for paid plan after trial
```

---

## 🔗 Navigation Links

### During Registration

**Header Links:**
- "MiraiWorks" → Back to home (/)
- "Back to Home" → Link below form (/)

**Footer Links:**
- "Already have an account? Sign in" → /auth/login

---

## 📱 Responsive Design

```
Mobile (< 640px):
- Single column layout
- Full-width inputs
- Stacked name fields
- Touch-optimized buttons

Tablet (640px - 1024px):
- Centered form (max-w-xl)
- 2-column name fields
- Larger touch targets

Desktop (> 1024px):
- Centered form (max-w-xl)
- Hover effects enabled
- Keyboard navigation optimized
```

---

## 🧪 Testing Considerations

### Test Scenarios for Each Role

**Candidate Registration:**
- [ ] Can access via home page card
- [ ] Role pre-filled correctly
- [ ] Green color scheme displayed
- [ ] "Create Account" button text
- [ ] Free account created
- [ ] Redirects to dashboard

**Employer Registration:**
- [ ] Can access via home page card
- [ ] Role pre-filled correctly
- [ ] Purple-pink color scheme displayed
- [ ] "Start Free Trial" button text
- [ ] Trial account created
- [ ] Redirects to dashboard

**Recruiter Registration:**
- [ ] Can access via home page card
- [ ] Role pre-filled correctly
- [ ] Blue-cyan color scheme displayed
- [ ] "Start Free Trial" button text
- [ ] Trial account created
- [ ] Redirects to dashboard

**Common Tests (All Roles):**
- [ ] Password strength validation works
- [ ] Password match validation works
- [ ] Email format validation works
- [ ] Form submission prevents double-clicks
- [ ] Error messages display correctly
- [ ] Success message shows before redirect
- [ ] Authentication state updates
- [ ] Can navigate back to home
- [ ] Can navigate to login
- [ ] Responsive design works on all devices

---

## 📊 Analytics Tracking Points

```
Events to Track:
1. Landing page view (by role)
2. Registration page view (by role)
3. Form field interactions
4. Form validation errors (by field)
5. Form submission attempts
6. Registration success (by role)
7. Registration failures (with error type)
8. Time to complete registration
9. Abandonment points
```

---

## 🚨 Security Features

```
1. Password strength enforcement (zxcvbn)
2. Common password blacklist
3. HTTPS required for production
4. CSRF protection
5. Rate limiting on registration endpoint
6. Email verification (if enabled)
7. SQL injection prevention (parameterized queries)
8. XSS protection (React escaping)
9. Secure password hashing (bcrypt)
10. JWT token with expiration
```

---

## 👨‍💼 ADMIN USER CREATION FLOW

### Overview
Super admins can create user accounts directly through the admin panel, bypassing the public registration process.

---

### 4️⃣ ADMIN-CREATED USER FLOW

#### **Step 1: Admin Panel Access**
```
URL: /app/users/add (or /app/admin/users/add)
Permission Required: Super Admin role
Authentication: Must be logged in as admin
```

#### **Step 2: User Creation Form**
```
Admin Panel Page: "Add New User"

Required Fields:
✓ Email (unique)
✓ First Name
✓ Last Name
✓ Role Selection:
  - Candidate
  - Employer
  - Recruiter
  - Admin
✓ Password (admin sets initial password)
✓ Company Name (optional for candidates)
✓ Company Domain (optional for candidates)
○ Phone (Optional)

Additional Admin Options:
✓ Account Status:
  - Active (default)
  - Inactive
  - Suspended
✓ Email Verified: Yes/No
✓ Skip Email Verification: Checkbox
✓ Send Welcome Email: Checkbox
✓ Force Password Reset on First Login: Checkbox
```

#### **Step 3: Form Submission**
```
API Endpoint: POST /api/admin/users
Authorization: Bearer {admin_jwt_token}
Permission Check: Super Admin role required

Request Payload:
{
  "email": "user@example.com",
  "password": "TempPassword123!@#",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+81 90 1234 5678",
  "role": "candidate|employer|recruiter|admin",
  "company_name": "Company Inc",
  "company_domain": "company.com",
  "is_active": true,
  "is_email_verified": true,
  "skip_email_verification": true,
  "send_welcome_email": true,
  "force_password_reset": false
}

Response:
{
  "success": true,
  "data": {
    "id": 123,
    "email": "user@example.com",
    "full_name": "John Doe",
    "role": "candidate",
    "is_active": true,
    "created_at": "2025-01-10T10:30:00Z"
  },
  "message": "User created successfully"
}
```

#### **Step 4: Post-Creation Actions**

**If "Send Welcome Email" is checked:**
```
Email Sent To: user@example.com
Subject: "Welcome to MiraiWorks"
Contents:
- Welcome message
- Login credentials (email provided, password set by admin)
- First login instructions
- Password change recommendation
- Platform overview
- Support contact information
```

**If "Force Password Reset" is checked:**
```
User record flagged with: must_reset_password = true
First login behavior:
1. User logs in with admin-provided credentials
2. Immediately redirected to /auth/reset-password
3. Must set new password before accessing platform
4. Cannot bypass password reset
```

#### **Step 5: User First Login**

**Scenario A: Normal Login (No Password Reset Required)**
```
1. User receives welcome email with credentials
2. User goes to /auth/login
3. Enters email and admin-provided password
4. Successfully logs in
5. Redirects to /dashboard
6. (Optional) Shown onboarding tour
```

**Scenario B: Forced Password Reset**
```
1. User receives welcome email with credentials
2. User goes to /auth/login
3. Enters email and admin-provided password
4. System detects must_reset_password flag
5. Automatically redirects to /auth/reset-password
6. User must set new password
7. After password reset → /dashboard
```

---

### Differences: Admin-Created vs Self-Registered

| Feature | Self-Registration | Admin-Created |
|---------|-------------------|---------------|
| **Password Set By** | User | Admin (initial) |
| **Email Verification** | Required | Optional/Skipped |
| **Account Activation** | Automatic | Admin choice |
| **Welcome Email** | Automatic | Admin choice |
| **Trial Period** | Automatic (employer/recruiter) | Admin configurable |
| **Force Password Reset** | No | Optional |
| **Account Status Control** | Active only | Active/Inactive/Suspended |
| **Role Assignment** | User chooses | Admin assigns |
| **Permissions** | Default by role | Admin can customize |
| **Onboarding Flow** | Standard | Can be customized |

---

### Admin Panel User Management Features

#### **User List View**
```
URL: /app/users or /app/admin/users
Features:
- Searchable user list
- Filter by role (Candidate, Employer, Recruiter, Admin)
- Filter by status (Active, Inactive, Suspended)
- Sort by name, email, created date, last login
- Pagination
- Bulk actions (activate, deactivate, delete)
```

#### **User Detail/Edit View**
```
URL: /app/users/{id}/edit or /app/admin/users/{id}
Available Actions:
- Edit user information
- Change role
- Reset password (send reset link)
- Activate/Deactivate account
- Verify email manually
- View login history
- View activity log
- Assign permissions
- Delete user (with confirmation)
```

#### **User Actions**
```
Available Admin Actions:
1. Create New User
2. Edit User Details
3. Activate/Deactivate Account
4. Suspend Account (temporary block)
5. Delete Account (permanent, with confirmation)
6. Reset Password (send email link)
7. Set Temporary Password
8. Verify Email Manually
9. Change User Role
10. Assign Custom Permissions
11. View Login History
12. View Activity Logs
13. Impersonate User (for support)
```

---

### Security Considerations for Admin-Created Users

#### **Password Security**
```
Admin-Set Password Requirements:
✓ Same strict requirements as self-registration
✓ Admin should use password generator
✓ Recommend "Force Password Reset" on first login
✓ Never share passwords via insecure channels
✓ Passwords should be transmitted via secure email only
```

#### **Access Control**
```
✓ Only Super Admin can create users
✓ Regular admins can only view/edit (configurable)
✓ Audit log for all admin actions
✓ IP logging for admin operations
✓ Two-factor authentication for admin accounts
✓ Session timeout for admin panel
```

#### **Email Verification**
```
Best Practices:
- Skip verification for internal/trusted users only
- Always verify external users
- Send verification email even if account is active
- Log verification bypass in audit trail
```

---

### Audit Trail for Admin Actions

#### **Logged Events**
```
All admin user creation/modification actions logged:
- Action type (create, update, delete, etc.)
- Admin user ID and name
- Target user ID and email
- Timestamp
- IP address
- Changes made (before/after values)
- Reason (if provided)

Log Storage:
- Database table: audit_logs
- Retention: Permanent (or per compliance policy)
- Access: Super Admin only
```

#### **Example Audit Log Entry**
```json
{
  "id": 456,
  "action": "user_created",
  "actor": {
    "id": 1,
    "email": "admin@miraiworks.com",
    "role": "super_admin"
  },
  "target": {
    "id": 123,
    "email": "newuser@example.com",
    "role": "employer"
  },
  "details": {
    "fields_set": [
      "email",
      "first_name",
      "last_name",
      "role",
      "company_name"
    ],
    "skip_email_verification": true,
    "send_welcome_email": true,
    "force_password_reset": false
  },
  "ip_address": "192.168.1.100",
  "timestamp": "2025-01-10T10:30:00Z",
  "user_agent": "Mozilla/5.0..."
}
```

---

### Notification Flows for Admin-Created Users

#### **Welcome Email Template**
```
Subject: Welcome to MiraiWorks - Your Account is Ready

Dear {{first_name}},

Your MiraiWorks account has been created by our administrative team.

Account Details:
- Email: {{email}}
- Role: {{role}}
- Login URL: https://miraiworks.com/auth/login

{{#if temporary_password}}
Temporary Password: {{temporary_password}}

⚠️ IMPORTANT: Please change your password after your first login for security.
{{/if}}

{{#if force_password_reset}}
⚠️ You will be required to set a new password upon first login.
{{/if}}

Getting Started:
1. Visit the login page
2. Enter your credentials
3. Complete your profile
4. Explore the platform

Need Help?
Contact our support team at support@miraiworks.com

Best regards,
The MiraiWorks Team
```

#### **Password Reset Email (If Forced)**
```
Subject: Set Your MiraiWorks Password

Dear {{first_name}},

Welcome to MiraiWorks! Before you can access your account, you need to set your password.

Click the link below to set your password:
{{password_reset_link}}

This link expires in 24 hours.

If you didn't expect this email, please contact support immediately.

Best regards,
The MiraiWorks Team
```

---

### Bulk User Import (Optional Feature)

#### **CSV Import Format**
```csv
email,first_name,last_name,role,company_name,phone
john@example.com,John,Doe,candidate,Company Inc,+81901234567
jane@company.com,Jane,Smith,employer,Smith Corp,+81901234568
mike@agency.com,Mike,Johnson,recruiter,Johnson Agency,+81901234569
```

#### **Import Process**
```
1. Admin uploads CSV file
2. System validates all rows
3. Shows preview of users to be created
4. Admin confirms import
5. System creates users in batch
6. Error report generated for failed imports
7. Success report shows created users
8. Bulk welcome emails sent (optional)
```

#### **Import Validation Rules**
```
✓ Email must be unique
✓ Email must be valid format
✓ Role must be: candidate, employer, recruiter, or admin
✓ First name required
✓ Last name required
✓ Company name optional (required for employer/recruiter)
✓ Phone optional
✓ All rows validated before any import
✓ Duplicate emails in CSV rejected
```

---

### Use Cases for Admin User Creation

#### **Use Case 1: Corporate Account Setup**
```
Scenario: Large company wants 50 employees onboarded
Process:
1. Admin creates employer account for company
2. Admin bulk imports 50 employee accounts
3. All set to "Force Password Reset"
4. Welcome emails sent with instructions
5. Employees set their own passwords on first login
```

#### **Use Case 2: Partner Onboarding**
```
Scenario: New recruitment agency partnership
Process:
1. Admin creates recruiter account for agency
2. Sets up custom permissions
3. Configures trial period
4. Sends welcome email with credentials
5. Agency admin can then create sub-accounts
```

#### **Use Case 3: Support Account Creation**
```
Scenario: User requests account via support ticket
Process:
1. Support verifies user identity
2. Admin creates account manually
3. Skips email verification (already verified)
4. Sends credentials via secure channel
5. User logs in immediately
```

#### **Use Case 4: Internal Testing**
```
Scenario: QA team needs test accounts
Process:
1. Admin creates test users
2. Sets temporary passwords
3. No welcome emails sent
4. Accounts marked for deletion after testing
5. Audit trail maintained
```

---

### Admin User Creation Best Practices

#### **Security Best Practices**
```
✓ Always use strong temporary passwords
✓ Enable "Force Password Reset" for external users
✓ Verify user identity before creating account
✓ Use secure channel for credential transmission
✓ Document reason for account creation
✓ Review and approve bulk imports
✓ Regular audit log reviews
✓ Disable admin accounts when not in use
✓ Use 2FA for all admin accounts
✓ Limit number of super admin accounts
```

#### **Operational Best Practices**
```
✓ Standardize naming conventions
✓ Use email templates for consistency
✓ Document account creation process
✓ Set up approval workflow for sensitive roles
✓ Regular cleanup of inactive accounts
✓ Maintain contact information for all users
✓ Schedule regular permission audits
✓ Backup user data regularly
✓ Train admins on user management
✓ Establish escalation procedures
```

---

## 🔮 Future Enhancements

```
Potential Features:
1. Email verification step
2. SMS verification (optional)
3. Social login (Google, LinkedIn)
4. Company domain verification (employers)
5. Profile completion wizard
6. Onboarding tours by role
7. Welcome email automation
8. Referral code support
9. Multi-language support
10. Progressive profiling
```

---

**Last Updated:** January 2025
**Version:** 1.0
**Maintained By:** MiraiWorks Development Team
