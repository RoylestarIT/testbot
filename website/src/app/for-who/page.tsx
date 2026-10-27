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
    "Для продавцов на Wildberries и Ozon, у которых от 30 до 1000+ отзывов в месяц и нет времени отвечать на каждый вручную.",
};

const personas = [
  {
    tag: "30–200 отзывов",
    title: "Ведёте магазин сами",
    text: "Вы и закупщик, и менеджер, и поддержка. Бот собирает отзывы и сразу предлагает ответы — хватает пары минут в день.",
  },
  {
    tag: "200–1000+ отзывов",
    title: "Есть менеджер или помощник",
    text: "Менеджер отвечает с телефона, а вы один раз задаёте, как общаться с покупателями. Пятёрки бот закрывает сам.",
  },
  {
    tag: "WB + Ozon",
    title: "Продаёте и на WB, и на Ozon",
    text: "Отзывы с обеих площадок в одном чате и одинаковый стиль ответов. Больше не нужно прыгать между кабинетами.",
  },
];

const fit = [
  "У вас от 30 до 1000+ отзывов в месяц на WB или Ozon",
  "Нет человека, который сидел бы в отзывах весь день",
  "Вам удобнее в Telegram, чем в кабинете маркетплейса",
  "Хотите сами отвечать на плохие отзывы",
  "У вас несколько магазинов",
];

const notFit = [
  "Вы продаёте только на Яндекс Маркете — его пока нет",
  "Хотите, чтобы бот сам отвечал вообще на всё, включая негатив",
  "Нужна большая аналитика продаж, а не ответы на отзывы",
  "Нужен именно сайт-кабинет — мы работаем только в Telegram",
];

export default function ForWhoPage() {
  return (
    <PageShell>
      <InnerPageHero
        eyebrow="Для кого"
        title="Для селлеров, которым важен каждый отзыв"
        description="Продавцы на Wildberries и Ozon из России и Беларуси, которые хотят отвечать быстро, но по-человечески."
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
              description="Лучше выяснить это сейчас, чем после оплаты."
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
        description="Попробуйте на своих отзывах — бесплатно и без карты."
        cta="Начать бесплатно"
        showCalculatorLink
      />
    </PageShell>
  );
}
