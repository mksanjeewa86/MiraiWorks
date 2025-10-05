# FRONTEND SECURITY AUDIT REPORT
**MiraiWorks Application**
**Date:** 2025-10-05
**Auditor:** Claude Code Security Analysis

---

## EXECUTIVE SUMMARY

This comprehensive security audit identified **21 security vulnerabilities** across the frontend codebase, ranging from **Critical** to **Low** severity. The most significant concerns include insecure token storage, XSS vulnerabilities through unsanitized HTML rendering, missing CSRF protection, and insecure HTTP communication in development environments.

**Vulnerability Distribution:**
- **Critical:** 3 findings
- **High:** 8 findings
- **Medium:** 7 findings
- **Low:** 3 findings

---

## CRITICAL SEVERITY VULNERABILITIES

### 1. Insecure Token Storage in localStorage
**Severity:** CRITICAL
**Files Affected:**
- `frontend/src/contexts/AuthContext.tsx` (Lines 107-108, 127-129, 149-150, 177-178, 208-209, 221-222, 250-251, 269-270, 310-311, 324-325)
- `frontend/src/api/apiClient.ts` (Line 18)
- `frontend/src/api/exam.ts` (Lines 151, 172)

**Description:**
Access and refresh tokens are stored in `localStorage`, which is vulnerable to XSS attacks. LocalStorage is accessible by any JavaScript running on the page, making tokens vulnerable to theft through XSS vulnerabilities.

**Current Implementation:**
```typescript
// AuthContext.tsx
localStorage.setItem('accessToken', response.data!.access_token);
localStorage.setItem('refreshToken', response.data!.refresh_token);
const token = localStorage.getItem('accessToken');
```

**Risk:**
- Tokens can be stolen via XSS attacks
- No protection against CSRF attacks
- Tokens persist even after browser closure
- Accessible from browser developer tools

**Recommended Fix:**
1. **Use HttpOnly cookies for token storage** (backend implementation required)
2. **Implement secure cookie attributes:**
   - `HttpOnly` - prevents JavaScript access
   - `Secure` - only transmitted over HTTPS
   - `SameSite=Strict` - prevents CSRF attacks

**Backend Fix Example:**
```python
# Backend should set cookies instead of returning tokens in response body
response.set_cookie(
    key="access_token",
    value=access_token,
    httponly=True,
    secure=True,
    samesite="strict",
    max_age=3600
)
```

**Frontend Fix Example:**
```typescript
// Remove localStorage usage entirely - cookies are sent automatically
// No manual token storage/retrieval needed
const login = async (credentials: LoginCredentials) => {
  const response = await authApi.login(credentials);
  // Token is now in HttpOnly cookie, no need to store
  dispatch({ type: 'AUTH_SUCCESS', payload: response.data! });
};
```

---

### 2. XSS Vulnerability via Unsanitized HTML Rendering
**Severity:** CRITICAL
**Files Affected:**
- `frontend/src/app/resumes/[id]/preview/page.tsx` (Line 505)
- `frontend/src/app/public/resume/[slug]/page.tsx` (Line 278)
- `frontend/src/components/resume/ResumePreview.tsx` (Line 253)

**Description:**
Resume preview HTML is rendered using `dangerouslySetInnerHTML` without sanitization, allowing potential XSS attacks if malicious HTML is injected into resume data.

**Current Implementation:**
```typescript
<div
  className="resume-preview"
  dangerouslySetInnerHTML={{ __html: previewHtml }}
  style={{
    fontFamily: resume.font_family || 'Inter',
    ['--theme-color' as any]: resume.theme_color || '#2563eb',
  }}
/>
```

**Risk:**
- Malicious scripts can be injected through resume content
- User data could be exfiltrated
- Session hijacking possible
- Keylogging and form manipulation

**Recommended Fix:**
Install and use DOMPurify for HTML sanitization:

```bash
npm install dompurify
npm install --save-dev @types/dompurify
```

```typescript
import DOMPurify from 'dompurify';

// Sanitize HTML before rendering
const sanitizedHtml = DOMPurify.sanitize(previewHtml, {
  ALLOWED_TAGS: ['p', 'div', 'span', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li', 'strong', 'em', 'br'],
  ALLOWED_ATTR: ['class', 'style'],
  ALLOW_DATA_ATTR: false,
});

<div
  className="resume-preview"
  dangerouslySetInnerHTML={{ __html: sanitizedHtml }}
/>
```

**Alternative (Better) Solution:**
Generate resume HTML server-side with strict validation and templating, then return sanitized HTML from the backend.

