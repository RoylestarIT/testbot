import { Reveal } from "./Reveal";
import { SectionHeading } from "./SectionHeading";

const rules = [
  {
    title: "Автоматом — только хорошие оценки",
    text: "На PRO можно включить автоответы на 4–5★. Пятёрки закрываются сами, вы не копируете одно и то же сотый раз.",
  },
  {
    title: "Плохие отзывы — только через вас",
    text: "На 1–3★ бот никогда не отправит ответ сам. Сначала вы читаете, правите черновик и только потом решаете.",
  },
  {
    title: "Выключить — одна кнопка",
    text: "Автомат не «навсегда». Передумали — выключаете в настройках и снова отвечаете вручную.",
  },
];

export function AutopilotGuardrailsSection() {
  return (
    <section className="section-y">
      <div className="container-page">
        <Reveal>
          <SectionHeading
            eyebrow="Без сюрпризов"
            title="Быстро, как автопилот — но с ограничителями"
            description="Конкуренты часто обещают «всё на автомате 24/7». Мы сознательно не делаем так: скорость там, где она безопасна, контроль — там, где покупатель может обидеться."
          />
        </Reveal>
        <div className="mt-14 grid gap-5 md:grid-cols-3 lg:mt-20">
          {rules.map((r, i) => (
            <Reveal key={r.title} delay={i * 70}>
              <article className="card-hover h-full p-8">
                <span className="flex h-10 w-10 items-center justify-center rounded-full bg-brand-100 font-display text-body font-semibold text-brand-800">
                  {i + 1}
                </span>
                <h3 className="mt-6 text-title">{r.title}</h3>
                <p className="mt-3 text-body text-ink-muted">{r.text}</p>
              </article>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}
