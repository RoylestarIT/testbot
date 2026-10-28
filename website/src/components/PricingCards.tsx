import { PRICES, PRO_TRIAL_DAYS } from "@/content/constants";
import { IconCheck } from "./icons";
import { LegalDisclaimer } from "./LegalDisclaimer";
import { TelegramButton } from "./TelegramButton";
import { Reveal } from "./Reveal";

const plans = [
  {
    name: "Free",
    price: "0 ₽",
    note: "навсегда",
    lead: "Попробовать на своих отзывах",
    cta: "Начать бесплатно",
    features: [
      "5 ответов в день",
      "1 кабинет WB или Ozon",
      "1 стиль общения",
      "Ответ копируете в кабинет",
    ],
  },
  {
    name: "Lite",
    price: `${PRICES.lite.rub} ₽`,
    note: `/ мес · ${PRICES.lite.byn} BYN`,
    lead: "Когда отзывов становится много",
    cta: "Выбрать Lite",
    features: [
      "Сколько угодно ответов",
      "2 кабинета WB и Ozon",
      "Разные стили для разных магазинов",
      "Ответ копируете в кабинет",
    ],
  },
  {
    name: "PRO",
    price: `${PRICES.pro.rub} ₽`,
    note: `/ мес · ${PRICES.pro.byn} BYN`,
    lead: "Чтобы вообще не заходить в кабинет",
    cta: "Попробовать PRO",
    featured: true,
    features: [
      "Всё, что есть в Lite",
      "4 кабинета WB и Ozon",
      "Ответ уходит прямо из бота",
      "Пятёрки и четвёрки — автоматически",
      `${PRO_TRIAL_DAYS} дня PRO бесплатно — один раз`,
    ],
  },
];

export function PricingCards({ showDisclaimer = false }: { showDisclaimer?: boolean }) {
  return (
    <div>
    <div className="grid gap-6 lg:grid-cols-3">
      {plans.map((plan, i) => (
        <Reveal key={plan.name} delay={i * 80} className="h-full">
          <div
            className={`relative flex h-full flex-col rounded-3xl p-8 transition duration-300 ease-smooth hover:-translate-y-1 ${
              plan.featured
                ? "bg-brand-900 text-white shadow-card-hover"
                : "border border-line bg-surface shadow-card hover:shadow-card-hover"
            }`}
          >
            {plan.featured && (
              <span className="absolute right-6 top-6 rounded-full bg-white/10 px-3 py-1 text-caption font-medium text-brand-100 ring-1 ring-white/15">
                Популярный
              </span>
            )}
            <h3 className={`text-title ${plan.featured ? "text-white" : ""}`}>{plan.name}</h3>
            <p className={`mt-2 text-small ${plan.featured ? "text-brand-200" : "text-ink-muted"}`}>
              {plan.lead}
            </p>
            {plan.featured ? (
              <p className="mt-3 text-caption font-medium text-brand-100">
                Пробный период: {PRO_TRIAL_DAYS} дня · в боте «Подписка» → «Попробовать PRO»
              </p>
            ) : null}
            <p className="mt-8 flex items-baseline gap-2">
              <span
                className={`font-display text-display font-semibold ${
                  plan.featured ? "text-white" : "text-ink"
                }`}
              >
                {plan.price}
              </span>
              <span className={`text-small ${plan.featured ? "text-brand-200" : "text-ink-subtle"}`}>
                {plan.note}
              </span>
            </p>
            <ul className="mt-8 flex-1 space-y-3.5">
              {plan.features.map((f) => (
                <li
                  key={f}
                  className={`flex gap-3 text-body ${plan.featured ? "text-brand-50" : "text-ink-muted"}`}
                >
                  <span
                    className={`mt-1 flex h-5 w-5 shrink-0 items-center justify-center rounded-full ${
                      plan.featured ? "bg-white/10 text-white" : "bg-brand-50 text-brand-600"
                    }`}
                    aria-hidden
                  >
                    <IconCheck className="h-3 w-3" />
                  </span>
                  {f}
                </li>
              ))}
            </ul>
            <TelegramButton
              trackSite
              variant={plan.featured ? "white" : "secondary"}
              className="mt-10 w-full"
            >
              {plan.cta}
            </TelegramButton>
          </div>
        </Reveal>
      ))}
    </div>
    {showDisclaimer && (
      <LegalDisclaimer className="mx-auto mt-10 max-w-3xl text-center" />
    )}
    </div>
  );
}
