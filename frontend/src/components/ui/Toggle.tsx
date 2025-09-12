'use client';

import type { ToggleProps } from '@/types/components';

export default function Toggle({ 
  id, 
  checked, 
  onChange, 
  disabled = false, 
  size = 'md',
  className = '' 
}: ToggleProps) {
  const sizeClasses = {
    sm: {
      container: 'w-8 h-5',
      knob: 'w-3 h-3',
      translate: checked ? 'translate-x-3' : 'translate-x-0.5'
    },
    md: {
      container: 'w-11 h-6',
      knob: 'w-4 h-4',
      translate: checked ? 'translate-x-5' : 'translate-x-1'
    },
    lg: {
      container: 'w-14 h-8',
      knob: 'w-6 h-6',
      translate: checked ? 'translate-x-6' : 'translate-x-1'
    }
  };

  const currentSize = sizeClasses[size];

  return (
    <button
      id={id}
      type="button"
      role="switch"
      aria-checked={checked}
      disabled={disabled}
      onClick={() => onChange(!checked)}
      className={`
        ${currentSize.container}
        relative inline-flex items-center rounded-full transition-colors duration-200 ease-in-out
        focus:outline-none focus:ring-2 focus:ring-brand-primary focus:ring-offset-2
        ${checked 
          ? 'bg-brand-primary' 
          : 'bg-gray-200 dark:bg-gray-700'
        }
        ${disabled 
          ? 'opacity-50 cursor-not-allowed' 
          : 'cursor-pointer hover:shadow-md'
        }
        ${className}
      `}
    >
      <span className="sr-only">Toggle setting</span>
      <span
        className={`
          ${currentSize.knob}
          ${currentSize.translate}
          inline-block rounded-full bg-white shadow-lg transform transition-transform duration-200 ease-in-out
          ring-0
        `}
      />
    </button>
  );
}