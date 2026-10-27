import { asset } from "./constants";

export type BotScreenshot = {
  id: string;
  src: string;
  alt: string;
  title: string;
  caption: string;
};

export const BOT_SCREENSHOTS: BotScreenshot[] = [
  {
    id: "dashboard",
    src: asset("/bot-screenshots/dashboard.png"),
    alt: "Сводка «Голос бренда» в Telegram: статус отзывов и быстрые действия",
    title: "Сводка",
    caption: "Статус кабинетов, отзывы и быстрые кнопки — без отдельного сайта.",
  },
  {
    id: "settings",
    src: asset("/bot-screenshots/settings.png"),
    alt: "Настройки бота: кабинеты WB/Ozon, тон ответа, уведомления",
    title: "Настройки",
    caption: "Кабинеты, tone of voice, шаблоны и авто-публикация на PRO.",
  },
  {
    id: "templates",
    src: asset("/bot-screenshots/templates.png"),
    alt: "Мои шаблоны фраз для быстрых ответов",
    title: "Шаблоны",
    caption: "До пяти фраз — кнопки прямо на экране вариантов ответа.",
  },
  {
    id: "support",
    src: asset("/bot-screenshots/support.png"),
    alt: "Раздел поддержки в боте",
    title: "Поддержка",
    caption: "Написать в поддержку, документы и возврат к сводке.",
  },
  {
    id: "description",
    src: asset("/bot-screenshots/description.png"),
    alt: "Описание бота в Telegram до нажатия «Старт»",
    title: "Профиль бота",
    caption: "Так бота видят новые пользователи до первого «Старт».",
  },
];
