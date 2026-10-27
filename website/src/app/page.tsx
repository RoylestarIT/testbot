import { PageShell } from "@/components/PageShell";
import { SectionHeading } from "@/components/SectionHeading";
import { TelegramButton } from "@/components/TelegramButton";
import { Button } from "@/components/Button";
import { TelegramMockup } from "@/components/TelegramMockup";
import { BotScreensShowcase } from "@/components/BotScreensShowcase";
import { TestimonialsSection } from "@/components/TestimonialsSection";
import { TrustSection } from "@/components/TrustSection";
import { PricingCards } from "@/components/PricingCards";
import { FAQAccordion } from "@/components/FAQAccordion";
import { FAQ_ITEMS } from "@/content/faq";
import { TESTIMONIALS } from "@/content/testimonials";
import { MarketplaceStrip } from "@/components/MarketplaceStrip";
import { FeatureCard } from "@/components/FeatureCard";
import { Reveal } from "@/components/Reveal";
import { CtaBanner } from "@/components/CtaBanner";
import { CalculatorBlock } from "@/components/CalculatorBlock";
import { JsonLd, faqSchema, softwareSchema } from "@/components/JsonLd";
import {
  IconArrowRight,
  IconCheck,
  IconShield,
  IconSpark,
  IconTelegram,
  IconWallet,
} from "@/components/icons";

const stats = [
  { value: "3", label: "варианта ответа на каждый отзыв" },
  { value: "2", label: "площадки в одном чате — WB и Ozon" },
  { value: "~30 сек", label: "чтобы выбрать и отправить ответ" },
  { value: "0", label: "автоответов на плохие отзывы" },
];

const benefits = [
  {
    icon: <IconTelegram />,
    title: "Отвечаете там, где и так сидите",
    text: "Новый отзыв приходит в Telegram. Ответили между делами — и забыли. Не нужно держать открытыми два кабинета.",
  },
  {
    icon: <IconSpark />,
    title: "WB и Ozon в одном месте",
    text: "Все отзывы с обеих площадок в одной ленте. Можно отложить на потом или получать сводку раз в день.",
  },
  {
    icon: <IconShield />,
    title: "Звучит как вы, а не как робот",
    text: "Один раз расскажите боту, как вы общаетесь с покупателями, — и ответы будут в вашем стиле. Запретные слова тоже можно задать.",
  },
  {
    icon: <IconWallet />,
    title: "Понятная цена",
    text: "Фиксированная сумма в месяц. Не нужно считать, сколько стоил каждый ответ.",
  },
];

const steps = [
  { title: "Подключите кабинет", text: "Вставьте ключ WB или Ozon в бота. Это пара минут." },
  { title: "Получайте отзывы", text: "Бот пришлёт каждый новый отзыв или сводку утром — как удобнее." },
  { title: "Выберите ответ", text: "Три варианта на выбор. Берёте любой или правите под себя." },
  { title: "Отправьте", text: "На PRO — одной кнопкой из бота. На Lite — копируете в кабинет." },
];

const nowFeatures = [
  "Отзывы с WB и Ozon в одном чате",
  "Три варианта ответа на выбор",
  "Свои фразы и автоответы на 4\u2060–\u20605★ (PRO)",
  "История ответов и выгрузка в Excel",
  "Уведомления о вопросах покупателей на WB",
  "Сводка: сколько отвечено за неделю",
];

