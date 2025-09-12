import { type ReactNode } from 'react';
import { clsx } from 'clsx';
import LoadingSpinner from './LoadingSpinner';
import { ButtonProps } from '../../types/ui';

const variantClasses = {
  primary: 'btn-primary',
  secondary: 'btn-secondary', 
  outline: 'btn-outline',
  ghost: 'bg-transparent text-gray-700 hover:bg-gray-100',
  danger: 'bg-red-600 text-white hover:bg-red-700',
};

const sizeClasses = {
  sm: 'h-8 px-3 text-xs',
  md: 'h-10 px-4 text-sm',
  lg: 'h-12 px-6 text-base',
};

export default function Button({
  variant = 'primary',
  size = 'md',
  loading = false,
  leftIcon,
  rightIcon,
  fullWidth = false,
  className,
  children,
  disabled,
  ...props
}: ButtonProps) {
  const isDisabled = disabled || loading;

  return (
    <button
      className={clsx(
        'btn',
        variantClasses[variant],
        sizeClasses[size],
        {
          'w-full': fullWidth,
          'opacity-50 cursor-not-allowed': isDisabled,
        },
        className
      )}
      disabled={isDisabled}
      {...props}
    >
      {loading && <LoadingSpinner size="sm" className="mr-2" />}
      {!loading && leftIcon && <span className="mr-2">{leftIcon}</span>}
      
      <span className={loading ? 'opacity-70' : ''}>{children}</span>
      
      {!loading && rightIcon && <span className="ml-2">{rightIcon}</span>}
    </button>
  );
}