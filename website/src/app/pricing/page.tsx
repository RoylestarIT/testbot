import type { Metadata } from "next";
import { PageShell } from "@/components/PageShell";
import { InnerPageHero } from "@/components/InnerPageHero";
import { PricingTable } from "@/components/PricingTable";
import { PRICES } from "@/content/constants";

export const metadata: Metadata = {
  title: "Тарифы Free, Lite и PRO",
  description:
    "Сравнение тарифов «Голос бренда»: генерации, кабинеты, publish в API, авто 4–5★. Lite 800 ₽, PRO 1600 ₽ в месяц.",
};

export default function PricingPage() {
  return (
    <PageShell>
      <InnerPageHero
        title="Тарифы"
        description={`Lite — ${PRICES.lite.rub} ₽ / ${PRICES.lite.byn} BYN · PRO — ${PRICES.pro.rub} ₽ / ${PRICES.pro.byn} BYN в месяц. Оплата в боте.`}
      />
      <div className="container-page section-y !pt-10">
        <PricingTable />
        <div className="mt-12 grid gap-6 md:grid-cols-3">
          <CompareCard
            title="Мы"
            items={[
              "Co-pilot в Telegram",
              "WB + Ozon",
              "Фикс в месяц",
              "Негатив только вручную",
            ]}
            positive
          />
          <CompareCard
            title="Типичный pay-per-answer"
            items={[
              "Оплата за каждый ответ (~1–3 ₽)",
              "Сложнее прогнозировать бюджет",
              "Часто отдельный сайт",
            ]}
          />
          <CompareCard
            title="Штат «на отзывы»"
            items={[
              "Часто 30–80 тыс. ₽/мес на рынке",
              "Зависимость от людей и графика",
              "Бот не заменяет стратегию, но снимает рутину",
            ]}
          />
        </div>
      </div>
    </PageShell>
  );
}

function CompareCard({
  title,
  items,
  positive,
}: {
  title: string;
  items: string[];
  positive?: boolean;
}) {
  return (
    <div
      className={`card p-6 sm:p-7 ${
        positive ? "ring-2 ring-brand-500/20 bg-brand-50/20" : ""
      }`}
    >
      <h3 className="font-display text-title text-ink">{title}</h3>
      <ul className="mt-4 space-y-2.5 text-body text-ink-muted">
        {items.map((item) => (
          <li key={item} className="flex gap-2">
            <span className="text-brand-500" aria-hidden>
              ·
            </span>
            {item}
          </li>
        ))}
      </ul>
    </div>
  );
}
