import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: 'standalone',
  poweredByHeader: false,
  turbopack: {
    resolveAlias: {
      '@/*': './src/*',
    }
  }
};

export default nextConfig;
