import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",              // <- New: self-contained production build
  async rewrites() {
    return [{
      source: "/api/:path*",
      destination: `${process.env.GATEWAY_URL ?? "http://localhost:3000"}/:path*`,
    }];
  },
};

export default nextConfig;