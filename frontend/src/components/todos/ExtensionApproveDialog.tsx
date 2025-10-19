'use client';

import { CheckCircle2 } from 'lucide-react';
import ConfirmDialog from '@/components/ui/ConfirmDialog';
import type { TodoExtensionRequest } from '@/types/todo';

interface ExtensionApproveDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  request: TodoExtensionRequest | null;
  loading?: boolean;
}

export default function ExtensionApproveDialog({
  isOpen,
  onClose,
  onConfirm,
  request,
  loading = false,
}: ExtensionApproveDialogProps) {
  if (!request) return null;

  const requestedDate = new Date(request.requested_due_date);

  return (
    <ConfirmDialog
      isOpen={isOpen}
      onClose={onClose}
      onConfirm={onConfirm}
      title="Approve Extension Request"
      description={`Are you sure you want to approve this extension request? The due date will be changed to ${requestedDate.toLocaleString()}.`}
      confirmText="Approve"
      cancelText="Cancel"
      variant="info"
      loading={loading}
    />
  );
}
