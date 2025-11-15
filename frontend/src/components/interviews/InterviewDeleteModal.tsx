'use client';

import React from 'react';
import { useTranslations } from 'next-intl';
import { AlertCircle, Trash2, X } from 'lucide-react';
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui';
import { Button } from '@/components/ui';

interface InterviewDeleteModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  interviewTitle: string;
  isDeleting?: boolean;
}

export default function InterviewDeleteModal({
  isOpen,
  onClose,
  onConfirm,
  interviewTitle,
  isDeleting = false,
}: InterviewDeleteModalProps) {
  const t = useTranslations('interviews.delete');

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <div className="flex items-start justify-between gap-4">
            <div className="flex items-start gap-4">
              <div className="flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-full bg-red-100">
                <AlertCircle className="h-6 w-6 text-red-600" />
              </div>
              <div className="flex-1">
                <DialogTitle className="text-xl font-semibold text-slate-900">
                  {t('title')}
                </DialogTitle>
                <DialogDescription className="mt-2 text-sm text-slate-600">
                  {t('confirm', { title: interviewTitle })}
                </DialogDescription>
              </div>
            </div>
            <DialogClose className="rounded-lg border border-slate-200 p-2 text-slate-400 transition hover:bg-slate-50 hover:text-slate-600 hover:border-slate-300">
              <X className="h-4 w-4" />
            </DialogClose>
          </div>
        </DialogHeader>

        <DialogFooter className="flex gap-3 pt-6">
          <Button
            type="button"
            onClick={onClose}
            variant="outline"
            disabled={isDeleting}
            className="flex-1"
          >
            {t('cancelButton')}
          </Button>
          <Button
            type="button"
            onClick={onConfirm}
            disabled={isDeleting}
            className="flex-1 bg-red-600 hover:bg-red-700 text-white whitespace-nowrap"
            leftIcon={<Trash2 className="h-4 w-4" />}
          >
            {isDeleting ? t('deleting') : t('confirmButton')}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
