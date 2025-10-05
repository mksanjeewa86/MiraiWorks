import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

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

  // Security headers are already set in next.config.ts
  return NextResponse.next();
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
  // Edge Runtime is used by default for middleware in Next.js 13+
};
