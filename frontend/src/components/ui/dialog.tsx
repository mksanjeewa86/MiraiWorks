import React, { forwardRef, createContext, useContext, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { clsx } from 'clsx';

interface DialogContextValue {
  open: boolean;
  setOpen: (open: boolean) => void;
}

const DialogContext = createContext<DialogContextValue | undefined>(undefined);

const useDialog = () => {
  const context = useContext(DialogContext);
  if (!context) {
    throw new Error('Dialog components must be used within a Dialog');
  }
  return context;
};

interface DialogProps {
  open?: boolean;
  defaultOpen?: boolean;
  onOpenChange?: (open: boolean) => void;
  children: React.ReactNode;
}

const Dialog = ({ open, defaultOpen = false, onOpenChange, children }: DialogProps) => {
  const [internalOpen, setInternalOpen] = React.useState(defaultOpen);

  const isOpen = open !== undefined ? open : internalOpen;

  const setOpen = (newOpen: boolean) => {
    if (open === undefined) {
      setInternalOpen(newOpen);
    }
    onOpenChange?.(newOpen);
  };

  return (
    <DialogContext.Provider value={{ open: isOpen, setOpen }}>{children}</DialogContext.Provider>
  );
};

interface DialogTriggerProps {
  asChild?: boolean;
  children: React.ReactNode;
  className?: string;
}

const DialogTrigger = forwardRef<HTMLButtonElement, DialogTriggerProps>(
  ({ asChild = false, children, className, ...props }, ref) => {
    const { setOpen } = useDialog();

    const handleClick = () => {
      setOpen(true);
    };

    if (asChild) {
      const child = children as React.ReactElement<any>;
      return React.cloneElement(child, {
        ...(child.props || {}),
        onClick: handleClick,
        ref,
      });
    }

    return (
      <button
        ref={ref}
        className={clsx(
          'inline-flex items-center justify-center rounded-md px-4 py-2 text-sm font-medium',
          'bg-blue-600 text-white hover:bg-blue-700',
          'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2',
          className
        )}
        onClick={handleClick}
        {...props}
      >
        {children}
      </button>
    );
  }
);

DialogTrigger.displayName = 'DialogTrigger';

interface DialogPortalProps {
  children: React.ReactNode;
  container?: HTMLElement;
}

const DialogPortal = ({ children, container }: DialogPortalProps) => {
  if (typeof window === 'undefined') return null;

  const portalContainer = container || document.body;

  return createPortal(children, portalContainer);
};

interface DialogOverlayProps {
  className?: string;
}

const DialogOverlay = forwardRef<HTMLDivElement, DialogOverlayProps>(
  ({ className, ...props }, ref) => {
    const { setOpen } = useDialog();

    return (
      <div
        ref={ref}
        className={clsx('fixed inset-0 z-50 bg-black/50 backdrop-blur-sm', className)}
        onClick={() => setOpen(false)}
        {...props}
      />
    );
  }
);

DialogOverlay.displayName = 'DialogOverlay';

interface DialogContentProps {
  children: React.ReactNode;
  className?: string;
  closeButton?: boolean;
  onEscapeKeyDown?: (event: KeyboardEvent) => void;
  onPointerDownOutside?: (event: PointerEvent) => void;
}

const DialogContent = forwardRef<HTMLDivElement, DialogContentProps>(
  (
    { children, className, closeButton = true, onEscapeKeyDown, onPointerDownOutside, ...props },
    ref
  ) => {
    const { open, setOpen } = useDialog();

    useEffect(() => {
      const handleKeyDown = (event: KeyboardEvent) => {
        if (event.key === 'Escape') {
          event.preventDefault();
          onEscapeKeyDown?.(event);
          setOpen(false);
        }
      };

      if (open) {
        document.addEventListener('keydown', handleKeyDown);
        return () => document.removeEventListener('keydown', handleKeyDown);
      }
    }, [open, onEscapeKeyDown, setOpen]);

    if (!open) return null;

    return (
      <DialogPortal>
        <DialogOverlay />
        <div
          ref={ref}
          className={clsx(
            'fixed left-[50%] top-[50%] z-50 grid w-full max-w-lg translate-x-[-50%] translate-y-[-50%] gap-4 border bg-white p-6 shadow-lg duration-200 sm:rounded-lg',
            className
          )}
          onClick={(e) => e.stopPropagation()}
          {...props}
        >
          {children}
        </div>
      </DialogPortal>
    );
  }
);

DialogContent.displayName = 'DialogContent';

interface DialogHeaderProps {
  children: React.ReactNode;
  className?: string;
}

const DialogHeader = ({ children, className }: DialogHeaderProps) => {
  return (
    <div className={clsx('flex flex-col space-y-1.5 text-center sm:text-left', className)}>
      {children}
    </div>
  );
};

interface DialogFooterProps {
  children: React.ReactNode;
  className?: string;
}

const DialogFooter = ({ children, className }: DialogFooterProps) => {
  return (
    <div
      className={clsx('flex flex-col-reverse sm:flex-row sm:justify-end sm:space-x-2', className)}
    >
      {children}
    </div>
  );
};

interface DialogTitleProps {
  children: React.ReactNode;
  className?: string;
}

const DialogTitle = forwardRef<HTMLHeadingElement, DialogTitleProps>(
  ({ children, className, ...props }, ref) => {
    return (
      <h2
        ref={ref}
        className={clsx('text-lg font-semibold leading-none tracking-tight', className)}
        {...props}
      >
        {children}
      </h2>
    );
  }
);

DialogTitle.displayName = 'DialogTitle';

interface DialogDescriptionProps {
  children: React.ReactNode;
  className?: string;
}

const DialogDescription = forwardRef<HTMLParagraphElement, DialogDescriptionProps>(
  ({ children, className, ...props }, ref) => {
    return (
      <p ref={ref} className={clsx('text-sm text-gray-500', className)} {...props}>
        {children}
      </p>
    );
  }
);

DialogDescription.displayName = 'DialogDescription';

interface DialogCloseProps {
  asChild?: boolean;
  children: React.ReactNode;
  className?: string;
}

const DialogClose = forwardRef<HTMLButtonElement, DialogCloseProps>(
  ({ asChild = false, children, className, ...props }, ref) => {
    const { setOpen } = useDialog();

    const handleClick = () => {
      setOpen(false);
    };

    if (asChild) {
      const child = children as React.ReactElement<any>;
      return React.cloneElement(child, {
        ...(child.props || {}),
        onClick: handleClick,
        ref,
      });
    }

    return (
      <button
        ref={ref}
        className={clsx(
          'absolute right-4 top-4 rounded-sm opacity-70 ring-offset-white transition-opacity hover:opacity-100',
          'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2',
          'disabled:pointer-events-none',
          className
        )}
        onClick={handleClick}
        {...props}
      >
        {children}
        <span className="sr-only">Close</span>
      </button>
    );
  }
);

DialogClose.displayName = 'DialogClose';

export {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogOverlay,
  DialogPortal,
  DialogTitle,
  DialogTrigger,
};
