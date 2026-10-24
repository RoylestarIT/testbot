import Link from "next/link";
import { PageShell } from "@/components/PageShell";
import { SectionHeading } from "@/components/SectionHeading";
import { TelegramButton } from "@/components/TelegramButton";
import { TelegramMockup } from "@/components/TelegramMockup";
import { PricingTable } from "@/components/PricingTable";
import { FAQAccordion } from "@/components/FAQAccordion";
import { FAQ_ITEMS } from "@/lib/faq";

const benefits = [
  {
    icon: "📱",
    title: "Telegram-first co-pilot",
    text: "Уведомление → три черновика → правка → publish или копия. Без перегруженного web-SaaS.",
  },
  {
    icon: "🛒",
    title: "WB + Ozon в одном боте",
    text: "Синхронизация, push, snooze, дайджест, история и калькулятор «подписка vs ₽ за ответ».",
  },
  {
    icon: "✍️",
    title: "ИИ с контролем",
    text: "Tone of voice, стоп-слова, шаблоны для 4–5★. Негатив 1–3★ — только после вашего решения.",
  },
  {
    icon: "💰",
    title: "Предсказуемый фикс",
    text: "Lite и PRO — фикс в месяц. На рынке часто встречают pay-per-answer (~1–3 ₽/ответ) или штат «только отзывы» (~30–80 тыс. ₽/мес).",
  },
];

const steps = [
  { n: "1", title: "Подключите кабинет", text: "WB/Ozon API в боте — ключи шифруются, на сайте не вводятся." },
  { n: "2", title: "Sync отзывов", text: "Push о новых отзывах, snooze и дайджест — всё в Telegram." },
  { n: "3", title: "3 варианта ответа", text: "ИИ предлагает черновики в вашем tone of voice." },
  { n: "4", title: "Publish или копия", text: "PRO — отправка в API из бота; Lite — копия в личный кабинет." },
];

