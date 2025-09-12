# Test Files Directory

This directory contains test files used by E2E tests for file upload/download functionality.

## Files Created During Tests

The following files are dynamically created during test execution:

- `test-image.jpg` - Small test image file for image upload tests
- `test-document.pdf` - Sample PDF document for document upload tests  
- `large-file.txt` - Large file for testing size limit validation
- `test-file.txt` - Generic text file for basic upload tests

## File Type Coverage

Tests cover the following file types:

### Supported Types
- Images: JPG, PNG, GIF, WebP
- Documents: PDF, DOC, DOCX, TXT, RTF
- Archives: ZIP, RAR (if enabled)
- Spreadsheets: XLS, XLSX, CSV

### Restricted Types  
- Executables: EXE, BAT, CMD, MSI
- Scripts: JS, VBS, PS1 (unless specifically allowed)
- System files: DLL, SYS

## Size Limits

- Maximum file size: 25MB (configurable)
- Individual file limit applies to each file in multi-file uploads
- Total upload limit may apply for batch uploads

## Test Scenarios

1. **Valid Uploads**: Supported file types within size limits
2. **Size Validation**: Files exceeding maximum size limits  
3. **Type Validation**: Unsupported or potentially dangerous file types
4. **Multiple Files**: Batch upload functionality
5. **Upload Progress**: Progress indicators and cancellation
6. **Error Handling**: Network failures, server errors, timeout scenarios
7. **Preview**: Image previews before sending
8. **Download**: File download and viewing functionality

## Notes

- Test files are created programmatically to ensure consistent test environment
- Files are cleaned up after test execution (handled by Playwright)
- Real file I/O is mocked in unit tests, actual files used in E2E tests
- File content is minimal to keep test execution fast