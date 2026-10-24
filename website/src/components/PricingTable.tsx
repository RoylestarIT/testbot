import { PRICES } from "@/content/constants";
import { TelegramButton } from "./TelegramButton";

type Row = {
  label: string;
  free: string;
  lite: string;
  pro: string;
};

const rows: Row[] = [
  {
    label: "Генерации",
    free: "5 / день",
    lite: "∞",
    pro: "∞",
  },
  {
    label: "Кабинеты WB/Ozon",
    free: "1",
    lite: "несколько",
    pro: "несколько",
  },
  {
    label: "Tone of voice",
    free: "1",
    lite: "несколько",
    pro: "несколько",
  },
  {
    label: "Publish в API",
    free: "пробный лимит",
    lite: "копия в кабинет",
    pro: "✓ из бота",
  },
  {
    label: "Авто-ответы",
    free: "—",
    lite: "—",
    pro: "только 4–5★",
  },
  {
    label: "Негатив 1–3★",
    free: "только вручную",
    lite: "только вручную",
    pro: "только вручную",
  },
];

export function PricingTable({ compact = false }: { compact?: boolean }) {
  return (
    <div className="overflow-x-auto rounded-3xl border border-line bg-surface shadow-card">
      <table className="w-full min-w-[640px] border-collapse text-left text-small">
        <caption className="sr-only">Сравнение тарифов Free, Lite и PRO</caption>
        <thead>
          <tr className="border-b border-line bg-surface-muted">
            <th scope="col" className="px-6 py-4 font-medium text-ink-muted">
              Возможность
            </th>
            <th scope="col" className="px-6 py-4 font-display font-semibold text-ink">
              Free
            </th>
            <th scope="col" className="px-6 py-4 font-display font-semibold text-ink">
              Lite
            </th>
            <th
              scope="col"
              className="bg-brand-50/90 px-6 py-4 font-display font-semibold text-brand-800"
            >
              PRO
            </th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr
              key={row.label}
              className="border-b border-line transition-colors hover:bg-surface-muted/50 last:border-0"
            >
              <th scope="row" className="px-6 py-3.5 font-medium text-ink">
                {row.label}
              </th>
              <td className="px-6 py-3.5 text-ink-muted">{row.free}</td>
              <td className="px-6 py-3.5 text-ink-muted">{row.lite}</td>
              <td className="bg-brand-50/35 px-6 py-3.5 font-medium text-ink">
                {row.pro}
              </td>
            </tr>
          ))}
          <tr className="bg-surface-muted">
            <th scope="row" className="px-6 py-4 font-display font-semibold text-ink">
              Цена / месяц
            </th>
            <td className="px-6 py-4 text-ink-muted">0 ₽</td>
            <td className="px-6 py-4 font-semibold text-ink">
              {PRICES.lite.rub} ₽ / {PRICES.lite.byn} BYN
            </td>
            <td className="bg-brand-100/45 px-6 py-4 font-display font-semibold text-brand-900">
              {PRICES.pro.rub} ₽ / {PRICES.pro.byn} BYN
            </td>
          </tr>
        </tbody>
      </table>
      {!compact && (
        <div className="flex flex-col items-start justify-between gap-4 border-t border-line px-4 py-5 sm:flex-row sm:items-center">
          <p className="max-w-xl text-body text-ink-muted">
            Оплата в боте: Telegram Stars, Crypto Bot (USDT и др.), карта РФ/РБ,
            СБП/перевод (ручная активация до 24 ч). Trial PRO — в боте, один раз на
            аккаунт.
          </p>
          <div className="flex flex-wrap gap-2">
            <TelegramButton variant="primary">Оплатить в боте</TelegramButton>
            <TelegramButton variant="ghost">Сравнение в боте</TelegramButton>
          </div>
        </div>
      )}
    </div>
  );
}