export default function HomePage() {
  return (
    <PageShell>
      <JsonLd data={softwareSchema()} />
      <JsonLd data={faqSchema(FAQ_ITEMS.slice(0, 5))} />

      {/* Hero */}
      <section className="relative -mt-16 overflow-hidden pt-16 sm:-mt-[4.5rem] sm:pt-[4.5rem]">
        <div className="absolute inset-0 bg-hero-mesh" aria-hidden />
        <div className="mask-fade-b absolute inset-0 bg-grid-lines bg-grid opacity-70" aria-hidden />
        <div className="container-page relative grid gap-16 pb-24 pt-14 sm:pt-20 lg:grid-cols-[1.1fr_0.9fr] lg:items-center lg:gap-20 lg:pb-32 lg:pt-24">
          <div className="animate-fade-up">
            <p className="badge-pill w-fit">
              <span className="relative flex h-2 w-2" aria-hidden>
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-brand-400 opacity-60" />
                <span className="relative inline-flex h-2 w-2 rounded-full bg-brand-500" />
              </span>
              Для продавцов на Wildberries и Ozon
            </p>
            <h1 className="mt-7 text-display sm:text-display-lg lg:text-display-xl">
              Отвечайте на&nbsp;отзывы за&nbsp;минуты.{" "}
              <span className="text-brand-700">Прямо в&nbsp;Telegram.</span>
            </h1>
            <p className="prose-muted mt-7 max-w-prose">
              Бот присылает новые отзывы и сразу предлагает три варианта ответа в вашем
              стиле. Вы выбираете лучший — покупатель получает живой, человеческий ответ.
            </p>
            <div className="mt-10 flex flex-wrap items-center gap-3">
              <TelegramButton trackSite size="lg">
                Попробовать бесплатно
              </TelegramButton>
              <Button href="/#calculator" variant="secondary" size="lg" trailing={<IconArrowRight />}>
                Посчитать экономию
              </Button>
            </div>
            <p className="mt-5 text-small text-ink-subtle">
              Без карты · 5 ответов в день бесплатно · Плохие отзывы — только через вас
            </p>

            <div className="mt-10 flex flex-wrap items-center gap-4">
              <div className="flex -space-x-2.5" aria-hidden>
                {TESTIMONIALS.slice(0, 5).map((t, i) => (
                  <span
                    key={t.name}
                    className={`flex h-9 w-9 items-center justify-center rounded-full font-display text-caption font-semibold ring-2 ring-[var(--background)] ${
                      ["bg-brand-100 text-brand-800", "bg-clay-100 text-clay-600", "bg-[#e4ecf5] text-[#2d5b8a]", "bg-[#efe7f3] text-[#6b4483]", "bg-brand-200 text-brand-900"][i]
                    }`}
                  >
                    {t.name.slice(0, 1)}
                  </span>
                ))}
              </div>
              <div>
                <div className="flex gap-0.5 text-clay-500" aria-hidden>
                  {Array.from({ length: 5 }).map((_, j) => (
                    <svg key={j} viewBox="0 0 20 20" className="h-3.5 w-3.5" fill="currentColor">
                      <path d="M10 1.5l2.6 5.3 5.9.9-4.3 4.1 1 5.8L10 14.9l-5.2 2.7 1-5.8L1.5 7.7l5.9-.9z" />
                    </svg>
                  ))}
                </div>
                <p className="mt-1 text-small text-ink-muted">
                  Селлеры уже отвечают на отзывы через бота
                </p>
              </div>
            </div>

            <div className="mt-10 border-t border-line pt-6">
              <MarketplaceStrip />
            </div>
          </div>
          <div className="animate-fade-up [animation-delay:150ms] lg:justify-self-end">
            <TelegramMockup />
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="border-y border-line bg-surface">
        <div className="container-page grid grid-cols-2 divide-line lg:grid-cols-4 lg:divide-x">
          {stats.map((s, i) => (
            <Reveal key={s.label} delay={i * 70} className="px-2 py-10 sm:py-12 lg:px-8 lg:first:pl-0">
              <p className="font-display text-headline font-semibold text-ink sm:text-display">
                {s.value}
              </p>
              <p className="mt-2 max-w-[14rem] text-small text-ink-muted">{s.label}</p>
            </Reveal>
          ))}
        </div>
      </section>

      {/* Problem / approach */}
      <section className="section-y">
        <div className="container-page grid gap-14 lg:grid-cols-2 lg:items-center lg:gap-20">
          <Reveal>
            <SectionHeading
              align="left"
              eyebrow="Знакомо?"
              title="Отзывов всё больше, а времени на них — нет"
              description="Вечером открываете кабинет, а там сорок новых отзывов. Каждому хочется ответить по-человечески, но на это уходит час, а то и два."
            />
          </Reveal>
          <Reveal delay={100}>
            <div className="card p-8 sm:p-10">
              <p className="eyebrow">Как мы это решаем</p>
              <h3 className="mt-4 text-headline">Бот пишет черновики — вы решаете</h3>
              <p className="mt-4 text-body text-ink-muted">
                Пришёл отзыв — бот уже подготовил три варианта ответа. Вы выбираете, при
                желании правите и отправляете. На пятёрки можно отвечать автоматически, а
                плохие отзывы бот всегда оставляет вам.
              </p>
              <ul className="mt-8 grid gap-3 sm:grid-cols-2">
                {["Без копипаста", "Без двух открытых кабинетов", "Без шаблонных отписок", "Без риска нагрубить"].map(
                  (item) => (
                    <li key={item} className="list-check">
                      <span className="list-check-icon" aria-hidden>
                        <IconCheck className="h-3 w-3" />
                      </span>
                      <span className="text-ink">{item}</span>
                    </li>
                  ),
                )}
              </ul>
            </div>
          </Reveal>
        </div>
      </section>

      <BotScreensShowcase />

      <TrustSection />

      {/* Benefits */}
      <section className="section-y bg-surface-muted">
        <div className="container-page">
          <Reveal>
            <SectionHeading
              eyebrow="Что вы получаете"
              title="Простой инструмент, который просто работает"
              description="Без сложных настроек, обучения и отдельного сайта. Только то, что реально экономит время."
            />
          </Reveal>
          <div className="mt-16 grid gap-5 sm:grid-cols-2 lg:mt-20">
            {benefits.map((b, i) => (
              <Reveal key={b.title} delay={i * 80}>
                <FeatureCard icon={b.icon} title={b.title}>
                  {b.text}
                </FeatureCard>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      <TestimonialsSection />

      {/* How it works */}
      <section className="section-y">
        <div className="container-page">
          <Reveal>
            <SectionHeading
              eyebrow="Как начать"
              title="Четыре шага до первого ответа"
              description="Ничего устанавливать не нужно — всё происходит в Telegram."
            />
          </Reveal>
          <ol className="mt-16 grid gap-px overflow-hidden rounded-3xl border border-line bg-line sm:grid-cols-2 lg:mt-20 lg:grid-cols-4">
            {steps.map((s, i) => (
              <li key={s.title} className="group bg-surface p-8 transition-colors duration-300 hover:bg-surface-elevated">
                <Reveal delay={i * 90}>
                  <span className="font-display text-small font-semibold text-brand-600">
                    0{i + 1}
                  </span>
                  <div className="mt-8 h-px w-10 bg-brand-300 transition-all duration-500 ease-smooth group-hover:w-20 group-hover:bg-brand-600" />
                  <h3 className="mt-8 text-title">{s.title}</h3>
                  <p className="mt-3 text-body text-ink-muted">{s.text}</p>
                </Reveal>
              </li>
            ))}
          </ol>
          <p className="mt-10 text-center">
            <Button href="/how-it-works" variant="ghost" trailing={<IconArrowRight />}>
              Подробнее, как всё устроено
            </Button>
          </p>
        </div>
      </section>

      {/* Features */}
      <section className="section-y border-y border-line bg-surface">
        <div className="container-page grid gap-14 lg:grid-cols-[0.9fr_1.1fr] lg:gap-20">
          <Reveal>
            <SectionHeading
              align="left"
              eyebrow="Возможности"
              title="Что бот умеет уже сейчас"
              description="И мы продолжаем добавлять то, о чём просят селлеры."
            />
            <div className="mt-10 rounded-2xl border border-dashed border-brand-200 bg-brand-50/50 p-6">
              <p className="eyebrow">Скоро</p>
              <ul className="mt-3 space-y-1.5 text-body text-ink-muted">
                <li>Подсказка «посмотрите ещё этот товар» в ответе</li>
                <li>Вопросы покупателей с Ozon</li>
                <li>Больше статистики по отзывам</li>
              </ul>
            </div>
          </Reveal>
          <Reveal delay={100}>
            <ul className="grid gap-x-8 sm:grid-cols-2">
              {nowFeatures.map((item) => (
                <li key={item} className="list-check border-b border-line py-5">
                  <span className="list-check-icon" aria-hidden>
                    <IconCheck className="h-3 w-3" />
                  </span>
                  <span className="text-ink">{item}</span>
                </li>
              ))}
            </ul>
            <p className="mt-6 text-small text-ink-subtle">
              Чего не будет: автоответов на плохие отзывы. Это наш принцип.
            </p>
          </Reveal>
        </div>
      </section>

      {/* Calculator */}
      <section className="section-y">
        <div className="container-page">
          <Reveal>
            <CalculatorBlock />
          </Reveal>
        </div>
      </section>

      {/* Pricing */}
      <section className="section-y !pt-0">
        <div className="container-page">
          <Reveal>
            <SectionHeading
              eyebrow="Тарифы"
              title="Платите за месяц, а не за каждый ответ"
              description="Начните бесплатно. Перейдёте на платный тариф, когда поймёте, что без бота уже не хочется."
            />
          </Reveal>
          <div className="mt-16 lg:mt-20">
            <PricingCards showDisclaimer />
          </div>
          <p className="mt-10 text-center">
            <Button href="/pricing" variant="ghost" trailing={<IconArrowRight />}>
              Сравнить тарифы подробно
            </Button>
          </p>
        </div>
      </section>

      {/* FAQ */}
      <section className="section-y bg-surface-muted">
        <div className="container-page grid gap-12 lg:grid-cols-[0.8fr_1.2fr] lg:gap-20">
          <Reveal>
            <SectionHeading
              align="left"
              eyebrow="Вопросы"
              title="Отвечаем честно"
              description="Не нашли свой вопрос? Напишите нам — ответит живой человек."
            />
            <div className="mt-8">
              <Button href="/faq" variant="secondary" trailing={<IconArrowRight />}>
                Все вопросы
              </Button>
            </div>
          </Reveal>
          <Reveal delay={100}>
            <FAQAccordion items={FAQ_ITEMS.slice(0, 5)} />
          </Reveal>
        </div>
      </section>

      <CtaBanner />
    </PageShell>
  );
}
