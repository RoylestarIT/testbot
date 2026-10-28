import type { Metadata } from "next";
import { PageShell } from "@/components/PageShell";
import { InnerPageHero } from "@/components/InnerPageHero";
import { Reveal } from "@/components/Reveal";
import { SectionHeading } from "@/components/SectionHeading";
import { CtaBanner } from "@/components/CtaBanner";
import { MarketCompareTable } from "@/components/MarketCompareTable";
import { PRICES } from "@/content/constants";

export const metadata: Metadata = {
  title: "Почему мы",
  description:
    "Почему селлеры выбирают «Голос бренда»: Telegram, Wildberries и Ozon вместе, фиксированная цена, плохие отзывы только через вас.",
};

const values = [
  {
    kicker: "Время",
    title: "Отвечаете между делами",
    points: [
      "Отзывы приходят в Telegram — не нужно скакать по кабинетам",
      "Три готовых варианта — поправить можно за минуту",
      "На PRO ответ уходит из бота, а пятёрки закрываются сами",
    ],
  },
  {
    kicker: "Деньги",
    title: "Дешевле, чем нанимать человека",
    points: [
      "Сотрудник только на отзывы обходится в 30–80 тыс. ₽ в месяц",
      `Lite — ${PRICES.lite.rub} ₽, PRO — ${PRICES.pro.rub} ₽ в месяц. И всё`,
      "Не платите за каждый ответ, как в других сервисах (1–3 ₽ за штуку)",
    ],
  },
  {
    kicker: "Покупатели",
    title: "Живые ответы вместо отписок",
    points: [
      "Когда продавец отвечает по-человечески, карточке больше доверяют",
      "На плохие отзывы отвечаете вы — бот только помогает",
      "Одинаковый стиль общения на WB и Ozon",
    ],
  },
];

export default function WhyUsPage() {
  return (
    <PageShell>
      <InnerPageHero
        eyebrow="Почему мы"
        title="Меньше рутины, больше довольных покупателей"
        description="Отзывы не должны съедать ваш день. Бот берёт на себя рутину, а что увидит покупатель — решаете вы."
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
              description="Без названий — просто как обычно устроены похожие сервисы."
            />
          </Reveal>
          <Reveal delay={100}>
            <div className="mt-14">
              <MarketCompareTable />
            </div>
          </Reveal>
        </div>
      </section>

      <CtaBanner title="Проверьте разницу сами" cta="Попробовать в боте" showCalculatorLink />
    </PageShell>
  );
}
