import type { NextConfig } from "next";
import path from "path";

const nextConfig: NextConfig = {
  output: 'standalone',
  poweredByHeader: false,
  // Turbopack configuration for development and modern environments
  turbopack: {
    resolveAlias: {
      '@': './src',
      '@/*': './src/*',
    }
  },
  // Webpack configuration as fallback for production builds
  webpack: (config, { dev, isServer, dir }) => {
    // Use dir parameter or process.cwd() for more reliable path resolution
    const projectRoot = dir || process.cwd();
    const srcPath = path.resolve(projectRoot, 'src');

    // Add alias configuration
    config.resolve.alias = {
      ...config.resolve.alias,
      '@': srcPath,
    };

    // Ensure proper resolution of @/ imports
    if (!config.resolve.fallback) {
      config.resolve.fallback = {};
    }

    return config;
  },
};

export default nextConfig;
