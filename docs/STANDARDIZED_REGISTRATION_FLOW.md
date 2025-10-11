# MiraiWorks Standardized User Registration Flow

## 🎯 Overview

**ALL users** (regardless of creation method) follow the same standardized registration flow to ensure security and consistency.

---

## 📋 Standardized Flow for ALL Users

### **Step 1: User Account Creation**

#### Self-Registration (Public)
```
User visits: /auth/register?role={candidate|employer|recruiter}
User fills form:
- First Name
- Last Name
- Email
- Phone (optional)
- Role (pre-filled from URL)

User clicks: "Create Account" or "Start Free Trial"
```

#### Admin-Created (Admin Panel)
```
Admin visits: /app/admin/users/add
Admin fills form:
- First Name
- Last Name
- Email
- Phone (optional)
- Role (dropdown selection)

Admin clicks: "Create User"
```

---

### **Step 2: System Processing**

```
Backend Process:
1. Validate user input
2. Check email uniqueness
3. Generate random temporary password (secure, 16 chars)
4. Hash temporary password
5. Create user record with:
   - is_active = FALSE (inactive)
   - must_reset_password = TRUE
   - email_verified = FALSE
   - created_at = current timestamp
6. Send welcome email with temporary password
7. Return success response
```

**API Endpoint:**
```
POST /api/auth/register (self-registration)
POST /api/admin/users (admin-created)

Request Payload:
{
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+81 90 1234 5678",
  "role": "candidate|employer|recruiter|admin"
}

Response:
{
  "success": true,
  "message": "Account created successfully. Check your email for login instructions.",
  "data": {
    "email": "user@example.com",
    "full_name": "John Doe",
    "role": "candidate"
  }
}
```

---

### **Step 3: Welcome Email Sent**

```
Email Template:
---
Subject: Welcome to MiraiWorks - Activate Your Account

Dear {{first_name}},

Welcome to MiraiWorks! Your account has been created.

Account Details:
- Email: {{email}}
- Role: {{role}}
- Temporary Password: {{temp_password}}

⚠️ IMPORTANT SECURITY NOTICE:
Your account is currently INACTIVE. You must complete the following steps to activate it:

1. Visit: https://miraiworks.com/auth/login
2. Login with your email and temporary password
3. You will be automatically redirected to set a new password
4. Choose a strong, secure password
5. Your account will be activated after password reset

Your temporary password will expire in 24 hours.

For security reasons, please change your password immediately after first login.

Need Help?
Contact our support team at support@miraiworks.com

Best regards,
The MiraiWorks Team
---
```

---

### **Step 4: User First Login**

```
User Action Flow:
1. User receives welcome email
2. User visits: /auth/login
3. User enters:
   - Email: user@example.com
   - Password: [temporary password from email]
4. User clicks "Sign in"
```

**Backend Validation:**
```
Login Process:
1. Verify email exists
2. Verify password matches (temp password)
3. Check must_reset_password flag → TRUE
4. Check is_active flag → FALSE
5. Generate session token (temporary)
6. Return: { require_password_reset: true }
```

**Frontend Response:**
```
If require_password_reset = true:
- Do NOT redirect to dashboard
- Redirect to: /auth/reset-password?token={session_token}
- Show message: "Please set a new password to activate your account"
```

---

### **Step 5: Forced Password Reset**

```
URL: /auth/reset-password?token={session_token}
Page Title: "Set Your New Password"
Subtitle: "Create a secure password to activate your account"

Form Fields:
✓ New Password (with strength meter)
✓ Confirm New Password

Password Requirements:
✓ Minimum 12 characters
✓ Uppercase letter (A-Z)
✓ Lowercase letter (a-z)
✓ Number (0-9)
✓ Special character (@$!%*?&^#())
✓ Cannot be same as temporary password
✓ Password strength score ≥ 3

Submit Button: "Activate Account"
```