---

### 3. Token Exposure in URL Parameters
**Severity:** CRITICAL
**Files Affected:**
- `frontend/src/hooks/useServerSentEvents.ts` (Line 19)

**Description:**
Authentication tokens are passed as URL query parameters in Server-Sent Events connections, which can be logged in server logs, browser history, and referrer headers.

**Current Implementation:**
```typescript
const sseUrl = `${url}?token=${encodeURIComponent(token)}`;
eventSourceRef.current = new EventSource(sseUrl);
```

**Risk:**
- Tokens visible in browser history
- Tokens logged in server access logs
- Tokens exposed in referrer headers
- Potential token theft from log files

**Recommended Fix:**
Use EventSource with custom headers (requires backend support) or upgrade to WebSocket with proper authentication:

```typescript
// Option 1: Use WebSocket instead of SSE for authenticated connections
const ws = new WebSocket(url);
ws.onopen = () => {
  ws.send(JSON.stringify({ type: 'auth', token }));
};

// Option 2: Use EventSource polyfill that supports headers
import { EventSourcePolyfill } from 'event-source-polyfill';

const eventSource = new EventSourcePolyfill(url, {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
```

---

## HIGH SEVERITY VULNERABILITIES

### 4. Missing CSRF Protection
**Severity:** HIGH
**Files Affected:** All API calls across the application

**Description:**
The application does not implement CSRF tokens for state-changing operations. While using Bearer tokens provides some protection, CSRF attacks are still possible if tokens are stored in localStorage.

**Risk:**
- Cross-Site Request Forgery attacks possible
- Unauthorized actions on behalf of authenticated users

**Recommended Fix:**
1. **Implement CSRF tokens for state-changing requests:**

```typescript
// apiClient.ts
const getCsrfToken = (): string | null => {
  // Get CSRF token from meta tag or cookie
  const meta = document.querySelector('meta[name="csrf-token"]');
  return meta?.getAttribute('content') || null;
};

export const makeAuthenticatedRequest = async <T>(
  url: string,
  options: RequestInit = {}
): Promise<{ data: T }> => {
  const csrfToken = getCsrfToken();

  const response = await fetch(`${API_CONFIG.BASE_URL}${url}`, {
    ...options,
    headers: {
      ...options.headers,
      ...(csrfToken && { 'X-CSRF-Token': csrfToken }),
    },
  });
  // ... rest of implementation
};
```

2. **Backend should validate CSRF tokens on all POST/PUT/PATCH/DELETE requests**

---

### 5. Insecure HTTP Communication in Development
**Severity:** HIGH
**Files Affected:**
- `frontend/.env.local` (Lines 2, 5)
- `frontend/src/api/config.ts` (Line 3)

**Description:**
API URLs use HTTP instead of HTTPS in development, and WebSocket uses WS instead of WSS.

**Current Implementation:**
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

**Risk:**
- Man-in-the-middle attacks possible
- Credentials and tokens transmitted in plaintext
- Data interception and manipulation

**Recommended Fix:**
```bash
# .env.local
NEXT_PUBLIC_API_URL=https://localhost:8000
NEXT_PUBLIC_WS_URL=wss://localhost:8000

# For production
NEXT_PUBLIC_API_URL=https://api.miraiworks.com
NEXT_PUBLIC_WS_URL=wss://api.miraiworks.com
```

**Backend Configuration:**
Set up SSL/TLS certificates for local development using mkcert:
```bash
mkcert -install
mkcert localhost 127.0.0.1 ::1
```

---

### 6. Sensitive Data Exposure in Console Logs
**Severity:** HIGH
**Files Affected:** 53 files across the codebase

**Description:**
Extensive use of `console.log`, `console.error`, and `console.warn` throughout the application, potentially logging sensitive data including tokens, user information, and API responses.

**Sample Locations:**
- `frontend/src/contexts/AuthContext.tsx` (Lines 183, 198, 203, 206, 215, 220, 274)
- `frontend/src/api/auth.ts` (Line 67)

**Current Implementation:**
```typescript
console.log('Verifying current token validity');
console.log('Token is valid, setting authenticated state');
console.error('Registration error:', error);
```

**Risk:**
- Sensitive data visible in browser console
- Information disclosure to attackers
- Production logs may contain PII

**Recommended Fix:**
1. **Create a secure logger utility:**

