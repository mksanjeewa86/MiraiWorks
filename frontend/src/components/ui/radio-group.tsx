import { forwardRef } from 'react';
import { clsx } from 'clsx';
import type { RadioGroupProps, RadioGroupItemProps } from '@/types/components';

const RadioGroup = forwardRef<HTMLDivElement, RadioGroupProps>(
  ({ children, className, ...props }, ref) => {
    return (
      <div ref={ref} className={clsx('grid gap-2', className)} role="radiogroup" {...props}>
        {children}
      </div>
    );
  }
);

RadioGroup.displayName = 'RadioGroup';

const RadioGroupItem = forwardRef<HTMLInputElement, RadioGroupItemProps>(
  ({ className, ...props }, ref) => {
    return (
      <input
        type="radio"
        className={clsx(
          'aspect-square h-4 w-4 rounded-full border border-gray-300 text-blue-600 ring-offset-white focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 dark:border-gray-700 dark:ring-offset-gray-950 dark:focus-visible:ring-blue-400',
          className
        )}
        ref={ref}
        {...props}
      />
    );
  }
);

RadioGroupItem.displayName = 'RadioGroupItem';

export { RadioGroup, RadioGroupItem };
export default RadioGroup;
