# User Permissions and Capabilities

**Last Updated**: October 2025


This document outlines what different user roles can view, create, edit, and manage in the MiraiWorks system.

## User Roles Overview

The system has the following user roles with hierarchical permissions:

1. **Super Admin** - System-wide administrative access
2. **Company Admin** - Administrative access within their company
3. **Employer** - Company user with hiring capabilities
4. **Recruiter** - Company user with recruitment capabilities
5. **Candidate** - Job seeker with limited access

---

## 🔴 Super Admin Permissions

**Full system access with no restrictions**

### 👀 **Can View:**
- ✅ All users across all companies
- ✅ All companies (active and deleted)
- ✅ All jobs across all companies
- ✅ All applications across all companies
- ✅ All messages and communications
- ✅ All files and attachments
- ✅ System-wide analytics and reports
- ✅ All notifications
- ✅ Password reset requests from all users
- ✅ User settings for all users

### ➕ **Can Create:**
- ✅ New companies
- ✅ Users for any company with any role (except other super admins)
- ✅ Company admin users
- ✅ Jobs for any company
- ✅ System-wide announcements

### ✏️ **Can Edit:**
- ✅ Any user's profile and settings
- ✅ Any company information
- ✅ Any job posting
- ✅ System configuration
- ✅ User roles and permissions
- ✅ Company status (activate/deactivate)

### 🗑️ **Can Delete:**
- ✅ Any user account
- ✅ Any company (soft delete)
- ✅ Any job posting
- ✅ Any application
- ✅ System data cleanup

### 🔧 **Special Capabilities:**
- ✅ Approve password reset requests for all users
- ✅ Access system logs and audit trails
- ✅ Manage demo company settings
- ✅ System backup and maintenance
- ✅ Cross-company data access

---

## 🟠 Company Admin Permissions

**Administrative access within their own company only**

### 👀 **Can View:**
- ✅ All users within their company
- ✅ Their company information and settings
- ✅ All jobs posted by their company
- ✅ All applications to their company's jobs
- ✅ Messages between company users and candidates
- ✅ Files shared within company context
- ✅ Company-specific analytics
- ✅ Notifications related to their company
- ✅ Password reset requests from company users
- ❌ Other companies' data
- ❌ System-wide information

### ➕ **Can Create:**
- ✅ New users within their company (employer/recruiter/candidate roles only)
- ✅ Job postings for their company
- ✅ Company announcements
- ✅ Interview schedules
- ❌ Users for other companies
- ❌ Super admin users
- ❌ Company admin users (in some configurations)

### ✏️ **Can Edit:**
- ✅ Company users' profiles and settings
- ✅ Their company information
- ✅ Company job postings
- ✅ User roles within company (limited)
- ✅ Company user status (activate/deactivate)
- ❌ Users from other companies
- ❌ System-wide settings

### 🗑️ **Can Delete:**
- ✅ Company users (except other admins)
- ✅ Company job postings
- ✅ Company-specific data
- ❌ Users from other companies
- ❌ The company itself

### 🔧 **Special Capabilities:**
- ✅ Approve password resets for company users
- ✅ Manage company user permissions
- ✅ View company analytics and reports
- ✅ Bulk user operations within company
- ✅ Company data export

### ⚠️ **Restrictions:**
- ❌ Cannot assign super_admin role to users
- ❌ Cannot create users for other companies
- ❌ Cannot view or modify other companies' data
- ❌ Cannot access system-wide functions

---

## 🟡 Employer Permissions

**Company user focused on hiring and job management**

### 👀 **Can View:**
- ✅ Their own profile and settings
- ✅ Company information (read-only)
- ✅ Job postings they created or are assigned to
- ✅ Applications to jobs they manage
- ✅ Candidate profiles (when applied to their jobs)
- ✅ Messages with candidates and team members
- ✅ Files related to their job postings
- ✅ Interview schedules they're involved in
- ✅ Company directory (limited)
- ❌ Other companies' data
- ❌ Jobs they're not assigned to
- ❌ System administration functions

### ➕ **Can Create:**
- ✅ Job postings for their company
- ✅ Interview schedules
- ✅ Messages to candidates and team members
- ✅ Job-related documents and attachments
- ✅ Application reviews and notes
- ❌ New user accounts
- ❌ Company-wide announcements

### ✏️ **Can Edit:**
- ✅ Their own profile and settings
- ✅ Job postings they created
- ✅ Application statuses for their jobs
- ✅ Interview details they manage
- ✅ Their job-related communications
- ❌ Other users' profiles
- ❌ Company settings
- ❌ Jobs created by others (unless assigned)

### 🗑️ **Can Delete:**
- ✅ Job postings they created
- ✅ Their own messages and files
- ✅ Interview schedules they created
- ❌ Other users' data
- ❌ Applications (can only update status)

### 🔧 **Special Capabilities:**
- ✅ Manage application workflow for their jobs
- ✅ Schedule and conduct interviews
- ✅ Collaborate with team members on hiring
- ✅ Generate reports for their jobs
- ✅ Export candidate data for their positions

---

## 🟢 Recruiter Permissions

**Company user focused on talent acquisition and candidate management**

### 👀 **Can View:**
- ✅ Their own profile and settings
- ✅ Company information (read-only)
- ✅ All company job postings
- ✅ Candidate database within company context
- ✅ Applications across company jobs (broader than employer)
- ✅ Messages with candidates and team members
- ✅ Recruitment analytics and pipeline data
- ✅ Company directory
- ❌ Other companies' data
- ❌ Administrative functions

