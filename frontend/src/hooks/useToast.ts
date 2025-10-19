import { useToast as useToastContext } from '@/contexts/ToastContext';

/**
 * Simplified toast hook for easy migration from alert()
 * Wraps the existing ToastContext with a cleaner API
 */
export const useToast = () => {
  const { showToast } = useToastContext();

  return {
    success: (message: string, title?: string) =>
      showToast({
        type: 'success',
        title: title || 'Success',
        message,
        duration: 3000,
      }),
    error: (message: string, title?: string) =>
      showToast({
        type: 'error',
        title: title || 'Error',
        message,
        duration: 5000,
      }),
    warning: (message: string, title?: string) =>
      showToast({
        type: 'warning',
        title: title || 'Warning',
        message,
        duration: 4000,
      }),
    info: (message: string, title?: string) =>
      showToast({
        type: 'info',
        title: title || 'Info',
        message,
        duration: 3000,
      }),
  };
};
