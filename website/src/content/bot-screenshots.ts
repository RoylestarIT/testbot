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
    id: "description",
    src: asset("/bot-screenshots/description.png"),
    alt: "Карточка бота в Telegram до нажатия «Старт»",
    title: "Первое знакомство",
    caption: "Так бот выглядит, когда вы открываете его впервые.",
  },
  {
    id: "dashboard",
    src: asset("/bot-screenshots/dashboard.png"),
    alt: "Главный экран бота: сводка по отзывам и кнопки действий",
    title: "Главный экран",
    caption: "Сразу видно, есть ли новые отзывы и сколько ответов ушло за неделю.",
  },
  {
    id: "settings",
    src: asset("/bot-screenshots/settings.png"),
    alt: "Настройки бота: кабинеты WB и Ozon, стиль ответов, уведомления",
    title: "Настройки",
    caption: "Подключаете кабинеты, задаёте стиль общения и включаете уведомления.",
  },
  {
    id: "templates",
    src: asset("/bot-screenshots/templates.png"),
    alt: "Мои шаблоны — готовые фразы для быстрых ответов",
    title: "Свои фразы",
    caption: "Сохраните до пяти любимых фраз — они появятся кнопками рядом с ответом.",
  },
  {
    id: "support",
    src: asset("/bot-screenshots/support.png"),
    alt: "Раздел поддержки в боте",
    title: "Поддержка",
    caption: "Пишете — отвечает живой человек. Документы тоже здесь.",
  },
];
