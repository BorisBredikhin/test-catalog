import type { NextConfig } from "next";

const MINIO_PUBLIC_URL = process.env.MINIO_PUBLIC_URL ?? "http://minio:9000";

const nextConfig: NextConfig = {
  /* config options here */
  cacheComponents: true,
  output: "standalone",
  partialPrefetching: true,
  async rewrites() {
    return [
      {
        source: "/catalog/:path*",
        destination: `${MINIO_PUBLIC_URL}/catalog/:path*`,
      },
    ];
  },
  turbopack: {
    rules: {
      "*.css": {
        loaders: ["@tailwindcss/turbopack"],
        as: "*.css",
      },
    },
  },
};

export default nextConfig;
