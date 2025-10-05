# Security Best Practices - Quick Reference

**For MiraiWorks Developers**

---

## 🛡️ MANDATORY SECURITY RULES

### 1. ❌ NEVER Use `dangerouslySetInnerHTML` Without Sanitization

**Bad:**
```typescript
<div dangerouslySetInnerHTML={{ __html: userContent }} />
```

**Good:**
```typescript
import DOMPurify from 'dompurify';

<div dangerouslySetInnerHTML={{
  __html: DOMPurify.sanitize(userContent, {
    ALLOWED_TAGS: ['p', 'div', 'span', 'h1', 'h2', 'h3', 'strong', 'em'],
    ALLOWED_ATTR: ['class', 'style'],
    ALLOW_DATA_ATTR: false,
  })
}} />
```

---

### 2. ❌ NEVER Log Sensitive Data

**Bad:**
```typescript
console.log('User authenticated', { token, password, user });
```

**Good:**
```typescript
import { logger } from '@/utils/logger';

logger.log('User authenticated');  // Automatically sanitizes sensitive data
```

---

### 3. ❌ NEVER Put Tokens in URLs

**Bad:**
```typescript
const url = `/api/endpoint?token=${token}`;
fetch(url);
```

**Good:**
```typescript
fetch('/api/endpoint', {
  headers: {
    Authorization: `Bearer ${token}`
  }
});
```

---

### 4. ✅ ALWAYS Validate File Uploads

**Bad:**
```typescript
const handleUpload = (file: File) => {
  uploadFile(file);  // No validation!
};
```

**Good:**
```typescript
import { fileService } from '@/services/file.service';

const handleUpload = async (file: File) => {
  try {
    await fileService.validateAndUpload(file, {
      maxSize: 10 * 1024 * 1024,  // 10MB
      allowedTypes: ['image/jpeg', 'image/png', 'application/pdf'],
    });
  } catch (error) {
    toast.error('File upload failed: ' + error.message);
  }
};
```

---

### 5. ✅ ALWAYS Use `accessToken` (Not `access_token`)

**Bad:**
```typescript
localStorage.getItem('access_token');  // Inconsistent!
```

**Good:**
```typescript
localStorage.getItem('accessToken');  // Standardized
```

---

### 6. ✅ ALWAYS Use Next.js Router for Navigation

**Bad:**
```typescript
window.location.href = '/login';  // Security risk!
```

**Good:**
```typescript
import { useRouter } from 'next/navigation';

const router = useRouter();
router.push('/login');
```

---

## 📋 SECURITY CHECKLIST FOR NEW FEATURES

Before submitting a PR, verify:

- [ ] No `dangerouslySetInnerHTML` without DOMPurify
- [ ] No sensitive data in console.log (use logger utility)
- [ ] No tokens in URL parameters
- [ ] File uploads have proper validation
- [ ] Using `accessToken` consistently
- [ ] Using Next.js router for navigation
- [ ] No hardcoded secrets or API keys
- [ ] Input validation on all user inputs
- [ ] Error messages don't reveal sensitive info

---

## 🔐 COMMON SECURITY PATTERNS

### Pattern 1: Safe HTML Rendering

```typescript
import DOMPurify from 'dompurify';

const SafeHtmlRenderer = ({ html }: { html: string }) => {
  const sanitized = DOMPurify.sanitize(html, {
    ALLOWED_TAGS: ['p', 'div', 'span', 'strong', 'em', 'br'],
    ALLOWED_ATTR: ['class', 'style'],
  });

  return <div dangerouslySetInnerHTML={{ __html: sanitized }} />;
};
```

---

### Pattern 2: Secure API Calls

```typescript
import { apiClient } from '@/api/apiClient';

// Good - uses centralized API client with auth
const fetchData = async () => {
  const response = await apiClient.get('/api/users');
  return response.data;
};

// Bad - manual fetch without auth handling
const fetchData = async () => {
  const response = await fetch('/api/users');
  return response.json();
};
```

