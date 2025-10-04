import { forwardRef } from 'react';
import { clsx } from 'clsx';
import type {
  SelectProps,
  SelectContentProps,
  SelectItemProps,
  SelectTriggerProps,
  SelectValueProps,
} from '@/types/components';

const Select = forwardRef<HTMLSelectElement, SelectProps>(
  ({ className, children, onValueChange, onChange, ...props }, ref) => {
    const handleChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
      if (onValueChange) {
        onValueChange(event.target.value);
      }
      if (onChange) {
        onChange(event);
      }
    };

    return (
      <select
        className={clsx(
          'flex h-10 w-full items-center justify-between rounded-md border border-gray-300 bg-white px-3 py-2 text-sm ring-offset-white placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 dark:border-gray-700 dark:bg-gray-950 dark:ring-offset-gray-950 dark:placeholder:text-gray-400 dark:focus:ring-blue-400',
          className
        )}
        ref={ref}
        onChange={handleChange}
        {...props}
      >
        {children}
      </select>
    );
  }
);

Select.displayName = 'Select';

const SelectContent = ({ children, className }: SelectContentProps) => {
  return <div className={clsx('select-content', className)}>{children}</div>;
};

const SelectItem = ({ children, value, className }: SelectItemProps) => {
  return (
    <option value={value} className={clsx('select-item', className)}>
      {children}
    </option>
  );
};

const SelectTrigger = forwardRef<HTMLSelectElement, SelectTriggerProps & SelectProps>(
  ({ children, className, ...props }, ref) => {
    return (
      <Select ref={ref} className={className} {...props}>
        {children}
      </Select>
    );
  }
);

SelectTrigger.displayName = 'SelectTrigger';

const SelectValue = ({ placeholder, className }: SelectValueProps) => {
  return <span className={clsx('select-value', className)}>{placeholder}</span>;
};

export { Select, SelectContent, SelectItem, SelectTrigger, SelectValue };

export default Select;
