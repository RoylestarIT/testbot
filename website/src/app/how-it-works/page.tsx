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
    "Подключение кабинета, синхронизация, три варианта ответа ИИ, publish в API или копия в личный кабинет — пошагово в Telegram.",
};

const steps = [
  {
    title: "Подключите кабинет",
    body: "Добавьте API-ключ WB или Ozon прямо в боте. Ключи хранятся в зашифрованном виде — на сайте их вводить не нужно.",
    hint: "≈ 2 минуты",
  },
  {
    title: "Получайте отзывы",
    body: "Каждый новый отзыв приходит сообщением. Можно отложить на потом или получать дайджест раз в день.",
    hint: "Автоматически",
  },
  {
    title: "Выберите ответ",
    body: "ИИ предлагает три варианта с учётом тона бренда, стоп-слов и товара. Берёте любой или правите под себя.",
    hint: "3 варианта",
  },
  {
    title: "Опубликуйте",
    body: "На PRO ответ уходит в маркетплейс прямо из бота, а 4–5★ можно отвечать автоматически. На Free и Lite — копируете готовый текст в кабинет.",
    hint: "В один клик на PRO",
  },
];

const flow = ["Маркетплейс", "Бот", "Три черновика", "Ваше решение", "Покупатель"];

const rules = [
  {
    title: "Негатив — только вручную",
    text: "Ответы на 1–3★ никогда не уходят без вашего подтверждения, на любом тарифе.",
  },
  {
    title: "Автоответы — только на 4–5★",
    text: "Включаются на PRO по вашим правилам и шаблонам. Выключить можно в любой момент.",
  },
  {
    title: "Ключи — только в боте",
    text: "Сайт ничего не запрашивает. Подключение кабинета и оплата — внутри Telegram.",
  },
];

export default function HowItWorksPage() {
  return (
    <PageShell>
      <InnerPageHero
        eyebrow="Как это работает"
        title="От отзыва до ответа — в одном чате"
        description="Никаких внедрений и обучения. Подключаете кабинет — и бот начинает присылать отзывы с готовыми черновиками."
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
              eyebrow="Поток"
              title="Человек всегда в цепочке"
              description="ИИ ускоряет работу, но последнее слово — за вами."
            />
          </Reveal>
          <Reveal delay={100}>
            <ol className="mt-14 flex flex-wrap items-center justify-center gap-3">
              {flow.map((item, i) => (
                <li key={item} className="flex items-center gap-3">
                  <span
                    className={`rounded-full px-5 py-2.5 text-small font-medium ring-1 transition duration-300 ease-smooth hover:-translate-y-0.5 ${
                      item === "Ваше решение"
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

      <CtaBanner title="Попробуйте на своих отзывах" />
    </PageShell>
  );
}
