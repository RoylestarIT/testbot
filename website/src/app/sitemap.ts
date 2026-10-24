import type { MetadataRoute } from "next";
import { SITE_URL } from "@/content/constants";

export const dynamic = "force-static";

const paths = [
  "",
  "/pricing",
  "/how-it-works",
  "/for-who",
  "/why-us",
  "/faq",
  "/contacts",
  "/privacy",
  "/terms",
  "/changelog",
];

export default function sitemap(): MetadataRoute.Sitemap {
  const base = SITE_URL.replace(/\/$/, "");
  return paths.map((path) => ({
    url: `${base}${path}/`,
    lastModified: new Date(),
    changeFrequency: path === "" ? "weekly" : "monthly",
    priority: path === "" ? 1 : 0.7,
  }));
}
