import type { NextConfig } from "next";

if (!process.env.NEXT_PUBLIC_SITE_URL?.trim() && !process.env.VERCEL_URL?.trim()) {
  console.warn(
    "\n⚠ NEXT_PUBLIC_SITE_URL is not set: canonical, sitemap and OG links will point to a placeholder domain.\n",
  );
}

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
