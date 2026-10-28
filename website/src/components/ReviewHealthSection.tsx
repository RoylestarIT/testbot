import { Reveal } from "./Reveal";
import { SectionHeading } from "./SectionHeading";

const metrics = [
  { label: "Новые отзывы", hint: "есть ли что ответить прямо сейчас" },
  { label: "За 7 дней", hint: "сколько ушло на маркетплейс и сколько скопировали сами" },
  { label: "Здоровье", hint: "ключ, синхронизация, всё ли подключено" },
];

export function ReviewHealthSection() {
  return (
    <section className="section-y bg-surface-muted">
      <div className="container-page grid gap-14 lg:grid-cols-2 lg:items-center lg:gap-20">
        <Reveal>
          <SectionHeading
            align="left"
            eyebrow="Сводка в боте"
            title="Видно, что с отзывами — без таблиц и Excel"
            description="Не обещаем «волшебный рейтинг за ночь». Зато на главном экране бота понятно: есть ли новые отзывы, как идёт неделя и не сломалось ли подключение."
          />
          <ul className="mt-10 space-y-4">
            {metrics.map((m) => (
              <li key={m.label} className="flex gap-4">
                <span className="mt-1.5 h-2 w-2 shrink-0 rounded-full bg-brand-500" aria-hidden />
                <span>
                  <span className="font-display font-semibold text-ink">{m.label}</span>
                  <span className="block text-body text-ink-muted">{m.hint}</span>
                </span>
              </li>
            ))}
          </ul>
          <p className="mt-8 text-small text-ink-subtle">
            Подробнее — кнопки «Подробнее» и «Здоровье» в боте. Цифры всегда ваши, мы их на сайте не придумываем.
          </p>
        </Reveal>
        <Reveal delay={100}>
          <div className="relative mx-auto max-w-sm">
            <div
              className="absolute -inset-3 rounded-[1.75rem] bg-gradient-to-br from-brand-200/50 to-transparent blur-xl"
              aria-hidden
            />
            <div className="relative overflow-hidden rounded-[1.75rem] border border-line bg-[#0e1621] p-5 shadow-mockup ring-1 ring-black/5">
              <p className="text-sm font-semibold text-white">✨ Голос бренда</p>
              <div className="mt-4 space-y-3 rounded-xl border border-white/10 bg-white/5 p-4 text-[13px] leading-snug text-sky-100/90">
                <p>
                  <span className="text-white/60">📬</span> Новых отзывов:{" "}
                  <span className="text-white">смотрите в боте</span>
                </p>
                <p>
                  <span className="text-white/60">📩</span> За 7 дн.:{" "}
                  <span className="text-white">отправлено · скопировано</span>
                </p>
                <p className="text-white/55">Обновление отзывов · статус синхронизации</p>
              </div>
              <div className="mt-4 grid grid-cols-2 gap-2 text-center text-[11px] font-medium text-sky-100/80">
                {["📊 Подробнее", "🩺 Здоровье", "📬 Ответы", "⚙️ Настройки"].map((label) => (
                  <span
                    key={label}
                    className="rounded-lg bg-white/10 px-2 py-2 ring-1 ring-white/10"
                  >
                    {label}
                  </span>
                ))}
              </div>
            </div>
            <p className="mt-4 text-center text-caption text-ink-subtle">
              Схема интерфейса, не скрин с чужими цифрами
            </p>
          </div>
        </Reveal>
      </div>
    </section>
  );
}
