import Link from "next/link";
import { Reveal } from "./Reveal";
import { SectionHeading } from "./SectionHeading";
import { TelegramButton } from "./TelegramButton";
import { Button } from "./Button";
import { IconArrowRight } from "./icons";

const steps = [
  {
    n: "1",
    title: "Откройте бота",
    text: "Нажмите «Попробовать бесплатно» — откроется @FeedBackReview_bot. Регистрация на сайте не нужна.",
  },
  {
    n: "2",
    title: "Подключите кабинет",
    text: "В «Настройки» вставьте API-ключ WB или Ozon. Бот подскажет, где его взять в личном кабинете.",
  },
  {
    n: "3",
    title: "Ответьте на первый отзыв",
    text: "Выберите один из трёх вариантов, при желании поправьте и отправьте — или скопируйте на бесплатном тарифе.",
  },
];

export function QuickStartSection() {
  return (
    <section className="section-y border-y border-line bg-surface">
      <div className="container-page">
        <Reveal>
          <SectionHeading
            eyebrow="Старт за пару минут"
            title="Три шага — и вы уже в деле"
            description="Без установки программ и без ввода карты. Всё в Telegram, ключ — только там."
          />
        </Reveal>
        <ol className="mt-14 grid gap-5 lg:mt-20 lg:grid-cols-3">
          {steps.map((s, i) => (
            <Reveal key={s.title} delay={i * 80}>
              <li className="card-hover list-none p-8">
                <span className="font-display text-display font-semibold text-brand-200">{s.n}</span>
                <h3 className="mt-4 text-title">{s.title}</h3>
                <p className="mt-3 text-body text-ink-muted">{s.text}</p>
              </li>
            </Reveal>
          ))}
        </ol>
        <Reveal delay={200}>
          <div className="mt-12 flex flex-col items-center gap-4 sm:flex-row sm:justify-center">
            <TelegramButton trackSite size="lg">
              Открыть бота
            </TelegramButton>
            <Button href="/faq#api-key" variant="secondary" trailing={<IconArrowRight />}>
              Где взять API-ключ
            </Button>
          </div>
          <p className="mt-6 text-center text-small text-ink-subtle">
            Бесплатно: 5 ответов в день · без карты · плохие отзывы только через вас
          </p>
        </Reveal>
      </div>
    </section>
  );
}
