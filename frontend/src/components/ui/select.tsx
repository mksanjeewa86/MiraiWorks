import { forwardRef, Children, isValidElement, cloneElement } from 'react';
import { clsx } from 'clsx';
import type {
  SelectProps,
  SelectContentProps,
  SelectItemProps,
  SelectTriggerProps,
  SelectValueProps,
} from '@/types/components';

// Internal context to collect children
interface SelectContextValue {
  placeholder?: string;
}

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

    // Extract placeholder from SelectValue component if present
    let placeholder = '';

    // Process children to extract SelectValue placeholder and filter out non-option children
    const processedChildren: React.ReactNode[] = [];

    Children.forEach(children, (child) => {
      if (isValidElement(child)) {
        // If it's SelectTrigger, process its children
        if (child.type === SelectTrigger) {
          const triggerProps = child.props as { children?: React.ReactNode };
          Children.forEach(triggerProps.children, (triggerChild) => {
            if (isValidElement(triggerChild) && triggerChild.type === SelectValue) {
              const valueProps = triggerChild.props as SelectValueProps;
              placeholder = valueProps.placeholder || '';
            }
          });
        }
        // If it's SelectContent, extract SelectItem children
        else if (child.type === SelectContent) {
          const contentProps = child.props as { children?: React.ReactNode };
          Children.forEach(contentProps.children, (contentChild) => {
            if (isValidElement(contentChild) && contentChild.type === SelectItem) {
              processedChildren.push(contentChild);
            }
          });
        }
        // If it's a direct SelectItem, include it
        else if (child.type === SelectItem) {
          processedChildren.push(child);
        }
      }
    });

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
        {placeholder && (
          <option value="" disabled>
            {placeholder}
          </option>
        )}
        {processedChildren}
      </select>
    );
  }
);

Select.displayName = 'Select';

const SelectContent = ({ children, className }: SelectContentProps) => {
  // SelectContent is just a logical wrapper, doesn't render anything
  return <>{children}</>;
};

const SelectItem = ({ children, value, className }: SelectItemProps) => {
  return (
    <option value={value} className={clsx('select-item', className)}>
      {children}
    </option>
  );
};

const SelectTrigger = forwardRef<HTMLDivElement, SelectTriggerProps>(
  ({ children, className }, ref) => {
    // SelectTrigger is just a logical wrapper, doesn't render anything
    return <>{children}</>;
  }
);

SelectTrigger.displayName = 'SelectTrigger';

const SelectValue = ({ placeholder, className }: SelectValueProps) => {
  // SelectValue doesn't render anything, it's just used to pass placeholder
  return null;
};

export { Select, SelectContent, SelectItem, SelectTrigger, SelectValue };

export default Select;
