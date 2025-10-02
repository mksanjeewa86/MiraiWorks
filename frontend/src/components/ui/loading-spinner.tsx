import { clsx } from 'clsx';
import type { LoadingSpinnerProps } from '@/types/components';

const sizeClasses = {
  sm: 'h-4 w-4',
  md: 'h-8 w-8',
  lg: 'h-12 w-12',
  xl: 'h-16 w-16',
};

function LoadingSpinner({ size = 'md', className }: LoadingSpinnerProps) {
  return (
    <div
      className={clsx(
        'animate-spin rounded-full border-2 border-gray-300 border-t-blue-600',
        sizeClasses[size],
        className
      )}
      aria-label="Loading"
    />
  );
}

export { LoadingSpinner };
export default LoadingSpinner;