---

### Pattern 3: Secure File Upload

```typescript
import { fileService } from '@/services/file.service';

const uploadWithValidation = async (file: File) => {
  // Automatic validation + upload
  return await fileService.validateAndUpload(file, {
    maxSize: 5 * 1024 * 1024,  // 5MB
    allowedTypes: ['image/jpeg', 'image/png'],
  });
};
```

---

### Pattern 4: Secure Logging

```typescript
import { logger } from '@/utils/logger';

// Development only, auto-sanitizes sensitive data
logger.log('Processing payment', { orderId: 123, amount: 50.00 });

// Errors always logged (but sanitized)
logger.error('Payment failed', error);

// Grouped logs for better debugging
logger.group('User Registration', () => {
  logger.log('Step 1: Validate input');
  logger.log('Step 2: Check email availability');
  logger.log('Step 3: Create account');
});
```

---

## 🚨 SECURITY RED FLAGS

Watch out for these in code reviews:

### 🔴 Critical Issues
- `dangerouslySetInnerHTML` without sanitization
- Tokens in URL parameters or query strings
- Passwords or secrets in code
- SQL queries with string concatenation
- `eval()` or `Function()` with user input

### 🟠 High Priority Issues
- Missing input validation
- Console.log with potentially sensitive data
- No file upload restrictions
- Missing authentication checks
- Direct database access from frontend

### 🟡 Medium Priority Issues
- Generic error messages exposing system details
- No rate limiting on API calls
- Missing request timeouts
- Inconsistent error handling

---

## 📚 SECURITY RESOURCES

### Internal Documentation
- **Security Audit Report:** `SECURITY_AUDIT_FRONTEND.md`
- **Security Fixes:** `SECURITY_FIXES_IMPLEMENTED.md`
- **Architecture Rules:** `CLAUDE.md`

### External Resources
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/)
- [MDN Web Security](https://developer.mozilla.org/en-US/docs/Web/Security)
- [Next.js Security](https://nextjs.org/docs/advanced-features/security-headers)

---

## 🛠️ SECURITY TOOLS

### Available in Project
- **DOMPurify** - HTML sanitization
- **Secure Logger** - `@/utils/logger`
- **File Service** - `@/services/file.service`
- **API Client** - `@/api/apiClient` (centralized auth)

### Recommended Extensions
- **ESLint Security Plugin** - Catches security issues
- **SonarLint** - Code quality and security

### CLI Tools
```bash
# Audit dependencies
npm audit

# Fix auto-fixable vulnerabilities
npm audit fix

# Check for outdated packages
npm outdated
```

---

## 💡 QUICK TIPS

1. **Default to Secure** - When in doubt, choose the more secure option
2. **Validate Everything** - Never trust user input
3. **Sanitize Output** - Always sanitize before rendering user content
4. **Use Libraries** - Don't roll your own crypto/auth/sanitization
5. **Least Privilege** - Only request permissions you need
6. **Defense in Depth** - Multiple layers of security
7. **Security by Design** - Consider security from the start
8. **Regular Updates** - Keep dependencies up to date

---

## ❓ WHEN IN DOUBT

If you're unsure about security:

1. **Check this guide** for common patterns
2. **Ask in code review** - security is everyone's responsibility
3. **Consult OWASP** documentation
4. **Test with security in mind** - try to break your own code
5. **Use established libraries** rather than custom solutions

---

## 🎯 SECURITY GOALS

Our security standards:

- ✅ **Zero** critical vulnerabilities in production
- ✅ **All** user input validated and sanitized
- ✅ **All** sensitive data encrypted in transit (HTTPS)
- ✅ **All** authentication properly implemented
- ✅ **All** file uploads validated and restricted
- ✅ **Regular** security audits and dependency updates

---

**Remember: Security is not a feature, it's a requirement!**

---

*Last Updated: 2025-10-05*
*Maintained by: Development Team*
