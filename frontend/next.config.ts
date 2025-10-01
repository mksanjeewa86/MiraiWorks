import type { NextConfig } from 'next';
import path from 'path';

const nextConfig: NextConfig = {
  poweredByHeader: false,
  output: 'standalone', // Required for Docker
  experimental: {
    optimizePackageImports: ['lucide-react', '@headlessui/react'],
  },
  webpack: (config, { dev }) => {
    // Ensure path aliases work in all environments (especially CI)
    config.resolve.alias = {
      ...config.resolve.alias,
      '@': path.resolve(__dirname, 'src'),
    };

    // Explicitly configure module resolution extensions for CI compatibility
    config.resolve.extensions = ['.tsx', '.ts', '.jsx', '.js', '.json'];

    if (dev) {
      // Improve chunk splitting for development
      config.optimization = {
        ...config.optimization,
        splitChunks: {
          chunks: 'all',
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
              chunks: 'all',
            },
          },
        },
      };
    }

    return config;
  },
};

export default nextConfig;