```typescript
// utils/logger.ts
const isDevelopment = process.env.NODE_ENV === 'development';

export const logger = {
  log: (...args: unknown[]) => {
    if (isDevelopment) console.log(...args);
  },
  error: (...args: unknown[]) => {
    // Always log errors, but sanitize sensitive data
    const sanitized = args.map(arg =>
      typeof arg === 'object' ? sanitizeObject(arg) : arg
    );
    console.error(...sanitized);
  },
  warn: (...args: unknown[]) => {
    if (isDevelopment) console.warn(...args);
  },
};

function sanitizeObject(obj: any): any {
  if (!obj) return obj;
  const sanitized = { ...obj };
  const sensitiveKeys = ['password', 'token', 'accessToken', 'refreshToken', 'secret'];

  for (const key of Object.keys(sanitized)) {
    if (sensitiveKeys.some(k => key.toLowerCase().includes(k))) {
      sanitized[key] = '[REDACTED]';
    }
  }
  return sanitized;
}
```

2. **Replace all console.* calls with logger:**
```typescript
// Before
console.log('Token is valid', token);

// After
logger.log('Token is valid');
```

---

### 7. Inconsistent Token Key Names
**Severity:** HIGH
**Files Affected:**
- `frontend/src/api/exam.ts` (Lines 151, 172)
- `frontend/src/app/exams/take/[examId]/page.tsx` (Line 79)

**Description:**
Some files use `access_token` instead of `accessToken` for localStorage, creating inconsistency and potential authentication failures.

**Current Implementation:**
```typescript
// exam.ts - WRONG
Authorization: `Bearer ${localStorage.getItem('access_token')}`

// apiClient.ts - CORRECT
return localStorage.getItem('accessToken');
```

**Risk:**
- Authentication failures
- Token not found errors
- Inconsistent behavior across features

**Recommended Fix:**
```typescript
// Standardize on 'accessToken' everywhere
Authorization: `Bearer ${localStorage.getItem('accessToken')}`
```

---

### 8. Missing Content Security Policy
**Severity:** HIGH
**Files Affected:** Next.js configuration

**Description:**
No Content Security Policy (CSP) headers are configured, leaving the application vulnerable to XSS and data injection attacks.

**Risk:**
- XSS attacks easier to execute
- No restriction on resource loading
- Inline scripts can be injected

**Recommended Fix:**
Add CSP headers in `next.config.ts`:

```typescript
const nextConfig: NextConfig = {
  // ... existing config
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'Content-Security-Policy',
            value: [
              "default-src 'self'",
              "script-src 'self' 'unsafe-eval' 'unsafe-inline'", // Adjust based on needs
              "style-src 'self' 'unsafe-inline'",
              "img-src 'self' data: https:",
              "font-src 'self' data:",
              "connect-src 'self' https://api.miraiworks.com wss://api.miraiworks.com",
              "frame-ancestors 'none'",
              "base-uri 'self'",
              "form-action 'self'"
            ].join('; ')
          },
          {
            key: 'X-Frame-Options',
            value: 'DENY'
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff'
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin'
          },
          {
            key: 'Permissions-Policy',
            value: 'camera=(), microphone=(), geolocation=()'
          }
        ],
      },
    ];
  },
};
```

---

### 9. Missing Input Validation on File Uploads
**Severity:** HIGH
**Files Affected:**
- `frontend/src/api/todo-attachments.ts` (Lines 17-79)
- `frontend/src/services/file.service.ts` (Lines 10-48)

**Description:**
File upload services have validation constants defined but limited client-side validation enforcement. File type checking is present but could be bypassed.

**Current Implementation:**
```typescript
private readonly DEFAULT_MAX_SIZE = 10 * 1024 * 1024; // 10MB
private readonly DEFAULT_ALLOWED_TYPES = [
  'image/jpeg',
  'image/png',
  // ...
];
```

**Risk:**
- Malicious files could be uploaded
- File size limits could be exceeded
- Server resource exhaustion

