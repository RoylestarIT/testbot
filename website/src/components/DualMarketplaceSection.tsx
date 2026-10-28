import { Reveal } from "./Reveal";

const platforms = [
  {
    name: "Wildberries",
    dot: "bg-[#a13a7a]",
    text: "Отзывы и вопросы покупателей — в ту же ленту, что и Ozon.",
  },
  {
    name: "Ozon",
    dot: "bg-[#2d6fd2]",
    text: "Не нужен второй сервис и второй логин. Один бот, один стиль ответов.",
  },
];

export function DualMarketplaceSection() {
  return (
    <section className="section-y bg-brand-900 text-white">
      <div className="container-page">
        <Reveal>
          <div className="mx-auto max-w-2xl text-center">
            <p className="text-caption font-semibold uppercase tracking-[0.14em] text-brand-300">
              Wildberries и Ozon
            </p>
            <h2 className="mt-4 text-headline text-white sm:text-display">Один Telegram — две площадки</h2>
            <p className="mx-auto mt-5 max-w-prose text-body-lg text-brand-100">
              Многие сервисы заточены только под WB. Мы с самого начала делаем обе площадки: отзывы,
              черновики и история — в одном месте.
            </p>
          </div>
        </Reveal>
        <div className="mt-14 grid gap-5 lg:mt-20 lg:grid-cols-[1fr_auto_1fr] lg:items-stretch lg:gap-8">
          {platforms.map((p, i) => (
            <Reveal key={p.name} delay={i * 80}>
              <article className="h-full rounded-2xl border border-white/10 bg-white/5 p-8 backdrop-blur-sm">
                <p className="inline-flex items-center gap-2 font-display text-title font-semibold">
                  <span className={`h-2.5 w-2.5 rounded-full ${p.dot}`} aria-hidden />
                  {p.name}
                </p>
                <p className="mt-4 text-body leading-relaxed text-brand-100">{p.text}</p>
              </article>
            </Reveal>
          ))}
          <Reveal delay={120} className="hidden lg:flex lg:flex-col lg:items-center lg:justify-center lg:px-2">
            <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-white/10 ring-1 ring-white/15 text-2xl" aria-hidden>
              💬
            </div>
            <p className="mt-4 max-w-[8rem] text-center text-caption text-brand-200">Один чат вместо двух кабинетов</p>
          </Reveal>
        </div>
        <Reveal delay={160}>
          <p className="mx-auto mt-12 max-w-2xl text-center text-small text-brand-200/90">
            На тарифе Lite — до двух кабинетов, на PRO — до четырёх. Один стиль общения можно настроить для всех
            магазинов или разный — как удобнее.
          </p>
        </Reveal>
      </div>
    </section>
  );
}
