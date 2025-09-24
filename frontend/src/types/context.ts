import React from 'react';

// Toast Context Types
export type ToastType = 'success' | 'error' | 'info' | 'warning';

export interface Toast {
  id: string;
  type: ToastType;
  title: string;
  message?: string;
  duration?: number;
}

export interface ToastContextType {
  toasts: Toast[];
  showToast: (toast: Omit<Toast, 'id'>) => void;
  hideToast: (id: string) => void;
}

export interface ToastProviderProps {
  children: React.ReactNode;
}

export interface ToastContainerProps {
  toasts: Toast[];
  onHide: (id: string) => void;
}

export interface ToastItemProps {
  toast: Toast;
  onHide: (id: string) => void;
}