**Recommended Fix:**
```typescript
async uploadFile(
  todoId: number,
  file: File,
  description?: string,
  onProgress?: (progress: number) => void
): Promise<FileUploadResponse> {
  // Validate file before upload
  if (!this.validateFile(file)) {
    throw new Error('Invalid file type or size');
  }

  // Check file extension matches MIME type
  if (!this.validateFileExtension(file)) {
    throw new Error('File extension does not match content type');
  }

  // ... proceed with upload
}

private validateFile(file: File): boolean {
  const MAX_SIZE = 10 * 1024 * 1024; // 10MB
  const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'application/pdf'];

  if (file.size > MAX_SIZE) {
    toast.error(`File size exceeds ${MAX_SIZE / 1024 / 1024}MB limit`);
    return false;
  }

  if (!ALLOWED_TYPES.includes(file.type)) {
    toast.error('File type not allowed');
    return false;
  }

  return true;
}

private validateFileExtension(file: File): boolean {
  const extension = file.name.split('.').pop()?.toLowerCase();
  const mimeToExtension: Record<string, string[]> = {
    'image/jpeg': ['jpg', 'jpeg'],
    'image/png': ['png'],
    'application/pdf': ['pdf'],
  };

  const allowedExtensions = mimeToExtension[file.type] || [];
  return extension ? allowedExtensions.includes(extension) : false;
}
```

---

### 10. Weak Password Validation
**Severity:** HIGH
**Files Affected:**
- `frontend/src/app/auth/register/page.tsx` (Lines 16-22)

**Description:**
Password validation regex exists but could be stronger. Current regex requires at least one uppercase, lowercase, number, and special character, but doesn't prevent common passwords.

**Current Implementation:**
```typescript
password: z
  .string()
  .min(8, 'Password must be at least 8 characters')
  .regex(
    /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/,
    'Password must contain at least one uppercase letter, one lowercase letter, one number, and one special character'
  ),
```

**Risk:**
- Weak passwords can be set
- No protection against common passwords
- No minimum complexity enforcement

**Recommended Fix:**
```typescript
import zxcvbn from 'zxcvbn'; // Install: npm install zxcvbn

const passwordSchema = z
  .string()
  .min(12, 'Password must be at least 12 characters') // Increase from 8
  .regex(
    /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&^#()])[A-Za-z\d@$!%*?&^#()]/,
    'Password must contain uppercase, lowercase, number, and special character'
  )
  .refine((password) => {
    const result = zxcvbn(password);
    return result.score >= 3; // Require score of 3 or higher (0-4 scale)
  }, {
    message: 'Password is too weak. Please use a stronger password.',
  })
  .refine((password) => {
    const commonPasswords = ['Password123!', 'Welcome123!', 'Admin123!'];
    return !commonPasswords.includes(password);
  }, {
    message: 'This password is too common. Please choose a different one.',
  });
```

---

### 11. Direct URL Manipulation for Navigation
**Severity:** HIGH
**Files Affected:**
- `frontend/src/contexts/AuthContext.tsx` (Lines 113, 338)

**Description:**
Using `window.location.href` for navigation bypasses Next.js router and can lead to security issues.

**Current Implementation:**
```typescript
if (typeof window !== 'undefined') {
  window.location.href = '/auth/login';
}
```

**Risk:**
- Open redirect vulnerabilities
- State not properly cleared
- Browser history manipulation

**Recommended Fix:**
```typescript
import { useRouter } from 'next/navigation';

const router = useRouter();

// Instead of window.location.href
router.push('/auth/login');
router.replace('/auth/login'); // For logout (no back navigation)
```

---

## MEDIUM SEVERITY VULNERABILITIES

### 12. Missing Security Headers
**Severity:** MEDIUM
**Files Affected:** `next.config.ts`

**Description:**
The Next.js configuration includes `poweredByHeader: false` but is missing other important security headers.

**Recommended Fix:**
See Vulnerability #8 for complete security headers configuration.

---

### 13. Insecure WebRTC Configuration
**Severity:** MEDIUM
**Files Affected:**
- `frontend/src/hooks/useWebRTC.ts` (Lines 21-25, 131-134)

**Description:**
WebRTC uses only public STUN servers and constructs WebSocket URLs dynamically, potentially exposing connections to eavesdropping.

**Current Implementation:**
```typescript
const iceServers = [
  { urls: 'stun:stun.l.google.com:19302' },
  { urls: 'stun:stun1.l.google.com:19302' },
  // Add TURN servers in production
];

const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const wsUrl = `${protocol}//${host}:${port}/ws/video/${roomId}`;
```

**Risk:**
- No TURN servers for NAT traversal
- Insecure WebSocket in development
- Potential connection failures

**Recommended Fix:**
```typescript
const getIceServers = () => {
  const isDev = process.env.NODE_ENV === 'development';

  return [
    { urls: 'stun:stun.l.google.com:19302' },
    // Add TURN servers for production
    ...(isDev ? [] : [
      {
        urls: 'turn:turn.miraiworks.com:3478',
        username: 'user',
        credential: 'pass'
      }
    ])
  ];
};

