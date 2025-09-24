import { forwardRef } from 'react';
import { clsx } from 'clsx';
import { InputProps } from '../../types/ui';

const Input = forwardRef<HTMLInputElement, InputProps>(
  (
    { label, error, helperText, leftIcon, rightIcon, fullWidth = true, className, id, ...props },
    ref
  ) => {
    const inputId = id || label?.toLowerCase().replace(/\s+/g, '-');
    const hasError = Boolean(error);

    return (
      <div className={clsx('flex flex-col space-y-2', { 'w-full': fullWidth })}>
        {label && (
          <label
            htmlFor={inputId}
            className="text-sm font-medium"
            style={{ color: 'var(--text-primary)' }}
          >
            {label}
            {props.required && <span className="text-red-500 ml-1">*</span>}
          </label>
        )}

        <div className="relative">
          {leftIcon && (
            <div
              className="absolute left-3 top-1/2 transform -translate-y-1/2"
              style={{ color: 'var(--text-muted)' }}
            >
              {leftIcon}
            </div>
          )}

          <input
            ref={ref}
            id={inputId}
            className={clsx(
              'input',
              {
                'pl-10': leftIcon,
                'pr-10': rightIcon,
                'border-red-300 focus-visible:ring-red-500 dark:border-red-700': hasError,
              },
              className
            )}
            {...props}
          />

          {rightIcon && (
            <div
              className="absolute right-3 top-1/2 transform -translate-y-1/2"
              style={{ color: 'var(--text-muted)' }}
            >
              {rightIcon}
            </div>
          )}
        </div>

        {error && <p className="text-sm text-red-600 dark:text-red-400">{error}</p>}

        {helperText && !error && (
          <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
            {helperText}
          </p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';

export { Input };
export default Input;
