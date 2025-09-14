// Emergency utility to debug and fix auth issues
export const clearAuthData = () => {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    // Also clear any other auth-related data
    const keys = Object.keys(localStorage);
    keys.forEach(key => {
      if (key.includes('auth') || key.includes('token') || key.includes('user')) {
        localStorage.removeItem(key);
      }
    });
    console.log('Auth data cleared');
  }
};

// Debug function to check auth state
export const debugAuthState = () => {
  if (typeof window !== 'undefined') {
    console.log('=== Auth Debug ===');
    console.log('Current URL:', window.location.href);
    console.log('AccessToken:', localStorage.getItem('accessToken'));
    console.log('RefreshToken:', localStorage.getItem('refreshToken'));
    console.log('==================');
  }
};

// Call this in browser console if needed:
// import { clearAuthData } from './utils/authDebug'; clearAuthData(); window.location.reload();