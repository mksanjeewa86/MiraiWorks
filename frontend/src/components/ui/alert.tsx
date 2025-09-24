import { clsx } from 'clsx';
import { ReactNode } from 'react';

interface AlertProps {
  variant?: 'default' | 'destructive' | 'warning' | 'success';
  children: ReactNode;
  className?: string;
}

const variantClasses = {
  default: 'bg-blue-50 border-blue-200 text-blue-800',
  destructive: 'bg-red-50 border-red-200 text-red-800',
  warning: 'bg-yellow-50 border-yellow-200 text-yellow-800',
  success: 'bg-green-50 border-green-200 text-green-800',
};

export function Alert({ variant = 'default', children, className }: AlertProps) {
  return (
    <div className={clsx('rounded-lg border p-4', variantClasses[variant], className)}>
      {children}
    </div>
  );
}

export function AlertDescription({
  children,
  className,
}: {
  children: ReactNode;
  className?: string;
}) {
  return <div className={clsx('text-sm', className)}>{children}</div>;
}
