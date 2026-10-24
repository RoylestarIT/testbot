import type { Metadata } from "next";
import Link from "next/link";
import { canonical } from "@/content/constants";
import { PageShell } from "@/components/PageShell";
import { SectionHeading } from "@/components/SectionHeading";
import { TelegramButton } from "@/components/TelegramButton";
import { TelegramMockup } from "@/components/TelegramMockup";
import { PricingTable } from "@/components/PricingTable";
import { FAQAccordion } from "@/components/FAQAccordion";
import { FAQ_ITEMS } from "@/content/faq";
import { MarketplaceStrip } from "@/components/MarketplaceStrip";
import { FeatureCard } from "@/components/FeatureCard";
import { IconShield, IconSpark, IconTelegram, IconWallet, IconCheck } from "@/components/icons";

const steps = [
  { n: "1", title: "Подключите кабинет", text: "WB/Ozon API в боте — ключи шифруются, на сайте не вводятся." },
  { n: "2", title: "Sync отзывов", text: "Push о новых отзывах, snooze и дайджест — всё в Telegram." },
  { n: "3", title: "3 варианта ответа", text: "ИИ предлагает черновики в вашем tone of voice." },
  { n: "4", title: "Publish или копия", text: "PRO — отправка в API из бота; Lite — копия в личный кабинет." },
];

export const metadata: Metadata = {
  alternates: canonical(),
};

