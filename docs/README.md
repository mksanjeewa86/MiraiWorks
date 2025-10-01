# MiraiWorks Documentation

**Last Updated**: October 2025

This directory contains all technical and architectural documentation for the MiraiWorks recruitment and HR management platform.

## 📚 Documentation Structure

### Core Documentation
- **[SYSTEM_DOCUMENTATION.md](SYSTEM_DOCUMENTATION.md)** - Complete system overview, user roles, permissions, API functions, and test coverage
- **[ARCHITECTURE_RECOMMENDATIONS.md](ARCHITECTURE_RECOMMENDATIONS.md)** - System architecture recommendations and best practices

### Backend Documentation
Located in [`backend/`](backend/) folder:
- **[BACKEND_STRUCTURE.md](backend/BACKEND_STRUCTURE.md)** - Backend directory structure and organization
- **[DATABASE_MIGRATION_GUIDE.md](backend/DATABASE_MIGRATION_GUIDE.md)** - Database migration procedures using Alembic
- **[SEEDS_DOCUMENTATION.md](backend/SEEDS_DOCUMENTATION.md)** - Database seeding guide for development and testing
- **[DOCKER_SEEDS_GUIDE.md](backend/DOCKER_SEEDS_GUIDE.md)** - Docker-based seeding workflow
- **[API_CONNECTION_TESTS.md](backend/API_CONNECTION_TESTS.md)** - API endpoint testing documentation
- **[CI_CD_PYTEST_FIXES.md](backend/CI_CD_PYTEST_FIXES.md)** - CI/CD pipeline and pytest configuration

### Feature Guides
Located in [`backend/`](backend/) folder:
- **[FILE_ATTACHMENTS_GUIDE.md](backend/FILE_ATTACHMENTS_GUIDE.md)** - File upload and attachment system
- **[VIDEO_CALLS_GUIDE.md](backend/VIDEO_CALLS_GUIDE.md)** - Video calling functionality
- **[MESSAGE_REPLY_FEATURE.md](backend/MESSAGE_REPLY_FEATURE.md)** - Messaging and reply system
- **[EXAM_SYSTEM_README.md](backend/EXAM_SYSTEM_README.md)** - Examination and assessment system
- **[MBTI_README.md](backend/MBTI_README.md)** - MBTI personality assessment integration

### Testing Documentation
Located in [`backend/`](backend/) folder:
- **[TEST_SUMMARY.md](backend/TEST_SUMMARY.md)** - Complete test coverage summary
- **[TEST_FIXES.md](backend/TEST_FIXES.md)** - Test optimization and fixes
- **[TEST_TRANSACTION_ISSUE_FIX.md](backend/TEST_TRANSACTION_ISSUE_FIX.md)** - Database transaction testing fixes

### Recruitment Workflows
- **[RECRUITMENT_WORKFLOW_SYSTEM_PLAN.md](RECRUITMENT_WORKFLOW_SYSTEM_PLAN.md)** - Comprehensive recruitment workflow system design
- **[RECRUITMENT_PROCESS_PLAN.md](RECRUITMENT_PROCESS_PLAN.md)** - Recruitment process implementation plan
- **[ASSIGNMENT_WORKFLOW_DOCUMENTATION.md](ASSIGNMENT_WORKFLOW_DOCUMENTATION.md)** - Assignment and task workflow system
- **[recruitment-strategy.md](recruitment-strategy.md)** - Recruitment strategy and best practices

### UI/UX Mockups
- **[workflow-editor-mockup-v2.md](workflow-editor-mockup-v2.md)** - Latest workflow editor design (v2)
- **[workflow-editor-mockup.md](workflow-editor-mockup.md)** - Original workflow editor design (v1)
- **[interview-modal-mockup.md](interview-modal-mockup.md)** - Interview creation/edit modal design

### Testing Strategy
- **[test-plan.md](test-plan.md)** - Comprehensive test plan and strategy
- **[scenario-testing-plan.md](scenario-testing-plan.md)** - Scenario-based testing approach
- **[scenario-test-implementations.md](scenario-test-implementations.md)** - Detailed test scenario implementations
- **[PYTEST_SPEEDUP_GUIDE.md](PYTEST_SPEEDUP_GUIDE.md)** - Pytest performance optimization

### Planning Documents
- **[video-call-feature-plan.md](video-call-feature-plan.md)** - Video calling feature planning
- **[CALENDAR_MIGRATION_PLAN.md](CALENDAR_MIGRATION_PLAN.md)** - Calendar system migration plan
- **[user-permissions.md](user-permissions.md)** - User roles and permission system

