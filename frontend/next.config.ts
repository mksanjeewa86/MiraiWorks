import type { NextConfig } from 'next';
import path from 'path';
import createNextIntlPlugin from 'next-intl/plugin';

// Configure next-intl plugin
const withNextIntl = createNextIntlPlugin('./src/i18n/request.ts');

const nextConfig: NextConfig = {
  poweredByHeader: false,
  output: 'standalone', // Required for Docker
  experimental: {
    optimizePackageImports: ['lucide-react', '@headlessui/react'],
  },
  // Allow cross-origin requests in development from network IPs
  allowedDevOrigins: [
    'http://192.168.150.156:3000',
    'http://localhost:3000',
  ],
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'Content-Security-Policy',
            value: [
              "default-src 'self'",
              "script-src 'self' 'unsafe-eval' 'unsafe-inline'",
              "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
              "img-src 'self' data: https: blob: http://localhost:8000",
              "font-src 'self' data: https://fonts.gstatic.com",
              "connect-src 'self' http://localhost:8000 ws://localhost:8000 https://api.miraiworks.com wss://api.miraiworks.com",
              "worker-src 'self' blob:",
              "child-src 'self' blob:",
              "frame-ancestors 'none'",
              "base-uri 'self'",
              "form-action 'self'",
            ].join('; '),
          },
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin',
          },
          {
            key: 'Permissions-Policy',
            value: 'camera=(), microphone=(), geolocation=()',
          },
          {
            key: 'X-XSS-Protection',
            value: '1; mode=block',
          },
        ],
      },
    ];
  },
  webpack: (config, { dev }) => {
    // Ensure path aliases work in all environments (especially CI)
    config.resolve.alias = {
      ...config.resolve.alias,
      '@': path.resolve(__dirname, 'src'),
    };

    // Explicitly configure module resolution extensions for CI compatibility
    config.resolve.extensions = [
      ...(config.resolve.extensions || []),
      '.tsx',
      '.ts',
      '.jsx',
      '.js',
      '.json',
    ];

    if (dev) {
      // Improve chunk splitting for development
      config.optimization = {
        ...config.optimization,
        splitChunks: {
          chunks: (chunk: { name?: string }) => {
            // Exclude middleware from chunk splitting (Edge Runtime compatibility)
            return chunk.name !== 'middleware';
          },
          cacheGroups: {
            default: {
              minChunks: 2,
              priority: -20,
              reuseExistingChunk: true,
            },
            vendor: {
              test: /[\\/]node_modules[\\/]/,
              name: 'vendors',
              priority: -10,
            },
          },
        },
      };
    }

    return config;
  },
};

export default withNextIntl(nextConfig);
