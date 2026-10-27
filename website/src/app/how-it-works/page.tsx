import type { Metadata } from "next";
import { PageShell } from "@/components/PageShell";
import { InnerPageHero } from "@/components/InnerPageHero";
import { TelegramMockup } from "@/components/TelegramMockup";
import { Reveal } from "@/components/Reveal";
import { SectionHeading } from "@/components/SectionHeading";
import { CtaBanner } from "@/components/CtaBanner";
import { IconArrowRight } from "@/components/icons";

export const metadata: Metadata = {
  title: "Как работает бот для отзывов WB и Ozon",
  description:
    "Подключаете кабинет, бот присылает отзывы и предлагает три варианта ответа. Вы выбираете — ответ уходит покупателю. Всё в Telegram.",
};

const steps = [
  {
    title: "Подключите кабинет",
    body: "Вставьте в бота ключ от кабинета WB или Ozon — бот подскажет, где его взять. Ключ хранится зашифрованным, на сайте его вводить не нужно.",
    hint: "Пара минут",
  },
  {
    title: "Получайте отзывы",
    body: "Каждый новый отзыв приходит сообщением. Не до этого сейчас — отложите. Не хотите уведомлений весь день — включите сводку раз в сутки.",
    hint: "Сами приходят",
  },
  {
    title: "Выберите ответ",
    body: "Бот сразу предлагает три варианта: с учётом товара, вашего стиля и слов, которые вы не любите. Берёте любой или правите под себя.",
    hint: "3 варианта",
  },
  {
    title: "Отправьте",
    body: "На PRO ответ уходит на маркетплейс одной кнопкой, а на пятёрки и четвёрки бот может отвечать сам. На Free и Lite — копируете готовый текст в кабинет.",
    hint: "Одна кнопка на PRO",
  },
];

const flow = ["Отзыв на WB или Ozon", "Бот", "Три варианта", "Вы выбираете", "Покупатель"];

const rules = [
  {
    title: "Плохие отзывы — только через вас",
    text: "На 1–3★ бот сам не ответит никогда. На любом тарифе.",
  },
  {
    title: "Автоматом — только хорошие",
    text: "На PRO можно включить автоответы на 4–5★. Выключаются одной кнопкой.",
  },
  {
    title: "Ключ — только в боте",
    text: "Сайт ничего не спрашивает. Подключение и оплата — внутри Telegram.",
  },
];

export default function HowItWorksPage() {
  return (
    <PageShell>
      <InnerPageHero
        eyebrow="Как это работает"
        title="От отзыва до ответа — в одном чате"
        description="Ничего не нужно устанавливать и изучать. Подключили кабинет — и бот начинает присылать отзывы с готовыми вариантами ответа."
      />

      <section className="pb-20 sm:pb-24 lg:pb-32">
        <div className="container-page grid gap-16 lg:grid-cols-[0.9fr_1.1fr] lg:gap-24">
          <div className="lg:sticky lg:top-28 lg:self-start">
            <Reveal>
              <TelegramMockup />
            </Reveal>
          </div>

          <ol className="relative">
            <span
              className="absolute bottom-6 left-5 top-6 w-px bg-gradient-to-b from-brand-300 via-brand-200 to-transparent"
              aria-hidden
            />
            {steps.map((step, i) => (
              <li key={step.title} className="relative pb-14 pl-16 last:pb-0">
                <Reveal delay={i * 80}>
                  <span className="absolute left-0 top-0 flex h-10 w-10 items-center justify-center rounded-full bg-surface font-display text-small font-semibold text-brand-700 shadow-xs ring-1 ring-brand-200">
                    {i + 1}
                  </span>
                  <p className="text-caption font-medium uppercase tracking-[0.12em] text-ink-subtle">
                    {step.hint}
                  </p>
                  <h2 className="mt-2 text-headline">{step.title}</h2>
                  <p className="mt-4 max-w-prose text-body-lg text-ink-muted">{step.body}</p>
                </Reveal>
              </li>
            ))}
          </ol>
        </div>
      </section>

      <section className="section-y border-y border-line bg-surface">
        <div className="container-page">
          <Reveal>
            <SectionHeading
              eyebrow="Главное правило"
              title="Человек всегда в цепочке"
              description="Бот экономит время, но решаете всегда вы."
            />
          </Reveal>
          <Reveal delay={100}>
            <ol className="mt-14 flex flex-wrap items-center justify-center gap-3">
              {flow.map((item, i) => (
                <li key={item} className="flex items-center gap-3">
                  <span
                    className={`rounded-full px-5 py-2.5 text-small font-medium ring-1 transition duration-300 ease-smooth hover:-translate-y-0.5 ${
                      item === "Вы выбираете"
                        ? "bg-brand-700 text-white ring-brand-700"
                        : "bg-surface-muted text-ink ring-line"
                    }`}
                  >
                    {item}
                  </span>
                  {i < flow.length - 1 && <IconArrowRight className="h-4 w-4 text-ink-faint" />}
                </li>
              ))}
            </ol>
          </Reveal>

          <div className="mt-20 grid gap-5 md:grid-cols-3">
            {rules.map((r, i) => (
              <Reveal key={r.title} delay={i * 80}>
                <div className="card-hover h-full p-8">
                  <h3 className="text-title">{r.title}</h3>
                  <p className="mt-3 text-body text-ink-muted">{r.text}</p>
                </div>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      <CtaBanner title="Попробуйте на своих отзывах" showCalculatorLink />
    </PageShell>
  );
}
