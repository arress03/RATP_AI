import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    // En production, vercel.json prend en charge le proxy /api/* -> Railway.
    // Ce rewrite ne s'active qu'en dev local pour pointer vers uvicorn.
    if (process.env.NODE_ENV === "production") return [];
    return [
      {
        source: "/api/:path*",
        destination: "http://localhost:8000/:path*",
      },
    ];
  },
};

export default nextConfig;
