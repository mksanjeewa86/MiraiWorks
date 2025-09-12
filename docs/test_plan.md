# MiraiWorks Messaging System Test Plan

## Overview

This document outlines the comprehensive testing strategy for the MiraiWorks messaging system, covering backend unit/integration tests with pytest and frontend E2E tests with Playwright.

## Test Coverage Requirements

### 1. Backend Testing (pytest)

#### 1.1 Direct Message Service Tests
- **Test File:** `backend/tests/test_direct_message_service.py`
- **Coverage:** All CRUD operations, search, validation
- **Functions to Test:**
  - `send_message()`
  - `get_messages_with_user()`
  - `get_conversations()` 
  - `search_messages()`
  - `mark_messages_as_read()`
  - `mark_conversation_as_read()`
  - Message validation and error handling

#### 1.2 Notification Service Tests  
- **Test File:** `backend/tests/test_notification_service.py`
- **Coverage:** Email and in-app notifications
- **Functions to Test:**
  - `create_notification()`
  - `handle_new_message_notifications()`
  - `get_user_notifications()`
  - `mark_notifications_as_read()`
  - `get_unread_count()`
  - Email debouncing logic
  - Settings-based notification filtering

#### 1.3 Email Service Tests
- **Test File:** `backend/tests/test_email_service.py`
- **Coverage:** Email delivery and templates
- **Functions to Test:**
  - `send_email()`
  - `send_message_notification()`
  - `send_2fa_code()`
  - SMTP connection handling
  - Template rendering

#### 1.4 Direct Messages API Tests
- **Test File:** `backend/tests/test_direct_messages_api.py`
- **Coverage:** REST endpoints and validation
- **Endpoints to Test:**
  - `GET /api/direct_messages/conversations`
  - `GET /api/direct_messages/with/{user_id}`
  - `POST /api/direct_messages/send`
  - `POST /api/direct_messages/search`
  - `PUT /api/direct_messages/mark-read`
  - `GET /api/direct_messages/participants`
  - Role-based permissions
  - Authentication/authorization

#### 1.5 Notifications API Tests
- **Test File:** `backend/tests/test_notifications_api.py`
- **Coverage:** Notification REST endpoints
- **Endpoints to Test:**
  - `GET /api/notifications`
  - `GET /api/notifications/unread-count`
  - `PUT /api/notifications/mark-read`
  - `PUT /api/notifications/mark-all-read`

#### 1.6 WebSocket Tests
- **Test File:** `backend/tests/test_messaging_websocket.py`
- **Coverage:** Real-time messaging functionality
- **Features to Test:**
  - Connection establishment
  - Message broadcasting
  - Typing indicators
  - Read receipts
  - User presence
  - Connection management
  - Error handling

#### 1.7 Integration Tests
- **Test File:** `backend/tests/test_messaging_integration.py`
- **Coverage:** End-to-end message flow
- **Scenarios to Test:**
  - Complete message sending flow
  - Notification trigger chain
  - Search across conversations
  - Role-based message filtering
  - File upload integration

### 2. Frontend E2E Testing (Playwright)

#### 2.1 Messaging Core Functionality
- **Test File:** `frontend-nextjs/tests/e2e/messaging/core.spec.ts`
- **Scenarios:**
  - Load messages page and auto-select last conversation
  - Send text messages between users
  - Real-time message delivery
  - Message history loading
  - Scroll to latest message

#### 2.2 Search Functionality
- **Test File:** `frontend-nextjs/tests/e2e/messaging/search.spec.ts`
- **Scenarios:**
  - Search messages by content
  - Search by sender name/email
  - Search by company name
  - Highlight search results
  - Navigate to conversation from search results
  - Clear search functionality

#### 2.3 Notifications System
- **Test File:** `frontend-nextjs/tests/e2e/messaging/notifications.spec.ts`
- **Scenarios:**
  - Real-time notification display
  - Notification badge updates
  - Browser notification permissions
  - Mark notifications as read
  - Notification history
  - Email notification settings

#### 2.4 Contacts and Conversations
- **Test File:** `frontend-nextjs/tests/e2e/messaging/contacts.spec.ts`
- **Scenarios:**
  - Switch between Conversations/Contacts tabs
  - Hover effects on contact cards
  - Send message button functionality
  - Role-based contact filtering
  - Conversation list ordering

#### 2.5 File Sharing
- **Test File:** `frontend-nextjs/tests/e2e/messaging/files.spec.ts`
- **Scenarios:**
  - Upload files through attachment button
  - Display file previews and thumbnails
  - Download file attachments
  - File type validation
  - File size limits

#### 2.6 Emoji Support
- **Test File:** `frontend-nextjs/tests/e2e/messaging/emoji.spec.ts`
- **Scenarios:**
  - Open emoji picker
  - Insert emojis into messages
  - Send emoji-containing messages
  - Display emojis correctly

#### 2.7 Real-time Features
- **Test File:** `frontend-nextjs/tests/e2e/messaging/realtime.spec.ts`
- **Scenarios:**
  - WebSocket connection establishment
  - Typing indicators
  - Message read receipts
  - User online status
  - Connection resilience

