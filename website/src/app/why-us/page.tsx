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
    "Почему селлеры выбирают «Голос бренда»: всё в Telegram, WB и Ozon вместе, понятная цена и плохие отзывы только через вас.",
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

const comparison = [
  { label: "Где работаете", us: "В Telegram", market: "Отдельный сайт" },
  { label: "Площадки", us: "WB и Ozon вместе", market: "Часто только WB" },
  { label: "Оплата", us: "Фиксированно в месяц", market: "За каждый ответ" },
  { label: "Плохие отзывы", us: "Только через вас", market: "Бывает автоматически" },
  { label: "Отправка ответа", us: "Одной кнопкой (PRO)", market: "Вручную в кабинете" },
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
            <div className="mt-14 overflow-hidden rounded-3xl border border-line">
              <div className="grid grid-cols-[1fr_1fr_1fr] bg-surface-muted text-small font-medium text-ink-subtle">
                <div className="px-5 py-4 sm:px-7" />
                <div className="bg-brand-50 px-5 py-4 font-display font-semibold text-brand-800 sm:px-7">
                  Голос бренда
                </div>
                <div className="px-5 py-4 sm:px-7">Обычно у других</div>
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

      <CtaBanner title="Проверьте разницу сами" cta="Попробовать в боте" showCalculatorLink />
    </PageShell>
  );
}
