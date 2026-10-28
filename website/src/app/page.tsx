import { PageShell } from "@/components/PageShell";
import { SectionHeading } from "@/components/SectionHeading";
import { TelegramButton } from "@/components/TelegramButton";
import { Button } from "@/components/Button";
import { TelegramMockup } from "@/components/TelegramMockup";
import { BotScreensShowcase } from "@/components/BotScreensShowcase";
import { TrustSection } from "@/components/TrustSection";
import { DualMarketplaceSection } from "@/components/DualMarketplaceSection";
import { QuickStartSection } from "@/components/QuickStartSection";
import { AutopilotGuardrailsSection } from "@/components/AutopilotGuardrailsSection";
import { MarketCompareSection } from "@/components/MarketCompareSection";
import { FeatureMapSection } from "@/components/FeatureMapSection";
import { ReviewHealthSection } from "@/components/ReviewHealthSection";
import { SellerScenariosSection } from "@/components/SellerScenariosSection";
import { PricingCards } from "@/components/PricingCards";
import { FAQAccordion } from "@/components/FAQAccordion";
import { FAQ_ITEMS } from "@/content/faq";
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
  { value: "WB + Ozon", label: "не нужно два разных сервиса" },
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
  { title: "Подключите кабинет", text: "Вставьте ключ WB или Ozon в бота. Это пара минут — подскажем, где его взять." },
  { title: "Получайте отзывы", text: "Бот пришлёт каждый новый отзыв или сводку утром — как удобнее." },
  { title: "Выберите ответ", text: "Три варианта на выбор. Берёте любой или правите под себя." },
  { title: "Отправьте", text: "На PRO — одной кнопкой из бота. На Lite — копируете в кабинет." },
];

const homeFaq = FAQ_ITEMS.filter((f) =>
  [
    "Где взять API-ключ и куда его вводить?",
    "Можно вообще не заходить в кабинет маркетплейса?",
    "Бот сам ответит на плохой отзыв?",
    "Только Wildberries или Ozon тоже?",
    "Это безопасно — отдавать боту ключ от кабинета?",
  ].includes(f.question),
);

export default function HomePage() {
  return (
    <PageShell>
      <JsonLd data={softwareSchema()} />
      <JsonLd data={faqSchema(FAQ_ITEMS.slice(0, 8))} />

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
              Wildberries и Ozon · прямо в Telegram
            </p>
            <h1 className="mt-7 text-display sm:text-display-lg lg:text-display-xl">
              Отвечайте на&nbsp;отзывы за&nbsp;минуты.{" "}
              <span className="text-brand-700">Без двух кабинетов.</span>
            </h1>
            <p className="prose-muted mt-7 max-w-prose">
              Бот присылает новые отзывы с WB и Ozon и сразу предлагает три варианта ответа в вашем
              стиле. Вы выбираете — покупатель видит живой ответ, а не шаблонную отписку.
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
              <p className="font-display text-headline font-semibold text-ink sm:text-display">{s.value}</p>
              <p className="mt-2 max-w-[14rem] text-small text-ink-muted">{s.label}</p>
            </Reveal>
          ))}
        </div>
      </section>

      <DualMarketplaceSection />

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
                Пришёл отзыв — бот уже подготовил три варианта. Вы выбираете, при желании правите и
                отправляете. На пятёрки можно отвечать автоматически, а плохие отзывы бот всегда
                оставляет вам.
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

      <QuickStartSection />

      <BotScreensShowcase />

      <TrustSection />

      <AutopilotGuardrailsSection />

      <MarketCompareSection />

      <FeatureMapSection />

      <ReviewHealthSection />

      {/* Benefits */}
      <section className="section-y">
        <div className="container-page">
          <Reveal>
            <SectionHeading
              eyebrow="Зачем это селлеру"
              title="Меньше рутины — больше контроля"
              description="Не заменяем вас перед покупателем. Убираем то, что можно убрать без риска."
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

      <SellerScenariosSection />

      {/* How it works */}
      <section className="section-y bg-surface-muted">
        <div className="container-page">
          <Reveal>
            <SectionHeading
              eyebrow="Как это устроено"
              title="Четыре шага в работе"
              description="После подключения кабинета — так каждый день."
            />
          </Reveal>
          <ol className="mt-16 grid gap-px overflow-hidden rounded-3xl border border-line bg-line sm:grid-cols-2 lg:mt-20 lg:grid-cols-4">
            {steps.map((s, i) => (
              <li key={s.title} className="group bg-surface p-8 transition-colors duration-300 hover:bg-surface-elevated">
                <Reveal delay={i * 90}>
                  <span className="font-display text-small font-semibold text-brand-600">0{i + 1}</span>
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
              description="Начните бесплатно: 5 ответов в день, без карты. Lite — 2 кабинета, PRO — 4 и отправка из бота."
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
              description="Не нашли свой вопрос? Напишите в поддержку — ответит живой человек."
            />
            <div className="mt-8">
              <Button href="/faq" variant="secondary" trailing={<IconArrowRight />}>
                Все вопросы
              </Button>
            </div>
          </Reveal>
          <Reveal delay={100}>
            <FAQAccordion items={homeFaq} />
          </Reveal>
        </div>
      </section>

      <CtaBanner />
    </PageShell>
  );
}