export default function HomePage() {
  return (
    <PageShell>
      {/* Hero */}
      <section className="relative overflow-hidden bg-hero-mesh">
        <div className="container-page grid gap-12 pb-16 pt-10 sm:pt-14 lg:grid-cols-2 lg:items-center lg:gap-16 lg:pb-24 lg:pt-16">
          <div>
            <p className="badge-pill w-fit">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-500/90" aria-hidden />
              Telegram-first для селлеров
            </p>
            <h1 className="mt-6 text-balance font-display text-display-lg text-ink sm:text-[3.5rem]">
              Голос бренда
            </h1>
            <p className="mt-3 font-display text-body-lg font-semibold text-brand-700">
              Время, деньги и лояльность покупателей — в одном Telegram
            </p>
            <p className="prose-muted mt-5 max-w-xl text-pretty">
              Отзывы не должны съедать ваш день. Подтягиваем WB/Ozon, предлагаем 3
              варианта ответа — вы решаете, что увидит покупатель.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <TelegramButton trackSite>
                Начать бесплатно
              </TelegramButton>
              <TelegramButton variant="secondary">
                Попробовать PRO
              </TelegramButton>
            </div>
            <p className="mt-4 text-caption text-ink-subtle">
              Trial PRO в боте · Free: 5 генераций в день · негатив только вручную
            </p>
            <div className="mt-8">
              <MarketplaceStrip />
            </div>
          </div>
          <div className="lg:justify-self-end">
            <TelegramMockup />
          </div>
        </div>
      </section>

      {/* Trust stats */}
      <section className="border-y border-line bg-surface">
        <div className="container-page grid grid-cols-2 gap-6 py-11 sm:grid-cols-4 sm:gap-8">
          {[
            ["3", "варианта ответа ИИ"],
            ["2", "маркетплейса в одном боте"],
            ["4–5★", "авто только на PRO"],
            ["1–3★", "только с вашего OK"],
          ].map(([val, label]) => (
            <div key={label} className="text-center sm:text-left">
              <p className="font-display text-3xl font-bold tracking-tight text-brand-700 sm:text-[2rem]">
                {val}
              </p>
              <p className="mt-1.5 text-caption text-ink-muted">{label}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Problem / solution */}
      <section className="section-y">
        <div className="container-page grid gap-10 lg:grid-cols-2 lg:items-center">
          <SectionHeading
            align="left"
            eyebrow="Задача"
            title="30–1000+ отзывов в месяц — некому «сидеть в кабинете»"
            description="Селлер или маленькая команда: отзывы важны для карточки, но каждый день уходит на копипаст и прыжки между WB и Ozon."
          />
          <div className="card p-8 lg:p-9">
            <p className="eyebrow">Наш подход</p>
            <h3 className="mt-2 font-display text-title text-ink">
              Co-pilot, а не «чёрный ящик»
            </h3>
            <p className="mt-4 text-body text-ink-muted">
              Sync → три черновика → вы правите → publish (PRO) или копия (Lite). Авто
              только на 4–5★; негатив не уходит без человека.
            </p>
            <blockquote className="mt-6 rounded-xl border border-brand-100/80 bg-brand-50/50 p-4 text-body italic text-ink-muted">
              «Раньше отзывы копились к вечеру. Сейчас отвечаю между созвонами — из
              Telegram.» — селлер WB/Ozon
            </blockquote>
          </div>
        </div>
      </section>

      {/* Benefits */}
      <section className="section-y bg-surface-muted/80">
        <div className="container-page">
          <SectionHeading
            title="Почему селлеры выбирают нас"
            description="Контроль и экономия времени — без обещаний «магии ИИ» и 100% автопилота."
          />
          <ul className="mt-14 grid gap-6 sm:grid-cols-2">
            <FeatureCard icon={<IconTelegram />} title="Telegram-first co-pilot" highlight>
              Уведомление → три черновика → правка → publish или копия. Без перегруженного
              web-SaaS — вся работа там, где вы и так онлайн.
            </FeatureCard>
            <FeatureCard icon={<IconSpark />} title="WB + Ozon в одном боте">
              Синхронизация, push, snooze, дайджест, история и калькулятор «подписка vs ₽
              за ответ».
            </FeatureCard>
            <FeatureCard icon={<IconShield />} title="ИИ с контролем">
              Tone of voice, стоп-слова, шаблоны для 4–5★. Негатив 1–3★ — только после
              вашего решения.
            </FeatureCard>
            <FeatureCard icon={<IconWallet />} title="Предсказуемый фикс">
              Lite и PRO — фикс в месяц. На рынке часто pay-per-answer (~1–3 ₽/ответ) или
              штат «только отзывы» (~30–80 тыс. ₽/мес).
            </FeatureCard>
          </ul>
        </div>
      </section>

      {/* How it works */}
      <section className="section-y">
        <div className="container-page">
          <SectionHeading
            title="Как это работает"
            description="Четыре шага — вся работа в @FeedBackReview_bot"
          />
          <ol className="mt-14 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
            {steps.map((s) => (
              <li
                key={s.n}
                className="card-hover relative flex flex-col p-6 before:absolute before:left-6 before:top-0 before:hidden before:h-full before:w-px before:bg-gradient-to-b before:from-brand-200 before:to-transparent lg:before:-right-3 lg:before:left-auto lg:before:block lg:last:before:hidden"
              >
                <span className="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-brand-600 to-brand-500 text-sm font-bold text-white shadow-md">
                  {s.n}
                </span>
                <h3 className="mt-5 font-semibold text-slate-900">{s.title}</h3>
                <p className="mt-2 flex-1 text-sm leading-relaxed text-slate-600">{s.text}</p>
              </li>
            ))}
          </ol>
          <p className="mt-10 text-center">
            <Link href="/how-it-works" className="link-arrow">
              Подробнее со схемой →
            </Link>
          </p>
        </div>
      </section>

      {/* Features bento */}
      <section className="section-y border-y border-slate-200/80 bg-white">
        <div className="container-page">
          <SectionHeading
            title="Возможности платформы"
            description="Уже в боте — плюс roadmap по запросу селлеров"
          />
          <div className="mt-14 grid gap-6 lg:grid-cols-3">
            <div className="card p-8 lg:col-span-2">
              <h3 className="font-semibold text-slate-900">В продукте сейчас</h3>
              <ul className="mt-6 grid gap-3 sm:grid-cols-2">
                {[
                  "Синхронизация отзывов WB/Ozon, push, snooze, дайджест",
                  "3 варианта ответа (LLM), шаблоны 4–5★, правила авто (PRO)",
                  "История, экспорт CSV, аналитика 7/30 дней",
                  "Вопросы WB (уведомления; ответ в кабинете)",
                  "Калькулятор подписка vs ₽ за ответ",
                  "Промокоды, поддержка с контекстом, onboarding",
                ].map((item) => (
                  <li key={item} className="flex gap-2.5 text-sm text-slate-700">
                    <span
                      className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-emerald-100 text-emerald-700"
                      aria-hidden
                    >
                      <IconCheck className="h-3 w-3" />
                    </span>
                    {item}
                  </li>
                ))}
              </ul>
            </div>
            <div className="flex flex-col gap-4">
              <div className="card flex-1 border-dashed border-brand-200 bg-brand-50/30 p-6">
                <p className="text-xs font-bold uppercase tracking-widest text-brand-600">
                  Скоро
                </p>
                <ul className="mt-4 space-y-2 text-sm text-slate-700">
                  <li>Рекомендация товара в ответе (PRO)</li>
                  <li>Очередь вопросов Ozon</li>
                  <li>Расширенная аналитика</li>
                </ul>
              </div>
              <p className="text-xs leading-relaxed text-slate-500">
                Не в фокусе: Яндекс Маркет, автомат на 1–3★, отдельный web-кабинет вместо
                Telegram.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing preview */}
      <section className="section-y bg-surface-muted/80">
        <div className="container-page">
          <SectionHeading title="Тарифы" description="Актуальные цифры — в боте при оплате" />
          <div className="mt-12">
            <PricingTable compact />
          </div>
          <p className="mt-8 text-center">
            <Link href="/pricing" className="link-arrow">
              Полная таблица и способы оплаты →
            </Link>
          </p>
        </div>
      </section>

      {/* FAQ preview */}
      <section className="section-y">
        <div className="container-page max-w-3xl">
          <SectionHeading title="Частые вопросы" />
          <div className="mt-12">
            <FAQAccordion items={FAQ_ITEMS.slice(0, 5)} />
          </div>
          <p className="mt-8 text-center">
            <Link href="/faq" className="link-arrow">
              Все вопросы →
            </Link>
          </p>
        </div>
      </section>

      {/* Footer CTA */}
      <section className="relative overflow-hidden bg-cta-gradient py-16 sm:py-20">
        <div
          className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGcgZmlsbD0ibm9uZSIgZmlsbC1vcGFjaXR5PSIuMDUiPjxjaXJjbGUgY3g9IjEiIGN5PSIxIiByPSIxIiBmaWxsPSIjZmZmIi8+PC9nPjwvc3ZnPg==')] opacity-40"
          aria-hidden
        />
        <div className="container-page relative max-w-3xl text-center">
          <h2 className="text-balance text-2xl font-bold text-white sm:text-3xl lg:text-4xl">
            Подключите первый кабинет за пару минут
          </h2>
          <p className="mx-auto mt-4 max-w-lg text-pretty text-blue-50/95">
            @FeedBackReview_bot · Free без карты · PRO trial в один клик
          </p>
          <div className="mt-9 flex flex-wrap justify-center gap-3">
            <TelegramButton variant="white" trackSite>
              Открыть в Telegram
            </TelegramButton>
          </div>
        </div>
      </section>
    </PageShell>
  );
}
