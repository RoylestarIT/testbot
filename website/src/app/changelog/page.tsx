import type { Metadata } from "next";
import { PageShell } from "@/components/PageShell";
import { SectionHeading } from "@/components/SectionHeading";

export const metadata: Metadata = {
  title: "Что нового",
  description: "Обновления «Голос бренда» — синхронизируйте с разделом в боте вручную.",
};

const entries = [
  {
    date: "2025-10",
    title: "Юридические документы и сайт",
    body: "Политика конфиденциальности и соглашение на отдельных URL для бота и лендинга.",
  },
  {
    date: "2025-09",
    title: "Подписка и оплата",
    body: "Telegram Stars, Crypto Bot, карта РФ/РБ, калькулятор тарифа в боте.",
  },
  {
    date: "2025-08",
    title: "PRO: publish и авто 4–5★",
    body: "Публикация в Seller API из Telegram; негатив только вручную.",
  },
];

export default function ChangelogPage() {
  return (
    <PageShell>
      <div className="mx-auto max-w-2xl px-4 py-14 sm:px-6">
        <SectionHeading
          title="Что нового"
          description="Краткий changelog лендинга. Полный список — в боте («Что нового»)."
        />
        <ul className="mt-10 space-y-8">
          {entries.map((e) => (
            <li key={e.title} className="border-l-2 border-brand-500 pl-4">
              <time className="text-caption font-medium text-ink-subtle">{e.date}</time>
              <h2 className="mt-1 font-display text-title text-ink">{e.title}</h2>
              <p className="mt-2 text-body text-ink-muted">{e.body}</p>
            </li>
          ))}
        </ul>
      </div>
    </PageShell>
  );
}
