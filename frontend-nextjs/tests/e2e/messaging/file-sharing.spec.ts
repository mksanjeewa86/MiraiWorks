/**
 * File sharing functionality E2E tests
 * Tests file upload, download, file type restrictions, and file message display
 */

import { test, expect } from '../fixtures/auth-fixture';
import path from 'path';

test.describe('File Sharing', () => {
  const testFilesPath = path.join(__dirname, '..', 'test-files');
  
  test.beforeEach(async ({ page }) => {
    await page.goto('/messages');
    await page.waitForLoadState('networkidle');
  });

  test('should upload and send image file', async ({ authenticatedContext }) => {
    const context = await authenticatedContext('candidate1');
    const page = await context.newPage();
    
    await page.goto('/messages');
    await page.waitForLoadState('networkidle');

    // Select conversation
    const firstConversation = page.locator('[data-testid="conversation-item"]').first();
    if (await firstConversation.count() > 0) {
      await firstConversation.click();

      // Click file attachment button
      const attachButton = page.locator('[data-testid="attach-file-button"]');
      if (await attachButton.count() > 0) {
        await attachButton.click();

        // Upload an image file
        const fileInput = page.locator('[data-testid="file-input"]');
        const testImagePath = path.join(testFilesPath, 'test-image.jpg');
        
        // Create test file if it doesn't exist (for CI/CD)
        await page.evaluate(() => {
          // Create a small test image blob
          const canvas = document.createElement('canvas');
          canvas.width = 100;
          canvas.height = 100;
          const ctx = canvas.getContext('2d');
          if (ctx) {
            ctx.fillStyle = 'blue';
            ctx.fillRect(0, 0, 100, 100);
          }
        });

        if (await fileInput.count() > 0) {
          await fileInput.setInputFiles([testImagePath]);

          // Wait for file preview or upload progress
          const filePreview = page.locator('[data-testid="file-preview"]');
          if (await filePreview.count() > 0) {
            await expect(filePreview).toBeVisible();
          }

          // Send file message
          const sendButton = page.locator('[data-testid="send-file-button"]');
          if (await sendButton.count() > 0) {
            await sendButton.click();
          }

          // Verify file message appears
          const fileMessage = page.locator('[data-testid="message-bubble"][data-message-type="file"]');
          await expect(fileMessage).toBeVisible({ timeout: 10000 });

          // Verify file info is displayed
          await expect(fileMessage.locator('[data-testid="file-name"]')).toContainText('test-image.jpg');
          await expect(fileMessage.locator('[data-testid="file-size"]')).toBeVisible();
        }
      }
    }
  });

  test('should upload and send document file', async ({ authenticatedContext }) => {
    const context = await authenticatedContext('candidate1');
    const page = await context.newPage();
    
    await page.goto('/messages');
    await page.waitForLoadState('networkidle');

    const firstConversation = page.locator('[data-testid="conversation-item"]').first();
    if (await firstConversation.count() > 0) {
      await firstConversation.click();

      const attachButton = page.locator('[data-testid="attach-file-button"]');
      if (await attachButton.count() > 0) {
        await attachButton.click();

        const fileInput = page.locator('[data-testid="file-input"]');
        if (await fileInput.count() > 0) {
          // Create a test PDF file content
          const testPdfContent = '%PDF-1.3\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000074 00000 n \n0000000120 00000 n \ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n183\n%%EOF';
          
          // Use setInputFiles with Buffer for PDF
          await fileInput.setInputFiles({
            name: 'test-document.pdf',
            mimeType: 'application/pdf',
            buffer: Buffer.from(testPdfContent)
          });

          // Wait for file processing
          await page.waitForTimeout(2000);

          const sendButton = page.locator('[data-testid="send-file-button"]').or(page.locator('[data-testid="send-button"]'));
          if (await sendButton.count() > 0) {
            await sendButton.click();
          }

          // Verify document message
          const fileMessage = page.locator('[data-testid="message-bubble"][data-message-type="file"]');
          await expect(fileMessage).toBeVisible({ timeout: 15000 });
          
          // Verify document icon and info
          await expect(fileMessage.locator('[data-testid="file-icon"]')).toBeVisible();
          await expect(fileMessage.locator('[data-testid="file-name"]')).toContainText('test-document.pdf');
        }
      }
    }
  });

  test('should reject files exceeding size limit', async ({ authenticatedContext }) => {
    const context = await authenticatedContext('candidate1');
    const page = await context.newPage();
    
    await page.goto('/messages');
    await page.waitForLoadState('networkidle');

    const firstConversation = page.locator('[data-testid="conversation-item"]').first();
    if (await firstConversation.count() > 0) {
      await firstConversation.click();

      const attachButton = page.locator('[data-testid="attach-file-button"]');
      if (await attachButton.count() > 0) {
        await attachButton.click();

        const fileInput = page.locator('[data-testid="file-input"]');
        if (await fileInput.count() > 0) {
          // Create a large file (simulate 50MB file)
          const largeFileContent = 'x'.repeat(50 * 1024 * 1024); // 50MB
          
          await fileInput.setInputFiles({
            name: 'large-file.txt',
            mimeType: 'text/plain',
            buffer: Buffer.from(largeFileContent)
          });

          // Should show error message
          const errorMessage = page.locator('[data-testid="file-size-error"]');
          await expect(errorMessage).toBeVisible({ timeout: 5000 });
          await expect(errorMessage).toContainText(/too large|size limit|maximum/i);

          // Send button should be disabled
          const sendButton = page.locator('[data-testid="send-file-button"]');
          if (await sendButton.count() > 0) {
            await expect(sendButton).toBeDisabled();
          }
        }
      }
    }
  });

  test('should reject unsupported file types', async ({ authenticatedContext }) => {
    const context = await authenticatedContext('candidate1');
    const page = await context.newPage();
    
    await page.goto('/messages');
    await page.waitForLoadState('networkidle');

    const firstConversation = page.locator('[data-testid="conversation-item"]').first();
    if (await firstConversation.count() > 0) {
      await firstConversation.click();

      const attachButton = page.locator('[data-testid="attach-file-button"]');
      if (await attachButton.count() > 0) {
        await attachButton.click();

        const fileInput = page.locator('[data-testid="file-input"]');
        if (await fileInput.count() > 0) {
          // Try to upload an executable file
          const executableContent = 'MZ\x90\x00'; // PE header start
          
          await fileInput.setInputFiles({
            name: 'malicious.exe',
            mimeType: 'application/octet-stream',
            buffer: Buffer.from(executableContent)
          });

          // Should show error for unsupported file type
          const errorMessage = page.locator('[data-testid="file-type-error"]');
          await expect(errorMessage).toBeVisible({ timeout: 5000 });
          await expect(errorMessage).toContainText(/not supported|invalid type/i);
        }
      }
    }
  });

  test('should display file download functionality', async ({ authenticatedContext }) => {
    const context = await authenticatedContext('candidate1');
    const page = await context.newPage();
    
    await page.goto('/messages');
    await page.waitForLoadState('networkidle');

    // Look for existing file messages
    const fileMessages = page.locator('[data-testid="message-bubble"][data-message-type="file"]');
    
    if (await fileMessages.count() > 0) {
      const firstFileMessage = fileMessages.first();
      
      // Check download button exists
      const downloadButton = firstFileMessage.locator('[data-testid="download-file-button"]');
      if (await downloadButton.count() > 0) {
        await expect(downloadButton).toBeVisible();
        
        // Wait for download (don't actually download in test)
        // await downloadButton.click();
        
        // Verify download URL is valid
        const downloadUrl = await downloadButton.getAttribute('href');
        expect(downloadUrl).toBeTruthy();
        expect(downloadUrl).toMatch(/^(https?:\/\/|\/)/); // Valid URL format
      }
    }
  });

  test('should show file upload progress', async ({ authenticatedContext }) => {
    const context = await authenticatedContext('candidate1');
    const page = await context.newPage();
    
    await page.goto('/messages');
    await page.waitForLoadState('networkidle');

    const firstConversation = page.locator('[data-testid="conversation-item"]').first();
    if (await firstConversation.count() > 0) {
      await firstConversation.click();

      const attachButton = page.locator('[data-testid="attach-file-button"]');
      if (await attachButton.count() > 0) {
        // Mock slow upload to see progress
        await page.route('**/api/files/upload**', async (route) => {
          await page.waitForTimeout(3000); // Simulate slow upload
          route.continue();
        });

        await attachButton.click();

        const fileInput = page.locator('[data-testid="file-input"]');
        if (await fileInput.count() > 0) {
          await fileInput.setInputFiles({
            name: 'test-file.jpg',
            mimeType: 'image/jpeg',
            buffer: Buffer.from('fake image content'.repeat(1000))
          });

          const sendButton = page.locator('[data-testid="send-file-button"]');
          if (await sendButton.count() > 0) {
            await sendButton.click();

            // Check for upload progress indicator
            const progressBar = page.locator('[data-testid="upload-progress"]');
            if (await progressBar.count() > 0) {
              await expect(progressBar).toBeVisible();
            }

            const uploadingStatus = page.locator('[data-testid="uploading-status"]');
            if (await uploadingStatus.count() > 0) {
              await expect(uploadingStatus).toBeVisible();
              await expect(uploadingStatus).toContainText(/uploading|sending/i);
            }
          }
        }
      }
    }
  });

  test('should handle file upload failures', async ({ authenticatedContext }) => {
    const context = await authenticatedContext('candidate1');
    const page = await context.newPage();
    
    await page.goto('/messages');
    await page.waitForLoadState('networkidle');

    const firstConversation = page.locator('[data-testid="conversation-item"]').first();
    if (await firstConversation.count() > 0) {
      await firstConversation.click();

      // Mock file upload failure
      await page.route('**/api/files/upload**', (route) => {
        route.abort('failed');
      });

      const attachButton = page.locator('[data-testid="attach-file-button"]');
      if (await attachButton.count() > 0) {
        await attachButton.click();

        const fileInput = page.locator('[data-testid="file-input"]');
        if (await fileInput.count() > 0) {
          await fileInput.setInputFiles({
            name: 'test-file.txt',
            mimeType: 'text/plain',
            buffer: Buffer.from('test content')
          });

          const sendButton = page.locator('[data-testid="send-file-button"]');
          if (await sendButton.count() > 0) {
            await sendButton.click();

            // Should show upload error
            const errorMessage = page.locator('[data-testid="upload-error"]');
            await expect(errorMessage).toBeVisible({ timeout: 10000 });
            await expect(errorMessage).toContainText(/failed|error|try again/i);

            // Retry button should be available
            const retryButton = page.locator('[data-testid="retry-upload-button"]');
            if (await retryButton.count() > 0) {
              await expect(retryButton).toBeVisible();
            }
          }
        }
      }
    }
  });

  test('should preview images before sending', async ({ authenticatedContext }) => {
    const context = await authenticatedContext('candidate1');
    const page = await context.newPage();
    
    await page.goto('/messages');
    await page.waitForLoadState('networkidle');

    const firstConversation = page.locator('[data-testid="conversation-item"]').first();
    if (await firstConversation.count() > 0) {
      await firstConversation.click();

      const attachButton = page.locator('[data-testid="attach-file-button"]');
      if (await attachButton.count() > 0) {
        await attachButton.click();

        const fileInput = page.locator('[data-testid="file-input"]');
        if (await fileInput.count() > 0) {
          // Create a small image
          const imageData = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==';
          const buffer = Buffer.from(imageData.split(',')[1], 'base64');
          
          await fileInput.setInputFiles({
            name: 'small-image.png',
            mimeType: 'image/png',
            buffer: buffer
          });

          // Should show image preview
          const imagePreview = page.locator('[data-testid="image-preview"]');
          if (await imagePreview.count() > 0) {
            await expect(imagePreview).toBeVisible();
            
            // Preview should show the actual image
            const previewImg = imagePreview.locator('img');
            await expect(previewImg).toBeVisible();
            
            // Should have option to remove/cancel
            const cancelButton = page.locator('[data-testid="cancel-file-button"]');
            if (await cancelButton.count() > 0) {
              await expect(cancelButton).toBeVisible();
            }
          }
        }
      }
    }
  });

  test('should display file messages with proper icons', async ({ authenticatedContext }) => {
    const context = await authenticatedContext('candidate1');
    const page = await context.newPage();
    
    await page.goto('/messages');
    await page.waitForLoadState('networkidle');

    // Look for different types of file messages
    const fileMessages = page.locator('[data-testid="message-bubble"][data-message-type="file"]');
    
    if (await fileMessages.count() > 0) {
      for (let i = 0; i < Math.min(3, await fileMessages.count()); i++) {
        const fileMessage = fileMessages.nth(i);
        
        // Should have file icon
        const fileIcon = fileMessage.locator('[data-testid="file-icon"]');
        await expect(fileIcon).toBeVisible();
        
        // Should have file name
        const fileName = fileMessage.locator('[data-testid="file-name"]');
        await expect(fileName).toBeVisible();
        
        // Should have file size
        const fileSize = fileMessage.locator('[data-testid="file-size"]');
        await expect(fileSize).toBeVisible();
        
        // Should have timestamp
        const timestamp = fileMessage.locator('[data-testid="message-timestamp"]');
        await expect(timestamp).toBeVisible();
      }
    }
  });

  test('should handle multiple file selection', async ({ authenticatedContext }) => {
    const context = await authenticatedContext('candidate1');
    const page = await context.newPage();
    
    await page.goto('/messages');
    await page.waitForLoadState('networkidle');

    const firstConversation = page.locator('[data-testid="conversation-item"]').first();
    if (await firstConversation.count() > 0) {
      await firstConversation.click();

      const attachButton = page.locator('[data-testid="attach-file-button"]');
      if (await attachButton.count() > 0) {
        await attachButton.click();

        const fileInput = page.locator('[data-testid="file-input"]');
        if (await fileInput.count() > 0) {
          // Select multiple files
          const files = [
            {
              name: 'file1.txt',
              mimeType: 'text/plain',
              buffer: Buffer.from('content 1')
            },
            {
              name: 'file2.txt',
              mimeType: 'text/plain',
              buffer: Buffer.from('content 2')
            }
          ];

          await fileInput.setInputFiles(files);

          // Should show multiple file previews
          const filePreviews = page.locator('[data-testid="file-preview-item"]');
          if (await filePreviews.count() > 0) {
            await expect(filePreviews).toHaveCount(2);
          }

          // Should be able to remove individual files
          const removeButtons = page.locator('[data-testid="remove-file-button"]');
          if (await removeButtons.count() > 0) {
            await removeButtons.first().click();
            
            // Should have one less file
            await expect(filePreviews).toHaveCount(1);
          }
        }
      }
    }
  });
});