**Backend Password Reset Process:**
```
POST /api/auth/reset-password

Request:
{
  "token": "{session_token}",
  "new_password": "NewSecurePassword123!@#"
}

Processing:
1. Validate session token
2. Validate new password requirements
3. Verify new password ≠ temporary password
4. Hash new password
5. Update user record:
   - password = new_hashed_password
   - must_reset_password = FALSE
   - is_active = TRUE
   - email_verified = TRUE
   - password_changed_at = current timestamp
6. Invalidate temporary password
7. Create permanent session token
8. Return success

Response:
{
  "success": true,
  "message": "Your account has been activated successfully!",
  "redirect": "/dashboard"
}
```

---

### **Step 6: Account Activation & Dashboard**

```
Success Flow:
1. Password successfully reset
2. Account status changed: inactive → ACTIVE
3. must_reset_password flag: true → FALSE
4. Show success message: "Account activated successfully!"
5. Redirect to: /dashboard
6. User can now use platform normally
```

---

## 🔄 Complete User Journey Comparison

### Candidate Registration Flow
```
User clicks "I'm a Candidate" card
→ /candidate landing page
→ Click "Create Free Account"
→ /auth/register?role=candidate
→ Fill form (no password field)
→ Submit
→ Email sent with temp password
→ Account created (INACTIVE)
→ User checks email
→ Login with temp password
→ Forced to /auth/reset-password
→ Set new password
→ Account activated (ACTIVE)
→ Redirect to /dashboard
```

### Employer Registration Flow
```
User clicks "I'm an Employer" card
→ /employer landing page
→ Click "Start Free Trial"
→ /auth/register?role=employer
→ Fill form (no password field)
→ Submit
→ Email sent with temp password
→ Account created (INACTIVE, TRIAL)
→ User checks email
→ Login with temp password
→ Forced to /auth/reset-password
→ Set new password
→ Account activated (ACTIVE, TRIAL)
→ Redirect to /dashboard
```

### Recruiter Registration Flow
```
User clicks "I'm a Recruiter" card
→ /recruiter landing page
→ Click "Start Free Trial"
→ /auth/register?role=recruiter
→ Fill form (no password field)
→ Submit
→ Email sent with temp password
→ Account created (INACTIVE, TRIAL)
→ User checks email
→ Login with temp password
→ Forced to /auth/reset-password
→ Set new password
→ Account activated (ACTIVE, TRIAL)
→ Redirect to /dashboard
```

### Admin-Created User Flow
```
Admin logs into admin panel
→ /app/admin/users/add
→ Fill user form (no password field)
→ Select role from dropdown
→ Submit
→ Email sent with temp password to new user
→ Account created (INACTIVE)
→ User checks email
→ Login with temp password
→ Forced to /auth/reset-password
→ Set new password
→ Account activated (ACTIVE)
→ Redirect to /dashboard
```

**ALL FLOWS ARE IDENTICAL FROM EMAIL ONWARDS**

---

## 📊 Account Status Flow

```
Account Status Lifecycle:

[REGISTRATION] → Status: INACTIVE
                 must_reset_password: TRUE
                 email_verified: FALSE
                 ↓
[EMAIL SENT]   → Temporary password sent
                 ↓
[FIRST LOGIN]  → User logs in with temp password
                 Session created (temporary)
                 ↓
[PASSWORD RESET] → User sets new password
                   ↓
[ACTIVATED]    → Status: ACTIVE
                 must_reset_password: FALSE
                 email_verified: TRUE
                 ↓
[DASHBOARD]    → Full platform access
```

---

## 🔐 Security Features

### Temporary Password Generation
```python
def generate_temporary_password():
    """
    Generate secure temporary password
    - 16 characters long
    - Mix of uppercase, lowercase, numbers, special chars
    - Cryptographically random
    - Cannot be guessed or brute-forced easily
    """
    import secrets
    import string

    chars = string.ascii_letters + string.digits + "@$!%*?&#"
    password = ''.join(secrets.choice(chars) for _ in range(16))

    # Ensure all character types present
    while not (
        any(c.isupper() for c in password) and
        any(c.islower() for c in password) and
        any(c.isdigit() for c in password) and
        any(c in "@$!%*?&#" for c in password)
    ):
        password = ''.join(secrets.choice(chars) for _ in range(16))

    return password
```

