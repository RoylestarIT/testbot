import type { Metadata } from "next";
import { PageShell } from "@/components/PageShell";
import { InnerPageHero } from "@/components/InnerPageHero";
import { Reveal } from "@/components/Reveal";
import { SectionHeading } from "@/components/SectionHeading";
import { CtaBanner } from "@/components/CtaBanner";
import { IconCheck } from "@/components/icons";

export const metadata: Metadata = {
  title: "Для кого сервис",
  description:
    "Селлеры Wildberries и Ozon с 30–1000+ отзывами в месяц, Telegram-first workflow и контроль негатива.",
};

const personas = [
  {
    tag: "30–200 отзывов",
    title: "Селлер-одиночка",
    text: "Сами ведёте магазин и отвечаете урывками. Бот собирает отзывы и даёт готовые черновики — хватает пары минут в день.",
  },
  {
    tag: "200–1000+ отзывов",
    title: "Небольшая команда",
    text: "Менеджер отвечает в Telegram, вы задаёте тон и правила. Автоответы на 4–5★ снимают основную нагрузку.",
  },
  {
    tag: "WB + Ozon",
    title: "Бренд на двух площадках",
    text: "Один тон бренда на обеих площадках, общая лента отзывов и история ответов в одном месте.",
  },
];

const fit = [
  "От 30 до 1000+ отзывов в месяц на WB и/или Ozon",
  "Некому сидеть в отзывах весь день",
  "Удобнее работать в Telegram, чем в кабинетах",
  "Важно, чтобы негатив проходил через человека",
  "Нужно несколько кабинетов и тонов бренда",
];

const notFit = [
  "Нужен только Яндекс Маркет — пока не поддерживаем",
  "Хочется 100% автомата на все звёзды без участия человека",
  "Нужна тяжёлая BI-аналитика, а не ответы на отзывы",
  "Нужен веб-кабинет вместо бота — мы осознанно в Telegram",
];

export default function ForWhoPage() {
  return (
    <PageShell>
      <InnerPageHero
        eyebrow="Для кого"
        title="Для селлеров, которым важен каждый отзыв"
        description="Продавцы на Wildberries и Ozon в России и Беларуси, которые хотят отвечать быстро и не терять контроль над тоном."
      />

      <section className="pb-20 sm:pb-24 lg:pb-32">
        <div className="container-page grid gap-5 md:grid-cols-3">
          {personas.map((p, i) => (
            <Reveal key={p.title} delay={i * 80}>
              <div className="card-hover h-full p-8">
                <span className="inline-flex rounded-full bg-brand-50 px-3 py-1 text-caption font-medium text-brand-700 ring-1 ring-brand-100">
                  {p.tag}
                </span>
                <h2 className="mt-6 text-title">{p.title}</h2>
                <p className="mt-3 text-body text-ink-muted">{p.text}</p>
              </div>
            </Reveal>
          ))}
        </div>
      </section>

      <section className="section-y border-y border-line bg-surface">
        <div className="container-page">
          <Reveal>
            <SectionHeading
              eyebrow="Честно"
              title="Подойдём ли мы вам"
              description="Лучше понять это сразу — до подключения кабинета."
            />
          </Reveal>
          <div className="mt-16 grid gap-5 lg:grid-cols-2">
            <Reveal>
              <div className="h-full rounded-3xl bg-brand-900 p-8 text-white sm:p-10">
                <h3 className="text-headline text-white">Подойдём, если</h3>
                <ul className="mt-8 space-y-4">
                  {fit.map((item) => (
                    <li key={item} className="flex gap-3 text-body text-brand-50">
                      <span
                        className="mt-1 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-white/10"
                        aria-hidden
                      >
                        <IconCheck className="h-3 w-3" />
                      </span>
                      {item}
                    </li>
                  ))}
                </ul>
              </div>
            </Reveal>
            <Reveal delay={100}>
              <div className="h-full rounded-3xl border border-line bg-surface-muted p-8 sm:p-10">
                <h3 className="text-headline">Скорее не подойдём, если</h3>
                <ul className="mt-8 space-y-4">
                  {notFit.map((item) => (
                    <li key={item} className="flex gap-3 text-body text-ink-muted">
                      <span
                        className="mt-1 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-white text-ink-subtle ring-1 ring-line"
                        aria-hidden
                      >
                        <span className="h-px w-2.5 bg-current" />
                      </span>
                      {item}
                    </li>
                  ))}
                </ul>
              </div>
            </Reveal>
          </div>
        </div>
      </section>

      <CtaBanner
        title="Узнали себя?"
        description="Проверьте на своих отзывах — Free без карты."
        cta="Начать бесплатно"
        showCalculatorLink
      />
    </PageShell>
  );
}