### Recommendations & Best Practices
- **[WORKFLOW_RECOMMENDATIONS.md](WORKFLOW_RECOMMENDATIONS.md)** - Workflow system recommendations
- **[PERFORMANCE_RECOMMENDATIONS.md](PERFORMANCE_RECOMMENDATIONS.md)** - System performance optimization
- **[SECURITY_RECOMMENDATIONS.md](SECURITY_RECOMMENDATIONS.md)** - Security best practices
- **[RECOMMENDATIONS.md](RECOMMENDATIONS.md)** - General system recommendations

### Setup & Configuration
- **[free-transcription-setup.md](free-transcription-setup.md)** - Audio/video transcription setup

## 🏗️ System Architecture

### Technology Stack
- **Backend**: Python FastAPI with SQLAlchemy ORM
- **Database**: PostgreSQL/MySQL with Alembic migrations
- **Frontend**: Next.js 14+ with TypeScript
- **Authentication**: JWT-based with 2FA support
- **File Storage**: MinIO/S3 compatible storage
- **Caching**: Redis
- **Real-time**: WebSocket support for messaging
- **Testing**: Pytest with comprehensive coverage

### Key Features
1. **User Management** - Multi-role system (Super Admin, Company Admin, Recruiter, Employer, Candidate)
2. **Recruitment Workflows** - Linear and branching recruitment process automation
3. **Interview Management** - Scheduling, video calls, and feedback collection
4. **Todo/Assignment System** - Task management with workflow integration
5. **Messaging System** - Real-time messaging with reply threading
6. **Resume Management** - Resume parsing, storage, and search
7. **Calendar Integration** - Unified event management
8. **File Attachments** - Secure file upload and management
9. **MBTI Assessment** - Personality testing integration
10. **Exam System** - Skills assessment and testing

## 📝 Quick Start

1. **For Developers**: Start with [SYSTEM_DOCUMENTATION.md](SYSTEM_DOCUMENTATION.md)
2. **For Backend Setup**: See [backend/BACKEND_STRUCTURE.md](backend/BACKEND_STRUCTURE.md)
3. **For Database**: Check [backend/DATABASE_MIGRATION_GUIDE.md](backend/DATABASE_MIGRATION_GUIDE.md)
4. **For Testing**: Review [test-plan.md](test-plan.md) and [backend/TEST_SUMMARY.md](backend/TEST_SUMMARY.md)
5. **For Workflows**: Read [RECRUITMENT_WORKFLOW_SYSTEM_PLAN.md](RECRUITMENT_WORKFLOW_SYSTEM_PLAN.md)

## 🔍 Finding Documentation

### By Feature
- **Recruitment**: Search for "recruitment", "workflow", "interview"
- **User Management**: See SYSTEM_DOCUMENTATION.md User Roles section
- **File Operations**: FILE_ATTACHMENTS_GUIDE.md
- **Video/Communication**: VIDEO_CALLS_GUIDE.md, MESSAGE_REPLY_FEATURE.md
- **Testing**: All TEST_*.md files in backend/ folder

### By Role
- **Backend Developers**: backend/ folder + SYSTEM_DOCUMENTATION.md
- **Frontend Developers**: *-mockup.md files + SYSTEM_DOCUMENTATION.md
- **DevOps**: CI_CD_PYTEST_FIXES.md, DOCKER_SEEDS_GUIDE.md
- **QA/Testing**: test-plan.md, scenario-testing-plan.md, TEST_SUMMARY.md
- **Product Managers**: RECRUITMENT_WORKFLOW_SYSTEM_PLAN.md, recruitment-strategy.md

## 🗂️ Deprecated/Archived Documents

The following documents are kept for historical reference but may be outdated:
- `CI_IMPORT_FIXES.md` - CI import fixes (superseded by CI_CD_PYTEST_FIXES.md)
- `CI_STILL_FAILING_ANALYSIS.md` - Old CI analysis
- `COMMIT_AND_FIX_CI.md` - Old CI fix documentation
- `FALLBACK_SOLUTION_ALIASED_IMPORTS.md` - Frontend import resolution (resolved)
- `FRONTEND_MODULE_RESOLUTION_FIX.md` - Frontend module fixes (resolved)
- `TEST_FIXES_SUMMARY.md` - Old test fixes (superseded by TEST_SUMMARY.md)

These files will be moved to an `archive/` folder in future cleanup.

## 📅 Documentation Maintenance

- **Review Cycle**: Quarterly (every 3 months)
- **Last Major Update**: October 2025
- **Next Scheduled Review**: April 2025
- **Maintainer**: Development Team

## 📞 Need Help?

If you can't find what you're looking for:
1. Check [SYSTEM_DOCUMENTATION.md](SYSTEM_DOCUMENTATION.md) - the most comprehensive document
2. Search for keywords using your IDE or grep
3. Check the git history for specific feature documentation
4. Contact the development team

---

**Note**: This documentation is actively maintained. If you find outdated information, please update it and commit the changes with a note in the commit message.
