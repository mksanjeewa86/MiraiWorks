import { useState, useContext } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { AuthContext } from '../../contexts/AuthContext';
import Brand from '../../components/common/Brand';
import LoginForm from '../../components/auth/LoginForm';
import TwoFactorForm from '../../components/auth/TwoFactorForm';
import PasswordResetRequest from '../../components/auth/PasswordResetRequest';

export default function LoginPage() {
  const { isAuthenticated, user } = useContext(AuthContext);
  const location = useLocation();
  const [showTwoFactor, setShowTwoFactor] = useState(false);
  const [showPasswordReset, setShowPasswordReset] = useState(false);
  const [twoFactorError, setTwoFactorError] = useState<string | null>(null);
  
  const from = location.state?.from?.pathname || '/dashboard';

  // Redirect if already authenticated
  if (isAuthenticated) {
    return <Navigate to={from} replace />;
  }

  const handleLoginSuccess = () => {
    // Check if user needs 2FA (admin roles)
    const needsTwoFactor = user?.role && ['super_admin', 'company_admin'].includes(user.role);
    
    if (needsTwoFactor) {
      setShowTwoFactor(true);
    } else {
      // Navigation will be handled by auth context
    }
  };

  const handleTwoFactorSubmit = async (code: string) => {
    setTwoFactorError(null);
    
    try {
      // TODO: Verify 2FA code with API
      await new Promise(resolve => setTimeout(resolve, 1000)); // Mock API call
      
      // For demo, accept code "123456"
      if (code === '123456') {
        // Complete authentication - navigation handled by auth context
        console.log('2FA verification successful');
      } else {
        throw new Error('Invalid verification code');
      }
    } catch (error) {
      setTwoFactorError(error instanceof Error ? error.message : 'Verification failed');
      throw error;
    }
  };

  const handleTwoFactorResend = async () => {
    // TODO: Resend 2FA code
    await new Promise(resolve => setTimeout(resolve, 500)); // Mock API call
    console.log('2FA code resent');
  };

  const handlePasswordResetRequest = async (email: string) => {
    // TODO: Send password reset email
    await new Promise(resolve => setTimeout(resolve, 1000)); // Mock API call
    console.log('Password reset email sent to:', email);
  };

  const handleGoogleSSO = () => {
    // TODO: Implement Google SSO
    console.log('Google SSO clicked');
  };

  const handleOutlookSSO = () => {
    // TODO: Implement Microsoft/Outlook SSO
    console.log('Outlook SSO clicked');
  };

  return (
    <div className="min-h-screen flex flex-col justify-center py-12 sm:px-6 lg:px-8" style={{ background: 'linear-gradient(to bottom right, rgba(108, 99, 255, 0.05), rgba(108, 99, 255, 0.1))' }}>
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="text-center mb-8">
          <Brand className="justify-center mb-4" />
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white">
            Welcome back
          </h2>
          <p className="mt-2 text-sm text-muted-600 dark:text-muted-300">
            Sign in to access your dashboard
          </p>
        </div>
      </div>

      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="card py-8 px-6 shadow-2xl">
          {showTwoFactor ? (
            <TwoFactorForm
              onSubmit={handleTwoFactorSubmit}
              onResend={handleTwoFactorResend}
              error={twoFactorError}
            />
          ) : (
            <>
              <LoginForm
                onSuccess={handleLoginSuccess}
                onForgotPassword={() => setShowPasswordReset(true)}
              />

              <div className="mt-6">
                <div className="relative">
                  <div className="absolute inset-0 flex items-center">
                    <div className="w-full" style={{ borderTop: '1px solid var(--border-color)' }} />
                  </div>
                  <div className="relative flex justify-center text-sm">
                    <span className="px-2" style={{ backgroundColor: 'var(--bg-primary)', color: 'var(--text-muted)' }}>Or continue with</span>
                  </div>
                </div>

                <div className="mt-6 grid grid-cols-2 gap-3">
                  <button
                    onClick={handleGoogleSSO}
                    className="w-full inline-flex justify-center py-3 px-4 btn-secondary text-sm"
                    type="button"
                  >
                    <svg className="h-5 w-5" viewBox="0 0 24 24">
                      <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                      <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                      <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                      <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                    </svg>
                    <span className="ml-2">Google</span>
                  </button>

                  <button
                    onClick={handleOutlookSSO}
                    className="w-full inline-flex justify-center py-3 px-4 btn-secondary text-sm"
                    type="button"
                  >
                    <svg className="h-5 w-5" viewBox="0 0 24 24" fill="#0078D4">
                      <path d="M24 12.003h-5.25V24h-5.25V12.003H24zM12.75 0H0v12.003h12.75V0z"/>
                    </svg>
                    <span className="ml-2">Outlook</span>
                  </button>
                </div>
              </div>

              <div className="mt-6">
                <div className="relative">
                  <div className="absolute inset-0 flex items-center">
                    <div className="w-full" style={{ borderTop: '1px solid var(--border-color)' }} />
                  </div>
                  <div className="relative flex justify-center text-sm">
                    <span className="px-2" style={{ backgroundColor: 'var(--bg-primary)', color: 'var(--text-muted)' }}>New to MiraiWorks?</span>
                  </div>
                </div>

                <div className="mt-6">
                  <a
                    href="/register"
                    className="w-full flex justify-center py-3 px-4 btn-secondary text-sm text-brand-primary"
                  >
                    Create an account
                  </a>
                </div>
              </div>
            </>
          )}
        </div>
      </div>

      <PasswordResetRequest
        isOpen={showPasswordReset}
        onClose={() => setShowPasswordReset(false)}
        onSubmit={handlePasswordResetRequest}
      />
    </div>
  );
}