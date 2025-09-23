import React from 'react';
import { clsx } from 'clsx';
import type { BadgeProps } from '@/types/components';

const variantClasses = {
  primary: 'badge-primary',
  secondary: 'badge-secondary',
  success: 'badge-success',
  warning: 'badge-warning',
  error: 'badge-error',
  destructive: 'bg-red-100 text-red-800 border-red-200',
  default: 'bg-gray-100 text-gray-800 border-gray-200',
  outline: 'bg-transparent text-gray-700 border-gray-300',
};

const sizeClasses = {
  sm: 'px-2 py-0.5 text-xs',
  md: 'px-2.5 py-0.5 text-xs',
  lg: 'px-3 py-1 text-sm',
};

function Badge({
  children,
  variant = 'secondary',
  size = 'md',
  className
}: BadgeProps) {
  return (
    <span
      className={clsx(
        'badge',
        variantClasses[variant],
        sizeClasses[size],
        className
      )}
    >
      {children}
    </span>
  );
}

export { Badge };
export default Badge;