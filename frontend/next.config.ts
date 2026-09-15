import type { NextConfig } from "next";

// Internal Docker service URL — baked in at build time via build arg.
// Used for Next.js rewrites (server-side proxy) and SSR fetches.
// In local dev this defaults to localhost.
const internalApiUrl =
  process.env.API_INTERNAL_URL ?? "http://localhost:8000";

const config: NextConfig = {
  output: "standalone",
  reactStrictMode: true,
  poweredByHeader: false,

  // All images are served unoptimized — thumbnails are small JPEG/PNG already.
  // This removes the need for remotePatterns entirely.
  images: {
    unoptimized: true,
  },

  // Proxy /api/* and /uploads/* to the FastAPI container internally.
  // The browser never needs to know the API's address — everything is same-origin.
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${internalApiUrl}/api/:path*`,
      },
      {
        source: "/uploads/:path*",
        destination: `${internalApiUrl}/uploads/:path*`,
      },
    ];
  },

  async headers() {
    return [
      {
        source: "/(.*)",
        headers: [
          { key: "X-Frame-Options", value: "DENY" },
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
          {
            key: "Permissions-Policy",
            value: "camera=(), microphone=(), geolocation=()",
          },
        ],
      },
    ];
  },
};

export default config;
