/** Публичные константы лендинга «Голос бренда». */

export const BRAND = "Голос бренда";
export const BRAND_TECH = "ReviewPilot";
export const BOT_USERNAME = "FeedBackReview_bot";
export const BOT_URL =
  process.env.NEXT_PUBLIC_BOT_URL ?? "https://t.me/FeedBackReview_bot";
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

const BASE_PATH = process.env.NEXT_PUBLIC_BASE_PATH ?? "";

/** Путь к файлу из public/ с учётом basePath (next/link его добавляет сам, <img> — нет). */
export function asset(path: string): string {
  return `${BASE_PATH}${path}`;
}

export const BOT_AVATAR = asset("/bot-avatar.png");

export const SUPPORT_TG = "brend_voice_support";
export const SUPPORT_TG_URL = `https://t.me/${SUPPORT_TG}`;

const supportEmailFromEnv = process.env.NEXT_PUBLIC_SUPPORT_EMAIL?.trim() ?? "";

/** Пусто или placeholder — на сайте показываем Telegram вместо почты. */
export const SUPPORT_EMAIL = supportEmailFromEnv.includes("example.com")
  ? ""
  : supportEmailFromEnv;

export const HAS_SUPPORT_EMAIL = SUPPORT_EMAIL.length > 0;

export const LEGAL_NAME = "Быстров Егор Максимович";
export const LEGAL_STATUS = "Самозанятый";
export const LEGAL_UNP = "EE5854155";

export const LEGAL_OPERATOR =
  process.env.NEXT_PUBLIC_LEGAL_OPERATOR_NAME?.trim() ||
  `${LEGAL_STATUS} ${LEGAL_NAME}, УНП ${LEGAL_UNP}`;

/** Пробный PRO — текст для hero и тарифов (срок как в FAQ бота). */
export const PRO_TRIAL_DAYS = 3;
export const PRO_TRIAL_HINT = `${PRO_TRIAL_DAYS} дня PRO бесплатно — один раз, в боте: «Подписка» → «Попробовать PRO»`;

/** Способы оплаты подписки в боте (единый источник для лендинга). */
export const PAYMENT_METHODS = [
  {
    title: "Карты РФ и РБ",
    text: "Visa, Mastercard, «Мир» и карты белорусских банков",
  },
  {
    title: "ЮKassa",
    text: "Эквайринг для оплат из России — прямо в боте",
  },
  {
    title: "bePaid",
    text: "Эквайринг для оплат из Беларуси — прямо в боте",
  },
] as const;

export const PAYMENT_METHODS_LINE =
  "карты РФ и РБ через ЮKassa (РФ) и bePaid (РБ)";

/** Дата актуализации цен на лендинге (обновляйте при изменении тарифов в боте). */
export const PRICING_UPDATED = "27.10.2026";

export const PRICES = {
  lite: { rub: 990, byn: 35 },
  pro: { rub: 1990, byn: 70 },
} as const;

export const SEO = {
  title: "Голос бренда — ответы на отзывы WB и Ozon в Telegram",
  description:
    "Telegram-бот для селлеров Wildberries и Ozon: три варианта ответа, один чат на две площадки, отправка из бота на PRO. Плохие отзывы — только с вашего решения. Бесплатный старт без карты.",
  keywords: [
    "бот для отзывов wildberries",
    "ответы на отзывы ozon telegram",
    "отзывы wb ozon один бот",
    "автоответы на отзывы 4 5 звезд",
    "telegram бот селлер wildberries ozon",
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
