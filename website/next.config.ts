import type { NextConfig } from "next";

const ghPages = process.env.GITHUB_PAGES === "1";
const basePath = ghPages ? "/testbot" : "";

const nextConfig: NextConfig = {
  output: "export",
  basePath,
  assetPrefix: basePath ? `${basePath}/` : undefined,
  images: {
    unoptimized: true,
  },
};

export default nextConfig;
