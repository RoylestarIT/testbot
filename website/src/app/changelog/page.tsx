import type { Metadata } from "next";
import { PageShell } from "@/components/PageShell";
import { InnerPageHero } from "@/components/InnerPageHero";
import { Reveal } from "@/components/Reveal";

export const metadata: Metadata = {
  title: "Что нового",
  description: "Обновления «Голос бренда» — синхронизируйте с разделом в боте вручную.",
};

const entries = [
  {
    date: "Октябрь 2025",
    title: "Сайт и юридические документы",
    body: "Политика конфиденциальности и пользовательское соглашение теперь доступны по отдельным ссылкам — для бота и сайта.",
  },
  {
    date: "Сентябрь 2025",
    title: "Подписка и оплата",
    body: "Telegram Stars, Crypto Bot, карты РФ и РБ, а также калькулятор тарифа прямо в боте.",
  },
  {
    date: "Август 2025",
    title: "PRO: публикация и автоответы на 4–5★",
    body: "Ответы публикуются в маркетплейс прямо из Telegram. Негатив по-прежнему только вручную.",
  },
];

export default function ChangelogPage() {
  return (
    <PageShell>
      <InnerPageHero
        eyebrow="Обновления"
        title="Что нового"
        description="Главные изменения продукта. Полный список — в боте, раздел «Что нового»."
      />
      <section className="pb-20 sm:pb-24 lg:pb-32">
        <ol className="container-page relative max-w-3xl">
          {entries.map((e, i) => (
            <li
              key={e.title}
              className="grid gap-2 border-t border-line py-10 first:border-t-0 sm:grid-cols-[10rem_1fr] sm:gap-10"
            >
              <Reveal delay={i * 60}>
                <time className="text-small font-medium text-brand-700">{e.date}</time>
              </Reveal>
              <Reveal delay={i * 60 + 60}>
                <h2 className="text-title">{e.title}</h2>
                <p className="mt-3 text-body text-ink-muted">{e.body}</p>
              </Reveal>
            </li>
          ))}
        </ol>
      </section>
    </PageShell>
  );
}
