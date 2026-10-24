import type { Metadata } from "next";
import { Inter, Onest } from "next/font/google";
import "./globals.css";
import { BRAND, SEO, SITE_URL } from "@/content/constants";

const inter = Inter({
  subsets: ["latin", "cyrillic"],
  variable: "--font-inter",
  display: "swap",
  weight: ["400", "500", "600"],
});

const onest = Onest({
  subsets: ["latin", "cyrillic"],
  variable: "--font-onest",
  display: "swap",
  weight: ["500", "600", "700", "800"],
});

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: {
    default: SEO.title,
    template: `%s · ${BRAND}`,
  },
  description: SEO.description,
  keywords: [...SEO.keywords],
  openGraph: {
    type: "website",
    locale: "ru_RU",
    siteName: BRAND,
    title: SEO.title,
    description: SEO.description,
    url: SITE_URL,
  },
  twitter: {
    card: "summary_large_image",
    title: SEO.title,
    description: SEO.description,
  },
  alternates: {
    canonical: SITE_URL,
  },
  robots: {
    index: true,
    follow: true,
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ru" className={`${inter.variable} ${onest.variable}`}>
      <body className="font-sans antialiased">{children}</body>
    </html>
  );
}
