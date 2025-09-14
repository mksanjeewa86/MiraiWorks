import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: 'standalone',
  poweredByHeader: false,
  experimental: {
    // Disable turbopack for now due to alias resolution issues
    turbo: {
      resolveAlias: {
        '@/*': './src/*',
      }
    }
  }
};

export default nextConfig;