## 3. Test Data and Fixtures

### 3.1 Backend Test Fixtures
- **File:** `backend/tests/conftest.py`
- **Fixtures:**
  - Database session management
  - Test user creation (multiple roles)
  - Test company setup
  - Mock email service
  - WebSocket client simulation

### 3.2 Frontend Test Fixtures
- **File:** `frontend-nextjs/tests/fixtures/messaging-fixtures.ts`
- **Fixtures:**
  - User authentication helpers
  - Message data generators
  - WebSocket mock servers
  - API response mocks
  - Test conversation setup

## 4. Test Environment Setup

### 4.1 Backend Test Environment
- **Database:** SQLite in-memory for unit tests, PostgreSQL for integration
- **Dependencies:** Mock external services (SMTP, S3, ClamAV)
- **Configuration:** Isolated test environment variables
- **Cleanup:** Automatic database cleanup between tests

### 4.2 Frontend Test Environment  
- **Browser:** Chromium, Firefox, WebKit (cross-browser)
- **Mock Services:** MSW for API mocking
- **Test Data:** Seeded test users and conversations
- **Screenshots:** Automatic failure screenshots
- **Video Recording:** For debugging complex scenarios

## 5. Performance Testing

### 5.1 Backend Performance
- **Load Testing:** Message sending under high load
- **Stress Testing:** WebSocket connection limits
- **Memory Testing:** Notification service memory usage
- **Database Performance:** Query optimization validation

### 5.2 Frontend Performance
- **Rendering:** Message list with large datasets
- **WebSocket:** Connection stability under network issues
- **Search:** Response times for large message volumes
- **Memory Leaks:** Long-running conversation sessions

## 6. Security Testing

### 6.1 Authentication & Authorization
- **Message Access Control:** Users can only access their messages
- **Role-based Permissions:** Proper role enforcement
- **CSRF Protection:** Token validation
- **Rate Limiting:** Message sending limits

### 6.2 Data Validation
- **Input Sanitization:** XSS prevention in messages
- **File Upload Security:** Malicious file detection
- **SQL Injection:** Parameter validation
- **WebSocket Security:** Connection authentication

## 7. CI/CD Integration

### 7.1 GitHub Actions Workflow
```yaml
name: Messaging System Tests
on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    services:
      postgres: # Database service
      redis: # Cache service
    steps:
      - checkout code
      - setup python
      - install dependencies
      - run pytest with coverage
      - upload coverage reports

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - checkout code  
      - setup node
      - install dependencies
      - run playwright tests
      - upload test artifacts
```

### 7.2 Coverage Requirements
- **Backend:** Minimum 85% code coverage
- **Frontend E2E:** 100% critical path coverage
- **Integration:** All API endpoints tested
- **WebSocket:** All message types covered

## 8. Test Execution Strategy

### 8.1 Development Workflow
1. **Pre-commit:** Run unit tests locally
2. **PR Creation:** Trigger full test suite
3. **Code Review:** Include test coverage analysis
4. **Merge:** All tests must pass

### 8.2 Test Categories
- **Smoke Tests:** Basic functionality (5 minutes)
- **Regression Tests:** Full test suite (15 minutes)  
- **Performance Tests:** Load testing (30 minutes)
- **Security Tests:** Penetration testing (45 minutes)

### 8.3 Test Reporting
- **Coverage Reports:** HTML and XML formats
- **Performance Metrics:** Response time trends
- **Failed Test Analysis:** Automatic issue creation
- **Test History:** Track flaky tests

## 9. Test Maintenance

### 9.1 Test Data Management
- **Seed Data:** Consistent test scenarios
- **Data Cleanup:** Prevent test pollution
- **Migration Testing:** Schema change validation
- **Backup/Restore:** Test data recovery

### 9.2 Test Code Quality
- **DRY Principles:** Reusable test utilities
- **Clear Naming:** Descriptive test names
- **Documentation:** Test case descriptions
- **Refactoring:** Regular test code maintenance

## 10. Monitoring and Alerts

### 10.1 Test Failure Alerts
- **Slack Integration:** Immediate failure notifications
- **Email Reports:** Daily test summaries
- **Dashboard:** Test health visualization
- **Trend Analysis:** Failure pattern detection

### 10.2 Test Environment Health
- **Resource Monitoring:** Memory and CPU usage
- **Service Availability:** External dependency health
- **Database Performance:** Query execution times
- **Network Latency:** API response times

## Success Criteria

✅ **Backend Tests:** 85%+ coverage, all critical paths tested
✅ **Frontend E2E:** All user journeys validated
✅ **Integration:** Message flow end-to-end tested  
✅ **Performance:** Sub-second response times
✅ **Security:** No critical vulnerabilities
✅ **Reliability:** 99.9% test success rate

This comprehensive test plan ensures the messaging system meets all functional requirements from `claude_instruction.md` with production-ready quality and reliability.