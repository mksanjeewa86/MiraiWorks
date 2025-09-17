/**
 * Scenario Test: File Download Permission System
 *
 * This test simulates the complete user workflow for uploading files,
 * sending them in messages, and downloading them with proper permissions.
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { rest } from 'msw';
import { setupServer } from 'msw/node';
import MessagesPage from '../app/messages/page';

// Mock data
const mockUsers = {
  sender: {
    id: 1,
    email: 'sender@example.com',
    first_name: 'John',
    last_name: 'Sender',
    company_id: 1,
    roles: [{ role: { name: 'candidate' } }]
  },
  recipient: {
    id: 2,
    email: 'recipient@example.com',
    first_name: 'Jane',
    last_name: 'Recipient',
    company_id: 1,
    roles: [{ role: { name: 'company_admin' } }]
  }
};

const mockFileUploadResponse = {
  success: true,
  data: {
    file_url: '/api/files/download/message-attachments/1/2025/09/test-file-123.pdf',
    file_name: 'test-document.pdf',
    file_size: 1024000,
    file_type: 'application/pdf',
    s3_key: 'message-attachments/1/2025/09/test-file-123.pdf'
  }
};

const mockConversations = [
  {
    id: 1,
    participant: mockUsers.recipient,
    last_message: {
      id: 1,
      content: 'File: test-document.pdf',
      type: 'file',
      file_url: '/api/files/download/message-attachments/1/2025/09/test-file-123.pdf',
      file_name: 'test-document.pdf',
      file_size: 1024000,
      file_type: 'application/pdf',
      sender_id: 1,
      recipient_id: 2,
      created_at: '2025-09-17T10:00:00Z'
    },
    unread_count: 1
  }
];

const mockMessages = [
  {
    id: 1,
    content: 'File: test-document.pdf',
    type: 'file',
    file_url: '/api/files/download/message-attachments/1/2025/09/test-file-123.pdf',
    file_name: 'test-document.pdf',
    file_size: 1024000,
    file_type: 'application/pdf',
    sender_id: 1,
    recipient_id: 2,
    created_at: '2025-09-17T10:00:00Z'
  }
];

// Create MSW server
const server = setupServer(
  // Auth endpoints
  rest.get('/api/auth/me', (req, res, ctx) => {
    const authHeader = req.headers.get('Authorization');
    if (!authHeader?.includes('Bearer')) {
      return res(ctx.status(401), ctx.json({ detail: 'Unauthorized' }));
    }

    // Simulate different users based on token
    const isRecipient = authHeader.includes('recipient-token');
    return res(ctx.json({
      user: isRecipient ? mockUsers.recipient : mockUsers.sender
    }));
  }),

  // File upload endpoint
  rest.post('/api/files/upload', (req, res, ctx) => {
    return res(ctx.json(mockFileUploadResponse));
  }),

  // File download endpoint with permission check
  rest.get('/api/files/download/:filePath*', (req, res, ctx) => {
    const authHeader = req.headers.get('Authorization');
    if (!authHeader?.includes('Bearer')) {
      return res(ctx.status(401), ctx.json({ detail: 'Unauthorized' }));
    }

    const filePath = req.params.filePath;
    const isRecipient = authHeader.includes('recipient-token');

    // Simulate permission check
    if (filePath === 'message-attachments/1/2025/09/test-file-123.pdf') {
      // Both sender and recipient should have access
      return res(ctx.status(200), ctx.body('Mock file content'));
    }

    // File not found or no permission
    return res(ctx.status(403), ctx.json({ detail: 'No permission to access this file' }));
  }),

  // Conversations endpoint
  rest.get('/api/direct-messages/conversations', (req, res, ctx) => {
    return res(ctx.json({
      success: true,
      data: { conversations: mockConversations }
    }));
  }),

  // Messages endpoint
  rest.get('/api/direct-messages/:conversationId', (req, res, ctx) => {
    return res(ctx.json({
      success: true,
      data: { messages: mockMessages }
    }));
  }),

  // Send message endpoint
  rest.post('/api/direct-messages/send', (req, res, ctx) => {
    return res(ctx.json({
      success: true,
      data: mockMessages[0]
    }));
  })
);

// Mock localStorage
const mockLocalStorage = {
  getItem: jest.fn((key) => {
    if (key === 'accessToken') return 'mock-sender-token';
    return null;
  }),
  setItem: jest.fn(),
  removeItem: jest.fn(),
};

Object.defineProperty(window, 'localStorage', {
  value: mockLocalStorage,
  writable: true,
});

// Mock fetch for file downloads
global.fetch = jest.fn();

describe('File Download Permission Scenario', () => {
  beforeAll(() => server.listen());
  afterEach(() => {
    server.resetHandlers();
    jest.clearAllMocks();
  });
  afterAll(() => server.close());

  describe('Sender Perspective', () => {
    beforeEach(() => {
      mockLocalStorage.getItem.mockReturnValue('mock-sender-token');
    });

    test('Sender can upload file, send message, and download their own file', async () => {
      const user = userEvent.setup();

      render(<MessagesPage />);

      // Wait for initial load
      await waitFor(() => {
        expect(screen.getByText(/messages/i)).toBeInTheDocument();
      });

      // 1. Upload a file
      const fileInput = screen.getByRole('button', { name: /attach file/i });
      const testFile = new File(['test content'], 'test-document.pdf', { type: 'application/pdf' });

      await user.click(fileInput);

      // Mock file input change
      const hiddenFileInput = screen.getByLabelText(/attach file/i, { hidden: true });
      await user.upload(hiddenFileInput, testFile);

      // 2. Verify file appears in attachment preview
      await waitFor(() => {
        expect(screen.getByText('test-document.pdf')).toBeInTheDocument();
        expect(screen.getByText('1 file(s) attached')).toBeInTheDocument();
      });

      // 3. Send the message with file
      const sendButton = screen.getByRole('button', { name: /send/i });
      await user.click(sendButton);

      // 4. Verify message appears in conversation
      await waitFor(() => {
        expect(screen.getByText('File: test-document.pdf')).toBeInTheDocument();
      });

      // 5. Try to download the file (sender should have access)
      const downloadButton = screen.getByRole('button', { name: /download/i });

      // Mock successful fetch response
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        blob: () => Promise.resolve(new Blob(['mock file content'])),
        headers: new Headers({
          'content-disposition': 'attachment; filename="test-document.pdf"'
        })
      });

      await user.click(downloadButton);

      // 6. Verify download was attempted with correct authorization
      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith(
          expect.stringContaining('/api/files/download/message-attachments/1/2025/09/test-file-123.pdf'),
          expect.objectContaining({
            headers: expect.objectContaining({
              'Authorization': 'Bearer mock-sender-token'
            })
          })
        );
      });
    });
  });

  describe('Recipient Perspective', () => {
    beforeEach(() => {
      // Switch to recipient token
      mockLocalStorage.getItem.mockReturnValue('mock-recipient-token');

      // Update server to return recipient user
      server.use(
        rest.get('/api/auth/me', (req, res, ctx) => {
          return res(ctx.json({ user: mockUsers.recipient }));
        })
      );
    });

    test('Recipient can download files sent to them', async () => {
      const user = userEvent.setup();

      render(<MessagesPage />);

      // Wait for messages to load
      await waitFor(() => {
        expect(screen.getByText('File: test-document.pdf')).toBeInTheDocument();
      });

      // Try to download the file (recipient should have access)
      const downloadButton = screen.getByRole('button', { name: /download/i });

      // Mock successful fetch response
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        blob: () => Promise.resolve(new Blob(['mock file content'])),
        headers: new Headers({
          'content-disposition': 'attachment; filename="test-document.pdf"'
        })
      });

      await user.click(downloadButton);

      // Verify download was attempted with recipient authorization
      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith(
          expect.stringContaining('/api/files/download/message-attachments/1/2025/09/test-file-123.pdf'),
          expect.objectContaining({
            headers: expect.objectContaining({
              'Authorization': 'Bearer mock-recipient-token'
            })
          })
        );
      });
    });

    test('Recipient cannot download files they have no permission for', async () => {
      const user = userEvent.setup();

      // Mock a message with a file the recipient shouldn't access
      const unauthorizedMessage = {
        ...mockMessages[0],
        file_url: '/api/files/download/private/other-user-file.pdf'
      };

      server.use(
        rest.get('/api/direct-messages/:conversationId', (req, res, ctx) => {
          return res(ctx.json({
            success: true,
            data: { messages: [unauthorizedMessage] }
          }));
        }),

        rest.get('/api/files/download/private/other-user-file.pdf', (req, res, ctx) => {
          return res(ctx.status(403), ctx.json({ detail: 'No permission to access this file' }));
        })
      );

      render(<MessagesPage />);

      // Wait for messages to load
      await waitFor(() => {
        expect(screen.getByText('File: test-document.pdf')).toBeInTheDocument();
      });

      const downloadButton = screen.getByRole('button', { name: /download/i });

      // Mock 403 response
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 403,
        json: () => Promise.resolve({ detail: 'No permission to access this file' })
      });

      await user.click(downloadButton);

      // Verify error handling
      await waitFor(() => {
        expect(screen.getByText(/failed to download file/i)).toBeInTheDocument();
      });
    });
  });

  describe('Unauthorized Access', () => {
    test('Unauthenticated users cannot download files', async () => {
      mockLocalStorage.getItem.mockReturnValue(null);

      const user = userEvent.setup();

      render(<MessagesPage />);

      // Since user is not authenticated, they should be redirected or see login
      await waitFor(() => {
        expect(screen.getByText(/please log in/i)).toBeInTheDocument();
      });
    });
  });

  describe('Multiple File Upload Scenario', () => {
    test('Can upload multiple files (max 5) and download them individually', async () => {
      const user = userEvent.setup();

      render(<MessagesPage />);

      await waitFor(() => {
        expect(screen.getByText(/messages/i)).toBeInTheDocument();
      });

      // Upload multiple files
      const files = [
        new File(['content1'], 'file1.pdf', { type: 'application/pdf' }),
        new File(['content2'], 'file2.pdf', { type: 'application/pdf' }),
        new File(['content3'], 'file3.pdf', { type: 'application/pdf' })
      ];

      const fileInput = screen.getByRole('button', { name: /attach file/i });
      await user.click(fileInput);

      const hiddenFileInput = screen.getByLabelText(/attach file/i, { hidden: true });
      await user.upload(hiddenFileInput, files);

      // Verify multiple files are attached
      await waitFor(() => {
        expect(screen.getByText('3 file(s) attached')).toBeInTheDocument();
        expect(screen.getByText('file1.pdf')).toBeInTheDocument();
        expect(screen.getByText('file2.pdf')).toBeInTheDocument();
        expect(screen.getByText('file3.pdf')).toBeInTheDocument();
      });

      // Test individual file removal
      const removeButtons = screen.getAllByRole('button', { name: /remove this file/i });
      await user.click(removeButtons[0]);

      await waitFor(() => {
        expect(screen.getByText('2 file(s) attached')).toBeInTheDocument();
        expect(screen.queryByText('file1.pdf')).not.toBeInTheDocument();
      });

      // Test remove all files
      const removeAllButton = screen.getByRole('button', { name: /remove all/i });
      await user.click(removeAllButton);

      await waitFor(() => {
        expect(screen.queryByText('file(s) attached')).not.toBeInTheDocument();
      });
    });

    test('Cannot upload more than 5 files', async () => {
      const user = userEvent.setup();

      render(<MessagesPage />);

      await waitFor(() => {
        expect(screen.getByText(/messages/i)).toBeInTheDocument();
      });

      // Try to upload 6 files
      const files = Array.from({ length: 6 }, (_, i) =>
        new File([`content${i + 1}`], `file${i + 1}.pdf`, { type: 'application/pdf' })
      );

      const fileInput = screen.getByRole('button', { name: /attach file/i });
      await user.click(fileInput);

      const hiddenFileInput = screen.getByLabelText(/attach file/i, { hidden: true });
      await user.upload(hiddenFileInput, files);

      // Should show error message
      await waitFor(() => {
        expect(screen.getByText(/you can only attach up to 5 files/i)).toBeInTheDocument();
      });
    });
  });
});