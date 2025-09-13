import { z } from 'zod';

// Schema definitions (these should match the schemas defined in the components)
export const loginSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(6, 'Password must be at least 6 characters'),
});

export const registerSchema = z.object({
  firstName: z.string().min(1, 'First name is required'),
  lastName: z.string().min(1, 'Last name is required'),
  email: z.string().email('Invalid email address'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
  confirmPassword: z.string(),
  role: z.enum(['candidate', 'recruiter', 'employer']),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"],
});

export const forgotPasswordSchema = z.object({
  email: z.string().email('Invalid email address'),
});

export const resetPasswordSchema = z.object({
  password: z.string().min(8, 'Password must be at least 8 characters'),
  confirmPassword: z.string(),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"],
});

export const twoFactorSchema = z.object({
  code: z.string().length(6, 'Code must be 6 digits'),
});

// Form Data Types (Zod-inferred)
export type LoginFormData = z.infer<typeof loginSchema>;
export type RegisterFormData = z.infer<typeof registerSchema>;
export type ForgotPasswordFormData = z.infer<typeof forgotPasswordSchema>;
export type ResetPasswordFormData = z.infer<typeof resetPasswordSchema>;
export type TwoFactorFormData = z.infer<typeof twoFactorSchema>;

// Company Form Data
export interface CompanyFormData {
  name: string;
  type: 'recruiter' | 'employer';
  email: string;
  phone: string;
  website: string;
  postal_code: string;
  prefecture: string;
  city: string;
  description: string;
}

// User Form Data
export interface UserFormData {
  email: string;
  first_name: string;
  last_name: string;
  phone: string;
  company_id: string;
  role: string; // Changed from roles array to single role
  is_admin: boolean;
  require_2fa: boolean;
}