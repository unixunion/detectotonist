import type { NextConfig } from "next";

const nextConfig = {
  reactStrictMode: true,
  experimental: {
    appDir: true,
  },
  async rewrites() {
    return [
      {
        source: "/api/:path*",  // Any request to /api/ will be proxied
        destination: "http://localhost:8080/:path*",  // Redirect to Flask API
      },
    ];
  },
};

export default nextConfig;