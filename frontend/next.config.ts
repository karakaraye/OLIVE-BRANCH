import type { NextConfig } from "next";

const config: NextConfig = {
  agentRules: false,
  async rewrites() {
    const backend = process.env.OLIVE_BACKEND_ORIGIN ?? "http://127.0.0.1:8000";
    return [{ source: "/api/staff/:path*/", destination: `${backend}/api/staff/:path*/` }];
  },
  skipTrailingSlashRedirect: true,
};

export default config;
