import type { NextConfig } from "next";
import path from "path";

const nextConfig: NextConfig = {
  output: 'standalone',
  poweredByHeader: false,
  // Turbopack configuration for development and modern environments
  turbopack: {
    resolveAlias: {
      '@': path.resolve(__dirname, './src'),
      '@/*': './src/*',
    }
  },
  // Webpack configuration as fallback for production builds
  webpack: (config) => {
    config.resolve.alias = {
      ...config.resolve.alias,
      '@': path.resolve(__dirname, './src'),
    };
    return config;
  },
};

export default nextConfig;
