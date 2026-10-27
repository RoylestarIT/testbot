import type { Metadata } from "next";
import { PageShell } from "@/components/PageShell";
import { InnerPageHero } from "@/components/InnerPageHero";
import { PricingCards } from "@/components/PricingCards";
import { PricingTable } from "@/components/PricingTable";
import { Reveal } from "@/components/Reveal";
import { SectionHeading } from "@/components/SectionHeading";
import { FAQAccordion } from "@/components/FAQAccordion";
import { CtaBanner } from "@/components/CtaBanner";
import { SavingsCalculator } from "@/components/SavingsCalculator";
import { FAQ_ITEMS } from "@/content/faq";
import { PRICING_UPDATED } from "@/content/constants";

export const metadata: Metadata = {
  title: "Тарифы Free, Lite и PRO",
  description:
    "Сравнение тарифов «Голос бренда»: генерации, кабинеты, publish в API, авто 4–5★. Lite 990 ₽ / 35 BYN, PRO 1990 ₽ / 70 BYN в месяц.",
};

const payments = [
  { title: "Telegram Stars", text: "Мгновенно, прямо в чате" },
  { title: "Crypto Bot", text: "USDT и другие монеты" },
  { title: "Карта РФ / РБ", text: "Через платёжную форму" },
  { title: "СБП или перевод", text: "Активация до 24 часов" },
];

const alternatives = [
  {
    title: "Оплата за ответ",
    text: "~1–3 ₽ за каждый ответ. Чем больше отзывов, тем сложнее прогнозировать бюджет.",
  },
  {
    title: "Сотрудник на отзывы",
    text: "Часто 30–80 тыс. ₽ в месяц, плюс зависимость от графика и отпусков.",
  },
  {
    title: "Голос бренда",
    text: "Фиксированная подписка. Бот снимает рутину, а стратегия и финальное слово — у вас.",
    highlight: true,
  },
];

const pricingFaq = FAQ_ITEMS.filter((f) =>
  ["Что такое Trial PRO?", "Как оплатить и когда активируется подписка?", "Как отменить подписку?"].includes(
    f.question,
  ),
);

export default function PricingPage() {
  return (
    <PageShell>
      <InnerPageHero
        eyebrow="Тарифы"
        title="Простые тарифы без оплаты за ответ"
        description="Начните бесплатно. Переходите на Lite или PRO, когда отзывов станет больше."
      />

      <section className="pb-20 sm:pb-24">
        <div className="container-page">
          <PricingCards showDisclaimer />
          <p className="mt-8 text-center text-small text-ink-subtle">
            Цены на {PRICING_UPDATED}. Актуальная сумма всегда показывается в боте перед оплатой.
          </p>
        </div>
      </section>

      <section className="pb-20 sm:pb-24 lg:pb-32">
        <div className="container-page">
          <Reveal>
            <SavingsCalculator />
          </Reveal>
        </div>
      </section>

      <section className="section-y border-y border-line bg-surface">
        <div className="container-page">
          <Reveal>
            <SectionHeading eyebrow="Подробно" title="Сравнение тарифов" />
          </Reveal>
          <Reveal delay={100} className="mt-14">
            <PricingTable compact />
          </Reveal>

          <div className="mt-20 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {payments.map((p, i) => (
              <Reveal key={p.title} delay={i * 60}>
                <div className="h-full rounded-2xl border border-line bg-surface-muted p-6 transition duration-300 ease-smooth hover:-translate-y-0.5 hover:bg-surface hover:shadow-card">
                  <p className="font-display text-body font-semibold text-ink">{p.title}</p>
                  <p className="mt-1.5 text-small text-ink-muted">{p.text}</p>
                </div>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      <section className="section-y">
        <div className="container-page">
          <Reveal>
            <SectionHeading
              eyebrow="Сколько это стоит иначе"
              title="Сравните с альтернативами"
            />
          </Reveal>
          <div className="mt-14 grid gap-5 md:grid-cols-3">
            {alternatives.map((a, i) => (
              <Reveal key={a.title} delay={i * 80}>
                <div
                  className={`h-full rounded-3xl p-8 transition duration-300 ease-smooth hover:-translate-y-1 ${
                    a.highlight
                      ? "bg-brand-900 text-white shadow-card-hover"
                      : "border border-line bg-surface shadow-card hover:shadow-card-hover"
                  }`}
                >
                  <h3 className={`text-title ${a.highlight ? "text-white" : ""}`}>{a.title}</h3>
                  <p className={`mt-3 text-body ${a.highlight ? "text-brand-100" : "text-ink-muted"}`}>
                    {a.text}
                  </p>
                </div>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      <section className="section-y border-t border-line bg-surface-muted">
        <div className="container-page grid gap-12 lg:grid-cols-[0.8fr_1.2fr] lg:gap-20">
          <Reveal>
            <SectionHeading align="left" eyebrow="Оплата" title="Вопросы про оплату" />
          </Reveal>
          <Reveal delay={100}>
            <FAQAccordion items={pricingFaq} />
          </Reveal>
        </div>
      </section>

      <CtaBanner title="Начните с бесплатного тарифа" cta="Начать бесплатно" />
    </PageShell>
  );
}
