import { PageShell } from "@/components/PageShell";
import { SectionHeading } from "@/components/SectionHeading";
import { TelegramButton } from "@/components/TelegramButton";
import { Button } from "@/components/Button";
import { TelegramMockup } from "@/components/TelegramMockup";
import { PricingCards } from "@/components/PricingCards";
import { FAQAccordion } from "@/components/FAQAccordion";
import { FAQ_ITEMS } from "@/content/faq";
import { MarketplaceStrip } from "@/components/MarketplaceStrip";
import { FeatureCard } from "@/components/FeatureCard";
import { Reveal } from "@/components/Reveal";
import { CtaBanner } from "@/components/CtaBanner";
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
  { value: "2", label: "маркетплейса в одном чате" },
  { value: "4–5★", label: "можно отвечать автоматически" },
  { value: "1–3★", label: "только после вашего одобрения" },
];

const benefits = [
  {
    icon: <IconTelegram />,
    title: "Всё в Telegram",
    text: "Новый отзыв приходит сообщением — отвечаете там же, между делами. Без лишних вкладок и кабинетов.",
  },
  {
    icon: <IconSpark />,
    title: "WB и Ozon вместе",
    text: "Отзывы с обеих площадок в одной ленте. Отложить, получить дайджест, посмотреть историю.",
  },
  {
    icon: <IconShield />,
    title: "ИИ под контролем",
    text: "Тон бренда, стоп-слова и шаблоны — ваши. Негатив никогда не уходит без вашего решения.",
  },
  {
    icon: <IconWallet />,
    title: "Цена без сюрпризов",
    text: "Фиксированная подписка вместо оплаты за каждый ответ. Бюджет известен заранее.",
  },
];

const steps = [
  { title: "Подключите кабинет", text: "Добавьте API-ключ WB или Ozon в боте. Ключи шифруются." },
  { title: "Получайте отзывы", text: "Бот присылает каждый новый отзыв — или дайджест раз в день." },
  { title: "Выберите ответ", text: "Три черновика в тоне бренда. Возьмите любой или поправьте." },
  { title: "Опубликуйте", text: "На PRO — прямо из бота. На Lite — скопируйте в кабинет." },
];

const nowFeatures = [
  "Синхронизация отзывов WB и Ozon",
  "Три варианта ответа от ИИ",
  "Шаблоны и автоответы на 4\u2060–\u20605★ (PRO)",
  "История, экспорт в CSV, аналитика",
  "Уведомления о вопросах WB",
  "Калькулятор «подписка или оплата за ответ»",
];

export default function HomePage() {
  return (
    <PageShell>
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
              Для селлеров Wildberries и Ozon
            </p>
            <h1 className="mt-7 text-display sm:text-display-lg lg:text-display-xl">
              Ответы на&nbsp;отзывы за&nbsp;минуты.{" "}
              <span className="text-brand-700">Прямо в&nbsp;Telegram.</span>
            </h1>
            <p className="prose-muted mt-7 max-w-prose">
              Бот собирает отзывы с WB и Ozon и предлагает три ответа в тоне вашего бренда.
              Вы выбираете — покупатель получает живой ответ.
            </p>
            <div className="mt-10 flex flex-wrap items-center gap-3">
              <TelegramButton trackSite size="lg">
                Начать бесплатно
              </TelegramButton>
              <Button
                href="/how-it-works"
                variant="secondary"
                size="lg"
                trailing={<IconArrowRight />}
              >
                Как это работает
              </Button>
            </div>
            <p className="mt-5 text-small text-ink-subtle">
              Без карты · 5 ответов в день бесплатно · Негатив — только с вашего одобрения
            </p>
            <div className="mt-12 border-t border-line pt-6">
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
              title="Отзывов всё больше, а времени — нет"
              description="Сотни отзывов в месяц, два кабинета и бесконечный копипаст. Отвечать важно — но не ценой всего рабочего дня."
            />
          </Reveal>
          <Reveal delay={100}>
            <div className="card p-8 sm:p-10">
              <p className="eyebrow">Наш подход</p>
              <h3 className="mt-4 text-headline">Бот готовит — решаете вы</h3>
              <p className="mt-4 text-body text-ink-muted">
                Отзыв → три черновика → ваша правка → публикация. Автоответы — только на
                4–5★. Негативные отзывы без вашего решения не уходят никогда.
              </p>
              <figure className="mt-8 border-l-2 border-clay-300 pl-5">
                <blockquote className="text-body-lg text-ink">
                  «Раньше отзывы копились к вечеру. Теперь отвечаю между созвонами — прямо из
                  Telegram».
                </blockquote>
                <figcaption className="mt-3 text-small text-ink-subtle">
                  Селлер на WB и Ozon
                </figcaption>
              </figure>
            </div>
          </Reveal>
        </div>
      </section>

      {/* Benefits */}
      <section className="section-y bg-surface-muted">
        <div className="container-page">
          <Reveal>
            <SectionHeading
              eyebrow="Преимущества"
              title="Всё для ответов. Ничего лишнего"
              description="Экономим ваше время, а не обещаем магию ИИ и стопроцентный автопилот."
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

      {/* How it works */}
      <section className="section-y">
        <div className="container-page">
          <Reveal>
            <SectionHeading
              eyebrow="Как это работает"
              title="Четыре шага до первого ответа"
              description="Никаких внедрений и обучений — всё происходит в @FeedBackReview_bot."
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
              Подробнее о процессе
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
              title="Что уже умеет бот"
              description="Работает сегодня. Новые функции добавляем по запросам селлеров."
            />
            <div className="mt-10 rounded-2xl border border-dashed border-brand-200 bg-brand-50/50 p-6">
              <p className="eyebrow">Скоро</p>
              <ul className="mt-3 space-y-1.5 text-body text-ink-muted">
                <li>Рекомендация товара в ответе</li>
                <li>Очередь вопросов Ozon</li>
                <li>Расширенная аналитика</li>
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
              Пока не планируем: Яндекс Маркет, автоответы на 1–3★, отдельный веб-кабинет.
            </p>
          </Reveal>
        </div>
      </section>

      {/* Pricing */}
      <section className="section-y">
        <div className="container-page">
          <Reveal>
            <SectionHeading
              eyebrow="Тарифы"
              title="Платите за подписку, а не за каждый ответ"
              description="Начните бесплатно и переходите на платный тариф, когда отзывов станет больше."
            />
          </Reveal>
          <div className="mt-16 lg:mt-20">
            <PricingCards />
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
              eyebrow="FAQ"
              title="Частые вопросы"
              description="Не нашли ответ? Напишите в поддержку прямо в боте."
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
