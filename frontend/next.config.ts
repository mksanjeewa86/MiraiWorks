import type { NextConfig } from "next";
import path from "path";

const isCI = process.env.CI === 'true' || process.env.GITHUB_ACTIONS === 'true';

const nextConfig: NextConfig = {
  output: 'standalone',
  poweredByHeader: false,
  // Only use Turbopack in non-CI environments
  ...(isCI ? {} : {
    turbopack: {
      resolveAlias: {
        '@': './src',
        '@/*': './src/*',
      }
    }
  }),
  // Simplified webpack configuration for CI
  webpack: (config, { dev, isServer, dir }) => {
    if (isCI) {
      // Minimal configuration for CI - let Next.js handle aliasing via tsconfig
      return config;
    }

    // Full configuration for development
    const projectRoot = dir || process.cwd();
    const srcPath = path.resolve(projectRoot, 'src');

    config.resolve.alias = {
      ...config.resolve.alias,
      '@': srcPath,
    };

    return config;
  },
};

export default nextConfig;
