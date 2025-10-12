'use client';

import { useAuth } from '@/contexts/AuthContext';
import { Card } from '@/components/ui';
import { Building, Mail, Phone, Briefcase } from 'lucide-react';

interface EmployerProfileViewProps {
  userId?: number;
  isOwnProfile?: boolean;
  readOnly?: boolean;
}

export default function EmployerProfileView({
  userId,
  isOwnProfile = true,
  readOnly = false,
}: EmployerProfileViewProps) {
  const { user } = useAuth();

  if (!user) return null;

  return (
    <div className="space-y-6">
      {/* Basic Info Card */}
      <Card className="p-6">
        <h2 className="text-xl font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>
          Professional Information
        </h2>

        <div className="flex items-center gap-2 mb-3">
          <Briefcase className="h-5 w-5" style={{ color: 'var(--text-muted)' }} />
          <span className="text-base" style={{ color: 'var(--text-secondary)' }}>
            {user.full_name}
          </span>
        </div>

        <p className="mt-4 text-sm" style={{ color: 'var(--text-muted)' }}>
          Company Representative
        </p>
      </Card>

      {/* Company Info Card */}
      {user.company && (
        <Card className="p-6">
          <h2 className="text-xl font-semibold mb-4 flex items-center gap-2" style={{ color: 'var(--text-primary)' }}>
            <Building className="h-5 w-5" />
            Company
          </h2>

          <div className="space-y-2">
            <div>
              <span className="font-medium text-lg" style={{ color: 'var(--text-primary)' }}>
                {user.company.name}
              </span>
            </div>

            <div className="text-sm" style={{ color: 'var(--text-muted)' }}>
              <span className="font-medium">Company ID: </span>
              {user.company.id}
            </div>
          </div>
        </Card>
      )}

      {/* Contact Information */}
      <Card className="p-6">
        <h2 className="text-xl font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>
          Contact
        </h2>

        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <Mail className="h-4 w-4" style={{ color: 'var(--text-muted)' }} />
            <a
              href={`mailto:${user.email}`}
              className="text-blue-600 dark:text-blue-400 hover:underline text-sm"
            >
              {user.email}
            </a>
          </div>

          {user.phone && (
            <div className="flex items-center gap-2">
              <Phone className="h-4 w-4" style={{ color: 'var(--text-muted)' }} />
              <a
                href={`tel:${user.phone}`}
                className="text-blue-600 dark:text-blue-400 hover:underline text-sm"
              >
                {user.phone}
              </a>
            </div>
          )}
        </div>
      </Card>

      {/* Empty State Message */}
      <Card className="p-6 text-center">
        <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
          Employer profiles are focused on company representation. For detailed profile information, please refer to the company profile page.
        </p>
      </Card>
    </div>
  );
}
