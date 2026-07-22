import type { NextConfig } from "next";

// Server-side only — proxied via rewrites(), never exposed to the browser.
// Points at the FastAPI backend (local docker-compose, or the deployed URL).
const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:8000";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${BACKEND_URL}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
