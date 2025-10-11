import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
import createMiddleware from 'next-intl/middleware';
import { routing } from './i18n/config';

// Create the i18n middleware with routing config
const intlMiddleware = createMiddleware(routing);

export function middleware(request: NextRequest) {
  const isProd = process.env.NODE_ENV === 'production';

  // HTTPS enforcement in production
  if (isProd) {
    const protocol = request.headers.get('x-forwarded-proto');
    const isHttps = protocol === 'https';

    if (!isHttps) {
      const host = request.headers.get('host');
      if (host) {
        const url = new URL(request.url);
        url.protocol = 'https:';
        return NextResponse.redirect(url.toString(), 301);
      }
    }
  }

  // Apply internationalization
  const response = intlMiddleware(request);

  // Security headers are already set in next.config.ts
  return response;
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - Files with extensions (e.g., .png, .jpg)
     */
    '/((?!api|_next|_vercel|.*\\..*).*)',
  ],
  // Edge Runtime is used by default for middleware in Next.js 13+
};
