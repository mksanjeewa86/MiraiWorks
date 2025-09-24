import { type ButtonHTMLAttributes, type InputHTMLAttributes, type ReactNode } from 'react';

// Button Component Types
export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger' | 'destructive' | 'default';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
  leftIcon?: ReactNode;
  rightIcon?: ReactNode;
  fullWidth?: boolean;
  asChild?: boolean;
}

// Input Component Types
export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  leftIcon?: ReactNode;
  rightIcon?: ReactNode;
  fullWidth?: boolean;
}

// Color Scheme Types for Role-based UI
export interface ColorScheme {
  // Main sidebar background and borders
  background: string;
  backgroundOverlay: string;
  border: string;
  headerBackground: string;

  // Brand/logo colors
  brandBackground: string;
  brandAccent: string;

  // Text colors
  textPrimary: string;
  textSecondary: string;

  // Button and navigation colors
  buttonBorder: string;
  buttonHover: string;
  buttonActive: string;

  // User avatar background
  avatarBackground: string;
  avatarRing: string;

  // Active indicators
  activeIndicator: string;
  activeIndicatorShadow: string;

  // Status indicator
  statusIndicator: string;
  statusIndicatorShadow: string;
}
