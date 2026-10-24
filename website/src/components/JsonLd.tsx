import { BOT_URL, BRAND, PRICES, SEO, SITE_URL } from "@/content/constants";
import type { FaqItem } from "@/content/faq";

export function JsonLd({ data }: { data: Record<string, unknown> }) {
  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(data).replace(/</g, "\\u003c") }}
    />
  );
}

export function organizationSchema() {
  return {
    "@context": "https://schema.org",
    "@type": "Organization",
    name: BRAND,
    url: SITE_URL,
    logo: `${SITE_URL}/bot-avatar.png`,
    sameAs: [BOT_URL],
  };
}

export function softwareSchema() {
  return {
    "@context": "https://schema.org",
    "@type": "SoftwareApplication",
    name: BRAND,
    applicationCategory: "BusinessApplication",
    operatingSystem: "Telegram",
    description: SEO.description,
    url: SITE_URL,
    offers: [
      { "@type": "Offer", name: "Free", price: "0", priceCurrency: "RUB" },
      { "@type": "Offer", name: "Lite", price: String(PRICES.lite.rub), priceCurrency: "RUB" },
      { "@type": "Offer", name: "PRO", price: String(PRICES.pro.rub), priceCurrency: "RUB" },
    ],
  };
}

export function faqSchema(items: FaqItem[]) {
  return {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    mainEntity: items.map((item) => ({
      "@type": "Question",
      name: item.question,
      acceptedAnswer: { "@type": "Answer", text: item.answer },
    })),
  };
}