// Always use secure protocol in production
const getWebSocketUrl = () => {
  const isProd = process.env.NODE_ENV === 'production';
  const protocol = isProd ? 'wss:' : (window.location.protocol === 'https:' ? 'wss:' : 'ws:');
  const host = isProd ? 'api.miraiworks.com' : window.location.hostname;
  const port = isProd ? '' : ':8000';

  return `${protocol}//${host}${port}/ws/video/${roomId}${userId ? `?user_id=${userId}` : ''}`;
};
```

---

### 14. No Rate Limiting on Client Side
**Severity:** MEDIUM
**Files Affected:** All API client files

**Description:**
No client-side rate limiting or request throttling implemented, potentially allowing abuse or DDoS attacks.

**Recommended Fix:**
```typescript
// utils/rateLimiter.ts
class RateLimiter {
  private requests: Map<string, number[]> = new Map();
  private readonly maxRequests: number;
  private readonly timeWindow: number;

  constructor(maxRequests: number = 100, timeWindowMs: number = 60000) {
    this.maxRequests = maxRequests;
    this.timeWindow = timeWindowMs;
  }

  canMakeRequest(key: string): boolean {
    const now = Date.now();
    const timestamps = this.requests.get(key) || [];

    // Remove old timestamps
    const validTimestamps = timestamps.filter(
      time => now - time < this.timeWindow
    );

    if (validTimestamps.length >= this.maxRequests) {
      return false;
    }

    validTimestamps.push(now);
    this.requests.set(key, validTimestamps);
    return true;
  }
}

export const apiRateLimiter = new RateLimiter();

// In apiClient.ts
export const makeAuthenticatedRequest = async <T>(
  url: string,
  options: RequestInit = {}
): Promise<{ data: T }> => {
  if (!apiRateLimiter.canMakeRequest(url)) {
    throw new Error('Rate limit exceeded. Please try again later.');
  }

  // ... rest of implementation
};
```

---

### 15. Missing Request Timeout Configuration
**Severity:** MEDIUM
**Files Affected:**
- `frontend/src/api/config.ts`

**Description:**
API configuration defines a timeout constant but it's not consistently applied across all API calls.

**Current Implementation:**
```typescript
export const API_CONFIG = {
  BASE_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  TIMEOUT: 30000, // 30 seconds - defined but not used
  RETRY_ATTEMPTS: 3,
} as const;
```

**Recommended Fix:**
```typescript
// apiClient.ts
export const makeAuthenticatedRequest = async <T>(
  url: string,
  options: RequestInit = {}
): Promise<{ data: T }> => {
  const controller = new AbortController();
  const timeoutId = setTimeout(
    () => controller.abort(),
    API_CONFIG.TIMEOUT
  );

  try {
    const response = await fetch(`${API_CONFIG.BASE_URL}${url}`, {
      ...options,
      signal: controller.signal,
      // ... rest of options
    });

    clearTimeout(timeoutId);
    return response;
  } catch (error) {
    clearTimeout(timeoutId);
    if (error.name === 'AbortError') {
      throw new Error('Request timeout. Please try again.');
    }
    throw error;
  }
};
```

---

### 16. Potential Race Conditions in Auth State
**Severity:** MEDIUM
**Files Affected:**
- `frontend/src/contexts/AuthContext.tsx` (Lines 165-228)

**Description:**
The auth initialization effect doesn't prevent multiple concurrent initializations, potentially causing race conditions.

**Current Implementation:**
```typescript
useEffect(() => {
  let isInitialized = false;

  const initAuth = async () => {
    if (isInitialized) return;
    isInitialized = true;
    // ... auth logic
  };

  initAuth();
}, []);
```

**Risk:**
- Multiple simultaneous auth checks
- Race conditions on token refresh
- Inconsistent auth state

**Recommended Fix:**
```typescript
useEffect(() => {
  let isMounted = true;
  let isInitializing = false;

  const initAuth = async () => {
    if (isInitializing || !isMounted) return;
    isInitializing = true;

    try {
      // ... auth logic
    } finally {
      isInitializing = false;
    }
  };

  initAuth();

  return () => {
    isMounted = false;
  };
}, []);
```

---

### 17. Exposed API Endpoints in Client Code
**Severity:** MEDIUM
**Files Affected:**
- `frontend/src/api/config.ts`

**Description:**
All API endpoints are exposed in client-side code, making it easier for attackers to discover the API structure.

**Risk:**
- API structure easily discoverable
- Easier to find attack vectors
- Admin endpoints exposed

**Mitigation:**
While this is difficult to fully prevent in SPAs, implement:
1. **Backend authorization checks** on all endpoints
2. **Rate limiting** on sensitive endpoints
3. **API endpoint obfuscation** for admin routes

---

### 18. No HTTPS Enforcement
**Severity:** MEDIUM
**Files Affected:** Next.js configuration

**Description:**
No automatic redirect from HTTP to HTTPS configured.

**Recommended Fix:**
```typescript
// middleware.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const isProd = process.env.NODE_ENV === 'production';
  const isHttps = request.headers.get('x-forwarded-proto') === 'https';

  if (isProd && !isHttps) {
    return NextResponse.redirect(
      `https://${request.headers.get('host')}${request.nextUrl.pathname}`,
      301
    );
  }

  return NextResponse.next();
}
```

---

## LOW SEVERITY VULNERABILITIES

### 19. No Dependency Vulnerability Monitoring
**Severity:** LOW
**Description:**
While current npm audit shows no vulnerabilities, there's no automated monitoring setup.

**Recommended Fix:**
```json
// package.json
{
  "scripts": {
    "audit": "npm audit",
    "audit:fix": "npm audit fix",
    "precommit": "npm audit && npm run lint && npm run typecheck"
  }
}
```

Add GitHub Actions workflow:
```yaml
# .github/workflows/security-audit.yml
name: Security Audit
on: [push, pull_request]
jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
      - run: npm audit --audit-level=moderate