### Temporary Password Expiration
```
- Temporary password valid for: 24 hours
- After 24 hours: Must request new password reset
- Stored in DB: temp_password_expires_at
- Checked on login: if expired, show "Password expired" error
```

### Session Token Security
```
Temporary Session (before password reset):
- Limited scope: can only access /auth/reset-password
- Expires in: 1 hour
- Cannot access dashboard or other routes

Permanent Session (after password reset):
- Full scope: all platform features
- Expires in: 7 days (configurable)
- Refresh token provided
```

---

## 🚨 Error Handling

### Registration Errors
```
1. Email already exists
   → Error: "An account with this email already exists"
   → Action: Prompt to login or reset password

2. Invalid email format
   → Error: "Please enter a valid email address"
   → Action: Correct email format

3. Email service unavailable
   → Error: "Unable to send welcome email. Please contact support."
   → Action: Account still created, admin must manually send email

4. Network/Database error
   → Error: "Registration failed. Please try again."
   → Action: Retry registration
```

### Login Errors
```
1. Temporary password expired
   → Error: "Your temporary password has expired"
   → Action: Show "Request new password" link
   → Redirect to: /auth/forgot-password

2. Wrong temporary password
   → Error: "Invalid email or password"
   → Action: Retry login or request password reset

3. Account suspended by admin
   → Error: "Your account has been suspended. Contact support."
   → Action: Show support contact information

4. Too many login attempts
   → Error: "Too many failed login attempts. Try again in 15 minutes."
   → Action: Rate limiting applied
```

### Password Reset Errors
```
1. New password same as temporary
   → Error: "New password cannot be the same as temporary password"
   → Action: Choose different password

2. Password too weak
   → Error: "Password does not meet security requirements"
   → Action: Show requirements and strength meter

3. Passwords don't match
   → Error: "Passwords do not match"
   → Action: Re-enter confirm password

4. Session token expired
   → Error: "Your session has expired. Please login again."
   → Action: Redirect to /auth/login
```

---

## 📧 Email Templates

### Welcome Email (All Users)
```html
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
        .content { background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px; }
        .password-box { background: white; border: 2px solid #667eea; border-radius: 8px; padding: 15px; margin: 20px 0; font-family: monospace; font-size: 18px; text-align: center; }
        .warning { background: #fef3c7; border-left: 4px solid #f59e0b; padding: 15px; margin: 20px 0; }
        .button { display: inline-block; background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 6px; margin: 20px 0; }
        .steps { background: white; padding: 20px; border-radius: 8px; margin: 20px 0; }
        .step { margin: 10px 0; padding-left: 30px; position: relative; }
        .step:before { content: "→"; position: absolute; left: 0; color: #667eea; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Welcome to MiraiWorks!</h1>
        </div>
        <div class="content">
            <h2>Hello {{first_name}},</h2>

            <p>Your MiraiWorks account has been created successfully!</p>

            <p><strong>Account Details:</strong></p>
            <ul>
                <li>Email: <strong>{{email}}</strong></li>
                <li>Role: <strong>{{role}}</strong></li>
            </ul>

            <p><strong>Your Temporary Password:</strong></p>
            <div class="password-box">
                {{temp_password}}
            </div>

            <div class="warning">
                <strong>⚠️ IMPORTANT SECURITY NOTICE:</strong><br>
                Your account is currently <strong>INACTIVE</strong>. You must activate it by setting a new password on your first login.
            </div>

            <div class="steps">
                <h3>Activation Steps:</h3>
                <div class="step">Visit the login page</div>
                <div class="step">Enter your email and temporary password</div>
                <div class="step">You'll be redirected to set a new password</div>
                <div class="step">Create a strong, secure password</div>
                <div class="step">Your account will be activated!</div>
            </div>

            <center>
                <a href="https://miraiworks.com/auth/login" class="button">Login Now</a>
            </center>

            <p><small>This temporary password will expire in 24 hours. For security reasons, please activate your account as soon as possible.</small></p>

            <hr>

            <p><strong>Need Help?</strong><br>
            Contact our support team at <a href="mailto:support@miraiworks.com">support@miraiworks.com</a></p>

            <p>Best regards,<br>
            <strong>The MiraiWorks Team</strong></p>
        </div>
    </div>
</body>
</html>
```

