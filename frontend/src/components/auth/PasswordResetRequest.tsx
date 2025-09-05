import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Mail, ArrowLeft, CheckCircle } from 'lucide-react';
import * as Dialog from '@radix-ui/react-dialog';
import Button from '../ui/Button';

const resetSchema = z.object({
  email: z.string().email('Invalid email address'),
});

type ResetFormData = z.infer<typeof resetSchema>;

interface PasswordResetRequestProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit?: (email: string) => Promise<void>;
}

export default function PasswordResetRequest({ isOpen, onClose, onSubmit }: PasswordResetRequestProps) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset
  } = useForm<ResetFormData>({
    resolver: zodResolver(resetSchema),
  });

  const handleFormSubmit = async (data: ResetFormData) => {
    if (isSubmitting) return;
    
    setIsSubmitting(true);
    setError(null);
    
    try {
      if (onSubmit) {
        await onSubmit(data.email);
      } else {
        // Mock API call for demo
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
      setIsSuccess(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send reset email');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = () => {
    setIsSuccess(false);
    setError(null);
    reset();
    onClose();
  };

  const handleBackToLogin = () => {
    handleClose();
  };

  return (
    <Dialog.Root open={isOpen} onOpenChange={handleClose}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-black/50 z-50" />
        <Dialog.Content className="fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-white dark:bg-gray-800 rounded-2xl shadow-2xl z-50 w-full max-w-md mx-4 p-6">
          {!isSuccess ? (
            <>
              <div className="text-center mb-6">
                <div className="w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-4" style={{ backgroundColor: 'rgba(108, 99, 255, 0.1)' }}>
                  <Mail className="h-8 w-8 text-brand-primary" />
                </div>
                <Dialog.Title className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                  Reset your password
                </Dialog.Title>
                <Dialog.Description className="text-sm text-muted-600 dark:text-muted-300">
                  Enter your email address and we'll send you a link to reset your password.
                </Dialog.Description>
              </div>

              {error && (
                <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-2xl p-4 mb-6">
                  <p className="text-sm text-red-700 dark:text-red-300">{error}</p>
                </div>
              )}

              <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-6">
                <div>
                  <label htmlFor="reset-email" className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-2">
                    Email address
                  </label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-500 h-5 w-5" />
                    <input
                      id="reset-email"
                      type="email"
                      autoComplete="email"
                      {...register('email')}
                      className={`
                        w-full pl-10 pr-4 py-3 bg-gray-50 dark:bg-gray-800 border rounded-2xl text-sm 
                        focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent 
                        transition-colors placeholder-muted-400 dark:placeholder-muted-500
                        ${errors.email 
                          ? 'border-red-300 dark:border-red-700 bg-red-50 dark:bg-red-900/20' 
                          : 'border-gray-200 dark:border-gray-700'
                        }
                      `}
                      placeholder="Enter your email"
                    />
                  </div>
                  {errors.email && (
                    <p className="mt-2 text-sm text-red-600 dark:text-red-400">{errors.email.message}</p>
                  )}
                </div>

                <div className="space-y-3">
                  <Button
                    type="submit"
                    loading={isSubmitting}
                    disabled={isSubmitting}
                    className="w-full btn-primary py-3"
                  >
                    Send reset link
                  </Button>
                  
                  <button
                    type="button"
                    onClick={handleBackToLogin}
                    className="w-full flex items-center justify-center py-3 text-sm font-medium hover:text-brand-primary transition-colors" style={{ color: 'var(--text-muted)' }}
                  >
                    <ArrowLeft className="h-4 w-4 mr-2" />
                    Back to login
                  </button>
                </div>
              </form>
            </>
          ) : (
            <div className="text-center">
              <div className="w-16 h-16 bg-accent-100 dark:bg-accent-900/20 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <CheckCircle className="h-8 w-8 text-accent-600 dark:text-accent-400" />
              </div>
              <Dialog.Title className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                Check your email
              </Dialog.Title>
              <Dialog.Description className="text-sm text-muted-600 dark:text-muted-300 mb-6">
                We've sent a password reset link to your email address. Click the link to reset your password.
              </Dialog.Description>
              
              <button
                onClick={handleBackToLogin}
                className="w-full flex items-center justify-center py-3 text-sm font-medium text-brand-primary hover:opacity-80 transition-colors"
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to login
              </button>
            </div>
          )}
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}