```

---

### 20. Missing Error Boundary Implementation
**Severity:** LOW
**Description:**
No global error boundary to catch and handle React errors securely.

**Recommended Fix:**
```typescript
// components/ErrorBoundary.tsx
'use client';

import React, { Component, ReactNode } from 'react';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    // Log to error reporting service (sanitize sensitive data)
    console.error('Error caught by boundary:', {
      message: error.message,
      stack: error.stack,
      componentStack: errorInfo.componentStack,
    });
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-boundary">
          <h2>Something went wrong</h2>
          <p>Please refresh the page or contact support.</p>
          {/* Don't show error details to users in production */}
        </div>
      );
    }

    return this.props.children;
  }
}
```

---

### 21. No Security.txt File
**Severity:** LOW
**Description:**
Missing security.txt file for responsible disclosure.

**Recommended Fix:**
Create `public/.well-known/security.txt`:
```
Contact: security@miraiworks.com
Expires: 2026-12-31T23:59:59.000Z
Encryption: https://miraiworks.com/pgp-key.txt
Preferred-Languages: en, ja
Canonical: https://miraiworks.com/.well-known/security.txt
Policy: https://miraiworks.com/security-policy
```

---

## SUMMARY OF RECOMMENDATIONS

### Immediate Actions (Critical Priority)
1. ✅ **Migrate from localStorage to HttpOnly cookies** for token storage
2. ✅ **Implement DOMPurify** for HTML sanitization
3. ✅ **Remove token from URL parameters** in SSE connections
4. ✅ **Fix token key inconsistency** (access_token vs accessToken)
5. ✅ **Add Content Security Policy** headers

### Short-term Actions (High Priority)
6. ✅ **Implement CSRF protection** with tokens
7. ✅ **Set up HTTPS/WSS** for all environments
8. ✅ **Remove/sanitize console.log** statements
9. ✅ **Add file upload validation**
10. ✅ **Strengthen password requirements**
11. ✅ **Use Next.js router** instead of window.location

### Medium-term Actions (Medium Priority)
12. ✅ **Configure security headers** (X-Frame-Options, etc.)
13. ✅ **Set up TURN servers** for WebRTC
14. ✅ **Implement client-side rate limiting**
15. ✅ **Add request timeout handling**
16. ✅ **Fix auth race conditions**

### Long-term Actions (Low Priority)
17. ✅ **Set up automated security monitoring**
18. ✅ **Implement error boundaries**
19. ✅ **Create security.txt** file

---

## TESTING RECOMMENDATIONS

After implementing fixes, perform:

1. **XSS Testing:**
   - Test all input fields with XSS payloads
   - Verify DOMPurify sanitization
   - Check CSP headers

2. **Authentication Testing:**
   - Verify token security
   - Test session timeout
   - Check CSRF protection

3. **Network Security:**
   - Verify HTTPS enforcement
   - Test WebSocket security
   - Check CORS configuration

4. **Input Validation:**
   - Test file upload restrictions
   - Verify password complexity
   - Check API input validation

---

**End of Security Audit Report**
