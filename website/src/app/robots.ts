import type { MetadataRoute } from "next";
import { SITE_URL } from "@/content/constants";

export const dynamic = "force-static";

export default function robots(): MetadataRoute.Robots {
  const base = SITE_URL.replace(/\/$/, "");
  return {
    rules: {
      userAgent: "*",
      allow: "/",
    },
    sitemap: `${base}/sitemap.xml`,
  };
}
