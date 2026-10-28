import type { Metadata } from "next";
import { PageShell } from "@/components/PageShell";
import { InnerPageHero } from "@/components/InnerPageHero";
import { Reveal } from "@/components/Reveal";

export const metadata: Metadata = {
  title: "Что нового",
  description: "Что изменилось в «Голос бренда» за последнее время.",
};

const entries = [
  {
    date: "Октябрь 2025",
    title: "Сайт и юридические документы",
    body: "Появился этот сайт, а политика конфиденциальности и соглашение теперь открываются по понятным ссылкам.",
  },
  {
    date: "Сентябрь 2025",
    title: "Подписка и оплата",
    body: "Оплата картой РФ и РБ через ЮKassa и bePaid прямо в боте. Появился калькулятор — подскажет, какой тариф выгоднее.",
  },
  {
    date: "Август 2025",
    title: "PRO: отправка из бота и автоответы на 4–5★",
    body: "Ответ можно отправить на маркетплейс прямо из Telegram. На плохие отзывы — по-прежнему только вы.",
  },
];

export default function ChangelogPage() {
  return (
    <PageShell>
      <InnerPageHero
        eyebrow="Обновления"
        title="Что нового"
        description="Самое важное из последних обновлений. Подробности — в боте, в разделе «Что нового»."
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
