'use client';

import { useState } from 'react';
import { XCircle } from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui';
import { Button, Textarea } from '@/components/ui';
import type { TodoExtensionRequest } from '@/types/todo';

interface ExtensionRejectDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (reason: string) => void;
  request: TodoExtensionRequest | null;
  loading?: boolean;
}

export default function ExtensionRejectDialog({
  isOpen,
  onClose,
  onConfirm,
  request,
  loading = false,
}: ExtensionRejectDialogProps) {
  const [reason, setReason] = useState('');

  const handleClose = () => {
    if (!loading) {
      setReason('');
      onClose();
    }
  };

  const handleConfirm = () => {
    if (reason.trim().length >= 10) {
      onConfirm(reason.trim());
      setReason('');
    }
  };

  if (!request) return null;

  const isValid = reason.trim().length >= 10;

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && handleClose()}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <div className="flex items-start gap-4">
            <div className="flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-full bg-red-100 text-red-600">
              <XCircle className="h-6 w-6" />
            </div>
            <div className="flex-1">
              <DialogTitle className="text-lg font-semibold text-slate-900">
                Reject Extension Request
              </DialogTitle>
              <DialogDescription className="mt-2 text-sm text-slate-600">
                Please provide a reason for rejecting this extension request.
              </DialogDescription>
            </div>
          </div>
        </DialogHeader>

        <div className="mt-4">
          <Textarea
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            placeholder="Explain why you are rejecting this request..."
            rows={4}
            minLength={10}
            maxLength={1000}
            required
            className="border border-slate-300 bg-white text-slate-900"
          />
          <p className="mt-1 text-xs text-slate-500">
            {reason.length}/1000 characters (minimum 10)
          </p>
        </div>

        <DialogFooter className="mt-6 gap-3 sm:gap-3">
          <Button
            type="button"
            variant="ghost"
            onClick={handleClose}
            disabled={loading}
            className="flex-1 sm:flex-none"
          >
            Cancel
          </Button>
          <Button
            type="button"
            variant="danger"
            onClick={handleConfirm}
            loading={loading}
            disabled={!isValid || loading}
            className="flex-1 sm:flex-none"
          >
            Reject Request
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
