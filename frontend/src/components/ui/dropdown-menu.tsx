import React, { forwardRef, createContext, useContext, useState } from 'react';
import { clsx } from 'clsx';

interface DropdownMenuContextValue {
  open: boolean;
  setOpen: (open: boolean) => void;
}

const DropdownMenuContext = createContext<DropdownMenuContextValue | undefined>(undefined);

const useDropdownMenu = () => {
  const context = useContext(DropdownMenuContext);
  if (!context) {
    throw new Error('DropdownMenu components must be used within a DropdownMenu');
  }
  return context;
};

interface DropdownMenuProps {
  children: React.ReactNode;
  className?: string;
}

const DropdownMenu = ({ children, className }: DropdownMenuProps) => {
  const [open, setOpen] = useState(false);

  return (
    <DropdownMenuContext.Provider value={{ open, setOpen }}>
      <div className={clsx('relative inline-block text-left', className)}>
        {children}
      </div>
    </DropdownMenuContext.Provider>
  );
};

interface DropdownMenuTriggerProps {
  asChild?: boolean;
  children: React.ReactNode;
  className?: string;
}

const DropdownMenuTrigger = forwardRef<HTMLButtonElement, DropdownMenuTriggerProps>(
  ({ asChild = false, children, className, ...props }, ref) => {
    const { open, setOpen } = useDropdownMenu();

    const handleClick = () => {
      setOpen(!open);
    };

    if (asChild) {
      const child = children as React.ReactElement<any>;
      return React.cloneElement(child, {
        ...(child.props || {}),
        onClick: handleClick,
        ref,
        'aria-expanded': open,
        'aria-haspopup': true,
      });
    }

    return (
      <button
        ref={ref}
        className={clsx(
          'inline-flex items-center justify-center rounded-md px-4 py-2 text-sm font-medium',
          'bg-white border border-gray-300 text-gray-700 hover:bg-gray-50',
          'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2',
          className
        )}
        onClick={handleClick}
        aria-expanded={open}
        aria-haspopup={true}
        {...props}
      >
        {children}
      </button>
    );
  }
);

DropdownMenuTrigger.displayName = 'DropdownMenuTrigger';

interface DropdownMenuContentProps {
  children: React.ReactNode;
  className?: string;
  align?: 'start' | 'center' | 'end';
  side?: 'top' | 'right' | 'bottom' | 'left';
}

const DropdownMenuContent = forwardRef<HTMLDivElement, DropdownMenuContentProps>(
  ({ children, className, align = 'start', side = 'bottom', ...props }, ref) => {
    const { open, setOpen } = useDropdownMenu();

    if (!open) return null;

    const alignmentClasses = {
      start: 'left-0',
      center: 'left-1/2 transform -translate-x-1/2',
      end: 'right-0',
    };

    const sideClasses = {
      top: 'bottom-full mb-1',
      right: 'left-full ml-1 top-0',
      bottom: 'top-full mt-1',
      left: 'right-full mr-1 top-0',
    };

    return (
      <>
        {/* Backdrop */}
        <div
          className="fixed inset-0 z-10"
          onClick={() => setOpen(false)}
        />

        {/* Content */}
        <div
          ref={ref}
          className={clsx(
            'absolute z-20 min-w-[8rem] rounded-md bg-white py-1 shadow-lg ring-1 ring-black ring-opacity-5',
            alignmentClasses[align],
            sideClasses[side],
            className
          )}
          {...props}
        >
          {children}
        </div>
      </>
    );
  }
);

DropdownMenuContent.displayName = 'DropdownMenuContent';

interface DropdownMenuItemProps {
  children: React.ReactNode;
  className?: string;
  asChild?: boolean;
  disabled?: boolean;
  onClick?: () => void;
}

const DropdownMenuItem = forwardRef<HTMLDivElement, DropdownMenuItemProps>(
  ({ children, className, asChild = false, disabled = false, onClick, ...props }, ref) => {
    const { setOpen } = useDropdownMenu();

    const handleClick = () => {
      if (!disabled) {
        onClick?.();
        setOpen(false);
      }
    };

    if (asChild) {
      const child = children as React.ReactElement<any>;
      return React.cloneElement(child, {
        ...(child.props || {}),
        onClick: handleClick,
        className: clsx(
          'block w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 hover:text-gray-900',
          'focus:outline-none focus:bg-gray-100 focus:text-gray-900',
          disabled && 'opacity-50 cursor-not-allowed',
          (child.props as any)?.className
        ),
        ref,
      });
    }

    return (
      <div
        ref={ref}
        className={clsx(
          'block w-full px-4 py-2 text-sm text-left text-gray-700 hover:bg-gray-100 hover:text-gray-900',
          'focus:outline-none focus:bg-gray-100 focus:text-gray-900 cursor-pointer',
          disabled && 'opacity-50 cursor-not-allowed',
          className
        )}
        onClick={handleClick}
        {...props}
      >
        {children}
      </div>
    );
  }
);

DropdownMenuItem.displayName = 'DropdownMenuItem';

interface DropdownMenuSeparatorProps {
  className?: string;
}

const DropdownMenuSeparator = forwardRef<HTMLDivElement, DropdownMenuSeparatorProps>(
  ({ className, ...props }, ref) => (
    <div
      ref={ref}
      className={clsx('my-1 h-px bg-gray-200', className)}
      {...props}
    />
  )
);

DropdownMenuSeparator.displayName = 'DropdownMenuSeparator';

interface DropdownMenuLabelProps {
  children: React.ReactNode;
  className?: string;
}

const DropdownMenuLabel = forwardRef<HTMLDivElement, DropdownMenuLabelProps>(
  ({ children, className, ...props }, ref) => (
    <div
      ref={ref}
      className={clsx(
        'px-4 py-2 text-sm font-semibold text-gray-900',
        className
      )}
      {...props}
    >
      {children}
    </div>
  )
);

DropdownMenuLabel.displayName = 'DropdownMenuLabel';

export {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
};