import React from 'react';
import { clsx } from 'clsx';
import { LoadingSpinner } from './loading-spinner';
import { ButtonProps } from '../../types/ui';

const variantClasses = {
  primary: 'btn-primary',
  secondary: 'btn-secondary',
  outline: 'btn-outline',
  ghost: 'bg-transparent text-gray-700 hover:bg-gray-100',
  danger: 'bg-red-600 text-white hover:bg-red-700',
  destructive: 'bg-red-600 text-white hover:bg-red-700',
  default: 'bg-white text-gray-900 border border-gray-300 hover:bg-gray-50',
  warning: 'bg-yellow-600 text-white hover:bg-yellow-700',
  info: 'bg-blue-600 text-white hover:bg-blue-700',
};

const sizeClasses = {
  sm: 'h-8 px-3 text-xs',
  md: 'h-10 px-4 text-sm',
  lg: 'h-12 px-6 text-base',
};

function Button({
  variant = 'primary',
  size = 'md',
  loading = false,
  leftIcon,
  rightIcon,
  fullWidth = false,
  className,
  children,
  disabled,
  asChild = false,
  ...props
}: ButtonProps) {
  const isDisabled = disabled || loading;

  const buttonClasses = clsx(
    'btn',
    variantClasses[variant],
    sizeClasses[size],
    {
      'w-full': fullWidth,
      'opacity-50 cursor-not-allowed': isDisabled,
    },
    className
  );

  const buttonContent = (
    <>
      {loading && <LoadingSpinner size="sm" className="mr-2" />}
      {!loading && leftIcon && <span className="mr-2">{leftIcon}</span>}

      <span className={loading ? 'opacity-70' : ''}>{children}</span>

      {!loading && rightIcon && <span className="ml-2">{rightIcon}</span>}
    </>
  );

  if (asChild) {
    // When asChild is true, clone the child element with button classes
    const child = children as React.ReactElement;
    const childProps = child.props as any;
    return React.cloneElement(child, {
      className: clsx(childProps?.className, buttonClasses),
      disabled: isDisabled,
      ...props,
    } as any);
  }

  return (
    <button className={buttonClasses} disabled={isDisabled} {...props}>
      {buttonContent}
    </button>
  );
}

export { Button };
export default Button;
