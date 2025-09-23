import { clsx } from 'clsx';
import type { CardProps, CardHeaderProps, CardContentProps, CardTitleProps, CardDescriptionProps } from '@/types/components';

const paddingClasses = {
  none: '',
  sm: 'p-4',
  md: 'p-6',
  lg: 'p-8',
};

const shadowClasses = {
  none: 'shadow-none',
  sm: 'shadow-sm',
  md: 'shadow-md',
  lg: 'shadow-lg',
};

function Card({
  children,
  className,
  padding = 'md',
  shadow = 'sm'
}: CardProps) {
  return (
    <div
      className={clsx(
        'card',
        paddingClasses[padding],
        shadowClasses[shadow],
        className
      )}
    >
      {children}
    </div>
  );
}

export { Card };
export default Card;

export function CardHeader({ children, className }: CardHeaderProps) {
  return (
    <div className={clsx('card-header', className)}>
      {children}
    </div>
  );
}

export function CardContent({ children, className }: CardContentProps) {
  return (
    <div className={clsx('card-content', className)}>
      {children}
    </div>
  );
}

export function CardTitle({ children, className }: CardTitleProps) {
  return (
    <h3 className={clsx('text-lg font-semibold leading-none tracking-tight', className)}>
      {children}
    </h3>
  );
}

export function CardDescription({ children, className }: CardDescriptionProps) {
  return (
    <p className={clsx('text-sm text-gray-500 dark:text-gray-400', className)}>
      {children}
    </p>
  );
}