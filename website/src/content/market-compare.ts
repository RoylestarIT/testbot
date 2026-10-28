export type CompareRow = { label: string; us: string; market: string };

export const MARKET_COMPARE_ROWS: CompareRow[] = [
  { label: "Где работаете", us: "В Telegram", market: "Отдельный сайт или кабинет" },
  { label: "Площадки", us: "Wildberries и Ozon", market: "Часто только WB" },
  { label: "Черновики", us: "Три варианта на выбор", market: "Один шаблон или сразу в автомат" },
  { label: "Оплата", us: "Фикс в месяц", market: "Платите за каждый ответ" },
  { label: "Плохие отзывы", us: "Только вы решаете", market: "Иногда уходят сами" },
  { label: "Отправка ответа", us: "Из бота на PRO", market: "Копируете вручную" },
];
