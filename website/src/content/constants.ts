/** Публичные константы лендинга «Голос бренда». */

export const BRAND = "Голос бренда";
export const BRAND_TECH = "ReviewPilot";
export const BOT_USERNAME = "FeedBackReview_bot";
export const BOT_URL =
  process.env.NEXT_PUBLIC_BOT_URL ?? `https://t.me/${BOT_USERNAME}`;
export const BOT_URL_SITE = `${BOT_URL}${BOT_URL.includes("?") ? "&" : "?"}start=site`;

/** Канонический URL: env → VERCEL_URL при сборке на Vercel → placeholder. */
export function resolveSiteUrl(): string {
  const fromEnv = process.env.NEXT_PUBLIC_SITE_URL?.trim();
  if (fromEnv) return fromEnv.replace(/\/$/, "");
  const vercel = process.env.VERCEL_URL?.trim();
  if (vercel) return `https://${vercel.replace(/\/$/, "")}`;
  return "https://golos-brenda.example";
}

export const SITE_URL = resolveSiteUrl();

/** Absolute canonical: a relative path would drop the GitHub Pages basePath from metadataBase. */
export function canonical(path = "/") {
  return { canonical: path === "/" ? SITE_URL : `${SITE_URL}${path}` };
}

export const SUPPORT_EMAIL =
  process.env.NEXT_PUBLIC_SUPPORT_EMAIL ?? "support@example.com";

export const LEGAL_OPERATOR =
  process.env.NEXT_PUBLIC_LEGAL_OPERATOR_NAME ??
  "[ИП/ООО — полное наименование и реквизиты уточняются у оператора сервиса]";

/** Дата актуализации цен на лендинге (обновляйте при изменении тарифов в боте). */
export const PRICING_UPDATED = "27.10.2026";

/** Дата последнего обновления контента (для sitemap lastModified). */
export const CONTENT_UPDATED = "2026-10-24";

export const PRICES = {
  lite: { rub: 990, byn: 35 },
  pro: { rub: 1990, byn: 70 },
} as const;

export const SEO = {
  title:
    "Голос бренда — ответы на отзывы WB и Ozon в Telegram | ИИ-черновики и publish",
  description:
    "Telegram-бот для селлеров Wildberries и Ozon: синхронизация отзывов, 3 варианта ответа ИИ, тон бренда, publish в API (PRO) и авто только на 4–5★. Негатив — только с вашего подтверждения.",
  keywords: [
    "бот для отзывов wildberries",
    "ответы на отзывы ozon telegram",
    "автоответы на отзывы 5 звезд",
    "отзывы wb ozon telegram",
    "publish ответов wildberries api",
  ],
} as const;

export const NAV = [
  { href: "/how-it-works", label: "Как работает" },
  { href: "/for-who", label: "Для кого" },
  { href: "/why-us", label: "Почему мы" },
  { href: "/pricing", label: "Тарифы" },
  { href: "/faq", label: "FAQ" },
  { href: "/contacts", label: "Контакты" },
] as const;