### ➕ **Can Create:**
- ✅ Job postings for their company
- ✅ Candidate profiles and records
- ✅ Recruitment campaigns
- ✅ Messages to candidates and team members
- ✅ Interview schedules
- ✅ Candidate sourcing records
- ❌ New user accounts
- ❌ Company settings

### ✏️ **Can Edit:**
- ✅ Their own profile and settings
- ✅ Job postings (with broader permissions than employer)
- ✅ Candidate profiles and notes
- ✅ Application statuses across jobs
- ✅ Recruitment pipeline data
- ❌ Other users' profiles
- ❌ Company administrative settings

### 🗑️ **Can Delete:**
- ✅ Job postings they manage
- ✅ Their own messages and files
- ✅ Candidate records they created
- ❌ Other users' data
- ❌ System data

### 🔧 **Special Capabilities:**
- ✅ Advanced candidate search and filtering
- ✅ Bulk candidate operations
- ✅ Recruitment pipeline management
- ✅ Cross-job application tracking
- ✅ Talent pool management
- ✅ Recruitment analytics and reporting

---

## 🔵 Candidate Permissions

**Job seekers with limited, self-service access**

### 👀 **Can View:**
- ✅ Their own profile and application history
- ✅ Public job postings they're eligible for
- ✅ Their application statuses
- ✅ Messages from employers/recruiters
- ✅ Interview schedules for their applications
- ✅ Public company information
- ✅ Their uploaded documents and files
- ❌ Other candidates' information
- ❌ Company internal data
- ❌ Administrative functions

### ➕ **Can Create:**
- ✅ Job applications
- ✅ Their candidate profile
- ✅ Messages to employers/recruiters (replies)
- ✅ Interview availability
- ✅ Document uploads (resume, portfolio, etc.)
- ❌ Job postings
- ❌ User accounts for others

### ✏️ **Can Edit:**
- ✅ Their own profile and personal information
- ✅ Their application preferences
- ✅ Their uploaded documents
- ✅ Interview availability
- ✅ Communication preferences
- ❌ Job postings
- ❌ Other users' data
- ❌ Application statuses (read-only)

### 🗑️ **Can Delete:**
- ✅ Their own uploaded files
- ✅ Their own messages
- ✅ Their candidate profile (account deletion)
- ❌ Job applications (can withdraw only)
- ❌ Other users' data

### 🔧 **Special Capabilities:**
- ✅ Job search and filtering
- ✅ Application tracking
- ✅ Interview scheduling
- ✅ Profile visibility settings
- ✅ Job alerts and notifications
- ✅ Application withdrawal

### ⚠️ **Restrictions:**
- ❌ Cannot view other candidates' profiles
- ❌ Cannot access company internal data
- ❌ Cannot create or modify job postings
- ❌ Cannot access administrative functions
- ❌ Limited to public information only

---

## 📊 Permission Matrix Summary

| Feature | Super Admin | Company Admin | Employer | Recruiter | Candidate |
|---------|-------------|---------------|----------|-----------|-----------|
| **User Management** |
| Create Users (Any Company) | ✅ | ❌ | ❌ | ❌ | ❌ |
| Create Users (Own Company) | ✅ | ✅ | ❌ | ❌ | ❌ |
| View All Users | ✅ | Company Only | ❌ | ❌ | ❌ |
| Edit User Profiles | ✅ | Company Only | Own Only | Own Only | Own Only |
| Delete Users | ✅ | Company Only | ❌ | ❌ | Own Only |
| **Company Management** |
| Create Companies | ✅ | ❌ | ❌ | ❌ | ❌ |
| Edit Company Info | ✅ | Own Only | ❌ | ❌ | ❌ |
| View All Companies | ✅ | Own Only | Own Only | Own Only | Public Only |
| Delete Companies | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Job Management** |
| Create Jobs | ✅ | ✅ | ✅ | ✅ | ❌ |
| Edit All Jobs | ✅ | Company Only | Own Only | Broader | ❌ |
| View All Jobs | ✅ | Company Only | Assigned | Company | Public Only |
| Delete Jobs | ✅ | Company Only | Own Only | Managed | ❌ |
| **Application Management** |
| View All Applications | ✅ | Company Only | Own Jobs | Company | Own Only |
| Manage Application Status | ✅ | Company Only | Own Jobs | Company | ❌ |
| Create Applications | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Communication** |
| Access All Messages | ✅ | Company Only | Related | Related | Own Only |
| Send Messages | ✅ | ✅ | ✅ | ✅ | Replies Only |
| **System Administration** |
| System Settings | ✅ | ❌ | ❌ | ❌ | ❌ |
| Password Reset Approval | ✅ | Company Only | ❌ | ❌ | ❌ |
| View System Logs | ✅ | ❌ | ❌ | ❌ | ❌ |

---

## 🔐 Security and Access Control

### **Authentication Requirements:**
- All users must authenticate with email/password
- 2FA required for admin roles in production
- Session timeout for security

### **Permission Enforcement:**
- Role-based access control (RBAC) at API level
- Company-scoped data access for non-super-admin users
- Frontend UI adapts based on user permissions
- Backend validation prevents unauthorized actions

### **Data Isolation:**
- Companies cannot access each other's data
- Users can only see data relevant to their role
- Soft deletion maintains data integrity
- Audit trails for sensitive operations

---

## 📝 Notes

1. **Hierarchical Permissions:** Higher-level roles generally include lower-level permissions within their scope
2. **Company Scoping:** Most roles are restricted to their own company's data
3. **Dynamic UI:** The frontend interface changes based on user role and permissions
4. **API Security:** All endpoints validate permissions server-side
5. **Demo Mode:** Special handling for demo companies with limited capabilities

This permission system ensures proper data security while providing appropriate access levels for each user role in the hiring and recruitment workflow.