### Account Activated Email
```
Subject: Your MiraiWorks Account is Now Active!

Dear {{first_name}},

Congratulations! Your MiraiWorks account has been successfully activated.

You now have full access to all platform features. Here's what you can do:

{{#if role == "candidate"}}
✓ Search and apply for jobs
✓ Build your professional resume
✓ Track your applications
✓ Manage your profile
{{/if}}

{{#if role == "employer"}}
✓ Post job openings
✓ Review candidate applications
✓ Schedule interviews
✓ Access analytics
✓ Your free trial is now active (30 days)
{{/if}}

{{#if role == "recruiter"}}
✓ Access candidate database
✓ Manage client relationships
✓ Track placements
✓ Monitor commissions
✓ Your free trial is now active (30 days)
{{/if}}

Login anytime at: https://miraiworks.com/auth/login

Need assistance? We're here to help!
support@miraiworks.com

Best regards,
The MiraiWorks Team
```

---

## 🧪 Testing Checklist

### Self-Registration Testing
- [ ] Can register as candidate
- [ ] Can register as employer
- [ ] Can register as recruiter
- [ ] Email validation works
- [ ] Duplicate email rejected
- [ ] Welcome email received
- [ ] Temporary password in email
- [ ] Account created as INACTIVE
- [ ] must_reset_password = TRUE

### First Login Testing
- [ ] Can login with temporary password
- [ ] Cannot access dashboard directly
- [ ] Redirected to reset password page
- [ ] Cannot skip password reset
- [ ] Session token has limited scope

### Password Reset Testing
- [ ] Password strength validation works
- [ ] Cannot reuse temporary password
- [ ] Password confirmation works
- [ ] Account activated after reset
- [ ] must_reset_password = FALSE
- [ ] Redirect to dashboard works

### Email Testing
- [ ] Welcome email sent immediately
- [ ] Email contains correct information
- [ ] Temporary password is secure
- [ ] Links in email work
- [ ] Email formatting correct

### Security Testing
- [ ] Temporary password expires after 24h
- [ ] Session expires appropriately
- [ ] Rate limiting on login works
- [ ] Audit trail captured
- [ ] Password cannot be reused

---

## 📈 Database Schema Changes

```sql
-- Add new columns to users table
ALTER TABLE users ADD COLUMN must_reset_password BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN temp_password_expires_at TIMESTAMP NULL;
ALTER TABLE users ADD COLUMN password_changed_at TIMESTAMP NULL;
ALTER TABLE users ADD COLUMN activation_token VARCHAR(255) NULL;
ALTER TABLE users ADD COLUMN activated_at TIMESTAMP NULL;

-- Update existing users (if any)
UPDATE users SET must_reset_password = FALSE WHERE must_reset_password IS NULL;
UPDATE users SET is_active = TRUE WHERE is_active IS NULL;
```

---

## 🔄 Migration Strategy

### For Existing Users
```
Option 1: Grandfather existing users
- Keep existing active users as-is
- New flow only for new registrations

Option 2: Force all users to reset
- Send email to all users
- Next login forces password reset
- All accounts temporarily inactive until reset

Recommended: Option 1 (less disruptive)
```

---

**Last Updated:** January 2025
**Version:** 2.0 (Standardized Flow)
**Maintained By:** MiraiWorks Development Team