export default function HomePage() {
  return (
    <PageShell>
      {/* Hero */}
      <section className="relative overflow-hidden bg-gradient-to-b from-white to-slate-50">
        <div className="mx-auto grid max-w-6xl gap-10 px-4 py-14 sm:px-6 lg:grid-cols-2 lg:items-center lg:py-20">
          <div>
            <p className="text-sm font-semibold text-blue-600">
              Время, деньги и лояльность покупателей — в одном Telegram
            </p>
            <h1 className="mt-3 text-balance text-4xl font-bold tracking-tight text-slate-900 sm:text-5xl">
              Голос бренда
            </h1>
            <p className="mt-5 text-pretty text-lg leading-relaxed text-slate-600">
              Отзывы не должны съедать ваш день. «Голос бренда» забирает рутину:
              подтягиваем WB/Ozon, предлагаем 3 варианта ответа — вы решаете, что
              увидит покупатель.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <TelegramButton trackSite>Начать бесплатно</TelegramButton>
              <TelegramButton variant="secondary">Попробовать PRO</TelegramButton>
            </div>
            <p className="mt-4 text-sm text-slate-500">
              Trial PRO — в боте, один раз на аккаунт · Free: 5 генераций в день
            </p>
          </div>
          <TelegramMockup />
        </div>
      </section>

      {/* Problem / solution */}
      <section className="mx-auto max-w-6xl px-4 py-16 sm:px-6">
        <div className="grid gap-10 lg:grid-cols-2 lg:items-start">
          <div>
            <SectionHeading
              align="left"
              eyebrow="Проблема"
              title="30–1000+ отзывов в месяц — некому «сидеть в кабинете»"
              description="Селлер или маленькая команда: отзывы важны для карточки, но каждый день уходит на копипаст и прыжки между WB и Ozon."
            />
          </div>
          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <h3 className="text-lg font-semibold text-slate-900">Решение</h3>
            <p className="mt-3 text-slate-600 leading-relaxed">
              Co-pilot в Telegram: sync → три варианта → вы правите → publish (PRO) или
              копия (Lite). Авто только на 4–5★; негатив не уходит без человека.
            </p>
            <blockquote className="mt-4 border-l-4 border-blue-500 pl-4 text-sm italic text-slate-600">
              «Раньше отзывы копились к вечеру. Сейчас отвечаю между созвонами — из
              Telegram.» — селлер WB/Ozon, имя по запросу
            </blockquote>
          </div>
        </div>
      </section>

      {/* Benefits */}
      <section className="bg-white py-16">
        <div className="mx-auto max-w-6xl px-4 sm:px-6">
          <SectionHeading
            title="Почему селлеры выбирают Telegram-first"
            description="Контроль и экономия времени — без обещаний «AI magic» и 100% автопилота."
          />
          <ul className="mt-12 grid gap-6 sm:grid-cols-2">
            {benefits.map((b) => (
              <li
                key={b.title}
                className="rounded-2xl border border-slate-200 p-6 shadow-sm"
              >
                <span className="text-2xl" aria-hidden>
                  {b.icon}
                </span>
                <h3 className="mt-3 text-lg font-semibold text-slate-900">{b.title}</h3>
                <p className="mt-2 text-sm leading-relaxed text-slate-600">{b.text}</p>
              </li>
            ))}
          </ul>
        </div>
      </section>

      {/* How it works */}
      <section className="mx-auto max-w-6xl px-4 py-16 sm:px-6">
        <SectionHeading
          title="Как это работает"
          description="Четыре шага — вся работа в @FeedBackReview_bot"
        />
        <ol className="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {steps.map((s) => (
            <li key={s.n} className="relative rounded-2xl bg-slate-50 p-5 ring-1 ring-slate-200">
              <span className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-600 text-sm font-bold text-white">
                {s.n}
              </span>
              <h3 className="mt-4 font-semibold text-slate-900">{s.title}</h3>
              <p className="mt-2 text-sm text-slate-600">{s.text}</p>
            </li>
          ))}
        </ol>
        <p className="mt-8 text-center">
          <Link href="/how-it-works" className="text-blue-600 font-medium hover:underline">
            Подробнее со схемой →
          </Link>
        </p>
      </section>

      {/* Features */}
      <section className="border-y border-slate-200 bg-slate-50 py-16">
        <div className="mx-auto max-w-6xl px-4 sm:px-6">
          <SectionHeading
            title="Возможности"
            description="Уже в боте — и коротко о roadmap"
          />
          <div className="mt-10 grid gap-8 lg:grid-cols-2">
            <ul className="space-y-2 text-sm text-slate-700">
              {[
                "Синхронизация отзывов WB/Ozon, push, snooze, дайджест",
                "3 варианта ответа (LLM), шаблоны 4–5★, правила авто (PRO)",
                "История, экспорт CSV, аналитика 7/30 дней",
                "Вопросы WB (уведомления; ответ в кабинете)",
                "Калькулятор подписка vs ₽ за ответ",
                "Промокоды, поддержка с контекстом, onboarding-чеклист",
              ].map((item) => (
                <li key={item} className="flex gap-2">
                  <span className="text-green-600" aria-hidden>
                    ✓
                  </span>
                  {item}
                </li>
              ))}
            </ul>
            <div className="rounded-2xl border border-dashed border-slate-300 bg-white p-6">
              <h3 className="font-semibold text-slate-900">Скоро / по спросу</h3>
              <ul className="mt-3 space-y-2 text-sm text-slate-600">
                <li>Мягкая рекомендация товара в ответе (PRO)</li>
                <li>Очередь вопросов Ozon</li>
                <li>Расширенная аналитика</li>
              </ul>
              <p className="mt-4 text-xs text-slate-500">
                Не в фокусе: Яндекс Маркет, автомат на 1–3★, отдельный web-кабинет
                вместо Telegram.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing preview */}
      <section className="mx-auto max-w-6xl px-4 py-16 sm:px-6">
        <SectionHeading title="Тарифы" description="Актуальные цифры — в боте при оплате" />
        <div className="mt-10">
          <PricingTable compact />
        </div>
        <p className="mt-6 text-center">
          <Link href="/pricing" className="font-medium text-blue-600 hover:underline">
            Полная таблица и способы оплаты →
          </Link>
        </p>
      </section>

      {/* FAQ preview */}
      <section className="bg-white py-16">
        <div className="mx-auto max-w-3xl px-4 sm:px-6">
          <SectionHeading title="Частые вопросы" />
          <div className="mt-10">
            <FAQAccordion items={FAQ_ITEMS.slice(0, 5)} />
          </div>
          <p className="mt-6 text-center">
            <Link href="/faq" className="font-medium text-blue-600 hover:underline">
              Все вопросы →
            </Link>
          </p>
        </div>
      </section>

      {/* Footer CTA */}
      <section className="bg-blue-600 py-14">
        <div className="mx-auto max-w-3xl px-4 text-center sm:px-6">
          <h2 className="text-2xl font-bold text-white sm:text-3xl">
            Откройте бота и подключите первый кабинет
          </h2>
          <p className="mt-3 text-blue-100">
            @FeedBackReview_bot · Free без карты · PRO trial в один клик
          </p>
          <div className="mt-8 flex justify-center">
            <TelegramButton
              variant="secondary"
              trackSite
              className="!bg-white !text-blue-700 hover:!bg-blue-50"
            >
              Открыть в Telegram
            </TelegramButton>
          </div>
        </div>
      </section>
    </PageShell>
  );
}
