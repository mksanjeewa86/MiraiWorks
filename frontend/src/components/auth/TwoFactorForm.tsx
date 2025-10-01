'use client';

import { useState, useRef, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Shield, RotateCcw } from 'lucide-react';
import { Button } from '@/components/ui';
import type { TwoFactorFormProps } from '@/types/components';
import { twoFactorSchema, type TwoFactorFormData } from '@/types/forms';

export default function TwoFactorForm({
  onSubmit,
  onResend,
  isLoading = false,
  error,
}: TwoFactorFormProps) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isResending, setIsResending] = useState(false);
  const [codeDigits, setCodeDigits] = useState(['', '', '', '', '', '']);
  const inputRefs = useRef<(HTMLInputElement | null)[]>([]);

  const {
    handleSubmit,
    setValue,
    formState: { errors },
  } = useForm<TwoFactorFormData>({
    resolver: zodResolver(twoFactorSchema),
  });

  // Update form value when digits change
  useEffect(() => {
    const code = codeDigits.join('');
    setValue('code', code);
  }, [codeDigits, setValue]);

  const handleDigitChange = (index: number, value: string) => {
    // Only allow single digit
    if (value.length > 1) value = value.slice(-1);
    if (!/^\d*$/.test(value)) return; // Only allow numbers

    const newDigits = [...codeDigits];
    newDigits[index] = value;
    setCodeDigits(newDigits);

    // Auto-focus next input
    if (value && index < 5) {
      inputRefs.current[index + 1]?.focus();
    }
  };

  const handleKeyDown = (index: number, e: React.KeyboardEvent<HTMLInputElement>) => {
    // Handle backspace
    if (e.key === 'Backspace' && !codeDigits[index] && index > 0) {
      inputRefs.current[index - 1]?.focus();
    }
    // Handle paste
    else if (e.key === 'v' && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      navigator.clipboard.readText().then((text) => {
        const digits = text.replace(/\D/g, '').slice(0, 6).split('');
        const newDigits = [...codeDigits];
        digits.forEach((digit, i) => {
          if (i < 6) newDigits[i] = digit;
        });
        setCodeDigits(newDigits);
        // Focus on the next empty field or the last field
        const nextIndex = Math.min(digits.length, 5);
        inputRefs.current[nextIndex]?.focus();
      });
    }
  };

  const handleFormSubmit = async () => {
    const code = codeDigits.join('');
    if (code.length !== 6) return;

    setIsSubmitting(true);
    try {
      await onSubmit(code);
    } catch {
      // Error handled by parent
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleResend = async () => {
    if (!onResend) return;

    setIsResending(true);
    try {
      await onResend();
    } catch {
      // Error handled by parent
    } finally {
      setIsResending(false);
    }
  };

  return (
    <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-6">
      <div className="text-center">
        <div
          className="w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-4"
          style={{ backgroundColor: 'rgba(108, 99, 255, 0.1)' }}
        >
          <Shield className="h-8 w-8 text-brand-primary" />
        </div>
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
          Two-Factor Authentication
        </h3>
        <p className="text-sm text-muted-600 dark:text-muted-300">
          Enter the 6-digit code from your authenticator app
        </p>
      </div>

      {error && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-2xl p-4">
          <p className="text-sm text-red-700 dark:text-red-300 text-center">{error}</p>
        </div>
      )}

      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-4 text-center">
          Verification Code
        </label>
        <div className="flex justify-center space-x-3">
          {codeDigits.map((digit, index) => (
            <input
              key={index}
              ref={(el) => {
                inputRefs.current[index] = el;
              }}
              type="text"
              inputMode="numeric"
              pattern="[0-9]"
              maxLength={1}
              value={digit}
              onChange={(e) => handleDigitChange(index, e.target.value)}
              onKeyDown={(e) => handleKeyDown(index, e)}
              className={`
                w-12 h-12 text-center text-lg font-semibold bg-gray-50 dark:bg-gray-800 
                border rounded-2xl focus:outline-none focus:ring-2 focus:ring-brand-primary 
                focus:border-transparent transition-colors
                ${
                  errors.code
                    ? 'border-red-300 dark:border-red-700 bg-red-50 dark:bg-red-900/20'
                    : 'border-gray-200 dark:border-gray-700'
                }
              `}
              aria-label={`Digit ${index + 1}`}
            />
          ))}
        </div>
        {errors.code && (
          <p className="mt-2 text-sm text-red-600 dark:text-red-400 text-center">
            {errors.code.message}
          </p>
        )}
      </div>

      <Button
        type="submit"
        loading={isSubmitting || isLoading}
        disabled={codeDigits.join('').length !== 6 || isSubmitting || isLoading}
        className="w-full btn-primary py-3"
      >
        Verify Code
      </Button>

      {onResend && (
        <div className="text-center">
          <button
            type="button"
            onClick={handleResend}
            disabled={isResending}
            className="inline-flex items-center text-sm hover:text-brand-primary transition-colors disabled:opacity-50"
            style={{ color: 'var(--text-muted)' }}
          >
            <RotateCcw className="h-4 w-4 mr-2" />
            {isResending ? 'Sending...' : "Didn't receive a code? Resend"}
          </button>
        </div>
      )}
    </form>
  );
}
