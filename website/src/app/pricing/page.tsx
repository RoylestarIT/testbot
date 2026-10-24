import type { Metadata } from "next";
import { PageShell } from "@/components/PageShell";
import { SectionHeading } from "@/components/SectionHeading";
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
      <div className="mx-auto max-w-6xl px-4 py-14 sm:px-6">
        <SectionHeading
          title="Тарифы"
          description={`Lite — ${PRICES.lite.rub} ₽ / ${PRICES.lite.byn} BYN · PRO — ${PRICES.pro.rub} ₽ / ${PRICES.pro.byn} BYN в месяц. Оплата в боте.`}
        />
        <div className="mt-10">
          <PricingTable />
        </div>
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
      className={`rounded-2xl border p-6 ${
        positive ? "border-blue-200 bg-blue-50/50" : "border-slate-200 bg-white"
      }`}
    >
      <h3 className="font-semibold text-slate-900">{title}</h3>
      <ul className="mt-4 space-y-2 text-sm text-slate-600">
        {items.map((item) => (
          <li key={item}>· {item}</li>
        ))}
      </ul>
    </div>
  );
}
