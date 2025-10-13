# Profile Information Plan by Role

## Overview

Different user roles require different levels of profile detail. This document outlines what information should be displayed for each role.

---

## 🎯 Role: CANDIDATE (Most Detailed)

**Purpose**: Marketing themselves to potential employers

### Profile Sections to Display

#### 1. Header Section (Always Visible)
- ✅ Cover photo
- ✅ Profile picture
- ✅ Full name
- ✅ Current job title / Desired role
- ✅ Location (city, country)
- ✅ Professional headline
- ✅ Contact info (email, phone - with privacy controls)
- ✅ Social links (LinkedIn, GitHub, Portfolio)
- ✅ Job search status badge (e.g., "Actively Looking", "Open to Opportunities")

#### 2. About / Summary
- ✅ Professional bio (500-1000 chars)
- ✅ Career objectives
- ✅ Years of experience

#### 3. Work Experience (Detailed)
- ✅ Company logos
- ✅ Position title
- ✅ Company name
- ✅ Duration (start - end / current)
- ✅ Location
- ✅ Job description / achievements
- ✅ Skills used in each role
- ✅ Employment type (Full-time, Contract, etc.)

#### 4. Education (Detailed)
- ✅ Institution logo/icon
- ✅ Degree type
- ✅ Field of study
- ✅ Institution name
- ✅ Graduation year
- ✅ GPA (optional)
- ✅ Honors/Awards

#### 5. Skills (Comprehensive)
- ✅ Technical skills (with proficiency levels)
- ✅ Soft skills
- ✅ Languages (with proficiency)
- ✅ Tools & technologies
- ✅ Endorsement counts (future)

#### 6. Certifications & Licenses
- ✅ Certification name
- ✅ Issuing organization
- ✅ Issue date & expiry
- ✅ Credential ID & URL
- ✅ Certificate image/badge

#### 7. Projects & Portfolio
- ✅ Project name & description
- ✅ Your role
- ✅ Technologies used
- ✅ Project URL / GitHub link
- ✅ Project images/screenshots
- ✅ Duration

#### 8. Achievements & Awards
- ✅ Title
- ✅ Issuer
- ✅ Date
- ✅ Description

#### 9. Profile Analytics (Sidebar)
- ✅ Profile views
- ✅ Applications sent
- ✅ Interviews completed
- ✅ Response rate
- ✅ Profile completeness %

#### 10. Preferences (Visible to recruiters)
- ✅ Desired job type (Full-time, Part-time, etc.)
- ✅ Desired salary range
- ✅ Willing to relocate
- ✅ Remote/Hybrid/Onsite preference
- ✅ Availability to start

#### 11. Resume/CV
- ✅ Upload/download resume
- ✅ Last updated date

---

## 👔 Role: RECRUITER (Moderate Detail)

**Purpose**: Professional identity for candidates to verify credibility

### Profile Sections to Display

#### 1. Header Section
- ✅ Profile picture
- ✅ Full name
- ✅ Job title (e.g., "Senior Recruiter", "Talent Acquisition Manager")
- ✅ Company name (with logo)
- ✅ Location
- ✅ Contact info (email, phone)
- ✅ LinkedIn profile

#### 2. About
- ✅ Brief professional bio (200-300 chars)
- ✅ Years of experience in recruitment
- ✅ Specializations (e.g., "Tech Recruitment", "Executive Search")

#### 3. Company Information
- ✅ Company name
- ✅ Company logo
- ✅ Industry
- ✅ Company size
- ✅ Link to company profile

#### 4. Recruitment Focus
- ✅ Industries you recruit for
- ✅ Job types (Full-time, Contract, etc.)
- ✅ Locations you hire for
- ✅ Experience levels (Junior, Mid, Senior)

#### 5. Activity Stats (Optional)
- ✅ Jobs posted
- ✅ Candidates placed
- ✅ Active job openings

#### 6. Contact & Social
- ✅ Email
- ✅ Phone
- ✅ LinkedIn
- ✅ Calendar booking link (optional)

---

## 🏢 Role: EMPLOYER (Minimal Detail)

**Purpose**: Basic professional identity as company representative

### Profile Sections to Display

#### 1. Header Section
- ✅ Profile picture
- ✅ Full name
- ✅ Job title/Role at company
- ✅ Company name (with logo)
- ✅ Location
- ✅ Contact info (email, phone)

#### 2. About
- ✅ Brief professional bio (150-200 chars)
- ✅ Role in company
- ✅ Department

#### 3. Company Information
- ✅ Company name
- ✅ Company logo
- ✅ Industry
- ✅ Link to company profile page

#### 4. Contact Information
- ✅ Email
- ✅ Phone
- ✅ LinkedIn (optional)

#### 5. Activity Stats (Optional)
- ✅ Jobs posted
- ✅ Active openings

---

## 🔒 Privacy Controls (All Roles)

### Candidates can control:
- Who can see their phone number
- Who can download their resume
- Profile visibility (Public / Recruiters Only / Private)
- Whether they appear in searches
- Email visibility

### Recruiters/Employers can control:
- Contact information visibility
- Who can contact them

---

## 📊 Profile Completeness Indicators

### For Candidates:
- Basic info (20%)
- Work experience (25%)
- Education (15%)
- Skills (15%)
- Resume uploaded (10%)
- Profile picture (5%)
- Projects/Portfolio (10%)

### For Recruiters:
- Basic info (40%)
- Company info (30%)
- Recruitment focus (20%)
- Profile picture (10%)

### For Employers:
- Basic info (50%)
- Company info (30%)
- Profile picture (20%)

---

## 🎨 UI Layout Differences

