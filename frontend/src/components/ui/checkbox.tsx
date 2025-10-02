import { forwardRef } from 'react';
import { clsx } from 'clsx';
import type { CheckboxProps } from '@/types/components';

const Checkbox = forwardRef<HTMLInputElement, CheckboxProps>(
  ({ className, onCheckedChange, onChange, ...props }, ref) => {
    const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
      if (onCheckedChange) {
        onCheckedChange(event.target.checked);
      }
      if (onChange) {
        onChange(event);
      }
    };

    return (
      <input
        type="checkbox"
        className={clsx(
          'peer h-4 w-4 shrink-0 rounded-sm border border-gray-300 ring-offset-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 data-[state=checked]:bg-blue-600 data-[state=checked]:text-white dark:border-gray-700 dark:ring-offset-gray-950 dark:focus-visible:ring-blue-400 dark:data-[state=checked]:bg-blue-500',
          className
        )}
        ref={ref}
        onChange={handleChange}
        {...props}
      />
    );
  }
);

Checkbox.displayName = 'Checkbox';

export { Checkbox };
export default Checkbox;
