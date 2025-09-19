/**
 * Frontend Tests for Account Activation Page
 * Tests user interactions, form validation, and API integration
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { useRouter, useParams } from 'next/navigation';
import '@testing-library/jest-dom';

// Mock Next.js router
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
  useParams: jest.fn(),
}));

// Mock fetch
global.fetch = jest.fn();

// Import component after mocks
import ActivateAccountPage from '../[userId]/page';

describe('ActivateAccountPage', () => {
  const mockRouter = {
    push: jest.fn(),
    back: jest.fn(),
  };

  const mockParams = {
    userId: '123',
  };

  beforeEach(() => {
    (useRouter as jest.Mock).mockReturnValue(mockRouter);
    (useParams as jest.Mock).mockReturnValue(mockParams);
    (fetch as jest.Mock).mockClear();
    mockRouter.push.mockClear();
    jest.clearAllMocks();
  });

  describe('Form Rendering', () => {
    test('renders all required form fields', () => {
      render(<ActivateAccountPage />);

      expect(screen.getByLabelText(/email address/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/temporary password/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/new password/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/confirm new password/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /activate account/i })).toBeInTheDocument();
    });

    test('renders password visibility toggles', () => {
      render(<ActivateAccountPage />);

      const passwordToggleButtons = screen.getAllByTitle(/show password|hide password/i);
      expect(passwordToggleButtons).toHaveLength(3); // temp, new, confirm passwords
    });

    test('renders helpful tip text', () => {
      render(<ActivateAccountPage />);

      expect(screen.getByText(/use the eye icon to show your password/i)).toBeInTheDocument();
    });

    test('has proper autocomplete settings', () => {
      render(<ActivateAccountPage />);

      const emailInput = screen.getByLabelText(/email address/i);
      const tempPasswordInput = screen.getByLabelText(/temporary password/i);
      const newPasswordInput = screen.getByLabelText(/new password/i);
      const confirmPasswordInput = screen.getByLabelText(/confirm new password/i);

      expect(emailInput).toHaveAttribute('autoComplete', 'off');
      expect(tempPasswordInput).toHaveAttribute('autoComplete', 'off');
      expect(newPasswordInput).toHaveAttribute('autoComplete', 'off');
      expect(confirmPasswordInput).toHaveAttribute('autoComplete', 'off');
    });
  });

  describe('Password Visibility Toggle', () => {
    test('toggles temporary password visibility', async () => {
      const user = userEvent.setup();
      render(<ActivateAccountPage />);

      const passwordInput = screen.getByLabelText(/temporary password/i);
      const toggleButton = passwordInput.parentElement?.querySelector('button');

      expect(passwordInput).toHaveAttribute('type', 'password');

      if (toggleButton) {
        await user.click(toggleButton);
        expect(passwordInput).toHaveAttribute('type', 'text');

        await user.click(toggleButton);
        expect(passwordInput).toHaveAttribute('type', 'password');
      }
    });

    test('toggles new password visibility', async () => {
      const user = userEvent.setup();
      render(<ActivateAccountPage />);

      const passwordInput = screen.getByLabelText(/new password/i);
      const toggleButton = passwordInput.parentElement?.querySelector('button');

      expect(passwordInput).toHaveAttribute('type', 'password');

      if (toggleButton) {
        await user.click(toggleButton);
        expect(passwordInput).toHaveAttribute('type', 'text');
      }
    });

    test('toggles confirm password visibility', async () => {
      const user = userEvent.setup();
      render(<ActivateAccountPage />);

      const passwordInput = screen.getByLabelText(/confirm new password/i);
      const toggleButton = passwordInput.parentElement?.querySelector('button');

      expect(passwordInput).toHaveAttribute('type', 'password');

      if (toggleButton) {
        await user.click(toggleButton);
        expect(passwordInput).toHaveAttribute('type', 'text');
      }
    });
  });

  describe('Form Validation', () => {
    test('shows error when passwords do not match', async () => {
      const user = userEvent.setup();
      render(<ActivateAccountPage />);

      // Fill form with mismatched passwords
      await user.type(screen.getByLabelText(/email address/i), 'test@example.com');
      await user.type(screen.getByLabelText(/temporary password/i), 'TempPass123');
      await user.type(screen.getByLabelText(/new password/i), 'NewPassword123');
      await user.type(screen.getByLabelText(/confirm new password/i), 'DifferentPassword123');

      const submitButton = screen.getByRole('button', { name: /activate account/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/new passwords do not match/i)).toBeInTheDocument();
      });
    });

    test('shows error when new password is too short', async () => {
      const user = userEvent.setup();
      render(<ActivateAccountPage />);

      // Fill form with short password
      await user.type(screen.getByLabelText(/email address/i), 'test@example.com');
      await user.type(screen.getByLabelText(/temporary password/i), 'TempPass123');
      await user.type(screen.getByLabelText(/new password/i), 'short');
      await user.type(screen.getByLabelText(/confirm new password/i), 'short');

      const submitButton = screen.getByRole('button', { name: /activate account/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/must be at least 8 characters/i)).toBeInTheDocument();
      });
    });

    test('prevents submission with empty fields', async () => {
      const user = userEvent.setup();
      render(<ActivateAccountPage />);

      const submitButton = screen.getByRole('button', { name: /activate account/i });
      await user.click(submitButton);

      // Should not make API call with empty fields
      expect(fetch).not.toHaveBeenCalled();
    });
  });

  describe('API Integration', () => {
    test('makes correct API call on successful form submission', async () => {
      const user = userEvent.setup();
      const mockResponse = {
        success: true,
        message: 'Account activated successfully',
        access_token: 'fake-access-token',
        refresh_token: 'fake-refresh-token',
        user: { id: 123, email: 'test@example.com' }
      };

      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      render(<ActivateAccountPage />);

      // Fill valid form data
      await user.type(screen.getByLabelText(/email address/i), 'test@example.com');
      await user.type(screen.getByLabelText(/temporary password/i), 'TempPass123');
      await user.type(screen.getByLabelText(/new password/i), 'NewPassword123');
      await user.type(screen.getByLabelText(/confirm new password/i), 'NewPassword123');

      const submitButton = screen.getByRole('button', { name: /activate account/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(fetch).toHaveBeenCalledWith('http://localhost:8000/api/auth/activate', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            userId: 123,
            email: 'test@example.com',
            temporaryPassword: 'TempPass123',
            newPassword: 'NewPassword123',
          }),
        });
      });
    });

    test('displays success message and redirects on successful activation', async () => {
      const user = userEvent.setup();
      const mockResponse = {
        success: true,
        message: 'Account activated successfully',
        access_token: 'fake-access-token',
        refresh_token: 'fake-refresh-token',
        user: { id: 123, email: 'test@example.com' }
      };

      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      render(<ActivateAccountPage />);

      // Fill and submit form
      await user.type(screen.getByLabelText(/email address/i), 'test@example.com');
      await user.type(screen.getByLabelText(/temporary password/i), 'TempPass123');
      await user.type(screen.getByLabelText(/new password/i), 'NewPassword123');
      await user.type(screen.getByLabelText(/confirm new password/i), 'NewPassword123');

      const submitButton = screen.getByRole('button', { name: /activate account/i });
      await user.click(submitButton);

      // Should show success message
      await waitFor(() => {
        expect(screen.getByText(/account activated!/i)).toBeInTheDocument();
        expect(screen.getByText(/redirecting to dashboard/i)).toBeInTheDocument();
      });

      // Should redirect after delay
      await waitFor(() => {
        expect(mockRouter.push).toHaveBeenCalledWith('/dashboard');
      }, { timeout: 3000 });
    });

    test('displays error message on API failure', async () => {
      const user = userEvent.setup();
      const mockErrorResponse = {
        detail: 'Invalid temporary password'
      };

      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        json: async () => mockErrorResponse,
      });

      render(<ActivateAccountPage />);

      // Fill and submit form
      await user.type(screen.getByLabelText(/email address/i), 'test@example.com');
      await user.type(screen.getByLabelText(/temporary password/i), 'WrongPassword123');
      await user.type(screen.getByLabelText(/new password/i), 'NewPassword123');
      await user.type(screen.getByLabelText(/confirm new password/i), 'NewPassword123');

      const submitButton = screen.getByRole('button', { name: /activate account/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/invalid temporary password/i)).toBeInTheDocument();
      });
    });

    test('displays detailed error tips for invalid temporary password', async () => {
      const user = userEvent.setup();
      const mockErrorResponse = {
        detail: 'Invalid temporary password'
      };

      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        json: async () => mockErrorResponse,
      });

      render(<ActivateAccountPage />);

      // Fill and submit form
      await user.type(screen.getByLabelText(/email address/i), 'test@example.com');
      await user.type(screen.getByLabelText(/temporary password/i), 'WrongPassword123');
      await user.type(screen.getByLabelText(/new password/i), 'NewPassword123');
      await user.type(screen.getByLabelText(/confirm new password/i), 'NewPassword123');

      const submitButton = screen.getByRole('button', { name: /activate account/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/troubleshooting tips/i)).toBeInTheDocument();
        expect(screen.getByText(/use the eye icon to show your password/i)).toBeInTheDocument();
        expect(screen.getByText(/check for extra spaces/i)).toBeInTheDocument();
        expect(screen.getByText(/passwords are case-sensitive/i)).toBeInTheDocument();
      });
    });

    test('stores tokens in localStorage on successful activation', async () => {
      const user = userEvent.setup();
      const mockResponse = {
        success: true,
        access_token: 'fake-access-token',
        refresh_token: 'fake-refresh-token',
        user: { id: 123, email: 'test@example.com' }
      };

      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      // Mock localStorage
      const localStorageMock = {
        setItem: jest.fn(),
      };
      Object.defineProperty(window, 'localStorage', {
        value: localStorageMock
      });

      render(<ActivateAccountPage />);

      // Fill and submit form
      await user.type(screen.getByLabelText(/email address/i), 'test@example.com');
      await user.type(screen.getByLabelText(/temporary password/i), 'TempPass123');
      await user.type(screen.getByLabelText(/new password/i), 'NewPassword123');
      await user.type(screen.getByLabelText(/confirm new password/i), 'NewPassword123');

      const submitButton = screen.getByRole('button', { name: /activate account/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(localStorageMock.setItem).toHaveBeenCalledWith('accessToken', 'fake-access-token');
        expect(localStorageMock.setItem).toHaveBeenCalledWith('refreshToken', 'fake-refresh-token');
        expect(localStorageMock.setItem).toHaveBeenCalledWith('user', JSON.stringify({
          id: 123,
          email: 'test@example.com'
        }));
      });
    });
  });

  describe('Loading States', () => {
    test('shows loading state during submission', async () => {
      const user = userEvent.setup();

      // Mock a slow API response
      (fetch as jest.Mock).mockImplementationOnce(() =>
        new Promise(resolve => setTimeout(() => resolve({
          ok: true,
          json: async () => ({ success: true })
        }), 1000))
      );

      render(<ActivateAccountPage />);

      // Fill and submit form
      await user.type(screen.getByLabelText(/email address/i), 'test@example.com');
      await user.type(screen.getByLabelText(/temporary password/i), 'TempPass123');
      await user.type(screen.getByLabelText(/new password/i), 'NewPassword123');
      await user.type(screen.getByLabelText(/confirm new password/i), 'NewPassword123');

      const submitButton = screen.getByRole('button', { name: /activate account/i });
      await user.click(submitButton);

      // Should show loading text
      expect(screen.getByText(/activating account/i)).toBeInTheDocument();
      expect(submitButton).toBeDisabled();
    });

    test('disables form during submission', async () => {
      const user = userEvent.setup();

      // Mock a slow API response
      (fetch as jest.Mock).mockImplementationOnce(() =>
        new Promise(resolve => setTimeout(() => resolve({
          ok: true,
          json: async () => ({ success: true })
        }), 100))
      );

      render(<ActivateAccountPage />);

      // Fill form
      await user.type(screen.getByLabelText(/email address/i), 'test@example.com');
      await user.type(screen.getByLabelText(/temporary password/i), 'TempPass123');
      await user.type(screen.getByLabelText(/new password/i), 'NewPassword123');
      await user.type(screen.getByLabelText(/confirm new password/i), 'NewPassword123');

      const submitButton = screen.getByRole('button', { name: /activate account/i });
      await user.click(submitButton);

      // Button should be disabled during submission
      expect(submitButton).toBeDisabled();
    });
  });

  describe('Accessibility', () => {
    test('has proper form labels and ARIA attributes', () => {
      render(<ActivateAccountPage />);

      const emailInput = screen.getByLabelText(/email address/i);
      const tempPasswordInput = screen.getByLabelText(/temporary password/i);
      const newPasswordInput = screen.getByLabelText(/new password/i);
      const confirmPasswordInput = screen.getByLabelText(/confirm new password/i);

      expect(emailInput).toHaveAttribute('required');
      expect(tempPasswordInput).toHaveAttribute('required');
      expect(newPasswordInput).toHaveAttribute('required');
      expect(confirmPasswordInput).toHaveAttribute('required');

      expect(newPasswordInput).toHaveAttribute('minLength', '8');
    });

    test('password toggle buttons have proper titles', () => {
      render(<ActivateAccountPage />);

      const toggleButtons = screen.getAllByTitle(/show password|hide password/i);
      expect(toggleButtons.length).toBeGreaterThan(0);

      toggleButtons.forEach(button => {
        expect(button).toHaveAttribute('type', 'button');
      });
    });
  });

  describe('Edge Cases', () => {
    test('handles network errors gracefully', async () => {
      const user = userEvent.setup();

      (fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'));

      render(<ActivateAccountPage />);

      // Fill and submit form
      await user.type(screen.getByLabelText(/email address/i), 'test@example.com');
      await user.type(screen.getByLabelText(/temporary password/i), 'TempPass123');
      await user.type(screen.getByLabelText(/new password/i), 'NewPassword123');
      await user.type(screen.getByLabelText(/confirm new password/i), 'NewPassword123');

      const submitButton = screen.getByRole('button', { name: /activate account/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/failed to activate account/i)).toBeInTheDocument();
      });
    });

    test('handles malformed JSON response', async () => {
      const user = userEvent.setup();

      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        json: async () => { throw new Error('Invalid JSON'); },
        text: async () => 'Invalid response',
      });

      render(<ActivateAccountPage />);

      // Fill and submit form
      await user.type(screen.getByLabelText(/email address/i), 'test@example.com');
      await user.type(screen.getByLabelText(/temporary password/i), 'TempPass123');
      await user.type(screen.getByLabelText(/new password/i), 'NewPassword123');
      await user.type(screen.getByLabelText(/confirm new password/i), 'NewPassword123');

      const submitButton = screen.getByRole('button', { name: /activate account/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/activation failed/i)).toBeInTheDocument();
      });
    });

    test('handles special characters in form fields', async () => {
      const user = userEvent.setup();
      render(<ActivateAccountPage />);

      // Test with special characters
      await user.type(screen.getByLabelText(/email address/i), 'test+special@example.com');
      await user.type(screen.getByLabelText(/temporary password/i), 'Temp@Pass#123!');
      await user.type(screen.getByLabelText(/new password/i), 'New@Pass#456!');
      await user.type(screen.getByLabelText(/confirm new password/i), 'New@Pass#456!');

      const emailInput = screen.getByLabelText(/email address/i);
      const tempPasswordInput = screen.getByLabelText(/temporary password/i);

      expect(emailInput).toHaveValue('test+special@example.com');
      expect(tempPasswordInput).toHaveValue('Temp@Pass#123!');
    });
  });
});