### Candidate Profile:
- LinkedIn-style layout (as implemented)
- Multiple sections with detailed cards
- Sidebar with analytics
- Cover photo + large profile picture
- Timeline-style experience/education

### Recruiter Profile:
- Simplified single-page layout
- Company-focused design
- Contact information prominent
- No cover photo needed
- 2-column layout (info + company)

### Employer Profile:
- Minimal card-based layout
- Company badge/logo prominent
- Contact card
- Very simple, professional
- No complex sections

---

## 🔄 Shared Components

These can be reused across roles with conditional rendering:
- `ProfileHeader` (with role-specific variants)
- `AboutSection`
- `ContactInfo`
- `ProfilePicture`
- `CompanyBadge`

---

## 📝 Implementation Priority

### Phase 1 ✅ COMPLETED
- ✅ Candidate profile (comprehensive)
- ✅ LinkedIn-style layout
- ✅ Cover photo + profile picture
- ✅ About, Experience, Education, Skills sections
- ✅ Profile analytics sidebar
- ✅ Achievements section
- ✅ All modals for editing sections
- ✅ Role-based visibility utility (profileVisibility.ts)

### Phase 2 🚧 IN PROGRESS (90% Complete)
- ✅ Backend: RecruiterProfile model and database table
- ✅ Backend: Recruiter profile CRUD operations
- ✅ Backend: Recruiter profile API endpoints
- ✅ Backend: Router integration
- ✅ Database migration for recruiter_profiles table
- 🚧 Frontend: TypeScript types for recruiter/employer
- 🚧 Frontend: API client functions
- 🚧 Frontend: RecruiterProfileView component
- 🚧 Frontend: EmployerProfileView component
- 🚧 Frontend: Role-based routing in UnifiedProfileView
- ⬜ Privacy controls UI
- ⬜ Profile completeness indicators

### Phase 3
- 🚧 Recruiter profile implementation (Backend ✅, Frontend 🚧)
- 🚧 Employer profile implementation (Backend ✅, Frontend 🚧)
- ⬜ Company profile pages
- ⬜ Profile visibility settings

### Phase 4
- ⬜ Advanced features (endorsements, recommendations)
- ⬜ Profile analytics dashboard
- ⬜ Public profile URLs
- ⬜ Profile export/download

---

## 🚀 Next Steps

1. **Fix HEIC upload issue** - Backend needs to accept HEIC/HEIF files
2. **Add role-based rendering** - Show different sections based on user role
3. **Implement privacy controls** - Allow users to control who sees what
4. **Add profile completeness** - Visual indicator of profile completion
5. **Create recruiter/employer profiles** - Simplified versions

---

## 📋 Database Schema Requirements

### Candidate Profile Extensions:
- ✅ `job_preferences` table (job type, salary range, location preferences)
- ✅ `profile_work_experiences` table (detailed experience records)
- ✅ `profile_educations` table (detailed education records)
- ✅ `profile_skills` table (with proficiency levels)
- ✅ `profile_certifications` table
- ✅ `profile_projects` table
- ⬜ `achievements` table (future)
- ⬜ `profile_views` table (analytics - future)

### Recruiter Profile Extensions:
- ✅ `recruiter_profiles` table (specializations, recruitment focus, stats)
  - years_of_experience
  - specializations
  - bio
  - company_description
  - industries, job_types, locations, experience_levels
  - calendar_link, linkedin_url
  - jobs_posted, candidates_placed, active_openings

### Employer Profile Extensions:
- ✅ Minimal - uses existing User and Company tables

---

## 🔍 API Endpoints

### Candidate Endpoints ✅:
- ✅ `GET /api/profile/work-experience` - Get work experiences
- ✅ `POST /api/profile/work-experience` - Add experience
- ✅ `PUT /api/profile/work-experience/{id}` - Update experience
- ✅ `DELETE /api/profile/work-experience/{id}` - Delete experience
- ✅ `GET /api/profile/education` - Get educations
- ✅ `POST /api/profile/education` - Add education
- ✅ `PUT /api/profile/education/{id}` - Update education
- ✅ `DELETE /api/profile/education/{id}` - Delete education
- ✅ `GET /api/profile/skills` - Get skills
- ✅ `POST /api/profile/skills` - Add skill
- ✅ `PUT /api/profile/skills/{id}` - Update skill
- ✅ `DELETE /api/profile/skills/{id}` - Delete skill
- ✅ `GET /api/profile/certifications` - Get certifications
- ✅ `POST /api/profile/certifications` - Add certification
- ✅ `PUT /api/profile/certifications/{id}` - Update certification
- ✅ `DELETE /api/profile/certifications/{id}` - Delete certification
- ✅ `GET /api/profile/projects` - Get projects
- ✅ `POST /api/profile/projects` - Add project
- ✅ `PUT /api/profile/projects/{id}` - Update project
- ✅ `DELETE /api/profile/projects/{id}` - Delete project
- ⬜ `GET /api/profile/completeness` - Get completion %

### Recruiter Endpoints ✅:
- ✅ `GET /api/recruiter-profile/me` - Get recruiter profile
- ✅ `POST /api/recruiter-profile/me` - Create recruiter profile
- ✅ `PUT /api/recruiter-profile/me` - Update recruiter profile
- ✅ `DELETE /api/recruiter-profile/me` - Delete recruiter profile
- ✅ `GET /api/recruiter-profile/{user_id}` - View recruiter profile

### Privacy Endpoints (Future):
- ⬜ `GET /api/user/privacy` - Get privacy settings
- ⬜ `PUT /api/user/privacy` - Update privacy settings

### Public Profile (Future):
- ⬜ `GET /api/public/profiles/{user_id}` - Get public profile (respects privacy)

---

*Last Updated: 2025-01-12*
