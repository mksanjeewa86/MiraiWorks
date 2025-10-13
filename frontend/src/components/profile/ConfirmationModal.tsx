'use client';

import { Button } from '@/components/ui';
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import { AlertTriangle, X } from 'lucide-react';

interface ConfirmationModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title?: string;
  description?: string;
  confirmText?: string;
  cancelText?: string;
  variant?: 'danger' | 'warning' | 'info';
  isLoading?: boolean;
}

export default function ConfirmationModal({
  isOpen,
  onClose,
  onConfirm,
  title = 'Confirm Action',
  description = 'Are you sure you want to proceed? This action cannot be undone.',
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  variant = 'danger',
  isLoading = false,
}: ConfirmationModalProps) {
  const handleConfirm = () => {
    onConfirm();
    onClose();
  };

  const variantStyles = {
    danger: {
      icon: 'bg-red-100 text-red-600',
      button: 'bg-red-600 text-white hover:bg-red-700',
    },
    warning: {
      icon: 'bg-yellow-100 text-yellow-600',
      button: 'bg-yellow-600 text-white hover:bg-yellow-700',
    },
    info: {
      icon: 'bg-blue-100 text-blue-600',
      button: 'bg-blue-600 text-white hover:bg-blue-700',
    },
  };

  const styles = variantStyles[variant];

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent
        closeButton={false}
        className="flex flex-col max-w-md overflow-hidden rounded-2xl border border-slate-200 bg-white text-slate-900 shadow-[0_20px_60px_-15px_rgba(15,23,42,0.3)]"
      >
        <DialogHeader className="px-6 pt-6">
          <div className="flex items-start justify-between gap-4">
            <div className="flex gap-4">
              <span className={`inline-flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-full ${styles.icon}`}>
                <AlertTriangle className="h-6 w-6" />
              </span>
              <div>
                <DialogTitle className="text-lg font-semibold text-slate-900 mb-2">
                  {title}
                </DialogTitle>
                <DialogDescription className="text-sm text-slate-600 leading-relaxed">
                  {description}
                </DialogDescription>
              </div>
            </div>
            <DialogClose className="rounded-lg border border-slate-200 p-2 text-slate-500 transition hover:bg-slate-100 hover:text-slate-700">
              <X className="h-4 w-4" />
            </DialogClose>
          </div>
        </DialogHeader>

        <DialogFooter className="gap-3 border-t border-slate-200 bg-slate-50 px-6 py-4">
          <div className="flex w-full items-center justify-end gap-3">
            <Button
              type="button"
              variant="ghost"
              onClick={onClose}
              disabled={isLoading}
              className="min-w-[100px] border border-slate-300 bg-white text-slate-600 hover:bg-slate-100"
            >
              {cancelText}
            </Button>
            <Button
              type="button"
              onClick={handleConfirm}
              disabled={isLoading}
              className={`min-w-[100px] ${styles.button}`}
            >
              {isLoading ? 'Processing...' : confirmText}
            </Button>
          </div>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
