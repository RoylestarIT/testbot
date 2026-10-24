import type { Metadata } from "next";
import { PageShell } from "@/components/PageShell";
import { InnerPageHero } from "@/components/InnerPageHero";
import { Reveal } from "@/components/Reveal";
import { SectionHeading } from "@/components/SectionHeading";
import { CtaBanner } from "@/components/CtaBanner";
import { PRICES } from "@/content/constants";

export const metadata: Metadata = {
  title: "Почему мы",
  description:
    "Co-pilot в Telegram vs типичные сервисы: фикс подписка, WB+Ozon, контроль негатива, publish из бота.",
};

const values = [
  {
    kicker: "Время",
    title: "Отвечаете между делами",
    points: [
      "Очередь отзывов в Telegram — без прыжков между кабинетами",
      "Три готовых черновика — правка за минуту",
      "На PRO — публикация из бота и автоответы на 4–5★",
    ],
  },
  {
    kicker: "Деньги",
    title: "Подписка дешевле сотрудника",
    points: [
      "Сотрудник «только на отзывы» — часто 30–80 тыс. ₽ в месяц",
      `Lite — ${PRICES.lite.rub} ₽, PRO — ${PRICES.pro.rub} ₽ в месяц, фиксированно`,
      "Без оплаты за каждый ответ (на рынке ~1–3 ₽/ответ)",
    ],
  },
  {
    kicker: "Лояльность",
    title: "Живые ответы, а не шаблоны",
    points: [
      "Ответ в тоне бренда повышает доверие к карточке",
      "Негатив 1–3★ — только после вашего решения",
      "Единый голос бренда на WB и Ozon",
    ],
  },
];

const comparison = [
  { label: "Где работаете", us: "В Telegram", market: "Отдельный сайт или кабинет" },
  { label: "Площадки", us: "WB и Ozon вместе", market: "Часто только WB" },
  { label: "Оплата", us: "Фикс в месяц", market: "За каждый ответ" },
  { label: "Негатив 1–3★", us: "Только с вашего OK", market: "Бывает автоматически" },
  { label: "Публикация", us: "Из бота (PRO)", market: "Вручную в кабинете" },
];

export default function WhyUsPage() {
  return (
    <PageShell>
      <InnerPageHero
        eyebrow="Почему мы"
        title="Время, деньги и лояльность — в одном Telegram"
        description="Отзывы не должны съедать ваш день. Мы забираем рутину — а решение, что увидит покупатель, остаётся за вами."
      />

      <section className="pb-20 sm:pb-24 lg:pb-32">
        <div className="container-page grid gap-5 lg:grid-cols-3">
          {values.map((v, i) => (
            <Reveal key={v.kicker} delay={i * 80}>
              <article className="card-hover flex h-full flex-col p-8 sm:p-9">
                <p className="eyebrow">{v.kicker}</p>
                <h2 className="mt-4 text-title">{v.title}</h2>
                <ul className="mt-6 space-y-3 border-t border-line pt-6">
                  {v.points.map((pt) => (
                    <li key={pt} className="flex gap-3 text-body text-ink-muted">
                      <span className="mt-[0.6rem] h-1.5 w-1.5 shrink-0 rounded-full bg-brand-400" aria-hidden />
                      {pt}
                    </li>
                  ))}
                </ul>
              </article>
            </Reveal>
          ))}
        </div>
      </section>

      <section className="section-y border-y border-line bg-surface">
        <div className="container-page max-w-4xl">
          <Reveal>
            <SectionHeading
              eyebrow="Сравнение"
              title="Чем мы отличаемся"
              description="Без имён конкурентов — просто типичные подходы на рынке."
            />
          </Reveal>
          <Reveal delay={100}>
            <div className="mt-14 overflow-hidden rounded-3xl border border-line">
              <div className="grid grid-cols-[1fr_1fr_1fr] bg-surface-muted text-small font-medium text-ink-subtle">
                <div className="px-5 py-4 sm:px-7" />
                <div className="bg-brand-50 px-5 py-4 font-display font-semibold text-brand-800 sm:px-7">
                  Голос бренда
                </div>
                <div className="px-5 py-4 sm:px-7">Часто на рынке</div>
              </div>
              {comparison.map((row) => (
                <div
                  key={row.label}
                  className="grid grid-cols-[1fr_1fr_1fr] border-t border-line text-small transition-colors hover:bg-surface-elevated sm:text-body"
                >
                  <div className="px-5 py-4 font-medium text-ink sm:px-7">{row.label}</div>
                  <div className="bg-brand-50/40 px-5 py-4 text-ink sm:px-7">{row.us}</div>
                  <div className="px-5 py-4 text-ink-subtle sm:px-7">{row.market}</div>
                </div>
              ))}
            </div>
          </Reveal>
        </div>
      </section>

      <CtaBanner title="Проверьте разницу сами" cta="Попробовать в боте" />
    </PageShell>
  );
}
