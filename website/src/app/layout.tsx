import type { Metadata } from "next";
import { Geologica, Golos_Text } from "next/font/google";
import "./globals.css";
import { BRAND, SEO, SITE_URL } from "@/content/constants";
import { Analytics } from "@/components/Analytics";
import { JsonLd, organizationSchema } from "@/components/JsonLd";

const OG_IMAGE = `${SITE_URL}/og.png`;

const display = Geologica({
  subsets: ["latin", "cyrillic"],
  variable: "--font-display",
  display: "swap",
  weight: ["500", "600", "700"],
});

const body = Golos_Text({
  subsets: ["latin", "cyrillic"],
  variable: "--font-body",
  display: "swap",
  weight: ["400", "500", "600"],
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
    images: [{ url: OG_IMAGE, width: 1200, height: 630, alt: BRAND }],
  },
  twitter: {
    card: "summary_large_image",
    title: SEO.title,
    description: SEO.description,
    images: [OG_IMAGE],
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
    <html
      lang="ru"
      className={`${display.variable} ${body.variable}`}
      suppressHydrationWarning
    >
      <head>
        <script
          dangerouslySetInnerHTML={{
            __html: "document.documentElement.classList.add('js')",
          }}
        />
      </head>
      <body className="font-sans antialiased">
        <JsonLd data={organizationSchema()} />
        <Analytics />
        {children}
      </body>
    </html>
  );
}
