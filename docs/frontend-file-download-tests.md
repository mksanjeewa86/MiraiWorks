# Frontend File Download Permission Tests

This directory contains scenario tests for the file download permission system.

## Test Files

- `file-download-scenario.test.tsx` - Comprehensive end-to-end test scenarios for file upload, messaging, and download permissions

## Running Tests

```bash
# Install dependencies first
npm install

# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run with coverage
npm run test:coverage

# Run only the file download scenario test
npm test -- file-download-scenario.test.tsx
```

## Test Scenarios Covered

### 1. Sender Perspective
- ✅ Upload file successfully
- ✅ Send message with file attachment
- ✅ Download own uploaded file
- ✅ Proper authorization headers sent

### 2. Recipient Perspective
- ✅ View received file messages
- ✅ Download files sent to them
- ✅ Proper permission validation

### 3. Permission Security
- ✅ Cannot download files without permission
- ✅ Proper 403 error handling
- ✅ Authentication required

### 4. Multiple File Handling
- ✅ Upload multiple files (max 5)
- ✅ Individual file removal
- ✅ Bulk file removal
- ✅ File limit enforcement

## Mock Server Setup

Tests use MSW (Mock Service Worker) to simulate the backend API:

- File upload endpoint with success response
- File download endpoint with permission checking
- Authentication endpoints
- Message sending and retrieval

## Test Data

All tests use realistic mock data that matches the actual API responses:

```typescript
const mockFileUploadResponse = {
  success: true,
  data: {
    file_url: '/api/files/download/message-attachments/1/2025/09/test-file-123.pdf',
    file_name: 'test-document.pdf',
    file_size: 1024000,
    file_type: 'application/pdf'
  }
}
```

## Error Scenarios Tested

- Unauthorized file access (403)
- File not found (404)
- Network errors
- Invalid file types
- File size limits
- Authentication failures

## Integration with Backend

These tests verify that the frontend correctly:

1. Sends proper Authorization headers
2. Handles file upload responses
3. Manages file permissions
4. Displays appropriate error messages
5. Supports multiple file workflows

The tests complement the backend permission tests to ensure end-to-end functionality.